import io
import json
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
from django.utils.text import capfirst


from survey.models import *
from survey.forms import *
import survey.helpers as helpers


def getAdminBreadcrumbBase():
	return []



def doCommonListView(request, model, listItems, viewTemplate=None, leftNavHighlight=None):
	thisModel = model
	newItemUrl = reverse(f'survey:admin_{thisModel._meta.model_name}_add')
	thisViewTemplate = f'survey/admin_{thisModel._meta.model_name}_list.html' if not viewTemplate else viewTemplate
	context = {
		'listItems': listItems,
		'modelMeta': thisModel._meta,
		'newItemUrl': newItemUrl,
		'leftNavHighlight': leftNavHighlight if leftNavHighlight else thisModel._meta.verbose_name_plural,
	}

	response = render(request, thisViewTemplate, context)
	helpers.clearPageMessage(request)
	return response


def doCommonAddItemView(request, thisModel, viewTemplate=None, leftNavHighlight=None, customPostProcess=None, customJs=False):
	thisModelForm = globals()[thisModel._meta.object_name + 'Form']
	thisViewTemplate = 'admin_common_add.html' if not viewTemplate else viewTemplate
	adminTemplate = 'survey/page_template_admin.html'
	thisModelListUrl = reverse(f'survey:admin_{thisModel._meta.model_name}_list')
	
	customJsPath = False
	if customJs:
		customJsPath = f'shared/js/{thisModel._meta.model_name}.js'
		
	breadcrumbs = getAdminBreadcrumbBase()
	breadcrumbs.append(
		{
			'text': capfirst(thisModel._meta.verbose_name_plural),
			'url': thisModelListUrl
		}
	)

	context = {
		'breadcrumbs': breadcrumbs,
		'form': None,
		'modelMeta': thisModel._meta,
		'newItemName': thisModel._meta.verbose_name,
		'adminTemplate': adminTemplate,
		'leftNavHighlight': leftNavHighlight if leftNavHighlight else thisModel._meta.verbose_name_plural,
		'customJsPath': customJsPath,
	}

	if request.method == 'GET':
		form = thisModelForm()
		context['form'] = form

		response = render(request, thisViewTemplate, context)
		helpers.clearPageMessage(request)
		
	elif request.method == 'POST':
		postData = request.POST.copy()
				
		if customPostProcess:
			postData = customPostProcess(postData)
		
		form = thisModelForm(postData)
		context['form'] = form
		
		if form.is_valid():
			post = form.save(commit=False)
			post.created_by = request.user
			post.updated_by = request.user
			post.save()
			form.save_m2m()
			
			# If it's a success and they want JSON back, return the ID and label as JSON,
			#  otherwise we redirect to the list page with a message.
			if request.POST.get('returntype', None) == 'json':
				response = JsonResponse({
					'id': post.id,
					'name': post.__str__()
				}, status=200)
			else:
				helpers.setPageMessage(request, 'success', f'{capfirst(thisModel._meta.verbose_name)} was added successfully')
				response = redirect(thisModelListUrl)
		else:
			response = render(request, thisViewTemplate, context)
			
	return response
	
	
def doCommonEditItemView(request, thisModel, id, nameField, viewTemplate=None, allowDelete=False, leftNavHighlight=None, customPostProcess=None, customJs=False):
	thisModelItem = get_object_or_404(thisModel, id=id)
	thisModelForm = globals()[thisModel._meta.object_name + 'Form']
	thisViewTemplate = 'admin_common_edit.html' if not viewTemplate else viewTemplate
	adminTemplate = 'survey/page_template_admin.html'
	addItemTemplate = 'admin_common_add.html'
	thisModelListUrl = reverse(f'survey:admin_{thisModel._meta.model_name}_list')
	
	try:
		thisModelDeleteUrl = reverse(f'survey:admin_{thisModel._meta.model_name}_delete')
	except:
		thisModelDeleteUrl = None
	
	customJsPath = False
	if customJs:
		customJsPath = f'shared/js/{thisModel._meta.model_name}.js'
		
	breadcrumbs = getAdminBreadcrumbBase()
	breadcrumbs.append(
		{
			'text': capfirst(thisModel._meta.verbose_name_plural),
			'url': thisModelListUrl
		}
	)

	context = {
		'breadcrumbs': breadcrumbs,
		'form': None,
		'modelMeta': thisModel._meta,
		'thisModelItem': thisModelItem,
		'itemName': getattr(thisModelItem, nameField),
		'adminTemplate': adminTemplate,
		'addItemTemplate': addItemTemplate,
		'thisModelDeleteUrl': thisModelDeleteUrl,
		'allowDelete': allowDelete,
		'leftNavHighlight': leftNavHighlight if leftNavHighlight else thisModel._meta.verbose_name_plural,
		'customJsPath': customJsPath,
	}

	if request.method == 'GET':
		form = thisModelForm(instance=thisModelItem)
		context['form'] = form

		response = render(request, thisViewTemplate, context)
		helpers.clearPageMessage(request)

	elif request.method == 'POST':
		postData = request.POST.copy()
		
		if customPostProcess:
			postData = customPostProcess(postData)
		
		form = thisModelForm(postData, instance=thisModelItem)
		context['form'] = form
		
		if form.is_valid():
			post = form.save(commit=False)
			post.updated_by = request.user
			post.save()
			form.save_m2m()
			
			helpers.setPageMessage(request, 'success', f'{capfirst(thisModel._meta.verbose_name)} was edited successfully')
			response = redirect(thisModelListUrl)
		else:
			response = render(request, thisViewTemplate, context)
			
	return response


