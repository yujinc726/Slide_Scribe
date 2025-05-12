import streamlit as st

def transcriber_tab():
    st.markdown(f'[Google Colaboratory](https://colab.research.google.com/drive/14FvsarkxDMjGCudHym-ttJy0qzwKu41o?usp=sharing)')
    st.text_area(f"[Google Colaboratory](https://colab.research.google.com/drive/14FvsarkxDMjGCudHym-ttJy0qzwKu41o?usp=sharing)", value="!git clone https://github.com/yujinc726/Whisper-AI-with-Gradio.git\n%cd Whisper-AI-with-Gradio\n!pip install -r requirements.txt\n%run main.py", height=100)