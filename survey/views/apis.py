import io
import requests
import sys

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
from django.views.decorators.clickjacking import xframe_options_exempt

from middleware.login_required import login_exempt


from survey.models import *
from survey.forms import *
import survey.helpers as helpers


MISSING_THANKYOU_MESSAGE = 'Thank you! Your response was submitted successfully.'


##
##	/survey/api/campaigns/responses/ <campaign=___, since=___>
##
@login_exempt
def api_responses(request):
	'''
	Return all responses for the given campaign, since the given date.
	"campaign" and "since" are required.
	'''
	try:
		campaign = Campaign.objects.get(uid=request.GET['campaign'])
		sinceDate = timezone.make_aware(datetime.fromtimestamp(int(request.GET['since'])+1))
	except:
		response = JsonResponse({'responses':[]}, status=404)
		response["Access-Control-Allow-Origin"] = "*"
		return response
		
	campaignResponses = campaign.response_campaign
	
	response = JsonResponse({
		'responses': list(campaign.response_campaign.filter(created_at__gt=sinceDate).values_list('raw_data', flat=True))
	}, status=200)
	
	response["Access-Control-Allow-Origin"] = "*"
	return response
	
	
##
##	/survey/api/user/add/ <POST DATA>
##
@user_passes_test(helpers.hasAdminAccess)
def api_user_add(request):
	'''
	Creates a user with the passed email and name. Basic.
	Returns the user object ID and user's name (for optional display).
	'''
	email = request.POST.get('email')
	httpCode = 404
	
	# NOTE: This ensures all usernames/emails to be lowercase. Prevents mismatch
	# for users with mix-case emails.
	try:
		user = helpers.createNewUser(email)
		
		httpCode = 200
		responseData = {
			'id': user.id,
			'username': user.username,
			'fullName': user.profile.full_name
		}
	except Exception as ex:
		httpCode = 500
		responseData = {
			'results': {
				'message': repr(ex)
			}
		}
		
	return JsonResponse(responseData, status=httpCode)
	
	
##
##	/survey/api/adminaccess/<POST>
##
@user_passes_test(helpers.hasAdminAccess)
def api_adminaccess(request):
	'''
	Admin access api, adds/removes user via email to admin group.
	'''
	email = request.POST.get('email')
	action = request.POST.get('action')
	adminGroup, created = Group.objects.get_or_create(name='admins')
	httpCode = 404
	
	# If user no existy, throw back default 404.
	try:
		user = User.objects.get(username=email)
	except Exception as ex:
		responseData = {
			'results': {
				'message': repr(ex)
			}
		}
		
	if user:
		if action == "add":
			user.groups.add(adminGroup) 
			httpCode = 200
			responseData = {
				'results': {
					'id': user.id,
					'name': user.profile.full_name,
					'username': user.username
				}
			}
		elif action == "remove":
			adminGroup.user_set.remove(user)
			httpCode = 200
			responseData = {
				'results': {
					'message': 'User removed successfully'
				}
			}
		else:
			httpCode = 400
			responseData = {
				'results': {
					'message': 'You forgot to tell me what to do; add or remove the user.'
				}
			}
		
	return JsonResponse(responseData, status=httpCode)


##
##	/survey/api/submit/<POST>
##
@xframe_options_exempt
@login_exempt
@csrf_exempt
def api_submit_response(request):
	'''
	Surveys post to this URL. Store the response and return message to display.
	'''
	try:
		campaign = Campaign.objects.get(uid=request.POST.get('cuid'))
	except:
		return JsonResponse({'results': {'message': 'The survey campaign is invalid.'}}, status=400)
	
	try:
		# Store the raw data, then set user survey submit timestamp/flag.
		response = campaign.storeResponse(request.session['uuid'], request)
		campaign.setUserStatus(request.session['uuid'], 'submitted')
		response.sendSlackNotification()
	except Exception as ex:
		try:
			userInfo, created = campaign.getCreateUserInfo(request)
			response = campaign.storeResponse(request.session['uuid'], request)
			campaign.setUserStatus(request.session['uuid'], 'submitted')
			response.sendSlackNotification()
			if campaign.survey.survey_type == 'feedback':
				response.sendToLux()
		except Exception as ex:
			cuid = campaign.uid if campaign else 'none'
			uuid = request.session['uuid'] if request.session['uuid'] else 'none'
			print(f'Error: api_submit_response failed - CUID:{cuid}:, UID :{uuid}:, error: - {ex}')
			return JsonResponse({'results': {'message': f'{ex}'}}, status=400)
	
	try:
		projectNameToUse = campaign.project.getDisplayName()
		if campaign.custom_project_name:
			projectNameToUse = campaign.custom_project_name
		
		thankyou = campaign.survey_thankyou.message
		thankyou = thankyou.replace('{projectname}', projectNameToUse)
	except:
		thankyou = MISSING_THANKYOU_MESSAGE
	
	response = JsonResponse({'message': thankyou}, status=200)
	response["Access-Control-Allow-Origin"] = "*"
	return response
	
