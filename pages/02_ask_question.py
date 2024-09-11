import streamlit as st
from modules import database, nlp
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

st.set_page_config(page_title="질문하기 - 유튜브 질문하기", page_icon="❓", layout="wide")


def display_response(question, response):
    st.markdown("### 질문:")
    st.write(question)
    st.divider()
    st.markdown("### 답변:")
    st.write(response)


def show_individual_video_question(user_id):
    st.subheader("개별 동영상 질문")

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
        all_channels = database.get_all_channels(user_id)
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
        user_id,
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

    if videos:
        video_options = {f"{v['title']} - {v['channel']}": v['video_id'] for v in videos}
        selected_video_title = st.selectbox("동영상 선택", list(video_options.keys()),
                                            key="individual_video_selector")
        selected_video_id = video_options[selected_video_title]

        question = st.text_input("질문을 입력하세요", key="individual_question_input")
        if st.button("답변 받기", key="individual_get_answer"):
            if question:
                with st.spinner("답변 생성 중..."):
                    try:
                        video_data = database.get_video_info_from_db([selected_video_id])
                        if video_data and 'transcript' in video_data[0]:
                            response = nlp.generate_response(question, [video_data[0]['transcript']])
                            display_response(question, response)
                        else:
                            st.error("선택한 동영상의 자막을 찾을 수 없습니다.")
                    except Exception as e:
                        st.error(f"답변 생성 중 오류가 발생했습니다: {str(e)}")
            else:
                st.warning("질문을 입력해주세요.")
    else:
        st.info("필터에 맞는 처리된 동영상을 찾을 수 없습니다.")


def show_tag_based_question(user_id):
    st.subheader("태그 기반 질문")
    all_tags = database.get_all_tags()
    selected_tags = st.multiselect("태그 선택", all_tags, key="tag_selector")

    if selected_tags:
        videos = database.get_videos_by_tags(selected_tags)
        if videos:
            st.write(f"선택된 동영상 수: {len(videos)}")

            # Limit video titles to the first 10 characters and add ellipsis
            video_titles = [f"{v['title'][:10]}..." for v in videos]

            # Join the limited titles into a string
            titles_str = ", ".join(video_titles)

            # Truncate the resulting string if it's too long
            max_display_length = 100  # Set maximum display length
            if len(titles_str) > max_display_length:
                titles_str = titles_str[:max_display_length] + "..."

            st.write(f"선택된 동영상: {titles_str}")

            question = st.text_input("질문을 입력하세요", key="tag_question_input")
            if st.button("답변 받기", key="tag_get_answer"):
                if question:
                    with st.spinner("답변 생성 중..."):
                        try:
                            video_data = database.get_video_info_from_db([v['video_id'] for v in videos])
                            if video_data:
                                transcripts = [v['transcript'] for v in video_data if 'transcript' in v]
                                response = nlp.generate_response(question, transcripts)
                                display_response(question, response)
                            else:
                                st.error("선택한 동영상들의 자막을 찾을 수 없습니다.")
                        except Exception as e:
                            st.error(f"답변 생성 중 오류가 발생했습니다: {str(e)}")
                else:
                    st.warning("질문을 입력해주세요.")




def main():
    st.title("💬 동영상에 대해 질문하기")

    if 'user' not in st.session_state or not st.session_state.user:
        st.warning("질문 기능을 사용하려면 로그인이 필요합니다.")
        st.page_link("main.py", label="로그인 페이지로 이동", icon="🏠")
        return

    user_id = st.session_state.user['_id']

    # Use tabs for question mode selection
    tab1, tab2 = st.tabs(["개별 동영상 질문", "태그별 여러 동영상 질문"])

    with tab1:
        show_individual_video_question(user_id)

    with tab2:
        show_tag_based_question(user_id)

if __name__ == "__main__":
    main()
