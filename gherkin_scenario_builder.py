import base64
import streamlit as st
import pdfplumber
import pandas as pd
import textdistance
import re
from autocorrect import Speller
 
def load_keywords():
    df = pd.read_excel('Keyword Identified (2).xlsx', sheet_name='KEYWORDS', header=None)
    column_names = df.iloc[6].tolist()
    df = df.iloc[7:].reset_index(drop=True)
    df.dropna(subset=[df.columns[8]], inplace=True)
    df.columns = column_names
    keywords_dict = df.set_index(df.columns[8]).T.to_dict('list')
    return df, keywords_dict, column_names
df, keywords_dict, column_names = load_keywords()
 
def format_gherkin_statement(keyword, statement):
    statement = statement.strip()
    return f"{keyword} {statement}"
 
def download_link(content, filename, link_text):
    b64 = base64.b64encode(content.encode()).decode()
    href = f'<a href="data:file/txt;base64,{b64}" download="{filename}">{link_text}</a>'
    return href
 
def generate_gherkin_scenario(tags=None, example_table=None):
    scenario = "Scenario: Your scenario title\n\n"
    if tags:
        scenario += "@" + " @".join(tags) + "\n"
    if example_table is not None and not example_table.empty:
        scenario += "Examples:\n"
        scenario += example_table.to_string(index=False)
    return scenario
 
"""def format_example_table(rows):
    column_widths = [max(len(str(item)) for item in col) for col in zip(*rows)]
    formatted_rows = []
    for row in rows:
        formatted_row = "|".join([f"{str(item).ljust(width)}" for item, width in zip(row, column_widths)])
        formatted_rows.append(f"|{formatted_row} |")
    return formatted_rows"""

def format_example_table(rows):
    # Calculate maximum width for each column, treating None/empty as empty string
    column_widths = [max(len(str(item or "")) for item in col) for col in zip(*rows)]
    formatted_rows = []
    for row in rows:
        # Format each cell, trimming whitespace and handling None/empty values
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
    spell = Speller(lang='en')
    return spell(input_text)
 
def reset_session_state():
    """Reset all session state variables to their default values"""
    # Create a list of all session state keys to remove
    keys_to_remove = [key for key in st.session_state.keys()]
    for key in keys_to_remove:
        del st.session_state[key]
    # Reinitialize essential variables with default values
    st.session_state.scenario_type = "DC"
    st.session_state.dc_num_given = 1
    st.session_state.sc_num_given = 1
    st.session_state.sc_num_when = 1
    st.session_state.sc_num_then = 1
    st.session_state.example_df = None
   
    # Initialize empty lists and dictionaries
    st.session_state.dc_given_statements = {}
    st.session_state.dc_given_selected_keys = [""]
    st.session_state.dc_given_input_text = [""]
   
    st.session_state.sc_given_statements = {}
    st.session_state.sc_when_statements = {}
    st.session_state.sc_then_statements = {}
    st.session_state.sc_given_selected_keys = [""]
    st.session_state.sc_when_selected_keys = [""]
    st.session_state.sc_then_selected_keys = [""]
    st.session_state.sc_given_input_text = [""]
    st.session_state.sc_when_input_text = [""]
    st.session_state.sc_then_input_text = [""]
 
