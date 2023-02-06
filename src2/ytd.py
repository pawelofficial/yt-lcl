
from utils import utils 
import os 
import glob 
import re 
import pandas as pd 
from tabulate import tabulate 
import numpy as np 
import json 
class ytd(utils):
    def __init__(self) -> None:
        super().__init__()
        self.tmp_dir=self.path_join('tmp','david') # path to tmp dir 
        
        self.logger=self.setup_logger(name='ytd_logger',log_file='ytd.log')
        #self.log_variable(logger=self.logger,msg='this is ytd')
        self.vid_fp=None                # modified by download_vid
        self.subs_fp=None               # modified by download_subs
        self.subprocess_out=None        # tracking subprocess execution 
        self.cols=['no','st','en','st_flt','en_flt','dif','txt']
        self.subs_d={k:None for k in self.cols} # dictionary for subs_dfs 
        self.subs_default_lang='en'             # default subs language 
        self.subs_df=pd.DataFrame(columns=self.subs_d.keys()) # modified by make_subs_df subs_to_df and clean_subs_df
        self.pause_flt=69420
    # downloads a vid to tmp directory 
    def download_vid(self,yt_url,timestamps = None ):
        d=self.parse_url(url=yt_url)
        l=["yt-dlp","--skip-download",d['vid_url'],"--get-title"]
        raw_title=self.subprocess_run(l).replace(' ','_').replace('|','').upper()
        title=''.join(e for e in raw_title if e.isalnum() or e=='_' )
        fp=self.path_join(self.tmp_dir,title)
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
    def download_subs(self,yt_url,lang='pl',format='vtt'):
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
        
        fp=self.path_join(self.tmp_dir,title)
        # skip download 
        l=["yt-dlp","-o", f"{fp}","--skip-download"]
        # download subs 
        l+=[d['vid_url'],"--force-overwrites",
            "--no-write-subs",  
            "--write-auto-sub",
            "--sub-format",format,
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
    def xmake_subs_df(self,subs_fp = None ,include_pauses=False, aggregate = (True,30)):
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
    def xsubs_to_df(self,subs_fp : str = None ) -> pd.DataFrame:
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
                self.subs_d['dif']=np.round(self.subs_d['en_flt']-self.subs_d['st_flt'],2)
                text = ''
                if self.subs_d['txt'].strip()!='':
                    self.df_insert_d(df=self.subs_df,d=self.subs_d)
        return self.subs_df
    
    # cleans subs df from duplicates 
    # returns self.subs_df, modifies seflsubs_df
    def xclean_subs_df(self,df : None,include_pauses = False  ) -> pd.DataFrame:
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
        next_row=tmp_df.loc[2].to_dict()
        if prev_row['txt'] not in cur_row['txt']:       # if first row is not a duplicate of second row then write it 
            self.df_insert_d(df=new_df,d=prev_row )
        i=0
        while i<=len(tmp_df)-3:
            #print('prev_row-->', prev_row['txt'])
            #print('cur_row-->', cur_row['txt'])
            #print('next_row-->', next_row['txt'])
            #input('wait')
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
                print('INSERTING  ',cur_row['txt'])
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
        timestamps = re.findall(r'<(\d\d:\d\d:\d\d\.\d{3})>', s)
#        strings_to_remove +=['tylko','bardzo']
        for st in strings_to_remove:
            #if st in s:
            #    print(f'removing --{st}---')
            s=s.replace(st,'')
        res=re.sub("<.*?>", " ", s).replace('  ',' ')
        res = re.sub(r'[.,](?=[a-zA-Z])', r'\g<0> ', res).strip()     # replace .foo with . foo works for . and ,
        #if res[-1]==',':
        #    res=res[:-1]

                
        if len(res)<2:
            print(res,timestamps)
            
            input('wait')
        return res,timestamps
            
    # parses subs based on <c> lines 
    def xsubs_to_df2(self,subs_fp=None):
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
        self.subs_d=cur_row
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
                self.subs_d=next_row
#        self.subs_d['txt']+=next_row['txt']
        
        self.df_insert_d(df=agg_df,d=next_row) # write rest of file 
                
        agg_df['dif']=np.round(agg_df['en_flt']-agg_df['st_flt'],2)
        return agg_df
                
    def parse_json_pld(self,p : dict ):
        subs_d={}
        subs_d['no']=int(p['wWinId'])
        subs_d['st_flt']=np.round(int(p['tStartMs'])/1000.0,2)
        if 'dDurationMs' not in p.keys():       # some rows don't have this key 
            subs_d['en_flt']=subs_d['st_flt']+0
        else:
            subs_d['en_flt']=np.round(subs_d['st_flt']+int(p['dDurationMs'])/1000.0,2)
        subs_d['st']=self.flt_to_ts(ff=subs_d['st_flt'])
        subs_d['en']=self.flt_to_ts(ff=subs_d['en_flt'])
        txt=' '.join([d['utf8'] for d in p['segs'] if d['utf8']!='\n']  ).replace('  ',' ').strip()
        # regexs: 1:   stuff between [] like [Muzyka]
                # 2:   strings starting and ending with , 
                # 3,4: broken tags like [Muzyka  or Muzyka]
        rs=[r'\[.*\]',r"^,|,$",r"^\[\w+",r"[aA-zZ]*\]"] # clean up stuff from yt 
        for r in rs:
            txt=re.sub(r,'',txt).replace('[','').replace(']','') # 
        subs_d['txt']=txt.strip()
        return subs_d
                
    def read_json3_to_df(self,fp):
        with open(fp,'r',encoding="utf-8") as f:
            pld=json.load(f)['events']                  # read data to list 
        pld=[i for i in pld if 'segs' in i.keys()]      # remove items without text 

        tmp_df=pd.DataFrame(columns=self.subs_d.keys()) # declare temporary df 
        for p in pld:                                   # insert data to temporary df 
            subs_d=self.parse_json_pld(p=p)
            txt=subs_d['txt'].strip()
            if txt not in ['']:                         # don't write empty rows 
                self.df_insert_d(df=tmp_df,d=subs_d)
        tmp_df['dif']=np.round(tmp_df['en_flt']-tmp_df['st_flt'],2 ) # calculate dif col 
        return tmp_df
    
    def concat_duplicate_rows(self,df):
        # when reading subs in json3 format they come with messy en_flt values - some rows start at different timestamps but end at the same timestamp,s this method ocncatenated them 
        indexes_to_remove=[]
        max_en_flt=0
        for no,row in df.iterrows():
            if np.round(row['en_flt'],3)== np.round(max_en_flt,3): 
                d=row.to_dict() # need a dictionary to write to df 
                d['txt']=df.loc[no-1]['txt'] + ' ' + row['txt']
                d['st_flt']=df.loc[no-1]['st_flt']
                df.iloc[no-1]=d
                indexes_to_remove.append(no)
            max_en_flt=row['en_flt']
        df2=df.drop(indexes_to_remove)
        df2.reset_index(inplace=True,drop=True  )
        
        df2['st']=df2['st_flt'].apply(self.flt_to_ts)
        df2['en']=df2['en_flt'].apply(self.flt_to_ts)
        df2['dif']=np.round(df2['en_flt']-df2['st_flt'],2)
        
        return df2
    
    def concat_overlapping_rows(self,df):
        # rows coming from json3 youtube do overlap
        # row 1 may end after row 2 starts - this method concats those rows based on proximity to a neighbour 
        prev_end =0 # skipping first row 
        indexes_to_remove=[]
        for no,row in df.iterrows():
            d=row.to_dict()
            start=d['st_flt']
            end=d['en_flt']
            dif= start - prev_end
            if dif<0: # move row up 
                d['txt']=df.loc[no-1]['txt'] + ' ' + d['txt'] # get text from prior and current row 
                d['st_flt']=df.loc[no-1]['st_flt'] # get start from previous row 
                df.iloc[no-1] = d                   # update previous row 
                indexes_to_remove.append(no)
            prev_end=end 
        df3=df.drop(indexes_to_remove)
        df3.reset_index(inplace=True,drop=True)
        
        df3['st']=df3['st_flt'].apply(self.flt_to_ts)
        df3['en']=df3['en_flt'].apply(self.flt_to_ts)
        df3['dif']=np.round(df3['en_flt']-df3['st_flt'],2)
        return df3
            
    def concat_short_rows(self,df,nwords=1):
        # concatenates one word rows 
        
        indexes_to_remove=[]
        for no in range(1,len(df)-1):
            prev_row=df.iloc[no-1].to_dict()
            cur_row=df.iloc[no].to_dict()
            next_row=df.iloc[no+1].to_dict()
            
            dif1=cur_row['st_flt']-prev_row['en_flt']  # time to previous row 
            dif2=next_row['st_flt']-cur_row['en_flt']  # time to next row 
            
            if len(cur_row['txt'].split() ) <=nwords:
                indexes_to_remove.append(no)
                if dif1<=dif2: # move row up 
                    prev_row['txt']=prev_row['txt']+' ' + cur_row['txt']
                    prev_row['en_flt']=cur_row['en_flt']
                    df.iloc[no-1]=prev_row
                else: # move row down 
                    next_row['txt']=cur_row['txt'] + ' ' + next_row['txt']
                    next_row['st_flt']=cur_row['en_flt']
                    df.iloc[no+1] = next_row
        
        df4=df.drop(indexes_to_remove)
        df4.reset_index(inplace=True,drop=True)
        df4['st']=df4['st_flt'].apply(self.flt_to_ts)
        df4['en']=df4['en_flt'].apply(self.flt_to_ts)
        df4['dif']=np.round(df2['en_flt']-df4['st_flt'],2)
        return df4 
            
    def parse_json3_to_df(self,fp):
        df=self.read_json3_to_df(fp=fp)
        df=self.concat_duplicate_rows(df=df)
        df=self.concat_overlapping_rows(df=df)
        df=self.concat_short_rows(df=df)
        return df  
    
    

def wf(ytd): # downloads vid and url 
    url='https://www.youtube.com/watch?v=nAk8MagnDsY&ab_channel=PowerfulJRE'
    url='https://www.youtube.com/watch?v=_ypD5iacrnI&ab_channel=MovieRecaps'
    url='https://www.youtube.com/watch?v=l4SeFcqN2Wo&t=101s&ab_channel=EasyEnglish'
    url='https://www.youtube.com/watch?v=RMeacmRH0wA&ab_channel=symmetry'
    timestamps=["00:00:00","00:5:00"]
#    ytd.download_vid(yt_url=url,timestamps=timestamps)
    fp=ytd.download_subs(yt_url=url,lang='pl',format='json3')
    return fp 
   
   
   
   
            
def wf2(ytd): # downloads vid and url 
    pass # my keyobrd went crazy here 
#    url='https://www.youtube.com 
    
#    f='RANDALL_CARLSON__GRAHAM_HANCOCK_ON_LOST_TECHNOLOGY_AND_THE_GREAT_PYRAMIDS.pl.vtt'
#    f='PEOPLE_BECOME_IMMORTAL_BUT_EACH_PERSON_CAN_LIVE_ONLY_26_YEARS_UNLESS_THEY_EARN_MORE_TIME.en-en.vtt'
#    f='PEOPLE_BECOME_IMMORTAL_BUT_EACH_PERSON_CAN_LIVE_ONLY_26_YEARS_UNLESS_THEY_EARN_MORE_TIME.pl-en.vtt'
#    # subs to df 
#    fp= ytd.path_join(self.tmp_dir,f) 
if __name__=='__main__':
    ytd=ytd()
#    wf(ytd)


    
    
    f='DAVID_ATTENBOROUGHS__TASMANIA__WEIRD_AND_WONDERFUL.en.json3'
    fp=ytd.path_join(ytd.tmp_dir,f)
    df1=ytd.read_json3_to_df(fp=fp)
    tmp_fp=ytd.path_join(ytd.tmp_dir,'df1.csv')
    df1.to_csv(path_or_buf=tmp_fp,sep='|',quoting=1)
    
    df2=ytd.concat_duplicate_rows(df=df1)
    tmp_fp=ytd.path_join(ytd.tmp_dir,'df2.csv')
    df2.to_csv(path_or_buf=tmp_fp,sep='|',quoting=1)
    
    df3=ytd.concat_overlapping_rows(df=df2)
    tmp_fp=ytd.path_join(ytd.tmp_dir,'df3.csv')
    df3.to_csv(path_or_buf=tmp_fp,sep='|',quoting=1)
    
    df4=ytd.concat_short_rows(df=df3)
    tmp_fp=ytd.path_join(ytd.tmp_dir,'df4.csv')
    df4.to_csv(path_or_buf=tmp_fp,sep='|',quoting=1)
    
    f='DAVID_ATTENBOROUGHS__TASMANIA__WEIRD_AND_WONDERFUL.en.json3'
    fp=ytd.path_join(ytd.tmp_dir,f)
    df5=ytd.parse_json3_to_df(fp=fp)
    tmp_fp=ytd.path_join(ytd.tmp_dir,'df5.csv')
    df5.to_csv(path_or_buf=tmp_fp,sep='|',quoting=1)
    exit(1)
    
    tmp_fp=ytd.path_join(ytd.tmp_dir,'df2.csv')
    df2.to_csv(path_or_buf=tmp_fp,sep='|',quoting=1)
    
    tmp_fp=ytd.path_join(ytd.tmp_dir,'df3.csv')
    df3.to_csv(path_or_buf=tmp_fp,sep='|',quoting=1)