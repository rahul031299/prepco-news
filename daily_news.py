import streamlit as st
import google.generativeai as genai
import feedparser
import datetime

# --- PAGE CONFIG ---
st.set_page_config(page_title="Auto-News Generator", page_icon="🤖")

# --- SIDEBAR: API KEY ---
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
else:
    api_key = st.sidebar.text_input("Enter Gemini API Key", type="password")

# --- AUTO-DETECT DAY & ADD-ON ---
today = datetime.date.today()
day_name = today.strftime("%A") 
weekday_num = today.weekday()   

# Schedule Logic
if weekday_num == 0 or weekday_num == 2:   # Mon, Wed
    current_mode = "Jargon Buster"
    icon = "💡"
elif weekday_num == 1 or weekday_num == 3: # Tue, Thu
    current_mode = "Guesstimate Drill"
    icon = "🧠"
elif weekday_num == 4:                     # Fri
    current_mode = "Sector Spotlight"
    icon = "🏭"
else:                                      # Sat, Sun
    current_mode = "Standard News"
    icon = "📰"

st.title(f"{icon} Daily Update: {day_name}")
st.info(f"Today's Auto-Mode: **{current_mode}**")

# --- NEWS FUNCTION ---
def get_google_news(query):
    # RSS Feed for Business News India
    url = f"https://news.google.com/rss/search?q={query.replace(' ', '+')}&hl=en-IN&gl=IN&ceid=IN:en"
    return feedparser.parse(url).entries[:5]

# --- MAIN APP ---
topic = st.text_input("Specific Topic (Optional)", placeholder="Leave blank for Top Stories")

if st.button("Generate Today's Update"):
    if not api_key:
        st.error("⚠️ Need API Key")
    else:
        try:
            with st.spinner(f"Crafting {day_name}'s Update..."):
                # 1. SETUP MODEL (Auto-Healing)
                genai.configure(api_key=api_key)
                
                # Try to find a working model
                active_model = "models/gemini-pro" # Safe default
                try:
                    available_models = [m.name for m in genai.list_models()]
                    if 'models/gem
