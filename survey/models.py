import requests

from datetime import datetime, timedelta

from django.conf import settings
from django.contrib.auth.models import User, Group
from django.contrib.postgres.fields import ArrayField
from django.contrib.staticfiles.storage import staticfiles_storage
from django.core import validators
from django.core.validators import MinValueValidator, MaxValueValidator, MinLengthValidator
from django.db import models, connection
from django.db.models import Count, Sum, Value, Q
from django.db.models.functions import Lower
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf.urls.static import static
from django.urls import reverse
from django.utils import timezone
from django.utils.crypto import get_random_string

from scheduler import commonScheduler
import survey.helpers as helpers


def defaultLatestDate():
	return timezone.make_aware(datetime(2020,1,1))

def getToday():
	return timezone.now()

def getDaysAgo(n):
	return timezone.now() - timedelta(days=n)
	
def getScriptUser():
	user = Profile.getCreateUser('automatedscript', 'automatedscript')
	return user

def estimateCount(modelName, app='survey'):
	'''
	Postgres really sucks at full table counts, this is a faster version:
	http://wiki.postgresql.org/wiki/Slow_Counting
	Return: {int} Estimated count of # of objects in model.
	'''
	cursor = connection.cursor()
	cursor.execute(f"select reltuples from pg_class where relname='{app}_{modelName.lower()}'")
	row = cursor.fetchone()
	return int(row[0])
	
def runInBackground(funct, kwargs=None):
	'''
	Shortcut to run any function as a background process on a separate thread.
	Return: Null
	'''
	sched = commonScheduler()
	sched.add_job(funct, kwargs=kwargs)
	

class Language(models.Model):
	created_by = models.ForeignKey(User, related_name='language_created_by', on_delete=models.PROTECT)
	created_at = models.DateTimeField(auto_now_add=True, editable=False)
	updated_by = models.ForeignKey(User, related_name='language_updated_by', on_delete=models.PROTECT)
	updated_at = models.DateTimeField(auto_now=True)
	
	name = models.CharField(max_length=64, unique=True)
	
	class Meta:
		ordering = ['name']
		
	def __str__(self):
		return self.name
		

class Button(models.Model):
	created_by = models.ForeignKey(User, related_name='button_created_by', on_delete=models.PROTECT)
	created_at = models.DateTimeField(auto_now_add=True, editable=False)
	updated_by = models.ForeignKey(User, related_name='button_updated_by', on_delete=models.PROTECT)
	updated_at = models.DateTimeField(auto_now=True)
	
	feedback_default = models.BooleanField(default=False)
	name = models.CharField(max_length=64, unique=True, help_text='A display name to identify this button')
	text = models.CharField(max_length=64, help_text='The actual button text')
	background_color = models.CharField(max_length=7, validators=[MinLengthValidator(7)], help_text='The hex color code, include the #')
	text_color = models.CharField(max_length=7, validators=[MinLengthValidator(7)], editable=False)
	position = models.CharField(choices=[
		('top', 'Top'),
		('right', 'Right'),
		('bottom', 'Bottom'),
		('left', 'Left'),
	], default='right', max_length=8)
	offset = models.PositiveIntegerField(default=50, validators=[MinValueValidator(0), MaxValueValidator(100)], help_text='The top/left button offset, in %')
	
	class Meta:
		ordering = ['text']
		
	def __str__(self):
		return self.name


	def save(self, *args, **kwargs):
		if not self.background_color:
			self.background_color = '#1D3649'
			
		self.text_color = helpers.blackOrWhite(self.background_color)
		
		super(Button, self).save(*args, **kwargs)


class Domain(models.Model):
	created_by = models.ForeignKey(User, related_name='domain_created_by', on_delete=models.PROTECT)
	created_at = models.DateTimeField(auto_now_add=True, editable=False)
	updated_by = models.ForeignKey(User, related_name='domain_updated_by', on_delete=models.PROTECT)
	updated_at = models.DateTimeField(auto_now=True)
	
	name = models.CharField(max_length=64, unique=True)
	lead = models.ForeignKey(User, related_name='domain_lead', null=True, blank=True, on_delete=models.SET_NULL)
	
	class Meta:
		ordering = ['name']
		
	def __str__(self):
		return self.name
	
	
	@staticmethod
	def getOrCreate(name, lead):
		scriptUser = getScriptUser()
		try:
			domain, created = Domain.objects.get_or_create(
				name = name,
				defaults = {
					'created_by': scriptUser,
					'updated_by': scriptUser,
					'lead': lead,
				}
			)
		except:
			domain = None
			
		return domain
	
		
