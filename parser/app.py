import streamlit as st
import requests

API_URL = "http://localhost:8000/v1/edi210/parse"

st.title("EDI 210 Parser Demo")

uploaded = st.file_uploader("Upload EDI 210 file", type=["edi", "txt"])

if uploaded:
    edi_text = uploaded.read().decode("utf-8")

    st.code(edi_text, language="text")

    if st.button("Parse EDI"):
        response = requests.post(
            API_URL,
            headers={"Content-Type": "text/plain"},
            data=edi_text
        )

        if response.status_code == 200:
            data = response.json()
            results = data["results"]
            warnings = data["warnings"]
            st.json(results)
            with st.sidebar:
                st.header("Warnings")
                for item in warnings:
                    st.write(item)
        else:
            st.error(f"Error: {response.text}")
