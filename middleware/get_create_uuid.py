from django.utils.crypto import get_random_string

class getOrCreateUuid:
	def __init__(self, get_response):
		self.get_response = get_response
		
	def __call__(self, request):
		try:
			request.session['uuid']
		except:
			request.session['uuid'] = get_random_string(24)
		return self.get_response(request)
