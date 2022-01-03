import io
import json
import requests
import sys
import time

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Count, Value, Q
from django.http import HttpResponse, HttpResponseNotAllowed, JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.crypto import get_random_string
from django.views.decorators.csrf import csrf_exempt

from middleware.login_required import login_exempt

from django.views.decorators.clickjacking import xframe_options_exempt

from ..models import *
from ..forms import *
import survey.helpers as helpers


##
##	/survey/
##
def home(request):
	# All 403s send user to home page, so add 'admin' check here to display 403 error.
	if not request.user.hasAdminAccess():
		return render(request, '403.html', {}, status=403)
		
	context = {
		'latestCampaigns': Campaign.objects.all().order_by('-created_at')[:3],
		'mostActiveCampaigns': Campaign.objects.all().order_by('-response_count')[:3],
		'mostRecentResponses': Response.objects.all().order_by('-created_at')[:3],
		'leftNavHighlight': 'dashboard',
	}
	
	response = render(request, 'survey/home.html', context)
	helpers.clearPageMessage(request)
	return response	
	
	
##
##	/survey/display/<id>/
##
@login_exempt
def survey_standalone_display(request, uid):
	'''
	Standalone survey version.
	'''
	try:
		campaign = Campaign.objects.filter(uid=uid).select_related('survey',).prefetch_related('survey__page_survey','survey__page_survey__question_order_page', 'survey__page_survey__question_order_page__question').first()
		campaignStats = campaign.getStatsForUser(request)
		
		pagesWithQuestions = []
		# For each page, call function that returns sorted standard survey + custom campaign questions.
		for page in campaign.survey.page_survey.all():
			page.questionOrders = page.getAllQuestionOrders(campaign)
			if page.questionOrders:
				pagesWithQuestions.append(page)
				
	except:
		return render(request, '404.html', {}, status=404)
	
	context = {
		'campaign': campaign,
		'campaignStats': campaignStats,
		'currentView': 'standalone',
		'pagesWithQuestions': pagesWithQuestions,
	}
	
	# Template chooser.
	if campaignStats['activeCampaign'] or request.GET.get('force', '') == 'y':
		template = 'survey/survey_standalone_display.html'
	else:
		template = 'survey/survey_standalone_no_display.html'
	
	projectNameToUse = campaign.project.getDisplayName()
	if campaign.custom_project_name:
		projectNameToUse = campaign.custom_project_name
	
	responseText = render_to_string(template, context=context, request=request)
	responseText = responseText.replace('{projectname}', projectNameToUse)
	response = HttpResponse(responseText)
	
	helpers.clearPageMessage(request)
	return response	
	

##
##	/survey/iframe/display/<id>/
##
@login_exempt
@xframe_options_exempt
def survey_iframe_display(request):
	'''
	Iframe survey version.
	'''
	try:
		uid = request.GET.get('cuid')
		campaign = Campaign.objects.filter(uid=uid).select_related('survey',).prefetch_related('survey__page_survey','survey__page_survey__question_order_page', 'survey__page_survey__question_order_page__question').first()
		campaignStats = campaign.getStatsForUser(request)
		
		pagesWithQuestions = []
		# For each page, call function that returns sorted standard survey + custom campaign questions.
		for page in campaign.survey.page_survey.all():
			page.questionOrders = page.getAllQuestionOrders(campaign)
			if page.questionOrders:
				pagesWithQuestions.append(page)
				
	except:
		return render(request, '404.html', {}, status=404)
		
	if campaignStats['interceptStatus'] == 'show_survey':
		campaignStats['campaign'].setUserStatus(request.session['uuid'], 'intercept_shown')
		#campaignStats['campaign'].intercept_shown_count = CampaignUserInfo.objects.filter(campaign=campaignStats['campaign'], intercept_shown_at__isnull=False).count()
		campaignStats['campaign'].intercept_shown_count += 1
		campaignStats['campaign'].save()
		
	context = {
		'campaignStats': campaignStats,
		'currentView': 'intercept',
		'pagesWithQuestions': pagesWithQuestions,
	}
	
	# Template chooser.
	if campaignStats['activeCampaign'] or request.GET.get('force', '') == 'y':
		template = 'survey/survey_iframe_display.html'
	else:
		template = 'survey/survey_iframe_no_display.html'
		
	projectNameToUse = campaignStats['campaign'].project.getDisplayName()
	if campaignStats['campaign'].custom_project_name:
		projectNameToUse = campaignStats['campaign'].custom_project_name
	
	responseText = render_to_string(template, context=context, request=request)
	responseText = responseText.replace('{projectname}', projectNameToUse)
	response = HttpResponse(responseText)
	
	helpers.clearPageMessage(request)
	return response	
	

