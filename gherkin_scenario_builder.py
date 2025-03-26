import base64
import streamlit as st
import pandas as pd
import re
from autocorrect import Speller
import json
import os

# Core Functions (Unchanged)
def load_keywords():
    try:
        df = pd.read_excel('Keyword Identified (2).xlsx', sheet_name='KEYWORDS', header=None)
        column_names = df.iloc[6].tolist()
        df = df.iloc[7:].reset_index(drop=True)
        df.dropna(subset=[df.columns[8]], inplace=True)
        df.columns = column_names
        keywords_dict = df.set_index(df.columns[8]).T.to_dict('list')
        return df, keywords_dict, column_names
    except Exception as e:
        st.error(f"Error loading keywords: {e}")
        return None, None, None

df, keywords_dict, column_names = load_keywords()

def format_gherkin_statement(keyword, statement):
    statement = statement.strip()
    return f"{keyword} {statement}"

def download_link(content, filename, link_text):
    b64 = base64.b64encode(content.encode()).decode()
    return f'<a href="data:file/txt;base64,{b64}" download="{filename}">{link_text}</a>'

def format_example_table(rows):
    column_widths = [max(len(str(item or "")) for item in col) for col in zip(*rows)]
    formatted_rows = []
    for row in rows:
        formatted_row = "|".join([f"{str(item or '').strip().ljust(width)}" for item, width in zip(row, column_widths)])
        formatted_rows.append(f"|{formatted_row}|")
    return formatted_rows

def generate_download_content(gherkin_scenario, example_df=None):
    content = gherkin_scenario
    if example_df is not None and not example_df.empty:
        content += "\nExamples:\n"
        example_data = [example_df.columns.tolist()] + example_df.values.tolist()
        formatted_table = format_example_table(example_data)
        content += "\n".join(formatted_table)
    return content

def autocorrect_input(input_text):
    if not isinstance(input_text, str):
        return ""
    spell = Speller(lang='en')
    return spell(input_text)

# New Phase 2 Functions
def save_scenarios(scenario_name, scenarios_dict):
    try:
        json_data = {}
        for key, content in scenarios_dict.items():
            filename = f"{scenario_name}_{key}.txt"
            with open(filename, "w") as f:
                f.write(content)
            json_data[key] = content
        with open("scenarios.json", "a") as f:
            json.dump({scenario_name: json_data}, f)
            f.write("\n")
    except Exception as e:
        st.error(f"Error saving scenarios: {e}")

def initialize_session_state():
    if "session_initialized" not in st.session_state:
        st.session_state["session_initialized"] = True
        st.session_state["initialized"] = False
        st.session_state["scenario_name"] = ""
        st.session_state["precondition_choice"] = "No"
        st.session_state["dc_choice"] = "Yes - Create New"
        st.session_state["sc_choice"] = "No"
        st.session_state["sc_count"] = 1
        st.session_state["tabs"] = []
        st.session_state["input_values"] = {}  # Store all input values by key
        st.session_state["select_values"] = {}  # Store all selectbox values by key

def update_num_statements(tab_name, scenario_key=None):
    if scenario_key:
        prefix = scenario_key
        st.session_state[f"{prefix}_num_given"] = st.session_state[f"{prefix}_num_given_input"]
        st.session_state[f"{prefix}_num_when"] = st.session_state[f"{prefix}_num_when_input"]
        st.session_state[f"{prefix}_num_then"] = st.session_state[f"{prefix}_num_then_input"]
    else:
        prefix = tab_name
        st.session_state[f"{prefix}_num_given"] = st.session_state[f"{prefix}_num_given_input"]

