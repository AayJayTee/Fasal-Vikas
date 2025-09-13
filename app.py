import streamlit as st
import pickle
import numpy as np
import os
import joblib
import pandas as pd
from streamlit_option_menu import option_menu

#To add translation feature (send request to LibreTranslate server)
import requests

LIBRE_URL = "https://libretranslate.de/translate"  # You can also self-host or use another instance


# Supported languages for dropdown (code: display name)
LANGUAGES = {
    "en": "English",
    "hi": "Hindi",
    "or": "Odia",
    "bn": "Bengali",
    "ta": "Tamil",
    "te": "Telugu",
    "mr": "Marathi",
    "gu": "Gujarati",
    "kn": "Kannada",
    "pa": "Punjabi"
}

# Session state for language
if "language" not in st.session_state:
    st.session_state.language = "en"

def translate_text(text, dest):
    if dest == "en":  # Skip if English
        return text
    try:
        response = requests.post(
            LIBRE_URL,
            data={
                "q": text,
                "source": "en",     # your base language
                "target": dest,
                "format": "text"
            }
        )
        if response.status_code == 200:
            return response.json()["translatedText"]
        else:
            return text  # fallback
    except Exception:
        return text

# Language selection dropdown at the top right
col1, col2 = st.columns([8, 1])
with col2:
    selected_lang = st.selectbox(
        "🌐",
        options=list(LANGUAGES.keys()),
        format_func=lambda x: LANGUAGES[x],
        index=list(LANGUAGES.keys()).index(st.session_state.language),
        key="language_select"
    )
    st.session_state.language = selected_lang

def _(text):
    """Translate text to selected language."""
    return translate_text(text, st.session_state.language)

st.set_page_config(
    page_title=_("Fasal Vikas"),
    page_icon=":corn:",
    layout="wide",
    initial_sidebar_state="expanded"
)

def get_yield_recommendations(crop, area, season, pH, rainfall, temperature, production, predicted_yield):
    recs = []

    # Area-based suggestions
    if area < 1:
        recs.append(
            _(f"Your cultivation area for {crop} is small ({area:.2f} hectares). Use high-yielding seed varieties, optimize plant spacing, and apply organic manure to maximize output.")
        )
    elif area > 10:
        recs.append(
            _(f"With a large area ({area:.2f} hectares) for {crop}, mechanize sowing and harvesting, and use precision agriculture tools for efficient resource management.")
        )

    # Crop-specific recommendations
    crop_lower = crop.lower()
    season_lower = season.lower()

    if crop_lower == "rice":
        if season_lower == "kharif" and rainfall < 60:
            recs.append(
                _("Rice in Kharif season needs at least 60 mm rainfall. Use alternate wetting and drying irrigation, and maintain proper bunds to conserve water.")
            )
        if pH < 6.0 or pH > 7.5:
            recs.append(
                _(f"Rice grows best in soil pH between 6.0 and 7.5. Your pH is {pH:.2f}. Apply lime if pH is low, or gypsum if pH is high.")
            )
        recs.append(
            _("Apply recommended doses of nitrogen, phosphorus, and potassium fertilizers at key growth stages. Use certified disease-free seeds.")
        )
        recs.append(
            _("Monitor for blast and bacterial leaf blight. Use resistant varieties and follow integrated pest management.")
        )
        recs.append(
            _("Harvest at the right moisture content (20-24%) to reduce post-harvest losses.")
        )

    elif crop_lower == "wheat":
        if season_lower == "rabi" and temperature < 15:
            recs.append(
                _(f"Wheat in Rabi season prefers temperatures above 15°C. Use early sowing and select cold-tolerant varieties.")
            )
        if pH < 6.0 or pH > 7.0:
            recs.append(
                _(f"Wheat prefers soil pH between 6.0 and 7.0. Your pH is {pH:.2f}. Apply lime or sulfur as needed.")
            )
        recs.append(
            _("Ensure timely irrigation at crown root initiation and grain filling stages. Avoid waterlogging.")
        )
        recs.append(
            _("Apply balanced fertilizers and micronutrients, especially zinc and iron, for better grain quality.")
        )
        recs.append(
            _("Control rust and aphids using recommended fungicides and insecticides.")
        )
        recs.append(
            _("Harvest when grains are hard and straw is dry for maximum yield.")
        )

    elif crop_lower == "cotton":
        if temperature < 20:
            recs.append(
                _(f"Cotton prefers warmer temperatures. Current temperature is {temperature:.1f}°C. Delay sowing or use protective covers if possible.")
            )
        if season_lower == "kharif":
            recs.append(
                _("Monitor for bollworm and whitefly. Use pheromone traps and biocontrol agents.")
            )
        recs.append(
            _("Apply nitrogen in split doses and ensure adequate potassium for boll development.")
        )
        recs.append(
            _("Practice timely irrigation, especially during flowering and boll formation.")
        )
        recs.append(
            _("Harvest cotton when bolls are fully mature and open to avoid quality loss.")
        )

    elif crop_lower == "soyabean":
        if rainfall < 40:
            recs.append(
                _(f"Soyabean needs at least 40 mm rainfall. Current rainfall is {rainfall:.1f} mm. Use supplemental irrigation if needed.")
            )
        if season_lower == "kharif":
            recs.append(
                _("Sow at the onset of monsoon for best results. Practice weed management during early growth.")
            )
        recs.append(
            _("Apply phosphorus and potassium fertilizers at sowing. Use rhizobium inoculation for better nitrogen fixation.")
        )
        recs.append(
            _("Monitor for yellow mosaic virus and use resistant varieties.")
        )
        recs.append(
            _("Harvest when pods turn yellow and seeds rattle inside for maximum yield.")
        )

    # Season-based suggestions
    if season_lower == "summer" and temperature > 35:
        recs.append(
            _(f"High temperatures in Summer can stress {crop}. Use mulching, shade nets, and timely irrigation to reduce heat stress.")
        )

    # Soil health and fertilizer management
    if pH < 5.5:
        recs.append(
            _("Very acidic soil detected. Apply lime and organic matter to improve pH and nutrient availability.")
        )
    elif pH > 8.0:
        recs.append(
            _("Alkaline soil detected. Apply gypsum and organic compost to lower pH and enhance crop growth.")
        )

    # Yield comparison and improvement
    if area > 0 and predicted_yield < (production / area):
        recs.append(
            _(f"Your predicted yield ({predicted_yield:.2f} tons/hectare) is below your current average. Review fertilizer schedule, irrigation timing, and pest management for {crop}.")
        )
        recs.append(
            _("Consider soil testing and consult local agricultural experts for customized advice.")
        )

    # General best practices for maximum yield
    recs.append(
        _(f"Regularly monitor your {crop} field for weeds and pests, especially during the {season} season. Timely intervention can prevent yield loss.")
    )
    recs.append(
        _("Follow crop rotation and intercropping to maintain soil fertility and reduce pest pressure.")
    )
    recs.append(
        _("Keep records of all farm activities and inputs to track what works best for your field.")
    )

    return recs

