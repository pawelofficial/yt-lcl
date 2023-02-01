import utils 
import pandas as pd 
import json 
import hashlib 
from gtts import gTTS
import torchaudio 
import torch 
import re 
import subprocess 
import os
import ffmpeg
import pydub 

from googletrans import Translator

class tts: 
    def __init__(self) -> None:
        self.logger=utils.setup_logger(name='tts_logger',log_file='tts.log')
        self.lambda_tmp_dir = lambda x: utils.path_join(dir_l=['tmp',x])[0]
        self.df= None 
        self.src='en'   # text translation src lang
        self.dest='pl'  # text translation tgt lang 
        self.lang ='pl' # speech language 
        self.tld= 'pl'  # 'com.au' # speech accent  
        self.lambda_hash = lambda  x: hashlib.sha256(x.encode()).hexdigest()
        self.trs=Translator()
        self.lambda_tts = lambda s: gTTS(s, lang=self.lang, tld=self.tld)
        self.text_d={self.src:None,self.dest:None}
        self.ffmpeg_path="C:\\ffmpeg\\bin\\"
        
    # read df to self.df 
    def read_df(self,fname):
        fp=self.lambda_tmp_dir(fname)
        self.df=pd.read_csv(fp,quoting=1,sep='|')
    
    def string_to_speech(self,s : str,**kwargs):
        return gTTS(s,lang=self.lang,tld=self.tld,**kwargs)
    
    
    # translate text in a dataframe based on self.src and self.tgt values 
    # returns df with new column corresponding to translation and a text_dict 
    def translate(self,df = None ,col='txt',dump_it=True,**kwargs):
        if df is None:
            df=self.df
        for no,row in df.iterrows(): # add new col with translated text to self.df 
            text=row[col]
            tr=self.trs.translate(text=text,dest=self.dest,src=self.src)
            df.loc[no,'hash']=self.lambda_hash(row[col])
            df.loc[no,self.dest]=tr.text
            
        whole_text=' '.join(df[col].tolist())   # save whole text to dictionary  
        self.text_d[self.src]=whole_text        
        whole_text_loc=self.trs.translate(text=whole_text,dest=self.dest,src=self.src).text
        self.text_d[self.dest]=whole_text_loc
        
        if dump_it:
            dump_name=kwargs.get('dump_name')
            if dump_name is None:
                dump_name='translated_df.csv'
            fp=utils.path_join(dir_l=['tmp',dump_name])[0]
            df.to_csv(fp,sep='|',encoding="utf-8",quoting=1,index=False)
        
        return df,self.text_d
    
    # text to speech with input as string -> saves .mp3 into tmp dir 
    def text_to_speech_str(self,s : str ,fname : str,  ext='.mp3'):
        fp=utils.path_join(dir_l=['tmp',fname+ext])[0]
        tts=self.lambda_tts(s=s)
        print(tts)
        exit(1)
        tts.save(fp)
        return fp 
        
    # text to speech with input as df -> saves .mp3 into /vid dir 
    def text_to_speech_df(self,df = None,col='txt',ext='.mp3',clear_dest_folder = True):
        if df is None : 
            df=self.df
        if clear_dest_folder: # clear vids d 
            utils.clear_dir(dir='tmp\\vids')
            
        out_fps=[]
        for no,row in df.iterrows(): # iterate through df and generate the transcripts 
            text=row[col]
            fname=utils.path_join(dir_l=['tmp','vids',row['hash']+f'_{str(no)}_'+ext])[0]            
            target_duration=row['en_flt']-row['st_flt']
            # save with original speed 
            tts=self.string_to_speech(s=text)
            #tts=gTTS(text)
            tts.save(fname)
            duration=len(pydub.AudioSegment.from_file(fname))/1000
            ratio=round(target_duration/duration,2)**-1
            out_fp=self.change_speed(vid_fp=fname,ratio=ratio,swap=True)
            out_fps.append(out_fp)
        return out_fps

            
    def trim_video(self,st_flt:float,en_flt:float,vid_fp):

    # ffmpeg -i input.mp4 -ss 00:05:20 -t 00:10:00 -c:v copy -c:a copy output1.mp4
    #>ffmpeg -i input_vid.webm -ss 00:00:10 -t 00:05:00 -c:v copy -c:a copy output_vid.webm
    #ffmpeg -ss 00:01:00 -to 00:02:00 -i input.mp4 -c copy output.mp4
        ffmpeg=[f"{self.ffmpeg_path}ffmpeg"]
        start_ts=utils.float_to_ts(st_flt)
        end_ts=utils.float_to_ts(en_flt)
        
        out_fp=utils.path_join(dir_l=['tmp','trimmed.webm'])[0]
        
        l=ffmpeg + ['-y','-ss',f'{start_ts}','-to',f'{end_ts}','-i',f'{vid_fp}','-c','copy', f'{out_fp}' ]
        self.subprocess_run(l)
        
        
    # aggregates df with text to chunks of N seconds ! 
    def aggregate_df(self,df=None,N=5):
        if df is None:
            df=self.df
        agg_df=pd.DataFrame(columns=df.columns)
        
        text=''                   # text 
        chunk=0                   # which chunk       
        start=df.loc[0,'start']
        end=df.loc[0,'end']
        
        for no,row in df.iterrows():
            cur_chunk=float(row['e'])//N
            if cur_chunk != chunk:
                pass # write stuff
                text +=' '+ row['text']
                agg_df.loc[len(agg_df)+1]=row
                agg_df.loc[len(agg_df),'text']=text
                agg_df.loc[len(agg_df),'start']=start
                agg_df.loc[len(agg_df),'chunk']=cur_chunk
                start=row['end']    # new start 
                chunk +=1
                text=''
                
            else:
                text +=' '+ row['text'] # aggregate text 
                end = row['end']   # update end 
            
        self.dump_df(df=agg_df,filename='agg_df.csv')
        return agg_df 
            

    
    # speeds up or slows down an audio ! 
    def change_speed(self,vid_fp,ratio=0.5,swap=True):
        # >ffmpeg -i audio1.mp3 -filter atempo=2.0 out.mp3
        r=str(round(ratio*1,2))
        print(r)
        out_fp=re.sub('\.',f'_{r}_.',vid_fp)
        l=[f"{self.ffmpeg_path}ffmpeg","-i", vid_fp, "-filter", f"atempo={ratio}",  out_fp]
        out=self.subprocess_run(l)
        
        if swap: 
            tmp=re.sub('\.',f'_tmp_.',vid_fp)
            os.rename(vid_fp,tmp)
            os.rename(out_fp,vid_fp)
            os.remove(tmp)
        return vid_fp
            
    def combine_audio(self,audio_fps : list):
        # ffmpeg -i "concat:audio1.mp3|audio2.mp3" -c copy output.mp3 
        # ffmpeg -f concat -safe 0 -i mylist.txt -c copy output.mp3
        

        ffmpeg=[f"{self.ffmpeg_path}ffmpeg"] # ffmpeg executable  
        
        #audio_fp1=['-i',audio_fp1]           # audio input 1 
        #audio_fp2=['-i',audio_fp2]           # audio input 2 
        out_fp=utils.path_join(dir_l=['tmp','out.mp3'])[0]
        
        
        mylist_fp=utils.path_join(dir_l=['tmp','mylist.txt'])[0]
        with open(mylist_fp,'w') as f:
            for fp in audio_fps:
                s=f"file \'{fp}\'" +'\n'
                f.write(s)
        
        l =ffmpeg + ['-f','concat','-safe','0','-i',f'{mylist_fp}','-y','-c','copy',f'{out_fp}' ]
        self.subprocess_run(l)
        return 
        
        