def doCommonDeleteView(request, thisModel):
	thisId = request.POST.get('id', None)
	thisItem = get_object_or_404(thisModel, id=thisId)
	thisModelListUrl = reverse(f'survey:admin_{thisModel._meta.model_name}_list')
	
	try:
		thisItem.delete()
		helpers.setPageMessage(request, 'success', f'{capfirst(thisModel._meta.verbose_name)} was deleted successfully')
	except Exception as ex:
		helpers.setPageMessage(request, 'error', f'{capfirst(thisModel._meta.verbose_name)} was unable to be deleted because there are associated responses.')
	
	response = redirect(thisModelListUrl)
		
	return response


##
##	/survey/admin/
##
##	Admin home.
##
@user_passes_test(helpers.hasAdminAccess)
def admin_home(request):
	
	context = {
		'leftNavHighlight': 'admin',
		'dataAudits': {},
		'counts': {
			'admins': User.objects.filter(groups__name='admins').count(),
			'buttons': Button.objects.count(),
			'campaigns': Campaign.objects.count(),
			'domains': Domain.objects.count(),
			'languages': Language.objects.count(),
			'projects': Project.objects.count(),
			'questions': Question.objects.count(),
			'releaseNotes': ReleaseNote.objects.count(),
			'surveyInvites': SurveyInvite.objects.count(),
			'surveys': Survey.objects.count(),
			'pages': Page.objects.count(),
			'questionOrders': QuestionOrder.objects.count(),
			'surveyThankyous': SurveyThankyou.objects.count(),
		},
		
	}
	
	response = render(request, 'survey/admin_home.html', context)
	
	helpers.clearPageMessage(request)
	
	return response


##
##	/survey/admin/adminaccess/
##
##	Manage who is in admin group (Admin access control).
##
@user_passes_test(helpers.hasAdminAccess)
def admin_adminaccess(request):
	breadcrumbs = getAdminBreadcrumbBase()
	breadcrumbs.append(
		{ 
			'text': 'Admin center',
			'url': reverse('survey:admin_home')
		}
	)	
	context = {
		'breadcrumbs': breadcrumbs,
		'adminUsers': User.objects.filter(groups__name='admins').order_by('profile__full_name'),
		'leftNavHighlight': 'admin',
	}
	
	return render(request, 'survey/admin_adminaccess.html', context)


##
##	/survey/admin/domain/
##
@user_passes_test(helpers.hasAdminAccess)
def admin_domain_list(request):
	thisModel = Domain
	listItems = thisModel.objects.all().select_related('lead').prefetch_related('project_domain').annotate(campaignCount=Count('project_domain__campaign_project'))
	return doCommonListView(request, thisModel, listItems)


##
##	/survey/admin/domain/add/
##
@user_passes_test(helpers.hasAdminAccess)
def admin_domain_add(request):
	thisModel = Domain
	return doCommonAddItemView(request, thisModel)


##
##	/survey/admin/domain/edit/<id>
##
@user_passes_test(helpers.hasAdminAccess)
def admin_domain_edit(request, id):
	thisModel = Domain
	return doCommonEditItemView(request, thisModel, id, 'name', allowDelete=True)


##
##	/survey/admin/domain/delete/
##
@user_passes_test(helpers.hasAdminAccess)
def admin_domain_delete(request):
	return doCommonDeleteView(request, Domain)


##
##	/survey/admin/project/
##
@user_passes_test(helpers.hasAdminAccess)
def admin_project_list(request):
	thisModel = Project
	listItems = thisModel.objects.all().select_related('domain').prefetch_related('campaign_project').annotate(responseCount=Count('campaign_project__response_campaign'))
	return doCommonListView(request, thisModel, listItems)


##
##	/survey/admin/project/add/
##
@user_passes_test(helpers.hasAdminAccess)
def admin_project_add(request):
	thisModel = Project
	return doCommonAddItemView(request, thisModel)


##
##	/survey/admin/project/edit/<id>
##
@user_passes_test(helpers.hasAdminAccess)
def admin_project_edit(request, id):
	thisModel = Project
	return doCommonEditItemView(request, thisModel, id, 'name', allowDelete=True)


