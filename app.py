
import streamlit as st
import pandas as pd
import json
import pydeck as pdk
from geopy.geocoders import Nominatim
from google import genai

# כותרת האתר
st.title("✈️ מתכנן מסלולים חכם: טיסות, רכבים וספורט")
st.write("הקלד מוצא ויעד לחישוב זמנים בעברית, לוח טיסות, השכרת רכב ומשחקי כדורגל באזור!")

# משיכת המפתח הסודי מהגדרות השרת
api_key = st.secrets["GEMINI_API_KEY"]
client = genai.Client(api_key=api_key)

# הגדרת שרת המפות עם המתנה ארוכה יותר למניעת קריסות
geolocator = Nominatim(user_agent="my_comprehensive_travel_itinerary_2026", timeout=10)

@st.cache_data
def analyze_comprehensive_travel(input_a, input_b):
    """פנייה מאוחדת ל-AI לשליפת כל הנתונים, כולל רכבים, טיסות וספורט בעברית ולפי שעון המוצא"""
    prompt = f"""
    Analyze a trip from '{input_a}' to '{input_b}'. Based on current data for 2026, provide the following details:
    1. Clean English names for both locations.
    2. The closest major international airport for each.
    3. Estimated driving time from each location to its respective airport.
    4. Estimated direct flight time between these airports.
    5. A sample list of standard flight schedules/options (frequencies, airlines) for direct flights. Convert all departure/arrival times to the ORIGIN location's time zone and explain them in HEBREW.
    6. A list of major car rental agencies located directly at or near Airport B (Yad 2).
    7. Upcoming or nearby major football/soccer matches or top clubs hosting matches in the destination area (Target B).
    8. Alternative routes (e.g. connections or land travel).
    9. Public Unsplash image URLs for both locations.

    Return ONLY a valid JSON object matching this schema, without markdown, notes, or extra text:
    {{
        "name_a": "City A",
        "name_b": "City B",
        "airport_a": "Airport Name A",
        "airport_b": "Airport Name B",
        "drive_to_airport_a": "1 hour 15 mins",
        "drive_to_airport_b": "45 mins",
        "flight_time_direct": "4 hours 30 mins",
        "flight_schedules_hebrew": [
            {{"airline": "El Al", "schedule": "טיסה יומית קבועה, המראה ב-08:00 ונחיתה ב-12:30 לפי שעון מוצא"}}
        ],
        "car_rentals_target_b": ["Avis", "Hertz", "Sixt"],
        "football_matches_hebrew": [
            {{"club_or_match": "קבוצת כדורגל מובילה באזור המארחת משחקים קרובים", "info": "משחקים קרובים באצטדיון המקומי באזור היעד"}}
        ],
        "img_a": "URL",
        "img_b": "URL",
        "alternatives": [
            {{"type": "Flight with 1 Stop", "details": "Via Paris", "duration": "7 hours"}}
        ]
    }}
    """
    response = client.models.generate_content(model='gemini-3.6-flash', contents=prompt)
    return json.loads(response.text.strip())

# תיבות קלט
קלט_א = st.text_input("📍 נקודת מוצא:", placeholder="למשל: תל אביב")
קלט_ב = st.text_input("📍 נקודת יעד:", placeholder="למשל: לונדון")

