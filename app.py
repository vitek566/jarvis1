import streamlit as st
import google.generativeai as genai
from PIL import Image
import pypdf

st.set_page_config(page_title="AI Studijní Asistent", page_icon="⚡", layout="wide")
st.title("⚡ AI Studijní Asistent – Rychlý test")

# Kontrola klíče v Secrets
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    
    try:
        # Stabilní a rychlý model pro bezplatné API
        model = genai.GenerativeModel("gemini-1.5-flash")
    except Exception as e:
        st.error(f"Chyba při inicializaci modelu: {e}")

    uploaded_file = st.file_uploader("Nahraj studijní materiál (PDF, PNG, JPG)", type=["png", "jpg", "jpeg", "pdf"])

    if uploaded_file is not None:
        file_data = None
        
        # Zpracování PDF nebo obrázku
        if uploaded_file.type == "application/pdf":
            try:
                reader = pypdf.PdfReader(uploaded_file)
                text_data = ""
                for page in reader.pages:
                    text_data += page.extract_text() or ""
                
                if text_data.strip():
                    file_data = text_data
                    st.success(f"PDF úspěšně přečteno ({len(reader.pages)} stran).")
                else:
                    st.error("PDF neobsahuje text (je to pravděpodobně naskenovaný obrázek).")
            except Exception as e:
                st.error(f"Chyba při čtení PDF: {e}")
        else:
            try:
                file_data = Image.open(uploaded_file)
                st.image(file_data, caption="Nahraný obrázek", use_container_width=True)
            except Exception as e:
                st.error(f"Chyba při načítání obrázku: {e}")

        # Tlačítko pro spuštění generování
        if file_data and st.button("🚀 Vygenerovat 5-minutovku"):
            with st.spinner("AI pročesává materiály... (trvá to cca 2 vteřiny)"):
                try:
                    prompt = (
                        "Jsi efektivní studijní asistent. "
                        "Vezmi přiložený materiál a vypiš: "
                        "1. 3 klíčové pojmy k naučení. "
                        "2. 3 zkušební otázky na ověření znalostí včetně odpovědí. "
                        "Jdi rovnou k věci."
                    )
                    
                    response = model.generate_content([prompt, file_data])
                    
                    st.subheader("📝 Výsledek od AI:")
                    st.markdown(response.text)
                    
                except Exception as e:
                    st.error(f"Chyba při komunikaci s Gemini API: {e}")
else:
    st.warning("V aplikaci není nastaven API klíč. Zkontroluj si nastavení v Secrets ve Streamlitu.")
