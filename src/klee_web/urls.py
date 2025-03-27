from django.urls import path, include
from django.contrib import admin
from django.contrib.auth.views import LoginView
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
import api

urlpatterns = [
    path('', include('frontend.urls')),
    path('api/', include(api.router.urls)),
    path('api/', include(api.file_router.urls)),
    path('admin/', admin.site.urls),
    path('manage/', include('control_panel.urls')),
    path('accounts/login/', LoginView.as_view(template_name='control_panel/login.html')),
    path('soc/', include('rest_framework_social_oauth2.urls')),
]

# Static files support in development mode
urlpatterns += staticfiles_urlpatterns()
