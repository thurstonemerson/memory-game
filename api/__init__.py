'''
Created on 18/03/2016

This package specifies the google app engine api 

@author: thurstonemerson
'''
import endpoints

MEMCACHE_MOVES_REMAINING = 'MOVES_REMAINING'

#define the name of the overall application api
memory_api = endpoints.api(name='memory', version='v1.0')

#import user and game api modules
import users
import games
