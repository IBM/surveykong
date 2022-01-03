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

from middleware.login_required import login_exempt


from survey.models import *
from survey.forms import *
import survey.helpers as helpers


MISSING_THANKYOU_MESSAGE = 'Thank you! Your response was submitted successfully.'


##
##	/survey/api/campaigns/responses/ 
##
@login_exempt
def api_responses(request):
	try:
		campaign = Campaign.objects.get(uid=request.GET.get('campaign'))
	except:
		response = JsonResponse({'responses':[]}, status=404)
		response["Access-Control-Allow-Origin"] = "*"
		return response
		
	campaignResponses = campaign.response_campaign
	
	# Require "since" param, if missing or invalid, 
	#  return nothing for safety (instead of returning all)
	try:
		sinceDate = timezone.make_aware(datetime.fromtimestamp(int(request.GET.get('since', None))+1))
	except:
		sinceDate = timezone.now()
		
	response = JsonResponse({
		'responses': list(campaign.response_campaign.filter(created_at__gt=sinceDate).values_list('raw_data', flat=True))
	}, status=200)
	
	response["Access-Control-Allow-Origin"] = "*"
	return response
	
	
##
##	/survey/api/user/add/ <POST DATA>
##
##	Creates a user with the passed email and name. Basic.
##	Returns the user object ID and user's name (for optional display).
##
@login_required
def api_user_add(request):
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
@login_exempt
def api_submit_response(request):
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
		return JsonResponse({'results': {'message': f'{ex}'}}, status=400)
	
	try:
		thankyou = campaign.survey_thankyou.message
	except:
		thankyou = MISSING_THANKYOU_MESSAGE
	
	response = JsonResponse({'message': thankyou}, status=200)
	response["Access-Control-Allow-Origin"] = "*"
	return response
	
##
##	/survey/api/deleteresponse/
##
def api_delete_response(request):
	try:
		response = Response.objects.get(id=request.POST.get('response'))
		response.deleteResponseAndRecalc()
	except Exception as ex:
		return JsonResponse({'results': {'message': f'{ex}'}}, status=400)
	
	return JsonResponse({'results': {'message': 'Success.'}}, status=200)
	
	
##
##	/survey/api/deletecampaignresponses/
##
def api_delete_campaign_responses(request):
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
def api_delete_taken_flags(request):
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
def api_campaign_toggle_enabled(request):
	try:
		campaign = Campaign.objects.get(id=request.POST.get('campaign'))
		campaign.enabled = True if not campaign.enabled else False
		campaign.customPreSave()
		campaign.save()
	except Exception as ex:
		return JsonResponse({'results': {'message': f'{ex}'}}, status=400)
	
	return JsonResponse({'results': {'message': 'Success.'}}, status=200)
	
	
##
##	/survey/takelater/<id>/
##
@login_exempt
@csrf_exempt
def api_campaign_take_later(request):
	'''
	When the elect to take it later, set their status so on page load we know
	to show a little reminder icon.
	'''
	try:
		campaign = Campaign.objects.get(uid=request.POST.get('cuid'))
		campaign.setUserStatus(request.session['uuid'], 'take_later')
	except Exception as ex:
		print(f'Error: Take later api_campaign_take_later failed. UID :{request.session["uuid"]}: - {ex}')

	response = JsonResponse({'results': {'message': 'Success.'}}, status=200)
	response["Access-Control-Allow-Origin"] = "*"
	
	try:
		response.delete_cookie(campaign.uid)
	except:
		pass
	
	return response
	
	
##
##	/survey/removetakelater/
##
@login_exempt
@csrf_exempt
def api_campaign_remove_take_later(request):
	'''
	When they click on the reminder icon remove take_later flag.
	'''
	try:
		campaign = Campaign.objects.get(uid=request.POST.get('cuid'))
		campaign.setUserStatus(request.session['uuid'], 'remove_take_later')
	except Exception as ex:
		print(f"Error: Take later api_campaign_remove_take_later failed. UID: {request.session['uuid']} | CUID: {request.POST.get('cuid')} | ex: {ex}")

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
	for c in Campaign.objects.allActive():
		c.setActiveState()
		c.save()
		
	return JsonResponse({'results':'Success.'}, status=200)
	
	
##
##	/survey/takelater/<id>/
##
@login_exempt
@csrf_exempt
def api_campaign_email_link(request):
	'''
	When they elect to take later and email them a link.
	'''
	try:
		campaign = Campaign.objects.get(uid=request.POST.get('cuid','None'))
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
