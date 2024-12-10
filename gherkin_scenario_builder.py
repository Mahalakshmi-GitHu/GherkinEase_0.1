import base64
import streamlit as st
import pandas as pd
import re
from autocorrect import Speller

def load_keywords():
    """Load keywords from Excel file"""
    df = pd.read_excel('keyword Identified.xlsx', sheet_name='KEYWORDS', header=None)
    column_names = df.iloc[6].tolist()
    df = df.iloc[7:].reset_index(drop=True)
    df.dropna(subset=[df.columns[1]], inplace=True)
    df.columns = column_names
    keywords_dict = df.set_index(df.columns[1]).T.to_dict('list')
    return df, keywords_dict, column_names

def initialize_session_state():
    """Ensure all necessary session state variables are initialized"""
    default_values = {
        'scenario_type': 'DC',
        'dc_num_given': 1,
        'sc_num_given': 1,
        'sc_num_when': 1,
        'sc_num_then': 1,
        'dc_given_statements': {},
        'sc_given_statements': {},
        'sc_when_statements': {},
        'sc_then_statements': {},
        'dc_given_selected_keys': [""],
        'dc_given_input_text': [""],
        'sc_given_selected_keys': [""],
        'sc_when_selected_keys': [""],
        'sc_then_selected_keys': [""],
        'sc_given_input_text': [""],
        'sc_when_input_text': [""],
        'sc_then_input_text': [""],
        'example_df': None,
        'gherkin_scenario': ""
    }
    
    for key, value in default_values.items():
        if key not in st.session_state:
            st.session_state[key] = value

def reset_session_state():
    """Reset all session state variables to their default values"""
    # List of keys to reset
    keys_to_reset = [
        'scenario_type', 
        'dc_num_given', 'sc_num_given', 'sc_num_when', 'sc_num_then', 
        'example_df',
        'dc_given_statements', 'dc_given_selected_keys', 'dc_given_input_text',
        'sc_given_statements', 'sc_when_statements', 'sc_then_statements', 
        'sc_given_selected_keys', 'sc_when_selected_keys', 'sc_then_selected_keys',
        'sc_given_input_text', 'sc_when_input_text', 'sc_then_input_text',
        'gherkin_scenario'
    ]

    for key in keys_to_reset:
        if key in st.session_state:
            del st.session_state[key]

    # Reinitialize
    initialize_session_state()

def format_gherkin_statement(keyword, statement):
    """Format a Gherkin statement"""
    statement = statement.strip()
    return f"{keyword} {statement}"

def download_link(content, filename, link_text):
    """Create a downloadable link for the content"""
    b64 = base64.b64encode(content.encode()).decode()
    href = f'<a href="data:file/txt;base64,{b64}" download="{filename}">{link_text}</a>'
    return href

def generate_download_content(gherkin_scenario, example_df=None):
    """Generate downloadable content"""
    content = gherkin_scenario
    if example_df is not None and not example_df.empty:
        content += "\nExamples:\n"
        example_data = [example_df.columns.tolist()] + example_df.values.tolist()
        formatted_table = format_example_table(example_data)
        content += "\n".join(formatted_table)
    return content

def format_example_table(rows):
    """Format example table with aligned columns"""
    column_widths = [max(len(str(item)) for item in col) for col in zip(*rows)]
    formatted_rows = []
    for row in rows:
        formatted_row = "|".join([f"{str(item).ljust(width)}" for item, width in zip(row, column_widths)])
        formatted_rows.append(f"|{formatted_row} |")
    return formatted_rows

def create_selectbox_with_initial_value(label, options, initial_value="", key=None):
    """
    Create a selectbox with an initial value and handle first-time selection
    """
    # Ensure initial_value is in options
    if initial_value and initial_value not in options:
        initial_value = ""
    
    # Determine initial index
    initial_index = options.index(initial_value) if initial_value in options else 0
    
    return st.selectbox(
        label, 
        options, 
        index=initial_index, 
        key=key
    )

