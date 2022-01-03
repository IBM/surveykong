'''
survey app URL Configuration
'''

from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import reverse_lazy
from django.views.generic import RedirectView, TemplateView

from .views import *


## All URLs are namespaced in root URL config with 'survey'.

urlpatterns = [
	
	## Pages
	url(r'^$', home, name='home'), 
	url(r'^campaign/responses/$', campaign_responses_list, name='campaign_responses_list'),
	url(r'^preconfig/(?P<uid>[\w-]+).js$', preconfig_javascript, name='preconfig_javascript'),
	url(r'^projectconfig/(?P<uid>[\w-]+).js$', project_config_javascript, name='project_config_javascript'),
	url(r'^display/(?P<uid>[\w-]+)/$', survey_standalone_display, name='survey_standalone_display'),
	url(r'^iframe/display/$', survey_iframe_display, name='survey_iframe_display'),
	url(r'^iframe/invite/(?P<uid>[\w-]+).html$', survey_iframe_invite, name='survey_iframe_invite'),
	url(r'^iframe/embedtest/$', iframe_embed_test, name='iframe_embed_test'),
	url(r'^iframe/admin_debugbox/(?P<uid>[\w-]+)/$', survey_iframe_admin_debug_box, name='survey_iframe_admin_debug_box'),
	url(r'^releasenotes/$', release_notes, name='release_notes'),
	
	
	## APIs.
	url(r'^api/adminaccess/$', api_adminaccess, name='api_adminaccess'),
	url(r'^api/campaign/toggleenabled/$', api_campaign_toggle_enabled, name='api_campaign_toggle_enabled'),
	url(r'^api/campaigns/$', api_campaigns, name='api_campaigns'),
	url(r'^api/defaultthankyou/$', api_get_default_thankyou, name='api_get_default_thankyou'),
	url(r'^api/deletecampaignresponses/$', api_delete_campaign_responses, name='api_delete_campaign_responses'),
	url(r'^api/deleteresponse/$', api_delete_response, name='api_delete_response'),
	url(r'^api/deletetakenflags/$', api_delete_taken_flags, name='api_delete_taken_flags'),
	url(r'^api/emaillink/$', api_campaign_email_link, name='api_campaign_email_link'),
	url(r'^api/removetakelater/$', api_campaign_remove_take_later, name='api_campaign_remove_take_later'),
	url(r'^api/removecampaignuserinfo/$', api_remove_campaign_user_info, name='api_remove_campaign_user_info'),
	url(r'^api/responses/$', api_responses, name='api_responses'),
	url(r'^api/submit/$', api_submit_response, name='api_submit_response'),
	url(r'^api/takelater/$', api_campaign_take_later, name='api_campaign_take_later'),
	url(r'^api/user/add/$', api_user_add, name='api_user_add'),
	
	
	
	
	## APIs crons.
	url(r'^api/setactivestates/$', api_set_active_states, name='api_set_active_states'),
		
	
	## Admin URLs
	url(r'^admin/$', admin_home, name='admin_home'),
	url(r'^admin/adminaccess/$', admin_adminaccess, name='admin_adminaccess'),
	
	url(r'^admin/domain/$', admin_domain_list, name='admin_domain_list'),
	url(r'^admin/domain/add/$', admin_domain_add, name='admin_domain_add'),
	url(r'^admin/domain/edit/(?P<id>[\w-]+)/$', admin_domain_edit, name='admin_domain_edit'),
	url(r'^admin/domain/delete/$', admin_domain_delete, name='admin_domain_delete'),
	
	url(r'^admin/project/$', admin_project_list, name='admin_project_list'),
	url(r'^admin/project/add/$', admin_project_add, name='admin_project_add'),
	url(r'^admin/project/edit/(?P<id>[\w-]+)/$', admin_project_edit, name='admin_project_edit'),
	url(r'^admin/project/delete/$', admin_project_delete, name='admin_project_delete'),
	
	url(r'^admin/campaign/$', admin_campaign_list, name='admin_campaign_list'),
	url(r'^admin/campaign/add/$', admin_campaign_add, name='admin_campaign_add'),
	url(r'^admin/campaign/edit/(?P<id>[\w-]+)/$', admin_campaign_edit, name='admin_campaign_edit'),
	url(r'^admin/campaign/delete/$', admin_campaign_delete, name='admin_campaign_delete'),
	
	url(r'^admin/survey/$', admin_survey_list, name='admin_survey_list'),
	url(r'^admin/survey/add/$', admin_survey_add, name='admin_survey_add'),
	url(r'^admin/survey/edit/(?P<id>[\w-]+)/$', admin_survey_edit, name='admin_survey_edit'),
	url(r'^admin/survey/delete/$', admin_survey_delete, name='admin_survey_delete'),
	
	url(r'^admin/button/$', admin_button_list, name='admin_button_list'),
	url(r'^admin/button/add/$', admin_button_add, name='admin_button_add'),
	url(r'^admin/button/edit/(?P<id>[\w-]+)/$', admin_button_edit, name='admin_button_edit'),
	url(r'^admin/button/delete/$', admin_button_delete, name='admin_button_delete'),
	
	url(r'^admin/language/$', admin_language_list, name='admin_language_list'),
	url(r'^admin/language/add/$', admin_language_add, name='admin_language_add'),
	url(r'^admin/language/edit/(?P<id>[\w-]+)/$', admin_language_edit, name='admin_language_edit'),
	url(r'^admin/language/delete/$', admin_language_delete, name='admin_language_delete'),
	
	url(r'^admin/page/$', admin_page_list, name='admin_page_list'),
	url(r'^admin/page/add/$', admin_page_add, name='admin_page_add'),
	url(r'^admin/page/edit/(?P<id>[\w-]+)/$', admin_page_edit, name='admin_page_edit'),
	url(r'^admin/page/delete/$', admin_page_delete, name='admin_page_delete'),
	
	url(r'^admin/question/$', admin_question_list, name='admin_question_list'),
	url(r'^admin/question/add/$', admin_question_add, name='admin_question_add'),
	url(r'^admin/question/edit/(?P<id>[\w-]+)/$', admin_question_edit, name='admin_question_edit'),
	url(r'^admin/question/delete/$', admin_question_delete, name='admin_question_delete'),

	url(r'^admin/questionorder/$', admin_questionorder_list, name='admin_questionorder_list'),
	url(r'^admin/questionorder/add/$', admin_questionorder_add, name='admin_questionorder_add'),
	url(r'^admin/questionorder/edit/(?P<id>[\w-]+)/$', admin_questionorder_edit, name='admin_questionorder_edit'),
	url(r'^admin/questionorder/delete/$', admin_questionorder_delete, name='admin_questionorder_delete'),
	
	url(r'^admin/surveybuilder/$', admin_surveybuilder_list, name='admin_surveybuilder_list'),
	url(r'^admin/surveybuilder/add/$', admin_surveybuilder_add, name='admin_surveybuilder_add'),
	url(r'^admin/surveybuilder/edit/(?P<id>[\w-]+)/$', admin_surveybuilder_edit, name='admin_surveybuilder_edit'),
	url(r'^admin/surveybuilder/delete/$', admin_surveybuilder_delete, name='admin_surveybuilder_delete'),
	
	url(r'^admin/releasenote/$', admin_releasenote_list, name='admin_releasenote_list'),
	url(r'^admin/releasenote/add/$', admin_releasenote_add, name='admin_releasenote_add'),
	url(r'^admin/releasenote/edit/(?P<id>[\w-]+)/$', admin_releasenote_edit, name='admin_releasenote_edit'),
	url(r'^admin/releasenote/delete/$', admin_releasenote_delete, name='admin_releasenote_delete'),
	
	url(r'^admin/surveyinvite/$', admin_surveyinvite_list, name='admin_surveyinvite_list'),
	url(r'^admin/surveyinvite/add/$', admin_surveyinvite_add, name='admin_surveyinvite_add'),
	url(r'^admin/surveyinvite/edit/(?P<id>[\w-]+)/$', admin_surveyinvite_edit, name='admin_surveyinvite_edit'),
	url(r'^admin/surveyinvite/delete/$', admin_surveyinvite_delete, name='admin_surveyinvite_delete'),
	
	url(r'^admin/surveythankyou/$', admin_surveythankyou_list, name='admin_surveythankyou_list'),
	url(r'^admin/surveythankyou/add/$', admin_surveythankyou_add, name='admin_surveythankyou_add'),
	url(r'^admin/surveythankyou/edit/(?P<id>[\w-]+)/$', admin_surveythankyou_edit, name='admin_surveythankyou_edit'),
	url(r'^admin/surveythankyou/delete/$', admin_surveythankyou_delete, name='admin_surveythankyou_delete'),


	## Sign in/out.
	url(r'^signin/$', signin, name='signin'),
	url(r'^signout/$', signout, name='signout'),

	# Dev test only.
	url(r'^403/$', TemplateView.as_view(template_name='403.html'), name='test403'),
	url(r'^404/$', TemplateView.as_view(template_name='404.html'), name='test404'),
	url(r'^500/$', TemplateView.as_view(template_name='500.html'), name='test500'),
	
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

## DEBUG is in root URL file.

