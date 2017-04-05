from __future__ import unicode_literals
from django.db import models
from django.conf import settings
from django.utils.html import mark_safe
from django.contrib.auth.models import AbstractBaseUser, UserManager,PermissionsMixin
from django.utils.translation import ugettext_lazy as _


from .managers import UserManager
#from django.core.files.storage import FileSystemStorage
# Create your models here.

from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token



@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
	if created:
		Token.objects.create(user=instance)


class ApprovedImagesManager(models.Manager):
	def get_queryset(self):
		return super(ApprovedImagesManager, self).get_queryset().filter(status='OK')

#class ImageDetailsManager(models.Manager):

	#def get_queryset(self):
	#	return self.get_queryset().filter(status="OK")
	
	#def get_queryset(self):
	#	return super(ImageDetailsManager, self).get_queryset().filter(status='OK')
		#return self.queryset.filter(status=='OK')
		#return self.get_queryset().filter(status="OK")

		

class ImageDetails(models.Model):
	class Meta:
		verbose_name_plural = " Image Details"


	STATUS_CHOICES = (
		('OK', 'Approved'), 
		('X', 'Rejected'),
		('Y', 'Pending'),
	)
	category = models.ForeignKey('Categories', on_delete= models.CASCADE, default=1)
	date_uploaded = models.DateTimeField(auto_now_add=True)
	image = models.ImageField(null=True, upload_to="datasets")	
	status = models.CharField(max_length=100, choices=STATUS_CHOICES, default='Y')
	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, default=1)
	
	objects = models.Manager()
	appImgObj = ApprovedImagesManager()

	def category_path(category):
		return format(category)

	def image_img(self):
		if self.image:
			return mark_safe(u'<img src="%s" height="125px" width="125px"/>' % (self.image.url))
		else:
			return '(No image found)'
	image_img.short_description = 'Thumbnail'


class Categories(models.Model):
	category = models.CharField(max_length=50)
	description = models.TextField(max_length=255)

	def __str__(self):
		return self.category

	class Meta:
		verbose_name_plural = "  Categories"


class GetApprovedImages(ImageDetails):
	objects = ApprovedImagesManager()

	class Meta:
		proxy = True
		verbose_name_plural = " View Training Images"



###### USER UPLOADS MODEL #######
class UserTestResults(models.Model):
	STATUS_CHOICES = (
		('OK', 'Approved'), 
		('X', 'Rejected'),
		('Y', 'Pending'),
	)
	image = models.ImageField(null=False, upload_to="testImages")
	classifierResult = models.CharField(max_length = 100, default='unknown')
	status = models.CharField(max_length=100, choices=STATUS_CHOICES, default='Y')
	date = models.DateTimeField(auto_now_add=True)
	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, default=1)


	class Meta:
		verbose_name_plural = "Test Results"

	def image_img(self):
		if self.image:
			return mark_safe(u'<img src="%s" height="125px" width="125px"/>' % (self.image.url))
		else:
			return '(No image found)'
	image_img.short_description = 'Thumbnail'

	def get_display(self,key,list):
		d = dict(list)
		if key in d:
			return d[key]
		return None

	def datasetStatus(self):
		return self.get_display(self.status, self.STATUS_CHOICES)
	datasetStatus.short_description = 'Dataset Status'


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(_('email address'), unique=True, db_index=True)
    #username = models.CharField(_('username'), unique=True, max_length=20)
    firstName = models.CharField(_('first name'), max_length=30, blank=True)
    lastName = models.CharField(_('last name'), max_length=30, blank=True)
    date_joined = models.DateTimeField(_('date joined'), auto_now_add=True)
    is_active = models.BooleanField(_('active'), default=True)
    is_staff = models.BooleanField(_('staff'), default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    @property
    def get_full_name(self):
        '''
        Returns the first_name plus the last_name, with a space in between.
        '''
        full_name = '%s %s' % (self.firstName, self.lastName)
        return full_name.strip()

    def get_short_name(self):
        '''
        Returns the short name for the user.
        '''
        return self.firstName


#class MyUser(AbstractBaseUser):
#	email = models.EmailField('email address', unique=True, db_index=True)
#	username = models.CharField(max_length = 20, unique=True)
#	fname =  models.CharField(max_length = 20)
#	lname =  models.CharField(max_length = 20)
#	password = models.CharField(max_length=20)
#	is_active = models.BooleanField(default=True)
#	is_admin = models.BooleanField(default=False)

#	USERNAME_FIELD = 'email'

#	objects =UserManager()

#	def __unicode__(self):
#		return self.email


'''
class getCategories(models.Model):
	categories = Categories.objects.all()
	
	def __str__(self):
		return self.categories
'''

'''
To add data model:
1. Add class in model then migrate
2. Run manage.py shell and type
from AppName.models import ModelClassName

to add objects:
	ModelClassName.objects.create(field1="val1", field2="val2", fieldN="valN")
to delete all objects:
	ModelClassName.objects.all().delete()

'''