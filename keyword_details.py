import streamlit as st
import pandas as pd


# Load data functions
def load_keywords():
    df = pd.read_excel("Keyword Identified (2).xlsx", sheet_name='KEYWORDS', header=None)
    column_names = df.iloc[6].tolist()
    df = df.iloc[7:].reset_index(drop=True)
    df.dropna(subset=[df.columns[1]], inplace=True)
    df.columns = column_names
    keywords_dict = df.set_index(df.columns[1]).T.to_dict('list')
    return df, keywords_dict, column_names
 
def load_signals():
    rx_df = pd.read_excel('CORE_CIL_v27.1_09Feb2024 1.xlsx', sheet_name='Rx')
    tx_df = pd.read_excel('CORE_CIL_v27.1_09Feb2024 1.xlsx', sheet_name='Tx')
    return rx_df, tx_df
 
# Page function
def show_keyword_details():
    # Load data
    df, keywords_dict, column_names = load_keywords()
    rx_df, tx_df = load_signals()
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
<h1 class="gradient-text">Keyword Details</h1>
    """, unsafe_allow_html=True)
 
    st.write("Here you can see the details of all the keywords identified.")
    st.write("Click on a signal to view its details.")
    keyword_click = st.dataframe(df)
 
    # Ensure 'Keyword' is the correct column name in your DataFrame (df)
    signal = st.selectbox("Select a signal:", df['Signals'].dropna().unique())
 
    # Display the details of the selected signal
    st.write(f"Keyword details for: {signal}")
 
    # Filter and display the rows that match the selected signal
    st.dataframe(df[df['Signals'] == signal])
 
    # Combine 'Object Content' and 'Associated Network Signal' for both 'Rx' and 'Tx'
    rx_signals = list(rx_df['Object Content'].unique()) + list(rx_df['Associated Network Signal'].unique())
    tx_signals = list(tx_df['Object Content'].unique()) + list(tx_df['Associated Network Signal'].unique())
    all_signals = [""] + rx_signals + tx_signals
 
    # Option to select a signal related to the keyword
    signal = st.selectbox("Select a signal:", all_signals)
 
    # Function to check if the signal is in Rx or Tx sheet and highlight it
    def highlight_signal(signal):
        if signal in rx_df['Object Content'].values:
            st.write(f"Signal found in Rx sheet under 'Object Content': {signal}")
            st.dataframe(rx_df[rx_df['Object Content'] == signal])
        elif signal in rx_df['Associated Network Signal'].values:
            st.write(f"Signal found in Rx sheet under 'Associated Network Signal': {signal}")
            st.dataframe(rx_df[rx_df['Associated Network Signal'] == signal])
        elif signal in tx_df['Object Content'].values:
            st.write(f"Signal found in Tx sheet under 'Object Content': {signal}")
            st.dataframe(tx_df[tx_df['Object Content'] == signal])
        elif signal in tx_df['Associated Network Signal'].values:
            st.write(f"Signal found in Tx sheet under 'Associated Network Signal': {signal}")
            st.dataframe(tx_df[tx_df['Associated Network Signal'] == signal])
        else:
            st.write("Signal not found in either sheet.")
    # When the button is pressed, check and highlight the signal
    if st.button("View Signal Details from CORE_CIL v27.1") and signal:
        st.session_state.selected_signal = signal
        highlight_signal(signal)  # Highlight the signal