##
## Project preset chainable queries.
##
class ProjectQueryset(models.QuerySet):
	def allActive(self):
		'''
		Get all projects that are active. Basic .fiter() preset.
		Usage: Project.objects.allActive()
		Return: {queryset} Chainable queryset, the same as if you used .filter().
		'''
		return self.filter(active=True)

class ProjectManager(models.Manager):
	def get_queryset(self):
		return ProjectQueryset(self.model, using=self._db)	## IMPORTANT KEY ITEM.

	def allActive(self):
		return self.get_queryset().allActive()


class Project(models.Model):
	created_by = models.ForeignKey(User, related_name='project_created_by', on_delete=models.PROTECT)
	created_at = models.DateTimeField(auto_now_add=True, editable=False)
	updated_by = models.ForeignKey(User, related_name='project_updated_by', on_delete=models.PROTECT)
	updated_at = models.DateTimeField(auto_now=True)
	
	active = models.BooleanField(default=True)
	uid = models.CharField(max_length=24, unique=True, editable=False)
	name = models.CharField(max_length=128, unique=True)
	domain = models.ForeignKey(Domain, related_name='project_domain', null=True, blank=True, on_delete=models.SET_NULL)
	display_name = models.CharField(max_length=128, blank=True, help_text='Alternate name to display in surveys if not name above', verbose_name='Alternate display name')
	contact = models.ForeignKey(User, related_name='project_contact', null=True, blank=True, on_delete=models.SET_NULL)
	comments = models.TextField(max_length=512, blank=True)
	
	objects = ProjectManager()
	
	class Meta:
		ordering = ['name']
		
	def __str__(self):
		return self.name
	
	
	def save(self, *args, **kwargs):
		if not self.uid:
			self.uid = get_random_string(8)
		
		super(Project, self).save(*args, **kwargs)	
	

	def getDisplayName(self):
		return self.display_name if self.display_name else self.name
	
	
	@staticmethod
	def getOrCreate(name, domain=None, contact=None):
		scriptUser = getScriptUser()
		try:
			project, created = Project.objects.get_or_create(
				name = name,
				defaults = {
					'created_by': scriptUser,
					'updated_by': scriptUser,
					'contact': contact,
					'domain': domain
				}
			)
		except:
			project = None
			
		return project


class Survey(models.Model):
	created_by = models.ForeignKey(User, related_name='survey_created_by', on_delete=models.PROTECT)
	created_at = models.DateTimeField(auto_now_add=True, editable=False)
	updated_by = models.ForeignKey(User, related_name='survey_updated_by', on_delete=models.PROTECT)
	updated_at = models.DateTimeField(auto_now=True)
	
	survey_type = models.CharField(default='other', choices=[
		('vote','VotE'),
		('feedback','Feedback'),
		('other','Other'),
	], max_length=10, help_text='IMPORTANT: This determines how responses are tagged and displayed.')
	
	feedback_default = models.BooleanField(default=False)
	name = models.CharField(max_length=128, unique=True, help_text='Only used in admin, to easily identify this survey.')
	title = models.CharField(max_length=128, blank=True, help_text='This will show as the header above the survey')
	language = models.ForeignKey(Language, related_name='survey_language', on_delete=models.PROTECT)
	comments = models.TextField(max_length=512, blank=True)
	
	
	class Meta:
		ordering = ['name']
		
	def __str__(self):
		return self.name
	
	
	def getQuestions(self):
		try:
			return Question.objects.filter(question_order_question__page__survey=self)
		except:
			return None
			
		
