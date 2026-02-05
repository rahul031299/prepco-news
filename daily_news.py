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
                    if 'models/gemini-1.5-flash' in available_models:
                        active_model = 'models/gemini-1.5-flash'
                except:
                    pass 
                
                model = genai.GenerativeModel(active_model)

                # 2. FETCH NEWS
                q = topic if topic else "Business India Economy"
                items = get_google_news(q)
                context = "\n".join([f"{i+1}. {x.title} ({x.link})" for i, x in enumerate(items)])

                # 3. DEFINE PROMPT
                prompt_extra = ""
                if current_mode == "Jargon Buster":
                    prompt_extra = "Add a '💡 Word of the Day' section. Pick a term from the news. Define it in 1 simple line."
                elif current_mode == "Guesstimate Drill":
                    prompt_extra = "Add a '🧠 Daily Guesstimate' section related to the news. Give a 1-line hint formula. No answer."
                elif current_mode == "Sector Spotlight":
                    prompt_extra = "Add a '🏭 Sector Spotlight' section on the industry in the news. List 1 Tailwind, 1 Headwind, 2 Top Players."

                full_prompt = f"""
                Act as an IIM Mentor. Create a WhatsApp update for {day_name}, {today}.
                
                NEWS CONTEXT:
                {context}
                
                TASK:
                1. Pick the ONE most critical story.
                2. Summarize (1 sentence).
                3. Two Business Implications (MBA Angle).
                4. One Interview Question.
                5. {prompt_extra}
                
                OUTPUT FORMAT:
                ☀️ *PrepCo Morning Edge – {today.strftime('%d %b')}*
                
                📰 *THE HEADLINE:* [Summary]
                
                💼 *THE MBA ANGLE:*
                • [Point 1]
                • [Point 2]
                
                🎤 *THE INTERVIEW GRILL:* "[Question]"
                
                🔗 *Read More:* [Link]
                
                --------------------------------
                
                [Add-on Section Here]
                """

                # 4. GENERATE
                response = model.generate_content(full_prompt)
                st.code(response.text, language="markdown")
                st.success("✅ Ready to send!")

        except Exception as e:
            st.error(f"Error: {e}")
            st.warning("If this fails, try running 'pip install --upgrade google-generativeai' in your terminal.")