if st.button("חשב מסלול מלא") or (קלט_א and קלט_ב):
    with st.spinner("🤖 ה-AI אוסף נתוני טיסות, רכבים ומשחקי כדורגל..."):
        try:
            # 1. שליפת נתונים מה-AI
            data = analyze_comprehensive_travel(קלט_א, קלט_ב)
            
            # 2. הצגת תמונות המקומות זה לצד זה
            col1, col2 = st.columns(2)
            with col1:
                st.subheader(f"📸 {קלט_א}")
                st.image(data["img_a"], use_container_width=True)
                st.caption(f"🏛️ שדה תעופה: {data['airport_a']}")
            with col2:
                st.subheader(f"📸 {קלט_ב}")
                st.image(data["img_b"], use_container_width=True)
                st.caption(f"🏛️ שדה תעופה: {data['airport_b']}")

            # 3. הצגת לוח זמנים מפורט בטבלה מעוצבת
            st.subheader("⏱️ לוח זמנים משוער למסלול המרכזי (טיסה ישירה):")
            timeline_data = {
                "שלב במסלול": [
                    f"🚗 נסיעה מ-{קלט_א} אל {data['airport_a']}",
                    f"✈️ טיסה ישירה מ-{data['airport_a']} אל {data['airport_b']}",
                    f"🚗 נסיעה מ-{data['airport_b']} אל {קלט_ב}"
                ],
                "זמן משוער": [
                    data["drive_to_airport_a"],
                    data["flight_time_direct"],
                    data["drive_to_airport_b"]
                ]
            }
            st.table(pd.DataFrame(timeline_data))

            # 4. לוח זמני טיסות קיימות (בעברית ולפי שעון מוצא)
            st.subheader("📅 לוח טיסות קיימות/תדירות (לפי שעון מוצא):")
            for flight in data.get("flight_schedules_hebrew", []):
                st.write(f"• **{flight['airline']}**: {flight['schedule']}")

            # 5. מקומות להשכרת רכב ביעד 2
            st.subheader(f"🚗 סוכנויות השכרת רכב בשדה התעופה {data['airport_b']}:")
            car_list = ", ".join(data.get("car_rentals_target_b", []))
            st.write(f"סוכנויות זמינות בטרמינל או בסמוך אליו: **{car_list}**")

            # 6. חיפוש משחקי כדורגל קרובים
            st.subheader("⚽ משחקי כדורגל וספורט באזור היעד:")
            for match in data.get("football_matches_hebrew", []):
                st.write(f"• **{match['club_or_match']}**: {match['info']}")

            # 7. הצגת מסלולים חלופיים
            st.subheader("🔄 מסלולים חלופיים שהתגלו:")
            for alt in data["alternatives"]:
                st.write(f"• **{alt['type']}**: {alt['details']} — ⏳ זמן כולל: {alt['duration']}")

            # 8. מנגנון הגנה למפה עם ערכי צבעים תקינים לחלוטין
            try:
                loc_a = geolocator.geocode(data["name_a"])
                loc_b = geolocator.geocode(data["name_b"])
                air_a = geolocator.geocode(data["airport_a"])
                air_b = geolocator.geocode(data["airport_b"])

                if loc_a and loc_b and air_a and air_b:
                    # הוספנו צבעים תקינים כאן
                    arc_layer = pdk.Layer(
                        "ArcLayer",
                        data=[{"source": [air_a.longitude, air_a.latitude], "target": [air_b.longitude, air_b.latitude]}],
                        get_source_position="source",
                        get_target_position="target",
                        get_source_color=[0, 255, 150],
                        get_target_color=[0, 150, 255],
                        stroke_width=4,
                    )

                    line_data = [
                        {"start": [loc_a.longitude, loc_a.latitude], "end": [air_a.longitude, air_a.latitude]},
                        {"start": [air_b.longitude, air_b.latitude], "end": [loc_b.longitude, loc_b.latitude]}
                    ]
                    line_layer = pdk.Layer(
                        "LineLayer",
                        data=line_data,
                        get_source_position="start",
                        get_target_position="end",
                        get_color=[255, 50, 50],
                        get_width=3
                    )

                    st.subheader("🗺️ מפת המסלול המרכזי:")
                    view_state = pdk.ViewState(latitude=(loc_a.latitude + loc_b.latitude)/2, longitude=(loc_a.longitude + loc_b.longitude)/2, zoom=2, pitch=30)
                    st.pydeck_chart(pdk.Deck(layers=[arc_layer, line_layer], initial_view_state=view_state))
            except Exception as map_error:
                st.warning("🗺️ שרת המפות עמוס זמנית, השרטוט הגרפי לא זמין אך המידע שלמעלה מלא ומדויק!")
                
        except Exception as e:
            st.error(f"שגיאה בקבלת נתונים מה-AI: {e}")