class SurveyInvite(models.Model):
	created_by = models.ForeignKey(User, related_name='survey_invite_created_by', on_delete=models.PROTECT)
	created_at = models.DateTimeField(auto_now_add=True, editable=False)
	updated_by = models.ForeignKey(User, related_name='survey_invite_updated_by', on_delete=models.PROTECT)
	updated_at = models.DateTimeField(auto_now=True)
	
	name = models.CharField(max_length=128, unique=True)
	message = models.TextField(max_length=512, help_text='Message to display. HTML is allowed at your own risk.')
	
	class Meta:
		ordering = ['name']
		
	def __str__(self):
		return self.name


class SurveyThankyou(models.Model):
	created_by = models.ForeignKey(User, related_name='survey_thankyou_created_by', on_delete=models.PROTECT)
	created_at = models.DateTimeField(auto_now_add=True, editable=False)
	updated_by = models.ForeignKey(User, related_name='survey_thankyou_updated_by', on_delete=models.PROTECT)
	updated_at = models.DateTimeField(auto_now=True)
	
	name = models.CharField(max_length=128, unique=True)
	message = models.TextField(max_length=512, help_text='Message to display. HTML is allowed at your own risk.')
	
	class Meta:
		ordering = ['name']
		
	def __str__(self):
		return self.name


