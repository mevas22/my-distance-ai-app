


import streamlit as st
import pandas as pd
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from google import genai

# כותרת האתר
st.title("🗺️ מחשב מרחקים חכם עם מפות ותמונות")
st.write("הקלד שני מקומות בעולם. ה-AI ינתח, יציג תמונות, ישרטט מפה ויחשב מרחק!")

# משיכת המפתח הסודי אוטומטית מהגדרות השרת של Streamlit
api_key = st.secrets["GEMINI_API_KEY"]
client = genai.Client(api_key=api_key)
geolocator = Nominatim(user_agent="my_distance_website_123")

# פונקציה לבקש מה-AI קישור לתמונה רלוונטית מהאינטרנט
def get_place_image_from_ai(place_name):
    prompt = f"Provide ONLY a direct, valid, and public image URL (Unsplash or Wikimedia preferred) representing the city or country '{place_name}'. Do not include markdown, text, or quotes. Just the raw URL."
    try:
        response = client.models.generate_content(model='gemini-3-flash-preview', contents=prompt)
        url = response.text.strip()
        if url.startswith("http"):
            return url
    except:
        pass
    return None

# תיבות קלט מעוצבות באתר
קלט_א = st.text_input("📍 מקום ראשון:", placeholder="למשל: תל אביבב")
קלט_ב = st.text_input("📍 מקום שני:", placeholder="למשל: ניו יורקק")

כפתור_לחץ = st.button("חשב מרחק ומצא תמונות")

if כפתור_לחץ or (קלט_א and קלט_ב):
    with st.spinner("🤖 ה-AI מנתח, מביא תמונות ומשרטט מפה..."):
        try:
            # 1. ניקוי שמות בעזרת ה-AI
            prompt_a = f"Take the following place name: '{קלט_א}'. Correct any typos and return ONLY the standard English name of this city or country."
            res_a = client.models.generate_content(model='gemini-3-flash-preview', contents=prompt_a).text.strip()
            
            prompt_b = f"Take the following place name: '{קלט_ב}'. Correct any typos and return ONLY the standard English name of this city or country."
            res_b = client.models.generate_content(model='gemini-3-flash-preview', contents=prompt_b).text.strip()

            # 2. מיקום גיאוגרפי
            מיקום_א = geolocator.geocode(res_a)
            מיקום_ב = geolocator.geocode(res_b)

            if מיקום_א and מיקום_ב:
                # 3. הצגת תמונות של המקומות בשני טורים (זה לצד זה)
                col1, col2 = st.columns(2)
                
                img_a_url = get_place_image_from_ai(res_a)
                img_b_url = get_place_image_from_ai(res_b)
                
                with col1:
                    st.subheader(f"📸 {קלט_a if 'קלט_a' in locals() else קלט_א}")
                    if img_a_url:
                        st.image(img_a_url, use_container_width=True)
                with col2:
                    st.subheader(f"📸 {קלט_ב}")
                    if img_b_url:
                        st.image(img_b_url, use_container_width=True)

                # 4. חישוב המרחק
                מרחק = geodesic((מיקום_א.latitude, מיקום_א.longitude), (מיקום_ב.latitude, מיקום_ב.longitude)).kilometers
                st.success(f"衡量 המרחק האווירי בין {קלט_א} ל-{קלט_ב} הוא {מרחק:.2f} קילומטרים.")

                # 5. יצירת מפה עם שתי הנקודות
                מפה_דאטה = pd.DataFrame({
                    'latitude': [מיקום_א.latitude, מיקום_ב.latitude],
                    'longitude': [מיקום_א.longitude, מיקום_ב.longitude]
                })
                st.subheader("🗺️ מיקום על המפה:")
                st.map(מפה_דאטה)
                
            else:
                st.error("המפה לא מצאה את המיקומים. נסה לדייק בשמות המקומות.")
        except Exception as e:
            st.error(f"ארעה שגיאה: {e}")
