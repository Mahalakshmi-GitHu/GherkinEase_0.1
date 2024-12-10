import base64
import streamlit as st
import pdfplumber
import fitz
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
 
def format_example_table(rows):
    column_widths = [max(len(str(item)) for item in col) for col in zip(*rows)]
    formatted_rows = []
    for row in rows:
        formatted_row = "|".join([f"{str(item).ljust(width)}" for item, width in zip(row, column_widths)])
        formatted_rows.append(f"|{formatted_row} |")
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
    
    # Put clear button at the bottom of the right column with specific styling
    with col2:
        st.markdown("<div style='flex-grow: 1;'></div>", unsafe_allow_html=True)  # Spacer to push the button down
        st.markdown(
            """
            <style>
            /* Style for Clear button */
            [data-testid="baseButton-secondary"].clear-button {
                background-color: #FF4B4B;
                color: white;
                font-size: 12px;
                padding: 4px 8px;
                width: auto;
                border-radius: 5px;
                height: 30px;
            }
            </style>
            """,
            unsafe_allow_html=True
        )
        st.markdown("<br><br><br>", unsafe_allow_html=True)  # Add spacing
        if st.button("Clear", key="clear_button", type="secondary", use_container_width=False):
            reset_session_state()

        
    st.write("Build your Gherkin scenarios below.")
 
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
                key=f"given_input_{i}"
            )
           
            # st.session_state.given_input_text[i] = autocorrect_input(st.session_state.given_input_text[i])
            # st.write(f"Auto-corrected Given {i+1}: {st.session_state.given_input_text[i]}")
           
            # # Select box with preserved value
            # st.session_state.given_selected_key = f"given_select_{i}"
            # options = [""] + list(keywords_dict.keys())
            # current_value = st.session_state.given_statements.get(given_select_key, "")
            # current_index = options.index(current_value) if current_value in options else 0
 
            # Select box with preserved value
            st.session_state.dc_given_selected_keys[i] = f"given_select_{i}"
            options = [""] + list(keywords_dict.keys())
 
 
            current_value = st.session_state.dc_given_statements.get(st.session_state.dc_given_selected_keys[i], "")
            current_index = options.index(current_value) if current_value in options else 0
            st.session_state.dc_given_statements[st.session_state.dc_given_selected_keys[i]] = st.selectbox(
                f"Given {i+1} (Or Select from keyword identified sheet):",
                options,
                index=current_index,
            )
            st.write(st.session_state.dc_given_statements[st.session_state.dc_given_selected_keys[i]])
 
 
    elif st.session_state.scenario_type == "SC":
        #initilaise the input fields in session state
        if "sc_num_given" not in st.session_state:
            st.session_state.sc_num_given = 1
       
 
        if "sc_given_statements" not in st.session_state:
            st.session_state.sc_given_statements = dict()
 
       # Initialize the lists if they don't exist
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
        # Resize lists while preserving existing values
        current_length = len(st.session_state.sc_given_selected_keys)
        if current_length != st.session_state.sc_num_given:
            if current_length < st.session_state.sc_num_given:
                # Extend lists with empty strings for new entries
                st.session_state.sc_given_selected_keys.extend([""] * (st.session_state.sc_num_given - current_length))
                st.session_state.sc_given_input_text.extend([""] * (st.session_state.sc_num_given - current_length))
            else:
                # Truncate lists while preserving existing values
                st.session_state.sc_given_selected_keys = st.session_state.sc_given_selected_keys[:st.session_state.sc_num_given]
                st.session_state.sc_given_input_text = st.session_state.sc_given_input_text[:st.session_state.sc_num_given]
       
 
        if "sc_num_then" not in st.session_state:
            st.session_state.sc_num_then = 1
       
        if "sc_then_statements" not in st.session_state:
            st.session_state.sc_then_statements = dict()
 
       # Initialize the lists if they don't exist
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
        # Resize lists while preserving existing values
        current_length = len(st.session_state.sc_then_selected_keys)
        if current_length != st.session_state.sc_num_then:
            if current_length < st.session_state.sc_num_then:
                # Extend lists with empty strings for new entries
                st.session_state.sc_then_selected_keys.extend([""] * (st.session_state.sc_num_then - current_length))
                st.session_state.sc_then_input_text.extend([""] * (st.session_state.sc_num_then - current_length))
            else:
                # Truncate lists while preserving existing values
                st.session_state.sc_then_selected_keys = st.session_state.sc_then_selected_keys[:st.session_state.sc_num_then]
                st.session_state.sc_then_input_text = st.session_state.sc_then_input_text[:st.session_state.sc_num_then]
 
        if "sc_num_when" not in st.session_state:
            st.session_state.sc_num_when = 1
       
 
        if "sc_when_statements" not in st.session_state:
            st.session_state.sc_when_statements = dict()
 
       # Initialize the lists if they don't exist
        if "sc_when_selected_keys" not in st.session_state:
            st.session_state.sc_when_selected_keys = [""] * st.session_state.sc_num_when
           
        if "sc_when_input_text" not in st.session_state:
            st.session_state.sc_when_input_text = [""] * st.session_state.sc_num_when
       
        st.session_state.sc_num_when = st.number_input(
            "Number of Given statements for sc:",
            min_value=1,
            max_value=10,
            value=st.session_state.sc_num_when,
            key = "Number of Given statements for sc:"
        )
        # Resize lists while preserving existing values
        current_length = len(st.session_state.sc_when_selected_keys)
        if current_length != st.session_state.sc_num_when:
            if current_length < st.session_state.sc_num_when:
                # Extend lists with empty strings for new entries
                st.session_state.sc_when_selected_keys.extend([""] * (st.session_state.sc_num_when - current_length))
                st.session_state.sc_when_input_text.extend([""] * (st.session_state.sc_num_when - current_length))
            else:
                # Truncate lists while preserving existing values
                st.session_state.sc_when_selected_keys = st.session_state.sc_when_selected_keys[:st.session_state.sc_num_when]
                st.session_state.sc_when_input_text = st.session_state.sc_when_input_text[:st.session_state.sc_num_when]
 
        #Handling Given Statements fields
        for i in range(st.session_state.sc_num_given):
            st.session_state.sc_given_input_text[i] = st.text_input(
                f"Given {i+1} (Type your keyword here):",
                value= st.session_state.sc_given_input_text[i],
                key=f"given_input_{i}"
            )
 
            # st.session_state.given_input_text[i] = autocorrect_input(st.session_state.given_input_text[i])
            # st.write(f"Auto-corrected Given {i+1}: {st.session_state.given_input_text[i]}")
 
           
            # Select box with preserved value
            st.session_state.sc_given_selected_keys[i] = f"given_select_{i}"
            options = [""] + list(keywords_dict.keys())
 
            given_current_value = st.session_state.sc_given_statements.get(st.session_state.sc_given_selected_keys[i], "")
            given_current_index = options.index(given_current_value) if given_current_value in options else 0
            st.session_state.sc_given_statements[st.session_state.sc_given_selected_keys[i]] = st.selectbox(
                f"Given {i+1} (Or Select from keyword identified sheet):",
                options,
                index = given_current_index,
                key=f"Given {i+1} (Or Select from keyword identified sheet):"
            )
 
        # When statements with similar pattern
        for i in range(st.session_state.sc_num_when):
            st.session_state.sc_when_input_text[i] = st.text_input(
                f"When {i+1} (Type your keyword here):",
                value= st.session_state.sc_when_input_text[i],
                key=f"When_input_{i}"
            )
 
 
           
            # Select box with preserved value
            st.session_state.sc_when_selected_keys[i] = f"When_select_{i}"
            options = [""] + list(keywords_dict.keys())
 
            when_current_value = st.session_state.sc_when_statements.get(st.session_state.sc_when_selected_keys[i], "")
            when_current_index = options.index(when_current_value) if when_current_value in options else 0
            st.session_state.sc_when_statements[st.session_state.sc_when_selected_keys[i]] = st.selectbox(
                f"When {i+1} (Or Select from keyword identified sheet):",
                options,
                index = when_current_index,
                key=f"When {i+1} (Or Select from keyword identified sheet):"
            )
 
 
        # Then statements with similar pattern
        for i in range(st.session_state.sc_num_then):
            st.session_state.sc_then_input_text[i] = st.text_input(
                f"Then {i+1} (Type your keyword here):",
                value= st.session_state.sc_then_input_text[i],
                key=f"Then {i+1} (Type your keyword here):"
            )
 
           
            # Select box with preserved value
            st.session_state.sc_then_selected_keys[i] = f"Then_select_{i}"
            options = [""] + list(keywords_dict.keys())
 
            then_current_value = st.session_state.sc_then_statements.get(st.session_state.sc_then_selected_keys[i], "")
            then_current_index = options.index(then_current_value) if then_current_value in options else 0
            st.session_state.sc_then_statements[st.session_state.sc_then_selected_keys[i]] = st.selectbox(
                f"Then {i+1} (Or Select from keyword identified sheet):",
                options,
                index = then_current_index,
                key=f"Then {i+1} (Or Select from keyword identified sheet):",
            )
           
 
    if st.session_state.scenario_type == "DC":
        # Generate Gherkin scenario
        st.session_state.dc_gherkin_scenario = ""
        for i, given in enumerate(st.session_state.dc_given_statements):
            if i == 0:
                st.session_state.dc_gherkin_scenario += format_gherkin_statement("Given", st.session_state.dc_given_statements[given]) + "\n"
            else:
                st.session_state.dc_gherkin_scenario += format_gherkin_statement("And", st.session_state.dc_given_statements[given]) + "\n"
        display_generated_scenario(st.session_state.dc_gherkin_scenario)
    else:
        # Generate Gherkin scenario
        st.session_state.sc_gherkin_scenario = ""
        # Generate for SC type
        for i, given in enumerate(st.session_state.sc_given_statements):
            if i == 0:
                st.session_state.sc_gherkin_scenario += format_gherkin_statement("Given", st.session_state.sc_given_statements[given]) + "\n"
            else:
                st.session_state.sc_gherkin_scenario += format_gherkin_statement("And", st.session_state.sc_given_statements[given]) + "\n"
 
        for i, when in enumerate(st.session_state.sc_when_statements):
            if i == 0:
                st.session_state.sc_gherkin_scenario += format_gherkin_statement("When", st.session_state.sc_when_statements[when]) + "\n"
            else:
                st.session_state.sc_gherkin_scenario += format_gherkin_statement("And", st.session_state.sc_when_statements[when]) + "\n"
 
        for i, then in enumerate(st.session_state.sc_then_statements):
            if i == 0:
                st.session_state.sc_gherkin_scenario += format_gherkin_statement("Then", st.session_state.sc_then_statements[then]) + "\n"
            else:
                st.session_state.sc_gherkin_scenario += format_gherkin_statement("And", st.session_state.sc_then_statements[then]) + "\n"
        display_generated_scenario(st.session_state.sc_gherkin_scenario)
 
   
 