class Campaign(models.Model):
	'''
	Logic:
	Intercept: Get campaigns that are intercepts that match URL that are active.
	Then, check for the user: If intercept.stats.activeCampaign = true, return JS for it.
	Button: Get campaigns that are button that match URL that are active.
	If any button, return JS to show button.
	'''
	
	created_by = models.ForeignKey(User, related_name='campaign_created_by', on_delete=models.PROTECT)
	created_at = models.DateTimeField(auto_now_add=True, editable=False)
	updated_by = models.ForeignKey(User, related_name='campaign_updated_by', on_delete=models.PROTECT)
	updated_at = models.DateTimeField(auto_now=True)
	
	# enabled is editor controlled hard on/off. NEVER USE THIS FOR LOGIC.
	enabled = models.BooleanField(default=False)
	# active is programatically determinted. USE IN ALL LOGIC.
	active = models.BooleanField(default=False)
	uid = models.CharField(max_length=25, unique=True, editable=False)
	key = models.CharField(max_length=128, blank=True, help_text='Auto-generated nice name identifier')
	project = models.ForeignKey(Project, related_name='campaign_project', on_delete=models.CASCADE)
	survey = models.ForeignKey(Survey, related_name='campaign_survey', on_delete=models.CASCADE)
	slack_notification_url = models.URLField(max_length=255, null=True, blank=True)
	survey_trigger_type = models.CharField(default='', choices=[
			('intercept','Intercept'),
			('button','Button'),
		], max_length=10, blank=True, help_text='If you are embedding this survey on a page, how do you want it to be triggered')
	survey_invite = models.ForeignKey(SurveyInvite, related_name='campaign_survey_invite', null=True, blank=True, help_text='If this is an intercept survey, choose which invite to use', on_delete=models.SET_NULL)
	survey_thankyou = models.ForeignKey(SurveyThankyou, related_name='campaign_survey_thankyou', null=True, blank=True, help_text='Choose the thankyou message to show for this survey', on_delete=models.SET_NULL)
	# Settings.
	# Delivery rules.
	button = models.ForeignKey(Button, related_name='campaign_button', null=True, blank=True, on_delete=models.SET_NULL)
	mouseout_trigger = models.BooleanField(default=True, help_text='Intercept will display when user\'s mouse leaves the browser window')
	url_accessible = models.BooleanField(default=True, verbose_name='URL accessible')
	visitor_percent = models.PositiveIntegerField(default=25, validators=[MinValueValidator(0), MaxValueValidator(100)])
	limit_one_submission = models.BooleanField(default=True, help_text='Users will only be allowed to take the survey once, every ## days.')
	limit_one_submission_days = models.PositiveIntegerField(default=90, help_text='Allow the user to enter the pool of participants after these many days.')
	seconds_on_page_delay = models.PositiveIntegerField(default=0)
	repeat_visitors_only = models.BooleanField(default=False, help_text="Only users who have visited the site at least twice (2+ sessions) will be included")
	page_view_count = models.PositiveIntegerField(default=0)
	start_date = models.DateField(null=True, blank=True, help_text='Campaign will be active starting at Midnight on this date.')
	stop_date = models.DateField(null=True, blank=True, help_text='Campaign will deactivate at 11:59pm on this date.')
	response_count_limit = models.PositiveIntegerField(null=True, blank=True, help_text='Disable the camapign when this many responses are received.')
	
	# Stats.
	# Set in storeResponse.
	latest_response_date = models.DateTimeField(default=defaultLatestDate)
	response_count = models.PositiveIntegerField(default=0)
	# Unique visitors, used for % traffic setting.
	# Standalone: Set in survey_standalone_display
	# For embedded: Set on page load in the JS ajax view that figures out what to do.
	unique_visitor_count = models.PositiveIntegerField(default=0)
	# Number times survey was shown.
	# Set on survey_iframe_display view.
	intercept_shown_count = models.PositiveIntegerField(default=0)
	comments = models.TextField(max_length=512, blank=True)
	
	class Meta:
		ordering = ['project__name', 'survey__name']
		
	def __str__(self):
		return f'{self.project.name} - {self.survey.name}'
	
	
	def save(self, *args, **kwargs):
		self.key = self.getKey()
		super(Campaign, self).save(*args, **kwargs)
	
	
	def customPreSave(self, *args, **kwargs):
		# In/active flag is programatically determined. 
		if not self.uid:
			self.uid = 'b'+ get_random_string(24)
		
		self.setActiveState()
		
		# Force 1-take if it's a vote survey. 
		if self.survey.survey_type == 'vote' and not self.limit_one_submission:
			self.limit_one_submission = True
	
	
	def resetUserStatusFlags(self):
		'''
		Removes all statuses for this campaign.
		'''
		self.campaign_user_info_campaign.all().delete()
		self.unique_visitor_count = 0
		self.intercept_shown_count = 0
	
	
	def deleteResponsesAndReset(self):
		'''
		Delete all responses, set all counters to zero, set date to Jan 1 2020,
		'''
		self.response_campaign.all().delete()
		self.response_count = 0
		self.latest_response_date = timezone.make_aware(datetime(2020,1,1))
		self.resetUserStatusFlags()
	

	def getQuestions(self):
		try:
			return list(campaign.survey.page_survey.values('question_order_page__question', 'question_order_page__question__question_text'))
		except:
			return None
	
	
	def isPastResponseLimit(self):
		try:
			if self.response_count >= self.response_count_limit:
				return True
			else:
				return False
		except:
			return False
	
	
	def storeResponse(self, uuid, request):
		# Process POSTed response.
		# Create the raw data and add it and save.
		omitFields = ['display_type', 'survey_type', 'csrfmiddlewaretoken', 'url', 'cuid']
		
		fieldsOnly = {}
		
		for key, val in request.POST.items():
			if key in omitFields:
				continue
			
			# [] at end of field name denotes it's a multi-value field and we have to use getlist on those.
			if key[-2:] != '[]':
				fieldsOnly[key] = val
			else:
				fieldsOnly[key[:-2]] = request.POST.getlist(key) 
		
		surveyResponse = Response.objects.create(
			campaign = self,
			uuid = uuid,
			raw_data = {}
		)
		
		surveyResponse.raw_data = {
			'date': surveyResponse.created_at.isoformat(),
			'id': surveyResponse.uid,
			'campaignId': self.uid,
			'displayType': request.POST.get('display_type', ''),
			'surveyType': self.survey.survey_type,
			'url': request.POST.get('url', ''),
			'userAgent': request.META['HTTP_USER_AGENT'],
			'data': fieldsOnly,
		}
		
		surveyResponse.save()
		
		# Set the campaign stats.
		self.latest_response_date = surveyResponse.created_at
		self.response_count = self.response_campaign.count()
		self.save()
		
		# If this response put us at the response limit, deactivate campaign.
		if self.isPastResponseLimit():
			self.active = False
			self.save()
			
		return surveyResponse
	
	
	# Set the in/active state for the campaign based on response limit and start/end dates.
	def setActiveState(self):
		# Hard stops: If it's disabled or past response count limit, dates don't matter
		if not self.enabled:
			self.active = False
			return
		
		if self.isPastResponseLimit():
			self.active = False
			return
			
		# If we make it here, do logic based on start/stop dates.
		today = datetime.today().date()
		
		# Currently active, try and deactivate.
		if self.active:
			try:
				if self.stop_date and today >= self.stop_date:
					self.active = False
				elif self.start_date and today < self.start_date:
					self.active = False
			except:
				pass
		# Currently inactive and not past response limit, try and activate.
		else:
			try:
				if self.start_date:
					if today >= self.start_date:
						if self.stop_date:
							if today < self.stop_date:
								self.active = True
						else:
							self.active = True
				elif self.stop_date:
					if today < self.stop_date:
						self.active = True
				else:
					self.active = True
			except:
				pass
	
	
	def getInterceptShownPercent(self):
		try:
			return int(self.intercept_shown_count / self.unique_visitor_count * 100)
		except:
			return 0
	
	
	def getStandaloneSubmittedPercent(self):
		try:
			return round(self.response_count / self.unique_visitor_count * 100, 2)
		except:
			return 0
	
	
	def getCreateUserInfo(self, request):
		userInfo, created = CampaignUserInfo.objects.get_or_create(
			uuid = request.session['uuid'],
			campaign = self,
		)
		
		# If it's existing user and past the 90 days reset date, scrub existance and create new one.
		if not created and userInfo.reset_date and getToday() > userInfo.reset_date:
			userInfo.delete()
			self.intercept_shown_count -= 1
			self.unique_visitor_count -= 1
			self.save()
			
			userInfo, created = CampaignUserInfo.objects.get_or_create(
				uuid = request.session['uuid'],
				campaign = self,
			)
		
		userInfo.view_count += 1
		
		# If they don't have this campaign session cookie (gets set after this function call)
		#   it means this is a first view of a new session, so increment it.
		if not request.COOKIES.get(self.uid + 'cs', None):
			userInfo.session_count += 1
			
		userInfo.save()
		
		return userInfo, created
		
	
	'''
	# Returns stats as well as if we should show the survey or not,
	# and if not, what message to show.
	# This is the main logic to call.
	
	# For standalone, this runs on standalone display view.
	# For intercept, this HAS to run on initial logic for invite. Iframe can't use this logic.
	'''
	def getStatsForUser(self, request):
		activeCampaign = True
		campaignMessage = ''
		interceptStatus = 'none'
		
		# Get/create user entry for the campaign.
		userInfo, created = self.getCreateUserInfo(request)
		
		# Increment unique visitor_count if user was first view to the camapign.
		if created:
			self.unique_visitor_count = CampaignUserInfo.objects.filter(campaign=self).count()
			self.save()
		
		# Get the % shown (includes this user).
		interceptShownPercent = self.getInterceptShownPercent()
		
		# These are hard no-gos. Feedback forms can be multi-submit.
		if not self.active:
			activeCampaign = False
			campaignMessage = 'Aw shucks. We\'re sorry, this survey is no longer available.'
		elif self.limit_one_submission and userInfo.submitted_at:
			activeCampaign = False
			campaignMessage = 'Woohoo! You\'ve already completed this survey.<br>Thanks for your response, we appreciate it.'
		
		# Set status to tell JS what to do.
		if (activeCampaign and not userInfo.intercept_shown_at 
			and interceptShownPercent < self.visitor_percent 
			and (not self.repeat_visitors_only or (self.repeat_visitors_only and userInfo.session_count > 1))
			):
		
			interceptStatus = 'show_survey'
		elif activeCampaign and userInfo.take_later_at:
			interceptStatus = 'show_reminder'
		
		
		data = {
			'campaign': self,
			'visitor_percent': self.visitor_percent,
			'repeat_visitors_only': self.repeat_visitors_only,
			'unique_visitor_count': self.unique_visitor_count,
			'intercept_shown_count': self.intercept_shown_count,
			'latest_response_date': self.latest_response_date,
			'responseCount': self.response_count,
			'responseCountLimit': self.response_count_limit,
			'interceptShownPercent': interceptShownPercent,
			'hasInvite': True if self.survey_invite else False,
			'standaloneSubmittedPercent': self.getStandaloneSubmittedPercent(),
			'activeCampaign': activeCampaign,
			'campaignMessage': campaignMessage,
			'userInfo': userInfo,
			'setSessionCookie': True if not request.COOKIES.get(self.uid + 'cs', None) else False,
			'interceptStatus': interceptStatus,
		}
		
		return data
	
	
	def setUserStatus(self, uuid, type):
		userInfo = CampaignUserInfo.objects.get(uuid=uuid, campaign=self)

		if type == 'submitted':
			userInfo.submitted_at = timezone.now()
			userInfo.take_later_at = None
			if self.limit_one_submission:
				userInfo.reset_date = timezone.now() + timedelta(days=self.limit_one_submission_days)
		elif type == 'intercept_shown':
			userInfo.intercept_shown_at = timezone.now()
			if self.limit_one_submission:
				userInfo.reset_date = timezone.now() + timedelta(days=self.limit_one_submission_days)
		elif type == 'take_later':
			userInfo.take_later_at = timezone.now()
		elif type == 'remove_take_later':
			userInfo.take_later_at = None
		elif type == 'email_link':
			userInfo.email_link_at = timezone.now()
		
		userInfo.save()
	
	
	def removeUserInfo(self, uuid):
		try:
			CampaignUserInfo.objects.get(uuid=uuid, campaign=self).delete()
		except Exception as ex:
			print(f'{ex}')
		
	
	def emailLink(self, email):
		from templatetags.common_templatetags import getTemplateHelpers
		templateHelpers = getTemplateHelpers(None)
		logo = templateHelpers['html']['icons']['logo']
		
		url = reverse('survey:survey_standalone_display', kwargs={'uid':self.uid})
		
		try:
			helpers.sendEmail({
				'subject': f'[SurveyKong] Survey you requested for {self.project.name}',
				'recipients': [email],
				'message': f'<div style="font-family:sans-serif;font-size:14px;line-height:20px;">{logo} &nbsp; <p>As requested, here is a link to the survey about your recent experience with {self.project.name}: <a href="https://REPLACE_ME.com{url}">https://REPLACE_ME.com{url}</a></p>',
				
			})
		except Exception as ex:
			pass
		
	
	def getKey(self):
		'''
		Auto-generated nice name. This is instead of admins creating a naming convention
		for campaigns like "41_w3u_home_vote".
		'''
		nameNoSpace = self.project.name.replace(' ','_')
		return f'{nameNoSpace}_{self.survey.survey_type}_{self.uid[:5]}'
	
	
