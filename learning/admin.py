from django.contrib import admin
from imagekit.admin import AdminThumbnail
from django.shortcuts import render
from .models import *
from django.conf import settings
from .checkitBackend import CreatingFeat as cf
from .checkitBackend import Training as trainer
from django.contrib import messages
from django.utils.safestring import mark_safe
from .forms import ImageDetailsForm
from django.core.files import File
import shutil
import os
import uuid

def approveImage(modeladmin, request, queryset):
	queryset.update(status='OK')
approveImage.short_description = "Mark selected as approved"

def rejectImage(modeladmin, request, queryset):
	queryset.update(status='X')
rejectImage.short_description = "Mark selected as rejected"

def deleteImage(modeladmin, request, queryset):
	for item in queryset.all():
		item.delete()
deleteImage.short_description = 'Delete selected images'

def trainImages(modeladmin,request,queryset):
	pass
	messages.add_message(request, messages.INFO, mark_safe('<p>Training started....</p>'))
	dictionary = []	
	for obj in queryset:
		imagename = settings.MEDIA_ROOT + "\%s" % obj.image
		categoryname = str(obj.category)
		dictionary.append({'label': categoryname, 'image': imagename})
	
	featuremapfile = cf.main(dictionary)
	svm = trainer.main(featuremapfile)
	if svm is not None:
		messages.add_message(request, messages.INFO, mark_safe('<p>The Classifier was successfully trained!</p>'))
	else:
		messages.add_message(request, messages.ERROR, mark_safe('<p>Failed to train the Classifier</p>'))
	#return render(request, "training.html", {'filename': featuremapfile})
trainImages.short_description = "Use images for training"

def useAsTrainingImage(modeladmin,request,queryset):
	queryset.update(status='OK')
	for obj in queryset:
		imagePath = obj.image.path
		categoryname = str(obj.classifierResult)
		status = obj.status		
		catID = Categories.objects.filter(category=categoryname).values('id').distinct()
		for item in catID:
			fkId = int(item['id'])
		
		imageURL = obj.image.name
		imageSplitName = imageURL.split("/")
		imageName = imageSplitName[-1]

		datasetPath = os.path.join(settings.MEDIA_ROOT, "datasets")
		newDirFileName = os.path.join(datasetPath, imageName)

		##checking of file name conflict

		if os.path.isfile(newDirFileName) == True:    
			uid = uuid.uuid4()
			randomName = uid.hex
			nameSplit = imageName.split(".")
			newImageName = randomName + "." + nameSplit[-1]
		else:
			newImageName = imageName

		newPath = os.path.join(datasetPath, newImageName)
		shutil.move(imagePath, newPath)
		newImageURL = "datasets/" + newImageName		
		
		##save image
		newData = ImageDetails(image=newImageURL,status=status,category=Categories.objects.get(pk=fkId))
		newData.save()
		obj.update(image=newImageURL)
		messages.add_message(request, messages.SUCCESS, mark_safe('<p>The test results are successfully marked as valid dataset!</p>'))
		
useAsTrainingImage.short_description = 'Mark result as valid dataset'

class ImageDetailsAdmin(admin.ModelAdmin):
	list_display = ("category", "image_img", "status")
	fields = ["category", "image", "status"]
	list_filter=("category","status")
	actions = [approveImage, rejectImage]

	
class GetApprovedImagesAdmin(admin.ModelAdmin):
 	list_display = ("category", "image_img")
 	list_filter = ["category"]
 	actions = [trainImages]
 	ordering = ('-category',)
 	pass
 	def queryset(self,request):
 		return self.model.objects.filter(status='OK')
 	
 	def has_add_permission(self,request):
 		return False

 	def get_actions(self, request):
 		actions = super(GetApprovedImagesAdmin, self).get_actions(request)
 		del actions['delete_selected']
 		return actions

 	def has_delete_permission(self,request, obj=None):
 		return False

class UserTestResultsAdmin(admin.ModelAdmin):
 	list_display = ("image_img", "classifierResult", "datasetStatus",)
 	fields = ["image", "classifierResult", "status",]
 	readonly_fields = ('classifierResult','image')
 	actions = [useAsTrainingImage]
	list_filter = ["classifierResult","status"] 

 	def has_add_permission(self,request):
 		return False



admin.site.register(User)
admin.site.register(ImageDetails, ImageDetailsAdmin)
admin.site.register(Categories)
admin.site.register(GetApprovedImages,GetApprovedImagesAdmin)
admin.site.register(UserTestResults,UserTestResultsAdmin)
