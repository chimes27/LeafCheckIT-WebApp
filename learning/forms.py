from django import forms
from .models import ImageDetails, UserTestResults, User
#from django.contrib.auth.models import User

class ImageDetailsForm(forms.ModelForm):
	class Meta:
		model = ImageDetails
		fields= ('category', 'image', 'status')
		widgets = {
			'status': forms.HiddenInput(),
		}
		
	'''
	def clean_image(self):
		image = self.cleaned_data.get("image", False)
		ftype = magic.from_buffer(image.read())
		if not "PNG" in ftype or not "JPG" in ftype:
			raise ValidationError("Please upload file in PNG or JPG format")
		return image	
	'''

class UserTestResultsForm(forms.ModelForm):
	class Meta:
		model = UserTestResults
		fields = ('image','classifierResult','status','user')
		widgets = {
			'status': forms.HiddenInput(),
			'classifierResult': forms.HiddenInput(),
			'user': forms.HiddenInput(),
		}		


class signupForm(forms.ModelForm):
	confirm_password = forms.CharField(widget=forms.PasswordInput())
	password = forms.CharField(widget=forms.PasswordInput())
	class Meta:
		model = User
		fields = ('firstName','lastName','email')
		labels = {
			#'username': 'User Name',
			'firstName' : 'First Name',
			'lastName': 'Last Name',
			'email': 'Email'
		}
	def clean_password2(self):
		password1 = self.cleaned_data.get("password")
		password2 = self.cleaned_data.get("confirm_password")
		if password1 and password2 and password1 != password2:
			raise forms.ValidationError(self.error_messages['password_mismatch'], code='password_mismatch',)
		return password2

	def save(self, commit=True):
		self.user = super(signupForm, self).save(commit=False)
		self.user.set_password(self.cleaned_data['password'])
		if commit:
			self.user.save()
		return self.user

'''
class signupForm(forms.ModelForm):
	confirm_password = forms.CharField(widget=forms.PasswordInput())
	class Meta:
		model = User
		fields = ('firstName','lastName','email','password')
		labels = {
			#'username': 'User Name',
			'firstName' : 'First Name',
			'lastName': 'Last Name',
			'email': 'Email',
			'password': 'Password'

		}
		
		widgets = {
			'password': forms.PasswordInput,
		}
		
		def __init__(self, user, *args, **kwargs):
			self.user = user
			super(signupForm,self).__init__(*args, **kwargs)

		def clean(self):
			self.cleaned_data = super(signupForm,self).clean()
			return self.cleaned_data


		def save(self, commit=True):
			#user = super(signupForm,self).save(commit=False)
			self.user.set_password(self.cleaned_data['password'])
			if commit:
				self.user.save()
			return self.user
'''	

class loginForm(forms.Form):
	email = forms.EmailField(widget = forms.widgets.TextInput)
	password = forms.CharField(widget = forms.widgets.PasswordInput)
	
	class Meta:
		fields = ['email', 'password']
		

