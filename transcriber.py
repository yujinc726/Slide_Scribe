import streamlit as st

def transcriber_tab():
    st.markdown(f'[Google Colab](https://colab.research.google.com/drive/14FvsarkxDMjGCudHym-ttJy0qzwKu41o?usp=sharing)')
    st.text_area("Code", value="!git clone https://github.com/yujinc726/Whisper-AI-with-Gradio.git\n%cd Whisper-AI-with-Gradio\n!pip install -r requirements.txt\n%run main.py", height=200, label_visibility="collapsed")