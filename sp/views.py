from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.http import JsonResponse
from django.views import View
# from django.views.generic.base import TemplateResponseMixin
from djangosaml2.signals import pre_user_save

import logging
import requests


logger = logging.getLogger(__name__)


# class EndPoint(LoginRequiredMixin, TemplateResponseMixin, View):
# class EndPoint(View):
class EndPoint(LoginRequiredMixin, View):
    ''' this view is part of a data exchange protocol between SP and IdP '''
    IDP_ENDPOINT = '{}/endpoint/get/'
    http_method_names = ['post']
    # template_name = 'endpoint.html'

    def post(self, request, *args, **kwargs):
        ''' Service Provider transactional protocol:
                1. receive POST from IdP
                2. perform GET at IdP to retrieve data
                3. provide response to POST request
        '''
        logger.debug('received POST from IdP')
        logger.debug(f'user object: {request.user}')

        url = self.IDP_ENDPOINT.format('http://localhost:8000')
        with requests.Session() as session:
            logger.debug("setting cookies")
            cookies = request.COOKIES

            logger.debug("it's time to GET from IdP!")
            response = session.get(url, cookies=cookies)

            logger.debug(f'IdP response status: {response.status_code}')
        logger.debug('sending response to IdP POST')

        context = {
            'IdP POST': request.POST,
            'IdP GET': response.json(),
            # 'username': str(request.user),
        }

        return JsonResponse(context)


class DirectPost(LoginRequiredMixin, View):
    ''' this view accept POST from a form available at IdP '''
    IDP_ENDPOINT = '{}/endpoint/alternate_get/'
    http_method_names = ['post']

    def post(self, request, *args, **kwargs):
        ''' Service Provider alternate transactional protocol:
                1. receive POST from a user at IdP
                2. perform POST at IdP to retrieve data
                3. provide response to POST request
        '''
        logger.debug('received POST from user form')
        logger.debug(f'user object: {request.user}')

        url = self.IDP_ENDPOINT.format('http://localhost:8000')
        with requests.Session() as session:
            logger.debug("setting cookies")
            cookies = request.COOKIES
            print(cookies)
            # add the parameter 'sessionid' as 'sessionid_idp'
            cookies['sessionid'] = cookies.get('sessionid_idp')

            logger.debug("retrieving data from IdP using POST")
            data = {
                'username': request.user.username,
                'csrfmiddlewaretoken': cookies.get('csrftoken')
            }
            r = session.post(url, data=data, cookies=cookies)

            logger.debug(f'IdP response status: {r.status_code}')
        logger.debug('sending response to user POST')

        context = {
            'user POST': request.POST,
            'IdP response': r.json() if r.status_code == 200 else None,
            'IdP response status': str(r),
            # 'username': str(request.user),
        }

        return JsonResponse(context)


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
