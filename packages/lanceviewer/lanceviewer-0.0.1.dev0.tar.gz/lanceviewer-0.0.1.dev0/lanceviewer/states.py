import streamlit as st


def widget_key(action, data):
    return f"form_{action}_on_{data}"


def init_states():
    st.session_state["URI"] = None
    st.session_state["table"] = None
    st.session_state["limit"] = None
    st.session_state["query"] = None
    st.session_state["query_result"] = None

def update_state(state, value):
    st.session_state[state] = value
