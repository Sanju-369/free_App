import streamlit as st
import requests
from youtube_transcript_api import YouTubeTranscriptApi
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
api_key = os.getenv("YOUTUBE_API_KEY")

# Function to search YouTube
def search_youtube_topic(topic, max_results):
    url = "https://www.googleapis.com/youtube/v3/search"
    all_videos = []
    next_page_token = None
    results_per_request = 50
    
    while len(all_videos) < max_results:
        params = {
            'part': 'snippet',
            'q': topic,
            'maxResults': min(results_per_request, max_results - len(all_videos)),
            'type': 'video',
            'regionCode': 'IN',  # Fixed region
            'key': api_key,
            'pageToken': next_page_token
        }
        
        response = requests.get(url, params=params)
        data = response.json()
        
        if 'items' in data:
            for item in data['items']:
                video_info = {
                    'title': item['snippet']['title'],
                    'video_id': item['id']['videoId']
                }
                all_videos.append(video_info)
        
        next_page_token = data.get('nextPageToken')
        if not next_page_token:
            break
    
    return all_videos

# Optimized function to get video view counts in batches
def get_video_views(video_ids):
    url = "https://www.googleapis.com/youtube/v3/videos"
    params = {
        'part': 'statistics',
        'id': ','.join(video_ids),  # Batch API call for multiple videos
        'key': api_key
    }
    
    response = requests.get(url, params=params)
    data = response.json()
    
    views_dict = {}
    if 'items' in data:
        for item in data['items']:
            video_id = item['id']
            view_count = int(item['statistics'].get('viewCount', 0))
            # Format view count to display in M or K
            if view_count >= 1_000_000:
                formatted_views = f"{view_count / 1_000_000:.1f}M"
            elif view_count >= 1_000:
                formatted_views = f"{view_count / 1_000:.0f}K"
            else:
                formatted_views = str(view_count)
            views_dict[video_id] = formatted_views
    
    return views_dict

# Streamlit UI layout for Free Version
def display_video_details(videos):
    for idx, video in enumerate(videos, start=1):
        st.markdown(
            f"""
            <div style='padding: 15px; background-color: #1E3A5F; border-radius: 10px; margin-bottom: 10px;'>
                <h3 style='color: #FFA500;'> {idx}. {video['title']} </h3>
                <p style='color: white;'>Views: <b>{video['views']}</b></p>
            </div>
            """,
            unsafe_allow_html=True
        )

# Main Streamlit App
def run_app():
    st.set_page_config(page_title="YouTube Video Researcher", layout="wide")
    
    # Custom Background Color (Light Blue)
    st.markdown(
        """
        <style>
            body {
                background-color: #ADD8E6;
                color: black;
            }
            .stTextInput>div>div>input {
                background-color: #262730;
                color: white;
            }
            .stButton>button {
                background-color: #FFA500;
                color: black;
                font-weight: bold;
            }
        </style>
        """,
        unsafe_allow_html=True
    )
    
    st.title("📊 YouTube Video Researcher")
    st.subheader("Gain Deep Insights into Your Search Topic on YouTube")
    
    st.sidebar.title("🔍 Research Input")
    topic = st.sidebar.text_input("Enter a topic to research")
    max_results = 50  # Fixed results count
    
    if topic:
        st.write(f"### Analyzed 1000 videos, Fetching top 5 videos for: `{topic}`")
        
        trending_videos = search_youtube_topic(topic, max_results)
        video_ids = [video['video_id'] for video in trending_videos]
        
        if video_ids:
            views_dict = get_video_views(video_ids)  # Batch API call for views
            for video in trending_videos:
                video['views'] = views_dict.get(video['video_id'], "0")
        
        # Sort videos by view count
        trending_videos.sort(key=lambda x: float(x['views'].replace('M', '000000').replace('K', '000')), reverse=True)
        
        # Display top 5 videos
        trending_videos = trending_videos[:5]
        
        display_video_details(trending_videos)

if __name__ == "__main__":
    run_app()