def show_gherkin_scenario_builder():
    initialize_session_state()
    st.markdown(
        """
        <h1 style="white-space: nowrap; margin-bottom: 0px;">
            Gherkinease - Scenario Builder
        </h1>
        """,
        unsafe_allow_html=True
    )
    st.markdown(
        """
        <h2 style="color: green; font-size: 20px;">
            Build your Test Set below:
        </h2>
        """,
        unsafe_allow_html=True
    )

    """with st.form(key="test_set_form"):
        scenario_name_input = st.text_input(
            "Test Set Name (e.g., Test_Case_001):",
            value=st.session_state.get("scenario_name", ""),
            key="scenario_name"
        )"""
    """with st.form(key="test_set_form"):
        # Let Streamlit manage scenario_name via the key
        st.text_input(
            "Test Set Name (e.g., Test_Case_001):",
            value=st.session_state.get("scenario_name", ""),
            key="scenario_name"
        )"""
        # Ensure persistent_scenario_name is initialized
    if "persistent_scenario_name" not in st.session_state:
        st.session_state["persistent_scenario_name"] = ""

    with st.form(key="test_set_form"):
        st.text_input(
            "Test Set Name (e.g., Test_Case_001):",
            value=st.session_state["persistent_scenario_name"],  # Use persistent value
            key="scenario_name"
        )
        
        
        precondition_choice = st.radio(
            "Precondition Scenario:",
            ["Yes - Create New", "No", "Already Existing"],
            index=["Yes - Create New", "No", "Already Existing"].index(st.session_state.get("precondition_choice", "No")),
            key="precondition_choice"
        )
        
        dc_choice = st.radio(
            "Drive Cycle (DC) Scenario (Mandatory):",
            ["Yes - Create New", "Already Existing"],
            index=["Yes - Create New", "Already Existing"].index(st.session_state.get("dc_choice", "Yes - Create New")),
            key="dc_choice"
        )
        
        sc_choice = st.radio(
            "Success Criteria (SC) Scenario:",
            ["Yes", "No"],
            index=["Yes", "No"].index(st.session_state.get("sc_choice", "No")),
            key="sc_choice"
        )
        
        sc_count = st.session_state.get("sc_count", 1)
        if st.session_state.sc_choice == "Yes":
            sc_count = st.number_input(
                "Number of SC Scenarios:",
                min_value=1,
                max_value=10,
                value=st.session_state.get("sc_count", 1),
                key="sc_count"
            )
        
        submit_button = st.form_submit_button(label="Generate Tabs")
    
    st.write(f"Debug: scenario_name before submission = {st.session_state.get('scenario_name', 'Not set')}")
    st.write(f"Debug: persistent_scenario_name = {st.session_state.get('persistent_scenario_name', 'Not set')}")

    if submit_button:
        st.session_state["persistent_scenario_name"] = st.session_state["scenario_name"]  # Save on submit
        st.write(f"Debug: scenario_name after submission = {st.session_state.get('scenario_name', 'Not set')}")
        if st.session_state["scenario_name"]:
            st.session_state.initialized = True
            tabs = []
            if st.session_state.precondition_choice == "Yes - Create New":
                tabs.append("Precondition")
            if st.session_state.dc_choice == "Yes - Create New":
                tabs.append("Drive Cycle")
            if st.session_state.sc_choice == "Yes":
                tabs.extend([f"Success Criteria {i+1}" for i in range(st.session_state.sc_count)])
            st.session_state.tabs = tabs
        else:
            st.error("Please enter a Test Set Name!")

    if st.session_state.initialized and st.session_state.tabs:
        scenarios_dict = {}
        tab_objects = st.tabs(st.session_state.tabs)
        for i, tab_name in enumerate(st.session_state.tabs):
            with tab_objects[i]:
                if tab_name == "Precondition":
                    scenario_content = build_dc_scenario(tab_name)
                    scenarios_dict["Precondition"] = scenario_content
                elif tab_name == "Drive Cycle":
                    scenario_content = build_dc_scenario(tab_name)
                    scenarios_dict["Drive Cycle"] = scenario_content
                elif "Success Criteria" in tab_name:
                    sc_index = tab_name.split()[-1]
                    scenario_content = build_sc_scenario(tab_name, f"sc_{sc_index}")
                    scenarios_dict[f"Success Criteria_{sc_index}"] = scenario_content

        if st.button("Save Test Set"):
            save_scenarios(st.session_state.scenario_name, scenarios_dict)
            st.success(f"Test Set '{st.session_state.scenario_name}' saved successfully!")

def build_dc_scenario(tab_name):
    st.subheader(f"{tab_name} Scenario")
    
    num_given_key = f"{tab_name}_num_given"
    if num_given_key not in st.session_state:
        st.session_state[num_given_key] = 1

    st.number_input(
        f"Number of Given statements for {tab_name}:",
        min_value=1,
        max_value=10,
        value=st.session_state[num_given_key],
        key=f"{tab_name}_num_given_input",
        on_change=update_num_statements,
        args=(tab_name,)
    )
    num_given = st.session_state[num_given_key]

    # Debug
    st.write(f"Debug: {num_given_key} = {num_given}")
    st.write(f"Debug: input_values for {tab_name} = {[st.session_state['input_values'].get(f'{tab_name}_given_input_{i}', '') for i in range(num_given)]}")

    gherkin_scenario = f"Scenario: {st.session_state.scenario_name} {tab_name}\n\n"
    for i in range(num_given):
        input_key = f"{tab_name}_given_input_{i}"
        select_key = f"{tab_name}_given_select_{i}"
        
        # Get or set default input value
        if input_key not in st.session_state["input_values"]:
            st.session_state["input_values"][input_key] = ""
        input_value = st.text_input(
            f"Given {i+1} (Type here):",
            value=st.session_state["input_values"][input_key],
            key=input_key
        )
        st.session_state["input_values"][input_key] = input_value
        typed_value = autocorrect_input(input_value)

        # Get or set default selectbox value
        if select_key not in st.session_state["select_values"]:
            st.session_state["select_values"][select_key] = ""
        options = [""] + list(keywords_dict.keys())
        current_value = st.session_state["select_values"][select_key]
        current_index = options.index(current_value) if current_value in options else 0
        select_value = st.selectbox(
            f"Given {i+1} (Or Select):",
            options,
            index=current_index,
            key=select_key
        )
        st.session_state["select_values"][select_key] = select_value

        final_value = typed_value if typed_value.strip() else select_value
        st.write(f"<span style='color: green;'>Final Given {i+1}: {final_value}</span>", unsafe_allow_html=True)

        if i == 0:
            gherkin_scenario += format_gherkin_statement("Given", final_value) + "\n"
        else:
            gherkin_scenario += format_gherkin_statement("And", final_value) + "\n"

    return display_generated_scenario(tab_name, gherkin_scenario)