##
##	/survey/admin/project/delete/
##
@user_passes_test(helpers.hasAdminAccess)
def admin_project_delete(request):
	return doCommonDeleteView(request, Project)


##
##	/survey/admin/campaign/
##
@user_passes_test(helpers.hasAdminAccess)
def admin_campaign_list(request):
	thisModel = Campaign
	queryItems = thisModel.objects.all().order_by('-enabled', 'project__name').select_related('survey', 'project').prefetch_related('response_campaign')
	if request.GET.get('question',None):
		queryItems = thisModel.objects.filter(survey__page_survey__question_order_page__question=request.GET.get('question'))
		
	listItems = queryItems.select_related('project').annotate(responseCount=Count('response_campaign'))
	return doCommonListView(request, thisModel, listItems)


##
##	/survey/admin/campaign/add/
##
@user_passes_test(helpers.hasAdminAccess)
def admin_campaign_add(request):
	# Needs special presave.
	thisModel = Campaign
	thisModelForm = globals()[thisModel._meta.object_name + 'Form']
	thisViewTemplate = 'survey/admin_campaign_add.html'
	adminTemplate = 'survey/page_template_admin.html'
	thisModelListUrl = reverse(f'survey:admin_{thisModel._meta.model_name}_list')
	
	breadcrumbs = getAdminBreadcrumbBase()
	breadcrumbs.append(
		{
			'text': capfirst(thisModel._meta.verbose_name_plural),
			'url': thisModelListUrl
		}
	)

	context = {
		'breadcrumbs': breadcrumbs,
		'form': None,
		'modelMeta': thisModel._meta,
		'newItemName': thisModel._meta.verbose_name,
		'questions': Question.objects.all(),
		'adminTemplate': adminTemplate,
		'leftNavHighlight': thisModel._meta.verbose_name_plural,
	}

	if request.method == 'GET':
		form = thisModelForm()
		context['form'] = form

		response = render(request, thisViewTemplate, context)
		helpers.clearPageMessage(request)
		
	elif request.method == 'POST':
		form = thisModelForm(request.POST)
		context['form'] = form
		
		if form.is_valid():
			post = form.save(commit=False)
			post.created_by = request.user
			post.updated_by = request.user
			post.customPreSave()
			post.save()
			form.save_m2m()
			
			# Now create the survey pages and orders with questions.	
			try:
				campaign = post
				
				# Delete all custom questionorders for this campaign and create them with posted data.
				QuestionOrder.objects.filter(campaign=campaign).delete()
				
				for fieldName in request.POST:
					if fieldName.startswith('cqo'):
						nameArr = fieldName.split('_')
						pageNum = nameArr[1]
						questionNum = nameArr[2]
						questionId = nameArr[3]
						
						# If there was a valid question ID passed (non-blank), create question order.
						try:
							question = Question.objects.get(id=questionId)
							surveyPage, created = Page.objects.get_or_create(survey=campaign.survey, page_number=pageNum)
							QuestionOrder.objects.create(
								campaign = campaign,
								page = surveyPage,
								question_number = questionNum,
								question = question,
								
							)
						except Exception as ex:
							print(f'{ex}')
				
				helpers.setPageMessage(request, 'success', 'Campaign was saved successfully')
				response = redirect(thisModelListUrl)
			except Exception as ex:
				helpers.setPageMessage(request, 'error', f'There was a problem saving the campaign: {ex}')
				response = render(request, thisViewTemplate, context)
		else:
			response = render(request, thisViewTemplate, context)
			
	return response
		

