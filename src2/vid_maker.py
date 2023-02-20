from utils import utils 
import datetime
import pydub 
import time 
class vid_maker(utils):
    def __init__(self,today = None ) -> None:
        super().__init__()
        self.logger=self.setup_logger(name='ytd_logger',log_file='ytd.log')
        self.ffmpeg_path="C:\\ffmpeg\\bin\\"
        self.lambda_make_fp = lambda dir,name: self.path_join(dir,name)
        self.root_dir=self.path_join('tmp')
        
        
        if today is None:
            today=datetime.datetime.now().strftime("%Y%m%d")
         
        self.tmp_dir=self.path_join('tmp',today)  # path to tmp dir
        self.vids_dir=self.path_join(self.tmp_dir,'vids')
        self.background_fp=''                           # fp to background vid
        self.speech_fp=''                               # fp to speech wav 
        self.video_fp=''                                # fp to video 
        
    # returns len of video in seconds 
    def get_vid_len(self,vid_fp):
        return len(pydub.AudioSegment.from_file(vid_fp))/1000
        
    # tries to return fp if name of file was pr
    def extract_sound_from_vid(self,vid_fp,
                               timestamps=None,
                               out_fp=None):
        ffmpeg=[f"{self.ffmpeg_path}ffmpeg",'-y'] # ffmpeg executable  
        l=['-i',f'{vid_fp}','-ss',f'{timestamps[0]}','-t',f'{timestamps[1]}','-q:a','0','-map','a',f'{out_fp}']
        l=ffmpeg + l     
        self.subprocess_run(l=l)
        return out_fp


    # adds background to speech  - essentialy overlays two audios 
    def add_background(self,background_fp,speech_fp,out_fp,background_volume=0.2):
        ffmpeg=[f"{self.ffmpeg_path}ffmpeg",'-y'] # ffmpeg executable  
        l =ffmpeg + ['-i',f'{background_fp}'
                     ,'-i',f'{speech_fp}'
                     ,'-filter_complex'
                     ,f'[0:0]volume={background_volume}[a];[1:0]volume=1[b];[a][b]amix=inputs=2:duration=longest', 
                     
                     f'{out_fp}' ]
        self.subprocess_run(l)
        return out_fp
        
        
    # overlay audio and video 
    def overlay_audio_and_video(self,video_fp,audio_fp,out_fp,offset=0):
        ffmpeg=[f"{self.ffmpeg_path}ffmpeg",'-y'] # ffmpeg executable  
        l=['-i',video_fp,
           '-itsoffset',f'{offset}',
           '-i',audio_fp,
           '-c:v','copy','-map','0:v','-map','1:a',f'{out_fp}']
        l=ffmpeg + l 
        self.subprocess_run(l)
        return out_fp
        
        
    # makes a vid out of timestamps 
    
    def cut_vid_to_timestamps(self,vid_fp,out_fp,timestamps):
        ffmpeg=[f"{self.ffmpeg_path}ffmpeg",'-y'] # ffmpeg executable  
        l=['-i',f'{vid_fp}','-ss',f'{timestamps[0]}','-t',f'{timestamps[1]}','-c:v','copy','-c:a','copy' ,f'{out_fp}' ]
        l=ffmpeg+l
        self.subprocess_run(l)
        return out_fp
        
        
    # combines audios together     
    def concat_streams(self,fps : list,out_fp):
        ffmpeg=[f"{self.ffmpeg_path}ffmpeg"] # ffmpeg executable  
        mylist_fp=self.path_join(self.root_dir,'mylist.txt')
        with open(mylist_fp,'w') as f:
            for fp in fps:
                s=f"file \'{fp}\'" +'\n'
                f.write(s)
        
        l =ffmpeg + ['-f','concat','-safe','0','-i',f'{mylist_fp}','-y','-c','copy',f'{out_fp}' ]
        self.subprocess_run(l)
        return 
        
        
    def add_watermark(self,vid_fp,watermark_fp,out_fp):
        ffmpeg=[f"{self.ffmpeg_path}ffmpeg",'-y'] # ffmpeg executable
        
        l=['-i',f'{vid_fp}','-i' ,f'{watermark_fp}',
           '-filter_complex',
#           'overlay=x=(main_w-overlay_w)/2:y=(main_h-overlay_h)/100',
           'overlay=10:10',
           f'{out_fp}']
        l=ffmpeg+l  
        self.subprocess_run(l)
        return watermark_fp
        
        
    def add_offset(self,vid_fp,duration=5,prepend=True):
        from moviepy.audio.io.AudioFileClip import AudioClip
        from moviepy.editor import  AudioFileClip,concatenate_audioclips
        silent_clip = AudioClip(lambda t: 0, duration=duration)
        vid = AudioFileClip(vid_fp)
        if prepend:
            output = concatenate_audioclips([silent_clip,vid])
        else:
            output = concatenate_audioclips([vid,silent_clip])
            
        vid_fp,_=self.strip_extension(s=vid_fp)
        vid_fp=vid_fp+'_pause2_.wav'
        output.write_audiofile(vid_fp)
        return vid_fp
        