class Page(models.Model):
	survey = models.ForeignKey(Survey, related_name='page_survey', on_delete=models.CASCADE)
	page_number = models.PositiveIntegerField(default=1)
	
	class Meta:
		ordering = ['survey', 'page_number']
		
	def __str__(self):
		return f'{self.survey} - page {self.page_number}'


class Question(models.Model):
	short_name = models.SlugField(max_length=48, help_text='This is used in the response data to identify this question. No spaces allowed: Use underscores')
	question_text = models.CharField(max_length=255, blank=True)
	question_text_past_tense = models.CharField(max_length=255, blank=True, help_text='This is used for \'take later\' and email campaigns')
	required = models.BooleanField(default=False)
	shared = models.BooleanField(default=False)
	type = models.CharField(default='text', choices=[
		('checkbox', 'Checkboxes'),
		('date', 'Date'),
		('email', 'Email'),
		('hidden', 'Hidden'),
		('message', 'Message'),
		('number', 'Number'),
		('radio', 'Radio buttons'),
		('stars', 'Stars'),
		('select', 'Select list'),
		('selectmultiple', 'Select multiple'),
		('textinput', 'Text input'),
		('textarea', 'Textarea'),
		('url', 'URL'),
	], max_length=20)
	layout = models.CharField(default='vertical', choices=[
		('horizontal', 'Horizontal'),
		('vertical', 'Vertical'),
	], max_length=15)
	message_text = models.TextField(max_length=1200, blank=True, verbose_name='Message to display. HTML is allowed. BE CAREFUL.')
	placeholder_text = models.CharField(max_length=255, blank=True)
	character_limit = models.PositiveIntegerField(null=True, blank=True)
	anchor_text_beginning = models.CharField(max_length=50, blank=True)
	anchor_text_end = models.CharField(max_length=50, blank=True)
	answers = ArrayField(ArrayField(models.CharField(max_length=255, blank=True)), blank=True, null=True)
	default_answer = models.CharField(max_length=96, blank=True)
	
	parent_question = models.ForeignKey('Question', related_name='question_parent_question', null=True, blank=True, help_text='Select the question who\'s answer should show/hide this question', on_delete=models.SET_NULL)
	parent_answer = models.CharField(max_length=255, blank=True)
	parent_answer_action = models.CharField(default='show', choices=[
		('show', 'Show this question'),
		('hide', 'Hide this question'),
	], max_length=4)
	
	class Meta:
		ordering = ['question_text']
	
	def __str__(self):
		displayName = self.question_text if self.question_text else self.message_text[:90]
		return f'{displayName} - ({self.type}) - {"(required)" if self.required else "(optional)"}'
		
		
	def save(self, *args, **kwargs):
		self.short_name = self.short_name.replace('-','_')
		super(Question, self).save(*args, **kwargs)