##
##	/survey/admin/campaign/edit/<id>
##
@user_passes_test(helpers.hasAdminAccess)
def admin_campaign_edit(request, id):
	thisModel = Campaign
	allowDelete=True
	thisModelItem = get_object_or_404(thisModel, id=id)
	thisModelForm = globals()[thisModel._meta.object_name + 'Form']
	thisViewTemplate = 'survey/admin_campaign_edit.html'
	adminTemplate = 'survey/page_template_admin.html'
	addItemTemplate = 'admin_common_add.html'
	thisModelListUrl = reverse(f'survey:admin_{thisModel._meta.model_name}_list')
	
	try:
		thisModelDeleteUrl = reverse(f'survey:admin_{thisModel._meta.model_name}_delete')
	except:
		thisModelDeleteUrl = None
	
	breadcrumbs = getAdminBreadcrumbBase()
	breadcrumbs.append(
		{
			'text': capfirst(thisModel._meta.verbose_name_plural),
			'url': thisModelListUrl
		}
	)

	context = {
		'breadcrumbs': breadcrumbs,
		'form': None,
		'modelMeta': thisModel._meta,
		'thisModelItem': thisModelItem,
		'itemName': thisModelItem.uid,
		'questions': Question.objects.all(),
		'customQuestions': QuestionOrder.objects.filter(campaign=thisModelItem),
		'adminTemplate': adminTemplate,
		'addItemTemplate': addItemTemplate,
		'thisModelDeleteUrl': thisModelDeleteUrl,
		'allowDelete': allowDelete,
		'leftNavHighlight': thisModel._meta.verbose_name_plural,
		'customJsPath': 'shared/js/admin_campaign.js',
	}

	if request.method == 'GET':
		form = thisModelForm(instance=thisModelItem)
		context['form'] = form

		response = render(request, thisViewTemplate, context)
		helpers.clearPageMessage(request)

	elif request.method == 'POST':
		form = thisModelForm(request.POST, instance=thisModelItem)
		context['form'] = form
		
		if form.is_valid():
			post = form.save(commit=False)
			post.updated_by = request.user
			post.customPreSave()
			post.save()
			form.save_m2m()
			
			# Now create the survey pages and orders with questions.	
			try:
				campaign = post
				
				# Delete all custom questionorders for this campaign and create them with posted data.
				QuestionOrder.objects.filter(campaign=campaign).delete()
				
				for fieldName in request.POST:
					if fieldName.startswith('cqo'):
						nameArr = fieldName.split('_')
						pageNum = nameArr[1]
						questionNum = nameArr[2]
						questionId = nameArr[3]
						
						# If there was a valid question ID passed (non-blank), create question order.
						try:
							question = Question.objects.get(id=questionId)
							surveyPage, created = Page.objects.get_or_create(survey=campaign.survey, page_number=pageNum)
							QuestionOrder.objects.create(
								campaign = campaign,
								page = surveyPage,
								question_number = questionNum,
								question = question,
								
							)
						except Exception as ex:
							print(f'{ex}')
				
				helpers.setPageMessage(request, 'success', 'Campaign was saved successfully')
				response = redirect(thisModelListUrl)
			except Exception as ex:
				helpers.setPageMessage(request, 'error', f'There was a problem saving the campaign: {ex}')
				response = render(request, thisViewTemplate, context)
		else:
			response = render(request, thisViewTemplate, context)
			
	return response



##
##	/survey/admin/campaign/delete/
##
@user_passes_test(helpers.hasAdminAccess)
def admin_campaign_delete(request):
	return doCommonDeleteView(request, Campaign)


##
##	/survey/admin/survey/
##
@user_passes_test(helpers.hasAdminAccess)
def admin_survey_list(request):
	thisModel = Survey
	queryItems = thisModel.objects.all()
	if request.GET.get('question',None):
		queryItems = thisModel.objects.filter(page_survey__question_order_page__question=request.GET.get('question',None))
		
	listItems = queryItems.select_related('language').annotate(campaignCount=Count('campaign_survey',distinct=True), pageCount=Count('page_survey',distinct=True))
	for item in listItems:
		item.questionCount = item.getQuestions().count()
		
	return doCommonListView(request, thisModel, listItems)


##
##	/survey/admin/survey/add/
##
@user_passes_test(helpers.hasAdminAccess)
def admin_survey_add(request):
	# Needs special presave.
	thisModel = Survey
	thisModelForm = globals()[thisModel._meta.object_name + 'Form']
	thisViewTemplate = 'admin_common_add.html'
	adminTemplate = 'survey/page_template_admin.html'
	thisModelListUrl = reverse(f'survey:admin_{thisModel._meta.model_name}_list')
	
	breadcrumbs = getAdminBreadcrumbBase()
	breadcrumbs.append(
		{
			'text': capfirst(thisModel._meta.verbose_name_plural),
			'url': thisModelListUrl
		}
	)

	context = {
		'breadcrumbs': breadcrumbs,
		'form': None,
		'modelMeta': thisModel._meta,
		'newItemName': thisModel._meta.verbose_name,
		'adminTemplate': adminTemplate,
		'leftNavHighlight': thisModel._meta.verbose_name_plural,
	}

	if request.method == 'GET':
		form = thisModelForm()
		context['form'] = form

		response = render(request, thisViewTemplate, context)
		helpers.clearPageMessage(request)
		
	elif request.method == 'POST':
		form = thisModelForm(request.POST)
		context['form'] = form
		
		if form.is_valid():
			post = form.save(commit=False)
			post.created_by = request.user
			post.updated_by = request.user
			post.save()
			form.save_m2m()
			
			# If it's a success and they want JSON back, return the ID and label as JSON,
			#  otherwise we redirect to the list page with a message.
			if request.POST.get('returntype', None) == 'json':
				response = JsonResponse({
					'id': post.id,
					'name': post.__str__()
				}, status=200)
			else:
				helpers.setPageMessage(request, 'success', f'{capfirst(thisModel._meta.verbose_name)} was added successfully')
				response = redirect(thisModelListUrl)
		else:
			response = render(request, thisViewTemplate, context)
			
	return response
		

