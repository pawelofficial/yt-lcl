import re 
import os 
import logging
import datetime 
import pandas as pd 
from tabulate import tabulate

    # logger setup 
def setup_logger(name, log_file, level=logging.INFO,mode='w'):
    log_file,_=path_join(dir_l=['logs',log_file])
    print(log_file)
    handler = logging.FileHandler(log_file,mode=mode)        
    BASIC_FORMAT = "%(levelname)s:%(name)s:%(message)s"  
    formatter=logging.Formatter(BASIC_FORMAT)
    handler.setFormatter(formatter)
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)
    return logger

# logs a variable 
def log_variable(logger,msg='',lvl='info',**kwargs):
    ts=datetime.datetime.now().isoformat()
    s=f'{msg} {ts}'
    
    for k,v in kwargs.items():
        s+= f'\n{k} : {v}'
    
    if lvl=='warning':
        logger.warning(s)
    else:
        logger.info(s)
    
    # pathjoin method 
def path_join(dir_l,ext=''):
    # joins list of strings into a path object and return flags indicating if it
    # is a directory or a file         
    current_dir = os.path.dirname(os.path.abspath(__file__))
    path_join = lambda l : os.path.join(current_dir,*l).replace('\\','\\\\')+ext
    path=path_join(dir_l)
    isfile=os.path.isfile(path)
    isdir=os.path.isdir(path)
    exist=os.path.exists(path)
    return path, (isfile,isdir,exist)
    
    # builds yt url from id or channel 
def build_url(id : str = None ,channel : str = None ):
    # builds url from id or from channel 
    vid_url = None 
    channel_url = None 
    
    if id != None :
        vid_url=f'www.youtube.com/watch?v={id}'
    if channel != None :
        channel_url=f'www.youtube.com/{channel}'
    
    d={"id":id
       ,"channel":channel
       ,"vid_url":vid_url
       ,"channel_url":channel_url}
    return d 
    
    # parses url into whatever it ocntains 
def parse_url(url : str ) -> dict:
    # parses yt url into stuff depending on what it contains 
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
        
# changes extension on a string or strips it 
def strip_extension(s: str, new_ext = None ):
    ext_reg=r'^([^.]+)'
    s= re.findall(ext_reg,s)[0]
    if new_ext is None:
        return s 
    s=s+f'.{new_ext}'
    return s.replace('..','.')

def clear_dir(dir='tmp'):
    fp,_=path_join(dir_l=[dir])
    files=os.listdir(fp)
    
    for file in files:
        fp,_=path_join(dir_l=[dir,file])
        isfile=_[0]
        if isfile:
            os.remove(fp)
    

#inserts d into a dataframe
def df_insert_d(df: pd.DataFrame,d : dict ):
    df.loc[len(df)]=d 
    d.clear()
    
    
    # parses subs to a df ! 
def subs_to_df(fp : str,N=5 ):
    subs=open(fp,'r',encoding="utf-8").read()        
    check_line = lambda line: line!='' and '<c>' not in line
    timestamp_pattern = re.compile(r'(\d\d:\d\d:\d\d\.\d\d\d) --> (\d\d:\d\d:\d\d\.\d\d\d)')
    lambda_match_ts = lambda line : timestamp_pattern.match(line)
    line_d={'st':None,'en':None,'txt':None}
    df=pd.DataFrame(columns=line_d.keys())
    lines=[line.strip() for line in subs.splitlines()]     
    # first loop - subs to df 
    for i in range(len(lines)):
        line=lines[i]
        if lambda_match_ts(line):                                # matches 00:00:24.400 --> 00:00:26.470 align:start position:0%
            line_d['st']=timestamp_pattern.match(line).group(1)  # save start timestamps 
            line_d['en']=timestamp_pattern.match(line).group(2)  # save end timestamp 
            chunk=[]                                             # stuff between timestamps   
            i=i+1                                                # increment to next line 
            next_line=lines[i]                                   # next line             
            while not lambda_match_ts(next_line):                # while not next ts line 
                if check_line(next_line):                   # function to weed out bad lines 
                    chunk.append(next_line)
                i+=1
                try:
                    next_line=lines[i]
                except IndexError as er:                         # if at the end of the file break while loop
                    break
            line_d['txt']=chunk                                  # save stuff between lines to a d 
            if line_d['txt']!=[]:                                # if it's not empty then save it 
                line_d['txt']=' '.join(line_d['txt'])
                df_insert_d(df=df,d=line_d)
    
    lambda_textlen = lambda s: len(s.split(' '))
    line_d={'st':None,'en':None,'txt':None}
    df2=pd.DataFrame(columns=line_d.keys())
    # second loop - concat rows that don't make sense 
    for no,row in df.iterrows():
        try:
            next_row=df.loc[no+1]
        except KeyError as er:
            break
        txt=row['txt']
        st=row['st']
        en=row['en']
        line_d['txt']=txt
        line_d['st']=st
        line_d['en']=en
        if lambda_textlen(next_row['txt'])<=N: # if next row is a one liner add it to current row 
            line_d['txt'] += ' ' + next_row['txt']
            line_d['en'] = next_row['en']
        if lambda_textlen(txt)<=N:      # if current row is one liner dont write it 
            pass            
        else:                           # write more than one liners 
            df_insert_d(df=df2,d=line_d)
            
    df2['len']=round(df2['en'].apply(ts_to_float)-df2['st'].apply(ts_to_float),2)
    cols=['st','en','len','txt']
    return df2[cols]

