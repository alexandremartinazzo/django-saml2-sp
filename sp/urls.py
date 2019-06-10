from django.contrib.auth.decorators import login_required
from django.contrib import admin
from django.views.generic import TemplateView
from django.urls import include, path


urlpatterns = [
    path('accounts/', include('django.contrib.auth.urls')),
    path('saml2/', include('djangosaml2.urls')),
    path('', TemplateView.as_view(template_name="index.html")),
    path(
        'protected-resource/',
        login_required(TemplateView.as_view(template_name="protected.html")),
        name='protected',
    ),
    path('admin', admin.site.urls),
]
