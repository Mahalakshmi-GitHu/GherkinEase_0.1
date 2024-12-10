import streamlit as st
from gherkin_scenario_builder import show_gherkin_scenario_builder
from keyword_details import show_keyword_details
from signal_details import show_signal_details
from gherkin_guidelines import show_gherkin_guidelines
from keyword_guidelines import show_keyword_guidelines


st.set_page_config(
    layout="wide",
    page_title="GherkinEase",
    page_icon="GE_logo.png"
)
# Custom CSS to reduce zoom to 75%
zoom_css = """
    <style>
        body {
            zoom: 82%;
        }
    </style>
"""
st.markdown(zoom_css, unsafe_allow_html=True)

# CSS for background and logo positioning
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(to right, #e5e5e0, #f2f2eb);
        color: black;
    }
    .top-right-logo {
        position: absolute;
        top: 0;
        right: 0;
        margin: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# Custom CSS to style the buttons and sidebar
st.markdown("""
    <style>
    .stButton button {
        background-color: #a9bbc8;
        color: black;
        border: none;
        padding: 10px 22px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 28px;
        margin: 4px 2px;
        transition-duration: 0.4s;
        cursor: pointer;
        border-radius: 12px;
    }
 
    .stButton button:hover {
        background-color: #0096c7;
        color: white;
    }
 
    /* Changing the sidebar background color */
    .css-1d391kg {
        background-color: #2b2e4a !important;  /* Ensure that background color is applied */
    }
    .css-1d391kg .css-1v3fvcr {
        background-color: #2b2e4a !important;
    }
 
    /* New approach for the sidebar: target more generic selectors */
    section[data-testid="stSidebar"] > div {
        background-color: #2b2e4a !important;
    }
 
    /* Padding adjustments for sidebar content */
    .css-18e3th9 {
        padding: 16px;
    }
    </style>
""", unsafe_allow_html=True)

def display_home():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@700&display=swap');
   
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
    <h1 class="gradient-text">Welcome to GherkinEase!</h1>
""", unsafe_allow_html=True)
 
    st.write("""
    ### How to Use GherkinEase
 
    1. **Select a Menu Option**:
    - Use the sidebar to navigate through the different sections of the tool:
        - **Gherkin Scenario**: Build and download your Gherkin scenarios.
        - **Keyword Details**: Explore and select predefined keywords.
        - **Signal Details**: View and select Rx and Tx signals for your scenarios.
        - **Gherkin Guidelines**: Learn best practices for writing Gherkin scenarios.
        - **Keyword Guidelines**: Get guidance on using keywords in your scenarios.
 
    2. **Building Gherkin Scenarios**:
    - Choose **DC** or **SC** scenario types from the Gherkin Scenario tab.
    - You can input multiple `Given`, `When`, and `Then` statements.
    - Autocorrect will help refine your input as you type.
    - You can also select predefined keywords from the dropdown for easier scenario building.
    - Generate the scenario and review the output in real time.
    - Add example tables if applicable, and define column names based on the tags you include in your scenario.
 
    3. **Keyword and Signal Details**:
    - In the **Keyword Details** section, you can view a list of available keywords to include in your scenarios.
    - In the **Signal Details** section, explore Rx and Tx signals extracted from the CORE_CIL Excel sheet and use them to enhance your Gherkin scenarios.
 
    4. **Download Scenarios**:
    - After creating your scenario, you can download it as a `.txt` file, including any example tables you have added.
    - Simply click the download button, and you will receive a file that you can share with your team.
 
    5. **Guidelines**:
    - Review the **Gherkin Guidelines** and **Keyword Guidelines** for detailed instructions and tips to ensure you're following the best practices when writing Gherkin scenarios.
 
    ### General Tips
    - Use the **Keyword Details** and **Signal Details** sections to find the right keywords and signals to ensure accuracy in your scenarios.
    - Ensure that your `Given`, `When`, and `Then` statements are concise and follow the structure of BDD scenarios.
    - When building complex scenarios, feel free to add multiple `And` statements to extend the flow.
    - Always review the autocorrected input suggestions to maintain clarity in your scenario writing.
    """)

# Initialize session state for navigation
if "selected_page" not in st.session_state:
    st.session_state.selected_page = "🏠 Home"

# Sidebar menu buttons
st.sidebar.title("Menu")
if st.sidebar.button("🏠 Home"):
    st.session_state.selected_page = "🏠 Home"

if st.sidebar.button("📝 Gherkin Scenario Builder"):
    st.session_state.selected_page = "📝 Gherkin Scenario Builder"

if st.sidebar.button("🔑 Keyword Details"):
    st.session_state.selected_page = "🔑 Keyword Details"

if st.sidebar.button("📡 Signal Details"):
    st.session_state.selected_page = "📡 Signal Details"

if st.sidebar.button("📘 Gherkin Guidelines"):
    st.session_state.selected_page = "📘 Gherkin Guidelines"

if st.sidebar.button("🔍 Keyword Guidelines"):
    st.session_state.selected_page = "🔍 Keyword Guidelines"

# Navigation logic based on selected page
if st.session_state.selected_page == "🏠 Home":
    display_home()

elif st.session_state.selected_page == "📝 Gherkin Scenario Builder":
    show_gherkin_scenario_builder()

elif st.session_state.selected_page == "🔑 Keyword Details":
    show_keyword_details()

elif st.session_state.selected_page == "📡 Signal Details":
    show_signal_details()

elif st.session_state.selected_page == "📘 Gherkin Guidelines":
    show_gherkin_guidelines()

elif st.session_state.selected_page == "🔍 Keyword Guidelines":
    show_keyword_guidelines()
