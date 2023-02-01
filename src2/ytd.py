
from utils import utils 
import os 
import glob 
import re 
import pandas as pd 
from tabulate import tabulate 
import numpy as np 
class ytd(utils):
    def __init__(self) -> None:
        super().__init__()
        self.tmp_dir=self.path_join('tmp') # path to tmp dir 
        self.logger=self.setup_logger(name='ytd_logger',log_file='ytd.log')
        #self.log_variable(logger=self.logger,msg='this is ytd')
        self.vid_fp=None                # modified by download_vid
        self.subs_fp=None               # modified by download_subs
        self.subprocess_out=None        # tracking subprocess execution 
        self.cols=['no','st','en','st_flt','en_flt','dif','txt']
        self.subs_d={k:None for k in self.cols} # dictionary for subs_dfs 
        self.subs_default_lang='en'             # default subs language 
        self.subs_df=pd.DataFrame(columns=self.subs_d.keys()) # modified by make_subs_df subs_to_df and clean_subs_df
        self.pause_flt=1
    # downloads a vid to tmp directory 
    def download_vid(self,yt_url,timestamps = None ):
        d=self.parse_url(url=yt_url)
        l=["yt-dlp","--skip-download",d['vid_url'],"--get-title"]
        raw_title=self.subprocess_run(l).replace(' ','_').replace('|','').upper()
        title=''.join(e for e in raw_title if e.isalnum() or e=='_' )
        fp=self.path_join('tmp',title)
        l=["yt-dlp",'--no-cache-dir',d['vid_url'],"-o", f"{fp}"]
        if timestamps is not None:
            l+=["--download-sections",f"*{timestamps[0]}-{timestamps[1]}"]
        self.subprocess_out=self.subprocess_run(l)
        self.vid_fp=fp+'.webm'
        return self.vid_fp

    # checks if subs language is available 
    def check_subs_availability(self,yt_url,lang='en-orig') -> bool:
        available_subs=self.get_available_subs(yt_url=yt_url)
        return lang in available_subs.keys(),available_subs
    
    # returns dictionary with info about subs availability 
    def get_available_subs(self,yt_url) -> dict:
        d=self.parse_url(url=yt_url)
        l=["yt-dlp","--skip-download",d['vid_url'],"--list-subs"]
        out=self.subprocess_run(l).splitlines()
        available_subs={}
        available_subs['vid_id']=out[0].split(' ')[1]           # id of video 
        available_subs['has_subs']=out[-1]                      # info it subs are available 
        for line in out[4:-1]:                                  # yeap...
            line2=[i for i in line.split(' ') if i !='']
            available_subs[line2[0]]=line2[1]
        available_subs['full_text']=out
        return available_subs
               
    # downloads subs to /tmp dir
    # returns subs_fp, modifies self.subs_fp
    def download_subs(self,yt_url,lang='pl'):
        if lang is None:
            lang=self.subs_default_lang
        lang_available,all_langs = self.check_subs_availability(yt_url=yt_url,lang=lang)
        if not lang_available:
            self.log_variable(logger=self.logger,msg=f'subs with lang {lang} are unavailable for {yt_url}',lvl='warning',all_langs=all_langs)
            return None 

        d=self.parse_url(url=yt_url)
        # get title  and remove special chars from it 
        l=["yt-dlp","--skip-download",d['vid_url'],"--get-title"]
        raw_title=self.subprocess_run(l).replace(' ','_').replace('|','').upper()
        title=''.join(e for e in raw_title if e.isalnum() or e=='_' )
        
        fp=self.path_join('tmp',title)
        # skip download 
        l=["yt-dlp","-o", f"{fp}","--skip-download"]
        # download subs 
        l+=[d['vid_url'],"--force-overwrites",
            "--no-write-subs",  
            "--write-auto-sub",
            "--sub-format","vtt",
            "--sub-langs",lang] # en.* might be better here 
        # subs come in various extensions like en.vtt or en.vtt.org so save them as text 
        self.subprocess_out=self.subprocess_run(l)
        myline=[i for i in self.subprocess_out.splitlines() if 'Destination' in i][0]
        #subs_fp=myline.split(' ')[-1]                       # subs fp 
        #fp=self.strip_extension(s=subs_fp,new_ext=f'_{lang}_.txt')   # renaming to txt 
        #os.remove(fp) # remove file if it exists
        #os.rename(subs_fp,fp)
        #self.subs_fp=fp
        self.subs_fp=myline.split(' ')[-1]  
        return self.subs_fp

    # wraps make_subs_df and clean_subs_df and aggregates it ! 
    # returns self.subs_df, subs_df_fp, modifies self.subs_df
    def make_subs_df(self,subs_fp = None ,include_pauses=False, aggregate = (True,30)):
        if subs_fp is None:
            subs_fp=self.subs_fp
        self.subs_fp=subs_fp
        df=self.subs_to_df()
        cdf=self.clean_subs_df(df=df,include_pauses=include_pauses)
        # dump df 
        subs_df_fp,ext=self.strip_extension(subs_fp)
        subs_df_fp=f'{subs_df_fp}.{ext[0]}.csv'
        
        if aggregate[0]:
            cdf=self.aggregate_subs_df(df=cdf,N=aggregate[1])
        
        cdf.to_csv(path_or_buf=subs_df_fp,sep='|',quoting=1)
        
        
        return self.subs_df,subs_df_fp
        
    # parses transcript to df 
    # returns self.subs_df, modifies self.subs_df 
    def subs_to_df(self,subs_fp : str = None ) -> pd.DataFrame:
        subs=open(subs_fp,encoding="utf-8").read()
        
        lines=[i.strip() for i in subs.splitlines()]    
        #lines=lines[:100]
        text=''     
        timestamp_pattern = re.compile(r'(\d\d:\d\d:\d\d\.\d\d\d) --> (\d\d:\d\d:\d\d\.\d\d\d)')
        for i, line in enumerate(lines):
            text=''
            match=timestamp_pattern.match(line)
            if match:
                start_timestamp = match.group(1)
                end_timestamp = match.group(2)
                
                i=i+1
                try:
                    next_line=lines[i]
                except IndexError as err:
                    break
            
                while not timestamp_pattern.match( next_line ):
                    if '<c>' not in next_line:
                        text += ' ' + next_line
                    i+=1
                    
                    try:
                        next_line=lines[i]
                    except IndexError as err:
                        break
                self.subs_d['no']=i
                self.subs_d['st_flt']=self.ts_to_flt(start_timestamp)
                self.subs_d['en_flt']=self.ts_to_flt(end_timestamp)
                self.subs_d['st']=start_timestamp
                self.subs_d['en']=end_timestamp
                self.subs_d['txt'],_=self.clean_line(s=text.strip())
                self.subs_d['dif']=self.subs_d['en_flt']-self.subs_d['st_flt']
                text = ''
                if self.subs_d['txt'].strip()!='':
                    self.df_insert_d(df=self.subs_df,d=self.subs_d)
        return self.subs_df
    
    # cleans subs df from duplicates 
    # returns self.subs_df, modifies seflsubs_df
    def clean_subs_df(self,df : None,include_pauses = False  ) -> pd.DataFrame:
        if df is None:
            df=self.subs_df
        
        tmp_df=pd.DataFrame(columns=self.subs_d.keys())
        d=df.iloc[0].to_dict()
        
        # remove exact duplicates 
        i=0
        while i<=len(df)-2:
            row=df.iloc[i]       
            next_row=df.iloc[i+1]  
            if row['txt']==next_row['txt']:
                self.subs_d['no']=min(row['no'],next_row['no'])
                self.subs_d['st_flt']=min(row['st_flt'],next_row['st_flt'])  
                self.subs_d['en_flt']=max(row['en_flt'],next_row['en_flt'])     
                self.subs_d['st']=min(row['st'],next_row['st'])     
                self.subs_d['en']=max(row['en'],next_row['en'])     
                self.subs_d['txt']=row['txt']     
                #self.subs_d['dif']=np.round(self.subs_d['en_flt']-self.subs_d['st_flt'],2)
                self.df_insert_d(df=tmp_df,d=self.subs_d)  
                i+=1 # skip next row since it's the same as current one 
                
            elif row['txt']!=next_row['txt']:            
                self.subs_d['no']=row['no']
                self.subs_d['st_flt']=row['st_flt']  
                self.subs_d['en_flt']=row['en_flt']     
                self.subs_d['st']=row['st']     
                self.subs_d['en']=row['en']     
                self.subs_d['txt']=row['txt']     
                #self.subs_d['dif']=np.round(self.subs_d['en_flt']-self.subs_d['st_flt'],2)
                self.df_insert_d(df=tmp_df,d=self.subs_d)      
            i+=1    
            
        self.df_insert_d(df=tmp_df,d=next_row.to_dict())
        tmp_df['dif']=np.round(tmp_df['en_flt']-tmp_df['st_flt'],2)
        # remove non unique row duplicates  
        new_df=pd.DataFrame(columns=self.subs_d.keys())
        prev_row=tmp_df.loc[0].to_dict()
        cur_row=tmp_df.loc[1].to_dict()
        if prev_row['txt'] not in cur_row['txt']:       # if first row is not a duplicate of second row then write it 
            self.df_insert_d(df=new_df,d=prev_row )
        i=0
        while i<=len(tmp_df)-3:
            prev_row=tmp_df.loc[i].to_dict()
            cur_row=tmp_df.loc[i+1].to_dict()
            next_row=tmp_df.loc[i+2].to_dict()
            if prev_row['txt'] in cur_row['txt']:       # if previous row is in current row then adjust current row's timestamps 
                cur_row['st']=prev_row['st']
                cur_row['st_flt']=prev_row['st_flt']
            if next_row['txt'] in cur_row['txt']:       # if next row is in current row the nadjust current row's timestamps 
                cur_row['en']=next_row['en']
                cur_row['en_flt']=next_row['en_flt']
            if cur_row['txt'] not in prev_row['txt'] and cur_row['txt'] not in next_row['txt']: # if current row is unique then write it 
                self.df_insert_d(df=new_df,d=cur_row)                
            i+=1
            
        cur_row=tmp_df.loc[i].to_dict()             # next to last row 
        if next_row['txt'] not in cur_row['txt']:   # if last row is not a duplicate then write it, if it is then timestamps has been taken int oaccount alreadyu  
            self.df_insert_d(df=new_df,d=next_row)
        
        new_df['dif']=np.round(new_df['en_flt']-new_df['st_flt'],2  )
        if not include_pauses:
            self.subs_df=new_df
            return self.subs_df
        
        # build another dataframe taking into account pauses - no way of simply inserting stuff at index with pandas ! 
        new_df2=pd.DataFrame(columns=self.subs_d.keys())
        previous_en_flt=df.loc[0,'en_flt']       
        
        previous_row=tmp_df.loc[0].to_dict()
        self.df_insert_d(df=new_df2,d=previous_row,clear_d=False)
        for i in range(1,len(tmp_df)):
            row=tmp_df.loc[i].to_dict()
            if row['st_flt']-previous_row['en_flt']>self.pause_flt: # if new row start is bigger than previous row end insert a record with pause 
                tmp_d={}
                tmp_d['no']=i
                tmp_d['txt']=f'<--pause-->'
                tmp_d['st']=previous_row['en']
                tmp_d['en']=row['st']
                tmp_d['st_flt']=previous_row['en_flt']
                tmp_d['en_flt']=row['en_flt']
                self.df_insert_d(df=new_df2,d=tmp_d,clear_d=False)
                #return new_df
                
            self.df_insert_d(df=new_df2,d=row,clear_d=False)
            previous_row=row          
                    
        self.subs_df=new_df2
        new_df2['dif']=np.round(new_df2['en_flt']-new_df['st_flt'],2 )
        return self.subs_df
                 
    def clean_line(self,s):
        strings_to_remove=['<c>','</c>','  ','   ','&nbsp',';;',';',':']
        
        przyslowki_fp=self.path_join('tmp','przyslowki.txt')
        przyslowki=open(przyslowki_fp,encoding='utf-8').read()
        prz=[i.strip() for i in przyslowki.splitlines()]
        for line in prz:
            if len(line)<=3:
                continue
            if ' ' in line:
                continue
            strings_to_remove.append(line)
        
