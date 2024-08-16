import streamlit as st
from modules import database, nlp
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

st.set_page_config(page_title="Ask Questions - AskOnTube", page_icon="❓", layout="wide")


def display_response(question, response):
    st.markdown("### Question:")
    st.write(question)
    st.divider()
    st.markdown("### Answer:")
    st.write(response)


def show_individual_video_question(user_id):
    st.subheader("Single Video Question")

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
        all_channels = database.get_all_channels(user_id)
        selected_channels = st.multiselect("Select channels", all_channels)
    with col4:
        show_no_tags = st.checkbox("Show only videos without tags")

    # Sort option
    sort_options = ["Processed Time (Newest First)", "Processed Time (Oldest First)", "Video Duration (Longest First)",
                    "Video Duration (Shortest First)"]
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
        user_id,
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

    if videos:
        video_options = {f"{v['title']} - {v['channel']}": v['video_id'] for v in videos}
        selected_video_title = st.selectbox("Select a video", list(video_options.keys()),
                                            key="individual_video_selector")
        selected_video_id = video_options[selected_video_title]

        question = st.text_input("Enter your question", key="individual_question_input")
        if st.button("Get Answer", key="individual_get_answer"):
            if question:
                with st.spinner("Generating answer..."):
                    try:
                        video_data = database.get_video_info_from_db([selected_video_id])
                        if video_data and 'transcript' in video_data[0]:
                            response = nlp.generate_response(question, [video_data[0]['transcript']])
                            display_response(question, response)
                        else:
                            st.error("Transcript for the selected video not found.")
                    except Exception as e:
                        st.error(f"An error occurred while generating the answer: {str(e)}")
            else:
                st.warning("Please enter a question.")
    else:
        st.info("No processed videos found matching the filters.")


def show_tag_based_question(user_id):
    st.subheader("Tag-based Question")
    all_tags = database.get_all_tags()
    selected_tags = st.multiselect("Select tags", all_tags, key="tag_selector")

    if selected_tags:
        videos = database.get_videos_by_tags(selected_tags)
        if videos:
            st.write(f"Number of selected videos: {len(videos)}")

            # Limit video titles to the first 10 characters and add ellipsis
            video_titles = [f"{v['title'][:10]}..." for v in videos]

            # Join the limited titles into a string
            titles_str = ", ".join(video_titles)

            # Truncate the resulting string if it's too long
            max_display_length = 100  # Set maximum display length
            if len(titles_str) > max_display_length:
                titles_str = titles_str[:max_display_length] + "..."

            st.write(f"Selected videos: {titles_str}")

            question = st.text_input("Enter your question", key="tag_question_input")
            if st.button("Get Answer", key="tag_get_answer"):
                if question:
                    with st.spinner("Generating answer..."):
                        try:
                            video_data = database.get_video_info_from_db([v['video_id'] for v in videos])
                            if video_data:
                                transcripts = [v['transcript'] for v in video_data if 'transcript' in v]
                                response = nlp.generate_response(question, transcripts)
                                display_response(question, response)
                            else:
                                st.error("Transcripts for the selected videos not found.")
                        except Exception as e:
                            st.error(f"An error occurred while generating the answer: {str(e)}")
                else:
                    st.warning("Please enter a question.")




def main():
    st.title("💬 Ask Questions About Videos")

    if 'user' not in st.session_state or not st.session_state.user:
        st.warning("You need to log in to use the question-asking feature.")
        st.page_link("main.py", label="Go to Login Page", icon="🏠")
        return

    user_id = st.session_state.user['_id']

    # Use tabs for question mode selection
    tab1, tab2 = st.tabs(["Single Video Question", "Multiple Videos by Tags"])

    with tab1:
        show_individual_video_question(user_id)

    with tab2:
        show_tag_based_question(user_id)

if __name__ == "__main__":
    main()
