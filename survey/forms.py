from django.forms import ModelForm
from django import forms
from django.contrib.admin.widgets import AdminDateWidget

from .models import *

requiredCssClass = 'bo-field-required'
DATE_PICKER = forms.TextInput(attrs={'type':'date', 'style': 'width: 160px'})


class BannerNotificationForm(ModelForm):
	required_css_class = requiredCssClass
	
	class Meta:
		model = BannerNotification
		readonly_fields = []
		exclude = ['created_by', 'updated_by']
		widgets = {}
		
		
class ButtonForm(ModelForm):
	required_css_class = requiredCssClass
	
	class Meta:
		model = Button
		readonly_fields = []
		exclude = ['created_by', 'updated_by']
		widgets = {
			'background_color': forms.TextInput(attrs={'style': 'padding:0;border:0;height:2rem;width:2rem;', 'type': 'color'}),
			'offset': forms.NumberInput(attrs={'data-units':'%', 'style': 'width:7rem;', 'min':0,'max':100}),
			'position': forms.Select(attrs={'data-width': '7rem'}),
		}
		
		
class CampaignForm(ModelForm):
	required_css_class = requiredCssClass
	
	class Meta:
		model = Campaign
		readonly_fields = []
		exclude = ['created_by', 'updated_by']
		widgets = {
			'active': forms.TextInput(attrs={'type':'hidden'}),
			'survey_trigger_type': forms.Select(attrs={'data-width':'16rem'}),
			'button': forms.Select(attrs={'data-width':'16rem'}),
			'comments': forms.Textarea(attrs={'class': 'bo-common-autotextarea', 'rows': '3'}),
			'start_date': DATE_PICKER,
			'stop_date': DATE_PICKER,
			'response_count_limit': forms.NumberInput(attrs={'style':'width:5rem;'}),
			'page_view_count': forms.NumberInput(attrs={'style':'width:5rem;'}),
			'visitor_percent': forms.NumberInput(attrs={'style':'width:5rem;'}),
			'seconds_on_page_delay': forms.NumberInput(attrs={'style':'width:5rem;'}),
			'latest_response_date': forms.TextInput(attrs={'type':'hidden'}),
			'response_count': forms.TextInput(attrs={'type':'hidden'}),
			'unique_visitor_count': forms.TextInput(attrs={'type':'hidden'}),
			'url_accessible': forms.TextInput(attrs={'type':'hidden'}),
			'intercept_shown_count': forms.TextInput(attrs={'type':'hidden'}),
			'uid': forms.TextInput(attrs={'readonly':'readonly'}),
			'key': forms.TextInput(attrs={'readonly':'readonly'}),
		}
		
	def __init__(self, *args, **kwargs):
		self.base_fields['project'].queryset = Project.objects.allActive()
		super().__init__(*args, **kwargs)
		
		
class DomainForm(ModelForm):
	required_css_class = requiredCssClass
	
	class Meta:
		model = Domain
		readonly_fields = []
		exclude = ['created_by', 'updated_by']
		widgets = {
			'lead': forms.Select(attrs={'data-widget':'addnewuser'}),
		}
			
	def __init__(self, *args, **kwargs):
		self.base_fields['lead'].choices = Profile.usersByFullnameWithEmpty()
		super().__init__(*args, **kwargs)

			
class LanguageForm(ModelForm):
	required_css_class = requiredCssClass
	
	class Meta:
		model = Language
		readonly_fields = []
		exclude = ['created_by', 'updated_by']
		widgets = {}
		
		
class PageForm(ModelForm):
	required_css_class = requiredCssClass
	
	class Meta:
		model = Page
		readonly_fields = []
		exclude = ['created_by', 'updated_by']
		widgets = {}
		
		
class ProfileForm(ModelForm):
	required_css_class = requiredCssClass
	
	class Meta:
		model = Profile
		readonly_fields = []
		exclude = ['created_by', 'updated_by']
		widgets = {}
		
		
class ProjectForm(ModelForm):
	required_css_class = requiredCssClass
	
	class Meta:
		model = Project
		readonly_fields = []
		exclude = ['created_by', 'updated_by']
		widgets = {
			'contact': forms.Select(attrs={'data-widget':'addnewuser'}),
			'comments': forms.Textarea(attrs={'class': 'bo-common-autotextarea', 'rows': '3'}),
			'uid': forms.TextInput(attrs={'readonly':'readonly'}),
		}
	
	def __init__(self, *args, **kwargs):
		self.base_fields['contact'].choices = Profile.usersByFullnameWithEmpty()
		super().__init__(*args, **kwargs)
		
		
class QuestionForm(ModelForm):
	required_css_class = requiredCssClass
	
	class Meta:
		model = Question
		readonly_fields = []
		exclude = ['created_by', 'updated_by']
		widgets = {
			'message_text': forms.Textarea(attrs={'class': 'bo-common-autotextarea', 'rows': '3'}),
			'type': forms.Select(attrs={'data-width':'16rem'}),
			'layout': forms.Select(attrs={'data-width':'16rem'}),
			'shared': forms.TextInput(attrs={'type':'hidden'}),
		}
		error_messages = {
			'short_name': {
				'invalid': 'Enter a valid “slug” consisting of letters, numbers or underscores'
			}
		}
		
		
class QuestionOrderForm(ModelForm):
	required_css_class = requiredCssClass
	
	class Meta:
		model = QuestionOrder
		readonly_fields = []
		exclude = ['created_by', 'updated_by']
		widgets = {}
		
		
class ReleaseNoteForm(ModelForm):
	required_css_class = requiredCssClass
	
	class Meta:
		model = ReleaseNote
		readonly_fields = []
		exclude = ['created_by', 'updated_by']
		widgets = {
			'date': DATE_PICKER,
		}
		
		
class ResponseForm(ModelForm):
	required_css_class = requiredCssClass
	
	class Meta:
		model = Response
		readonly_fields = []
		exclude = ['created_by', 'updated_by']
		widgets = {}
		
		
class SurveyForm(ModelForm):
	required_css_class = requiredCssClass
	
	class Meta:
		model = Survey
		readonly_fields = []
		exclude = ['created_by', 'updated_by']
		widgets = {
			'comments': forms.Textarea(attrs={'class': 'bo-common-autotextarea', 'rows': '3'}),
			'language': forms.Select(attrs={'data-width':'16rem'}),			
		}
		

class SurveyInviteForm(ModelForm):
	required_css_class = requiredCssClass
	
	class Meta:
		model = SurveyInvite
		readonly_fields = []
		exclude = ['created_by', 'updated_by']
		widgets = {
			'message': forms.Textarea(attrs={'class': 'bo-common-autotextarea', 'rows': '6'}),
		}
		
		
class SurveyThankyouForm(ModelForm):
	required_css_class = requiredCssClass
	
	class Meta:
		model = SurveyThankyou
		readonly_fields = []
		exclude = ['created_by', 'updated_by']
		widgets = {
			'message': forms.Textarea(attrs={'class': 'bo-common-autotextarea', 'rows': '6'}),
		}
		
		
class CampaignUserInfoForm(ModelForm):
	required_css_class = requiredCssClass
	
	class Meta:
		model = CampaignUserInfo
		readonly_fields = []
		exclude = ['created_by', 'updated_by']
		widgets = {}
		
class TranslationForm(ModelForm):
	required_css_class = requiredCssClass
	
	class Meta:
		model = Translation
		readonly_fields = []
		exclude = ['created_by', 'updated_by']
		widgets = {}
	
