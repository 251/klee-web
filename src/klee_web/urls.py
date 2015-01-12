from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
import api

urlpatterns = patterns(
    '',
    url(r'^', include('frontend.urls')),
    url(r'^api/', include(api.router.urls)),
    url(r'^api/', include(api.file_router.urls)),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^manage/', include('control_panel.urls', namespace="control_panel")),
    url(r'^accounts/login/$', 'django.contrib.auth.views.login',
        {'template_name': 'control_panel/login.html'}),
)

urlpatterns += staticfiles_urlpatterns()
