import utils 
import subprocess 
import glob 
import re 
import pandas as pd 
import datetime 
import os 
#d={"id":id
#   ,"channel":channel
#   ,"vid_url":vid_url
#   ,"channel_url":channel_url}

class ytd: 
    def __init__(self) -> None:
        self.logger=utils.setup_logger(name='ytd_logger',log_file='ytd.log')
        self.lambda_tmp_dir = lambda x: utils.path_join(dir_l=['tmp',x])[0]
        
    def dummy(self):
        x='hello world'
        utils.log_variable(logger=self.logger,var=x)
        return True 
    
    # wrapper on subprocess command     
    def subprocess_run(self,l,**kwargs):
        try:
            q=subprocess.run(l,capture_output=True, text=True,shell=True)
            utils.log_variable(logger=self.logger, msg='subprocess run query', q=q)
        except Exception as err:
            print(err)
            utils.log_variable(logger=self.logger, msg=' error when executing subprocess query ',lvl='warning',err=err,q=q)
            return 
        if  q.returncode==0:
            return q.stdout.strip()
        else:
            print('dupa!')
            utils.log_variable(logger=self.logger, msg=' returncode from subprocess != 0 ',lvl='warning',q=q)
        return q.returncode

    # returns dictionary with last N videos uploaded to a channel {id:date}
    def get_channel_vids(self,channel_url,N=10):
        l=["yt-dlp","--skip-download",channel_url,"--playlist-start","1","--playlist-end",f"{N}",'--print','id','--print','upload_date']
        o=self.subprocess_run(l).splitlines()
        d={o[k]:o[k+1] for k in range(0,len(o),2) }
        return d 
    
    # download subs to /tmp/ folder and returns it's filepath 
    def download_vid(self,yt_url,timestamps = None ):
        d=utils.parse_url(url=yt_url)    
        l=["yt-dlp","--skip-download",d['vid_url'],"--get-title"]
        raw_title=self.subprocess_run(l).replace(' ','_').replace('|','').upper()
        title=''.join(e for e in raw_title if e.isalnum() or e=='_' )
        fp,_=utils.path_join(dir_l=['tmp',title])
        l=["yt-dlp",'--no-cache-dir',d['vid_url'],"-o", f"{fp}"]
        if timestamps is not None:
            l+=["--download-sections",f"*{timestamps[0]}-{timestamps[1]}"]
        out=self.subprocess_run(l)
        
        fp,_=utils.path_join(dir_l=['tmp'])
        files=os.listdir(fp)
        xs=['.webm']
        for f in files:
            l=[x in f for x in xs]
            if  any(l):
                return utils.path_join(dir_l=['tmp',f])[0] 
            
        return glob.glob(fp+'*')[0]
        
        
    
    def download_subs(self,yt_url, skip_download = True,  clear_tmp = True, save_as_txt=True):
        if clear_tmp:
            utils.clear_dir(dir='tmp')
        # make most out of the url provided 
        d=utils.parse_url(url=yt_url)
        if d['vid_url'] is None:
            utils.log_variable(logger=self.logger,msg=' dictionary lacks video url ',info='warning',d=d)
            return 
        
        # get title  and remove special chars from it 
        l=["yt-dlp","--skip-download",d['vid_url'],"--get-title"]
        
            
        raw_title=self.subprocess_run(l).replace(' ','_').replace('|','').upper()
        title=''.join(e for e in raw_title if e.isalnum() or e=='_' )
        
        # download the file to tmp 
        fp,_=utils.path_join(dir_l=['tmp',title])
        if skip_download:
            l=["yt-dlp","-o", f"{fp}","--skip-download"]
        else:
            l=["yt-dlp","-o", f"{fp}"]
            
         
        l+=[yt_url,"--force-overwrites","--no-write-subs",  "--write-auto-sub","--sub-format","vtt","--sub-langs","en.*"]
        out=self.subprocess_run(l)
        print(out)
        linez=out.splitlines()
        myline=[i for i in linez if 'Destination' in i][0]
        subs_fp=myline.split(' ')[-1]
        
        # open file downloaded 
        # fp=glob.glob(fp+'*')[0]     # use glob to open the file with wildcard  
        raw_text=open(subs_fp,'r',encoding="utf-8" ).read()  
        
        if save_as_txt:
            fp=utils.strip_extension(s=subs_fp,new_ext='.txt')
            with open(fp,'w',encoding="utf-8") as f: 
                f.write(raw_text)
                
        
        return fp,raw_text
    
    def clear_line(self,s):
