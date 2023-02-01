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
    """ tests whether invoking wizard works and variables are initiated  """
    i=ytd.ytd()
    a1=i.vid_fp is None 
    a2=i.subs_fp is None 
    a3=i.subprocess_out is None 
    a4 =all([v is None for v in i.subs_d.values()])
    a5=i.subs_df.empty 
    assert a1 == True  and a2 == True and a3==True and a4==True and a5==True 
    
@pytest.mark.ytd
def test_download_vid():
    """ downloads a vid and checks if it's there  """
    i=ytd.ytd()
    url='https://www.youtube.com/watch?v=UADcrh2pfpA&ab_channel=CrushClips'
    fp=i.download_vid(yt_url=url)
    fpp,meta=i.path_join('tmp',fp,meta=True)
    
    assert meta[0] == True and i.vid_fp is not None 
    
@pytest.mark.ytd
def test_download_subs():
    """ downloads subs and checks if it's there  """
    i=ytd.ytd()
    url='https://www.youtube.com/watch?v=nAk8MagnDsY&ab_channel=PowerfulJRE'
    fp=i.download_subs(yt_url=url)
    fpp,meta=i.path_join('tmp',fp,meta=True)
    assert meta[0] == True and i.subs_fp is not None 
    
@pytest.mark.ytd
def test_make_subs_df():
    """parses subs to df - needs subs file in /tmp """
    i=ytd.ytd()
    f='RANDALL_CARLSON__GRAHAM_HANCOCK_ON_LOST_TECHNOLOGY_AND_THE_GREAT_PYRAMIDS.pl.vtt'
    fp=i.path_join('tmp',f)
    i.subs_fp=fp
    subs_df,subs_df_fp=i.make_subs_df()                     # make subs df 
    fpp,meta=i.path_join('tmp',subs_df_fp,meta=True)        # check if it's there 
    assert i.subs_df is not None  and meta[0] == True 
    
@pytest.mark.dev
def test_aggregate_subs_df():
    """parses subs to df - needs subs file in /tmp """
    i=ytd.ytd()
    f='RANDALL_CARLSON__GRAHAM_HANCOCK_ON_LOST_TECHNOLOGY_AND_THE_GREAT_PYRAMIDS.pl.vtt'
    fp=i.path_join('tmp',f)
    i.subs_fp=fp
    print(1)
    subs_df,subs_df_fp=i.make_subs_df()                     # make subs df 
    print(2)
    i.aggregate_subs_df(df=subs_df)
    print(3)
    
if __name__=='__main__':
    print('tests')
#    test_download_vid()
    test_aggregate_subs_df()