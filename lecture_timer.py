import streamlit as st
from datetime import datetime, timedelta
import json
import os
import pandas as pd
import streamlit.components.v1 as components

def load_lecture_names():
    """lecture_names.json에서 강의 이름목록 로드"""
    lecture_names_file = "lecture_names.json"
    try:
        if os.path.exists(lecture_names_file):
            with open(lecture_names_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    except Exception as e:
        st.error(f"강의 이름 로드 중 오류: {e}")
        return []

def save_lecture_names(lecture_names):
    """lecture_names.json에 강의 이름 목록 저장"""
    lecture_names_file = "lecture_names.json"
    try:
        with open(lecture_names_file, 'w', encoding='utf-8') as f:
            json.dump(lecture_names, f, ensure_ascii=False, indent=2)
    except Exception as e:
        st.error(f"강의 이름 저장 중 오류: {e}")

def ensure_directory(directory):
    """디렉토리가 존재하는지 확인하고 없으면 생성"""
    if not os.path.exists(directory):
        os.makedirs(directory)

def save_records_to_json(lecture_name, date, records):
    """타이머 기록을 JSON 파일로 저장"""
    try:
        lecture_name = lecture_name.replace("/", "_").replace("\\", "_")
        date = date.replace("/", "_").replace("\\", "_")
        directory = f"lectures/{lecture_name}"
        ensure_directory(directory)
        file_path = f"{directory}/{date}.json"
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(records, f, ensure_ascii=False, indent=2)
        return file_path
    except Exception as e:
        st.error(f"JSON 파일 저장 중 오류: {e}")
        return None

def lecture_timer_tab():
    """Slide Timer 탭 구현"""
    try:
        st.header("Slide Timer")

        # 세션 상태 초기화
        if 'lecture_names' not in st.session_state:
            st.session_state.lecture_names = load_lecture_names()
        if 'timer_running' not in st.session_state:
            st.session_state.timer_running = False
        if 'start_time' not in st.session_state:
            st.session_state.start_time = None
        if 'timer_start' not in st.session_state:
            st.session_state.timer_start = None
        if 'elapsed_time' not in st.session_state:
            st.session_state.elapsed_time = 0
        if 'last_slide_start_time' not in st.session_state:
            st.session_state.last_slide_start_time = None
        if 'records' not in st.session_state:
            st.session_state.records = []
        if 'slide_number' not in st.session_state:
            st.session_state.slide_number = 1

        # 두 개의 주요 컬럼으로 레이아웃 구성
        left_col, right_col = st.columns([1, 2])

        with left_col:
            # Lecture Information 섹션
            st.subheader("Lecture Information")
            lecture_name = st.selectbox(
                "강의:",
                st.session_state.lecture_names if st.session_state.lecture_names else ["강의를 추가해주세요"],
                key="lecture_name"
            )
            
            if not st.session_state.lecture_names:
                st.info("Settings 탭에서 강의를 추가해주세요.")
            
            dates = [(datetime.now() + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)]
            date = st.selectbox("날짜:", dates, key="date")

            # Stopwatch 섹션
            st.subheader("Slide Timer")
            start_time_input = st.text_input("Start Time", value="00:00", key="start_time_input")
            
            col1, col2, col3 = st.columns([1, 1, 1])
            with col1:
                start_button_label = "Resume" if st.session_state.elapsed_time > 0 and not st.session_state.timer_running else "Start"
                if st.button(start_button_label, disabled=st.session_state.timer_running, use_container_width=True):
                    if st.session_state.elapsed_time == 0 or st.session_state.start_time is None:
                        # 처음 시작하는 경우
                        try:
                            start_time_str = start_time_input
                            start_time = datetime.strptime(start_time_str, "%M:%S")
                            st.session_state.start_time = datetime.combine(datetime.now().date(), start_time.time())
                            if st.session_state.start_time > datetime.now():
                                st.session_state.start_time -= timedelta(days=1)
                        except ValueError:
                            st.session_state.start_time = datetime.combine(datetime.now().date(), datetime.time(0, 0, 0))
                        st.session_state.last_slide_start_time = st.session_state.start_time.strftime("%H:%M:%S") + ".000"
                    # 일시정지 후 재개하는 경우는 elapsed_time이 유지된 상태에서 timer_start만 갱신
                    st.session_state.timer_running = True
                    st.session_state.timer_start = datetime.now()
                    st.rerun()
            with col2:
                if st.button("Pause", disabled=not st.session_state.timer_running, use_container_width=True):
                    st.session_state.timer_running = False
                    # 현재까지 경과한 시간을 누적
                    st.session_state.elapsed_time = st.session_state.elapsed_time + (datetime.now() - st.session_state.timer_start).total_seconds() * 1000
                    st.rerun()
            with col3:
                if st.button("Reset", use_container_width=True):
                    st.session_state.timer_running = False
                    st.session_state.elapsed_time = 0
                    st.session_state.start_time = None
                    st.session_state.timer_start = None
                    st.session_state.last_slide_start_time = None
                    st.session_state.records = []
                    st.session_state.slide_number = 1
                    st.rerun()

            # 타이머 표시
            if st.session_state.timer_start or st.session_state.elapsed_time > 0:
                elapsed_ms = st.session_state.elapsed_time
                if st.session_state.timer_running:
                    current_elapsed = (datetime.now() - st.session_state.timer_start).total_seconds() * 1000
                    elapsed_ms = st.session_state.elapsed_time + current_elapsed
                elapsed_seconds = elapsed_ms / 1000
                if st.session_state.start_time:
                    absolute_time = st.session_state.start_time + timedelta(seconds=elapsed_seconds)
                    initial_time = absolute_time.strftime("%H:%M:%S") + f".{int(elapsed_ms % 1000):03d}"
                else:
                    # start_time이 없는 경우 (직접 경과 시간 표시)
                    hours = int(elapsed_seconds // 3600)
                    minutes = int((elapsed_seconds % 3600) // 60)
                    seconds = int(elapsed_seconds % 60)
                    milliseconds = int(elapsed_ms % 1000)
                    initial_time = f"{hours:02d}:{minutes:02d}:{seconds:02d}.{milliseconds:03d}"
            else:
                initial_time = "00:00:00.000"

            timer_html = f"""
            <div id="timer-display" style="font-size: 18px; font-weight: bold; padding: 10px; border: 1px solid #ddd; border-radius: 5px; text-align: center;">{initial_time}</div>
            <script>
                let timerRunning = {str(st.session_state.timer_running).lower()};
                let startTime = new Date().getTime();
                let elapsedTime = {st.session_state.elapsed_time};

                function updateTimer() {{
                    if (timerRunning) {{
                        let now = new Date().getTime();
                        let elapsedMs = (now - startTime) + elapsedTime;
                        let elapsedSeconds = Math.floor(elapsedMs / 1000);
                        let hours = Math.floor(elapsedSeconds / 3600);
                        let minutes = Math.floor((elapsedSeconds % 3600) / 60);
                        let seconds = elapsedSeconds % 60;
                        let milliseconds = Math.floor(elapsedMs % 1000);
                        let timeStr = hours.toString().padStart(2, '0') + ':' +
                                      minutes.toString().padStart(2, '0') + ':' +
                                      seconds.toString().padStart(2, '0') + '.' +
                                      milliseconds.toString().padStart(3, '0');
                        document.getElementById('timer-display').innerText = timeStr;
                    }}
                    setTimeout(updateTimer, 10);
                }}

                updateTimer();
            </script>
            """
            components.html(timer_html, height=60)

            # Slide Control 섹션
            st.session_state.slide_number = st.number_input("Slide Number:", min_value=1, value=st.session_state.slide_number, step=1, key="slide_input")
            if st.button("Record Time", key="record_button", help="Press Enter to record", use_container_width=True):
                # 현재 경과 시간 계산
                current_elapsed_ms = st.session_state.elapsed_time
                if st.session_state.timer_running:
                    current_elapsed_ms += (datetime.now() - st.session_state.timer_start).total_seconds() * 1000
                elapsed_seconds = current_elapsed_ms / 1000
                current_time = st.session_state.start_time + timedelta(seconds=elapsed_seconds)
                current_time_str = current_time.strftime("%H:%M:%S") + f".{int(current_elapsed_ms % 1000):03d}"
                start_time = st.session_state.last_slide_start_time if st.session_state.last_slide_start_time else st.session_state.start_time.strftime("%H:%M:%S") + ".000"
                st.session_state.last_slide_start_time = current_time_str
                st.session_state.records.append({
                    "slide_number": str(st.session_state.slide_number),
                    "start_time": start_time,
                    "end_time": current_time_str,
                    "notes": ""
                })
                st.session_state.slide_number += 1
                st.rerun()

            # JSON 저장
            if st.session_state.records:
                if st.button("Save to JSON", use_container_width=True):
                    json_file_path = save_records_to_json(
                        lecture_name,
                        date,
                        st.session_state.records
                    )
                    
                    if json_file_path:
                        with open(json_file_path, 'r', encoding='utf-8') as f:
                            json_data = f.read()
                            
                        st.download_button(
                            label="Download JSON",
                            data=json_data,
                            file_name=os.path.basename(json_file_path),
                            mime="application/json",
                            use_container_width=True
                        )
                        st.success(f"JSON 파일이 저장되었습니다: {json_file_path}")

        with right_col:
            # 기록된 시간 표시
            st.subheader("Records")
            if st.session_state.records:
                df = pd.DataFrame(st.session_state.records)
                edited_df = st.data_editor(
                    df,
                    num_rows="dynamic",
                    use_container_width=True,
                    column_config={
                        "slide_number": st.column_config.TextColumn("Slide Number", help="슬라이드 번호"),
                        "start_time": st.column_config.TextColumn("Start Time", help="시작 시간"),
                        "end_time": st.column_config.TextColumn("End Time", help="종료 시간"),
                        "notes": st.column_config.TextColumn("Notes", help="메모")
                    }
                )
                if edited_df is not None:
                    st.session_state.records = edited_df.to_dict('records')
            else:
                st.info("표시할 기록이 없습니다.")

        # Enter 키로 Record Time 호출
        st.markdown("""
            <script>
            document.addEventListener('keydown', function(event) {
                if (event.key === 'Enter') {
                    const recordButton = document.querySelector('button[kind="primary"][id="record_button"]');
                    if (recordButton && !recordButton.disabled) {
                        recordButton.click();
                    }
                }
            });
            </script>
        """, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"강의 타이머 탭에서 오류: {e}")