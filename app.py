import streamlit as st
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from google import genai

# כותרת האתר
st.title("🤖 מחשב מרחקים חכם עם AI")
st.write("הקלד שני מקומות בעולם (לחץ Enter או על הכפתור כדי לחשב!)")

# משיכת המפתח הסודי אוטומטית מהגדרות השרת של Streamlit
api_key = st.secrets["GEMINI_API_KEY"]

client = genai.Client(api_key=api_key)
geolocator = Nominatim(user_agent="my_distance_website_123")

# תיבות קלט מעוצבות באתר
קלט_א = st.text_input("📍 מקום ראשון:", placeholder="למשל: תל אביבב")
קלט_ב = st.text_input("📍 מקום שני:", placeholder="למשל: ניו יורקק")

# יצירת הכפתור
כפתור_לחץ = st.button("חשב מרחק")

# השינוי המרכזי: החיפוש ירוץ אם לחצו על הכפתור או אם שני השדות מלאים ונלחץ Enter
if כפתור_לחץ or (קלט_א and קלט_ב):
    with st.spinner("ה-AI מנתח את השמות ומחשב..."):
        try:
            # פנייה ל-AI בשביל מקום ראשון
            prompt = f"Take the following place name: '{קלט_א}'. Correct any typos and return ONLY the standard English name of this city or country."
            res_a = client.models.generate_content(model='gemini-3-flash-preview', contents=prompt).text.strip()
            
            # פנייה ל-AI בשביל מקום שני
            prompt_b = f"Take the following place name: '{קלט_ב}'. Correct any typos and return ONLY the standard English name of this city or country."
            res_b = client.models.generate_content(model='gemini-3-flash-preview', contents=prompt_b).text.strip()

            # חיפוש במפה
            מיקום_א = geolocator.geocode(res_a)
            מיקום_ב = geolocator.geocode(res_b)

            if מיקום_א and מיקום_ב:
                מרחק = geodesic((מיקום_א.latitude, מיקום_א.longitude), (מיקום_ב.latitude, מיקום_ב.longitude)).kilometers
                st.success(f"📏 המרחק האווירי בין {קלט_א} ({res_a}) ל-{קלט_ב} ({res_b}) הוא {מרחק:.2f} קילומטרים.")
            else:
                st.error("המפה לא מצאה את המיקומים. נסה לדייק בשמות.")
        except Exception as e:
            st.error(f"שגיאה בהפעלת ה-AI: {e}")


