import logging 
logging.basicConfig(level=logging.INFO,filename='./logs/wizard.log',filemode='w')
from .yt_downloader import yt_downloader


class wizard:
    def __init__(self) -> None:
        print('this is wizard')
        self.yt_downloader=yt_downloader()
        
    def download_vid(self,yt_url : str):
        self.yt_downloader.download_vid(yt_url=yt_url)
        
        
