import subprocess 
import re 
import os 


if __package__=='wizard':                               # imports when run as package
    from .utils import *    
else:                                                   # import when ran as script and from other scripts
    from utils import *


# yt class for getting things from youtube 
class yt_url:
    def __init__(self) -> None:
        self.url=None
        self.reg=r'v=([^&]+)'
    def get_base(self,url): # returns base from whole yt url 
        x=re.findall(self.reg,url)[0]
        return x 
    def build(self,base): # returns whole url from it's base 
        return f"https://www.youtube.com/watch?v={base}"
    
    def parse(self,url):
        base=self.get_base(url)
        return self.build(base=base)
    
    
#------------------------------------------------------------------------------------------------
class ytDownloader:
    def __init__(self) -> None:
        self.current_dir = os.path.dirname(os.path.abspath(__file__))
        self.path_join = lambda l : os.path.join(self.current_dir,*l).replace('\\','\\\\')
        
        self.vids_dir=self.path_join(['vids',])
        self.transcript_dir=self.path_join(['transcripts'])
 

        self.logger=setup_logger(name='ytDownloader_logger',log_file='ytDownloader_logger.log')
        self.yt_url=yt_url()

    # logs a variable 
    def log_variable(self,var,msg='',wait=False,lvl='INFO'):
        log_variable(logger=self.logger,var=var,msg='',wait=False,lvl=lvl)
    
    # wrapper on yt-dlp utility
    def subprocess_run(self,l,**kwargs):
        try:
            q=subprocess.run(l,capture_output=True, text=True,shell=True)
            log_variable(logger=self.logger,var=q,msg='subprocess run query: ')
        except Exception as err:
            print(err)
            return 
        if  q.returncode==0:
            return q.stdout.strip()
        else:
            print('dupa!')
            log_variable(logger=self.logger,var=q,msg='subprocess query returncode !=0 ',lvl='warning')


    # returns dictionary with info about last n videos found on a channel 
    # d = {'video_id':'upload_date'} date is in YYYYMMDD ufortunately :< 
    @measure_time
    def get_channel_info(self,channel_url):
        id,channel,url,base=parse_url(channel_url)
        channel_url=base+channel
        
        l=["yt-dlp","--skip-download",channel_url,"--playlist-start","1","--playlist-end","10"
           ,"--write-info-json"
           #,'--print',"approximate_date"
           ]
        l=["yt-dlp","--skip-download",channel_url,"--playlist-start","1","--playlist-end","10"
           ,'--print','id','--print','upload_date'
           ]
        o=self.subprocess_run(l).splitlines()
        d={o[k]:o[k+1] for k in range(0,len(o),2) }
        return d 
    @measure_time
    def download_vid(self,yt_url : yt_url =None,
                     convert_to_wav : bool = True,      # convert video to wav 
                     timestamps : list = [None, None],  # for example  ["00:00:00","inf"],
                     download_subs : bool = True,       # download subs in addition to video 
                     subs_only : bool = True ,          # downloads only subs 
                     delete_vid: bool = True ):         # drlete downloaded  video 
 

        yt_url=self.yt_url.parse(yt_url)
        # get title  and remove special chars 
        l=["yt-dlp","--skip-download",yt_url,"--get-title"]
        raw_title=self.subprocess_run(l).replace(' ','_').replace('|','') 
        title=''.join(e for e in raw_title if e.isalnum() or e=='_' )

        # download a video
        f=self.path_join([self.vids_dir,title+'.webm'])
        l=["yt-dlp","-o", f"{f}", yt_url,"--force-overwrites"]
   
        # download only subs 
        if subs_only:
            l=["yt-dlp","-o", f"{f}","--skip-download", yt_url,"--force-overwrites"]
        
        # add timestamps 
        if timestamps[0] is not None:
            l+=["--download-sections",f"*{timestamps[0]}-{timestamps[1]}"]
        
        # write subs 
        if download_subs or subs_only:
#            l+=['--list-subs']
            l+=["--write-auto-sub","--sub-format","vtt"]
            
        # download:
        out=self.subprocess_run(l)
        input_file=f"{title}.webm"
        output_file=f'{title}.wav'

        
        # convert to wav 
        if convert_to_wav and not subs_only:
            f=self.path_join([self.vids_dir,input_file])
            f2=self.path_join([self.vids_dir,output_file])
            l=["C:\\ffmpeg\\bin\\ffmpeg","-y", "-i", f, "-vn", "-acodec", "pcm_u8",  f2]
            out=self.subprocess_run(l,shell=True)
        
        # delete original vid 
        if delete_vid and not subs_only:
            l=["del",input_file]
            subprocess.run(l,shell=True,cwd=self.vids_dir)
            
        # move subs to transcript and parse yt subs 
        if download_subs or subs_only:
            subs_filename=output_file.split('.')[0].strip()+'.en.vtt'
            subs_out_filename=subs_filename.split('.')[0].strip()+'.txt'
            self.move_file(subs_filename,'vids','transcripts\\raw',rename=subs_out_filename)
            self.parse_yt_subs(dir='transcripts\\raw',filename=subs_out_filename,tgt_dir='transcripts\\parsed')
        
        return output_file.split('.')[0],output_file.split('.')[1],raw_title
    
    
    def move_file(self,filename,src_dir,tgt_dir,rename = None):
        src=self.path_join([src_dir,filename])
        tgt=self.path_join([tgt_dir,filename])
        if rename is not None:
            tgt=self.path_join([tgt_dir,rename])
        l=['move',src,tgt]
        out=self.subprocess_run(l)
    
    def parse_yt_subs(self,dir,filename,tgt_dir='transcripts\\parsed'):
        f=self.path_join([dir,filename.split('.')[0]+'.txt'])
        f2=self.path_join([tgt_dir,filename.split('.')[0]+'.txt'])
        with open(f,'r') as f:
            lines=f.readlines()
        timestamp_pattern = re.compile(r'(\d\d:\d\d:\d\d\.\d\d\d) --> (\d\d:\d\d:\d\d\.\d\d\d)')
        old_text=''
        previous_text=''
        with open(f2,'w+') as f:
            for i,line in enumerate(lines):
                match = timestamp_pattern.match(line)
                if match:
                    start_timestamp = match.group(1)
                    end_timestamp = match.group(2)
                    text = lines[i+1]#.replace(start_timestamp, '').replace(end_timestamp, '')
                    
                    no=len(text.strip().split(' '))
                    if no<=1:
                        previous_text=text.strip()+' ' # move one worders to next line 
                        continue
                    
                    text=(previous_text + text ).strip()
                    s=f"{start_timestamp} || {end_timestamp} || {text}\n"
                    if text!=old_text and text.strip()!='': # remove duplicated lines 
                        f.write(s)    
                    old_text=text
                    previous_text=''
        
           
 
        
    
    
    
if __name__=='__main__':
    
    url='https://www.youtube.com/watch?v=Yir4WyDi8rU'
    ytd=ytDownloader()
    
    urls=['https://www.youtube.com/watch?v=MMI9_Mv8aZA']
    urls=['https://www.youtube.com/watch?v=kh5dN72GTQ8']
    urls=['https://www.youtube.com/watch?v=ENwb4vWeHc0']
    urls=['https://www.youtube.com/watch?v=BsNP5ygW-AM']
#    urls=['https://www.youtube.com/watch?v=05TbPI4CoAY&ab_channel=JREDaily']
    ts=["00:02:40","00:03:10"]
    for url in urls:
        ytd.download_vid(yt_url=url,timestamps=ts)
#        ytd.download_vid(yt_url=url,timestamps=ts,subs_only=False)
    