##
##	/survey/admin/survey/edit/<id>
##
@user_passes_test(helpers.hasAdminAccess)
def admin_survey_edit(request, id):
	thisModel = Survey
	allowDelete=True
	thisModelItem = get_object_or_404(thisModel, id=id)
	thisModelForm = globals()[thisModel._meta.object_name + 'Form']
	thisViewTemplate = 'admin_common_edit.html'
	adminTemplate = 'survey/page_template_admin.html'
	addItemTemplate = 'admin_common_add.html'
	thisModelListUrl = reverse(f'survey:admin_{thisModel._meta.model_name}_list')
	
	try:
		thisModelDeleteUrl = reverse(f'survey:admin_{thisModel._meta.model_name}_delete')
	except:
		thisModelDeleteUrl = None
	
	breadcrumbs = getAdminBreadcrumbBase()
	breadcrumbs.append(
		{
			'text': capfirst(thisModel._meta.verbose_name_plural),
			'url': thisModelListUrl
		}
	)

	context = {
		'breadcrumbs': breadcrumbs,
		'form': None,
		'modelMeta': thisModel._meta,
		'thisModelItem': thisModelItem,
		'itemName': thisModelItem.name,
		'adminTemplate': adminTemplate,
		'addItemTemplate': addItemTemplate,
		'thisModelDeleteUrl': thisModelDeleteUrl,
		'allowDelete': allowDelete,
		'leftNavHighlight': thisModel._meta.verbose_name_plural,
	}

	if request.method == 'GET':
		form = thisModelForm(instance=thisModelItem)
		context['form'] = form
		
		response = render(request, thisViewTemplate, context)
		helpers.clearPageMessage(request)

	elif request.method == 'POST':
		form = thisModelForm(request.POST, instance=thisModelItem)
		context['form'] = form
				
		if form.is_valid():
			post = form.save(commit=False)
			post.updated_by = request.user
			post.save()
			form.save_m2m()
			
			helpers.setPageMessage(request, 'success', f'{capfirst(thisModel._meta.verbose_name)} was edited successfully')
			response = redirect(thisModelListUrl)
		else:
			response = render(request, thisViewTemplate, context)
			
	return response



##
##	/survey/admin/survey/delete/
##
@user_passes_test(helpers.hasAdminAccess)
def admin_survey_delete(request):
	return doCommonDeleteView(request, Survey)
















##
##	/survey/admin/button/
##
@user_passes_test(helpers.hasAdminAccess)
def admin_button_list(request):
	thisModel = Button
	listItems = thisModel.objects.all().annotate(campaignCount=Count('campaign_button'), surveyCount=Count('campaign_button__survey'))
	return doCommonListView(request, thisModel, listItems)


##
##	/button/admin/button/add/
##
@user_passes_test(helpers.hasAdminAccess)
def admin_button_add(request):
	thisModel = Button
	return doCommonAddItemView(request, thisModel, viewTemplate='survey/admin_button_add.html')


##
##	/button/admin/button/edit/<id>
##
@user_passes_test(helpers.hasAdminAccess)
def admin_button_edit(request, id):
	thisModel = Button
	return doCommonEditItemView(request, thisModel, id, 'name', viewTemplate='survey/admin_button_edit.html', allowDelete=True)


##
##	/button/admin/button/delete/
##
@user_passes_test(helpers.hasAdminAccess)
def admin_button_delete(request):
	return doCommonDeleteView(request, Button)


##
##	/survey/admin/language/
##
@user_passes_test(helpers.hasAdminAccess)
def admin_language_list(request):
	thisModel = Language
	listItems = thisModel.objects.all().annotate(surveyCount=Count('survey_language'))
	return doCommonListView(request, thisModel, listItems)


##
##	/language/admin/language/add/
##
@user_passes_test(helpers.hasAdminAccess)
def admin_language_add(request):
	thisModel = Language
	return doCommonAddItemView(request, thisModel)


##
##	/language/admin/language/edit/<id>
##
@user_passes_test(helpers.hasAdminAccess)
def admin_language_edit(request, id):
	thisModel = Language
	return doCommonEditItemView(request, thisModel, id, 'name')


##
##	/language/admin/language/delete/
##
@user_passes_test(helpers.hasAdminAccess)
def admin_language_delete(request):
	return doCommonDeleteView(request, Language)


##
##	/survey/admin/question/
##
@user_passes_test(helpers.hasAdminAccess)
def admin_question_list(request):
	questions = Question.objects.all()
	
	if request.GET.get('survey', None):
		try:
			questions = Survey.objects.get(id=request.GET.get('survey')).getQuestions()
		except:
			pass
	
	# Not perfect, but good enough for now.
	for question in questions:
		surveys = Survey.objects.filter(page_survey__question_order_page__question=question)
		question.surveyCount = surveys.count()
		# Get custom campaign count.
		question.campaignCount = Campaign.objects.filter(survey__in=surveys,question_order_campaign__question=question).count()
		if question.campaignCount == 0:
			question.campaignCount = Campaign.objects.filter(survey__in=surveys,survey__page_survey__question_order_page__question=question).count()
			
	context = {
		'listItems': questions,
		'surveys': Survey.objects.all().only('name'),
		'modelMeta': Question._meta,
		'newItemUrl': reverse('survey:admin_question_add'),
		'leftNavHighlight': 'questions',
	}
	
	response = render(request, 'survey/admin_question_list.html', context)
	helpers.clearPageMessage(request)
	return response