def display_generated_scenario(gherkin_scenario):
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
 
        # Initialize or update example_df with unique column names
        if ('example_df' not in st.session_state or
            st.session_state.example_df is None or
            st.session_state.example_df.shape != (num_rows, num_cols)):
           
            # Create new DataFrame with unique column names
            st.session_state.example_df = pd.DataFrame(
                columns=unique_tags[:num_cols],
                index=range(num_rows)
            )
        else:
            # If DataFrame exists but needs resizing
            current_df = st.session_state.example_df
           
            # Handle column count changes
            if len(current_df.columns) != num_cols:
                # Keep existing data for common columns
                new_df = pd.DataFrame(
                    columns=unique_tags[:num_cols],
                    index=range(num_rows)
                )
               
                # Copy existing data for columns that exist in both
                for i, new_col in enumerate(new_df.columns):
                    if i < len(current_df.columns):
                        new_df[new_col] = current_df.iloc[:, i]
               
                st.session_state.example_df = new_df
           
            # Handle row count changes
            if len(current_df) != num_rows:
                # Resize while preserving data
                if num_rows > len(current_df):
                    # Add new rows
                    new_rows = pd.DataFrame(
                        columns=st.session_state.example_df.columns,
                        index=range(len(current_df), num_rows)
                    )
                    st.session_state.example_df = pd.concat([st.session_state.example_df, new_rows])
                else:
                    # Truncate rows
                    st.session_state.example_df = st.session_state.example_df.iloc[:num_rows]
 
        st.write("Example Table:")
        # Display the data editor with the unique column names
        edited_df = st.data_editor(
            st.session_state.example_df,
            num_rows="dynamic",
            key=f"example_table_{len(tags)}"  # Unique key for the editor
        )
       
        # Store the edited DataFrame back in session state
        st.session_state.example_df = edited_df
 
        # For generating download content, map back to original tags
        download_df = edited_df.copy()
        download_df.columns = tags[:num_cols]  # Use original tags without suffixes
 
        # Generate download content and link
        content = generate_download_content(st.session_state.gherkin_scenario, download_df)
        download_link_html = download_link(content, "gherkin_scenario.txt", "Download Gherkin Scenario")
        st.markdown(download_link_html, unsafe_allow_html=True)
