import streamlit as st
from moviepy.editor import VideoFileClip, concatenate_videoclips
import whisper
from pydub import AudioSegment, silence

st.title("App de Cortes Automáticos com IA")

uploaded_file = st.file_uploader("Envie seu vídeo", type=["mp4", "mov", "avi"])

if uploaded_file:
    with open("temp_video.mp4", "wb") as f:
        f.write(uploaded_file.getbuffer())
    st.video("temp_video.mp4")

    st.info("Carregando modelo Whisper...")
    model = whisper.load_model("base")

    st.info("Transcrevendo áudio do vídeo...")
    result = model.transcribe("temp_video.mp4")
    st.write("Transcrição:")
    st.write(result["text"])

    audio = AudioSegment.from_file("temp_video.mp4")
    silences = silence.detect_silence(audio, min_silence_len=700, silence_thresh=-40)
    silences_sec = [(start/1000, stop/1000) for start, stop in silences]

    st.write("Silêncios detectados (segundos):", silences_sec)

    video = VideoFileClip("temp_video.mp4")

    fala_intervals = []
    start = 0
    for silence_start, silence_end in silences_sec:
        fala_intervals.append((start, silence_start))
        start = silence_end
    fala_intervals.append((start, video.duration))

    st.write("Intervalos de fala para manter:", fala_intervals)

    clips = [video.subclip(start, end) for start, end in fala_intervals if end > start + 1]

    if clips:
        final_clip = concatenate_videoclips(clips)
        final_clip.write_videofile("video_cortado.mp4", codec="libx264")
        st.success("Vídeo cortado criado!")
        st.video("video_cortado.mp4")
    else:
        st.warning("Vídeo não possui segmentos de fala detectados.")
