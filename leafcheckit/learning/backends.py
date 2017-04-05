from django.contrib.auth.hashers import check_password
from django.core.exceptions import ObjectDoesNotExist
#from .models import MyUser
from .models import User

class EmailAuthBackend(object):

	def authenticate(self, email=None, password=None):
		try:
			user = User.objects.get(email=email)
			pwd_valid = check_password(password, user.password)
			if pwd_valid:
				return user
			else:
				return None
		except User.DoesNotExist:
			return None
	
	
	'''
	def authenticate(self, email=None, password=None):
		try:
			User = settings.AUTH_USER_MODEL
			user = User.objects.get(email=email, password=password)
			#user = User.objects.get(email=email, password=password)
			return user
		except:
			return None
	'''

	def get_user(self, user_id):
		try:
		 	user = User.objects.get(pk=user_id)
			if user.is_active:
				return user
			return None
		except User.DoesNotExist:
			return None
