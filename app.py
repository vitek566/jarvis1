import streamlit as st
import google.generativeai as genai
from PIL import Image
import pypdf

# Nastavení vzhledu stránky
st.set_page_config(page_title="AI Studijní Asistent Pro", page_icon="🎓", layout="wide")
st.title("🎓 AI Studijní Asistent s chatem a PDF")
st.write("Nahraj fotku nebo PDF skriptů, vygeneruj bleskovou 5-minutovku a pak se dál zeptej v chatu nebo se nech vyzkoušet!")

# Načtení klíče ze zabezpečeného úložiště Streamlitu
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    # Aktualizovaný model podle chybové hlášky od Googlu
    model = genai.GenerativeModel("gemini-3.8-flash")

    # Inicializace stavu chatu
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "extracted_data" not in st.session_state:
        st.session_state.extracted_data = None
    if "chat_session" not in st.session_state:
        st.session_state.chat_session = None

    # Nahrání souboru (podpora obrázků i PDF)
    uploaded_file = st.file_uploader("Nahraj studijní materiály (PDF, PNG, JPG)", type=["png", "jpg", "jpeg", "pdf"])

    file_content = None
    file_type = None

    if uploaded_file is not None:
        if uploaded_file.type == "application/pdf":
            file_type = "pdf"
            reader = pypdf.PdfReader(uploaded_file)
            text_data = ""
            for page in reader.pages:
                text_data += page.extract_text() or ""
            file_content = text_data
            st.success(f"Úspěšně načteno PDF ({len(reader.pages)} stran)")
        else:
            file_type = "image"
            file_content = Image.open(uploaded_file)
            st.image(file_content, caption="Nahrané poznámky", use_container_width=True)

        # Tlačítko pro generování testu
        if st.button("🚀 Vygenerovat 5-minutovku"):
            with st.spinner("AI zpracovává materiál a připravuje tahák..."):
                try:
                    prompt = (
                        "Jsi nemilosrdně efektivní studijní asistent. "
                        "Vezmi přiložený materiál, ignoruj veškerou vatu a vypiš pouze: "
                        "1. 3 klíčové pojmy, které je nutné umět nazpaměť. "
                        "2. 3 rychlé zkušební otázky na ověření znalostí (včetně správných odpovědí schovaných níže). "
                        "Jdi rovnou k věci."
                    )
                    
                    response = model.generate_content([prompt, file_content])
                    st.session_state.extracted_data = response.text
                    
                    # Spuštění kontextového chatu pro zkoušení
                    st.session_state.chat_session = model.start_chat(history=[])
                    st.session_state.chat_session.send_message(
                        f"Tohle jsou studijní materiály studenta:\n{file_content if file_type=='pdf' else '[Obrázek poznámek]'}\n"
                        f"Zde je vygenerovaný úvodní test: {response.text}\n"
                        "Nyní budeme vést konverzaci. Pomáhej studentovi s učením, zkoušej ho na test, vymýšlej doplňující otázky nebo vysvětluj nejasnosti."
                    )
                    
                    st.success("Materiál je připraven! Níže najdeš test a můžeš začít chatovat.")
                except Exception as e:
                    st.error(f"Došlo k chybě: {e}")

    # Pokud už máme vygenerovaný obsah, zobrazíme test a chatovací okno
    if st.session_state.extracted_data:
        st.markdown("---")
        st.subheader("📝 Vygenerovaný tahák a 5-minutovka")
        st.markdown(st.session_state.extracted_data)
        
        st.markdown("---")
        st.subheader("💬 Interaktivní chat & zkoušení s AI")
        st.write("Zeptej se na cokoliv z materiálů, požádej o vysvětlení nebo napiš např.: *'Vyzkoušej mě z toho formou testu'*, *'Ptej se mě na otázky jednu po druhé'*.")

        # Zobrazení historie chatu
        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Vstup pro uživatele v chatu
        if user_input := st.chat_input("Napiš zprávu AI (např. 'Pojď mě vyzkoušet')..."):
            st.session_state.chat_history.append({"role": "user", "content": user_input})
            with st.chat_message("user"):
                st.markdown(user_input)

            with st.chat_message("assistant"):
                with st.spinner("AI přemýšlí..."):
                    try:
                        if st.session_state.chat_session:
                            response = st.session_state.chat_session.send_message(user_input)
                            bot_reply = response.text
                        else:
                            bot_reply = "Nejprve prosím nahraj materiál nahoře."
                        st.markdown(bot_reply)
                        st.session_state.chat_history.append({"role": "assistant", "content": bot_reply})
                    except Exception as e:
                        st.error(f"Chyba v chatu: {e}")
else:
    st.warning("V aplikaci není nastaven API klíč. Nastav ho prosím v administraci Streamlitu (Secrets).")
