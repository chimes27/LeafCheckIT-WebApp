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
from django.template import RequestContext

from rest_framework import mixins, viewsets
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import ParseError, ValidationError
from .auth import RestAuthentication


#from rest_framework.renderers import JSONRenderer
#import json
#from django.forms.models import model_to_dict
from django.http import JsonResponse

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
		result = str(label)
		resURL = result.lower()	
		UserTestResults.objects.filter(pk=formID).update(classifierResult=label)
		return render(request, 'classificationResult.html', {'result': result, 'resURL': resURL})
		#return HttpResponse("<p>Classifier Result: "+ str(label) +"<p>")
	else:
		return render(request, "<p>Error in using image. Please reupload it.</p>")

def nitrogen(request):
	return render(request, 'nitrogen.html')
def phosphorus(request):
	return render(request, 'phosphorus.html')
def potassium(request):
	return render(request, 'potassium.html')

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
		full_name = request.user.get_full_name()
		user = User.objects.get(email=email)
		return render(request, 'account.html', {'user': user, 'fullname': full_name})
	else:
		return HttpResponse("Bad Request")

def getUserTestResults(request):
	if request.user.is_authenticated:
		user = request.user
		result = UserTestResults.objects.filter(user=user)
		return render(request, 'viewTestResults.html', {'result': result})
	else:
		return HttpResponse("Bad Request")

##############################################
# API Views 								 #
#											 #
##############################################
'''
class SetEncoder(json.JSONEncoder):
	def default(self, obj):
		if isinstance(obj, set):
			return list(obj)
		return json.JSONEncoder.default(self, obj)
'''
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

class ImageDetailsViewSet(APIView):
	serializer_class = UserTestResultsSerializer
	
	def post(self,request, *args, **kwargs):
		try:
			#serializer = ImageDetailsSerializer(data=request.data)
			serializer = UserTestResultsSerializer(data=request.data)
			if serializer.is_valid():
				serializer.save()
				pk = serializer.data['id']
				#label = tryclassify(serializer.validated_data['image'].name)
				imageName = serializer.validated_data['image'].name
				if imageName.endswith('.jpg') == True or imageName.endswith('.png') == True:
					label = classifier.main(imageName)
				strLabel = str(label)

				UserTestResults.objects.filter(id=pk).update(classifierResult=strLabel)
				listdesc = Categories.objects.filter(category=strLabel).values('description')
				dum = listdesc[0]
				desc = dum['description']
				return Response({'label': strLabel, 'desc': desc}, status=status.HTTP_201_CREATED)
			return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
		except:
			raise 
			return Response(status=status.HTTP_415_BAD_REQUEST)

class GetTestResult(APIView):
	def get(self, request):
		if request.user.is_authenticated:
			user = request.user
			result = UserTestResults.objects.filter(user=user).order_by('-date')
			data = {}
			image = []
			category = []
			for item in result:
				category.append(item.classifierResult)
				imgpath = settings.BASE_URL + settings.MEDIA_URL + item.image.name
				image.append(imgpath)
			data = {'category': category, 'image': image}
			return Response(data, status=status.HTTP_200_OK)
		else:
			return Response(status=status.HTTP_403_FORBIDDEN_REQUEST)
		
		

'''
class ViewUserTestResults(APIView):
	def get(self, request, format=None):
		user = request.user
		result = UserTestResults.objects.filter(user=user)
		response = JsonResponse(result, safe=False)
		return Response(response)
'''

'''
def tryclassify(imageName):
	if imageName.endswith('.jpg') == True or imageName.endswith('.png') == True:
		label = classifier.main(imageName)
	return label
'''



'''
class ImageDetailsViewSet(APIView):

	def post(self,request, *args, **kwargs):
		try:
			imgStr = request.data['image']

			media_filename = os.path.join(settings.MEDIA_ROOT, 'img.jpg')
			media_url = settings.MEDIA_URL + 'img.jpg'
			

			img = Image.open(StringIO(imgStr.decode('base64')))
			img.save(media_filename, 'JPEG')

			#request.data['image'] = media_filename
			request.data['user'] = request.user

			#data1 = {'image': media_filename, 'category': 1, 'status': 'Y', 'user': user}

			serializer = ImageDetailsSerializer(data=request.data)
			if serializer.is_valid():
				serializer.save()
				return Response(serializer.data, status=status.HTTP_201_CREATED)
			return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
		except:
			raise
			return Response(serializer.errors, status=status.HTTP_415_BAD_REQUEST)


			#img_out = cStringIO.StringIO()
			#img_out.write(imgData.decode('base64'))
			#img_out.seek(0)
			
			

			#image = SimpleUploadedFile(media_file, img_out.read(), content_type='image/png')
'''



'''
try:
	media_dir = settings.MEDIA_ROOT

	if not os.path.exists(media_dir):
		os.makedirs(media_dir)
	imageFile = os.path.join(media_dir, "img.png")

	with open(imageFile, "wb") as fh:
		fh.write(base64.decodestring(image))
	fh.close
	return Response(status=status.HTTP_200_OK)
except:
	raise
	return Response(status=status.HTTP_400_BAD_REQUEST)
'''


'''
class ImageDetailsViewSet(generics.ListCreateAPIView):
	queryset = ImageDetails.objects.all()
	serializer_class  = ImageDetailsSerializer
	
	
	def create(self, request, *args, **kwargs):
		serializer = self.get_serializer(data=request.data)		

		if not serializer.is_valid():
			print(serializer.errors)
			raise ValidationError(serializer.errors)
		self.perform_create(serializer)
		headers = self.get_success_headers(serializer.data)
		return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
'''	
'''
class ImageDetailsView(APIView):
	serializer_class  = ImageDetailsSerializer
	#parser_classes = (MultiPartParser, FormParser,)
	def post(self, request, format=None):

		serializer = ImageDetailsSerializer(data=request.data)
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data, status=status.HTTP_201_CREATED)
		else:
			return Response(serializer.data, status=status.HTTP_400_BAD_REQUEST)	
'''


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