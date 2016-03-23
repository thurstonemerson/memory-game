'''
Created on 21/03/2016

Factory module creating a google app engine application from the api module

@author: thurstonemerson
'''

import endpoints
from api import memory_api

#Creates a google app engine application from the api module
application = endpoints.api_server([memory_api])