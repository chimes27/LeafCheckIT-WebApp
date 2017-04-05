from django.conf import settings
from rest_framework import authentication
from rest_framework import exceptions
from rest_framework.authtoken.models import Token

class RestAuthentication(authentication.BaseAuthentication):

	def authenticate(self, request):
		email = request.META.get('email')
		password = request.META.get('password')
		try:
			User = settings.AUTH_USER_MODEL
			user = User.objects.get(email=email, password=password)
			#token = Token.objects.create(user=user)
			return (user, None)
		except:
			raise exceptions.AuthenticationFailed('Wrong email or password')

