'''
Created on 18/03/2016

User api concerned primarily with communicating to/from the api's users. Contains
api endpoints to create a user.
User logic and persistence is manipulated in the user service module.

@author: thurstonemerson
'''

import endpoints
from protorpc import remote, messages

from forms import StringMessage
from services import users 

from api import memory_api
USER_REQUEST = endpoints.ResourceContainer(name=messages.StringField(1),
                                           email=messages.StringField(2))

@memory_api.api_class(resource_name='users', path='users')
class UserApi(remote.Service):
    """Memory game API for requesting creation of a user"""

    @endpoints.method(request_message=USER_REQUEST,
                      response_message=StringMessage,
                      path='user',
                      name='create_user',
                      http_method='POST')
    def create_user(self, request):
        """Create a User. Requires a unique username"""
        if users.get_by_name(request.name):
            raise endpoints.ConflictException(
                    'A User with that name already exists!')
            
        users.create(request)    
            
        return StringMessage(message='User {} created!'.format(
                request.name))