class QuestionOrder(models.Model):
	page = models.ForeignKey(Page, related_name='question_order_page', on_delete=models.CASCADE)
	question = models.ForeignKey(Question, related_name='question_order_question', on_delete=models.CASCADE)
	question_number = models.FloatField(default=1)
	
	class Meta:
		ordering = ['page', 'question_number']
		
	def __str__(self):
		displayName = self.question.question_text if self.question.question_text else self.question.short_name
		return f'{self.page} - {displayName}'


class Response(models.Model):
	'''
	raw_data gets exported via API and table. Example:
		{
			"date": "2020-03-13T17:23:04.278Z",
			"id": "5e6bc174ef3c5c031c01a044",
			"campaignUid": "5e31f04d93906e699b5ff65a",
			"url": "",
			"userAgent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:68.0) Gecko/20100101 Firefox/68.0",
			"data": {
				"nps": 10,
				"UMUX_LITE_ease_of_use": 7,
				"UMUX_LITE_capabilities": 7,
				"email": "someon@domain.com"
			},
		}
	'''
	created_at = models.DateTimeField(auto_now_add=True)
	uid = models.CharField(max_length=24, unique=True)
	campaign = models.ForeignKey(Campaign, related_name='response_campaign', on_delete=models.CASCADE)
	uuid = models.CharField(max_length=64)
	raw_data = models.JSONField()
	
	class Meta:
		ordering = ['-created_at']
		
	def __str__(self):
		return f'{self.campaign} - {self.uid}'
		
	
	def save(self, *args, **kwargs):
		if not self.uid:
			self.uid = get_random_string(24)
			
		super(Response, self).save(*args, **kwargs)


	def deleteResponseAndRecalc(self):
		'''
		Delete this response and recalc (counts, latest date, etc)
		'''
		campaign = self.campaign
		
		self.delete()
		
		try:
			campaign.latest_response_date = campaign.response_campaign.order_by('-created_at').first().created_at
		except:
			campaign.latest_response_date = defaultLatestDate()
		campaign.response_count = campaign.response_campaign.count()
		campaign.customPreSave()
		campaign.save()
	
	
	def sendSlackNotification(self):
		'''
		Sends this response summary to whatever URL is set on the campaign
		'''
		slackUrl = self.campaign.slack_notification_url
		
		if slackUrl:
			dataFormatted = ''
			for key in self.raw_data['data']:
				if key == 'email':
					continue
				if key == 'cc':
					keyNicename = 'country_code'
				else:
					keyNicename = key
				
				dataFormatted += f'*{keyNicename}*: {self.raw_data["data"][key]}\n'
				
			payload = {
				'username': 'SurveyKong',
				'text': f'*A new {self.campaign.survey.survey_type} response just came in for {self.campaign.project.name}*\n{dataFormatted}',
			}
			r = requests.post(slackUrl, json=payload)

		
