import pandas as pd
import re
from datetime import datetime
import streamlit as st
import os
from functools import lru_cache

# unified helpers
from utils import (
    load_lecture_names,
    list_json_files_for_lecture,
    load_records_from_json,
    get_user_base_dir,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_TIME_RE = re.compile(r"(?P<h>\d{2}):(?P<m>\d{2}):(?P<s>\d{2})[.,](?P<ms>\d{3})")

@lru_cache(maxsize=4096)
def parse_srt_time(time_str: str) -> float:
    """Convert `HH:MM:SS,mmm` or `HH:MM:SS.mmm` to seconds (float).

    Uses regex+cache instead of `datetime.strptime` for ~10× speed-up.
    """
    m = _TIME_RE.match(time_str)
    if not m:
        raise ValueError(f"Invalid time format: {time_str}. Expected HH:MM:SS,mmm")
    h = int(m.group("h")); mnt = int(m.group("m")); s = int(m.group("s")); ms = int(m.group("ms"))
    return h * 3600 + mnt * 60 + s + ms / 1000.0

def read_srt_file(srt_content):
    """SRT 파일 내용을 읽고 자막 데이터를 파싱"""
    subtitles = []
    blocks = srt_content.strip().split('\n\n')
    
    for block in blocks:
        lines = block.strip().split('\n')
        if len(lines) < 3:
            continue
        index = lines[0]
        time_range = lines[1]
        text = ' '.join(lines[2:]).replace('\n', ' ')
        
        try:
            start_time, end_time = re.match(r"(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})", time_range).groups()
            subtitles.append({
                'index': index,
                'start_time': parse_srt_time(start_time),
                'end_time': parse_srt_time(end_time),
                'text': text
            })
        except (re.error, ValueError):
            continue
    
    return subtitles

def get_available_lectures():
    """lectures 디렉토리에서 사용 가능한 강의 목록 가져오기"""
    timer_logs_dir = get_user_base_dir()
    lectures = []
    
    if os.path.exists(timer_logs_dir):
        for lecture_name in os.listdir(timer_logs_dir):
            lecture_path = os.path.join(timer_logs_dir, lecture_name)
            if os.path.isdir(lecture_path):
                lectures.append(lecture_name)
    
    return lectures

def get_json_files_for_lecture(lecture_name):
    """특정 강의 디렉토리에서 사용 가능한 JSON 파일 목록 가져오기"""
    if not lecture_name:
        return []
    timer_logs_dir = os.path.join(get_user_base_dir(), lecture_name)
    json_files = []
    
    if os.path.exists(timer_logs_dir):
        for file_name in os.listdir(timer_logs_dir):
            if file_name.endswith('.json'):
                json_files.append(file_name)
    
    return json_files

def process_files(srt_file=None, json_ref=None):
    """JSON 타이머 기록과 SRT 자막을 합쳐 슬라이드별 텍스트를 반환."""

    # 타이머 기록 읽기 (로컬 또는 GitHub)
    if json_ref:
        records = load_records_from_json(json_ref)
        if not records:
            st.error("선택한 JSON 기록을 불러올 수 없습니다.")
            return None
        df = pd.DataFrame(records)
    else:
        st.error("타이머 기록(JSON) 필요")
        return None
    
    # SRT 파일 읽기 (Streamlit UploadedFile 처리)
    srt_content = srt_file.read().decode('utf-8')
    subtitles = read_srt_file(srt_content)
    
    # 출력 데이터 준비
    output_data = []
    
    # --- 슬라이드 ↔︎ 자막 매핑 (O(S+N)) -----------------------------------
    sub_idx = 0
    n_subs = len(subtitles)

    # ensure subtitles are sorted by start_time (SRT 보장되지만 안전 차원)
    subtitles.sort(key=lambda x: x['start_time'])

    for _, row in df.iterrows():
        slide_title = row.get('slide_title', row.get('Slide Title'))
        slide_num = row.get('slide_number', row.get('Slide Number'))
        start_time = parse_srt_time(row.get('start_time', row.get('Start Time')))
        end_time = parse_srt_time(row.get('end_time', row.get('End Time')))

        # sub_idx 전진 (현재 슬라이드 시작 이전 자막 스킵)
        while sub_idx < n_subs and subtitles[sub_idx]['end_time'] < start_time:
            sub_idx += 1

        # 현재 슬라이드 범위 내 자막 수집
        j = sub_idx
        texts = []
        while j < n_subs and subtitles[j]['start_time'] <= end_time:
            if subtitles[j]['end_time'] <= end_time:
                texts.append(subtitles[j]['text'])
            j += 1

        # 다음 슬라이드에서도 계속 이어서 검색할 수 있도록 sub_idx 유지
        # (sub_idx 는 start_time 이전은 모두 지나갔으므로 그대로)

        if texts:
            output_data.append({
                'Slide Title': slide_title,
                'Slide Number': slide_num,
                'Text': ' '.join(texts)
            })
    
    # 데이터프레임 반환
    if output_data:
        return pd.DataFrame(output_data)
    else:
        return None

def srt_parser_tab():
    """SRT Parser 탭 구현"""
    # 초기화
    if 'result_df' not in st.session_state:
        st.session_state.result_df = None
    
    # 레이아웃 설정
    col1, col2 = st.columns([1, 2])  # 좌측: 파일 업로드, 우측: 결과
    
    with col1:
        # st.subheader("File Upload")
        # SRT 파일 업로드
        srt_file = st.file_uploader("SRT 파일 업로드", type=["srt"], key="srt_uploader")
        
        # 강의 선택 및 JSON 파일 선택
        available_lectures = load_lecture_names()

        if not available_lectures:
            st.info("등록된 강의가 없습니다.")
            selected_lecture = None
            json_ref = None
        else:
            selected_lecture = st.selectbox(
                "강의 선택",
                available_lectures,
                key="lecture_selector",
                index=None,
                placeholder="강의를 선택해주세요",
            )

            # JSON 파일 (타이머 기록) 목록 불러오기
            if selected_lecture:
                json_names = list_json_files_for_lecture(selected_lecture, names_only=True)
                json_refs = list_json_files_for_lecture(selected_lecture, names_only=False)
                if not json_names:
                    st.info("타이머 기록이 없습니다.")
                    json_ref = None
                else:
                    selected_name = st.selectbox(
                        "기록 선택",
                        json_names,
                        key="json_file_selector",
                        index=None,
                        placeholder="기록을 선택해주세요",
                        disabled=not selected_lecture,
                    )
                    if selected_name:
                        idx = json_names.index(selected_name)
                        json_ref = json_refs[idx]
                    else:
                        json_ref = None
            else:
                json_ref = None
        
        # 처리 버튼
        if st.button("Parse SRT", type='primary', use_container_width=True, disabled=not (srt_file and json_ref)):
            if srt_file is None:
                st.error("SRT 파일을 업로드 해주세요.")
            elif json_ref is None:
                st.error("JSON 파일을 선택해주세요.")
            else:
                with st.spinner("Processing..."):
                    st.session_state.result_df = process_files(srt_file, json_ref)
    
    with col2:
        st.subheader("Parsed SRT")
        if st.session_state.result_df is not None:
            if not st.session_state.result_df.empty:
                # 편집 가능한 텍스트로 변환
                edited_texts = []
                for i, row in st.session_state.result_df.iterrows():
                    st.markdown(f'##### Slide {row["Slide Number"]}{' - ' + row["Slide Title"] if row["Slide Title"] else ""}')
                    if row["Notes"]:
                        st.markdown(f'**Notes:** {row["Notes"]}')
                    # 텍스트 에어리어를 사용하여 편집 가능하게 만들기
                    text_key = f"text_{i}_{row['Slide Number']}"
                    edited_text = st.text_area(
                        "", 
                        value=row['Text'],
                        key=text_key,
                        height=200,
                        label_visibility="collapsed"
                    )
                    # 편집된 텍스트 저장
                    edited_texts.append({
                        'Slide Number': row['Slide Number'],
                        'Text': edited_text
                    })
                
            else:
                st.warning("추출된 내용이 없습니다.")
        else:
            st.info("SRT 파일을 업로드하고, JSON 파일을 선택해주세요.")