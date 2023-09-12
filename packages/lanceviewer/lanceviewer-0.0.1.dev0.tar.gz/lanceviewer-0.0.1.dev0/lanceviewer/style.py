import streamlit as st

def set_style():
    st.set_page_config(layout="wide", initial_sidebar_state="collapsed")
    st.markdown("""
        <style>
               .block-container {
                    padding-top: 1rem;
                    padding-bottom: 0rem;
                    padding-left: 5rem;
                    padding-right: 5rem;
                }
                [data-testid="stForm"] {border: 0px}
        </style>
        """, unsafe_allow_html=True)