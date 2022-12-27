import torch
import zipfile
import torchaudio
from glob import glob
from silero import silero_stt, silero_tts, silero_te
import librosa
import matplotlib.pyplot as plt 
device = torch.device('cpu')  # gpu also works, but our models are fast enough for CPU

model, decoder, utils = torch.hub.load(repo_or_dir='snakers4/silero-models',
                                       model='silero_stt',
                                       language='en', # also available 'de', 'es'
                                       device=device)
(read_batch, split_into_batches,
 read_audio, prepare_model_input) = utils  # see function signature for details

# download a single file, any format compatible with TorchAudio (soundfile backend)
#torch.hub.download_url_to_file('https://opus-codec.org/static/examples/samples/speech_orig.wav',
#                               dst ='speech_orig.wav', progress=True)


def plot_waveform(waveform, sample_rate):
    waveform = waveform.numpy()

    num_channels, num_frames = waveform.shape
    time_axis = torch.arange(0, num_frames) / sample_rate

    figure, axes = plt.subplots(num_channels, 1)
    if num_channels == 1:
        axes = [axes]
    for c in range(num_channels):
        axes[c].plot(time_axis, waveform[c], linewidth=1)
        axes[c].grid(True)
        if num_channels > 1:
            axes[c].set_ylabel(f"Channel {c+1}")
    figure.suptitle("waveform")
    plt.show(block=False)

def plot_specgram(waveform, sample_rate, title="Spectrogram"):
    waveform = waveform.numpy()

    num_channels, num_frames = waveform.shape

    figure, axes = plt.subplots(num_channels, 1)
    if num_channels == 1:
        axes = [axes]
    for c in range(num_channels):
        axes[c].specgram(waveform[c], Fs=sample_rate)
        if num_channels > 1:
            axes[c].set_ylabel(f"Channel {c+1}")
    figure.suptitle(title)
    plt.show(block=False)
    
f='./vids/speech_orig.wav' # 48000 16000
jre='./vids/Hilarious_Hitler_on_Speed__Joe_Rogan_Experience_48000.wav'
jre='./vids/jre_multi_1.wav'

m1 = torchaudio.info(f)
m2=torchaudio.info(jre)
print(m2)
print(m2.num_frames)
exit(1)


wv,sr=torchaudio.load(jre)

wv2=torch.sum(wv,dim=0).view(1,-1)
torchaudio.save('./vids/jre_multi_2.wav',wv2,sr)
exit(1)
print(m1)
print(m2) # 2 channels 
exit(1)
t1 = torchaudio.load(f)


waveform, sample_rate = torchaudio.load(jre)
t2=torch.sum(waveform,dim=0)


test_files = glob(jre)
batches = split_into_batches(test_files, batch_size=5)

for no,batch in enumerate(batches):

    input = prepare_model_input(read_batch(batch),device=device)
    output = model(input) # tensor 
    
    for example in output:
        print(decoder(example.cpu()))