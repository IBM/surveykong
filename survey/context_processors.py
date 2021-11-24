from django.conf import settings

def app_settings(request):
	'''
	Props here get sent to every view, as direct variable to use.
	'''
	return {
		'DATABASE_HOST': settings.DATABASES['default']['HOST'],
		'CDN_FILES_URL': settings.CDN_FILES_URL,
	}
