from googleapiclient.discovery import build
import pandas as pd

API_KEY = "AIzaSyBSMeP-GqGwlE56gmqT1D6iPrShYNYzXQs"

TOPICS = [
    # Machine Learning & AI
    "machine learning tutorial",
    "deep learning explained",
    "neural networks lecture",
    "natural language processing tutorial",
    "computer vision explained",

    # Data Science
    "data science course",
    "data analysis tutorial",
    "statistics lecture beginner",
    "pandas python tutorial",
    "data visualization explained",

    # Programming
    "python programming lecture",
    "javascript tutorial beginners",
    "algorithms and data structures",
    "object oriented programming explained",
    "web development tutorial",

    # Computer Science
    "operating systems lecture",
    "computer networks explained",
    "database management tutorial",
    "cybersecurity basics",
    "cloud computing explained",

    # Mathematics
    "mathematics lecture beginner",
    "calculus explained",
    "linear algebra tutorial",
    "probability and statistics",
    "discrete mathematics lecture",

    # Science
    "physics explained beginner",
    "chemistry tutorial",
    "biology lecture",
    "astronomy explained",
    "environmental science tutorial",

    # Engineering
    "electrical engineering basics",
    "mechanical engineering explained",
    "civil engineering tutorial",
    "chemical engineering lecture",

    # Humanities & Social Science
    "world history documentary lecture",
    "economics explained beginner",
    "psychology lecture",
    "philosophy basics explained",
    "sociology tutorial",

    # Skills & Productivity
    "public speaking tips",
    "speed reading techniques",
    "memory improvement techniques",
    "time management study tips",
    "critical thinking explained"
]


def fetch_videos(query, total=200):
    youtube = build("youtube", "v3", developerKey=API_KEY)
    videos = []
    next_page_token = None

    while len(videos) < total:
        request = youtube.search().list(
            q=query,
            part="snippet",
            type="video",
            videoCategoryId="27",  # Education category
            maxResults=50,
            pageToken=next_page_token,
            relevanceLanguage="en"
        )
        response = request.execute()

        for item in response.get("items", []):
            videos.append({
                "title":       item["snippet"]["title"],
                "description": item["snippet"]["description"],
                "channel":     item["snippet"]["channelTitle"],
                "video_id":    item["id"]["videoId"],
                "url":         f"https://youtube.com/watch?v={item['id']['videoId']}",
                "thumbnail":   item["snippet"]["thumbnails"]["medium"]["url"],
                "topic":       query
            })

        next_page_token = response.get("nextPageToken")
        if not next_page_token:
            break

    return videos[:total]


if __name__ == "__main__":
    all_videos = []

    for topic in TOPICS:
        print(f"📥 Fetching: {topic}...")
        try:
            videos = fetch_videos(topic, total=200)
            all_videos.extend(videos)
            print(f"   ✅ Got {len(videos)} videos")
        except Exception as e:
            print(f"   ❌ Error fetching '{topic}': {e}")

    df = pd.DataFrame(all_videos)
    df.drop_duplicates(subset="video_id", inplace=True)
    df.to_csv("data/videos.csv", index=False)

    print(f"\n🎉 Done! Saved {len(df)} unique videos to data/videos.csv")