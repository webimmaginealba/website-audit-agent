import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import openai
import builtwith

st.set_page_config(page_title="Website Audit AI Agent", layout="wide")
st.title("🔎 Website Audit AI Agent - Analisi avanzata")

# OpenAI API Key input
openai_api_key = st.text_input("🔑 Inserisci la tua OpenAI API Key", type="password")

# Model selection
model_choice = st.selectbox("🧠 Seleziona il modello GPT", ["gpt-3.5-turbo", "gpt-4-0125-preview"])

# Predefined prompts
prompt_options = {
    "🔍 Analisi generale B2B": "Valuta la chiarezza della proposta, il tono di voce, le CTA e suggerisci miglioramenti concreti per un sito B2B.",
    "🛒 E-commerce": "Analizza l'efficacia del sito nel guidare l'acquisto, chiarezza delle offerte e punti di fiducia per il cliente.",
    "🧠 Posizionamento e branding": "Valuta la coerenza tra messaggio, contenuti e identità percepita del brand. Suggerisci 3 miglioramenti per rafforzare il posizionamento."
}
selected_prompt = st.selectbox("📋 Seleziona un prompt predefinito (modificabile)", list(prompt_options.values()))
custom_prompt = st.text_area("✍️ Oppure scrivi un prompt personalizzato", value=selected_prompt)

# File uploader
uploaded_file = st.file_uploader("📂 Carica il tuo file Excel (.xlsx) con una colonna 'Website'", type=["xlsx"])

# Functions
def extract_text_from_homepage(url):
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.content, "html.parser")
        for script in soup(["script", "style", "noscript"]):
            script.extract()
        text = ' '.join(soup.stripped_strings)
        return text[:4000]
    except Exception as e:
        return f"Errore scraping: {e}"

def detect_technologies(url):
    try:
        tech = builtwith.parse(url)
        return ', '.join([f"{k}: {', '.join(v)}" for k, v in tech.items()])
    except Exception as e:
        return f"Errore CMS/tech: {e}"

def check_compliance(url):
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.content, "html.parser")
        links = [a.get("href", "").lower() for a in soup.find_all("a")]
        cookies = any("cookie" in link for link in links)
        privacy = any("privacy" in link for link in links)
        return f"Privacy: {'✅' if privacy else '❌'}, Cookie Policy: {'✅' if cookies else '❌'}"
    except Exception as e:
        return f"Errore compliance: {e}"

def analyze_with_gpt(text, prompt, key, model):
    try:
        openai.api_key = key
        full_prompt = f"{prompt}\n\nContenuto da analizzare:\n{text}"
        response = openai.ChatCompletion.create(
            model=model,
            messages=[{"role": "user", "content": full_prompt}],
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Errore GPT: {e}"

# Processing
if uploaded_file:
    df = pd.read_excel(uploaded_file)

    if "Website" not in df.columns:
        st.error("❗ Il file deve contenere una colonna 'Website'")
    else:
        st.success("✅ File caricato correttamente")
        st.dataframe(df)

        selected_sites = st.multiselect("🔘 Seleziona i siti da analizzare", df["Website"].tolist())

        if openai_api_key and selected_sites and st.button("🚀 Avvia analisi"):
            results = []

            for site in selected_sites:
                st.write(f"🔍 Analisi in corso per: {site}")
                homepage_text = extract_text_from_homepage(site)
                tech_info = detect_technologies(site)
                compliance_info = check_compliance(site)
                gpt_output = analyze_with_gpt(homepage_text, custom_prompt, openai_api_key, model_choice)

                results.append({
                    "Sito": site,
                    "Tecnologie": tech_info,
                    "Compliance": compliance_info,
                    "Analisi GPT": gpt_output
                })

            result_df = pd.DataFrame(results)
            st.subheader("📊 Risultati completi")
            st.dataframe(result_df)

            csv = result_df.to_csv(index=False).encode("utf-8")
            st.download_button("📥 Scarica il report CSV", data=csv, file_name="website_audit_report.csv", mime="text/csv")