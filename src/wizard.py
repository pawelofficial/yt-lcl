
import ytd  # importing youtube downloader 
import trs  # importing transcript 

class wizard: 
    def __init__(self) -> None:
        self.ytd = ytd.ytd()
        self.trs = trs.trs()
    def dummy(self):
        print('i am wizard')
        return True 
    
    
    
    
    
    
    
    
    
    
if __name__=='__main__':
    w=wizard()
    
    