# Loading all the models
working_dir = os.path.dirname(os.path.abspath(__file__))
crop_recom_model = pickle.load(open(f'{working_dir}/RF_Crop.sav', 'rb'))
crop_yield_model =joblib.load(open(f'{working_dir}/voting_yield.sav', 'rb'))


# Set background color
st.markdown(
    """
    <style>
        body {
            background-color: #f0f5f5;
        }
        .profile-pic {
            border-radius: 50%;
            width: 150px;
            height: 150px;
            object-fit: cover;
            margin-bottom: 10px;
        }
        .profile-column {
            text-align: center;
            padding: 20px;
        }
        .icon {
            width: 24px;
            height: 24px;
            margin: 0 5px;
        }
        .profile-name {
            font-size: 18px;
            font-weight: bold;
            margin-top: 10px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    options = [_("Home"), _("Crop Yield Prediction"), _("Crop Recommendation"), _("Meet the Creators")]
    selected = option_menu(_("Fasal Vikas"),
                           options,
                           menu_icon=":seedling:",
                           icons=["house", "tree", "tree", "people"],
                           default_index=0)

# Crop Recommendation
if selected == _("Crop Recommendation"):
    st.title(_("Crop Recommendation"))

    st.write(_("Provide the following information to get crop recommendations:"))
    st.write(_("""
    - **Nitrogen (N)**: Essential nutrient for plant growth.
    - **Phosphorus (P)**: Vital for root development and energy transfer.
    - **Potassium (K)**: Important for water regulation and disease resistance.
    - **pH Value**: Soil acidity or alkalinity level.
    - **Temperature (°C)**: Current temperature.
    - **Humidity (%)**: Moisture content in the air.
    - **Rainfall (mm)**: Amount of recent rainfall.
    """))

    N = st.number_input(_("Nitrogen (N)"), min_value=0, value=0)
    P = st.number_input(_("Phosphorus (P)"), min_value=0, value=0)
    K = st.number_input(_("Potassium (K)"), min_value=0, value=0)
    pH = st.number_input(_("pH Value"), min_value=0.0, max_value=14.0, value=0.0)
    temperature = st.number_input(_("Temperature (°C)"), min_value=0.0, value=0.0)
    humidity = st.number_input(_("Humidity (%)"), min_value=0.0, max_value=100.0, value=0.0)
    rainfall = st.number_input(_("Rainfall (mm)"), min_value=0.0, value=0.0)
    
    # if st.button(_("Recommend Crop")):
    #     crop_input = np.array([[N, P, K, pH, temperature, humidity, rainfall]])
        
    #     if all(crop_input[0][:3]):  # Check if N, P, K values are provided
    #         crop_recommendation = crop_recom_model.predict(crop_input)
    #         st.success(_(f"Recommended Crop: {crop_recommendation[0]}"))
    #     else:
    #         st.error(_("Please enter values for Nitrogen (N), Phosphorus (P), and Potassium (K)"))

# Crop Yield Prediction
elif selected == _("Crop Yield Prediction"):
    st.title(_("Crop Yield Prediction"))
    st.write("")
    st.markdown(_("""
### Using the Crop Yield Prediction Model

- **Select State**: Choose the state where the crop is being cultivated.
- **Select Crop**: Pick the specific crop for yield prediction.
- **Select Season**: Choose the appropriate growing season.
- **Input Soil pH**: Enter the soil pH level. [Measure pH at home](https://www.youtube.com/watch?v=mZgxUqoJMcg).
- **Input Rainfall**: Enter the rainfall amount (mm). [Check local rainfall](https://mausam.imd.gov.in/responsive/rainfallinformation.php).
- **Input Temperature**: Enter the average temperature (°C). [Check local temperature](https://www.accuweather.com/).
- **Input Area**: Enter the cultivation area (hectares).
- **Input Production**: Enter the total production (tons).
- **Click Predict**: Get the yield prediction.
### Interpreting Results

- Predicted yield is shown in tons per hectare.
- Use this data for crop management and planning.

Leverage machine learning for accurate crop yield predictions to enhance productivity and sustainability.
"""))

    states = ['Andaman and Nicobar Islands', 'Andhra Pradesh', 'Arunachal Pradesh', 'Assam', 'Bihar', 'Chandigarh', 'Chhattisgarh', 
              'Dadra and Nagar Haveli', 'Goa', 'Gujarat', 'Haryana', 'Himachal Pradesh', 
              'Jammu and Kashmir', 'Jharkhand', 'Karnataka', 'Kerala', 'Madhya Pradesh', 'Maharashtra', 
              'Manipur', 'Meghalaya', 'Mizoram', 'Nagaland', 'Odisha', 'Puducherry', 'Punjab', 
              'Rajasthan', 'Sikkim', 'Tamil Nadu', 'Telangana', 'Tripura', 'Uttar Pradesh', 
              'Uttarakhand', 'West Bengal']

    crops = ['Arecanut', 'Barley', 'Banana', 'Blackpepper', 'Brinjal', 'Cabbage', 'Cardamom', 'Cashewnuts', 'Cauliflower', 
             'Coriander', 'Cotton', 'Garlic', 'Grapes', 'Horsegram', 'Jowar', 'Jute', 'Ladyfinger', 'Maize', 
             'Mango', 'Moong', 'Onion', 'Orange', 'Papaya', 'Pineapple', 'Potato', 'Rapeseed', 'Ragi', 'Rice', 
             'Sesamum', 'Soyabean', 'Sunflower', 'Sweetpotato', 'Tapioca', 'Tomato', 'Turmeric', 'Wheat']

    seasons = ['Kharif', 'Rabi', 'Summer', 'Whole Year']

    state = st.selectbox(_("Select State"), states)
    crop = st.selectbox(_("Select Crop"), crops)
    season = st.selectbox(_("Select Season"), seasons)
    pH = st.number_input(_("Soil pH Value"), min_value=0.0, max_value=14.0, value=0.0)
    rainfall = st.number_input(_("Rainfall (mm)"), min_value=0.0, value=0.0)
    temperature = st.number_input(_("Temperature (°C)"), min_value=0.0, value=0.0)
    area = st.number_input(_("Area (hectares)"), min_value=0.0, value=0.0)
    production = st.number_input(_("Production (tons)"), min_value=0.0, value=0.0)

    if st.button(_("Predict Yield")):
        if state and crop and season and pH and rainfall and temperature and area and production:
            state_lower = state.lower()
            crop_lower = crop.lower()
            season_lower = season.lower()

            state_encoded = [0] * (len(states) - 1) if state_lower == 'andaman and nicobar islands' else [1 if s.lower() == state_lower else 0 for s in states if s.lower() != 'andaman and nicobar islands']
            crop_encoded = [0] * (len(crops) - 1) if crop_lower == 'arecanut' else [1 if c.lower() == crop_lower else 0 for c in crops if c.lower() != 'arecanut']
            season_encoded = [0] * (len(seasons) - 1) if season_lower == 'kharif' else [1 if s.lower() == season_lower else 0 for s in seasons if s.lower() != 'kharif']

            input_features = np.array(state_encoded + crop_encoded + season_encoded + [pH, rainfall, temperature, area, production]).reshape(1, -1)

            expected_num_features = len(states) + len(crops) + len(seasons) - 3 + 5

            if input_features.shape[1] != expected_num_features:
                st.error(_(f"Feature shape mismatch, expected: {expected_num_features}, got: {input_features.shape[1]}"))
            else:
                predicted_yield = crop_yield_model.predict(input_features)
                st.success(_(f'The predicted yield for the selected inputs is: {predicted_yield[0]:.2f} tons/hectare'))
                # Show tailored recommendations to improve yield
                recs = get_yield_recommendations(crop, area, season, pH, rainfall, temperature, production, predicted_yield[0])
                st.markdown(_("#### Recommendations to Improve Yield"))
                for r in recs:
                    st.info(r)
        else:
            st.error(_("Please enter all required values"))

# Meet Creators
elif selected == _("Meet the Creators"):
    st.title(_("Meet the Creators"))
    st.markdown("<br>", unsafe_allow_html=True)  # Adding space between the title and the profiles

    creators = [
        
        {
            "name": "Aaron Thomas",
            "linkedin": "https://www.linkedin.com/in/aaron-jthomas/",
            "github": "https://github.com/AayJayTee",
            "image": "images/aaron.jpg"
        },
        {
            "name": "Saumyaa Garg",
            "linkedin": "https://www.linkedin.com/in/saumyaa-garg/",
            "github": "https://github.com/saumyaagarg",
            "image": "images/saumyaa.jpg"
        },
        {
            "name": "Yati",
            "linkedin": "https://www.linkedin.com/in/yati21/",
            "github": "https://github.com/Yati-21",
            "image": "images/aaron.jpg"
        },
        {
            "name": "Ananya Gupta",
            "linkedin": "https://www.linkedin.com/in/ananya-gupta-513753258/",
            "github": "https://github.com/Ananyagupta1812",
            "image": "images/aaron.jpg"
        },
        {
            "name": "Chirag Dhooria",
            "linkedin": "https://www.linkedin.com/in/chirag-dhooria-324859305/",
            "github": "",
            "image": "images/aaron.jpg"
        },
        {
            "name": "Aanya Chauhan",
            "linkedin": "",
            "github": "",
            "image": "images/aaron.jpg"
        }
    ]

    # Display creators in two rows of three columns each
    for row_start in range(0, len(creators), 3):
        cols = st.columns(3)
        for i, creator in enumerate(creators[row_start:row_start+3]):
            with cols[i]:
                st.image(creator["image"], width=80, caption=None, use_container_width=True, output_format='auto')
                st.markdown(
                    f"<div class='profile-column'><p class='profile-name'>{_(creator['name'])}</p>"
                    f"<a href='{creator['linkedin']}'><img src='https://upload.wikimedia.org/wikipedia/commons/8/81/LinkedIn_icon.svg' class='icon'></a> "
                    f"<a href='{creator['github']}'><img src='https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png' class='icon'></a></div>",
                    unsafe_allow_html=True
                )

# Home
else:
    img = "hero2.jpg"
    st.title(_("Fasal Vikas"))
    st.write(_("##### Welcome to Fasal Vikas! Explore our tools in the sidebar to make informed agricultural decisions."))
    st.image(img, width=750)
    
    st.write("")  # Leave some space after the image
    st.write(_("### Overview"))  # Section title for introduction
    st.write(_("Fasal Vikas is an AI-powered platform designed to empower farmers with personalized crop recommendations and accurate yield predictions. By leveraging advanced machine learning models and real-time data, it helps optimize irrigation, fertilization, and pest management. The intuitive interface and actionable insights enable farmers to boost productivity, make informed decisions, and sustainably manage their agricultural practices."))
    st.write(_("### Find the Code at:"))
    st.write(_("Link: "))
    st.write(_("Made with 💖 by Saumyaa, Aaron, Yati, Ananya, Chirag, and Aanya"))