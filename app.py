import streamlit as st
import pandas as pd
import json
import pydeck as pdk
from datetime import datetime, timedelta
from geopy.geocoders import Nominatim
from google import genai

# הגדרת ממשק האתר ופריסה רחבה
st.set_page_config(page_title="מערכת תכנון מסלולים וספורט", layout="wide")

# הזרקת קוד עיצוב (CSS) למראה בוגר, רציני, RTL מלא ותמונת רקע מגמר מונדיאל 2022
st.markdown(
    """
    <style>
    /* רקע האפליקציה - מונדיאל 2022 עם שכבה כהה יוקרתית */
    .stApp {
        direction: rtl;
        text-align: right;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        background-image: linear-gradient(rgba(17, 24, 39, 0.88), rgba(17, 24, 39, 0.88)), 
                          url('https://unsplash.com');
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        color: #f3f4f6 !important;
    }
    
    /* התאמת צבעי כותרות וטקסטים למראה נקי */
    h1, h2, h3, h4, h5, h6, p, span, label {
        color: #ffffff !important;
        text-align: right !important;
    }
    
    /* הפיכת תיבות קלט וטבלאות ל-RTL מלא ומראה מודרני */
    input, select, textarea, div {
        direction: rtl !important;
        text-align: right !important;
    }
    
    /* הפיכת הטבלאות (DataFrame) למימין לשמאל */
    .stDataFrame, table, th, td {
        direction: rtl !important;
        text-align: right !important;
        color: #f3f4f6 !important;
        background-color: rgba(31, 41, 55, 0.6) !important;
    }
    
    /* עיצוב כפתור רציני וסולידי */
    .stButton>button {
        width: 100%;
        background-color: #0f766e !important;
        color: white !important;
        border: none !important;
        padding: 10px !important;
        font-weight: bold !important;
        border-radius: 4px !important;
    }
    
    /* עיצוב אלמנטים של התראות ומידע */
    .stAlert {
        background-color: rgba(55, 65, 81, 0.7) !important;
        color: #ffffff !important;
        border: 1px solid #4b5563 !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# כותרת האתר במראה רשמי
st.title("מערכת ניתוח מסלולים ואירועי ספורט בינלאומיים")
st.write("הזן נקודת מוצא ויעד לקבלת זמני נסיעה, תדירות טיסות וסריקת משחקי כדורגל מקומיים ואירופיים.")

# משיכת המפתח הסודי מהגדרות השרת
api_key = st.secrets["GEMINI_API_KEY"]
client = genai.Client(api_key=api_key)
geolocator = Nominatim(user_agent="my_comprehensive_travel_itinerary_2026", timeout=10)

@st.cache_data
def analyze_comprehensive_travel(input_a, input_b, start_date, end_date, max_price):
    """פנייה מאוחדת ל-AI לסריקת כל המשחקים, כולל ליגות מקומיות ומפעלים אירופיים"""
    prompt = f"""
    Analyze a trip from '{input_a}' to '{input_b}' for the year 2026. Provide the following details:
    1. Clean HEBREW names for both locations.
    2. Official English names for both locations (for mapping).
    3. The closest major international airport for each location, formatted EXACTLY like this: 'Official English Name (Hebrew Translation in Parentheses)'.
    4. Estimated driving time from each location to its respective airport.
    5. Estimated direct flight time between these airports.
    6. A sample list of standard flight schedules/options (frequencies, airlines) explained in HEBREW.
    7. A list of major car rental agencies located directly at or near Airport B.
    8. A COMPREHENSIVE and exhaustive list of ALL major football matches (including local leagues AND European tournaments like UEFA Champions League, Europa League, Conference League) scheduled within a 100km radius of the destination area (Target B) strictly between the dates {start_date} and {end_date}, where ticket prices start BELOW {max_price} USD.
       For each match, provide: the date of the match, the club/match name in Hebrew (including tournament type if European), the stadium name in Hebrew, the approximate minimum ticket price in USD, specific approximate latitude and longitude, and a REAL valid public ticketing search URL.
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
            {{"date": "2026-08-15", "club_or_match": "צ'לסי נגל ריאל מדריד (ליגת האלופות)", "stadium": "סטמפורד ברידג'", "price": 140, "lat": 51.4816, "lon": -0.1910, "ticket_url": "https://stubhub.com"}}
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
    st.subheader("📅 תאריך יציאה:")
    תאריך_יציאה_קלט = st.date_input("תאריך טיסה הלוך:", datetime.now())
with col_end:
    st.subheader("📅 תאריך חזרה:")
    תאריך_חזרה_קלט = st.date_input("תאריך טיסה חזור:", datetime.now() + timedelta(days=7))
with col_price:
    st.subheader("💰 תקציב מקסימלי לכרטיס:")
    מחיר_מקסימום = st.slider("בחר מחיר מקסימלי (USD $):", min_value=20, max_value=500, value=150, step=10)

if st.button("בצע ניתוח מסלול") or (קלט_א and קלט_ב):
    תאריך_התחלה = תאריך_יציאה_קלט.strftime('%Y-%m-%d')
    תאריך_סיום = תאריך_חזרה_קלט.strftime('%Y-%m-%d')

    # הודעת טעינה קצרה ומקצועית בלבד
    with st.spinner("מחפש..."):
        try:
            # 1. שליפת נתונים מה-AI
            data = analyze_comprehensive_travel(קלט_א, קלט_ב, תאריך_התחלה, תאריך_סיום, מחיר_מקסימום)
            
            # 2. הצגת תמונות המקומות
            col1, col2 = st.columns(2)
            with col1:
                st.subheader(f"📸 {data['name_a_hebrew']}")
                st.image(data["img_a"], use_container_width=True)
                st.caption(f"שדה תעופה: {data['airport_a']}")
            with col2:
                st.subheader(f"📸 {data['name_b_hebrew']}")
                st.image(data["img_b"], use_container_width=True)
                st.caption(f"שדה תעופה: {data['airport_b']}")

            # 3. הצגת לוח זמנים מפורט בטבלה מעוצבת מימין לשמאל
            st.subheader("⏱️ לוח זמנים משוער למסלול (טיסה ישירה):")
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
            st.subheader("📅 תדירות טיסות קיימות:")
            for flight in data.get("flight_schedules_hebrew", []):
                st.write(f"• **{flight['airline']}**: {flight['schedule']}")

            # 5. מקומות להשכרת רכב
            st.subheader(f"🚗 סוכנויות השכרת רכב בשדה התעופה {data['airport_b']}:")
            car_list = ", ".join(data.get("car_rentals_target_b", []))
            st.write(f"סוכנויות זמינות בטרמינל: **{car_list}**")

            # 6. רשימת משחקים מלאה כולל ליגות אירופיות בטבלה מימין לשמאל
            st.subheader("⚽ אירועי ספורט ומפעלים אירופיים באזור:")
            matches = data.get("football_matches_hebrew", [])
            filtered_matches = [m for m in matches if m.get("price", 0) <= מחיר_מקסימום]
            
            if filtered_matches:
                matches_df_list = []
                for m in filtered_matches:
                    matches_df_list.append({
                        "תאריך": m.get("date", "לא צוין"),
                        "משחק / מפעל אירופי": m["club_or_match"],
                        "אצטדיון": m["stadium"],
                        "מחיר התחלתי": f"${m['price']}"
                    })
                st.table(pd.DataFrame(matches_df_list))

                st.write("🎟️ **ערוצי רכישת כרטיסים רשמיים:**")
                for m in filtered_matches: st.markdown(f"• **{m['club_or_match']}** ({m.get('date', '')}) — [לחץ למעבר לאתר הרכישה]({m['ticket_url']})")
                
                # מפת אצטדיונים
                st.write("🗺️ מיקומי האצטדיונים באזור היעד:")
                st.map(pd.DataFrame({
                    'latitude': [m["lat"] for m in filtered_matches],
                    'longitude': [m["lon"] for m in filtered_matches]
                }))
            else:
                st.info("לא נמצאו משחקים או מפעלים אירופיים בטווח המחירים והתאריכים המבוקשים.")

            # 7. הצגת מסלולים חלופיים בטבלה רשמית
            st.subheader("🔄 חלופות מסלול מוצעות:")
            st.table(pd.DataFrame([{"סוג מסלול": a.get("type", ""), "פרטים": a.get("details", ""), "משך זמן כולל": a.get("duration", "")} for a in data.get("alternatives", [])]))
            
