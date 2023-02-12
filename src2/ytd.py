
from utils import utils 
import os 
import glob 
import re 
import pandas as pd 
from tabulate import tabulate 
import numpy as np 
import json 
import datetime 
class ytd(utils):
    def __init__(self) -> None:
        super().__init__()
        self.logger=self.setup_logger(name='ytd_logger',log_file='ytd.log')
        
        self.tmp_dir=self.path_join('tmp')  # path to tmp dir 
        self.vid_fp=None                            # filepath to video modified by self.download_vid
        self.subs_fp=None                           # modified by                   self.download_subs
        self.cols=['no','st','en','st_flt','en_flt','dif','pause_flt','txt']
        self.subs_d={k:None for k in self.cols}     # 
        self.tmp_df=pd.DataFrame(columns=self.subs_d.keys())  # temporary subs df during parsing process 
        self.subs_df=pd.DataFrame(columns=self.subs_d.keys()) # final subs df 
        self.pause_flt=0.1                      # pause cutoff for concatenation of subs 
        self.subs_default_lang='en'             # default subs language 
        self.subprocess_out=None                # tracking subprocess execution 
        
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
    def download_subs(self,yt_url,lang=None,format='json3'):
        if lang is None:
            lang=self.subs_default_lang
        lang_available,all_langs = self.check_subs_availability(yt_url=yt_url,lang=lang)
        if not lang_available:
            print(f'subs with lang {lang} are unavailable')
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
        self.subs_fp=myline.split(' ')[-1]  
        return self.subs_fp
    
    # cleans txt line  from special chars 
    def _clean_txt(self,s):
        translation_table = str.maketrans("\xa0", " ")
        translation_table[ord("\n")] = " "
        clean_string = s.translate(translation_table)
        return clean_string.strip()
        
    # parses json from youtube into a di tionary              
    def parse_json_pld(self,p : dict,no : int = 0  ):
        subs_d={}
        subs_d['no']=no # int(p['wWinId'])
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
                # 3,4: broken tags like "[Muzyka"  or "Muzyka]"
        rs=[r'\[.*\]',r"^,|,$",r"^\[\w+",r"[aA-zZ]*\]"] # clean up stuff from yt 
        for r in rs:
            txt=re.sub(r,'',txt).replace('[','').replace(']','') # 
        subs_d['txt']=self._clean_txt(txt)
