import os 
import numpy as np 
import librosa 
import soundfile as sf
import torchaudio
import torch 
import re 
from torchaudio.models.decoder import download_pretrained_files
from torchaudio.models.decoder import ctc_decoder
files = download_pretrained_files("librispeech-4-gram")

if __package__=='wizard':
    from .utils import *
    from .transcript import transcript
        

# simple wave to text model if for some reason yt subtitles are not available     
class speechToText:
    def __init__(self) -> None:
        self.nsec=5
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.vids_dir=os.path.join(current_dir,'vids\\').replace("\\","\\\\")        
        self.configs_dir=os.path.join(current_dir,'configs\\').replace("\\","\\\\")     
        self.transcripts_dir=os.path.join(current_dir,'transcripts\\parsed\\').replace("\\","\\\\")     
        self.logger=setup_logger(name='speechToText_logger',log_file='speechToText_logger.log')
        self.vid=None
        self.transcript=transcript() # transcript object 
        
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        self.bundle = torchaudio.pipelines.WAV2VEC2_ASR_BASE_960H
        #self.bundle = torchaudio.pipelines.HUBERT_BASE
        self.bundle = torchaudio.pipelines.HUBERT_ASR_LARGE
        #self.bundle = torchaudio.pipelines.HUBERT_ASR_XLARGE
        self.model = self.bundle.get_model().to(self.device)

    # logs a variable 
    def log_variable(self,var,msg='',wait=False,lvl='INFO'):
        log_variable(logger=self.logger,var=var,msg='',wait=False,lvl=lvl)
    # returns indices of chunks of tensor of  [1,N] shape with a percentage overlap  
    def chunkify2(self,t,n=3,ovr=0.1): 
        # returns indexes that correspond to chunks of a tensor of shape [1,N] with overlap
        # why would you use it? the same reason as you would use a torch.chunk but here you have overlap 
        L=t.shape[1]        # len of tensor 
        q=L//n+1            # index multiplier 
        e=0                 # end index of tensor 
        i=-1                # index declaration 
        overlap=int(ovr*L)  # overlap in percentages 
        indices=[]           # list to store subtensors 
        while e < L: 
            i+=1
            s=i* q - (overlap if i > 0 else 0)  
            e=(i+1) * q 
            indices.append([s,e] )
        return indices
    # returns indices of waveform tensors that correspond to chunks by seconds and their respective timestamps 
    def chunkify_by_seconds(self,wv,sr,nsec=5,ovr_sec=1):
        vid_len=wv.shape[1]/sr # vid len in seconds 
        indices=[]
        start_index=0
        i=1
        end_index=i*self.nsec*sr 
        which_second = lambda i,wv,sr : np.round(i/wv.shape[1] * ( wv.shape[1]/sr ),2)
        
        while end_index<=wv.shape[1]:
            ovr_end_index=np.min([end_index + ovr_sec * sr,wv.shape[1]])  # index when overwrite is applied, min makes sure you don't overflow above wv len
            indices.append([start_index,ovr_end_index,which_second(start_index,wv,sr)])
            i+=1
            start_index=end_index
            end_index=i*self.nsec*sr 

        indices.append([start_index,wv.shape[1],which_second(start_index,wv,sr)])
        return indices
                
    def wav_to_text(self,vid_name,save=True):
        self.vid=self.vids_dir+vid_name
        self.vid = re.sub('(\\..*)','',self.vid)+'.wav'
        
        wv, sample_rate = torchaudio.load(self.vid)
        LM_WEIGHT = 5 #  3.23
        WORD_SCORE = -0.26
        beam_search_decoder = ctc_decoder(
                    lexicon=self.configs_dir+'lexicon.txt',#  files.lexicon,
                    tokens=files.tokens,
                    lm=files.lm,
                    nbest=3,
                    beam_size=1500,
                    lm_weight=LM_WEIGHT,
                    word_score=WORD_SCORE,
                )
        for ind in self.chunkify_by_seconds(wv=wv,sr=sample_rate,nsec=5,ovr_sec=1):
            s=ind[0]
            e=ind[1]
            ts=self.float_to_ts(ind[2])
            end_ts=self.float_to_ts(ind[2]+self.nsec)
            waveform=wv[:,s:e]
            waveform = waveform.to(self.device)
            if sample_rate != self.bundle.sample_rate:
                waveform = torchaudio.functional.resample(waveform, sample_rate, self.bundle.sample_rate)

            with torch.inference_mode():
                emission, _ = self.model(waveform)

            beam_search_result = beam_search_decoder(emission)
            transcript = " ".join(beam_search_result[0][0].words).strip()
              
            print(transcript)
            if save:
                file_name=vid_name.split('.')[0].strip()+'.txt'
                with open(self.transcripts_dir+file_name,'a') as f:
                    s=f"{ts} || {end_ts} || {transcript}\n"
                    f.write(s)
                    
    def float_to_ts(self,ts):
        hour=float(ts)//60//60
        min=float(ts)//60 - hour 
        sec=float(ts) - hour*60*60 - min *60
        time_string="{:02d}:{:02d}:{:02d}.{:03d}".format(int(hour), int(min), int(sec), int(0))
        return time_string

if __name__=='__main__':
    from utils import * 
    from transcript import transcript
    
    sa=speechToText()

    f='Justin_Gaethje_Problem_With_Barstools_Dave_Portnoy.wav'
#    sa.wav_to_text(vid_name=f)
#    input('wait')    
    f='Justin_Gaethje_Problem_With_Barstools_Dave_Portnoy.txt'
#    f='Gareth_Soloway_Bitcoin_to_target_9k_SP_500_to_fall_25_in_2023_no_early_Fed_rescue.txt'
    filepath=path_join(l=['transcripts','parsed',f])
    sa.transcript.read_transcript(filepath=filepath)
    print(sa.transcript.tr_df)