# Modified display functions to use session state
def show_gherkin_scenario_builder():
    # Create a layout with two columns
    col1, col2 = st.columns([6, 8])
    
    # Put title in left column
    with col1:
         st.markdown(
        """
        <h1 style="white-space: nowrap; margin-bottom: 0px;">
            Gherkin Scenario Builder
        </h1>
        """,
        unsafe_allow_html=True
    )
    # Add the scenario type options (DC or SC) below the title
    st.markdown(
        """
        <h2 style="color: green; font-size: 20px;">
            Build your Gherkin Scenarios below:
        </h2>
        """,
        unsafe_allow_html=True
    )
    
    # Put clear button at the bottom of the right column with specific styling
    with col2:
        st.markdown(
            """
            <style>
            /* Style for Clear button to position it on the left side */
            [data-testid="baseButton-secondary"].clear-button {
                background-color: #FF4B4B;
                color: white;
                font-size: 12px;
                padding: 4px 8px;
                width: auto;
                border-radius: 5px;
                height: 30px;
                float: left;  /* Align the button to the left */
                margin-top: 20px;
            }
            </style>
            """,
            unsafe_allow_html=True
        )
        st.markdown("<br><br><br>", unsafe_allow_html=True)  # Add spacing
        if st.button("Clear", key="clear_button", type="secondary", use_container_width=False):
            reset_session_state()

        
    #st.write("Build your Gherkin scenarios below.")
 
    if "scenario_type" not in st.session_state:
        st.session_state.scenario_type = "DC"
 
    # Load keywords
    df, keywords_dict, column_names = load_keywords()
    if keywords_dict is None:
        return
 
    scenario_type_options = ["DC","SC"]
    # Use session state for radio button
    st.session_state.scenario_type = st.radio(
        "Select Scenario Type:",
        scenario_type_options,
        key="scenario_type_radio",
        index=scenario_type_options.index(st.session_state.scenario_type)
    )
    if st.session_state.scenario_type == "DC":
        #initilaise the input fields in session state
        if "dc_num_given" not in st.session_state:
            st.session_state.dc_num_given = 1
 
        if "dc_given_statements" not in st.session_state:
            st.session_state.dc_given_statements = dict()
 
       # Initialize the lists if they don't exist
        if "dc_given_selected_keys" not in st.session_state:
            st.session_state.dc_given_selected_keys = [""] * st.session_state.dc_num_given
           
        if "dc_given_input_text" not in st.session_state:
            st.session_state.dc_given_input_text = [""] * st.session_state.dc_num_given
       
        st.session_state.dc_num_given = st.number_input(
            "Number of Given statements:",
            min_value=1,
            max_value=10,
            value=st.session_state.dc_num_given,
        )
        # Resize lists while preserving existing values
        current_length = len(st.session_state.dc_given_selected_keys)
        if current_length != st.session_state.dc_num_given:
            if current_length < st.session_state.dc_num_given:
                # Extend lists with empty strings for new entries
                st.session_state.dc_given_selected_keys.extend([""] * (st.session_state.dc_num_given - current_length))
                st.session_state.dc_given_input_text.extend([""] * (st.session_state.dc_num_given - current_length))
            else:
                # Truncate lists while preserving existing values
                st.session_state.dc_given_selected_keys = st.session_state.dc_given_selected_keys[:st.session_state.dc_num_given]
                st.session_state.dc_given_input_text = st.session_state.dc_given_input_text[:st.session_state.dc_num_given]
 
        for i in range(st.session_state.dc_num_given):
            st.session_state.dc_given_input_text[i] = st.text_input(
                f"Given {i+1} (Type your keyword here):",
                value= st.session_state.dc_given_input_text[i],
                key=f"given_input_text{i}"
            )
            typed_value = autocorrect_input(st.session_state.dc_given_input_text[i])

            st.session_state.dc_given_selected_keys[i] = f"dc_given_select_{i}"
            options = [""] + list(keywords_dict.keys())
            current_value = st.session_state.dc_given_statements.get(st.session_state.dc_given_selected_keys[i], "")
            current_index = options.index(current_value) if current_value in options else 0
            st.session_state.dc_given_statements[st.session_state.dc_given_selected_keys[i]] = st.selectbox(
                f"Given {i+1} (Or Select from keyword identified sheet):",
                options,
                index=current_index,
                key=f"dc_given_select_{i}"
            )
            selected_value = st.session_state.dc_given_statements[st.session_state.dc_given_selected_keys[i]]
            final_value = typed_value if typed_value.strip() else selected_value
            st.write(f"Final Given {i+1}: {final_value}")

        # Generate scenario
        st.session_state.dc_gherkin_scenario = ""
        for i in range(st.session_state.dc_num_given):
            typed_value = autocorrect_input(st.session_state.dc_given_input_text[i])
            selected_value = st.session_state.dc_given_statements.get(f"dc_given_select_{i}", "")
            final_value = typed_value if typed_value.strip() else selected_value
            if i == 0:
                st.session_state.dc_gherkin_scenario += format_gherkin_statement("Given", final_value) + "\n"
            else:
                st.session_state.dc_gherkin_scenario += format_gherkin_statement("And", final_value) + "\n"
        display_generated_scenario(st.session_state.dc_gherkin_scenario)

    elif st.session_state.scenario_type == "SC":
        # Given initialization
        if "sc_num_given" not in st.session_state:
            st.session_state.sc_num_given = 1
        if "sc_given_statements" not in st.session_state:
            st.session_state.sc_given_statements = dict()
        if "sc_given_selected_keys" not in st.session_state:
            st.session_state.sc_given_selected_keys = [""] * st.session_state.sc_num_given
        if "sc_given_input_text" not in st.session_state:
            st.session_state.sc_given_input_text = [""] * st.session_state.sc_num_given

        st.session_state.sc_num_given = st.number_input(
            "Number of Given statements:",
            min_value=1,
            max_value=10,
            value=st.session_state.sc_num_given,
        )
        current_length = len(st.session_state.sc_given_selected_keys)
        if current_length != st.session_state.sc_num_given:
            if current_length < st.session_state.sc_num_given:
                st.session_state.sc_given_selected_keys.extend([""] * (st.session_state.sc_num_given - current_length))
                st.session_state.sc_given_input_text.extend([""] * (st.session_state.sc_num_given - current_length))
            else:
                st.session_state.sc_given_selected_keys = st.session_state.sc_given_selected_keys[:st.session_state.sc_num_given]
                st.session_state.sc_given_input_text = st.session_state.sc_given_input_text[:st.session_state.sc_num_given]

        # When initialization
        if "sc_num_when" not in st.session_state:
            st.session_state.sc_num_when = 1
        if "sc_when_statements" not in st.session_state:
            st.session_state.sc_when_statements = dict()
        if "sc_when_selected_keys" not in st.session_state:
            st.session_state.sc_when_selected_keys = [""] * st.session_state.sc_num_when
        if "sc_when_input_text" not in st.session_state:
            st.session_state.sc_when_input_text = [""] * st.session_state.sc_num_when

        st.session_state.sc_num_when = st.number_input(
            "Number of When statements:",  # Fixed label typo
            min_value=1,
            max_value=10,
            value=st.session_state.sc_num_when,
            key="sc_num_when_input"
        )
        current_length = len(st.session_state.sc_when_selected_keys)
        if current_length != st.session_state.sc_num_when:
            if current_length < st.session_state.sc_num_when:
                st.session_state.sc_when_selected_keys.extend([""] * (st.session_state.sc_num_when - current_length))
                st.session_state.sc_when_input_text.extend([""] * (st.session_state.sc_num_when - current_length))
            else:
                st.session_state.sc_when_selected_keys = st.session_state.sc_when_selected_keys[:st.session_state.sc_num_when]
                st.session_state.sc_when_input_text = st.session_state.sc_when_input_text[:st.session_state.sc_num_when]

        # Then initialization
        if "sc_num_then" not in st.session_state:
            st.session_state.sc_num_then = 1
        if "sc_then_statements" not in st.session_state:
            st.session_state.sc_then_statements = dict()
        if "sc_then_selected_keys" not in st.session_state:
            st.session_state.sc_then_selected_keys = [""] * st.session_state.sc_num_then
        if "sc_then_input_text" not in st.session_state:
            st.session_state.sc_then_input_text = [""] * st.session_state.sc_num_then

        st.session_state.sc_num_then = st.number_input(
            "Number of Then statements:",
            min_value=1,
            max_value=10,
            value=st.session_state.sc_num_then,
        )
        current_length = len(st.session_state.sc_then_selected_keys)
        if current_length != st.session_state.sc_num_then:
            if current_length < st.session_state.sc_num_then:
                st.session_state.sc_then_selected_keys.extend([""] * (st.session_state.sc_num_then - current_length))
                st.session_state.sc_then_input_text.extend([""] * (st.session_state.sc_num_then - current_length))
            else:
                st.session_state.sc_then_selected_keys = st.session_state.sc_then_selected_keys[:st.session_state.sc_num_then]
                st.session_state.sc_then_input_text = st.session_state.sc_then_input_text[:st.session_state.sc_num_then]

        # Given statements
        for i in range(st.session_state.sc_num_given):
            st.session_state.sc_given_input_text[i] = st.text_input(
                f"Given {i+1} (Type your keyword here):",
                value=st.session_state.sc_given_input_text[i],
                key=f"sc_given_input_text_{i}"
            )
            typed_value = autocorrect_input(st.session_state.sc_given_input_text[i])

            st.session_state.sc_given_selected_keys[i] = f"sc_given_select_{i}"
            options = [""] + list(keywords_dict.keys())
            current_value = st.session_state.sc_given_statements.get(st.session_state.sc_given_selected_keys[i], "")
            current_index = options.index(current_value) if current_value in options else 0
            st.session_state.sc_given_statements[st.session_state.sc_given_selected_keys[i]] = st.selectbox(
                f"Given {i+1} (Or Select from keyword identified sheet):",
                options,
                index=current_index,
                key=f"sc_given_select_{i}"
            )
            selected_value = st.session_state.sc_given_statements[st.session_state.sc_given_selected_keys[i]]
            final_value = typed_value if typed_value.strip() else selected_value
            st.write(f"Final Given {i+1}: {final_value}")

        # When statements
        for i in range(st.session_state.sc_num_when):
            st.session_state.sc_when_input_text[i] = st.text_input(
                f"When {i+1} (Type your keyword here):",
                value=st.session_state.sc_when_input_text[i],
                key=f"sc_when_input_text_{i}"
            )
            typed_value = autocorrect_input(st.session_state.sc_when_input_text[i])

            st.session_state.sc_when_selected_keys[i] = f"sc_when_select_{i}"
            options = [""] + list(keywords_dict.keys())
            current_value = st.session_state.sc_when_statements.get(st.session_state.sc_when_selected_keys[i], "")
            current_index = options.index(current_value) if current_value in options else 0
            st.session_state.sc_when_statements[st.session_state.sc_when_selected_keys[i]] = st.selectbox(
                f"When {i+1} (Or Select from keyword identified sheet):",
                options,
                index=current_index,
                key=f"sc_when_select_{i}"
            )
            selected_value = st.session_state.sc_when_statements[st.session_state.sc_when_selected_keys[i]]
            final_value = typed_value if typed_value.strip() else selected_value
            st.write(f"Final When {i+1}: {final_value}")

        # Then statements
        for i in range(st.session_state.sc_num_then):
            st.session_state.sc_then_input_text[i] = st.text_input(
                f"Then {i+1} (Type your keyword here):",
                value=st.session_state.sc_then_input_text[i],
                key=f"sc_then_input_text_{i}"
            )
            typed_value = autocorrect_input(st.session_state.sc_then_input_text[i])

            st.session_state.sc_then_selected_keys[i] = f"sc_then_select_{i}"
            options = [""] + list(keywords_dict.keys())
            current_value = st.session_state.sc_then_statements.get(st.session_state.sc_then_selected_keys[i], "")
            current_index = options.index(current_value) if current_value in options else 0
            st.session_state.sc_then_statements[st.session_state.sc_then_selected_keys[i]] = st.selectbox(
                f"Then {i+1} (Or Select from keyword identified sheet):",
                options,
                index=current_index,
                key=f"sc_then_select_{i}"
            )
            selected_value = st.session_state.sc_then_statements[st.session_state.sc_then_selected_keys[i]]
            final_value = typed_value if typed_value.strip() else selected_value
            st.write(f"Final Then {i+1}: {final_value}")

        # Generate scenario
        st.session_state.sc_gherkin_scenario = ""
        for i in range(st.session_state.sc_num_given):
            typed_value = autocorrect_input(st.session_state.sc_given_input_text[i])
            selected_value = st.session_state.sc_given_statements.get(f"sc_given_select_{i}", "")
            final_value = typed_value if typed_value.strip() else selected_value
            if i == 0:
                st.session_state.sc_gherkin_scenario += format_gherkin_statement("Given", final_value) + "\n"
            else:
                st.session_state.sc_gherkin_scenario += format_gherkin_statement("And", final_value) + "\n"

        for i in range(st.session_state.sc_num_when):
            typed_value = autocorrect_input(st.session_state.sc_when_input_text[i])
            selected_value = st.session_state.sc_when_statements.get(f"sc_when_select_{i}", "")
            final_value = typed_value if typed_value.strip() else selected_value
            if i == 0:
                st.session_state.sc_gherkin_scenario += format_gherkin_statement("When", final_value) + "\n"
            else:
                st.session_state.sc_gherkin_scenario += format_gherkin_statement("And", final_value) + "\n"

        for i in range(st.session_state.sc_num_then):
            typed_value = autocorrect_input(st.session_state.sc_then_input_text[i])
            selected_value = st.session_state.sc_then_statements.get(f"sc_then_select_{i}", "")
            final_value = typed_value if typed_value.strip() else selected_value
            if i == 0:
                st.session_state.sc_gherkin_scenario += format_gherkin_statement("Then", final_value) + "\n"
            else:
                st.session_state.sc_gherkin_scenario += format_gherkin_statement("And", final_value) + "\n"
        display_generated_scenario(st.session_state.sc_gherkin_scenario)

    
