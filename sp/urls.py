from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import admin
from django.dispatch import receiver
from django.views.generic import TemplateView
from django.urls import include, path
from djangosaml2.signals import pre_user_save


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


# from djangosaml2idp example setup
@receiver(pre_user_save, sender=User)
def custom_update_user(sender, instance, attributes, user_modified, **kargs):
    """ Default behaviour does not play nice with booleans
        encoded in SAML as u'true'/u'false'.
        This will convert those attributes to real booleans when saving.
    """
    for k, v in attributes.items():
        u = set.intersection(set(v), set([u'true', u'false']))
        if u:
            setattr(instance, k, u.pop() == u'true')
    return True  # I modified the user object