#        strings_to_remove +=['tylko','bardzo']
        for st in strings_to_remove:
            #if st in s:
            #    print(f'removing --{st}---')
            s=s.replace(st,'')
        res=re.sub("<.*?>", " ", s)
        #res=re.sub("<\d\d:\d\d:\d\d\.\d\d\d>", "", s)
        timestamps = re.findall(r'<(\d\d:\d\d:\d\d\.\d{3})>', s)
        res = re.sub(r'[.,](?=[a-zA-Z])', r'\g<0> ', res)     # replace .foo with . foo works for . and ,
        return res,timestamps
            
    # parses subs based on <c> lines 
    def subs_to_df2(self,subs_fp=None):
        subs=open(subs_fp,encoding="utf-8").read()
        lines=[i.strip() for i in subs.splitlines()]   
        timestamp_pattern = re.compile(r'(\d\d:\d\d:\d\d\.\d\d\d) --> (\d\d:\d\d:\d\d\.\d\d\d)')
        for no,line in enumerate(lines): 
            #input('                                                                                                   wait')
            next_line=None
            match=timestamp_pattern.match(line)
            if match:
                start_timestamp = match.group(1)
                end_timestamp = match.group(2)
                self.subs_d['st']=start_timestamp
                self.subs_d['en']=end_timestamp
                self.subs_d['st_flt']=self.ts_to_flt(start_timestamp)
                self.subs_d['en_flt']=self.ts_to_flt(end_timestamp)
                self.subs_d['dif']= self.subs_d['en_flt'] -  self.subs_d['st_flt']
                self.subs_d['no']=no
                i=0
                while True:
                    i+=1
                    if i+no>=len(lines):
                        break
                    next_line=lines[no+i]
                    if timestamp_pattern.match(next_line):
                        break
                    if '<c>' in next_line and '</c>' in next_line:
                        self.subs_d['txt'],ts=self.clean_line(s=next_line)
                        self.subs_d['st']=ts[0]
                        self.subs_d['en']=ts[-1]
                        self.subs_d['st_flt']=self.ts_to_flt(ts[0])
                        self.subs_d['en_flt']=self.ts_to_flt(ts[-1])
                        
                if self.subs_d['txt'] is not None :
                    #print(f'inserting  --{next_line}--')
                    #print(self.subs_d)
                    #print(f'next_line {next_line}' )
                    self.df_insert_d(df=self.subs_df,d=self.subs_d)
        return self.subs_df
                    
    def aggregate_subs_df2(self,df,N=60):
        agg_df=pd.DataFrame(columns=df.columns)
        agg_dif=0
        cur_row=df.loc[0].to_dict()
        agg_dif=cur_row['dif']
        self.subs_d['txt']=cur_row['txt']
        for i in range(1,len(df)):
            next_row=df.loc[i].to_dict() # next row 
            if agg_dif + next_row['dif']<N:                 # if lower than curoff then aggregate 
                agg_dif+=next_row['dif']
                self.subs_d['st']=cur_row['st']
                self.subs_d['st_flt']=cur_row['st_flt']
                self.subs_d['en']=next_row['en']
                self.subs_d['en_flt']=next_row['en_flt']
                self.subs_d['txt']+=' ' + next_row['txt']
            else:
                self.df_insert_d(df=agg_df,d=self.subs_d)
                agg_dif=0
                cur_row=next_row
                self.subs_d['txt']=next_row['txt']