def build_sc_scenario(tab_name, scenario_key):
    st.subheader(f"{tab_name} Scenario")
    
    # Initialize counts
    if f"{scenario_key}_num_given" not in st.session_state:
        st.session_state[f"{scenario_key}_num_given"] = 1
    if f"{scenario_key}_num_when" not in st.session_state:
        st.session_state[f"{scenario_key}_num_when"] = 1
    if f"{scenario_key}_num_then" not in st.session_state:
        st.session_state[f"{scenario_key}_num_then"] = 1

    st.number_input(
        f"Number of Given statements for {tab_name}:",
        min_value=1,
        max_value=10,
        value=st.session_state[f"{scenario_key}_num_given"],
        key=f"{scenario_key}_num_given_input",
        on_change=update_num_statements,
        args=(None, scenario_key)
    )
    st.number_input(
        f"Number of When statements for {tab_name}:",
        min_value=1,
        max_value=10,
        value=st.session_state[f"{scenario_key}_num_when"],
        key=f"{scenario_key}_num_when_input",
        on_change=update_num_statements,
        args=(None, scenario_key)
    )
    st.number_input(
        f"Number of Then statements for {tab_name}:",
        min_value=1,
        max_value=10,
        value=st.session_state[f"{scenario_key}_num_then"],
        key=f"{scenario_key}_num_then_input",
        on_change=update_num_statements,
        args=(None, scenario_key)
    )

    num_given = st.session_state[f"{scenario_key}_num_given"]
    num_when = st.session_state[f"{scenario_key}_num_when"]
    num_then = st.session_state[f"{scenario_key}_num_then"]

    # Debug
    st.write(f"Debug: {scenario_key}_num_given = {num_given}")
    st.write(f"Debug: given_input_values = {[st.session_state['input_values'].get(f'{scenario_key}_given_input_{i}', '') for i in range(num_given)]}")
    st.write(f"Debug: {scenario_key}_num_when = {num_when}")
    st.write(f"Debug: when_input_values = {[st.session_state['input_values'].get(f'{scenario_key}_when_input_{i}', '') for i in range(num_when)]}")
    st.write(f"Debug: {scenario_key}_num_then = {num_then}")
    st.write(f"Debug: then_input_values = {[st.session_state['input_values'].get(f'{scenario_key}_then_input_{i}', '') for i in range(num_then)]}")

    gherkin_scenario = f"Scenario: {st.session_state.scenario_name} {tab_name}\n\n"
    
    for i in range(num_given):
        input_key = f"{scenario_key}_given_input_{i}"
        select_key = f"{scenario_key}_given_select_{i}"
        
        if input_key not in st.session_state["input_values"]:
            st.session_state["input_values"][input_key] = ""
        input_value = st.text_input(
            f"Given {i+1} (Type here):",
            value=st.session_state["input_values"][input_key],
            key=input_key
        )
        st.session_state["input_values"][input_key] = input_value
        typed_value = autocorrect_input(input_value)

        if select_key not in st.session_state["select_values"]:
            st.session_state["select_values"][select_key] = ""
        options = [""] + list(keywords_dict.keys())
        current_value = st.session_state["select_values"][select_key]
        current_index = options.index(current_value) if current_value in options else 0
        select_value = st.selectbox(
            f"Given {i+1} (Or Select):",
            options,
            index=current_index,
            key=select_key
        )
        st.session_state["select_values"][select_key] = select_value

        final_value = typed_value if typed_value.strip() else select_value
        st.write(f"<span style='color: green;'>Final Given {i+1}: {final_value}</span>", unsafe_allow_html=True)

        if i == 0:
            gherkin_scenario += format_gherkin_statement("Given", final_value) + "\n"
        else:
            gherkin_scenario += format_gherkin_statement("And", final_value) + "\n"

    for i in range(num_when):
        input_key = f"{scenario_key}_when_input_{i}"
        select_key = f"{scenario_key}_when_select_{i}"
        
        if input_key not in st.session_state["input_values"]:
            st.session_state["input_values"][input_key] = ""
        input_value = st.text_input(
            f"When {i+1} (Type here):",
            value=st.session_state["input_values"][input_key],
            key=input_key
        )
        st.session_state["input_values"][input_key] = input_value
        typed_value = autocorrect_input(input_value)

        if select_key not in st.session_state["select_values"]:
            st.session_state["select_values"][select_key] = ""
        options = [""] + list(keywords_dict.keys())
        current_value = st.session_state["select_values"][select_key]
        current_index = options.index(current_value) if current_value in options else 0
        select_value = st.selectbox(
            f"When {i+1} (Or Select):",
            options,
            index=current_index,
            key=select_key
        )
        st.session_state["select_values"][select_key] = select_value

        final_value = typed_value if typed_value.strip() else select_value
        st.write(f"<span style='color: green;'>Final When {i+1}: {final_value}</span>", unsafe_allow_html=True)

        if i == 0:
            gherkin_scenario += format_gherkin_statement("When", final_value) + "\n"
        else:
            gherkin_scenario += format_gherkin_statement("And", final_value) + "\n"

    for i in range(num_then):
        input_key = f"{scenario_key}_then_input_{i}"
        select_key = f"{scenario_key}_then_select_{i}"
        
        if input_key not in st.session_state["input_values"]:
            st.session_state["input_values"][input_key] = ""
        input_value = st.text_input(
            f"Then {i+1} (Type here):",
            value=st.session_state["input_values"][input_key],
            key=input_key
        )
        st.session_state["input_values"][input_key] = input_value
        typed_value = autocorrect_input(input_value)

        if select_key not in st.session_state["select_values"]:
            st.session_state["select_values"][select_key] = ""
        options = [""] + list(keywords_dict.keys())
        current_value = st.session_state["select_values"][select_key]
        current_index = options.index(current_value) if current_value in options else 0
        select_value = st.selectbox(
            f"Then {i+1} (Or Select):",
            options,
            index=current_index,
            key=select_key
        )
        st.session_state["select_values"][select_key] = select_value

        final_value = typed_value if typed_value.strip() else select_value
        st.write(f"<span style='color: green;'>Final Then {i+1}: {final_value}</span>", unsafe_allow_html=True)

        if i == 0:
            gherkin_scenario += format_gherkin_statement("Then", final_value) + "\n"
        else:
            gherkin_scenario += format_gherkin_statement("And", final_value) + "\n"

    return display_generated_scenario(tab_name, gherkin_scenario)