def display_generated_scenario(gherkin_scenario):
    st.session_state.gherkin_scenario = gherkin_scenario
    st.subheader("Generated Gherkin Scenario")
    st.code(st.session_state.gherkin_scenario, language='gherkin')
    
    tags = [tag.strip() for tag in re.findall(r'<(.*?)>', st.session_state.gherkin_scenario)]
    tags = re.findall(r'<(.*?)>', st.session_state.gherkin_scenario)
    st.write("Extracted tags:", tags)  # Debug to confirm

    if tags:
        # Use a form to prevent automatic reruns on widget interaction
        with st.form(key="table_form"):
            # Default num_cols to len(tags) to include all extracted tags
            num_cols = st.number_input(
                "Number of Columns in Example Table:",
                min_value=1,
                max_value=len(tags),
                value=len(tags),  # Default to all tags
                key="example_num_cols_input"
            )
            
            # Default num_rows to 1, persist user changes
            if "example_num_rows" not in st.session_state:
                st.session_state.example_num_rows = 1
            num_rows = st.number_input(
                "Number of Rows in Example Table:",
                min_value=1,
                value=st.session_state.example_num_rows,
                key="example_num_rows_input"
            )
            st.session_state.example_num_rows = num_rows

            # Initialize or update example_df with all tags up to num_cols
            if ('example_df' not in st.session_state or
                st.session_state.get('prev_tags', []) != tags):
                st.session_state.example_df = pd.DataFrame(
                    columns=tags[:num_cols],  # Use tags directly
                    index=range(num_rows)
                )
                st.session_state.prev_tags = tags
            else:
                current_df = st.session_state.example_df
                # Only adjust if num_cols or tags differ
                if len(current_df.columns) != num_cols or list(current_df.columns) != tags[:num_cols]:
                    # Preserve existing data where possible
                    new_df = pd.DataFrame(columns=tags[:num_cols], index=range(num_rows))
                    for col in current_df.columns:
                        if col in new_df.columns:
                            new_df[col] = current_df[col].reindex(range(num_rows)).fillna("")
                    st.session_state.example_df = new_df
                elif len(current_df) != num_rows:
                    # Adjust rows without changing columns
                    if num_rows > len(current_df):
                        new_rows = pd.DataFrame(
                            columns=current_df.columns,
                            index=range(len(current_df), num_rows)
                        )
                        st.session_state.example_df = pd.concat([current_df, new_rows])
                    else:
                        st.session_state.example_df = current_df.iloc[:num_rows]

            st.write("Example Table:")
            edited_df = st.data_editor(
                st.session_state.example_df,
                num_rows="dynamic",
                key=f"example_table_{len(tags)}"
            )

            # Submit button to apply changes
            submit_button = st.form_submit_button(label="Apply Changes")

            if submit_button:
                st.session_state.example_df = edited_df
                download_df = edited_df.copy()
            else:
                # Use current state if no submit
                download_df = st.session_state.example_df.copy() if 'example_df' in st.session_state else None
    else:
        download_df = None

    content = generate_download_content(st.session_state.gherkin_scenario, download_df)
    download_link_html = download_link(content, "gherkin_scenario.txt", "Download Gherkin Scenario")
    st.markdown(download_link_html, unsafe_allow_html=True)
        