#        print(subs_d)
#        input('wait')
        return subs_d
                
    # 1st step in subs parsing - reads json into a df 
    # modifies self.tmp_df 
    def read_json3_to_df(self,fp):
        with open(fp,'r',encoding="utf-8") as f:
            pld=json.load(f)['events']                  # read data to list 
        pld=[i for i in pld if 'segs' in i.keys()]      # remove items without text 

        tmp_df=pd.DataFrame(columns=self.subs_d.keys()) # declare temporary df 
        for no,p in enumerate(pld):                                   # insert data to temporary df 
            subs_d=self.parse_json_pld(p=p,no=no)
            txt=subs_d['txt'].strip()
            if txt not in ['']:                         # don't write empty rows 
                self.df_insert_d(df=tmp_df,d=subs_d)
        tmp_df['dif']=np.round(tmp_df['en_flt']-tmp_df['st_flt'],2 ) # calculate dif col 
        self.tmp_df=tmp_df
        self._calculate_pause_to_next(df=self.tmp_df)
        
        return tmp_df
    
    # 4th step in subs parsing 
    def concat_overlapping_rows(self,df):    
        cond=lambda prev_row,cur_row,next_row  : cur_row['pause_flt']<=0
        df=self._concat_on_condition(df=df,cond=cond)
        self.tmp_df=df 
        self._calculate_pause_to_next(df=self.tmp_df)
        return df 
        
    # 4th step in subs parsing 
    def concat_short_rows(self,df):    
        cond=lambda prev_row,cur_row,next_row  : len(cur_row['txt'].strip().split(' '))==1 
        df=self._concat_on_condition(df=df,cond=cond)
        self.tmp_df=df 
        self._calculate_pause_to_next(df=self.tmp_df)
        return df 
    
    # moving a row up or down based on condition on that row 
    def _concat_on_condition(self,df,cond):
        indexes_to_remove=[]
        no=1
        min_st_flt=df.iloc[0]['st_flt']
        max_en_flt=df.iloc[0]['en_flt']
        txt=''
        # catching first row  and moving it to second row if it meets condition 
        first_row=df.iloc[0].to_dict()
        second_row=df.iloc[1].to_dict()
        if cond(first_row,first_row,second_row):
            indexes_to_remove.append(0)
            second_row['txt'] = first_row['txt'] + ' ' + second_row['txt']
            second_row['st_flt']=first_row['st_flt']
            df.iloc[1]=second_row

        # does not catch first row
        while no < len(df)-1:
            prev_row=df.iloc[no-1].to_dict()
            cur_row=df.iloc[no].to_dict()
            next_row=df.iloc[no+1].to_dict()
            dif1=cur_row['st_flt']-prev_row['en_flt']
            dif2=next_row['st_flt']-cur_row['en_flt']
            min_st_flt=cur_row['st_flt']
            b=0
            j=no-1
            while cond(prev_row,cur_row,next_row):
                b=1
                txt+= cur_row['txt'] + ' '         # aggregating text 
                max_en_flt=cur_row['en_flt']           # catching end flt 
                min_st_flt=min(cur_row['st_flt'],min_st_flt)
                indexes_to_remove.append(no)    
                no+=1
                if no+1 ==len(df):
                    break
                prev_row=df.iloc[no-1].to_dict()
                cur_row=df.iloc[no].to_dict()
                next_row=df.iloc[no+1].to_dict()       

            if b:                                                         # if concat happened
                last_row=df.iloc[j].to_dict()                             # this row <concat rows 
                future_row=df.iloc[max(indexes_to_remove)+1].to_dict()    # concat rows> this row 
                dif1=min_st_flt- last_row['en_flt']
                dif2=future_row['st_flt'] - max_en_flt  
                if dif1<=dif2 and b : # move concat rows to last row        
                    last_row['txt']=last_row['txt'] + ' ' + txt 
                    last_row['en_flt']=max_en_flt
                    df.loc[j]=last_row
                elif dif1 > dif2 and b: 
                    future_row['txt'] = txt + ' ' + future_row['txt']
                    future_row['st_flt']=min_st_flt
                    df.loc[no]=future_row
            
            txt='' # reset txt 
            no+=1
            
        df=df.drop(indexes_to_remove)
        df.reset_index(inplace=True)
        df['st']=df['st_flt'].apply(self.flt_to_ts)
        df['en']=df['en_flt'].apply(self.flt_to_ts)
        self._calculate_pause_to_next(df=df)        
        return df 
    
    
    def split_rows(self,df):
        def has_dot_in_middle(prev_row,cur_row,next_row): # function checking if row should be splitted 
            foo= '. ' in cur_row['txt'] #or ', ' in cur_row['txt']
            bar=' .' in cur_row ['txt'] #or ' ,' in cur_row['txt']
            return foo or bar
            
        def extract_words(string): # function splitting text 
            chars=['. ',', ','-']
            chars=['. ','-']
            for char in chars:
                if char in string: 
                    return string.split(char)[0].strip()+char.strip(),string.split(char)[1].strip()
        def split_fun(row): # function splitting rows 
            row1=row.copy()
            row2=row.copy()
            row1['txt'],row2['txt']=extract_words(row['txt'])
            w1 = len(row1['txt'])/ ( len(row2['txt']) + len(row1['txt']) ) 
            
            row1['dif']=np.round(row1['en_flt']-row2['st_flt'],2)
            row1['en_flt']=np.round(row1['en_flt'] - row1['dif'] * w1 ,2)
            row2['st_flt']=np.round(row1['en_flt'],2)
            return row1,row2
            
            
        df=self._split_on_condition(df=df,cond=has_dot_in_middle,split_fun=split_fun)
        pd.options.display.max_colwidth = 100
        print(df)
        df.reset_index(inplace=True)
        df['st']=df['st_flt'].apply(self.flt_to_ts)
        df['en']=df['en_flt'].apply(self.flt_to_ts)
        df['dif']=np.round(df['en_flt']-df['st_flt'],2)
        
        self._calculate_pause_to_next(df=df)  
        self.tmp_df=df 
        print(df)
        input('wait')
        return df
    
    def _split_on_condition(self,df,cond,split_fun):
        df2=pd.DataFrame(columns=df.columns)
        indexes_to_remove=[]
        b=True
        no=0
        
        # first row 
        first_row=df.iloc[0].to_dict()
        if cond(first_row,first_row,first_row):
            row1,row2=split_fun(first_row)
            first_row['txt']=row1['txt']
            first_row['en_flt']=row1['en_flt']
            
            second_row=df.iloc[1].to_dict()
            second_row['txt']=row2['txt'] + ' ' + second_row['txt']
            second_row['st_flt']=first_row['en_flt']
            # update first and second row 
            df.loc[0]=first_row
            df.loc[1] = second_row                       
        
        # last row 
        last_row=df.iloc[-1].to_dict()
        if cond(last_row,last_row,last_row):
            second_to_last_row=df.iloc[-2].to_dict()
            row1,row2=split_fun(last_row)
            second_to_last_row['txt']=second_to_last_row['txt'] + ' ' +  row1['txt']
            second_to_last_row['en_flt']=row1['en_flt']
            last_row['txt']=row2['txt']
            df.iloc[-1]=last_row
            df.iloc[-2]=second_to_last_row
            
            
        while no <len(df)-2:
            no+=1
            prev_row=df.iloc[no-1].to_dict()
            cur_row=df.iloc[no].to_dict()
            next_row=df.iloc[no+1].to_dict() # not used
            if cond(cur_row,cur_row,cur_row):