# takes a vid, plays it, plays it back and plays it forward
# makes vid 3 times longer if N = 1 
    def boomerangize(self,vid_fp,out_fp,N=1):
        self.ffmpeg_path="C:\\ffmpeg\\bin\\"
        ffmpeg=[f"{self.ffmpeg_path}ffmpeg",'-y'] # ffmpeg executable  
        
        l=['-i',f'{vid_fp}'
           ,'-filter_complex'
            ,f'[0]reverse[r];[0][r][0]concat=n=3,setpts={N}*PTS'
           ,f'{out_fp}']
        l=ffmpeg + l 
        self.subprocess_run(l=l)
        
        
def silerka_wf(dir_name
               ,background_music_fname
               ,speech_fname
               ,video_fname
               ,final_name):

    vm=vid_maker(dir_name)
    
    
    watermark_fp=vm.lambda_make_fp(vm.root_dir,'silerka2.png')

    

#    background_music_fname='CHILLSTEP_SAPPHEIROS__DAWN.webm'
#    speech_fname='0_4cac653d02dbfd1a26bbfacdc93962469baf28337a572f28aee5828646694338.wav'
#    video_fname='HE_TOOK_IT_TOO_DEEP.webm'
    
    vm.background_fp=vm.path_join(vm.root_dir,background_music_fname)
    vm.speech_fp=vm.path_join(vm.vids_dir,speech_fname)
    vm.video_fp=vm.path_join(vm.tmp_dir,video_fname)
    
    
    
    # 0 prepeend speech with pause
    pause_fp=vm.add_offset(vid_fp=vm.speech_fp)
    vm.speech_fp=pause_fp

    
    #0. cut video to timestamps 
    action_fp=vm.lambda_make_fp(vm.tmp_dir,'boomerang.webm')
    timestamps=['00:00:05.000','00:00:35.000']
    vm.cut_vid_to_timestamps(vid_fp=vm.video_fp,out_fp=action_fp,timestamps=timestamps)



#    input('wait 1 ')

    time.sleep(1)
    #1. concat actions so it's longer than speech 
    fps=[action_fp for i in range(5)]
    boomerganged_fp=vm.lambda_make_fp(vm.tmp_dir,'boomerang_out.webm')
    vm.concat_streams(fps=fps,out_fp=boomerganged_fp)
    
    time.sleep(1)
#    input('wait 2 ')
    #2. get speech file len
    speech_len=vm.get_vid_len(vm.speech_fp)
    en=vm.flt_to_ts(speech_len)
    #input('wait 3 ')
    
    #2. make background music 
    cut_background_fp=vm.lambda_make_fp(vm.tmp_dir,'cut_background.wav')
    vm.background_fp=vm.extract_sound_from_vid(vid_fp=vm.background_fp,timestamps=['00:00:00',vm.flt_to_ts(speech_len)],out_fp=cut_background_fp)
    #input('wait 4 ')
    time.sleep(1)
    #3. combine speech with background 
    audio_fps=[vm.background_fp,vm.speech_fp]
    combined_audios_fp=vm.lambda_make_fp(vm.tmp_dir,'combined_audios_offset.wav')
    combined_audios_fp=vm.add_background(background_fp=audio_fps[0],speech_fp=audio_fps[1], out_fp=combined_audios_fp)
    #input('wait 5')
    time.sleep(1)
    
    #4. combine audio and video 
    out_fp=vm.lambda_make_fp(vm.tmp_dir,'final.webm')
    vm.overlay_audio_and_video(video_fp=boomerganged_fp,audio_fp=combined_audios_fp,out_fp=out_fp,offset=5)
    #input('wait 6')
    time.sleep(1)
    
    #5. cut final video to good timestamps 
    out_fp2=vm.lambda_make_fp(vm.tmp_dir,f'{final_name}.webm')
    timestamps=['00:00:00.000',en]
    vm.cut_vid_to_timestamps(vid_fp=out_fp,out_fp=out_fp2,timestamps=timestamps)
    

#    print('add watermark')
#    #6. add watermark 
#    out_fp3=vm.lambda_make_fp(vm.tmp_dir,'final_watermark.webm')
#    watermark_fp=vm.path_join(vm.root_dir,'silerka.png')
#    vm.add_watermark(vid_fp=out_fp2,watermark_fp=watermark_fp,out_fp=out_fp3)
    
    
    exit(1)
    
    print(combined_audios_fp)