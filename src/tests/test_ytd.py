import sys
import os.path
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
import pytest 


import ytd 
import utils as ut
# to run tests cd to this dir \src\tests
#  issue  $ pytest in terminal 
#  issue $ pytest::test_my_method to run specific test  
#  issue $ pytest -m <marker> to issu markers 


@pytest.mark.ytd
def test_invoke_ytd():
    """ tests whether invoking wizard works """
    i=ytd.ytd()
    res = i.dummy()
    assert res == True 
    
@pytest.mark.ytd
def test_get_channel_vids():
    url='https://www.youtube.com/watch?v=_elvaRJrhE0&ab_channel=PowerfulJRE'
    url_d=ut.parse_url(url=url)
    i=ytd.ytd()
    N=5
    d=i.get_channel_vids(channel_url=url_d['channel_url'],N=N)
    print(d)
    assert len(d)==N
    
if __name__=='__main__':
    test_get_channel_vids()