from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('ASP_app.urls')),
    path('users/', include('users.urls')),
    path('users/', include('django.contrib.auth.urls')),
    path('users/', include('authtools.urls')),
]
