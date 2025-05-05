from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views
from app.views import *

urlpatterns = [
	path('',home.as_view(),name='home'),
    path('login',Login.as_view(),name='login'),
    path('logout',Logout.as_view(), name='logout'),
	path('signup',SignUp.as_view(),name='signup'),
    path('add-app',addApp.as_view(),name='add-app'),
    path('add-points',AddPointsView.as_view(),name='add-points'),
    path('view',taskDtls.as_view(),name='view'),
    path('add-app-sv',addAppSave.as_view(),name='add-app-sv'),
    path('app-list', views.AppListView.as_view(), name='app-list'),
    path('user-view',UserDashboardView.as_view(),name='user-view'),
    path('task-submit',TaskSubmit.as_view(),name='task-submit'),
    path('admin-signup',AdminSignup.as_view(),name='admin-signup'),
    path('create-groups/', CreateGroupsAPIView.as_view(), name='create-groups'),
    path('create-status', AddStatusDataAPIView.as_view(), name='create-status'),
    path('delete-all-task', DeleteAllTask.as_view(), name='delete-all-task'),


]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