#        print(s)
#        input('wiait')
        return s.replace('&nbsp;','')
    
    # parses subs  string to very nice dataframe !  
    def subs_to_df(self, subs : str):
        lines=subs.splitlines()
        timestamp_pattern = re.compile(r'(\d\d:\d\d:\d\d\.\d\d\d) --> (\d\d:\d\d:\d\d\.\d\d\d)')
        old_text=''
        previous_text=''
        d={'no':None,'start':None,'end':None,'s':None,'e':None,'text':None}
        df=pd.DataFrame(d,index=[])
        
        for i,line in enumerate(lines):
            match = timestamp_pattern.match(line)

            if match :
                start_timestamp = match.group(1)
                end_timestamp = match.group(2)
                
                next_line =lines[i+1]
                if '<c>' in next_line:
                    next_line=''
                next_next_line = lines[i+2]
                if '<c>' in next_next_line:
                    next_next_line=''
                    
                text = next_line+' ' + next_next_line#.replace(start_timestamp, '').replace(end_timestamp, '')
                text=self.clear_line(text)
                
                no=len(text.strip().split(' '))
                if no<=2: # getting rid of lines with <=2 words 
                    previous_text=text.strip()+' ' # move one worders to next line 

                    print(previous_text)
                    print(start_timestamp)
                    print(end_timestamp)
                    input('wait')
                    continue

                text=(previous_text + text ).strip()
                d['no']=i
                d['start']=start_timestamp
                d['end']=end_timestamp
                d['s']=self.ts_to_float(start_timestamp)
                d['e']=self.ts_to_float(end_timestamp)
                d['text']=text.replace("[&nbsp;__&nbsp;]","fucking").replace("[&nbsp]","fuck")
                
                if text!=old_text and text.strip()!='': # remove duplicated lines 
                    df.loc[len(df)]=d
                old_text=text
                previous_text=''
        
        return df
    # casts s='00:01:04.200' to 64.2s 
    def ts_to_float(self,s = None):
        #s='00:01:04.200'
        hh,mm,ss,ff=s.replace('.',':').split(':')
        dt=round(float(ff)/1000+float(ss)+float(mm)*60+float(hh)*60*60,3)
        return dt 
        
        
    # dump df to tmp directory with a name 
    def dump_df(self,df : pd.DataFrame, filename : str):
        fp=self.lambda_tmp_dir(filename)
        df.to_csv(fp,sep='|',encoding="utf-8",quoting=1,index=False)
        
    
def download_vid(ytd,url):
    if 0: # skip download
        print('skipidi skip ! ')
        s='ASTRONAUTS_LAND_ON_TERRAFORMED_MARS_ONLY_TO_BE_ATTACKED_BY_A_SWARM_OF_MANEATING_INSECTS.webm'
        s='RANDALL_CARLSON__GRAHAM_HANCOCK_ON_LOST_TECHNOLOGY_AND_THE_GREAT_PYRAMIDS.webm'
        return utils.path_join(dir_l=['tmp',s])[0]
    timestamps=["00:00:00","00:01:00"]
    fp = ytd.download_vid(yt_url=url,timestamps=timestamps)
    return fp 
    
    
    
def workflow1(download_vid=False):
    url='https://www.youtube.com/watch?v=WRjyK7yrAns&ab_channel=StoryRecapped'
    if download_vid:
        ytd.download_vid(yt_url=url)
    url_d = utils.parse_url(url=url)
    subs_txt_fp,s=ytd.download_subs(yt_url=url_d['vid_url'],clear_tmp=False)
    df=utils.subs_to_df(fp=subs_txt_fp)    
    #df['len']=df['en'].apply(utils.ts_to_float)-df['st'].apply(utils.ts_to_float)   
    f=utils.strip_extension(s=subs_txt_fp,new_ext='.csv')
    ytd.dump_df(df=df,filename=f)
    
if __name__=='__main__':
    ytd=ytd()
    workflow1(download_vid=True)
    exit(1)
    
    # download vid 
    url='https://www.youtube.com/watch?v=z9jeqf-8w_M'
    url='https://www.youtube.com/watch?v=BsNP5ygW-AM&t=3s&ab_channel=UMCS'
    url='https://www.youtube.com/watch?v=nAk8MagnDsY&ab_channel=PowerfulJRE'
    url='https://www.youtube.com/watch?v=WRjyK7yrAns&ab_channel=StoryRecapped'

    if 0: # download vid if you want to 
        url='https://www.youtube.com/watch?v=l4SeFcqN2Wo&ab_channel=EasyEnglish'
        ytd.download_vid(yt_url=url)    
    
    # download subs 
    url_d = utils.parse_url(url=url)
    subs_txt_fp,s=ytd.download_subs(yt_url=url_d['vid_url'],clear_tmp=True)

    
    if 0: # read from file 
        f='RANDALL_CARLSON__GRAHAM_HANCOCK_ON_LOST_TECHNOLOGY_AND_THE_GREAT_PYRAMIDS.txt'
        fp=utils.path_join(dir_l=['tmp',f])[0]
            
    df=utils.subs_to_df(fp=subs_txt_fp)    
    
    # dump_df 
    f=utils.strip_extension(s=subs_txt_fp,new_ext='.csv')
    ytd.dump_df(df=df,filename=f)

    
#    print(df.to_string(max_colwidth=1000))
    
    #print(l)