import wizard as wiz 
import re 
from wizard.utils import path_join,build_url


w=wiz.wizard()

urls=[
    'https://www.youtube.com/watch?v=AjmpznRmAIQ&ab_channel=KitcoNEWS'
    ,'https://www.youtube.com/watch?v=Mp1_T3hmogc&ab_channel=KitcoNEWS'
    ,'https://www.youtube.com/watch?v=JpQFFn948gw&ab_channel=KitcoNEWS'
    ,'https://www.youtube.com/watch?v=A5R_XbKcKKw&ab_channel=KitcoNEWS'
    ,'https://www.youtube.com/watch?v=A5R_XbKcKKw&ab_channel=KitcoNEWS'
    ,'https://www.youtube.com/watch?v=xNcvXBGFQCY&ab_channel=KitcoNEWS'
#    ,'https://www.youtube.com/watch?v=JZPozJbi_Mw&ab_channel=KitcoNEWS'    
      ]
 

#@f='AMC_down_40_stock_market_plunge_to_continue_no_new_highs_for_10_years__Gareth_Soloway'
#@f='Bitcoin_dropped_30_in_a_month_heres_whats_next__Gareth_Soloway_updates_gold_stocks_crypto'
#@w.ytDownloader.parse_yt_subs(dir='transcripts\\raw',filename=f)

#for url in urls:
# #   pass
#    f,_=w.download_vid(yt_url=url) # download and parse transcript
#    w.read_transcript(filename=f)  # read transcript 
#    w.scan_transcript(keyword='bitcoin') # scan transcript for a keyword 
    

#    w.ytDownloader.parse_yt_subs(dir='transcripts\\raw',filename=vid)
#   w.speech_to_text(vid_name=vid)

def example1(): # example 1 of wizard capabilities - download yt subtitles 
    w=wiz.wizard()
    url='https://www.youtube.com/watch?v=AjmpznRmAIQ&ab_channel=KitcoNEWS'
#    url='https://www.youtube.com/watch?v=6QfX1PDw7cQ&ab_channel=nyatponggaming'
#    url='https://www.youtube.com/watch?v=HjhCv2d5z_k'
    url='https://www.youtube.com/watch?v=HjhCv2d5z_k&ab_channel=LibertyandFinance'
    f,_,_=w.download_vid(yt_url=url)

def example2(): # download yt subtitles and perform transcript scan for a kayeowrd 
    w=wiz.wizard()
    url='https://www.youtube.com/watch?v=AjmpznRmAIQ&ab_channel=KitcoNEWS'
    f,_,_=w.download_vid(yt_url=url)
    w.read_transcript(filename=f)
    matches=w.scan_transcript(keyword='bitcoin',threshold=90)
    print(matches)
    
def example3(): # uses pytorch wav to speech to make a transcript 
    w=wiz.wizard()
    url='https://www.youtube.com/watch?v=zurNfKQB5Cw&ab_channel=MotivationHub'
    f,_,_=w.download_vid(yt_url=url)
    w.speech_to_text(vid_name=f)
    w.read_transcript(filename=f)
    matches=w.scan_transcript(keyword='bitcoin',threshold=50)
    print(matches)

def example4(): # check out updates on channel:
    w=wiz.wizard()
    url='https://www.youtube.com/watch?v=AjmpznRmAIQ&ab_channel=KitcoNEWS'
#    url='https://www.youtube.com/@kitco'
    d=w.ytDownloader.get_channel_info(channel_url=url)
    return d 

def get_channel_info(w : wiz.wizard,url) -> list : # return last n ids uploaded to the channel 
    d=w.ytDownloader.get_channel_info(channel_url=url)
    return list(d.keys())

def check_ids_not_present_in_db(w: wiz.wizard,l):
    o=w.db.select_antijoin(table_name='TEST',column_name='ID',l=l)
    return o 
    
# id, url, title, transcript_raw, transcript_parsed 

if __name__=='__main__':

    w=wiz.wizard()
    url='https://www.youtube.com/@kitco'
    url='https://www.youtube.com/@LibertyandFinance'
#    l=get_channel_info(w=w,url=url)             # get last n videos uploaded 

#    o=check_ids_not_present_in_db(w=w,l=l)      # get videos that are not in db 
    # download subtitles of new videos and insert them into db 
    d={}
    l=['3Ic_3pP6y1E']
    for id in l:
        print(id)
        d['ID']=id
        url=build_url(s=id,from_id=True)
        url='https://www.youtube.com/watch?v=3Ic_3pP6y1E&ab_channel=LibertyandFinance'
        fname,ext,org_title=w.download_vid(yt_url=url)
        d['URL']=url
        d['TITLE']=fname
        d['RAW_TRANSCRIPT']=open(path_join(l=['transcripts','raw',fname+'.txt']),'r').read()
        d['PARSED_TRANSCRIPT']=open(path_join(l=['transcripts','parsed',fname+'.txt']),'r').read()
        w.db.insert_into_d(table_name='TEST',d=d)
        exit(1)
#        o=w.db.select_star(table_name='TEST')