##
##	/survey/api/deleteresponse/
##
@user_passes_test(helpers.hasAdminAccess)
def api_delete_response(request):
	'''
	Admin center response list delete a response link hits this.
	'''
	try:
		response = Response.objects.get(id=request.POST.get('response'))
		response.deleteResponseAndRecalc()
	except Exception as ex:
		return JsonResponse({'results': {'message': f'{ex}'}}, status=400)
	
	return JsonResponse({'results': {'message': 'Success.'}}, status=200)
	
	
##
##	/survey/api/deletecampaignresponses/
##
@user_passes_test(helpers.hasAdminAccess)
def api_delete_campaign_responses(request):
	'''
	Admin center campaign list page "delete all responses" hits this.
	'''
	try:
		campaign = Campaign.objects.get(id=request.POST.get('campaign'))
		campaign.deleteResponsesAndReset()
		campaign.customPreSave()
		campaign.save()
	except Exception as ex:
		return JsonResponse({'results': {'message': f'{ex}'}}, status=400)
	
	return JsonResponse({'results': {'message': 'Success.'}}, status=200)
	
	
##
##	/survey/api/deletetakenflags/
##
@user_passes_test(helpers.hasAdminAccess)
def api_delete_taken_flags(request):
	'''
	Admin center api to ONLY delete campaignUserInfos for a campaign. Leaves responses.
	Use case is if you want to leave existing responses, but allow everyone to be able to take
	the survey again. Essentially clearing the "shown" and "taken" flags.
	'''
	try:
		campaign = Campaign.objects.get(id=request.POST.get('campaign'))
		campaign.resetUserStatusFlags()
		campaign.customPreSave()
		campaign.save()
	except Exception as ex:
		return JsonResponse({'results': {'message': f'{ex}'}}, status=400)
	
	return JsonResponse({'results': {'message': 'Success.'}}, status=200)
	
	
##
##	/survey/api/campaign/toggleenabled/
##
@user_passes_test(helpers.hasAdminAccess)
def api_campaign_toggle_enabled(request):
	'''
	Admin center campaign list, toggle a campaign on/off.
	'''
	try:
		campaign = Campaign.objects.get(id=request.POST.get('campaign'))
		campaign.enabled = True if not campaign.enabled else False
		campaign.customPreSave()
		campaign.save()
	except Exception as ex:
		return JsonResponse({'results': {'message': f'{ex}'}}, status=400)
	
	return JsonResponse({'results': {'message': 'Success.'}}, status=200)
	
	
##
##	/survey/takelater/
##
@login_exempt
@csrf_exempt
def api_campaign_take_later(request):
	'''
	When the elect to take it later, set their status so on page load we know
	to show a little reminder icon.
	If setting fails because it can't find it, create user status then set it.
	'''
	try:
		campaign = Campaign.objects.get(uid=request.POST.get('cuid'))
		campaign.setUserStatus(request.session['uuid'], 'take_later')
	except:
		try:
			userInfo, created = campaign.getCreateUserInfo(request)
			campaign.setUserStatus(request.session['uuid'], 'intercept_shown')
			campaign.setUserStatus(request.session['uuid'], 'take_later')
		except Exception as ex:
			cuid = campaign.uid if campaign else 'none'
			uuid = request.session['uuid'] if request.session['uuid'] else 'none'
			print(f'Error: api_campaign_take_later failed - CUID:{cuid}:, UID :{uuid}: - {ex}')

	response = JsonResponse({'results': {'message': 'Success.'}}, status=200)
	response["Access-Control-Allow-Origin"] = "*"
	
	try:
		response.delete_cookie(campaign.uid)
	except:
		pass
	
	return response
	
	
