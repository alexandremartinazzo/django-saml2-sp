from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.views import View
from django.views.generic.base import TemplateResponseMixin
from djangosaml2.signals import pre_user_save


class EndPoint(LoginRequiredMixin,
               TemplateResponseMixin,
               View):
    ''' we shall accept POST from authenticated users '''

    http_method_names = ['post']
    template_name = 'endpoint.html'

    def post(self, request, *args, **kwargs):
        ''' display what has been POSTed '''
        context = {
            'post_dict': request.POST,
            'user': request.user,
        }

        return self.render_to_response(context)


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
