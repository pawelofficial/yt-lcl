import json 
import requests 
from requests.compat import urljoin 
import subprocess 
import ffmpeg 

# yt class for getting things from youtube 

class yt:
    def __init__(self) -> None: # read secrets 
        self.secret_json='client_secret_554653095551-pkun9bqj1elkikr15ctj1k5tqtllommi.apps.googleusercontent.com'
        self.secrets=json.load(open(f'./secrets/{self.secret_json}.json'))['installed']
        self.base_uri='https://www.googleapis.com/youtube/v3/'
        self.endpoints={'activities':'activities'}
        self.api_key=json.load(open(f'./secrets/{self.secret_json}.json'))['api_key']
        
        # yeah this is not working 
        self.session=None 
        self.initialize_session()
        
    def initialize_session(self):
        params={}
        params['key'] =self.api_key
        self.s=requests.Session()
        self.s.auth=('key',self.api_key)
        
        
    # adds api key and kwargs as params in get request 
    def get(self,url,**kwargs):
        params={k:v for k,v in kwargs.items()} 
        params['key'] =self.api_key
        r=requests.get(url=url,params=params)
        if r.status_code!=200:
            print(f' watchout, your status code is {r.status_code}' )
        return r 
    # using weird dl lib because yt does not let you download stuff onbiously !
     
    def download_vid(self,title='comedy'):
        video_url='https://www.youtube.com/watch?v=g0djoi9NRN4'
        subprocess.run(["yt-dlp","-o", f"./vids/{title}.webm", video_url])          
        mycwd=r"C:\\Users\\zdune\\Documents\\moonboy\\speech-enhancer\\speech-enhancer\\vids\\"
        input_file=f"{title}.webm"
        output_file=f'{title}.mp3'
        l=["C:\\ffmpeg\\bin\\ffmpeg", "-i", mycwd+input_file, "-vn", "-acodec", "libmp3lame", "-b:a", "128k", mycwd+output_file]
        subprocess.run(l,shell=True)
        
        l=["del",input_file]
        subprocess.run(l,shell=True,cwd=mycwd)

    
    def get_activities(self):
        url=urljoin(self.base_uri,self.endpoints['activities'])
        r=self.get(url=url)
        print(r.text)
        return r 
 


if __name__=='__main__':
    yt=yt()
    yt.download()
#    yt.get_activities()