##
##	/question/admin/question/add/
##
@user_passes_test(helpers.hasAdminAccess)
def admin_question_add(request):
	thisModel = Question
	
	def createAnswers(postData):
		postData['answers'] = []
		answerLabels = postData.getlist('answers_label')
		answerValues = postData.getlist('answers_value')
		for i in range(len(answerLabels)):
			if answerValues[i]:
				postData['answers'].append([answerValues[i], answerLabels[i]])
		
		return postData
	
	return doCommonAddItemView(request, thisModel, viewTemplate='survey/admin_question_add.html', customPostProcess=createAnswers)


##
##	/question/admin/question/edit/<id>
##
@user_passes_test(helpers.hasAdminAccess)
def admin_question_edit(request, id):
	thisModel = Question
	
	def createAnswers(postData):
		postData['answers'] = []
		answerLabels = postData.getlist('answers_label')
		answerValues = postData.getlist('answers_value')
		for i in range(len(answerLabels)):
			if answerValues[i]:
				postData['answers'].append([answerValues[i], answerLabels[i]])
		
		return postData
	
	return doCommonEditItemView(request, thisModel, id, 'short_name', viewTemplate='survey/admin_question_edit.html', allowDelete=True, customPostProcess=createAnswers)


##
##	/question/admin/question/delete/
##
@user_passes_test(helpers.hasAdminAccess)
def admin_question_delete(request):
	return doCommonDeleteView(request, Question)


##
##	/survey/admin/question/
##
@user_passes_test(helpers.hasAdminAccess)
def admin_questionorder_list(request):
	thisModel = QuestionOrder
	listItems = thisModel.objects.order_by('page', 'question_number').all().select_related('page', 'question')
	return doCommonListView(request, thisModel, listItems)


##
##	/questionorder/admin/questionorder/add/
##
@user_passes_test(helpers.hasAdminAccess)
def admin_questionorder_add(request):
	thisModel = QuestionOrder
	return doCommonAddItemView(request, thisModel)


##
##	/questionorder/admin/questionorder/edit/<id>
##
@user_passes_test(helpers.hasAdminAccess)
def admin_questionorder_edit(request, id):
	thisModel = QuestionOrder
	return doCommonEditItemView(request, thisModel, id, 'question', allowDelete=True)


##
##	/questionorder/admin/questionorder/delete/
##
@user_passes_test(helpers.hasAdminAccess)
def admin_questionorder_delete(request):
	return doCommonDeleteView(request, QuestionOrder)


##
##	/survey/admin/releasenote/
##
@user_passes_test(helpers.hasAdminAccess)
def admin_releasenote_list(request):
	thisModel = ReleaseNote
	listItems = thisModel.objects.all()
	return doCommonListView(request, thisModel, listItems)


##
##	/survey/admin/releasenote/add/
##
@user_passes_test(helpers.hasAdminAccess)
def admin_releasenote_add(request):
	thisModel = ReleaseNote
	return doCommonAddItemView(request, thisModel)


##
##	/survey/admin/releasenote/edit/<id>
##
@user_passes_test(helpers.hasAdminAccess)
def admin_releasenote_edit(request, id):
	thisModel = ReleaseNote
	return doCommonEditItemView(request, thisModel, id, 'release_number', allowDelete=True)


##
##	/survey/admin/releasenote/delete/
##
@user_passes_test(helpers.hasAdminAccess)
def admin_releasenote_delete(request):
	return doCommonDeleteView(request, ReleaseNote)


##
##	/survey/admin/surveyinvite/
##
@user_passes_test(helpers.hasAdminAccess)
def admin_surveyinvite_list(request):
	thisModel = SurveyInvite
	listItems = thisModel.objects.all()
	return doCommonListView(request, thisModel, listItems)


##
##	/survey/admin/surveyinvite/add/
##
@user_passes_test(helpers.hasAdminAccess)
def admin_surveyinvite_add(request):
	thisModel = SurveyInvite
	return doCommonAddItemView(request, thisModel)


##
##	/survey/admin/surveyinvite/edit/<id>
##
@user_passes_test(helpers.hasAdminAccess)
def admin_surveyinvite_edit(request, id):
	thisModel = SurveyInvite
	return doCommonEditItemView(request, thisModel, id, 'name', allowDelete=True)