##
##	/survey/api/removetakelater/
##
@login_exempt
@csrf_exempt
def api_campaign_remove_take_later(request):
	'''
	When they click on the reminder icon remove take_later flag.
	'''
	try:
		campaign = Campaign.objects.get(uid=request.POST.get('cuid'))
	except:
		campaign = None
	
	uuid = request.session['uuid'] if request.session['uuid'] else 'none'
	
	if campaign:
		try:
			campaign.setUserStatus(uuid, 'remove_take_later')
		except Exception as ex:
			try:
				userInfo, created = campaign.getCreateUserInfo(request)
				campaign.setUserStatus(uuid, 'intercept_shown')
			except Exception as ex:
				print(f'Error: api_campaign_remove_take_later failed - CUID:{campaign.uid}:, UID :{uuid}: - {ex}')
	else:
		print(f"Error: api_campaign_remove_take_later failed, no campaign found - CUID:{request.POST.get('cuid')}:, UID :{request.session['uuid']}:")
	
	response = JsonResponse({'results': {'message': 'Success.'}}, status=200)
	try:
		reqDomain = request.META['HTTP_ORIGIN']
	except:
		reqDomain = '*'
	response['Access-Control-Allow-Origin'] = reqDomain
	response['Access-Control-Allow-Credentials'] = 'true'
	return response


##
##	/survey/api/setactivestates/
##
@login_exempt
def api_set_active_states(request):
	'''
	Cron job api run daily to check for campaigns with dates and en/disable them.
	'''
	Campaign.setActiveStateAllCampaigns()
	return JsonResponse({'results':'Success.'}, status=200)
	
	
##
##	/survey/takelater/<id>/
##
@login_exempt
@csrf_exempt
def api_campaign_email_link(request):
	'''
	When they elect to take later and email them a link.
	If we can't get a campaign user status, create one.
	'''
	try:
		campaign = Campaign.objects.get(uid=request.POST.get('cuid','None'))
		campaign.setUserStatus(request.session['uuid'], 'email_link')
		email = request.POST.get('email')
		runInBackground(campaign.emailLink, {'email':email})
	except Exception as ex:
		try:
			userInfo, created = campaign.getCreateUserInfo(request)
			campaign.setUserStatus(request.session['uuid'], 'email_link')
			email = request.POST.get('email')
			runInBackground(campaign.emailLink, {'email':email})
		except Exception as ex:
			print(f'Error: email link api_campaign_email_link failed - {ex}')
	
	response = JsonResponse({'results': {'message': 'Success.'}}, status=200)
	response["Access-Control-Allow-Origin"] = "*"
	return response
	

##
##	/survey/api/campaigns/
##
@login_exempt
def api_campaigns(request):
	'''
	List of active campaigns. This is for downstream systems to pull and
	then loop through to get responses for a given campaign.
	'''
	try:
		campaigns = list(Campaign.objects.filter(active=True).values('uid', 'key'))
	except:
		campaigns = []
	
	return JsonResponse({'campaigns': campaigns}, status=200)
	

##
##	/survey/removecampaignuserinfo/
##
def api_remove_campaign_user_info(request):
	'''
	For admins - when clicking "force survey" in debug box, we first remove their entry for the campaign.
	'''
	try:
		campaign = Campaign.objects.get(uid=request.POST.get('campaign'))
		campaign.removeUserInfo(request.session['uuid'])
	except Exception as ex:
		print(f'{ex}')

	response = JsonResponse({'results': {'message': 'Success.'}}, status=200)
	response["Access-Control-Allow-Origin"] = "*"
	return response


##
##	/survey/api/defaultthankyou/
##
def api_get_default_thankyou(request):
	'''
	For admins - when choosing campaign survey, get and set the initial thank you based on survey type.
	'''
	data = {
		'thankyouId': False
	}
	
	try:
		surveyType = Survey.objects.get(id=request.GET.get('surveyid')).survey_type
		
		if surveyType == 'vote':
			ty = SurveyThankyou.objects.get(vote_default=True)
		elif surveyType == 'feedback':
			ty = SurveyThankyou.objects.get(feedback_default=True)
		
		data = {
			'thankyouId': ty.id,
		}
	except Exception as ex:
		pass

	response = JsonResponse(data, status=200)
	return response


