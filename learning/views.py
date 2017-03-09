from django.shortcuts import render, render_to_response, redirect, get_object_or_404
from django.http import HttpResponse
from .forms import ImageDetailsForm, UserTestResultsForm, signupForm, loginForm
from .models import *
from django.contrib import messages
from django.utils.safestring import mark_safe
from django.conf import settings
import os
from .checkitBackend import Classify as classifier
from django.contrib.auth import login as django_login, logout as django_logout, authenticate
from .backends import EmailAuthBackend
from django.contrib.auth.decorators import login_required
from .serializers import *

from rest_framework import mixins
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import ParseError
from .auth import RestAuthentication

def index(request):
	index = 'index.html'
	return render(request,index)

def startclassify(request):
	if request.method == 'POST':
		form = UserTestResultsForm(request.POST, request.FILES)
		if form.is_valid():
			imageName = form.instance.image.name
			if imageName.endswith('.jpg') == True or imageName.endswith('.png') == True:
				form.save()
				formID = form.instance.id
				imageName = form.instance.image.name
				imageURL = settings.MEDIA_URL + imageName
				return render(request,'ClassificationMainForm.html', {'imageURL': imageURL, 'imagename': imageName, 'imageID': formID})	
			else:
				return HttpResponse("Invalid file format. Please select a valid image file")
		else:
			return HttpResponse("Invalid file format. Please select a valid image file")
	else:
		if request.session.session_key:
			form = UserTestResultsForm
			return render(request,'inputForm_Classification.html', {'form': form})
		else:
			return redirect('/login/')

def classify(request):
	if request.method == 'POST':
		imageName = request.POST['image']
		formID = request.POST['formID']
		label = classifier.main(imageName)

		UserTestResults.objects.filter(pk=formID).update(classifierResult=label)
		return HttpResponse("<p>Classifier Result: "+ str(label) +"<p>")
	else:
		return HttpResponse("<p>Error in using image. Please reupload it.</p>")

def aboutNitrogen(request):
	return render(request, 'aboutNitrogen.html')
def aboutPhosphorus(request):
	return render(request, 'aboutPhosphorus.html')
def aboutPotassium(request):
	return render(request, 'aboutPotassium.html')

def aboutLeafCheckIT(request):
	return render(request,'aboutLeafCheckIT.html')

def signup(request):
	if request.method == 'POST':
		form = signupForm(data=request.POST)
		if form.is_valid():
			user = form.save()
			return redirect('/')
		else:
			return HttpResponse("Please fill all needed data")
	else:
		form = signupForm()
		return render(request, 'signupForm.html', {'form': form})


def login(request):
	if request.method == 'POST':
		form = loginForm(request.POST)
		if form.is_valid():
			email = request.POST['email']
			password = request.POST['password']
			#email = form.cleaned_data['email']
			#password = form.cleaned_data['password']
			eb = EmailAuthBackend()


			user = eb.authenticate(email, password)
			
			if user is not None:
				request.session['email'] = user.email
				request.session['admin'] = user.is_superuser
				django_login(request, user)
				return render(request, 'account.html')
			else:
				return HttpResponse("wrong credentials")
		else:
			return HttpResponse("Please fill all missing data")
	else:
		form = loginForm()
		return render(request, 'login.html', {'form': form})

def logout(request):
	try:
		del request.session['email']
		django_logout(request)
	except:
		pass
	return redirect('/')

def account(request):
	if request.user.is_authenticated:
		email = request.user.email
		user = User.objects.get(email=email)
		return render(request, 'account.html', {'user': user})
	else:
		return HttpResponse("bad request")

class CategoriesList(generics.ListCreateAPIView):
	queryset = Categories.objects.all()
	serializer_class = CategoriesSerializer

class CreateUsers(APIView):
	permission_classes = (AllowAny,)

	def post(self, request, format=None):
		serializer = UserSerializer(data=request.data)
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class APIViewUsers(APIView):

	def get(self, request, format=None):
		user = request.user
		serializer = UserSerializer(user)
		return Response(serializer.data)

class LogoutAPIUsers(APIView):
	
	def get(self, request, format=None):
		request.user.auth_token.delete()
		return Response(status=status.HTTP_200_OK)



'''
def inputImage(request):
	if request.method == 'POST':
		form = ImageDetailsForm(request.POST, request.FILES)
		if form.is_valid():
			form.save()
			message = "The image was successfully uploaded!"
			imageName = form.instance.image.name
			imageURL = settings.MEDIA_URL + imageName
			return render(request,'success.html', {'message': message, 'imageURL': imageURL, 'imagename': imageName})
		else:
			message = "Error: " + forms.errors
			return render_to_response('success.html', {'message': message})
	else:
		form = ImageDetailsForm()
		return render(request, 'inputForm.html', {'form': form})
'''
'''


def donateImage(request):
	if request.method == 'POST':
		form = ImageDetailsForm(request.POST, request.FILES)
		if form.is_valid():
			form.save()
			message = "Thank you for donating your image. The admin will have to approve the image first to ensure data integrity."
			return render(request,'donate.html', {'message': message})
		else:
			message = "Error: " + forms.errors
			return render_to_response('donate.html', {'message': message})
	else:
		form = ImageDetailsForm()
		return render(request, 'inputForm.html', {'form': form})
'''