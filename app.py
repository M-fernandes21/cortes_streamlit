
import streamlit as st
from moviepy.editor import VideoFileClip
import tempfile

st.title("Corte de Vídeo Simples com MoviePy + Streamlit")

uploaded_file = st.file_uploader("Envie um vídeo", type=["mp4", "mov", "avi"])

if uploaded_file is not None:
    tfile = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
    tfile.write(uploaded_file.read())
    tfile.close()

    clip = VideoFileClip(tfile.name)
    duration = clip.duration

    st.video(tfile.name)
    st.write(f"Duração do vídeo: {duration:.2f} segundos")

    start = st.number_input("Início (segundos)", min_value=0.0, max_value=duration, value=0.0)
    end = st.number_input("Fim (segundos)", min_value=0.0, max_value=duration, value=duration)

    if st.button("Cortar vídeo"):
        if start >= end:
            st.error("Início deve ser menor que fim!")
        else:
            with st.spinner("Processando corte..."):
                cut_clip = clip.subclip(start, end)
                output_path = "video_cortado.mp4"
                cut_clip.write_videofile(output_path, codec="libx264", audio_codec="aac")
                cut_clip.close()

            st.success("Vídeo cortado com sucesso!")
            st.video(output_path)

    clip.close()
