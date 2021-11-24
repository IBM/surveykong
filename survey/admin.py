from django.contrib import admin

from .models import Language, Button, Domain, Project, Survey, SurveyInvite, SurveyThankyou, Campaign, Page, Question, QuestionOrder, Response, CampaignUserInfo, Profile, BannerNotification, ReleaseNote


@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
	list_display = (
		'id',
		'created_by',
		'created_at',
		'updated_by',
		'updated_at',
		'name',
	)
	list_filter = ('created_by', 'created_at', 'updated_by', 'updated_at')
	search_fields = ('name',)
	date_hierarchy = 'created_at'


@admin.register(Button)
class ButtonAdmin(admin.ModelAdmin):
	list_display = (
		'id',
		'created_by',
		'created_at',
		'updated_by',
		'updated_at',
		'feedback_default',
		'name',
		'text',
		'background_color',
		'text_color',
		'position',
		'offset',
	)
	list_filter = (
		'created_by',
		'created_at',
		'updated_by',
		'updated_at',
		'feedback_default',
	)
	search_fields = ('name',)
	date_hierarchy = 'created_at'


@admin.register(Domain)
class DomainAdmin(admin.ModelAdmin):
	list_display = (
		'id',
		'created_by',
		'created_at',
		'updated_by',
		'updated_at',
		'name',
		'lead',
	)
	list_filter = (
		'created_by',
		'created_at',
		'updated_by',
		'updated_at',
		'lead',
	)
	search_fields = ('name',)
	date_hierarchy = 'created_at'


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
	list_display = (
		'id',
		'created_by',
		'created_at',
		'updated_by',
		'updated_at',
		'active',
		'uid',
		'name',
		'domain',
		'display_name',
		'contact',
		'comments',
	)
	list_filter = ('created_at', 'updated_at', 'active')
	raw_id_fields = ('created_by', 'updated_by', 'domain', 'contact')
	search_fields = ('name',)
	date_hierarchy = 'created_at'


@admin.register(Survey)
class SurveyAdmin(admin.ModelAdmin):
	list_display = (
		'id',
		'created_by',
		'created_at',
		'updated_by',
		'updated_at',
		'survey_type',
		'feedback_default',
		'name',
		'title',
		'language',
		'comments',
	)
	list_filter = (
		'created_by',
		'created_at',
		'updated_by',
		'updated_at',
		'feedback_default',
		'language',
	)
	search_fields = ('name',)
	date_hierarchy = 'created_at'


@admin.register(SurveyInvite)
class SurveyInviteAdmin(admin.ModelAdmin):
	list_display = (
		'id',
		'created_by',
		'created_at',
		'updated_by',
		'updated_at',
		'name',
		'message',
	)
	list_filter = ('created_by', 'created_at', 'updated_by', 'updated_at')
	search_fields = ('name',)
	date_hierarchy = 'created_at'


@admin.register(SurveyThankyou)
class SurveyThankyouAdmin(admin.ModelAdmin):
	list_display = (
		'id',
		'created_by',
		'created_at',
		'updated_by',
		'updated_at',
		'name',
		'message',
	)
	list_filter = ('created_by', 'created_at', 'updated_by', 'updated_at')
	search_fields = ('name',)
	date_hierarchy = 'created_at'


@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
	list_display = (
		'id',
		'created_by',
		'created_at',
		'updated_by',
		'updated_at',
		'enabled',
		'active',
		'uid',
		'key',
		'project',
		'survey',
		'survey_invite',
		'survey_thankyou',
		'slack_notification_url',
		'survey_trigger_type',
		'button',
		'mouseout_trigger',
		'url_accessible',
		'visitor_percent',
		'limit_one_submission',
		'limit_one_submission_days',
		'seconds_on_page_delay',
		'repeat_visitors_only',
		'page_view_count',
		'start_date',
		'stop_date',
		'response_count_limit',
		'latest_response_date',
		'response_count',
		'unique_visitor_count',
		'intercept_shown_count',
		'comments',
	)
	list_filter = (
		'created_by',
		'created_at',
		'updated_by',
		'updated_at',
		'enabled',
		'active',
		'project',
		'survey',
		'survey_invite',
		'survey_thankyou',
		'button',
		'mouseout_trigger',
		'url_accessible',
		'limit_one_submission',
		'repeat_visitors_only',
		'start_date',
		'stop_date',
		'latest_response_date',
	)
	date_hierarchy = 'created_at'


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
	list_display = ('id', 'survey', 'page_number')
	list_filter = ('survey',)


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
	list_display = (
		'id',
		'short_name',
		'question_text',
		'question_text_past_tense',
		'required',
		'shared',
		'type',
		'layout',
		'message_text',
		'placeholder_text',
		'character_limit',
		'anchor_text_beginning',
		'anchor_text_end',
		'answers',
		'default_answer',
		'parent_question',
		'parent_answer',
		'parent_answer_action',
	)
	list_filter = ('required', 'shared')


@admin.register(QuestionOrder)
class QuestionOrderAdmin(admin.ModelAdmin):
	list_display = ('id', 'page', 'question', 'question_number')


@admin.register(Response)
class ResponseAdmin(admin.ModelAdmin):
	list_display = (
		'id',
		'created_at',
		'uid',
		'campaign',
		'uuid',
		'raw_data',
	)
	list_filter = ('created_at', 'campaign')
	date_hierarchy = 'created_at'


@admin.register(CampaignUserInfo)
class CampaignUserInfoAdmin(admin.ModelAdmin):
	list_display = (
		'id',
		'uuid',
		'campaign',
		'view_count',
		'session_count',
		'intercept_shown_at',
		'take_later_at',
		'email_link_at',
		'submitted_at',
		'reset_date',
	)
	list_filter = (
		'intercept_shown_at',
		'take_later_at',
		'email_link_at',
		'submitted_at',
		'reset_date',
	)
	raw_id_fields = ('campaign',)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
	list_display = ('id', 'inactive', 'user', 'full_name', 'image')
	list_filter = ('inactive',)
	raw_id_fields = ('user',)


@admin.register(BannerNotification)
class BannerNotificationAdmin(admin.ModelAdmin):
	list_display = ('id', 'name', 'active', 'banner_text', 'banner_type')
	list_filter = ('active',)
	search_fields = ('name',)


@admin.register(ReleaseNote)
class ReleaseNoteAdmin(admin.ModelAdmin):
	list_display = (
		'id',
		'created_at',
		'created_by',
		'updated_at',
		'updated_by',
		'release_number',
		'date',
		'notes',
	)
	list_filter = (
		'created_at',
		'created_by',
		'updated_at',
		'updated_by',
		'date',
	)
	date_hierarchy = 'created_at'
	
