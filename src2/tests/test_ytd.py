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
    #assert a1 == True  and a2 == True and a3==True and a4==True and a5==True 
    
@pytest.mark.ytd
def test_download_vid():
    """ downloads a vid and checks if it's there  """
    i=ytd.ytd()
    url='https://www.youtube.com/watch?v=UADcrh2pfpA&ab_channel=CrushClips'
    fp=i.download_vid(yt_url=url)
    fpp,meta=i.path_join('tmp',fp,meta=True)
    
    #assert meta[0] == True and i.vid_fp is not None 
    
@pytest.mark.ytd
def test_download_subs():
    """ downloads subs and checks if it's there  """
    i=ytd.ytd()
    url='https://www.youtube.com/watch?v=nAk8MagnDsY&ab_channel=PowerfulJRE'
    fp=i.download_subs(yt_url=url)
    fpp,meta=i.path_join('tmp',fp,meta=True)
    #assert meta[0] == True and i.subs_fp is not None 
    
    
@pytest.mark.ytd
def test_read_json3_to_df(files : list  = None ):
    # reads example json3 to a df 
    i=ytd.ytd()
    if files is None:
        files=['DAVID_ATTENBOROUGHS__TASMANIA__WEIRD_AND_WONDERFUL.en.json3']
    i.tmp_dir=i.path_join('tests','tests_output')
    for f in files:
        fp=i.path_join('tests',f)
        df=i.read_json3_to_df(fp=fp)                                    # method 
        out_fp,_=i.strip_extension(s=f)
        out_fp=i.path_join(i.tmp_dir,'df_out_test_read_json3_to_df.csv')
        print(out_fp)
        i.dump_df(df=df,fp=out_fp)
        

@pytest.mark.ytd
def test_concat_overlapping_rows(files : list  = None ):
    # reads example json3 to a df 
    i=ytd.ytd()
    if files is None:
        files=['DAVID_ATTENBOROUGHS__TASMANIA__WEIRD_AND_WONDERFUL.en.json3','test_concat_overlapping_rows.csv']
    i.tmp_dir=i.path_join('tests','tests_output')
    for f in files:
        fp=i.path_join('tests',f)
        core,ext=i.strip_extension(s=f)
        if 'csv' in ext:
            df=i.read_csv(fp)
        elif 'json3' in ext:
            df=i.read_json3_to_df(fp=fp)                                    
        df=i.concat_overlapping_rows(df=df)
        out_fp,_=i.strip_extension(s=f)
        out_fp=i.path_join(i.tmp_dir,'df_out_concat_overlapping_rows.csv')
        print(out_fp)
        i.dump_df(df=df,fp=out_fp)

@pytest.mark.ytd
def test_concat_overlapping_rows(files : list  = None ):
    # reads example json3 to a df 
    i=ytd.ytd()
    if files is None:
        files=['DAVID_ATTENBOROUGHS__TASMANIA__WEIRD_AND_WONDERFUL.en.json3','test_concat_overlapping_rows.csv']
    i.tmp_dir=i.path_join('tests','tests_output')
    for f in files:
        fp=i.path_join('tests',f)
        core,ext=i.strip_extension(s=f)
        if 'csv' in ext:
            df=i.read_csv(fp)
        elif 'json3' in ext:
            df=i.read_json3_to_df(fp=fp)                                    
        df=i.concat_overlapping_rows(df=df)
        df=i.concat_short_rows(df=df)
        out_fp,_=i.strip_extension(s=f)
        out_fp=i.path_join(i.tmp_dir,'df_out_concat_overlapping_rows.csv')
        print(out_fp)
        i.dump_df(df=df,fp=out_fp)
    
@pytest.mark.ytd
def test_split_rows(files : list  = None ):
    # reads example json3 to a df 
    i=ytd.ytd()
    if files is None:
        files=['DAVID_ATTENBOROUGHS__TASMANIA__WEIRD_AND_WONDERFUL.en.json3','test_concat_overlapping_rows.csv']
        files=['PEOPLE_BECOME_IMMORTAL_BUT_EACH_PERSON_CAN_LIVE_ONLY_26_YEARS_UNLESS_THEY_EARN_MORE_TIME.pl-en.json3']
#        files=['test_split_rows.csv']
    i.tmp_dir=i.path_join('tests','tests_output')
    for f in files:
        fp=i.path_join('tests',f)
        core,ext=i.strip_extension(s=f)
        if 'csv' in ext:
            df=i.read_csv(fp)
        elif 'json3' in ext:
            df=i.read_json3_to_df(fp=fp)                                    
        df=i.split_rows(df=df)
        out_fp,_=i.strip_extension(s=f)
        out_fp=i.path_join(i.tmp_dir,'df_out_split_rows.csv')
        print(out_fp)
        i.dump_df(df=df,fp=out_fp)
    
        
if __name__=='__main__':
    print('tests')

#    test_read_json3_to_df()
#    test_concat_overlapping_rows()
    test_split_rows()
#    test_concat_short_rows()
#    test_concat_overlapping_rows()
#    test_concat_short_rows()
#    test_concat_overlapping_rows()
    #test_concat_short_rows()
    #test_concat_no_pause()
    #test_concat_on_agg_time()
    #test_concat_short_rows2()