def ts_to_float(s = None): # string timestamp to float 
    #s='00:01:04.200'
    hh,mm,ss,ff=s.replace('.',':').split(':')
    dt=round(float(ff)/1000+float(ss)+float(mm)*60+float(hh)*60*60,3)
    return dt 

def float_to_ts(ff = None ):
    hh=ff/60/60//1
    mm=(ff-hh*60*60)/60//1
    ss=(ff-hh*60*60-mm*60)
    return '{:02d}:{:02d}:{:02d}'.format(int(hh), int(mm), int(ss))
    
    
    
# aggregates df to n seconds chunks 
def aggregate_df(df,N=30,txt_col='txt',start_col='st',end_col='en'):
    agg_df=pd.DataFrame(columns=[start_col,end_col,txt_col])
    text=''
    

    df[start_col]=df[start_col].apply(ts_to_float)
    df[end_col]=df[end_col].apply(ts_to_float)
    start=df.loc[0,start_col]
    end=df.loc[0,end_col]
    
    cur_chunk=0
    d={'st':None,'en':None,'txt':None}
    d['st']=start
    d['en']=end
    d['txt']=text
    for no,row in df.iterrows():
        ts_chunk=row[end_col]//N
        d['txt'] += ' ' + row[txt_col]
        d['en'] = row[end_col]
        d['st']=min(start,row[start_col])
#        print(no)
#        print(d)
#        input('wait')
        if ts_chunk !=cur_chunk:  # agg flipped to next row 
            print('             writing')
            start=d['en']
            df_insert_d(df=agg_df,d=d)
            d['st']=start
            cur_chunk+=1
            d['txt']=''
#            print(agg_df)
#            print(tabulate(agg_df, headers='keys', tablefmt='psql')  )
    agg_df.rename(columns={
        start_col:f'{start_col}_flt'
        ,end_col:f'{end_col}_flt'
    },inplace=True)
    
    return agg_df
    
    
    
    for no,row in df.iterrows():
        cur_chunk=row[end_col]//N  # current chunk 
        if cur_chunk!=chunk:                         #
            text += ' ' + row[txt_col]
            agg_df.loc[len(agg_df)+1]=row
            agg_df.loc[len(agg_df),txt_col]=text
            agg_df.loc[len(agg_df),start_col]=start
            agg_df.loc[len(agg_df),end_col]=end
            start=row[end_col]    # new start 

            chunk +=1
            text=''
        else:
            text +=' '+ row[txt_col] # aggregate text 
            end = row[end_col]   # update end 
            
    agg_df.rename(
        columns={start_col:f'{start_col}_flt'
                 ,end_col:f'{end_col}_flt'
                 },inplace=True)
    
    
    return agg_df
   
#        
if __name__=='__main__':
    
    fp=path_join(
        dir_l=['tmp','THEY_DISCOVERED_ADVANCE_TINY_HUMANS_LIVING_IN_A_FRIDGE.csv']
    )[0]
    df=pd.read_csv(fp,sep='|')
    agg_df=aggregate_df(df=df)
    
    fp=path_join(dir_l=['tmp','agg_df.csv'])[0]
    agg_df.to_csv(path_or_buf=fp,sep='|',quoting=1)
    
    
    exit(1)
    
    
    f='THEY_DISCOVERED_ADVANCE_TINY_HUMANS_LIVING_IN_A_FRIDGE.txt'
    out='THEY_DISCOVERED_ADVANCE_TINY_HUMANS_LIVING_IN_A_FRIDGE.csv'
    fp=path_join(dir_l=['tmp',f])[0]
    out_fp=path_join(dir_l=['tmp',out])[0]
    df=subs_to_df(fp)
    
    
    df.to_csv(out_fp,sep='|',quoting=1)
    
    exit(1)



#    print(tabulate(df.iloc[:20], headers='keys', tablefmt='psql')  )
#
#    grp = df.groupby('txt', as_index=False).agg({'st': 'min', 'en': 'max'})
#    grp.sort_values(by='st',inplace=True)
#    print(tabulate(grp.iloc[:20], headers='keys', tablefmt='psql')  )

    

    fp=path_join(dir_l=['tmp','RANDALL_CARLSON__GRAHAM_HANCOCK_ON_LOST_TECHNOLOGY_AND_THE_GREAT_PYRAMIDS.csv'])[0]
    
    df=pd.read_csv(filepath_or_buffer=fp,delimiter='|')
    print(tabulate(df.iloc[:20], headers='keys', tablefmt='psql')  )
    
    new_df=clear_subs_df(df=df)
    grp = new_df.groupby('text', as_index=False).agg({'start': 'min', 'end': 'max'})
    print(tabulate(new_df, headers='keys', tablefmt='psql')  )
    exit(1)
    grp.sort_values(by='start',inplace=True)
    print(tabulate(grp.iloc[:20], headers='keys', tablefmt='psql')  )
    
    
    exit(1)
    cl_df=clear_subs_df(df=df)


    print(df)

    print(cl_df)
    