##
##	/survey/iframe/invite/<uid>.html
##
@login_exempt
@xframe_options_exempt
def survey_iframe_invite(request, uid):
	campaign = get_object_or_404(Campaign, uid=uid)
	
	context = {
		'campaign': campaign,
	}
	
	projectNameToUse = campaign.project.getDisplayName()
	if campaign.custom_project_name:
		projectNameToUse = campaign.custom_project_name
	
	responseText = render_to_string('survey/survey_iframe_invite.html', context=context, request=request)
	responseText = responseText.replace('{projectname}', projectNameToUse)
	response = HttpResponse(responseText)
	
	return response


##
##	/survey/campaigns/responses/
##
@user_passes_test(helpers.hasAdminAccess)
def campaign_responses_list(request):
	try:
		campaign = Campaign.objects.get(uid=request.GET.get('uid', None))
		responses = campaign.response_campaign.all()
	except:
		campaign = None
		responses = None		
		
	context = {
		'campaigns': Campaign.objects.filter(response_campaign__isnull=False).distinct().order_by('key'),
		'campaign': campaign,
		'responses': responses,
		'leftNavHighlight': 'responses',
	}
	
	response = render(request, 'survey/campaign_responses_list.html', context)
	helpers.clearPageMessage(request)
	return response	
	
	
##
##	/survey/preconfig/<uid>.js
##
@login_exempt
@xframe_options_exempt
def preconfig_javascript(request, uid):
	'''
	Return JS that does ajax request, sending origin to project_config.
	'''
	context = {
		'projectUid': uid,
	}
	
	responseText = render_to_string('survey/preconfig_javascript.js', context=context, request=request)
	responseText = responseText.replace('\n','').replace('\t','')
	response = HttpResponse(responseText, content_type='text/javascript')
	return response
	

##
##	/survey/projectconfig/<uid>.js
##
@login_exempt
@xframe_options_exempt
@csrf_exempt
def project_config_javascript(request, uid):
	'''
	If there's an active intercept campaign, and they don't have the lottery cookie:
	Get the stats for the user for the campaign (lottery logic) and JS decides what to do (show or not)
	'''
	t0 = time.time()
	project = get_object_or_404(Project, uid=uid)
	interceptCampaign = project.getActiveMatchingInterceptCampaign(request.POST.get('url'))
	interceptCampaignStats = None
	setLotteryCookie = False
	
	# If there's an intercept and they don't have the lottery cookie yet, see if they are a winner.
	#if interceptCampaign and not request.COOKIES.get(interceptCampaign.uid, None):
	try:
		interceptCampaignStats = interceptCampaign.getStatsForUser(request)
		if interceptCampaignStats['interceptStatus'] != 'show_reminder':
			setLotteryCookie = True
	except:
		interceptCampaignStats = None
	
	buttonCampaign = project.getActiveMatchingButtonCampaign(request.POST.get('url', ''))
	
	# Generate some stats as JS object for the page to see/use if they want their own rules to 
	#  manually trigger a campaign survey.
	activeCampaignsData = {}
	for campaign in Campaign.objects.filter(project=project, active=True):
		stats = campaign.getStats(request)
		activeCampaignsData[campaign.uid] = stats
		
	context = {
		'campaignStats': interceptCampaignStats,
		'buttonCampaign': buttonCampaign,
		'forceIntercept': request.GET.get('forceintercept', None),
		'activeCampaignsData': json.dumps(activeCampaignsData),
		'flags': {
			'hasIntercept': True if interceptCampaignStats and not interceptCampaignStats['hasInvite'] else False,
			'hasInvite': True if interceptCampaignStats and interceptCampaignStats['hasInvite'] else False,
			'hasButton': True if buttonCampaign else False,
			
		}
	}
	
	#content = render(request, 'survey/project_config_javascript.js', context)
	#response = HttpResponse(content, content_type='text/javascript')
	responseText = render_to_string('survey/project_config_javascript.js', context=context, request=request)
	responseText = responseText.replace('\n','').replace('\t','').replace('[timer]', str(round((time.time()-t0)*1000)))
	response = HttpResponse(responseText, content_type='text/javascript')
	
	try:
		reqDomain = request.META['HTTP_ORIGIN']
	except:
		reqDomain = '*'
	response['Access-Control-Allow-Origin'] = reqDomain
	response['Access-Control-Allow-Credentials'] = 'true'
	
	# Campaign Session tracker.
	if interceptCampaignStats and interceptCampaignStats['setSessionCookie']:
		response.set_cookie(interceptCampaignStats['campaign'].uid + 'cs', value='1', max_age=None, expires=None, path='/', domain=None, secure=True, httponly=False, samesite='lax')
		
	# if setLotteryCookie and not (request.user.is_authenticated and request.user.hasAdminAccess):
	# 	response.set_cookie(interceptCampaign.uid, value='1', max_age=(interceptCampaign.limit_one_submission_days*86400), path='/', domain=None, secure=False, httponly=False, samesite='lax')
	
	return response
	