##
##	/survey/admin/surveyinvite/delete/
##
@user_passes_test(helpers.hasAdminAccess)
def admin_surveyinvite_delete(request):
	return doCommonDeleteView(request, SurveyInvite)


##
##	/survey/admin/surveythankyou/
##
@user_passes_test(helpers.hasAdminAccess)
def admin_surveythankyou_list(request):
	thisModel = SurveyThankyou
	listItems = thisModel.objects.all()
	return doCommonListView(request, thisModel, listItems)


##
##	/survey/admin/surveythankyou/add/
##
@user_passes_test(helpers.hasAdminAccess)
def admin_surveythankyou_add(request):
	thisModel = SurveyThankyou
	return doCommonAddItemView(request, thisModel)


##
##	/survey/admin/surveythankyou/edit/<id>
##
@user_passes_test(helpers.hasAdminAccess)
def admin_surveythankyou_edit(request, id):
	thisModel = SurveyThankyou
	return doCommonEditItemView(request, thisModel, id, 'name', allowDelete=True)


##
##	/survey/admin/surveythankyou/delete/
##
@user_passes_test(helpers.hasAdminAccess)
def admin_surveythankyou_delete(request):
	return doCommonDeleteView(request, SurveyThankyou)


##
##	/survey/admin/releasenotes/
##
@user_passes_test(helpers.hasAdminAccess)
def admin_releasenotes_list(request):
	thisModel = ReleaseNote
	listItems = thisModel.objects.all()
	return doCommonListView(request, thisModel, listItems)


##
##	/survey/admin/releasenotes/add/
##
@user_passes_test(helpers.hasAdminAccess)
def admin_releasenotes_add(request):
	thisModel = ReleaseNote
	return doCommonAddItemView(request, thisModel)


##
##	/survey/admin/releasenotes/edit/<id>
##
@user_passes_test(helpers.hasAdminAccess)
def admin_releasenotes_edit(request, id):
	thisModel = ReleaseNote
	return doCommonEditItemView(request, thisModel, id, 'release_number', allowDelete=True)


##
##	/survey/admin/releasenotes/delete/
##
@user_passes_test(helpers.hasAdminAccess)
def admin_releasenotes_delete(request):
	return doCommonDeleteView(request, ReleaseNote)


##
##	/survey/admin/page/
##
@user_passes_test(helpers.hasAdminAccess)
def admin_page_list(request):
	thisModel = Page
	listItems = thisModel.objects.order_by('survey__name', 'page_number').all().annotate(numQuestions=Count('question_order_page'))
	for page in listItems:
		page.numCampaigns = Campaign.objects.filter(survey=page.survey).distinct().count()
	return doCommonListView(request, thisModel, listItems)


##
##	/survey/admin/page/add/
##
@user_passes_test(helpers.hasAdminAccess)
def admin_page_add(request):
	thisModel = Page
	return doCommonAddItemView(request, thisModel)


##
##	/survey/admin/page/edit/<id>
##
@user_passes_test(helpers.hasAdminAccess)
def admin_page_edit(request, id):
	thisModel = Page
	return doCommonEditItemView(request, thisModel, id, 'survey', allowDelete=True)


##
##	/survey/admin/page/delete/
##
@user_passes_test(helpers.hasAdminAccess)
def admin_page_delete(request):
	return doCommonDeleteView(request, Page)


##
##	/survey/admin/surveybuilder/
##
@user_passes_test(helpers.hasAdminAccess)
def admin_surveybuilder_list(request):
	surveys = Survey.objects.all().order_by('name').prefetch_related('page_survey__question_order_page__question').select_related('language').annotate(campaignCount=Count('campaign_survey',distinct=True))
	
	for survey in surveys:
		for page in survey.page_survey.all():
			page.questionOrders = page.getAllQuestionOrders(None)
		
	context = {
		'surveys': surveys,
		'leftNavHighlight': 'survey builders',
	}
	
	response = render(request, 'survey/admin_surveybuilder_list.html', context)
	helpers.clearPageMessage(request)
	return response
	