#                input('here')
                indexes_to_remove.append(no)
                row1,row2=split_fun(cur_row)
                # move stuff with dot to prior row 
                prev_row['txt']=prev_row['txt'] + ' ' + row1['txt']
                prev_row['en_flt']=row1['en_flt']                
                # remove stuff moved above from cur row 
                cur_row['txt']=row2['txt']
                cur_row['st_flt']=prev_row['en_flt']
                df.loc[no-1]=prev_row
                df.loc[no]=cur_row
                df.reset_index(inplace=True,drop=True)
                #df=df
                #print(indexes_to_remove)
                #df=df.drop(indexes_to_remove)
                df['st']=df['st_flt'].apply(self.flt_to_ts)
                df['en']=df['en_flt'].apply(self.flt_to_ts)
                
        return df  
     
    
    # tbd     
    # step bringing all parsing methods together  parsing steps together 
    def parse_json3_to_df(self,fp,dump_df=True,**kwargs):
        # step 1 
        df=self.read_json3_to_df(fp=fp)
        if kwargs.get('dump_all'):
            self.dump_df(df=df,name='df1_read_json3_to_df.csv')
        
        # recalculate pause_to_next
        self._calculate_pause_to_next(df=df)
        if dump_df:
            name=kwargs.get('name')
            if name is None:
                name='df_parsed.csv'
            self.dump_df(df=df,name=name)
        return df  
    
    # calculates pause to next row 
    def _calculate_pause_to_next(self,df):
        a=df['en_flt']
        b=df['st_flt'].shift(-1)
        df['pause_flt']=np.round(b-a,2)
#        df.iloc[-1]['pause_flt']=0
        df.loc[len(df)-1,'pause_flt']=1.0
        return a-b


   
# workflow 1 - download and parse subs 
def wf1(ytd: ytd
        ,url='https://www.youtube.com/watch?v=_ypD5iacrnI&ab_channel=MovieRecaps'
        ,download_timestamps=True,
        download_vid=False):
    dir_name=datetime.datetime.now().strftime("%Y%m%d")     # make a dir 
    dir_fp=ytd.path_join(ytd.tmp_dir, dir_name)             # make a dir 
    
    #ytd.make_dir(fp=dir_fp)    # let's make a dir
    ytd.tmp_dir= dir_fp                                     # set a dir 

    if download_timestamps and download_vid:                       # speeds up download fren 
        timestamps=["00:00:00","00:1:00"]
        ytd.download_vid(yt_url=url,timestamps=timestamps)
    else:
        ytd.download_vid(yt_url=url)                        # download whole thing 
    ytd.download_subs(yt_url=url,lang='en')              # download subs 
    ytd.parse_json3_to_df(fp=ytd.subs_fp,dump_all=True)     # parse subs, dump all 
    
        
       
       
        
if __name__=='__main__':
    ytd=ytd()
    url='https://www.youtube.com/watch?v=RMeacmRH0wA&t=3s&ab_channel=symmetry'
    wf1(ytd=ytd,url=url)
   