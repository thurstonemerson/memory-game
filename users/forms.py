'''
Created on 18/03/2016

Forms to be used when interacting with the user module of the memory api

@author: thurstonemerson
'''
from protorpc import messages

class StringMessage(messages.Message):
    """StringMessage-- outbound (single) string message"""
    message = messages.StringField(1, required=True)
    