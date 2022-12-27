import json 
import requests 
from requests.compat import urljoin 
import subprocess 
import ffmpeg 
import os 
import re 
import logging 
logging.basicConfig(level=logging.INFO,filename='my.log',filemode='w')


# to do:
    # read ut-config urls as yt_url instances 
    # handle timestamps in yt-config and yt-dlp !    

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

#u=yt_url(url='https://www.youtube.com/watch?v=BQ5YolePaAQ&ab_channel=peter234w')
#base=u.get_base()
#print(base)
#print(u.build(base=base))
#exit(1)
#



class yt:
    def __init__(self) -> None: # read secrets 
        self.secret_json='client_secret_554653095551-pkun9bqj1elkikr15ctj1k5tqtllommi.apps.googleusercontent.com'
        self.secrets=json.load(open(f'./secrets/{self.secret_json}.json'))['installed']
        self.base_uri='https://www.googleapis.com/youtube/v3/'
        self.endpoints={'activities':'activities'}
        self.api_key=json.load(open(f'./secrets/api_key.json'))['api_key']
        
        self.vids_dir=os.getcwd().replace("\\","\\\\")+'\\\\vids\\\\'
        self.config_dir=os.getcwd().replace("\\","\\\\")+'\\\\configs\\\\'
        self.dummy_vide_url='https://www.youtube.com/watch?v=2kmBI48HhWU&ab_channel=peter234w'
        
        # yeah this is not working 
        self.session=None 
        self.initialize_session()
    # not used - yt session 
    def initialize_session(self):
        params={}
        params['key'] =self.api_key
        self.s=requests.Session()
        self.s.auth=('key',self.api_key)
        
    # not used - yt stuff 
    def get(self,url,**kwargs):
        params={k:v for k,v in kwargs.items()} 
        params['key'] =self.api_key
        r=requests.get(url=url,params=params)
        if r.status_code!=200:
            print(f' watchout, your status code is {r.status_code}' )
        return r 

    def log_variable(self,var,msg='',wait=False,lvl='info'):
        if var is None:
            var='None'
        s= f' {msg} \n{var}'
        if lvl=='warning':
            logging.warning(s)
        else:
            logging.info(s)
        if wait:
            print(s)
            input('waiting in log ')


    # wraps subprocess run with error handling 
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
            

    def read_yt_config(self):
        config=json.load(open(self.config_dir+'yt-config.json'))
        return config 

    # download video and dump to mp3 with dl-lib
    def download_vid(self,title='dummy_title',yt_url : yt_url =None):
        if yt_url is None:
            yt_url=self.dummy_vide_url
            print('reading url from config ')
            yt_url=self.read_yt_config()['urls'][0]
            
            
        # get title 
        l=["yt-dlp",yt_url,"--get-title"]
        title=self.subprocess_run(l).replace(' ','_').replace('|','')         
        out=self.subprocess_run(["yt-dlp","-o", f"./vids/{title}.webm", yt_url,"--force-overwrites"])  
        input_file=f"{title}.webm"
        output_file=f'{title}.wav'
        # make mp3 
#        l=["C:\\ffmpeg\\bin\\ffmpeg","-y", "-i", self.vids_dir+input_file, "-vn", "-acodec", "libmp3lame", "-b:a", "128k", self.vids_dir+output_file]
        l=["C:\\ffmpeg\\bin\\ffmpeg","-y", "-i", self.vids_dir+input_file, "-vn", "-acodec", "pcm_u8", "-ar", "22050", self.vids_dir+output_file]
        
        out=self.subprocess_run(l,shell=True)
        # delete original vid 
        l=["del",input_file]
        subprocess.run(l,shell=True,cwd=self.vids_dir)

    
    def get_activities(self):
        url=urljoin(self.base_uri,self.endpoints['activities'])
        r=self.get(url=url)
        print(r.text)
        return r 
 


if __name__=='__main__':
    yt=yt()
    yt.read_yt_config()
    yt.download_vid()
#    yt.get_activities()