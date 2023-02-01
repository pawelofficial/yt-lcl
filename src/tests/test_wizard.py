import sys
import os.path
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
import pytest 


import wizard as wiz 
# to run tests cd to this dir \src\tests
#  issue  $ pytest in terminal 
#  issue $ pytest::test_my_method to run specific test  
#  issue $ pytest -m <marker> to issu markers 


@pytest.mark.wiz
def test_invoke_wizard():
    """ tests whether invoking wizard works """
    i=wiz.wizard()
    res = i.dummy()
    assert res == True 
    
    
def test_dupa():
    pass 
    
    

    
    
