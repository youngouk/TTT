import os
import requests
from urllib.parse import urlencode
from modules.database import users_collection
from bson.objectid import ObjectId
from config import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REDIRECT_URI

def get_google_auth_url():
    base_url = "https://accounts.google.com/o/oauth2/v2/auth"
    params = {
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "consent"
    }
    url = f"{base_url}?{urlencode(params)}"
    return url

def get_google_user_info(code):
    token_url = "https://oauth2.googleapis.com/token"
    data = {
        "code": code,
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "grant_type": "authorization_code"
    }
    response = requests.post(token_url, data=data)
    response.raise_for_status()
    tokens = response.json()
    id_token = tokens.get("id_token")
    access_token = tokens.get("access_token")

    user_info_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    headers = {"Authorization": f"Bearer {access_token}"}
    user_info_response = requests.get(user_info_url, headers=headers)
    user_info_response.raise_for_status()
    user_info = user_info_response.json()
    return user_info  # 예: {'id': '...', 'email': '...', 'name': '...', 'picture': '...'}

def authenticate_google_user(code):
    try:
        user_info = get_google_user_info(code)
        email = user_info.get("email")
        name = user_info.get("name")
        picture = user_info.get("picture")

        # 기존 사용자 확인
        user = users_collection.find_one({"email": email})
        if not user:
            # 새 사용자 생성
            user_data = {
                "email": email,
                "name": name,
                "picture": picture,
                "created_at": datetime.utcnow(),
                "oauth_provider": "google"
            }
            result = users_collection.insert_one(user_data)
            user = users_collection.find_one({"_id": result.inserted_id})

        return user
    except Exception as e:
        print(f"Google OAuth 인증 중 오류 발생: {e}")
        return None