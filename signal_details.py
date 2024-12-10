import streamlit as st
import pandas as pd

def load_signals():
    rx_df = pd.read_excel('CORE_CIL_v27.1_09Feb2024 1.xlsx', sheet_name='Rx')
    tx_df = pd.read_excel('CORE_CIL_v27.1_09Feb2024 1.xlsx', sheet_name='Tx')
    return rx_df, tx_df


def show_signal_details():
    st.title("Signal Details")
    st.write("View RX and TX signal details below.")
    

    # Load signal data
    rx_df, tx_df = load_signals()
    if rx_df is None or tx_df is None:
        return  # Exit if there's an error loading signals
 
    # Display the signal data
    st.write("Rx Signals:")
    st.write(rx_df)
 
    st.write("Tx Signals:")
    st.write(tx_df)