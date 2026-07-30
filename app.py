
import streamlit as st
import pandas as pd
import json
import pydeck as pdk
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from google import genai

# כותרת האתר
st.title("✈️ מחשב מסלולי תעופה ונסיעה חכם")
st.write("הקלד שני מקומות בעולם. ה-AI ימצא את שדות התעופה הקרובים, יחשב מרחקים וישרטט את מסלולי הנסיעה והטיסה!")

# משיכת המפתח הסודי מהגדרות השרת
api_key = st.secrets["GEMINI_API_KEY"]
client = genai.Client(api_key=api_key)
geolocator = Nominatim(user_agent="my_advanced_flight_website_2026")

@st.cache_data
def analyze_places_and_airports(input_a, input_b):
    """פנייה חכמה ל-AI שמוצאת את שמות הערים באנגלית, תמונות, ושדות התעופה הבינלאומיים הקרובים ביותר"""
    prompt = f"""
    Analyze these two user inputs: '{input_a}' and '{input_b}'.
    For each input:
    1. Correct typos and find the official English name of the city/country.
    2. Find the closest major INTERNATIONAL Airport (return its official name or IATA code, e.g., 'John F. Kennedy International Airport' or 'Ben Gurion Airport').
    3. Provide a valid public Unsplash image URL for the place.
    
    Return ONLY a valid JSON object matching this schema, no markdown or formatting:
    {{
        "name_a": "Official English Name A",
        "airport_a": "Closest International Airport Name A",
        "img_a": "URL A",
        "name_b": "Official English Name B",
        "airport_b": "Closest International Airport Name B",
        "img_b": "URL B"
    }}
    """
    response = client.models.generate_content(model='gemini-3.6-flash', contents=prompt)
    return json.loads(response.text.strip())

# תיבות קלט
קלט_א = st.text_input("📍 נקודת מוצא (מקום א'):", placeholder="למשל: ירושלים")
קלט_ב = st.text_input("📍 נקודת יעד (מקום ב'):", placeholder="למשל: מנהטן")

if st.button("חשב מסלול שלם") or (קלט_א and קלט_ב):
    with st.spinner("⚡ ה-AI מאתר שדות תעופה ומשרטט מפות..."):
        try:
            # 1. שליפת נתונים מה-AI
            data = analyze_places_and_airports(קלט_א, קלט_ב)
            
            # 2. מציאת קואורדינטות במפה עבור כל 4 הנקודות
            loc_a = geolocator.geocode(data["name_a"])
            loc_b = geolocator.geocode(data["name_b"])
            air_a = geolocator.geocode(data["airport_a"])
            air_b = geolocator.geocode(data["airport_b"])

            if loc_a and loc_b and air_a and air_b:
                # 3. הצגת תמונות המקומות
                col1, col2 = st.columns(2)
                with col1:
                    st.subheader(f"📸 {קלט_א}")
                    st.image(data["img_a"], use_container_width=True)
                    st.caption(f"✈️ שדה תעופה קרוב: {data['airport_a']}")
                with col2:
                    st.subheader(f"📸 {קלט_ב}")
                    st.image(data["img_b"], use_container_width=True)
                    st.caption(f"✈️ שדה תעופה קרוב: {data['airport_b']}")

                # 4. חישוב מרחקים
                dist_flight = geodesic((air_a.latitude, air_a.longitude), (air_b.latitude, air_b.longitude)).kilometers
                st.info(f"🛫 המרחק האווירי (טיסה) בין שדות התעופה {data['airport_a']} ל-{data['airport_b']} הוא: {dist_flight:.2f} קילומטרים.")

                # 5. בניית מפה מתקדמת עם קווים ומסלולים (Pydeck)
                # קו נסיעה 1: ממקום א' לשדה תעופה א'
                # קשת טיסה: משדה א' לשדה ב'
                # קו נסיעה 2: משדה תעופה ב' למקום ב'
                
                # יצירת שכבת הקשת האווירית (צבע ירוק-כחול זוהר)
                arc_layer = pdk.Layer(
                    "ArcLayer",
                    data=[{
                        "source": [air_a.longitude, air_a.latitude],
                        "target": [air_b.longitude, air_b.latitude]
                    }],
                    get_source_position="source",
                    get_target_position="target",
                    get_source_color=[0, 255, 200, 200],
                    get_target_color=[255, 0, 150, 200],
                    stroke_width=4,
                )

                # יצירת שכבות נסיעה יבשתית לשדות התעופה (קווים ישרים בצבע אדום)
                line_data = [
                    {"start": [loc_a.longitude, loc_a.latitude], "end": [air_a.longitude, air_a.latitude]},
                    {"start": [air_b.longitude, air_b.latitude], "end": [loc_b.longitude, loc_b.latitude]}
                ]
                line_layer = pdk.Layer(
                    "LineLayer",
                    data=line_data,
                    get_source_position="start",
                    get_target_position="end",
                    get_color=[255, 50, 50, 255],
                    get_width=3
                )

                # שכבת נקודות ציון (נקודות על המפה)
                point_data = pd.DataFrame({
                    "lon": [loc_a.longitude, loc_b.longitude, air_a.longitude, air_b.longitude],
                    "lat": [loc_a.latitude, loc_b.latitude, air_a.latitude, air_b.latitude],
                    "name": [data["name_a"], data["name_b"], "Airport A", "Airport B"]
                })
                point_layer = pdk.Layer(
                    "ScatterplotLayer",
                    data=point_data,
                    get_position="[lon, lat]",
                    get_color=[255, 255, 255, 200],
                    get_radius=5000,
                    radius_min_pixels=5
                )

                st.subheader("🗺️ מפת מסלול משולבת (קווים אדומים = נסיעה לשדה, קשת זוהרת = מסלול טיסה):")
                
                # הצגת המפה האינטראקטיבית
                view_state = pdk.ViewState(latitude=(loc_a.latitude + loc_b.latitude)/2, longitude=(loc_a.longitude + loc_b.longitude)/2, zoom=2, pitch=30)
                st.pydeck_chart(pdk.Deck(layers=[arc_layer, line_layer, point_layer], initial_view_state=view_state))
                
            else:
                st.error("המערכת לא הצליחה לאתר את כל נקודות הציון במפה. נסה לשנות או לדייק בשמות המקומות.")
        except Exception as e:
            st.error(f"שגיאה בעיבוד הנתונים: {e}")