class CampaignUserInfo(models.Model):
	'''
	Track which users have been shown which campaigns/surveys.
	This is basically advanced session handling that allows us to clear session
	data per campaign or per survey (shared), with advanced options like "clear session for this
	campaign for everyone in the past week"
	'''
	uuid = models.CharField(max_length=64)
	campaign = models.ForeignKey(Campaign, related_name='campaign_user_info_campaign', on_delete=models.CASCADE)
	view_count = models.PositiveIntegerField(default=0)
	session_count = models.PositiveIntegerField(default=0)
	intercept_shown_at = models.DateTimeField(null=True, blank=True)
	take_later_at = models.DateTimeField(null=True, blank=True)
	email_link_at = models.DateTimeField(null=True, blank=True)
	submitted_at = models.DateTimeField(null=True, blank=True)
	reset_date = models.DateTimeField(null=True, blank=True)
	
	class Meta:
		ordering = ['campaign', '-intercept_shown_at', '-take_later_at', '-submitted_at']
		unique_together = ['uuid', 'campaign']
		
	def __str__(self):
		return '{} : {}'.format(self.intercept_shown_at, self.campaign)
		
			
class Profile(models.Model):
	'''
	Extension of user object. Receives signal from User obj and 
	creates/saves the user's profile.
	'''
	inactive = models.BooleanField(default=False)
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	full_name = models.CharField(max_length=255, blank=True)
	image = models.TextField(blank=True, default='')

	class Meta:
		ordering = ['full_name']
		
	def __str__(self):
		return '{} : {}'.format(self.user, self.full_name)
	
	
	def updateFromPost(self, post):
		updatableFields = [
			'full_name',
			'image',
		]
		
		for field in updatableFields:
			postedValue = post.get(field, None)
			
			if postedValue:
				setattr(self, field, postedValue)


	@staticmethod
	def usersByFullname():
		users = Profile.objects.filter(user__username__contains='@').exclude(Q(full_name__isnull=True) | Q(inactive=True)).order_by('full_name').values_list('user_id','full_name')
		return tuple(list(users))
	
	
	@staticmethod
	def usersByFullnameWithEmpty():
		users = Profile.objects.filter(user__username__contains='@').exclude(Q(full_name__isnull=True) | Q(inactive=True)).order_by('full_name').values_list('user_id','full_name')
		return tuple([('', '---------')] + list(users))
	

	@staticmethod
	def getCreateUser(email, name):
		if email:
			try:
				user, created = User.objects.get_or_create(
					username = email,
					defaults = {
						'password': get_random_string(),
					}
				)
				user.profile.full_name = name
				user.save()
			except:
				user = None
		else:
			user = None
		
		return user
	
	