def display_generated_scenario(tab_name, gherkin_scenario):
    st.code(gherkin_scenario, language='gherkin')
    tags = re.findall(r'<(.*?)>', gherkin_scenario)
    st.write("Extracted tags:", tags)

    example_df_key = f"{tab_name}_example_df"
    example_df = None
    if tags:
        with st.form(key=f"{tab_name}_table_form"):
            num_cols = st.number_input(
                "Number of Columns in Example Table:",
                min_value=1,
                max_value=len(tags),
                value=len(tags),
                key=f"{tab_name}_num_cols"
            )
            default_rows = len(st.session_state[example_df_key]) if example_df_key in st.session_state else 1
            num_rows = st.number_input(
                "Number of Rows in Example Table:",
                min_value=1,
                value=default_rows,
                key=f"{tab_name}_num_rows"
            )

            if example_df_key not in st.session_state:
                st.session_state[example_df_key] = pd.DataFrame(
                    columns=tags[:num_cols],
                    index=range(num_rows)
                )
            else:
                current_df = st.session_state[example_df_key]
                if (len(current_df.columns) != num_cols or 
                    list(current_df.columns) != tags[:num_cols] or 
                    len(current_df) != num_rows):
                    new_df = pd.DataFrame(columns=tags[:num_cols], index=range(num_rows))
                    for col in current_df.columns:
                        if col in new_df.columns:
                            new_df[col] = current_df[col].reindex(range(num_rows)).fillna("")
                    st.session_state[example_df_key] = new_df

            st.write("Example Table:")
            edited_df = st.data_editor(
                st.session_state[example_df_key],
                num_rows="dynamic",
                key=f"{tab_name}_example_table"
            )
            st.session_state[example_df_key] = edited_df

            if st.form_submit_button("Apply Changes"):
                example_df = edited_df
            else:
                example_df = edited_df

    content = generate_download_content(gherkin_scenario, example_df)
    download_link_html = download_link(
        content, 
        f"{st.session_state.scenario_name}_{tab_name}.txt", 
        f"Download {tab_name}"
    )
    st.markdown(download_link_html, unsafe_allow_html=True)
    return content

