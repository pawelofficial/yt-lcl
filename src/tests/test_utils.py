import sys
import os.path
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
import pytest 
import utils 


# to run tests cd to this dir \src\tests
#  issue  $ pytest in terminal 
#  issue $ pytest::test_my_method to run specific test  
#  issue $ pytest -v -m <marker> to run markers 


@pytest.mark.utils
def test_path_join():
    """ tests if path join method works correctly  """
    input=['tests','test_utils']  
    pj,isfile,isdir,exists=utils.path_join(dir_l=input) # not a file - missing extension 
    t1 = isfile==False and isdir==False and  exists==False 
    input=['tests','test_utils'] 
    pj,isfile,isdir,exists=utils.path_join(dir_l=input,ext='.py') # a file 
    t2 = isfile==True and isdir==False and exists==True  
    assert t1 == True and t2==True 
    
    
    
    
    
if __name__=='__main__':
    test_path_join() 
    
    
    
    
