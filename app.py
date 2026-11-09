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
        # Stabilní model pro bezproblémové API
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
                
                # Omezení na prvních 10 stran pro maximální rychlost
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

        # Inicializace stavu chatu v session
        if "messages" not in st.session_state:
            st.session_state.messages = []
        if "material_cache" not in st.session_state:
            st.session_state.material_cache = None

        # Uložíme si data materiálu do paměti relace
        if file_data:
            st.session_state.material_cache = file_data

        # Tlačítko pro spuštění vygenerování 5-minutovky (používá přímé volání bez timeoutu)
        if st.session_state.material_cache and st.button("🚀 Vygenerovat 5-minutovku"):
            with st.spinner("AI připravuje test... (trvá 2-3 sekundy)"):
                try:
                    prompt = (
                        "Jsi efektivní studijní asistent. "
                        "Vezmi přiložený materiál a vypiš: "
                        "1. 3 klíčové pojmy k naučení. "
                        "2. 3 zkušební otázky na ověření znalostí včetně odpovědí. "
                        "Jdi rovnou k věci."
                    )
                    
                    # Přímé vygenerování odpovědi (vyhýbá se chybám start_chat)
                    response = model.generate_content([prompt, st.session_state.material_cache])
                    
                    # Uložení do historie zpráv
                    st.session_state.messages = [
                        {"role": "user", "content": "Vygeneruj 5-minutovku z nahraného materiálu."},
                        {"role": "assistant", "content": response.text}
                    ]
                    
                except Exception as e:
                    st.error(f"Chyba při komunikaci s Gemini API: {e}")

        # Zobrazení historie konverzace a doplňujícího chatu
        if st.session_state.messages:
            st.markdown("---")
            st.subheader("💬 Výsledek a interaktivní zkoušení")
            
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])
            
            # Doplňující otázky
            if user_input := st.chat_input("Zeptej se na cokoliv z materiálu..."):
                st.session_state.messages.append({"role": "user", "content": user_input})
                with st.chat_message("user"):
                    st.markdown(user_input)
                    
                with st.chat_message("assistant"):
                    with st.spinner("AI přemýšlí..."):
                        try:
                            # Sestavíme kontext z historie pro navazující dotaz
                            full_prompt = [
                                "Tady je studijní materiál, o kterém se bavíme:",
                                st.session_state.material_cache,
                                "Historie konverzace:"
                            ]
                            for m in st.session_state.messages:
                                full_prompt.append(f"{m['role']}: {m['content']}")
                            
                            response = model.generate_content(full_prompt)
                            st.markdown(response.text)
                            st.session_state.messages.append({"role": "assistant", "content": response.text})
                        except Exception as e:
                            st.error(f"Chyba v chatu: {e}")
else:
    st.warning("V aplikaci není nastaven API klíč. Zkontroluj si nastavení v Secrets ve Streamlitu.")
