import streamlit as st
import pandas as pd
import json
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from google import genai

# כותרת האתר
st.title("🗺️ מחשב מרחקים חכם ומהיר")
st.write("הקלד שני מקומות בעולם לחישוב מהיר של מרחק, מפה ותמונות!")

# משיכת המפתח הסודי מהגדרות השרת
api_key = st.secrets["GEMINI_API_KEY"]
client = genai.Client(api_key=api_key)
geolocator = Nominatim(user_agent="my_fast_distance_website_123")

# פונקציית זיכרון מטמון
@st.cache_data
def analyze_places_with_ai(input_a, input_b):
    """פנייה אחת מהירה ל-AI שמחזירה את כל המידע על שני המקומות בבת אחת בפורמט JSON"""
    prompt = f"""
    Analyze these two user inputs: '{input_a}' and '{input_b}'.
    1. Correct typos and find their official English names.
    2. Provide a valid, public image URL for each place (use Unsplash).
    Return ONLY a valid JSON object matching this schema, no formatting or markdown:
    {{
        "name_a": "Official English Name A",
        "name_b": "Official English Name B",
        "img_a": "URL",
        "img_b": "URL"
    }}
    """
    # שינינו את המודל ל-gemini-2.5-flash כדי לקבל מכסה ענקית בחינם
    response = client.models.generate_content(model='gemini-2.5-flash', contents=prompt)
    return json.loads(response.text.strip())

# תיבות קלט
קלט_א = st.text_input("📍 מקום ראשון:", placeholder="למשל: תל אביבב")
קלט_ב = st.text_input("📍 מקום שני:", placeholder="למשל: ניו יורקק")

if st.button("חשב מרחק") or (קלט_א and קלט_ב):
    with st.spinner("⚡ ה-AI מנתח במהירות..."):
        try:
            # 1. קריאה מהירה ומאוחדת ל-AI
            ai_data = analyze_places_with_ai(קלט_א, קלט_ב)
            res_a = ai_data["name_a"]
            res_b = ai_data["name_b"]
            
            # 2. מיקום גיאוגרפי
            מיקום_א = geolocator.geocode(res_a)
            מיקום_ב = geolocator.geocode(res_b)

            if מיקום_א and מיקום_ב:
                # 3. הצגת תמונות זה לצד זה
                col1, col2 = st.columns(2)
                with col1:
                    st.subheader(f"📸 {קלט_א}")
                    if ai_data["img_a"]:
                        st.image(ai_data["img_a"], use_container_width=True)
                with col2:
                    st.subheader(f"📸 {קלט_ב}")
                    if ai_data["img_b"]:
                        st.image(ai_data["img_b"], use_container_width=True)

                # 4. חישוב מרחק
                מרחק = geodesic((מיקום_א.latitude, מיקום_א.longitude), 
                                (מיקום_ב.latitude, מיקום_ב.longitude)).kilometers
                st.success(f"📏 המרחק האווירי הוא {מרחק:.2f} קילומטרים.")

                # 5. מפה
                מפה_דאטה = pd.DataFrame({
                    'latitude': [מיקום_א.latitude, מיקום_ב.latitude],
                    'longitude': [מיקום_א.longitude, מיקום_ב.longitude]
                })
                st.map(מפה_דאטה)
            else:
                st.error("המפה לא מצאה את המיקומים. נסה לדייק בשמות.")
        except Exception as e:
            st.error(f"שגיאה: {e}")
