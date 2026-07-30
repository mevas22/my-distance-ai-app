import streamlit as st
import pandas as pd
import json
import pydeck as pdk
from datetime import datetime
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
def analyze_comprehensive_travel(input_a, input_b, start_date, end_date):
    """פנייה מאוחדת ל-AI לשליפת כל הנתונים בעברית מלאה כולל סינון משחקים לפי תאריכים ומיקום"""
    prompt = f"""
    Analyze a trip from '{input_a}' to '{input_b}'. Based on current data for 2026, provide the following details:
    1. Clean HEBREW names for both locations.
    2. Official English names for both locations (for mapping).
    3. The closest major international airport for each, formatted like 'Official English Name (Hebrew Translation)'.
    4. Estimated driving time from each location to its respective airport.
    5. Estimated direct flight time between these airports.
    6. A sample list of standard flight schedules/options (frequencies, airlines) for direct flights explained in HEBREW.
    7. A list of major car rental agencies located directly at or near Airport B.
    8. A list of major football/soccer matches (including local leagues AND European tournaments like Champions League) within a 100km radius of Target B strictly between the dates {start_date} and {end_date}. 
       For each match/club, provide: the date, the club/match name in Hebrew, the stadium name in Hebrew, and latitude/longitude for mapping.
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
            {{"date": "2026-08-15", "club_or_match": "ברצלונה נגד ריאל מדריד", "stadium": "קאמפ נואו", "lat": 41.3809, "lon": 2.1228}}
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

# תיבות קלט
col_input1, col_input2 = st.columns(2)
with col_input1:
    קלט_א = st.text_input("📍 נקודת מוצא:", placeholder="למשל: תל אביב")
with col_input2:
    קלט_ב = st.text_input("📍 נקודת יעד:", placeholder="למשל: לונדון")

# שורת חיפוש לטווח תאריכים (תיבה אחת מאוחדת שעובדת בטוח)
st.subheader("📅 בחירת טווח תאריכים לחיפוש משחקים:")
טווח_תאריכים = st.date_input("בחר תאריך התחלה וסיום:", [datetime.now(), datetime.now()])

if st.button("בצע ניתוח מסלול") or (קלט_א and קלט_ב):
    if len(טווח_תאריכים) == 2:
        תאריך_התחלה = טווח_תאריכים[0].strftime('%Y-%m-%d')
        תאריך_סיום = טווח_תאריכים[1].strftime('%Y-%m-%d')
    else:
        תאריך_התחלה = datetime.now().strftime('%Y-%m-%d')
        תאריך_סיום = datetime.now().strftime('%Y-%m-%d')

    # הודעת טעינה קצרה ומקצועית בלבד כפי שביקשת
    with st.spinner("מחפש..."):
        try:
            # 1. שליפת נתונים מה-AI
            data = analyze_comprehensive_travel(קלט_א, קלט_ב, תאריך_התחלה, תאריך_סיום)
            
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
            st.subheader(f"⚽ אירועי ספורט ומפעלים אירופיים באזור:")
            matches = data.get("football_matches_hebrew", [])
            
            if matches:
                matches_df_list = []
                for m in matches:
                    matches_df_list.append({
                        "תאריך": m.get("date", "לא צוין"),
                        "משחק / מפעל אירופי": m["club_or_match"],
                        "אצטדיון": m["stadium"]
                    })
                # הצגת הטבלה בכיווניות ימין לשמאל
                st.table(pd.DataFrame(matches_df_list))
                
                # מפת אצטדיונים
                st.write("🗺️ מיקומי האצטדיונים באזור היעד:")
                st.map(pd.DataFrame({
                    'latitude': [m["lat"] for m in matches],
                    'longitude': [m["lon"] for m in matches]
                }))
            else:
                st.info(f"לא נמצאו משחקים או מפעלים אירופיים בטווח התאריכים המבוקשים.")

            # 7. הצגת מסלולים חלופיים
            st.subheader("🔄 חלופות מסלול מוצעות:")
            for alt in data["alternatives"]:
                st.write(f"• **{alt['type']}**: {alt['details']} — ⏳ זמן כולל: {alt['duration']}")
                
        except Exception as e:
            st.error(f"שגיאה בקבלת נתונים מה-AI: {e}")

            
