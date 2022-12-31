import torchaudio 
import numpy  as np 

# files: 
fs=['Hilarious_Hitler_on_Speed__Joe_Rogan_Experience_22050','jre_multi_1','speech_orig']
speech_file=f'./vids/{fs[1]}.wav'

# calculate 30s chunks info  
def calc_chunks(speech_file = speech_file, sec = 30 ):
    n_frames=torchaudio.info(speech_file).num_frames
    s_rate=torchaudio.info(speech_file).sample_rate
    file_len=n_frames/s_rate
    chunk_30s=int(sec /file_len*n_frames) # len of tensor that corresponds to 30s 
    n_chunks=int(np.ceil(n_frames/chunk_30s)) # number of 30s chunks in a video 
    return chunk_30s, n_chunks 

# get tensor 
bundle = torchaudio.pipelines.WAV2VEC2_ASR_BASE_960H
acoustic_model=bundle.get_model()
waveform, sample_rate = torchaudio.load(speech_file)

if sample_rate != bundle.sample_rate:
    waveform = torchaudio.functional.resample(waveform, sample_rate, bundle.sample_rate)


# download files , or use cached 
if 1:
    from torchaudio.models.decoder import download_pretrained_files
    files = download_pretrained_files("librispeech-4-gram")
    print(files)

LM_WEIGHT = 5 #  3.23
WORD_SCORE = -0.26

# make a decoder 
from torchaudio.models.decoder import ctc_decoder
beam_search_decoder = ctc_decoder(
    lexicon=files.lexicon,
    tokens=files.tokens,
    lm=files.lm,
    nbest=3,
    beam_size=1500,
    lm_weight=LM_WEIGHT,
    word_score=WORD_SCORE,
)

actual_transcript = "i really was very much afraid of showing him how much shocked i was at some parts of what he said"
actual_transcript = actual_transcript.split()
emission, _ = acoustic_model(waveform)


beam_search_result = beam_search_decoder(emission)
beam_search_transcript = " ".join(beam_search_result[0][0].words).strip()
beam_search_wer = torchaudio.functional.edit_distance(actual_transcript, beam_search_result[0][0].words) / len(
    actual_transcript
)

print(f"Transcript: {beam_search_transcript}")
print(f"WER: {beam_search_wer}")


# https://github.com/pyannote/pyannote-audio