from django.conf.urls import url, include
from . import views
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.urlpatterns import format_suffix_patterns

from rest_framework.authtoken import views as rest_framework_views


urlpatterns = [
	#url(r'^inputImage', views.inputImage, name='inputImage'),
	#url(r'^donate', views.donateImage, name='donateImage'),
	url(r'^classify/$', views.classify, name='classify'),
	url(r'^startclassify/$', views.startclassify, name='startclassify'),
	url(r'^nitrogen/$', views.nitrogen, name='nitrogen'),
	url(r'^phosphorus/$', views.phosphorus, name='phosphorus'),
	url(r'^potassium/$', views.potassium, name='potassium'),
	url(r'^aboutLeafCheckIT/$', views.aboutLeafCheckIT, name='aboutLeafCheckIT'),
	url(r'^getUserTestResults/$', views.getUserTestResults, name='getUserTestResults'),
	url(r'^account/$', views.account, name='account'),
	#url(r'^getUserTest/$', views.getUserTest, name='getUserTest'),
	url(r'^login/$', views.login, name="login"),
	url(r'^logout/$', views.logout, name="logout"),
	url(r'^signup/$', views.signup, name='signup'),
	url(r'^api-categories', views.CategoriesList.as_view()),
	url(r'^api-user-create', views.CreateUsers.as_view()),
	url(r'^api-get-user', views.APIViewUsers.as_view()),
	url(r'^api-gettestResults', views.GetTestResult.as_view()),
	url(r'^api-user-logout', views.LogoutAPIUsers.as_view()),
	url(r'^api-token-auth', rest_framework_views.obtain_auth_token),
	url(r'^api-imageUpload', views.ImageDetailsViewSet.as_view()),
	url(r'^$', views.index, name='index'),
]
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns = format_suffix_patterns(urlpatterns)