##
##	/survey/iframe/embedtest/
##
@login_exempt
def iframe_embed_test(request):
	response = render(request, 'survey/test_implementation.html', {})
	return response
	

##
##	/survey/iframe/admin/debugbox/<uid>.html
##
@login_exempt
@xframe_options_exempt
def survey_iframe_admin_debug_box(request, uid):
	try:
		campaign = Campaign.objects.filter(uid=uid).select_related('survey').first()
		campaignStats = campaign.getStatsForUser(request)
	except:
		return render(request, '404.html', {}, status=404)
		
	context = {
		'campaignStats': campaign.getStatsForUser(request),
		'currentView': 'intercept',
	}
	
	response = render(request, 'survey/survey_iframe_admin_debug_box.html', context)
	return response


##
##	/survey/releasenotes/
##
##
def release_notes(request):
	context = {
		'releaseNotes': ReleaseNote.objects.all(),
		'leftNavHighlight': 'releasenotes',
	}
	return render(request, 'survey/release_notes.html', context)

	
	
	
########################################################
########################################################
##
## Standards views in each app, direct copy/paste.
##
########################################################
########################################################

##
##	/survey/signin/
##
##	Sign in page
##
def signin(request):
	## If user is already signed in they don't need to be here, so redirect them to home page.
	if request.user.is_authenticated:
		response = redirect(reverse('survey:home'))
	
	elif request.method == 'GET':
		response = render(request, 'signin.html', {
			'form': AuthenticationForm,
		})
	
	elif request.method == 'POST':
		username = request.POST['username']
		password = request.POST['password']
		
		# NOTE: This ensures all usernames/emails to be lowercase. Prevents mismatch
		# for users with mix-case emails.
		try:
			user = authenticate(request, username=username.lower(), password=password)
		except Exception as ex:
			context = {
				'form': AuthenticationForm,
				'error': 'Uh oh, we were unable to authenticate you. Check your ID/PW and try again.',
			}
			
			return render(request, 'signin.html', context)
		
		## Success
		if user is not None:
			login(request, user)
			
			# Hit some company profile API to create/update their profile.
			helpers.updateUserProfile(user)
			
			# Send them back to the page they originally went to before they had to sign in.
			response = redirect(request.POST.get('next', reverse('survey:home')))
		
		## Fail
		else:
			context = {
				'form': AuthenticationForm,
				'error': 'DOH! It seems your ID/PW combination wasn\'t quite right.<br>Please try again.',
			}
			response = render(request, 'signin.html', context)
	
	return response


##
##	/survey/signout/
##
##	Signs the user out.
##
def signout(request):
	logout(request)
	return render(request, 'signout.html', {})


##
##	404
##
##	This is only needed if you want to do custom processing when a 404 happens.
##
def custom_404(request, exception):
	referer = request.META.get('HTTP_REFERER', 'None')

	if request.user.username:
		userCaused = '\n*User:* {}'.format(request.user.username)
	else: 
		userCaused = ''	

	if request.get_host() in referer:
		helpers.sendSlackAlert(404, '*Requested path:*  {}\n*Referring page:*	 {}{}'.format(request.path, referer, userCaused))
		
	return render(request, '404.html', {}, status=404)
	

##
##	500
##
##	This is only needed if you want to do custom processing when a 500 happens.
##
def custom_500(request):
	exctype, value = sys.exc_info()[:2]
	
	errMsg = value or '(No error provided)'
	errMsg = str(errMsg)
		
	referer = request.META.get('HTTP_REFERER', 'None')

	if request.user.username:
		userCaused = '\n*User:* {}'.format(request.user.username)
	else: 
		userCaused = ''	

	helpers.sendSlackAlert(500, '*Requested path:*	{}{}\n*Error msg:*	{}\nCheck email for full debug.'.format(request.path, userCaused, errMsg))
		
	return render(request, '500.html', {}, status=500)
	
