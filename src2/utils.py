import os 
import subprocess 
import logging 
import datetime 
import re 
import pandas as pd 
# class for utilities things 
class utils:
    def __init__(self) -> None:
        pass
    def dummy(self):
        print('this is utils')
    
    # returns absolute path for directories behind *args, for exmplae path_join('tmp','vids') will point to ./tmp/vids/
    def path_join(self,*args,ext='',meta=False):     
        current_dir = os.path.dirname(os.path.abspath(__file__))
        path_join = lambda l : os.path.join(current_dir,*l).replace('\\','\\\\')+ext
        path=path_join(args)
        isfile=os.path.isfile(path)
        isdir=os.path.isdir(path)
        exist=os.path.exists(path)
        if meta:    # if meta returns metadata about filepath 
            return path, (isfile,isdir,exist)
        return path
    
    # sets up logger object for logging 
    def setup_logger(self,name, log_file, level=logging.INFO,mode='w'):
        log_fp=self.path_join('tmp','logs',log_file)
        print(log_fp)

        handler = logging.FileHandler(log_fp,mode=mode,encoding="utf-8")        
        BASIC_FORMAT = "%(levelname)s:%(name)s:%(message)s"  
        formatter=logging.Formatter(BASIC_FORMAT)
        handler.setFormatter(formatter)

        logger = logging.getLogger(name)
        logger.setLevel(level)
        logger.addHandler(handler)
        self.log_variable(logger,msg=' logger setup ')
        return logger
    
    # wrapper for better logging 
    def log_variable(self,logger,msg='',lvl='info',**kwargs):
        ts=datetime.datetime.now().isoformat()
        s=f'{msg} {ts}'
        for k,v in kwargs.items():
            s+= f'\n{k} : {v}'
        if lvl=='warning':
            logger.warning(s)
        else:
            logger.info(s)
    
    # wrapper for subprocess utility 
    def subprocess_run(self,l,**kwargs):
        try:
            q=subprocess.run(l,capture_output=True, text=True,shell=True)
            self.log_variable(logger=self.logger, msg='subprocess run query', q=q)
        except Exception as err:
            print(err)
            self.log_variable(logger=self.logger, msg=' error when executing subprocess query ',lvl='warning',err=err,q=q)
            return 
        if  q.returncode==0:
            return q.stdout.strip()
        else:
            print('dupa!')
            self.log_variable(logger=self.logger, msg=' returncode from subprocess != 0 ',lvl='warning',q=q)
        return q.returncode
    
    # parses yt url into stuff depending on what it contains 
    def parse_url(self,url : str ) -> dict:
        id_reg=r'v=([^&]+)'
        channel_reg=r'ab_channel=(.*)|(\@.*)'
        vid_reg=r'\&ab_channel.*'
        vid_reg=r'watch\?v=([aA0-zZ9]+)'
        base_reg=r'(.*com/)'    
        id=re.findall(id_reg,url)
        #print('id: ', id)
        channel=re.findall(channel_reg,url)
        #print('channel: ',channel)
        vid_url=re.findall(vid_reg,url)
        base_url=re.findall(base_reg,url)[0]
        channel_url = None 
        vid_url = None 

        if id==[]:
            id=None 
        else:
            id=id[0]
        if channel==[]:
            channel=None
        else:
            channel=max(channel[0])
        if id is not None:
            vid_url=base_url+'watch?v='+id 
        if channel is not None:
            channel_url = base_url+channel+'/videos'

        d={"id":id
           ,"channel":channel
           ,"vid_url":vid_url
           ,"channel_url":channel_url
           ,"orig_url":url }
        return d
    # strips extension from a file and changes it to new_ext 
    def strip_extension_old(self,s: str, new_ext = None ):
        ext_reg=r'^([^.]+)'
        s= re.findall(ext_reg,s)[0]
        if new_ext is None:
            return s 
        s=s+f'{new_ext}'
        return s.replace('..','.')
    
    def strip_extension(self,s : str,new_ext=''):
        match = re.search(r"([^.]+)\.([^.]+)\.([^.]+)", s)
        core=match.groups(0)[0]+new_ext
        ext=[i for i in match.groups(0)][1:]
        return core,ext
    
    
    # inserts dictionary to a dataframe and clears dictionary 
    def df_insert_d(self,df: pd.DataFrame,d : dict,clear_d=True ):
        df.loc[len(df)]=d 
        if clear_d:
            for k,v in d.items():
                d[k]=None
#        d.clear()
        
    def ts_to_flt(self,s = None): # string timestamp to float 
        #s='00:01:04.200'
        hh,mm,ss,ff=s.replace('.',':').split(':')
        dt=round(float(ff)/1000+float(ss)+float(mm)*60+float(hh)*60*60,3)
        return dt 

    def flt_to_ts(self,ff = None ):
        hh=ff/60/60//1
        mm=(ff-hh*60*60)/60//1
        ss=(ff-hh*60*60-mm*60)
        return '{:02d}:{:02d}:{:02d}'.format(int(hh), int(mm), int(ss))
    
    # clears tmp directory or other directory 
    def clear_tmp(self,*args):
        if args==():
            args=('tmp',)
        fp=self.path_join(*args)
        files=os.listdir(fp)
        for file in files:
            fp,meta=self.path_join(*args,file,meta=True)
            isfile=meta[0]
            if isfile:
                os.remove(fp)