##
##	/survey/admin/surveybuilder/add/
##
@user_passes_test(helpers.hasAdminAccess)
def admin_surveybuilder_add(request):
	thisViewTemplate = 'survey/admin_surveybuilder_add.html'
	adminTemplate = 'survey/page_template_admin.html'
	thisModelListUrl = reverse('survey:admin_surveybuilder_list')
	
	breadcrumbs = getAdminBreadcrumbBase()
	breadcrumbs.append(
		{
			'text': 'Survey builder',
			'url': thisModelListUrl
		}
	)
	
	context = {
		'breadcrumbs': breadcrumbs,
		'form': None,
		'questions': Question.objects.all(),
		'adminTemplate': adminTemplate,
		'leftNavHighlight': 'survey builders',
	}
	
	if request.method == 'GET':
		form = SurveyForm()
		context['form'] = form
	
		response = render(request, thisViewTemplate, context)
		helpers.clearPageMessage(request)
		
	elif request.method == 'POST':
		form = SurveyForm(request.POST)
		context['form'] = form
		
		if form.is_valid():
			post = form.save(commit=False)
			post.created_by = request.user
			post.updated_by = request.user
			post.save()
			form.save_m2m()
		else:
			helpers.setPageMessage(request, 'error', f'There was a problem saving survey changes: {ex}')
			response = render(request, thisViewTemplate, context)

		# Now create the survey pages and orders with questions.	
		try:
			survey = post
			
			# Delete all questionorders and pages for this survey and create them with posted data.
			QuestionOrder.objects.filter(page__survey=survey).delete()
			Page.objects.filter(survey=survey).delete()
			
			for fieldName in request.POST:
				if fieldName.startswith('qo'):
					# Pages already exist right now thur "Survey" admin.
					# Future use, they will create pages in here and will need to create pages first.
					nameArr = fieldName.split('_')
					pageNum = nameArr[1][1:]
					questionNum = nameArr[2][1:]
					
					# If there was a valid question ID passed (non-blank), create question order.
					try:
						question = Question.objects.get(id=request.POST.get(fieldName))
						page, created = Page.objects.get_or_create(survey=survey, page_number=pageNum)
						QuestionOrder.objects.create(
							page = page,
							question = question,
							question_number = questionNum
						)
					except Exception as ex:
						pass
			
			helpers.setPageMessage(request, 'success', 'Survey was edited successfully')
			response = redirect(thisModelListUrl)
		except Exception as ex:
			helpers.setPageMessage(request, 'error', f'There was a problem saving survey changes: {ex}')
			response = render(request, thisViewTemplate, context)
	
	return response


##
##	/survey/admin/surveybuilder/edit/<id>
##
@user_passes_test(helpers.hasAdminAccess)
def admin_surveybuilder_edit(request, id):
	#survey = get_object_or_404(Survey, id=id)
	try:
		survey = Survey.objects.filter(id=id).prefetch_related('page_survey__question_order_page__question')[0]
	except:
		return render(request, '404.html', {}, status=404)
	
	for page in survey.page_survey.all():
		page.questionOrders = page.getAllQuestionOrders(None)
	
	thisViewTemplate = 'survey/admin_surveybuilder_edit.html'
	adminTemplate = 'survey/page_template_admin.html'
	thisModelListUrl = reverse('survey:admin_surveybuilder_list')
	
	breadcrumbs = getAdminBreadcrumbBase()
	breadcrumbs.append(
		{
			'text': 'Survey builder',
			'url': thisModelListUrl,
		}
	)

	context = {
		'breadcrumbs': breadcrumbs,
		'form': None,
		'survey': survey,
		'questions': Question.objects.all(),
		'adminTemplate': adminTemplate,
		'leftNavHighlight': 'survey builders',
	}

	if request.method == 'GET':
		form = SurveyForm(instance=survey)
		context['form'] = form
		
		response = render(request, thisViewTemplate, context)
		helpers.clearPageMessage(request)
		
	elif request.method == 'POST':
		form = SurveyForm(request.POST, instance=survey)
		context['form'] = form
		
		# Save the survey info part.
		if form.is_valid():
			post = form.save(commit=False)
			post.updated_by = request.user
			post.save()
			form.save_m2m()
		else:
			helpers.setPageMessage(request, 'error', f'There was a problem saving survey changes: {ex}')
			response = render(request, thisViewTemplate, context)
		
		# Now create the survey pages and orders with questions.	
		try:
			# Delete all questionorders and pages for this survey and create them with posted data.
			QuestionOrder.objects.filter(page__survey=survey).delete()
			Page.objects.filter(survey=survey).delete()
			
			for fieldName in request.POST:
				if fieldName.startswith('qo'):
					# Pages already exist right now thur "Survey" admin.
					# Future use, they will create pages in here and will need to create pages first.
					nameArr = fieldName.split('_')
					pageNum = nameArr[1][1:]
					questionNum = nameArr[2][1:]
					
					# If there was a valid question ID passed (non-blank), create question order.
					try:
						question = Question.objects.get(id=request.POST.get(fieldName))
						page, created = Page.objects.get_or_create(survey=survey, page_number=pageNum)
						QuestionOrder.objects.create(
							page = page,
							question = question,
							question_number = questionNum
						)
					except Exception as ex:
						pass
			
			helpers.setPageMessage(request, 'success', 'Survey was edited successfully')
			response = redirect(thisModelListUrl)
		except Exception as ex:
			helpers.setPageMessage(request, 'error', f'There was a problem saving survey changes: {ex}')
			response = render(request, thisViewTemplate, context)
	
	return response


##
##	/survey/admin/surveybuilder/delete/
##
@user_passes_test(helpers.hasAdminAccess)
def admin_surveybuilder_delete(request):
	return doCommonDeleteView(request, QuestionOrder)

