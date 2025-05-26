import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import openai

st.set_page_config(page_title="Website Audit AI Agent", layout="wide")
st.title("🔎 Website Audit AI Agent")
st.markdown("Carica un file Excel con una colonna 'Website'. L'app analizzerà il CMS e i contenuti testuali.")

openai_api_key = st.text_input("Inserisci la tua OpenAI API Key", type="password")

uploaded_file = st.file_uploader("Carica il tuo file Excel (.xlsx)", type=["xlsx"])

def extract_text_from_homepage(url):
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.content, "html.parser")
        for script in soup(["script", "style", "noscript"]):
            script.extract()
        text = ' '.join(soup.stripped_strings)
        return text[:4000]  # limita a 4000 caratteri per prompt
    except Exception as e:
        return f"Errore durante lo scraping: {e}"

def analyze_with_gpt(content, key):
    try:
        openai.api_key = key
        prompt = f"""
Analizza il seguente contenuto della homepage di un sito aziendale:

{content}

Fornisci:
1. Una valutazione sulla chiarezza della proposta di valore
2. Un commento sul tono di voce
3. Un giudizio sulla presenza e chiarezza delle CTA
4. 3 suggerimenti per migliorare il contenuto, anche dal punto di vista commerciale e semantico.
"""
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Errore analisi GPT: {e}"

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    if "Website" not in df.columns:
        st.error("Il file deve contenere una colonna 'Website'")
    else:
        st.success("File caricato correttamente!")
        st.dataframe(df)

        if openai_api_key and st.button("Avvia analisi"):
            results = []
            for index, row in df.iterrows():
                site = row["Website"]
                st.write(f"🔍 Analisi in corso per: {site}")
                homepage_text = extract_text_from_homepage(site)
                analysis = analyze_with_gpt(homepage_text, openai_api_key)
                results.append({
                    "Sito": site,
                    "Analisi GPT": analysis
                })

            result_df = pd.DataFrame(results)
            st.subheader("🧠 Risultati analisi GPT")
            st.dataframe(result_df)

            csv = result_df.to_csv(index=False).encode("utf-8")
            st.download_button("📥 Scarica il report CSV", data=csv, file_name="gpt_analysis_report.csv", mime="text/csv")