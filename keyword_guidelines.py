import streamlit as st
import pandas as pd
import base64

def display_pdf(file_path):
    with open(file_path, 'rb') as pdf_file:
        pdf_data = pdf_file.read()
        base64_pdf = base64.b64encode(pdf_data).decode('utf-8')
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)

def show_keyword_guidelines():
    
    st.markdown("""
        <style>
        .gradient-text {
            background: linear-gradient(to right, #1e3c72, #2a5298, #53a0fd, #b0e0e6, #98fb98);
            -webkit-background-clip: text;
            color: transparent;
            font-size: 48px;
            font-weight: 700;
            font-family: 'Poppins', sans-serif;
            text-align: left;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2);
            margin-top: 20px;
        }
        </style>
        <h1 class="gradient-text">Keyword Guidelines</h1>
                <p1 class>View keyword guidelines below:</p1>
        
    """, unsafe_allow_html=True)
 
    # display_text_from_pdf()
    display_pdf('Keyword-Guidelines.pdf')