def show_gherkin_scenario_builder():
    """Main Gherkin scenario builder function"""
    # Initialize session state
    initialize_session_state()

    # Create a layout with two columns
    col1, col2 = st.columns([6, 1])

    # Put title in left column
    with col1:
        st.title("Gherkin Scenario Builder")
    
    # Put clear button in right column with specific styling
    with col2:
        st.markdown(
            """
            <style>
            /* Style specifically for clear button using its key */
            [data-testid="baseButton-secondary"].clear-button {
                float: right;
                margin-top: 20px;
                background-color: #FF4B4B;
                color: white;
            }
            </style>
            """,
            unsafe_allow_html=True
        )
        if st.button("Clear", key="clear_button_unique", type="secondary"):
            reset_session_state()
            st.experimental_rerun()

    st.write("Build your Gherkin scenarios below.")

    # Debugging prints
    st.write(f"Current Scenario Type: {st.session_state.get('scenario_type', 'Not Set')}")
    st.write(f"Session State Keys: {list(st.session_state.keys())}")

    # Load keywords
    df, keywords_dict, column_names = load_keywords()
    if keywords_dict is None:
        st.error("Failed to load keywords!")
        return

    scenario_type_options = ["DC","SC"]
    # Use session state for radio button
    st.session_state.scenario_type = st.radio(
        "Select Scenario Type:",
        scenario_type_options,
        key="scenario_type_radio",
        index=scenario_type_options.index(st.session_state.scenario_type)
    )

    def handle_scenario_inputs(scenario_type):
        """Handle inputs for different scenario types"""
        if scenario_type == "DC":
            # DC Scenario Handling
            st.session_state.dc_num_given = st.number_input(
                "Number of Given statements:",
                min_value=1,
                max_value=10,
                value=st.session_state.dc_num_given,
                key="dc_num_given_input"
            )

            # Adjust lists to match number of given statements
            current_length = len(st.session_state.dc_given_selected_keys)
            if current_length != st.session_state.dc_num_given:
                if current_length < st.session_state.dc_num_given:
                    st.session_state.dc_given_selected_keys.extend([""] * (st.session_state.dc_num_given - current_length))
                    st.session_state.dc_given_input_text.extend([""] * (st.session_state.dc_num_given - current_length))
                else:
                    st.session_state.dc_given_selected_keys = st.session_state.dc_given_selected_keys[:st.session_state.dc_num_given]
                    st.session_state.dc_given_input_text = st.session_state.dc_given_input_text[:st.session_state.dc_num_given]

            # Given statements for DC
            for i in range(st.session_state.dc_num_given):
                st.session_state.dc_given_input_text[i] = st.text_input(
                    f"Given {i+1} (Type your keyword here):",
                    value=st.session_state.dc_given_input_text[i],
                    key=f"dc_given_input_{i}_unique"
                )

                st.session_state.dc_given_statements[f"given_select_{i}"] = create_selectbox_with_initial_value(
                    f"Given {i+1} (Or Select from keyword identified sheet):",
                    [""] + list(keywords_dict.keys()),
                    key=f"dc_given_select_{i}_unique"
                )

            return st.session_state.dc_given_statements

        else:  # SC Scenario
            # SC Scenario with Given, When, Then statements
            scenario_sections = [
                ('Given', 'sc_num_given', 'sc_given_statements', 'sc_given_selected_keys', 'sc_given_input_text'),
                ('When', 'sc_num_when', 'sc_when_statements', 'sc_when_selected_keys', 'sc_when_input_text'),
                ('Then', 'sc_num_then', 'sc_then_statements', 'sc_then_selected_keys', 'sc_then_input_text')
            ]

            all_statements = {}
            for section, num_key, statements_key, selected_keys_key, input_text_key in scenario_sections:
                # Number input for each section
                num_statements = st.number_input(
                    f"Number of {section} statements:",
                    min_value=1,
                    max_value=10,
                    value=getattr(st.session_state, num_key),
                    key=f"{num_key}_input_unique"
                )
                setattr(st.session_state, num_key, num_statements)

                # Adjust lists to match number of statements
                current_keys = getattr(st.session_state, selected_keys_key)
                current_input = getattr(st.session_state, input_text_key)
                if len(current_keys) != num_statements:
                    if len(current_keys) < num_statements:
                        current_keys.extend([""] * (num_statements - len(current_keys)))
                        current_input.extend([""] * (num_statements - len(current_input)))
                    else:
                        current_keys = current_keys[:num_statements]
                        current_input = current_input[:num_statements]
                    
                    setattr(st.session_state, selected_keys_key, current_keys)
                    setattr(st.session_state, input_text_key, current_input)

                # Inputs for each statement
                section_statements = {}
                for i in range(num_statements):
                    # Text input
                    input_text = st.text_input(
                        f"{section} {i+1} (Type your keyword here):",
                        value=current_input[i],
                        key=f"{section.lower()}_input_{i}_unique"
                    )
                    current_input[i] = input_text

                    # Selectbox
                    selected_statement = create_selectbox_with_initial_value(
                        f"{section} {i+1} (Or Select from keyword identified sheet):",
                        [""] + list(keywords_dict.keys()),
                        key=f"{section.lower()}_select_{i}_unique"
                    )
                    section_statements[f"{section.lower()}_select_{i}"] = selected_statement

                all_statements.update(section_statements)

            return all_statements

    # Handle scenario inputs based on type
    if st.session_state.scenario_type == "DC":
        st.session_state.dc_given_statements = handle_scenario_inputs("DC")
        gherkin_scenario = ""
        for i, given in enumerate(st.session_state.dc_given_statements.values()):
            if given:  # Only add non-empty statements
                gherkin_scenario += format_gherkin_statement("Given" if i == 0 else "And", given) + "\n"
    else:
        st.session_state.sc_statements = handle_scenario_inputs("SC")
        gherkin_scenario = ""
        
        # Collect and format statements from different sections
        statement_types = [
            ('Given', st.session_state.sc_given_statements),
            ('When', st.session_state.sc_when_statements),
            ('Then', st.session_state.sc_then_statements)
        ]
        
        for section_type, statements in statement_types:
            used_first = False
            for statement in statements.values():
                if statement:  # Only add non-empty statements
                    keyword = section_type if not used_first else "And"
                    gherkin_scenario += format_gherkin_statement(keyword, statement) + "\n"
                    used_first = True

    # Display generated scenario
    display_generated_scenario(gherkin_scenario)

