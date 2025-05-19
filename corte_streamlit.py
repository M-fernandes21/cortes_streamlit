import streamlit as st
import os
from moviepy.editor import VideoFileClip
from pydub import AudioSegment, silence
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip

def extrair_audio(video_path, audio_path="audio.wav"):
    video = VideoFileClip(video_path)
    video.audio.write_audiofile(audio_path)
    return audio_path

def detectar_pausas(audio_path, min_silencio_ms=700, silencio_db=-40):
    audio = AudioSegment.from_wav(audio_path)
    silencios = silence.detect_silence(audio, min_silencio_ms=min_silencio_ms, silence_thresh=silencio_db)
    return [(i/1000, f/1000) for i, f in silencios]

def gerar_cortes(video_path, pausas, margem=0.5, min_duracao=3):
    cortes = []
    inicio_anterior = 0
    for inicio, fim in pausas:
        if inicio - inicio_anterior >= min_duracao:
            cortes.append((inicio_anterior, inicio - margem))
        inicio_anterior = fim + margem
    return cortes

def salvar_cortes(video_path, cortes, pasta_saida="cortes"):
    if not os.path.exists(pasta_saida):
        os.makedirs(pasta_saida)
    caminhos = []
    for i, (inicio, fim) in enumerate(cortes):
        nome = os.path.join(pasta_saida, f"corte_{i+1}.mp4")
        ffmpeg_extract_subclip(video_path, int(inicio), int(fim), targetname=nome)
        caminhos.append(nome)
    return caminhos

st.set_page_config(page_title="Corte Automático de Vídeos", page_icon="✂️", layout="centered", initial_sidebar_state="collapsed")

st.markdown(
    '''
    <style>
    body {
        background-color: #121212;
        color: #e0e0e0;
    }
    .stButton>button {
        height: 3em;
        font-size: 1.1em;
    }
    </style>
    ''',
    unsafe_allow_html=True,
)

st.title("Corte Automático de Vídeos - Interface")

uploaded_file = st.file_uploader("Escolha o vídeo para cortar", type=["mp4", "mov", "avi"])

min_silencio_ms = st.slider("Silêncio mínimo (ms)", min_value=200, max_value=3000, value=700, step=100)
margem_corte = st.slider("Margem de corte (s)", min_value=0.0, max_value=3.0, value=0.5, step=0.1)
min_duracao_corte = st.slider("Duração mínima do corte (s)", min_value=1, max_value=15, value=3, step=1)

if uploaded_file is not None:
    with open("temp_video.mp4", "wb") as f:
        f.write(uploaded_file.getbuffer())
    st.success("Vídeo carregado com sucesso!")
    if st.button("Iniciar corte automático"):
        st.info("Processando vídeo, aguarde...")
        try:
            audio_path = extrair_audio("temp_video.mp4")
            pausas = detectar_pausas(audio_path, min_silencio_ms=min_silencio_ms, silencio_db=-40)
            cortes = gerar_cortes("temp_video.mp4", pausas, margem=margem_corte, min_duracao=min_duracao_corte)
            caminhos = salvar_cortes("temp_video.mp4", cortes)
            st.success(f"{len(cortes)} cortes gerados com sucesso!")
            for caminho in caminhos:
                st.write(f"- {caminho}")
        except Exception as e:
            st.error(f"Erro: {e}")
else:
    st.info("Envie um vídeo para começar.")