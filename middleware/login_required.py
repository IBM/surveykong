from django.contrib.auth.decorators import login_required
from django.urls import reverse


def login_exempt(view):
	view.login_exempt = True
	return view


class LoginRequiredMiddleware:
	def __init__(self, get_response):
		self.get_response = get_response

	def __call__(self, request):
		return self.get_response(request)

	def process_view(self, request, view_func, view_args, view_kwargs):
		if getattr(view_func, 'login_exempt', False):
			return

		if request.user.is_authenticated:
			return
 
		# Exclude SSO OIDC URLs to prevent loop. Uncomment this line if you're using SSO:
		#if request.path == reverse('oidc_authentication_init') or request.path == reverse('oidc_authentication_callback'):
		#	return
		
		# Exclude sign in/signout to prevent loop
		if request.path == reverse('survey:signin') or request.path == reverse('survey:signout'):
			return

		return login_required(view_func)(request, *view_args, **view_kwargs)