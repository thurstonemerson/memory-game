'''
Created on 12/04/2016
Run all functional and unit tests in the testing suite

@author: thurstonemrson
'''
import unittest
import sys
 
SDK_PATH = "C:\Program Files (x86)\Google\google_appengine"
TEST_PATH = "."
 
 
def run_tests(sdk_path, test_path):
    sys.path.insert(0, sdk_path)
    import dev_appserver
    dev_appserver.fix_sys_path()
    suite = unittest.loader.TestLoader().discover(test_path)
    unittest.TextTestRunner(verbosity=2).run(suite)
 
if __name__ == '__main__':
    run_tests(SDK_PATH, TEST_PATH)