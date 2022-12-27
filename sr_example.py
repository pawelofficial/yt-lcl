import torch
import zipfile
import torchaudio
from glob import glob
from silero import silero_stt, silero_tts, silero_te
import librosa
from pydub import AudioSegment
import speech_recognition as sr 
import io 
device = torch.device('cpu')  # gpu also works, but our models are fast enough for CPU

model, decoder, utils = torch.hub.load(repo_or_dir='snakers4/silero-models',
                                       model='silero_stt',
                                       language='en', # also available 'de', 'es'
                                       device=device)
(read_batch, split_into_batches,
 read_audio, prepare_model_input) = utils  # see function signature for details


r=sr.Recognizer()

with sr.Microphone(sample_rate=16000) as mic:
    r.adjust_for_ambient_noise(mic)
    print('start speaking')
    while True:
        audio=r.listen(mic)
        audio=io.BytesIO(audio.get_wav_data())
        audio=AudioSegment.from_file(audio)
        x=torch.FloatTensor(audio.get_array_of_samples()).view(1,-1)
        x=x.to(device)
        z=model(x)
        print('you said: ', decoder(z[0]))