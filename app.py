import streamlit as st
import pandas as pd
import json
import pydeck as pdk
from geopy.geocoders import Nominatim
from google import genai

# כותרת האתר
st.title("✈️ מתכנן מסלולים חכם: נסיעות, טיסות וחלופות")
st.write("הקלד מוצא ויעד. ה-AI יחשב זמני נסיעה, זמני טיסה ויציע מסלולים חלופיים!")

# משיכת המפתח הסודי מהגדרות השרת
api_key = st.secrets["GEMINI_API_KEY"]
client = genai.Client(api_key=api_key)
geolocator = Nominatim(user_agent="my_advanced_travel_itinerary_2026")

@st.cache_data
def analyze_comprehensive_travel(input_a, input_b):
    """פנייה מאוחדת ל-AI לשליפת שמות, שדות תעופה, זמנים ומסלולים חלופיים בפורמט JSON"""
    prompt = f"""
    Analyze a trip from '{input_a}' to '{input_b}'.
    Provide the following details based on current typical flights and routes:
    1. Clean English names for both locations.
    2. The closest major international airport for each.
    3. Estimated driving time (in hours/minutes) from each location to its respective airport.
    4. Estimated direct flight time between these airports.
    5. Alternative routes: Provide 1 or 2 alternative ways (e.g., a flight with 1 stopover/connection, or a direct train/drive if applicable). Include names and estimated total durations.
    6. A public Unsplash image URL for both locations.

    Return ONLY a valid JSON object matching this schema, without markdown or extra text:
    {{
        "name_a": "City A",
        "name_b": "City B",
        "airport_a": "Airport Name A",
        "airport_b": "Airport Name B",
        "drive_to_airport_a": "1 hour 15 mins",
        "drive_to_airport_b": "45 mins",
        "flight_time_direct": "4 hours 30 mins",
        "img_a": "URL",
        "img_b": "URL",
        "alternatives": [
            {{"type": "Flight with 1 Stop", "details": "Via Paris (CDG)", "duration": "7 hours 15 mins"}},
            {{"type": "Land Travel", "details": "Direct Train", "duration": "5 hours 0 mins"}}
        ]
    }}
    """
    response = client.models.generate_content(model='gemini-3.6-flash', contents=prompt)
    return json.loads(response.text.strip())

# תיבות קלט
קלט_א = st.text_input("📍 נקודת מוצא:", placeholder="למשל: תל אביב")
קלט_ב = st.text_input("📍 נקודת יעד:", placeholder="למשל: לונדון")

if st.button("חשב מסלול מלא") or (קלט_א and קלט_ב):
    with st.spinner("🤖 ה-AI מנתח טיסות, זמנים ומסלולים חלופיים..."):
        try:
            # 1. שליפת נתונים מה-AI
            data = analyze_comprehensive_travel(קלט_א, קלט_ב)
            
            # 2. מציאת קואורדינטות במפה
            loc_a = geolocator.geocode(data["name_a"])
            loc_b = geolocator.geocode(data["name_b"])
            air_a = geolocator.geocode(data["airport_a"])
            air_b = geolocator.geocode(data["airport_b"])

            if loc_a and loc_b and air_a and air_b:
                # 3. הצגת תמונות המקומות זה לצד זה
                col1, col2 = st.columns(2)
                with col1:
                    st.subheader(f"📸 {קלט_א}")
                    st.image(data["img_a"], use_container_width=True)
                    st.caption(f"🏛️ שדה תעופה: {data['airport_a']}")
                with col2:
                    st.subheader(f"📸 {קלט_ב}")
                    st.image(data["img_b"], use_container_width=True)
                    st.caption(f"🏛️ שדה תעופה: {data['airport_b']}")

                # 4. הצגת לוח זמנים מפורט בטבלה מעוצבת
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

                # 5. הצגת מסלולים חלופיים
                st.subheader("🔄 מסלולים חלופיים שהתגלו:")
                for alt in data["alternatives"]:
                    st.write(f"• **{alt['type']}**: {alt['details']} — ⏳ זמן כולל: {alt['duration']}")

                # 6. שרטוט המפה המתקדמת (Pydeck)
                arc_layer = pdk.Layer(
                    "ArcLayer",
                    data=[{"source": [air_a.longitude, air_a.latitude], "target": [air_b.longitude, air_b.latitude]}],
                    get_source_position="source",
                    get_target_position="target",
                    get_source_color=[0, 255, 150, 200],
                    get_target_color=[0, 150, 255, 200],
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
                    get_color=[255, 50, 50, 200],
                    get_width=3
                )

                st.subheader("🗺️ מפת המסלול המרכזי:")
                view_state = pdk.ViewState(latitude=(loc_a.latitude + loc_b.latitude)/2, longitude=(loc_a.longitude + loc_b.longitude)/2, zoom=2, pitch=30)
                st.pydeck_chart(pdk.Deck(layers=[arc_layer, line_layer], initial_view_state=view_state))
                
            else:
                st.error("המפה לא הצליחה לאתר את כל נקודות הציון. נסה שמות של ערים מרכזיות.")
        except Exception as e:
            st.error(f"שגיאה בקבלת נתונים מה-AI: {e}")
