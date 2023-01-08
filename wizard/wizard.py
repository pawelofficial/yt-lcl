# this is a wizard class, a wrapper being an interface to all submodules in wizard package 
if __package__=='wizard':
    from .utils import *
    from .ytDownloader import ytDownloader
    from .speechtotext import speechToText,transcript
    from .db import db

class wizard:
    def __init__(self) -> None:
        self.logger=setup_logger(name='wizard_logger',log_file='wizard_logger.log')
        self.ytDownloader=ytDownloader()
        self.sa=speechToText()
        self.tr=transcript()
        self.db=db()
    
    # log variable 
    def log_variable(self,var,msg='',wait=False,lvl='INFO'):
        log_variable(logger=self.logger,var=var,msg=msg,wait=wait,lvl=lvl)
    
    # download a yt video using ytDownloader class        
    def download_vid(self,yt_url : str,**kwargs):
        vid_name=self.ytDownloader.download_vid(yt_url=yt_url,**kwargs)
        return vid_name
    
    # wav to text if yt subs are not available 
    def speech_to_text(self,vid_name):
        self.sa.wav_to_text(vid_name=vid_name)
    
    # read parsed transcript to transcript df      
    def read_transcript(self,filename):
        fp=path_join(l=['transcripts','parsed',filename])
        self.tr.read_transcript(filepath=fp)
    # scan transcript df for presence of a word 
    def scan_transcript(self,keyword,threshold=80):
        return self.tr.scan(keyword=keyword,threshold=threshold)
        
    
        
        
if __name__=='__main__':
    from ytDownloader import ytDownloader
    from speechtotext import speechToText
    from utils import setup_logger
    

    w=wizard()
    url='https://www.youtube.com/watch?v=2kmBI48HhWU&ab_channel=peter234w'
    w.download_vid(yt_url=url)