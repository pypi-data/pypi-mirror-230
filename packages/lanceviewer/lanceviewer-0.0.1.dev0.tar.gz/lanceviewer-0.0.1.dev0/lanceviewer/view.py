import subprocess
import streamlit as st
from lanceviewer.states import update_state, init_states
from lanceviewer.settings import get_transforms
from lanceviewer.style import set_style
from lanceviewer.table_utils import load_dataset, run_sql_query, get_column_config, apply_transforms

def table_uri_form():
    with st.form("uri_form"):
        subcol1, subcol2, subcol3 = st.columns([0.7, 0.1, 0.2])
        with subcol1:
            url = st.text_input("uri", value="Table URI", label_visibility="collapsed")
        with subcol2:
            submit = st.form_submit_button("Submit")
        with subcol3:
            subcol1, subcol2 = st.columns([0.5, 0.5])
            with subcol1:
                limit_enabled = st.toggle("Limit", value=False)
            with subcol2:
                limit = st.number_input("limit", value=100, min_value=1, step=1, key="limit_key", label_visibility="collapsed")
        if submit:
            if url:
                init_states() # Always reset to original state when new URI is submitted
                update_state("URI", url)
                update_state("table", load_dataset(url))
                update_state("limit", limit) if limit_enabled else None
                st.experimental_rerun()

def query_form():
    with st.form("query_form"):
        subcol1, subcol2 = st.columns([0.8, 0.20])
        with subcol1:
            query = st.text_input("query", value="SQL", label_visibility="collapsed", disabled=st.session_state.get("table") is None)
        with subcol2:
            submit = st.form_submit_button("Submit")
        if submit:
            if query and st.session_state.get("table"):
                update_state("query", query)
                update_state("query_result", run_sql_query(st.session_state.get("table"), query, limit=st.session_state.get("limit")))
                st.experimental_rerun()


#### LAYOUT ####
def layout():
    IS_INIT_STATE = st.session_state.get("URI") is None
    if IS_INIT_STATE:
        init_states()
    set_style()
    table_uri_form()
    query_form()
    df = None
    if st.session_state.get("query_result") is not None:
        df = st.session_state.get("query_result")
    elif st.session_state.get("table"):
        df = st.session_state.get("table").to_table(limit=st.session_state.get("limit")).to_pandas()
    
    if df is not None:
        transforms = get_transforms()
        df = apply_transforms(df, transforms)
        column_config = get_column_config(transforms)
        st.dataframe(data=df, use_container_width=True, column_config=column_config)


def launch():
    cmd = ["streamlit", "run", __file__, "--server.maxMessageSize", "4096"] # port MessageSize is hardcoded
    try:
        subprocess.run(cmd, check=True)
    except Exception as e:
        print(e)


if __name__ == "__main__":
    layout()
