import json
from copy import copy

from .models import *
from .helpers import createNewUser


def createSampleSurveys():
	user = getScriptUser()
	
	adminGroup, created = Group.objects.get_or_create(name='admins')
	
	Campaign.objects.all().delete()
	Survey.objects.all().delete()
	SurveyInvite.objects.all().delete()
	SurveyThankyou.objects.all().delete()
	Page.objects.all().delete()
	Question.objects.all().delete()
	QuestionOrder.objects.all().delete()
	Language.objects.all().delete()
	Button.objects.all().delete()
	
	
	language, created = Language.objects.get_or_create(
		name = 'English',
		created_by = user,
		updated_by = user,
	)
	
	button, created = Button.objects.get_or_create(
		name = 'Default feedback',
		text = 'Feedback',
		background_color = '#2571eb',
		position = 'right',
		offset = 50,
		created_by = user,
		updated_by = user,
	)
	
	project, created = Project.objects.get_or_create(
		name = 'Demo project 1',
		created_by = user,
		updated_by = user,
	)
	
	survey = Survey.objects.create(
		name = 'Survey with all question types',
		title = 'Personalize your Lamborghini order',
		language = language,
		created_by = user,
		updated_by = user,
	)
	
	surveyInvite = SurveyInvite.objects.create(
		created_by = user,
		updated_by = user,
		name = 'Default invite',
		message = 'When you\'re done with the {projectname} site, would you be willing to take a quick survey?'
	)
	
	campaign = Campaign(
		project = project,
		survey = survey,
		created_by = user,
		updated_by = user,
		enabled = True,
		survey_invite = surveyInvite,
	)
	campaign.customPreSave()
	campaign.save()
	
	page1 = Page.objects.create(
		survey = survey,
		page_number = 1,
	)
	page2 = Page.objects.create(
		survey = survey,
		page_number = 2,
	)
	page3 = Page.objects.create(
		survey = survey,
		page_number = 3,
	)
	
	# Questions
	questions = []
	
	q1 = Question.objects.create(
		short_name = 'favorite_color',
		question_text = 'If you had a Lamborghini, which color would it be',
		answers = [
			('red','Red'),
			('orange','Orange'),
			('green','Green'),
			('blue','Blue'),
			('white','White'),
			('black','Black'),
		],
		required = True,
		type = 'radio',		
	)
	questions.append(q1)
	
	q = copy(q1)
	q.pk = None
	q.short_name += '2'
	q.layout = 'horizontal'
	q.required = False
	q.save()
	questions.append(q)

	q2 = Question.objects.create(
		short_name = 'want_a_lambo',
		question_text = 'How much would you like to have a lambo?',
		answers = [
			(1,1),
			(2,2),
			(3,3),
			(4,4),
			(5,5),
			(6,6),
			(7,7),
		],
		required = True,
		type = 'radio',	
		layout = 'horizontal',
		anchor_text_beginning = 'Waste of $',
		anchor_text_end = 'Fuck ya!',
	)
	questions.append(q2)
		
	q = copy(q1)
	q.pk = None
	q.short_name += '3'
	q.question_text = 'What are your other favorite colors'
	q.type = 'checkbox'
	q.layout = 'vertical'
	q.required = True
	q.save()
	questions.append(q)
	
	q = copy(q1)
	q.pk = None
	q.short_name += '4'
	q.question_text = 'What are your other favorite colors'
	q.type = 'checkbox'
	q.required = False
	q.layout = 'horizontal'
	q.save()
	questions.append(q)
	
	q = copy(q1)
	q.pk = None
	q.short_name += '5'
	q.type = 'select'
	q.layout = 'vertical'
	q.save()
	questions.append(q)
	
	q = copy(q1)
	q.pk = None
	q.short_name += '6'
	q.question_text = 'What are your other favorite colors'
	q.type = 'selectmultiple'
	q.layout = 'vertical'
	q.save()
	questions.append(q)
	
	q = Question.objects.create(
		short_name = 'number_lambos',
		question_text = 'Enter the # of lambos you want',
		type = 'number',
	)
	questions.append(q)
	
	q = Question.objects.create(
		short_name = 'delivery_date',
		question_text = 'When would you like your lambo delivered?',
		type = 'date',
	)
	questions.append(q)
	
	q = Question.objects.create(
		short_name = 'message',
		message_text = 'You are almost finished with your new lambo order. Only a few more fields left and your dream will come true. This is a message type which allows you to enter random text in wherever you want.',
		type = 'message',
	)
	questions.append(q)
	
	q = Question.objects.create(
		short_name = 'dealer_name',
		question_text = 'What is the name of the dealer you want it delivered to?',
		placeholder_text = 'e.g.  Bob\'s Bitchin\' Lambo Lot',
		type = 'textinput',
	)
	questions.append(q)
	
	q = Question.objects.create(
		short_name = 'dealer_url',
		question_text = 'URL of the dealer online?',
		type = 'url',
	)
	questions.append(q)
	
	
	q = Question.objects.create(
		short_name = 'special_requests',
		question_text = 'Special requests for your lambo?',
		type = 'textarea',
	)
	questions.append(q)
	
	q = Question.objects.create(
		short_name = 'email',
		question_text = 'What email would you like order updates sent to?',
		type = 'email',
		required = False,
	)
	questions.append(q)
	
	
	# Question orders.
	for idx, question in enumerate(questions):
		if idx > 10:
			page = page3
		elif idx > 5:
			page = page2
		else:
			page = page1
			
		questionOrder = QuestionOrder.objects.create(
			page = page,
			question = question,
			question_number = idx+1,
		)
	
	
	####### VOTE SURVEY #######
	
	
	voteSurvey = Survey.objects.create(
		name = 'Standard VotE - nps/umux/improvement',
		title = 'We\'d love to hear your feedback, to help us improve the {projectname} site',
		language = language,
		survey_type = 'vote',
		created_by = user,
		updated_by = user,
	)
	
	voteThankyou = SurveyThankyou.objects.create(
		created_by = user,
		updated_by = user,
		name = 'VotE default thankyou',
		message = 'Thanks for the feedback! It\'s people like you who help make our products great.'
	)
	
	voteCampaign = Campaign(
		project = project,
		survey = voteSurvey,
		limit_one_submission = True,
		created_by = user,
		updated_by = user,
		enabled = True,
		survey_trigger_type = 'intercept',
		survey_thankyou = voteThankyou,
	)
	voteCampaign.customPreSave()
	voteCampaign.save()
	
	votePage1 = Page.objects.create(
		survey = voteSurvey,
		page_number = 1,
	)
	
	votePage2 = Page.objects.create(
		survey = voteSurvey,
		page_number = 2,
	)
	
	q = Question.objects.create(
		short_name = 'nps',
		question_text = 'How likely are you to recommend {projectname} to your colleagues?',
		answers = [
			(0,0),
			(1,1),
			(2,2),
			(3,3),
			(4,4),
			(5,5),
			(6,6),
			(7,7),
			(8,8),
			(9,9),
			(10,10),
		],
		required = True,
		anchor_text_beginning = 'Not at all likely',
		anchor_text_end = 'Extremely likely',
		type = 'radio',
		layout = 'horizontal',
	)
	questionOrder = QuestionOrder.objects.create(
		page = votePage1,
		question = q,
		question_number = 1,
	)
	
	q = Question.objects.create(
		short_name = 'requirements_met',
		question_text = '{projectname} capabilities meet my requirements',
		answers = [
			(1,1),
			(2,2),
			(3,3),
			(4,4),
			(5,5),
			(6,6),
			(7,7),
		],
		required = True,
		anchor_text_beginning = 'Strongly disagree',
		anchor_text_end = 'Strongly agree',
		type = 'radio',
		layout = 'horizontal',
	)
	questionOrder = QuestionOrder.objects.create(
		page = votePage1,
		question = q,
		question_number = 2,
	)
	
	q = Question.objects.create(
		short_name = 'ease_of_use',
		question_text = '{projectname} is easy to use',
		answers = [
			(1,1),
			(2,2),
			(3,3),
			(4,4),
			(5,5),
			(6,6),
			(7,7),
		],
		required = True,
		anchor_text_beginning = 'Strongly disagree',
		anchor_text_end = 'Strongly agree',
		type = 'radio',
		layout = 'horizontal',
	)
	questionOrder = QuestionOrder.objects.create(
		page = votePage1,
		question = q,
		question_number = 3,
	)
	
	q = Question.objects.create(
		short_name = 'suggestions_to_improve',
		question_text = 'What can {projectname} do to improve?',
		required = False,
		type = 'textarea',
	)
	questionOrder = QuestionOrder.objects.create(
		page = votePage1,
		question = q,
		question_number = 4,
	)
	
	q = Question.objects.create(
		short_name = 'primary_goal',
		question_text = 'What was your primary goal using {projectname} today?',
		required = False,
		type = 'textinput',
	)
	questionOrder = QuestionOrder.objects.create(
		page = votePage2,
		question = q,
		question_number = 1,
	)
	
	q = Question.objects.create(
		short_name = 'goal_completed',
		question_text = 'Did you accomplish your primary goal?',
		required = False,
		type = 'radio',
		answers = [
			('yes','Yes'),
			('no','No'),
			('partially','Partially'),
		],
		layout = 'vertical',
	)
	questionOrder = QuestionOrder.objects.create(
		page = votePage2,
		question = q,
		question_number = 2,
	)
	
	q = Question.objects.create(
		short_name = 'email',
		question_text = 'Provide your email if you would like a follow up, if appropriate',
		required = False,
		type = 'email',
	)
	questionOrder = QuestionOrder.objects.create(
		page = votePage2,
		question = q,
		question_number = 3,
	)
	
	
	####### Feedback SURVEY #######
	
	
	feedbackSurvey = Survey.objects.create(
		name = 'Standard feedback',
		title = '',
		survey_type = 'feedback',
		language = language,
		created_by = user,
		updated_by = user,
	)
	
	feedbackThankyou = SurveyThankyou.objects.create(
		created_by = user,
		updated_by = user,
		name = 'Feedback default thankyou',
		message = 'Thanks for the feedback! Know that we\'re handling it with care.'
	)
	
	feedbackCampaign = Campaign(
		project = project,
		survey = feedbackSurvey,
		limit_one_submission = False,
		created_by = user,
		updated_by = user,
		enabled = True,
		survey_trigger_type = 'button',
		button = button,
		survey_thankyou = feedbackThankyou,
	)
	feedbackCampaign.customPreSave()
	feedbackCampaign.save()
	
	p1 = Page.objects.create(
		survey = feedbackSurvey,
		page_number = 1,
	)
	
	
	q = Question.objects.create(
		short_name = 'rating',
		question_text = 'How would you rate {projectname} overall',
		answers = [
			(1,1),
			(2,2),
			(3,3),
			(4,4),
			(5,5),
		],
		required = True,
		anchor_text_beginning = 'Poor',
		anchor_text_end = 'Great',
		type = 'stars',
		layout = 'horizontal',
	)
	questionOrder = QuestionOrder.objects.create(
		page = p1,
		question = q,
		question_number = 1,
	)
	
	q = Question.objects.create(
		short_name = 'feedback_type',
		question_text = 'Type of feedback',
		answers = [
			('suggestion','Suggestion'),
			('compliment','Compliment'),
			('bug_issue','Bug/issue'),
		],
		required = False,
		type = 'select',
	)
	questionOrder = QuestionOrder.objects.create(
		page = p1,
		question = q,
		question_number = 2,
	)
		
	q = Question.objects.create(
		short_name = 'comments',
		question_text = 'Feedback',
		type = 'textarea',
	)
	questionOrder = QuestionOrder.objects.create(
		page = p1,
		question = q,
		question_number = 3,
	)
	
	q = Question.objects.create(
		short_name = 'email',
		question_text = 'Provide your email if you would like a follow up, if appropriate',
		required = False,
		placeholder_text = 'youremail@domain.com',
		type = 'email',
	)
	questionOrder = QuestionOrder.objects.create(
		page = p1,
		question = q,
		question_number = 4,
	)
		
