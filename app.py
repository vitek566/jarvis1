import streamlit as st
import google.generativeai as genai
from PIL import Image
import pypdf

st.set_page_config(page_title="AI Studijní Asistent", page_icon="⚡", layout="wide")
st.title("⚡ AI Studijní Asistent – Zkoušení a 5-minutovky")

# Kontrola API klíče v Secrets
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    
    try:
        # Použití univerzálního aliasu pro maximální stabilitu bez chyb 404
        model = genai.GenerativeModel("gemini-flash-latest")
    except Exception as e:
        st.error(f"Chyba při inicializaci modelu: {e}")

    # Nahrání souboru
    uploaded_file = st.file_uploader("Nahraj studijní materiál (PDF, PNG, JPG)", type=["png", "jpg", "jpeg", "pdf"])

    if uploaded_file is not None:
        file_data = None
        
        # Zpracování PDF nebo obrázku
        if uploaded_file.type == "application/pdf":
            try:
                reader = pypdf.PdfReader(uploaded_file)
                text_data = ""
                
                # Omezení na prvních 10 stran pro rychlé zpracování (řeší zasekávání)
                max_pages = min(len(reader.pages), 10)
                for i in range(max_pages):
                    text_data += reader.pages[i].extract_text() or ""
                
                if text_data.strip():
                    file_data = text_data
                    st.success(f"PDF úspěšně přečteno (zpracováno {max_pages} z {len(reader.pages)} stran).")
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

        # Inicializace chatu v session state, pokud ještě neexistuje
        if "chat_session" not in st.session_state:
            st.session_state.chat = None
        if "messages" not in st.session_state:
            st.session_state.messages = []

        # Tlačítko pro spuštění vygenerování 5-minutovky
        if file_data and st.button("🚀 Vygenerovat 5-minutovku a spustit chat"):
            with st.spinner("AI připravuje test a analyzuje materiál... (trvá 2-3 sekundy)"):
                try:
                    prompt = (
                        "Jsi efektivní studijní asistent. "
                        "Vezmi přiložený materiál a vypiš: "
                        "1. 3 klíčové pojmy k naučení. "
                        "2. 3 zkušební otázky na ověření znalostí včetně odpovědí. "
                        "Jdi rovnou k věci."
                    )
                    
                    # Vytvoříme novou chat session s materiálem v kontextu
                    chat = model.start_chat(history=[])
                    st.session_state.chat = chat
                    st.session_state.messages = [] # reset historie pro nový soubor
                    
                    # Odeslání prvotního pokynu s daty
                    response = chat.send_message([prompt, file_data])
                    
                    # Uložení do historie zpráv
                    st.session_state.messages.append({"role": "user", "content": "Vygeneruj 5-minutovku z materiálu."})
                    st.session_state.messages.append({"role": "model", "content": response.text})
                    
                except Exception as e:
                    st.error(f"Chyba při komunikaci s Gemini API: {e}")

        # Pokud již proběhla inicializace chatu, zobrazíme interaktivní konverzaci
        if st.session_state.get("chat_session") is not None:
            st.markdown("---")
            st.subheader("💬 Interaktivní zkoušení a doplňující dotazy")
            
            # Zobrazení dosavadní historie zpráv
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])
            
            # Chatové okno dole
            if user_input := st.chat_input("Zeptej se na cokoliv z materiálu nebo požádej o vyzkoušení..."):
                st.session_state.messages.append({"role": "user", "content": user_input})
                with st.chat_message("user"):
                    st.markdown(user_input)
                    
                with st.chat_message("model"):
                    with st.spinner("AI přemýšlí..."):
                        try:
                            response = st.session_state.chat.send_message(user_input)
                            st.markdown(response.text)
                            st.session_state.messages.append({"role": "model", "content": response.text})
                        except Exception as e:
                            st.error(f"Chyba v chatu: {e}")
else:
    st.warning("V aplikaci není nastaven API klíč. Zkontroluj si nastavení v Secrets ve Streamlitu.")
