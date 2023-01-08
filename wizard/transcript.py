import os 
import numpy as np 
import librosa 
import soundfile as sf
import torchaudio
import torch 
from torchaudio.models.decoder import download_pretrained_files
from torchaudio.models.decoder import ctc_decoder
files = download_pretrained_files("librispeech-4-gram")
import nltk 
import pandas as pd 
from difflib import SequenceMatcher
import re 

import datetime 

if __package__=='wizard':
    from .utils import *
    
# lets use pandas xd 
class transcript:
    def __init__(self) -> None:
        self.keys=['start_sec','end_sec','start_ts','end_ts','chunk']                        # keys/ column in the transcript cf 
        self.keywords=['romania']
        self.tr_dic={}.fromkeys(self.keys)              # dictionary for saving stuff to df 
        self.tr_df=pd.DataFrame(self.tr_dic,index=[0])  # transcript df 
        
        self.ts_to_sec = lambda s: datetime.datetime.strptime(s, "%H:%M:%S.%f").second+datetime.datetime.strptime(s, "%H:%M:%S.%f").minute*60+datetime.datetime.strptime(s, "%H:%M:%S.%f").hour*60*60
        
        
    # saves kwargs to tr_df if kwarg key is in self.keys 
    def save(self,**kwargs):
        for key,value in kwargs.items():
            if key not in self.keys:
                print(f' cant write unknown column -> {key} to transcript ')
            self.tr_dic[key]=value
        self.tr_df.loc[len(self.tr_df),:]=self.tr_dic
        self.tr_dic.clear()

    # reads temporary txt files to populate tr_df with transcript 
    def read_transcript(self,filepath):
        filepath=re.sub('(\\..*)','',filepath)+'.txt'
        with open(filepath,'r') as f:
            for line in f.readlines():
                start_ts=line.split('||')[0].strip()
                end_ts=line.split('||')[1].strip()
                chunk=line.split('||')[2].strip()
                start_sec=self.ts_to_sec(start_ts)                    # start ts 
                end_sec=self.ts_to_sec(end_ts) 
                self.save(start_sec=start_sec,
                          end_sec=end_sec,
                          chunk=chunk,
                          start_ts=start_ts,end_ts=end_ts)  # save 
        
    # this should be done on words embedding rather than simple string comparison, but let's do it later 
    def compare_words(self,w1,w2):
        return SequenceMatcher(None,w1,w2).ratio()*100 
        
    # dictionary with matches for provided keyword
    # this will fail in finding a word someone if the transcript puts it into "some one"
    def scan(self,keyword='romania',threshold=80):
        matches={}
        for i,row in self.tr_df.iterrows():
            if i==0: # skip first row which is none 
                continue
            words=[word.strip() for word in row['chunk'].split(' ')]
            
            for word in words:
                score=self.compare_words(keyword,word)
                if score > threshold:
                    matches[row['start_ts']]=row['chunk']
        return matches 

        


if __name__=='__main__':
    from utils import * 
    
    t=transcript()
    f2='Gareth_Soloway_Bitcoin_to_target_9k_SP_500_to_fall_25_in_2023_no_early_Fed_rescue.txt'
#    f2='What_ChatGPT_Could_Mean_for_the_Future_of_Artificial_Intelligence.wav'

    sa.transcript.scan(keyword='gold')

#cool 20min transcript here on gold keyword 
#{60.0: 'when you called for god to be the most dominant asset again this her relative', 1030.0: 'old condition of natural gas came right into the three and a half level which is by the way going back', 1045.0: "as a natural gas so again there's always trading opportunities of course still love gold i'm sure we'll touch", 1065.0: "let's let's finish up gold gold you said was going to be the best of the best class of the year compared", 1085.0: 'we are coming into some resistance on gold so you might get a little bit of a pull back you can see that this hope consoled', 1095.0: "i do think that gold is going to head sharply higher to show you this this parallel channel it's one of my favorite", 1105.0: 'this is what we would call a bullish consolidation multi year period of gold and what this tells us', 1130.0: 'action and then gold literally went from about a hundred dollars at once back into a thousand nine hundred dollars', 1135.0: "nine hundred dollars an ounce and again i'm not calling for nine or ten on gold here i think i'd be very happy with you", 1140.0: 'happy with two or three times as old as you know for me this is the play right now', 1145.0: 'right now i think next year and twenty twenty four and very likely it would be the best performer but gold', 1150.0: 'but gold again is the safest best bet here for twenty twenty three i see you might be'}