#        self.subs_d['txt']+=next_row['txt']
        
        self.df_insert_d(df=agg_df,d=next_row) # write rest of file 
                
        agg_df['dif']=np.round(agg_df['en_flt']-agg_df['st_flt'],2)
        return agg_df
                
                
            

def wf(ytd): # downloads vid and url 
            
    url='https://www.youtube.com/watch?v=nAk8MagnDsY&ab_channel=PowerfulJRE'
    url='https://www.youtube.com/watch?v=_ypD5iacrnI&ab_channel=MovieRecaps'
    url='https://www.youtube.com/watch?v=l4SeFcqN2Wo&t=101s&ab_channel=EasyEnglish'
    url='https://www.youtube.com/watch?v=RMeacmRH0wA&ab_channel=symmetry'
    timestamps=["00:00:00","00:5:00"]
    ytd.download_vid(yt_url=url,timestamps=timestamps)
    fp=ytd.download_subs(yt_url=url)
   
            
def wf2(ytd): # downloads vid and url 
    pass # my keyobrd went crazy here 
#    url='https://www.youtube.com 
    
#    f='RANDALL_CARLSON__GRAHAM_HANCOCK_ON_LOST_TECHNOLOGY_AND_THE_GREAT_PYRAMIDS.pl.vtt'
#    f='PEOPLE_BECOME_IMMORTAL_BUT_EACH_PERSON_CAN_LIVE_ONLY_26_YEARS_UNLESS_THEY_EARN_MORE_TIME.en-en.vtt'
#    f='PEOPLE_BECOME_IMMORTAL_BUT_EACH_PERSON_CAN_LIVE_ONLY_26_YEARS_UNLESS_THEY_EARN_MORE_TIME.pl-en.vtt'
#    # subs to df 
#    fp= ytd.path_join('tmp',f) 
    
    fp=wf2(ytd)

    fp=ytd.subs_fp
    print(fp)
 
    df=ytd.subs_to_df(subs_fp=fp)    
    tmp_fp=ytd.path_join('tmp','subs_df.csv')
    df.to_csv(path_or_buf=tmp_fp,sep='|',quoting=1)
    
    # clean subs df 
    c_df=ytd.clean_subs_df(df=df,include_pauses=True)
    tmp_fp=ytd.path_join('tmp','subs_cdf.csv')
    c_df.to_csv(path_or_buf=tmp_fp,sep='|',quoting=1)

    # agg df 
    agg_df=ytd.aggregate_subs_df2(df=c_df)    
    tmp_fp=ytd.path_join('tmp','agg.csv')
    agg_df.to_csv(path_or_buf=tmp_fp,sep='|',quoting=1)
    exit(1)
    
    ytd.subs_to_df(subs=subs)
    df=ytd.subs_df
    
    c_df=ytd.clean_subs_df(df=df)
    print(c_df)
    print('here')
#    print(tabulate(df, headers='keys', tablefmt='psql')  )
    

#    print(fp)
    


# test 3 - download subs and parse them
def download_subs_and_parse():
    ytd=ytd()
    url='https://www.youtube.com/watch?v=nAk8MagnDsY&ab_channel=PowerfulJRE'
    fp=ytd.download_subs(yt_url=url)
    
# test2 - download subs 
def download_subs():
    ytd=ytd()
    url='https://www.youtube.com/watch?v=nAk8MagnDsY&ab_channel=PowerfulJRE'
    fp=ytd.download_subs(yt_url=url)
    print(fp)
# test1 - download vid 
def test_download_vid():
    ytd=ytd()
    url='https://www.youtube.com/watch?v=nAk8MagnDsY&ab_channel=PowerfulJRE'
    ytd.download_vid(yt_url=url)
