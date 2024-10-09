# 03_video_list.py

import streamlit as st
from modules import database
from datetime import datetime, timedelta
import logging
import time
import re
import streamlit_tags as st_tags

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

st.set_page_config(page_title="동영상 목록 - 유튜브 질문하기", page_icon="📋", layout="wide")

def delete_tag(video_id, tag):
    try:
        return database.remove_tag_from_video(video_id, tag)
    except Exception as e:
        logger.error(f"태그 삭제 중 오류 발생: {str(e)}")
        return False

def add_tag_to_video(video_id, new_tag):
    success, message = database.add_tag_to_video(video_id, new_tag)
    return success, message

def parse_title(title):
    # Remove emojis and replace consecutive spaces with a single space
    title = re.sub(r'\s+', ' ', title).strip()

    # Select first 25 characters and add "🎥"
    return f"🎥 {title[:25].strip()}{'...' if len(title) > 25 else ''}"

def main():
    st.title("📋 처리된 동영상 목록")

    if 'user' not in st.session_state or not st.session_state.user:
        st.warning("동영상 목록을 보려면 로그인이 필요합니다.")
        st.page_link("main.py", label="로그인 페이지로 이동", icon="🏠")
        return

    # Filter options
    st.subheader("필터 옵션")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        all_tags = database.get_all_tags()
        logger.info(f"모든 태그: {all_tags}")
        selected_tags = st.multiselect("태그 선택", all_tags)
    with col2:
        today = datetime.now().date()
        date_range = st.date_input("날짜 범위 선택", [today - timedelta(days=30), today])
    with col3:
        all_channels = database.get_all_channels(st.session_state.user['_id'])
        selected_channels = st.multiselect("채널 선택", all_channels)
    with col4:
        show_no_tags = st.checkbox("태그 없는 동영상만 표시")

    # Sort option
    sort_options = ["처리 시간 (최신순)", "처리 시간 (오래된순)", "동영상 길이 (긴 순)", "동영상 길이 (짧은 순)"]
    selected_sort = st.selectbox("정렬 기준", sort_options)

    # Apply filters and sorting
    start_date = None
    end_date = None
    if date_range:
        if isinstance(date_range, (list, tuple)):
            if len(date_range) == 2:
                start_date, end_date = date_range
            elif len(date_range) == 1:
                start_date = end_date = date_range[0]
        else:
            start_date = end_date = date_range

        start_date = datetime.combine(start_date, datetime.min.time())
        end_date = datetime.combine(end_date, datetime.max.time())

    # Get filtered videos
    videos = database.get_user_videos(
        st.session_state.user['_id'],
        selected_tags=selected_tags,
        start_date=start_date,
        end_date=end_date,
        selected_channels=selected_channels,
        show_no_tags=show_no_tags
    )

    # Apply sorting
    if selected_sort == "처리 시간 (최신순)":
        videos.sort(key=lambda x: x.get('processed_at'), reverse=True)
    elif selected_sort == "처리 시간 (오래된순)":
        videos.sort(key=lambda x: x.get('processed_at'))
    elif selected_sort == "동영상 길이 (긴 순)":
        videos.sort(key=lambda x: x.get('duration'), reverse=True)
    elif selected_sort == "동영상 길이 (짧은 순)":
        videos.sort(key=lambda x: x.get('duration'))

    if not videos:
        st.info("조건에 맞는 처리된 동영상이 없습니다.")
        st.page_link("pages/01_process_video.py", label="새 동영상 처리하기", icon="🎥")
    else:
        for video in videos:
            parsed_title = parse_title(video['title'])
            # Expander 추가 및 폰트 사이즈 복구
            with st.expander(f"{parsed_title}"):
                st.markdown(f"<p style='font-size:12px;'>채널: {video['channel']}</p>", unsafe_allow_html=True)

                if 'processed_at' in video:
                    processed_time = video['processed_at']
                    if isinstance(processed_time, datetime):
                        processed_time_str = processed_time.strftime("%Y-%m-%d %H:%M:%S")
                    else:
                        processed_time_str = str(processed_time)
                    st.markdown(f"<p style='font-size:12px;'>처리 시간: {processed_time_str}</p>",
                                unsafe_allow_html=True)
                else:
                    st.info("처리 시간 정보가 없습니다.")

                if 'duration' in video:
                    st.markdown(f"<p style='font-size:12px;'>동영상 길이: {video['duration']} 초</p>",
                                unsafe_allow_html=True)
                else:
                    st.info("동영상 길이 정보가 없습니다.")

                # Tags section
                tags = video.get('tags', [])
                st.markdown("###### 태그")  # "Tags" 섹션 제목 추가

                # streamlit-tags 컴포넌트를 사용하여 태그 입력 및 표시
                selected_tags = st_tags.st_tags(
                    label="",  # 라벨 숨기기
                    text="태그 입력",
                    value=tags,
                    suggestions=all_tags,  # 자동 완성 기능 추가
                    key=f"tags_{video['_id']}"
                )

                # 새로운 태그 추가 로직 (st_tags에서 입력된 값 처리)
                if st.session_state.get(f"tags_{video['_id']}") != selected_tags:
                    new_tags = st.session_state.get(f"tags_{video['_id']}")
                    # new_tags가 None인지 확인
                    if new_tags is not None:
                        for new_tag in new_tags:
                            if new_tag not in tags:
                                success, message = add_tag_to_video(video['_id'], new_tag)
                                if success:
                                    st.success("태그가 추가되었습니다.")
                                else:
                                    st.warning(message)
                        st.session_state[f"tags_{video['_id']}"] = selected_tags
                        time.sleep(1)
                        st.experimental_rerun()

                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"질문하기 🙋‍♀️", key=f"ask_{video['_id']}"):
                        st.session_state.last_processed_video_id = video['_id']
                        st.switch_page("pages/02_ask_question.py")
                with col2:
                    if st.button(f"전체 자막 보기 📜", key=f"transcript_{video['_id']}"):
                        if 'transcript' in video:
                            st.text_area("전체 자막", value=video['transcript'], height=300)
                        else:
                            st.info("자막 정보가 없습니다")

if __name__ == "__main__":
    main()