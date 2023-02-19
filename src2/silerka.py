import ytd 
import datetime
import azure_tts
from vid_maker import silerka_wf

def wf1(ytd: ytd
        ,url='https://www.youtube.com/watch?v=_ypD5iacrnI&ab_channel=MovieRecaps'
        ,download_timestamps=True
        ,download_vid=True
        ,lang='pl'
        ,pause_flt=0.1
        ,clear_tmp = True ):

    dir_name=datetime.datetime.now().strftime("%Y%m%d%H%M")     # make a dir 
    dir_fp=ytd.path_join(ytd.tmp_dir, dir_name)             # make a dir 
    ytd.make_dir(fp=dir_fp)
    ytd.tmp_dir= dir_fp                                     # set a dir 
    if clear_tmp:
        ytd.clear_dir(fp=ytd.tmp_dir)
    if download_vid:
        if download_timestamps:
            timestamps=None # ["00:00:00","00:1:00"]
            ytd.download_vid(yt_url=url,timestamps=timestamps)
        else:
            ytd.download_vid(yt_url=url)
            
    # download whole thing 
    ytd.download_subs(yt_url=url,lang=lang)                 # download subs 
    df_fp=ytd.parse_json3_to_df(fp=ytd.subs_fp,dump_all=True,N=pause_flt)     # parse subs, dump all 
    return df_fp,dir_name



    

def fix_silerka_txt(s):
    
    welcome='Siemanko, witaj na kanale siłerka, miło Cię widzieć!'
    s=s.replace('Dziś zagraniczny,',welcome)
    
    welcome='Siemanko, witaj na kanale siłerka, miło Cię widzieć!'
    s=s.replace('Zagraniczny,',welcome)
    welcome='Siemanko, witaj na kanale siłerka, miło Cię widzieć!'
    s=s.replace('Zagraniczny',welcome)
    
    welcome='Siemanko, witaj na kanale siłerka, miło Cię widzieć!'
    s=s.replace('zagraniczny,',welcome)
    welcome='Siemanko, witaj na kanale siłerka, miło Cię widzieć!'
    s=s.replace('zagraniczny',welcome)
    
    welcome='Siemanko, witaj na kanale siłerka, miło Cię widzieć!'
    s=s.replace('zagraniczni',welcome)
    
    welcome='Siemanko, witaj na kanale siłerka, miło Cię widzieć!'
    s=s.replace('Zagraniczni',welcome)
    

    s=s.replace('w podnoszeniu vault','')
    s=s.replace('vault','')
#    foo='na tyle w dzisiejszym filmie'
#    bar='To by było na tyle w dzisiejszym filmie'
#    s=s.replace(foo,bar)
    print(s)
    ss='dzięki za oglądanie'
    L=''.join(s.split(ss)[0])
    L=L.replace('  ',' ').strip()
    outro='. To wszystko w dzisiejszym filmie, dzięki za oglądanie, koniecznie zasubskrybuj kanał siłerka!'
    L=L+outro
    return L

if __name__=='__main__':
    ytd=ytd.ytd()
    url='https://www.youtube.com/watch?v=_yd8dV_7oho&ab_channel=LiftingVault'
    url='https://www.youtube.com/watch?v=rz-hHjQPaQE&ab_channel=LiftingVault'
    url='https://www.youtube.com/watch?v=xhSSmrdQAUQ&ab_channel=LiftingVault'
    url='https://www.youtube.com/watch?v=x3UcrkMyEA0&ab_channel=LiftingVault'
    url='https://www.youtube.com/watch?v=N3xLz1BwUNo&ab_channel=LiftingVault'
    url='https://www.youtube.com/watch?v=u-GXZ5u3vaU&ab_channel=LiftingVault'
    url='https://www.youtube.com/watch?v=u-GXZ5u3vaU&ab_channel=LiftingVault'
    
    df_fp,dir_name=wf1(ytd=ytd
        ,url=url
        ,download_timestamps=False
        ,download_vid=True
        ,clear_tmp=False
        ,pause_flt=0.5
        ,lang='pl'
        )
    print(df_fp)
    df=ytd.read_csv(df_fp)
    d=df.iloc[0].to_dict()
    d['txt']=fix_silerka_txt(d['txt'])
    df.loc[0]=d
    ytd.dump_df(df=df,fp=df_fp)
    


    

    a=azure_tts.azure_tts()
    #a.talk()
    
    a.set_lang='pl'                                         # set language 
    a.tmp_dir=ytd.tmp_dir                                   # rewrite tmp dir 
    a.vids_dir=a.make_dir(fp=a.path_join(a.tmp_dir,'vids'))         # make vids dir 

        
    a.clear_dir(fp=a.vids_dir)                              # clear if you're running it again
    df_fp=a.path_join(a.tmp_dir,'df_parsed.csv')            # get df fp 
    a.read_df(df_fp=df_fp)                                  # read it 
    
    
    duration=a.make_vids(df=df)                                  # make vids 
    out_fp=ytd.path_join(a.vids_dir,'background.mp3')       # define backgound 
                   # 
    background_music_fname='CHILLSTEP_SAPPHEIROS__DAWN.webm'
    speech_fname='combined.wav'
    video_fname=ytd.vid_fname
    
    final_name='silerka'
    silerka_wf(dir_name=dir_name
               ,background_music_fname=background_music_fname
               ,speech_fname=speech_fname
               ,video_fname=video_fname
               ,final_name = final_name
               )
    



