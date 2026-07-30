%%writefile app.py
import streamlit as st
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from google import genai

# כותרת האתר שתופיע למעלה
st.title("🤖 מחשב מרחקים חכם עם AI")
st.write("הקלד שני מקומות בעולם (בכל שפה, גם עם שגיאות כתיב) וה-AI יחשב את המרחק ביניהם!")

# שדה להזנת מפתח ה-API בצורה בטוחה באתר
api_key = st.sidebar.text_input("הכנס את מפתח ה-Gemini API שלך:", type="password")

if api_key:
    client = genai.Client(api_key=api_key)
    geolocator = Nominatim(user_agent="my_distance_website_123")

    # תיבות קלט מעוצבות באתר
    קלט_א = st.text_input("📍 מקום ראשון:", placeholder="למשל: תל אביבב")
    קלט_ב = st.text_input("📍 מקום שני:", placeholder="למשל: ניו יורקק")

    # כפתור הפעלה לאתר
    if st.button("חשב מרחק"):
        if קלט_א and קלט_ב:
            with st.spinner("ה-AI מנתח את השמות ומחשב..."):
                try:
                    # פנייה ל-AI
                    prompt = f"Take the following place name: '{קלט_א}'. Correct any typos and return ONLY the standard English name of this city or country."
                    res_a = client.models.generate_content(model='gemini-3-flash-preview', contents=prompt).text.strip()
                    
                    prompt_b = f"Take the following place name: '{קלט_ב}'. Correct any typos and return ONLY the standard English name of this city or country."
                    res_b = client.models.generate_content(model='gemini-3-flash-preview', contents=prompt_b).text.strip()

                    # חיפוש במפה
                    מיקום_א = geolocator.geocode(res_a)
                    מיקום_ב = geolocator.geocode(res_b)

                    if מיקום_א and מיקום_ב:
                        מרחק = geodesic((מיקום_א.latitude, מיקום_א.longitude), (מיקום_ב.latitude, מיקום_ב.longitude)).kilometers
                        # הצגת התוצאה בריבוע ירוק ויפה באתר
                        st.success(f"📏 המרחק האווירי בין {קלט_א} ({res_a}) ל-{קלט_ב} ({res_b}) הוא {מרחק:.2f} קילומטרים.")
                    else:
                        st.error("המפה לא מצאה את המיקומים. נסה לדייק בשמות.")
                except Exception as e:
                    st.error(f"שגיאה בהפעלת ה-AI: {e}")
        else:
            st.warning("אנא הכנס את שני המקומות.")
else:
    st.info("👈 אנא הכנס את מפתח ה-API שלך בתפריט הצדדי כדי להפעיל את האתר.")