#        l=vid_l+['-itsoffset','10','-i',audio_fp,'-c:v','copy','-map','0:v','-map','1:a','-y',out_fp]
    def subprocess_run(self,l,**kwargs):
        try:
            q=subprocess.run(l,capture_output=True, text=True,shell=True)
            utils.log_variable(logger=self.logger,var=q,msg='subprocess run query: ')
        except Exception as err:
            print(err)
            return 
        if  q.returncode==0:
            return q.stdout.strip()
        else:
            print('dupa!')
            utils.log_variable(logger=self.logger,var=q,msg='subprocess query returncode !=0 ',lvl='warning')
        

            
    def dump_df(self,df : pd.DataFrame, filename : str):
        fp=self.lambda_tmp_dir(filename)
        df.to_csv(fp,sep='|',encoding="utf-8",quoting=1,index=False)
    
    def dump_str(self,s : str,filename):
        fp=self.lambda_tmp_dir(filename)
        with open(fp,'w+', encoding="utf-8") as f: 
            f.write(s)
            
    def dump_dic(self,d = None,fname='whole_text_d.json'):
        if d is None:
            d=self.whole_text_d
            
        fp=self.lambda_tmp_dir(fname)
        with open(fp,'w',encoding="utf-8") as f:
            json.dump(d,f,ensure_ascii=False,indent=4)
    
    def df_algo(self,df = None):
        if df is None:
            df=self.df 
        print(df)
        
        
    

    
def combine_audio_old(vidname, audname, outname, fps=25):
    from moviepy import editor as mpe
    my_clip = mpe.VideoFileClip(vidname)
    audio_background = mpe.AudioFileClip(audname)
    final_clip = my_clip.set_audio(audio_background)
    final_clip.write_videofile(outname,fps=fps)
    
def combine_audio(audname, outname,vidname, fps=25):
    from moviepy.editor import AudioFileClip,CompositeAudioClip,CompositeVideoClip,concatenate_audioclips
    from moviepy.audio.io.AudioFileClip import AudioClip
    from moviepy.editor import VideoFileClip, AudioFileClip
    
    duration = 5 # duration in seconds
    silent_clip = AudioClip(lambda t: 0, duration=duration)
    from moviepy.editor import AudioFileClip, concatenate_audioclips

    audio1 = AudioFileClip(audname)
    output = concatenate_audioclips([audio1, silent_clip,audio1])
    output.write_audiofile(outname)
    
    video = VideoFileClip(vidname)
    video = video.set_audio(output)
    outname=outname.replace('.mp3','.mp4')
    print(outname)
    video.write_videofile(outname,codec="libx264", bitrate="10000k")
    

# reads csv translates it and dumps it 
def workflow1(csv_name='agg_df'):
    return
    f=f'{csv_name}.csv'
    df=pd.read_csv(utils.path_join(dir_l=['tmp',f])[0],delimiter='|')
    agg_df=utils.aggregate_df(df=df)
    df,d = tts.translate(df=agg_df)
    out_fps=tts.text_to_speech_df(df=df,col='pl')
    print(out_fps)
    tts.combine_audio(audio_fps=out_fps)
    return out_fps
    
if __name__=='__main__':

    tts=tts()
    f='THEY_DISCOVERED_ADVANCE_TINY_HUMANS_LIVING_IN_A_FRIDGE.webm'
    vid_fp=utils.path_join(dir_l=['tmp',f'{f}'])[0]
    tts.trim_video(vid_fp=vid_fp,st_flt=0,en_flt=120)
    csv_name='THEY_DISCOVERED_ADVANCE_TINY_HUMANS_LIVING_IN_A_FRIDGE'
    fps=workflow1(csv_name=csv_name)
    exit(1)
    