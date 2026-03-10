import streamlit as st
import pandas as pd
from recommender import recommend
import os
import hashlib

# ─────────────────────────────────────────
# Page Config
# ─────────────────────────────────────────
st.set_page_config(
    page_title="LectureFinder",
    page_icon="🎓",
    layout="wide"
)

# ─────────────────────────────────────────
# Custom CSS
# ─────────────────────────────────────────
st.markdown("""
    <style>
        .main { background-color: #0f0f0f; }
        .stTextInput > div > div > input {
            background-color: #1e1e1e;
            color: white;
            border: 1px solid #444;
            border-radius: 8px;
            padding: 10px;
            font-size: 16px;
        }
        .card {
            background-color: #1a1a1a;
            border-radius: 12px;
            padding: 16px;
            margin-bottom: 16px;
            border: 1px solid #2a2a2a;
        }
        .channel-tag {
            background-color: #2a2a2a;
            color: #aaa;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 13px;
        }
        .score-label {
            color: #888;
            font-size: 12px;
        }
    </style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────
# Header
# ─────────────────────────────────────────
st.markdown("## 🎓 LectureFinder")
st.caption("Find the best YouTube lectures for any topic you're studying — instantly.")
st.divider()

# ─────────────────────────────────────────
# Load Data
# ─────────────────────────────────────────
DATA_PATH = "data/videos.csv"

if not os.path.exists(DATA_PATH):
    st.error("⚠️ Dataset not found! Please run `fetch_data.py` first.")
    st.code("python fetch_data.py", language="bash")
    st.stop()

@st.cache_data
def load_data():
    return pd.read_csv(DATA_PATH)

df = load_data()

# ─────────────────────────────────────────
# Sidebar
# ─────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    top_n = st.slider("Number of results", 3, 12, 6)
    st.divider()
    st.success(f"✅ {len(df):,} videos loaded")
    st.caption("Topics: ML, Python, Math, Physics, Chemistry, Biology, History, Economics & more")
    st.divider()
    st.markdown("### 💡 Try searching for:")
    examples = [
        "gradient descent",
        "photosynthesis",
        "world war 2",
        "recursion in python",
        "black holes",
        "supply and demand",
        "human psychology",
        "calculus derivatives"
    ]
    for ex in examples:
        st.caption(f"• {ex}")

# ─────────────────────────────────────────
# Search Bar
# ─────────────────────────────────────────
query = st.text_input(
    "🔍 What are you studying today?",
    placeholder="e.g. neural networks, photosynthesis, world war 2, recursion in python..."
)

# ─────────────────────────────────────────
# Results
# ─────────────────────────────────────────
if query:
    with st.spinner("🔎 Finding best lectures..."):
        results = recommend(query, df, top_n=top_n)

    if results.empty:
        st.warning("😕 No relevant videos found. Try a different or broader search term.")
    else:
        st.subheader(f"📺 Top {len(results)} results for: *{query}*")
        st.divider()

        for _, row in results.iterrows():
            col1, col2 = st.columns([1, 3])

            with col1:
                st.image(row["thumbnail"], width=280)

            with col2:
                st.markdown(f"### [{row['title']}]({row['url']})")
                st.markdown(f"<span class='channel-tag'>📺 {row['channel']}</span>", unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)

                # Relevance score bar
                score = float(row["score"])
                st.progress(min(score * 5, 1.0))
                st.markdown(f"<span class='score-label'>Relevance Score: {score:.3f}</span>", unsafe_allow_html=True)

                # Smart description: use real one if good, else generate a unique one
                raw_desc = str(row["description"]) if pd.notna(row["description"]) else ""
                title     = str(row["title"])
                channel   = str(row["channel"])
                topic     = str(row.get("topic", ""))

                if len(raw_desc.strip()) > 60:
                    display_desc = raw_desc[:400] + ("..." if len(raw_desc) > 400 else "")
                else:
                    # Generate a unique description from title + channel + topic
                    seed = int(hashlib.md5(row["video_id"].encode()).hexdigest(), 16) % 100
                    templates = [
                        f"This video by **{channel}** dives into **{title}**, making complex ideas easy to follow with clear explanations and real-world examples.",
                        f"A well-structured lesson from **{channel}** covering **{title}** — ideal for students who want a solid foundational understanding.",
                        f"**{channel}** breaks down **{title}** step by step, perfect for self-learners looking to master the topic at their own pace.",
                        f"Explore **{title}** through engaging visuals and expert commentary by **{channel}**. Great for both beginners and intermediate learners.",
                        f"This lecture from **{channel}** offers an in-depth look at **{title}**, with practical insights and examples that stick.",
                        f"**{channel}** presents **{title}** in a clear, concise format — highly recommended for anyone studying {topic.replace(' tutorial','').replace(' explained','').strip()}.",
                        f"A focused and informative video by **{channel}** that walks you through **{title}** with easy-to-understand explanations.",
                        f"Learn **{title}** the right way with this comprehensive guide from **{channel}**. Covers key concepts from scratch.",
                        f"**{channel}** simplifies **{title}** into digestible lessons — a great resource for students at any level.",
                        f"This educational video by **{channel}** covers **{title}** thoroughly, blending theory with practical understanding."
                    ]
                    display_desc = templates[seed % len(templates)]

                with st.expander("📄 About this video"):
                    st.markdown(display_desc)

            st.divider()

else:
    st.info("👆 Type a topic above to get started!")
    st.markdown("### 🔥 Popular Topics")
    cols = st.columns(4)
    popular = ["Machine Learning", "Python", "Calculus", "Physics",
               "World History", "Economics", "Biology", "Psychology"]
    for i, topic in enumerate(popular):
        with cols[i % 4]:
            st.button(topic, key=topic, disabled=True)