def display_generated_scenario(gherkin_scenario):
    """Display the generated Gherkin scenario"""
    st.session_state.gherkin_scenario = gherkin_scenario
    st.subheader("Generated Gherkin Scenario")
    st.code(st.session_state.gherkin_scenario, language='gherkin')

    # Handle example table
    tags = re.findall(r'<(.*?)>', st.session_state.gherkin_scenario)
    
    if tags:
        # Make tags unique by adding suffix
        unique_tags = [f"{tag}_{i}" for i, tag in enumerate(tags, 1)]
        
        num_cols = st.number_input(
            "Number of Columns in Example Table:",
            min_value=1,
            max_value=len(tags),
            value=len(tags)
        )
        num_rows = st.number_input("Number of Rows in Example Table:", min_value=1, value=1)

        # Initialize or update example_df
        if (st.session_state.example_df is None or 
            st.session_state.example_df.shape != (num_rows, num_cols)):
            st.session_state.example_df = pd.DataFrame(
                columns=unique_tags[:num_cols],
                index=range(num_rows)
            )

        st.write("Example Table:")
        edited_df = st.data_editor(
            st.session_state.example_df,
            num_rows="dynamic",
            key=f"example_table_{len(tags)}"
        )
        
        # Store the edited DataFrame back in session state
        st.session_state.example_df = edited_df

        # For generating download content, map back to original tags
        download_df = edited_df.copy()
        download_df.columns = tags[:num_cols]

        # Generate download content and link
        content = generate_download_content(st.session_state.gherkin_scenario, download_df)
        download_link_html = download_link(content, "gherkin_scenario.txt", "Download Gherkin Scenario")
        st.markdown(download_link_html, unsafe_allow_html=True)

def main():
    """Main function to run the Streamlit app"""
    st.set_page_config(page_title="Gherkin Scenario Builder", page_icon=":memo:")
    show_gherkin_scenario_builder()

if __name__ == "__main__":
    main()