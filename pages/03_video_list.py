import streamlit as st
from modules import database
from datetime import datetime, timedelta
import logging
import time
import re
import streamlit_tags as st_tags

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

st.set_page_config(page_title="Video List - AskOnTube", page_icon="📋", layout="wide")


def delete_tag(video_id, tag):
    try:
        database.remove_tag_from_video(video_id, tag)
        return True
    except Exception as e:
        logger.error(f"Error occurred while deleting tag: {str(e)}")
        return False


def add_tag_to_video(video_id, new_tag):
    video = videos_collection.find_one({"_id": ObjectId(video_id)})
    if not video:
        return False

    current_tags = video.get('tags', [])
    if len(current_tags) >= 3:
        return False

    if new_tag not in current_tags:
        videos_collection.update_one(
            {"_id": ObjectId(video_id)},
            {"$push": {"tags": new_tag}}
        )
        return True
    return False


def parse_title(title):
    # Remove emojis and replace consecutive spaces with a single space
    title = re.sub(r'\s+', ' ', title).strip()

    # Select first 25 characters and add "🎥"
    return f"🎥 {title[:25].strip()}{'...' if len(title) > 25 else ''}"


def main():
    st.title("📋 Processed Video List")

    if 'user' not in st.session_state or not st.session_state.user:
        st.warning("You need to log in to view the video list.")
        st.page_link("main.py", label="Go to Login Page", icon="🏠")
        return

    # Filter options
    st.subheader("Filter Options")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        all_tags = database.get_all_tags()
        logger.info(f"All tags: {all_tags}")
        selected_tags = st.multiselect("Select tags", all_tags)
    with col2:
        today = datetime.now().date()
        date_range = st.date_input("Select date range", [today - timedelta(days=30), today])
    with col3:
        all_channels = database.get_all_channels(st.session_state.user['_id'])
        selected_channels = st.multiselect("Select channels", all_channels)
    with col4:
        show_no_tags = st.checkbox("Show only videos without tags")

    # Sort option
    sort_options = ["Processed Time (Newest First)", "Processed Time (Oldest First)", "Video Duration (Longest First)", "Video Duration (Shortest First)"]
    selected_sort = st.selectbox("Sort by", sort_options)

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
    if selected_sort == "Processed Time (Newest First)":
        videos.sort(key=lambda x: x.get('processed_at'), reverse=True)
    elif selected_sort == "Processed Time (Oldest First)":
        videos.sort(key=lambda x: x.get('processed_at'))
    elif selected_sort == "Video Duration (Longest First)":
        videos.sort(key=lambda x: x.get('duration'), reverse=True)
    elif selected_sort == "Video Duration (Shortest First)":
        videos.sort(key=lambda x: x.get('duration'))

    if not videos:
        st.info("No processed videos match the criteria.")
        st.page_link("pages/01_process_video.py", label="Process a New Video", icon="🎥")
    else:
        for video in videos:
            parsed_title = parse_title(video['title'])
            # Expander 추가 및 폰트 사이즈 복구
            with st.expander(f"{parsed_title}"):
                st.markdown(f"<p style='font-size:12px;'>Channel: {video['channel']}</p>", unsafe_allow_html=True)

                if 'processed_at' in video:
                    processed_time = video['processed_at']
                    if isinstance(processed_time, datetime):
                        processed_time_str = processed_time.strftime("%Y-%m-%d %H:%M:%S")
                    else:
                        processed_time_str = str(processed_time)
                    st.markdown(f"<p style='font-size:12px;'>Processed at: {processed_time_str}</p>",
                                unsafe_allow_html=True)
                else:
                    st.info("Processing time information not available.")

                if 'duration' in video:
                    st.markdown(f"<p style='font-size:12px;'>Video duration: {video['duration']} seconds</p>",
                                unsafe_allow_html=True)
                else:
                    st.info("Video duration information not available.")

                # Tags section
                tags = video.get('tags', [])
                st.markdown("###### Tags")  # "Tags" 섹션 제목 추가

                # streamlit-tags 컴포넌트를 사용하여 태그 입력 및 표시
                selected_tags = st_tags.st_tags(
                    label="",  # 라벨 숨기기
                    text="Enter tags",
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
                                if add_tag_to_video(video['_id'], new_tag):
                                    st.success("Tag added.")
                                else:
                                    current_tags = video.get('tags', [])
                                    if len(current_tags) >= 3:
                                        st.warning("Cannot add more tags. (Maximum 3)")
                                    else:
                                        st.warning("Tag already exists or cannot be added.")
                        st.session_state[f"tags_{video['_id']}"] = selected_tags
                        time.sleep(1)
                        st.rerun()

                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"Ask Questions 🙋‍♀️", key=f"ask_{video['_id']}"):
                        st.session_state.last_processed_video_id = video['_id']
                        st.switch_page("pages/02_ask_question.py")
                with st.container():
                    if st.button(f"View Full Transcript 📜", key=f"transcript_{video['_id']}"):
                        if 'transcript' in video:
                            st.text_area("Full Transcript", value=video['transcript'], height=300)
                        else:
                            st.info("Transcript information not available")


if __name__ == "__main__":
    main()
