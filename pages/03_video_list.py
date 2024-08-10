import streamlit as st
from modules import database
from datetime import datetime, timedelta
import logging
import time
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

st.set_page_config(page_title="영상 목록 - AskOnTube", page_icon="📋", layout="wide")


def delete_tag(video_id, tag):
    try:
        database.remove_tag_from_video(video_id, tag)
        return True
    except Exception as e:
        logger.error(f"태그 삭제 중 오류 발생: {str(e)}")
        return False


def parse_title(title):
    # 이모지 제거 및 연속된 공백을 하나의 공백으로 대체
    title = re.sub(r'\s+', ' ', title).strip()

    # 첫 30글자만 선택하고 "🎥" 추가
    return f"🎥 {title[:25].strip()}{'...' if len(title) > 10 else ''}"


def main():
    st.title("📋 처리된 영상 목록")

    if 'user' not in st.session_state or not st.session_state.user:
        st.warning("영상 목록을 보려면 로그인이 필요합니다.")
        st.page_link("main.py", label="로그인 페이지로 이동", icon="🏠")
        return

    # 필터 옵션
    st.subheader("필터 옵션")
    col1, col2, col3 = st.columns(3)
    with col1:
        all_tags = database.get_all_tags()
        logger.info(f"All tags: {all_tags}")
        selected_tags = st.multiselect("태그 선택", all_tags)
    with col2:
        today = datetime.now().date()
        date_range = st.date_input("기간 선택", [today - timedelta(days=30), today])
    with col3:
        show_no_tags = st.checkbox("태그 없는 영상만 표시")

    # 필터 적용
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

    logger.info(f"Date range: {start_date} to {end_date}")

    # 필터링된 영상 가져오기
    videos = database.get_user_videos(
        st.session_state.user['_id'],
        selected_tags=selected_tags,
        start_date=start_date,
        end_date=end_date,
        show_no_tags=show_no_tags
    )

    if not videos:
        st.info("조건에 맞는 처리된 영상이 없습니다.")
        st.page_link("pages/01_process_video.py", label="새 영상 처리하기", icon="🎥")
    else:
        for video in videos:
            parsed_title = parse_title(video['title'])
            with st.expander(f"{parsed_title}"):
                st.write(f"채널: {video['channel']}")

                if 'processed_at' in video:
                    processed_time = video['processed_at']
                    if isinstance(processed_time, datetime):
                        processed_time_str = processed_time.strftime("%Y-%m-%d %H:%M:%S")
                    else:
                        processed_time_str = str(processed_time)
                    st.write(f"처리 시간: {processed_time_str}")
                else:
                    st.write("처리 시간 정보 없음")

                if 'duration' in video:
                    st.write(f"영상 길이: {video['duration']} 초")
                else:
                    st.write("영상 길이 정보 없음")

                # 태그 영역
                tags = video.get('tags', [])
                if tags:
                    st.markdown("##### 태그")
                    for tag in tags:
                        col1, col2 = st.columns([4, 1])
                        with col1:
                            st.write(tag)
                        with col2:
                            if st.button("삭제", key=f"delete_{video['_id']}_{tag}"):
                                if delete_tag(video['_id'], tag):
                                    st.success(f"태그 '{tag}'가 삭제되었습니다.")
                                    time.sleep(1)
                                    st.experimental_rerun()
                                else:
                                    st.error("태그 삭제 중 오류가 발생했습니다.")
                else:
                    st.write("태그가 없습니다.")

                # 새 태그 추가 영역
                col1, col2 = st.columns([3, 1])
                with col1:
                    input_key = f"new_tag_{video['_id']}_{st.session_state.get('tag_input_key', 0)}"
                    new_tag = st.text_input("새 태그 추가", key=input_key, placeholder="새 태그 입력")
                with col2:
                    if st.button("태그 추가", key=f"add_tag_{video['_id']}"):
                        if new_tag:
                            if database.add_tag_to_video(video['_id'], new_tag):
                                st.success("태그가 추가되었습니다.")
                                st.session_state['tag_input_key'] = st.session_state.get('tag_input_key', 0) + 1
                                time.sleep(1)
                                st.experimental_rerun()
                            else:
                                st.warning("태그를 추가할 수 없습니다. (최대 3개)")
                        else:
                            st.warning("태그를 입력해주세요.")

                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"질문하기", key=f"ask_{video['_id']}"):
                        st.session_state.last_processed_video_id = video['_id']
                        st.switch_page("pages/02_ask_question.py")
                with col2:
                    if st.button(f"전체 스크립트 보기", key=f"transcript_{video['_id']}"):
                        if 'transcript' in video:
                            st.text_area("전체 스크립트", value=video['transcript'], height=300)
                        else:
                            st.write("스크립트 정보 없음")
if __name__ == "__main__":
    main()