import streamlit as st
import pandas as pd



# Load data functions
def load_keywords():
    df = pd.read_excel('Keyword Identified.xlsx', sheet_name='KEYWORDS', header=None)
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

# Highlight function
def highlight_signal(signal,rx_df,tx_df):
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

# Page function
def show_keyword_details():
    # Load data
    df, keywords_dict, column_names = load_keywords()
    rx_df, tx_df = load_signals()

    # # Initialize the session state variable if not already set
    # if "testing_session" not in st.session_state:
    #     st.session_state.testing_session = ""

    # # Dropdown options
    # options = ["", "Option 1", "Option 2", "Option 3"]

    # # Dropdown for user selection
    # st.session_state.testing_session = st.selectbox(
    #     "Choose an option:",
    #     options,
    #     index=options.index(st.session_state.testing_session) if st.session_state.testing_session in options else 0,
    # )

    # # Display the selected value
    # if st.session_state.testing_session:
    #     st.write("You selected:", st.session_state.testing_session)


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

    # Initialize session state for selected signal
    if 'selected_signal' not in st.session_state:
        st.session_state.selected_signal = ""

    # Display DataFrame and keyword details
    st.dataframe(df)

    if "keyword_signal" not in st.session_state:
        st.session_state.keyword_signal = ""  # Default to empty selection

    signal_options = [""] + df['Signals'].dropna().unique().tolist()

    # Dropdown for selecting a signal
    st.session_state.keyword_signal = st.selectbox(
        "Select a signal:",
        signal_options,
        index=signal_options.index(st.session_state.keyword_signal)
        if st.session_state.keyword_signal in signal_options else 0)

    if(st.session_state.keyword_signal):
        st.write(f"Keyword details for: {st.session_state.keyword_signal}")
        st.dataframe(df[df['Signals'] == st.session_state.keyword_signal])

    # Save selected signal to session state
    # st.session_state.selected_signal = signal



    # Combine 'Object Content' and 'Associated Network Signal' for Rx and Tx
    # rx_signals = list(rx_df['Object Content'].unique()) + list(rx_df['Associated Network Signal'].unique())
    # tx_signals = list(tx_df['Object Content'].unique()) + list(tx_df['Associated Network Signal'].unique())
    # all_signals = [""] + rx_signals + tx_signals

    # # Option to select a signal related to the keyword
    # selected_signal = st.selectbox("Select a signal from CORE_CIL:", all_signals)
    # st.session_state.selected_signal = selected_signal



    # Button to view signal details
    if st.button("View Signal Details from CORE_CIL v27.1") and st.session_state.selected_signal:
        highlight_signal(st.session_state.selected_signal,rx_df,tx_df)
