# %matplotlib inline

import os

import IPython
import matplotlib
import matplotlib.pyplot as plt
import requests
import torch
import torchaudio
from difflib import SequenceMatcher

import IPython
import matplotlib.pyplot as plt
from torchaudio.models.decoder import ctc_decoder
from torchaudio.utils import download_asset
import numpy as np 

matplotlib.rcParams["figure.figsize"] = [16.0, 4.8]

torch.random.manual_seed(0)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

print(torch.__version__)
print(torchaudio.__version__)
print(device)

SPEECH_URL = "https://pytorch-tutorial-assets.s3.amazonaws.com/VOiCES_devkit/source-16k/train/sp0307/Lab41-SRI-VOiCES-src-sp0307-ch127535-sg0042.wav"  # noqa: E501
SPEECH_FILE = "_assets/speech.wav"

f='Hilarious_Hitler_on_Speed__Joe_Rogan_Experience_22050'
f='jre_multi_1'
#f='speech_orig'
SPEECH_FILE=f'./vids/{f}.wav'
n_frames=torchaudio.info(SPEECH_FILE).num_frames
s_rate=torchaudio.info(SPEECH_FILE).sample_rate
file_len=n_frames/s_rate
chunk_30s=int(30/file_len*n_frames) # len of tensor that corresponds to 30s 
n_chunks=int(np.ceil(n_frames/chunk_30s)) # number of 30s chunks in a video 


bundle = torchaudio.pipelines.WAV2VEC2_ASR_BASE_960H
#bundle = torchaudio.pipelines.HUBERT_BASE
#bundle = torchaudio.pipelines.HUBERT_ASR_LARGE
#bundle = torchaudio.pipelines.HUBERT_ASR_XLARGE
model = bundle.get_model().to(device)

labels=bundle.get_labels()
print(labels)

from torchaudio.models.decoder import download_pretrained_files
files = download_pretrained_files("librispeech-4-gram")
print(files)
exit(1)

class GreedyCTCDecoder(torch.nn.Module):
    def __init__(self, labels, blank=0):
        super().__init__()
        self.labels = labels
        self.blank = blank
        self.keys=['SHEEP']
        self.sep='|'
    
    def scan(self,output : str = None ):
        sims=[]
        for key in self.keys:
            for word in output.split(self.sep):
                sim=SequenceMatcher(None,word,key).ratio()
                sims.append(sim)
        pass 

    def forward(self, emission: torch.Tensor) -> str:
        """Given a sequence emission over labels, get the best path string
        Args:
          emission (Tensor): Logit tensors. Shape `[num_seq, num_label]`.

        Returns:
          str: The resulting transcript
        """
        indices = torch.argmax(emission, dim=-1)  # [num_seq,]
        indices = torch.unique_consecutive(indices, dim=-1)
        indices = [i for i in indices if i != self.blank]
        output= "".join([self.labels[i] for i in indices])
        self.scan(output=output)
        return output

    

decoder = GreedyCTCDecoder(labels=bundle.get_labels())


waveform_1, sample_rate = torchaudio.load(SPEECH_FILE)

#print(waveform_1.shape)
#
#foo=torch.chunk(waveform_1,chunks=2,dim=1)
#print(foo[0].shape)
#exit(1)

def chunkify2(t,n=3,ovr=0.01): 
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


for ind in chunkify2(t=waveform_1,n=10,ovr=0.01):
    s=ind[0]
    e=ind[1]
    waveform=waveform_1[:,s:e]
    waveform = waveform.to(device)
    if sample_rate != bundle.sample_rate:
        waveform = torchaudio.functional.resample(waveform, sample_rate, bundle.sample_rate)

    with torch.inference_mode():
        features, _ = model.extract_features(waveform)

    with torch.inference_mode():
        emission, _ = model(waveform)


    transcript = decoder(emission[0]).replace('|',' ')
    print(transcript)
    print(waveform.shape,s,e)
    print('-----------------')