import streamlit as st
import pandas as pd

st.set_page_config(page_title="Website Audit AI Agent", layout="wide")

st.title("🔎 Website Audit AI Agent")
st.markdown("Carica un file Excel con l'elenco delle aziende e i rispettivi siti web.")

uploaded_file = st.file_uploader("Carica il tuo file Excel (.xlsx)", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    if "Website" not in df.columns:
        st.error("Il file deve contenere una colonna 'Website'")
    else:
        st.success("File caricato correttamente!")
        st.dataframe(df)

        if st.button("Avvia analisi"):
            results = []
            for index, row in df.iterrows():
                site = row["Website"]
                # Simula analisi (qui potrai integrare i tuoi moduli)
                results.append({
                    "Sito": site,
                    "CMS": "WordPress (esempio)",
                    "Suggerimenti": "Migliorare la chiarezza della CTA (esempio)"
                })
            result_df = pd.DataFrame(results)
            st.subheader("Risultati dell'analisi")
            st.dataframe(result_df)

            csv = result_df.to_csv(index=False).encode("utf-8")
            st.download_button("📥 Scarica il report CSV", data=csv, file_name="report.csv", mime="text/csv")