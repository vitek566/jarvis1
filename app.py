import streamlit as st
import google.generativeai as genai
from PIL import Image

st.set_page_config(page_title="Rychlá 5-minutovka", page_icon="⚡")
st.title("⚡ Rychlý AI Studijní Asistent")
st.write("Nahraj fotku poznámek a získej okamžitou 5-minutovku bez zbytečné vaty!")

# Načtení klíče ze zabezpečeného úložiště Streamlitu
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel("gemini-1.5-flash")

    uploaded_file = st.file_uploader("Nahraj fotku sešitu nebo poznámek (PNG, JPG)", type=["png", "jpg", "jpeg"])

    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Nahrané poznámky", use_container_width=True)
        
        if st.button("Vygenerovat 5-minutovku před testem"):
            with st.spinner("AI pročesává poznámky a vybírá to nejdůležitější..."):
                try:
                    prompt = (
                        "Jsi nemilosrdně efektivní studijní asistent. "
                        "Vezmi přiložené poznámky, ignoruj veškerou vatu a vypiš pouze: "
                        "1. 3 klíčové pojmy, které je nutné umět nazpaměť. "
                        "2. 3 rychlé zkušební otázky na ověření znalostí (včetně správných odpovědí schovaných níže). "
                        "Jdi rovnou k věci, žádné zbytečné úvody."
                    )
                    
                    response = model.generate_content([prompt, image])
                    
                    st.success("Hotovo! Zde je tvůj tahák k úspěchu:")
                    st.markdown(response.text)
                    
                except Exception as e:
                    st.error(f"Došlo k chybě při zpracování: {e}")
else:
    st.warning("V aplikaci není nastaven API klíč. Zadej ho v administraci Streamlitu (Secrets).")