'''
Django signals: Tells Django to automatically save the User's Profile record when User is saved.
Profile is an extention of User.
You should never save Profile directly. Update profile fields ('user.profile.fieldABC') and do "user.save()".
'''
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
	if created:
		Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
	instance.profile.save()
	

class BannerNotification(models.Model):
	'''
	Allows you to create a site-wide banner at the top of the page for site-wide 
	notifications, i.e. site maintenance, problems, important updates, etc.
	'''
	name = models.CharField(max_length=32)
	active = models.BooleanField(default=False)
	banner_text = models.CharField(max_length=255)
	banner_type = models.CharField(default='info', choices=[
			('info','info'),
			('warn','warn'),
			('alert','alert'),
		], max_length=10)

	class Meta:
		ordering = ['active','name']

	def __str__(self):
		return '%s - %s - %s' % (self.name, self.banner_type, self.active)


def incrementReleaseNum():
	try:
		return ReleaseNote.objects.order_by('-release_number').first().release_number+1
	except:
		return 1
	
class ReleaseNote(models.Model):
	created_at = models.DateTimeField(auto_now_add=True)
	created_by = models.ForeignKey(User, related_name='release_note_created_by', on_delete=models.PROTECT)
	updated_at = models.DateTimeField(auto_now=True)
	updated_by = models.ForeignKey(User, related_name='release_note_updated_by', on_delete=models.PROTECT)
	
	release_number = models.PositiveIntegerField(default=incrementReleaseNum, unique=True)
	date = models.DateTimeField(default=getToday)
	notes = models.TextField(max_length=1000)
	
	class Meta:
		ordering = ['-release_number']
		
	def __str__(self):
		return '{} : {}'.format(self.release_number, self.date)


