import subprocess 
import re 
import logging
import os 
import datetime 

# yt class for getting things from youtube 
class yt_url:
    def __init__(self,url) -> None:
        self.url=url
        self.reg=r'watch\?v=(.*)&'
    def get_base(self): # returns base from whole yt url 
        x=re.findall(self.reg,self.url)[0]
        return x 
    def build(self,base): # returns whole url from it's base 
        return f"https://www.youtube.com/watch?v={base}"
    
    def build_with_ts(self): # build url from base with ts's
        pass 

#------------------------------------------------------------------------------------------------
class yt_downloader:
    def __init__(self) -> None:
        self.vids_dir=os.getcwd().replace("\\","\\\\")+'\\\\vids\\\\'

    # logs a variable 
    def log_variable(self,var,msg='',wait=False,lvl='info'):
        ts=datetime.datetime.now().isoformat()
        if var is None:
            var='None'
        s= f' {msg} {ts} \n{var}'
        if lvl=='warning':
            logging.warning(s)
        else:
            logging.info(s)
        if wait:
            print(s)
            input('waiting in log ')
    
    # wrapper on yt-dlp utility
    def subprocess_run(self,l,**kwargs):
        try:
            q=subprocess.run(l,capture_output=True, text=True)
            self.log_variable(q,msg='subprocess run query: ')
        except Exception as err:
            print(err)
            return 
        if  q.returncode==0:
            return q.stdout.strip()
        else:
            print('dupa!')
            self.log_variable(q,msg='subprocess query returncode !=0 ',lvl='warning')

    # downloads a vid based on video url
    def download_vid(self,yt_url : yt_url =None):
        # get title 
        l=["yt-dlp",yt_url,"--get-title"]
        # remove special characters from the title so it doesnt affect ffmpeg
        title=self.subprocess_run(l).replace(' ','_').replace('|','') 
        title=''.join(e for e in title if e.isalnum() or e=='_' )
        # download a video         
        out=self.subprocess_run(["yt-dlp","-o", f"./vids/{title}.webm", yt_url,"--force-overwrites"])  
        input_file=f"{title}.webm"
        output_file=f'{title}.wav'
        # convert to wav 
        l=["C:\\ffmpeg\\bin\\ffmpeg","-y", "-i", self.vids_dir+input_file, "-vn", "-acodec", "pcm_u8", "-ar", "22050", self.vids_dir+output_file]
        out=self.subprocess_run(l,shell=True)
        # delete original vid 
        l=["del",input_file]
        subprocess.run(l,shell=True,cwd=self.vids_dir)
    
    
    
    
if __name__=='__main__':
    logging.basicConfig(level=logging.INFO,filename='./logs/downloader.log',filemode='w')
    url='https://www.youtube.com/watch?v=2kmBI48HhWU&ab_channel=peter234w'
    ytd=yt_downloader()
    ytd.download_vid(yt_url=url)
    