from pymongo import MongoClient
from pymongo.server_api import ServerApi
import certifi
from config import MONGODB_URI
from datetime import datetime
from bson.objectid import ObjectId  # Add this import


# MongoDB 연결 설정
client = MongoClient(MONGODB_URI, server_api=ServerApi('1'), tlsCAFile=certifi.where())
db = client['youtube_transcripts']
users_collection = db['users']
videos_collection = db['videos']


def find_user_by_email(email):
    return users_collection.find_one({"email": email})

def create_user(email, name, picture):
    user_data = {
        "email": email,
        "name": name,
        "picture": picture,
        "created_at": datetime.utcnow(),
        "oauth_provider": "google"
    }
    result = users_collection.insert_one(user_data)
    return users_collection.find_one({"_id": result.inserted_id})


def get_video_tags(video_id):
    """비디오에 대한 태그 정보 조회"""
    video = videos_collection.find_one({"video_id": video_id})
    return video.get("tags", []) if video else []


def get_video_info_from_db(video_ids):
    """데이터베이스에서 여러 비디오 정보 조회"""
    return list(videos_collection.find({"video_id": {"$in": video_ids}}))

def get_user_videos(user_id, selected_tags=None, start_date=None, end_date=None, show_no_tags=False, selected_channels=None):
    """사용자의 처리된 비디오 목록 가져오기 (필터링 포함)"""
    query = {"user_ids": user_id}

    if show_no_tags:
        query["$or"] = [{"tags": {"$exists": False}}, {"tags": []}]
    elif selected_tags:
        query["tags"] = {"$in": selected_tags}

    if start_date and end_date:
        query["processed_at"] = {
            "$gte": start_date,
            "$lte": end_date
        }

    if selected_channels:
        query["channel"] = {"$in": selected_channels}

    return list(videos_collection.find(query))


def remove_tag_from_video(video_id, tag):
    """비디오에서 태그 제거"""
    try:
        result = videos_collection.update_one(
            {"video_id": video_id},
            {"$pull": {"tags": tag}}
        )
        if result.modified_count > 0:
            logger.info(f"태그 '{tag}'가 비디오 ID {video_id}에서 성공적으로 제거되었습니다.")
            return True
        else:
            logger.warning(f"태그 '{tag}'를 비디오 ID {video_id}에서 제거하지 못했습니다. 태그가 존재하지 않을 수 있습니다.")
            return False
    except Exception as e:
        logger.error(f"태그 제거 중 오류 발생: {str(e)}")
        return False

def save_feedback(user_id, feedback):
    """피드백을 데이터베이스에 저장합니다."""
    feedback_data = {
        "user_id": user_id,
        "feedback": feedback,
        "timestamp": datetime.utcnow()
    }
    db['feedback'].insert_one(feedback_data)


def add_tag_to_video(video_id, new_tag):
    video = videos_collection.find_one({"_id": ObjectId(video_id)})
    if not video:
        return False, "영상을 찾을 수 없습니다."

    current_tags = video.get('tags', [])
    if len(current_tags) >= 3:
        return False, "태그는 최대 3개까지만 추가할 수 있습니다."

    if new_tag in current_tags:
        return False, "이미 존재하는 태그입니다."

    videos_collection.update_one(
        {"_id": ObjectId(video_id)},
        {"$push": {"tags": new_tag}}
    )
    print(f"Added tag {new_tag} to video ID {video_id}")
    return True, "태그가 성공적으로 추가되었습니다."


def remove_tag_from_video(video_id, tag):
    """비디오에서 태그 제거"""
    videos_collection.update_one(
        {"video_id": video_id},
        {"$pull": {"tags": tag}}
    )


def get_all_tags():
    """모든 고유 태그 가져오기"""
    all_tags = videos_collection.distinct("tags")
    return [tag for tag in all_tags if tag is not None]  # None 값 제거

def get_videos_by_tags(tags):
    """태그 리스트에 해당하는 비디오 정보 가져오기"""
    return list(videos_collection.find({"tags": {"$in": tags}}))

def get_all_channels(user_id):
    """사용자가 업로드한 비디오들의 채널 목록 가져오기"""
    channels = videos_collection.distinct("channel", {"user_ids": user_id})
    return channels

def get_user_videos(user_id, selected_tags=None, start_date=None, end_date=None, show_no_tags=False, selected_channels=None):
    """사용자의 처리된 비디오 목록 가져오기 (필터링 포함)"""
    query = {"user_ids": user_id}

    if show_no_tags:
        query["$or"] = [{"tags": {"$exists": False}}, {"tags": []}]
    elif selected_tags:
        query["tags"] = {"$in": selected_tags}

    if start_date and end_date:
        query["processed_at"] = {
            "$gte": start_date,
            "$lte": end_date
        }

    # selected_channels를 이용한 필터링 추가
    if selected_channels:
        query["channel"] = {"$in": selected_channels}

    return list(videos_collection.find(query))
