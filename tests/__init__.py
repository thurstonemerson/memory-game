"""
Created on 30/03/2016

Base testing module, sets up/tears down the sqllite database configuration and testbed 
@author: thurstonemerson
"""
import yaml
import unittest
import os 

from google.appengine.ext import ndb
from google.appengine.ext import testbed

class MemoryGameUnitTest(unittest.TestCase):
    
    def setUp(self):
        """Set up the test bed and activate it"""
        #first load the configuration file
        script_dir = os.path.dirname(__file__) #<-- absolute dir the script is in
        abs_file_path = os.path.join(script_dir, "config.yaml")
        yaml.safe_load(open(abs_file_path))
         
        # First, create an instance of the Testbed class.
        self.testbed = testbed.Testbed()
        self.testbed.setup_env(current_version_id='testbed.version') 
        # Then activate the testbed, which prepares the service stubs for use.
        self.testbed.activate()
        # Next, declare which service stubs you want to use.
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()
        # Clear ndb's in-context cache between tests.
        ndb.get_context().clear_cache()
        
    
    def tearDown(self):
        """Tear down the test bed by deactivating it"""
        self.testbed.deactivate()
        
