
import streamlit as st
import pandas as pd
import json
import pydeck as pdk
from datetime import datetime, timedelta
from geopy.geocoders import Nominatim
from google import genai

# הגדרת ממשק האתר ופריסה רחבה
st.set_page_config(page_title="מתכנן מסלולים חכם", layout="wide")

# הזרקת קוד עיצוב (CSS) להפיכת האתר ל-RTL והוספת תמונת רקע
st.markdown(
    """
    <style>
    .stApp {
        direction: rtl;
        text-align: right;
        background-image: linear-gradient(rgba(255, 255, 255, 0.85), rgba(255, 255, 255, 0.85)), 
                          url('https://unsplash.com');
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }
    input, select, textarea, div {
        direction: rtl !important;
        text-align: right !important;
    }
    .stButton>button {
        width: 100%;
        background-color: #1e7e34 !important;
        color: white !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# כותרת האתר
st.title("⚽ מתכנן מסלולים חכם: טיסות, רכבים וכל משחקי הספורט ביעד")
st.write("הקלד מוצא ויעד לחישוב זמנים, השכרת רכב וסריקה מלאה של כל משחקי הכדורגל לאורך כל תקופת השהות!")

# משיכת המפתח הסודי מהגדרות השרת
api_key = st.secrets["GEMINI_API_KEY"]
client = genai.Client(api_key=api_key)
geolocator = Nominatim(user_agent="my_comprehensive_travel_itinerary_2026", timeout=10)

@st.cache_data
def analyze_comprehensive_travel(input_a, input_b, start_date, end_date, max_price):
    """פנייה מאוחדת ל-AI לסריקה מקיפה של כל המשחקים באזור לאורך כל ימי השהות המבוקשים"""
    prompt = f"""
    Analyze a trip from '{input_a}' to '{input_b}'. Based on current live data for 2026, provide the following details:
    1. Clean HEBREW names for both locations.
    2. Official English names for both locations (for mapping).
    3. The closest major international airport for each location, formatted EXACTLY like this: 'Official English Name (Hebrew Translation in Parentheses)'.
    4. Estimated driving time from each location to its respective airport.
    5. Estimated direct flight time between these airports.
    6. A sample list of standard flight schedules/options (frequencies, airlines) for direct flights explained in HEBREW.
    7. A list of major car rental agencies located directly at or near Airport B.
    8. A COMPREHENSIVE and exhaustive list of ALL major football matches or sports events scheduled within a 100km radius of the destination area (Target B) during the entire duration from {start_date} to {end_date}, where ticket prices start BELOW {max_price} USD. Include as many matches as possible for these dates.
       For each match, provide: the date of the match, the club/match name in Hebrew, the stadium name in Hebrew, the approximate minimum ticket price in USD, specific approximate latitude and longitude, and a REAL valid public ticketing search URL (e.g., StubHub, Ticketmaster, or Viagogo search link for that match).
    9. Alternative routes explained in Hebrew.
    10. Public Unsplash image URLs for both locations.

    Return ONLY a valid JSON object matching this schema, without markdown, notes, or extra text:
    {{
        "name_a_hebrew": "שם מוצא בעברית",
        "name_b_hebrew": "שם יעד בעברית",
        "name_a_en": "City A",
        "name_b_en": "City B",
        "airport_a": "Ben Gurion Airport (נמל התעופה בן גוריון)",
        "airport_b": "Heathrow Airport (נמל התעופה הית'רו)",
        "drive_to_airport_a": "שעה ו-15 דקות",
        "drive_to_airport_b": "45 דקות",
        "flight_time_direct": "4 שעות ו-30 דקות",
        "flight_schedules_hebrew": [
            {{"airline": "אל על", "schedule": "טיסה יומית קבועה"}}
        ],
        "car_rentals_target_b": ["Avis", "Hertz"],
        "football_matches_hebrew": [
            {{"date": "2026-08-15", "club_or_match": "ברצלונה נגד ריאל מדריד", "stadium": "קאמפ נואו", "price": 120, "lat": 41.3809, "lon": 2.1228, "ticket_url": "https://stubhub.com"}}
        ],
        "img_a": "URL",
        "img_b": "URL",
        "alternatives": [
            {{"type": "טיסה עם עצירת ביניים", "details": "דרך פריז", "duration": "7 שעות"}}
        ]
    }}
    """
    response = client.models.generate_content(model='gemini-3.6-flash', contents=prompt)
    return json.loads(response.text.strip())

# תיבות קלט ומערך הגדרות
col_input1, col_input2 = st.columns(2)
with col_input1:
    קלט_א = st.text_input("📍 נקודת מוצא:", placeholder="למשל: תל אביב")
with col_input2:
    קלט_ב = st.text_input("📍 נקודת יעד:", placeholder="למשל: לונדון")

# פיצול התאריכים לשתי תיבות נפרדות ומד תקציב
col_start, col_end, col_price = st.columns(3)
with col_start:
    st.subheader("📅 תאריך יציאה לדרך:")
    תאריך_יציאה_קלט = st.date_input("בחר תאריך טיסה הלוך:", datetime.now())
with col_end:
    st.subheader("📅 תאריך חזרה:")
    תאריך_חזרה_קלט = st.date_input("בחר תאריך טיסה חזור:", datetime.now() + timedelta(days=7))
with col_price:
    st.subheader("💰 תקציב מקסימלי לכרטיס:")
    מחיר_מקסימום = st.slider("בחר מחיר מקסימלי (בדולר $):", min_value=20, max_value=500, value=150, step=10)

if st.button("חשב מסלול וחפש כרטיסים") or (קלט_א and קלט_ב):
    תאריך_התחלה = תאריך_יציאה_קלט.strftime('%Y-%m-%d')
    תאריך_סיום = תאריך_חזרה_קלט.strftime('%Y-%m-%d')

    with st.spinner("🤖 ה-AI סורק את כל לוחות המשחקים לימי השהות שלכם..."):
        try:
            # 1. שליפת נתונים מה-AI
            data = analyze_comprehensive_travel(קלט_א, קלט_ב, תאריך_התחלה, תאריך_סיום, מחיר_מקסימום)
            
            # 2. הצגת תמונות המקומות
            col1, col2 = st.columns(2)
            with col1:
                st.subheader(f"📸 {data['name_a_hebrew']}")
                st.image(data["img_a"], use_container_width=True)
                st.caption(f"🏛️ שדה תעופה: {data['airport_a']}")
            with col2:
                st.subheader(f"📸 {data['name_b_hebrew']}")
                st.image(data["img_b"], use_container_width=True)
                st.caption(f"🏛️ שדה תעופה: {data['airport_b']}")

            # 3. הצגת לוח זמנים מפורט בטבלה מעוצבת
            st.subheader("⏱️ לוח זמנים משוער למסלול המרכזי (טיסה ישירה):")
            timeline_data = {
                "שלב במסלול": [
                    f"🚗 נסיעה מ-{data['name_a_hebrew']} אל {data['airport_a']}",
                    f"✈️ טיסה ישירה בין שדות התעופה",
                    f"🚗 נסיעה מ-{data['airport_b']} אל {data['name_b_hebrew']}"
                ],
                "זמן משוער": [
                    data["drive_to_airport_a"],
                    data["flight_time_direct"],
                    data["drive_to_airport_b"]
                ]
            }
            st.table(pd.DataFrame(timeline_data))

            # 4. לוח זמני טיסות קיימות
            st.subheader("📅 לוח טיסות קיימות/תדירות:")
            for flight in data.get("flight_schedules_hebrew", []):
                st.write(f"• **{flight['airline']}**: {flight['schedule']}")

            # 5. מקומות להשכרת רכב
            st.subheader(f"🚗 סוכנויות השכרת רכב בשדה התעופה {data['airport_b']}:")
            car_list = ", ".join(data.get("car_rentals_target_b", []))
            st.write(f"סוכנויות זמינות: **{car_list}**")

            # 6. רשימת משחקים מלאה ומורחבת לכל ימי השהות
            st.subheader(f"⚽ כל המשחקים באזור בין ה-{תאריך_התחלה} ל-{תאריך_סיום} (עד ${מחיר_מקסימום}):")
            matches = data.get("football_matches_hebrew", [])
            filtered_matches = [m for m in matches if m.get("price", 0) <= מחיר_מקסימום]
            
            if filtered_matches:
                # הצגת המשחקים בפורמט טבלה נקייה הכוללת את תאריך המשחק
                matches_df_list = []
                for m in filtered_matches:
                    matches_df_list.append({
                        "תאריך": m.get("date", "לא צוין"),
                        "משחק / אירוע": m["club_or_match"],
                        "אצטדיון": m["stadium"],
                        "מחיר התחלתי": f"${m['price']}"
                    })
                st.table(pd.DataFrame(matches_df_list))

                # הצגת כפתורי רכישה נוחים מתחת לטבלה
                st.write("🎟️ **קישורים ישירים לבדיקת זמינות ורכישת כרטיסים:**")
                for m in filtered_matches:
                    st.markdown(f"• לכרטיסים עבור **{m['club_or_match']}** ({m.get('date', '')}) — [לחץ כאן לרכישה]({m['ticket_url']})")
                
                # מפת אצטדיונים
                st.write("🗺️ מיקומי האצטדיונים הפעילים ביעד לאורך השהות שלכם:")
                st.map(pd.DataFrame({
                    'latitude': [m["lat"] for m in filtered_matches],
                    'longitude': [m["lon"] for m in filtered_matches]
                }))
            else:
                st.info(f"לא נמצאו משחקי ספורט שתואמים את התאריכים או את מסגרת התקציב שלכם.")

            # 7. הצגת מסלולים חלופיים
            st.subheader("🔄 מסלולים חלופיים שהתגלו:")
            for alt in data["alternatives"]:
                st.write(f"• **{alt['type']}**: {alt['details']} — ⏳ זמן כולל: {alt['duration']}")
                
        except Exception as e:
            st.error(f"שגיאה בקבלת נתונים מה-AI: {e}")
