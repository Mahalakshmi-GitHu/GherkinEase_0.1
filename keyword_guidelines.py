import streamlit as st


'''def display_pdf(file_path):
    with open(file_path, 'rb') as pdf_file:
        pdf_data = pdf_file.read()
        base64_pdf = base64.b64encode(pdf_data).decode('utf-8')
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)'''

def show_keyword_guidelines():
    st.markdown("""
        <style>
        .gradient-text {
            background: linear-gradient(to right, #1e3c72, #2a5298, #53a0fd, #b0e0e6, #98fb98);
            -webkit-background-clip: text;
            color: transparent;
            font-size: 48px;
            font-weight: 700;
            font-family: 'Poppins', sans-serif;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2);
            margin-top: 20px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            font-family: Arial, sans-serif;
        }
        th, td {
            border: 1px solid black;
            padding: 10px;
            text-align: left;
        }
        .approved { background-color: #90EE90; }
        .rejected { background-color: #FF7F7F; }
        .under-review { background-color: #FFA500; }
        .duplicate { background-color: #FFFFFF; }
        .need-discuss { background-color: #FFFF99; }
        </style>
        <h1 class="gradient-text">Keyword Guidelines</h1>

        <!-- Table 1: Guidelines -->
        <h3>Keyword Guidelines</h3>
        <table>
            <tr><th>Point</th><th>Details</th></tr>
            <tr><td>1</td><td>Column B: New keywords (generic) to be discussed in the 3 Amigos to be populated.</td></tr>
            <tr><td>2</td><td>Column C: Status of keywords discussed (Approved, Rejected, Duplicate, Need to be discussed in 3 Amigos, Under review).</td></tr>
            <tr><td>3</td><td>Column H: Keywords suggested in 3 Amigos.</td></tr>
            <tr><td>4</td><td>Examples to be captured in Column H with the heading “Example:”.</td></tr>
            <tr><td>5</td><td>In display, keyword <b>centre</b> should be used instead of center. <br>
                            e.g.: The “powertrain run dry” option is “active” on “front centre” screen.</td></tr>
            <tr><td>6</td><td>Refer Sr no:746 for display-related keyword.<br>
                            The “low power mode” is “&lt;action&gt;” on “front centre” display. <br>
                            <b>action:</b> selected/deselected/<br>
                            <b>validation:</b> displayed/not displayed/highlighted/not highlighted.</td></tr>
        </table>

        <!-- Table 2: Keyword Status -->
        <h3>Keyword Status Table</h3>
        <table>
            <tr><th>Status</th><th>Description</th></tr>
            <tr class="approved"><td>Approved</td><td>The keyword is approved after discussion with KDT and CoC in 3 Amigos session and ready for implementation.</td></tr>
            <tr class="rejected"><td>Rejected</td><td>The keyword is rejected after discussion with KDT and CoC in 3 Amigos session.</td></tr>
            <tr class="under-review"><td>Under Review</td><td>The keyword is in under review. Yet to be approved/rejected.</td></tr>
            <tr class="duplicate"><td>Duplicate</td><td>The keyword is a duplicate of another approved keyword.</td></tr>
            <tr class="need-discuss"><td>Need to discuss in 3 Amigos</td><td>The keyword is yet to be discussed in 3 Amigos session.</td></tr>
        </table>

        <!-- Table 3: Parameters and Units -->
        <h3>Parameters and Units</h3>
        <table>
            <tr><th>Parameter</th><th>Unit</th></tr>
            <tr><td>Voltage</td><td>volt</td></tr>
            <tr><td>Current</td><td>ampere</td></tr>
            <tr><td>Torque</td><td>newton metre</td></tr>
            <tr><td>Speed</td><td>rpm/kph/mph</td></tr>
            <tr><td>Power</td><td>kilowatt</td></tr>
            <tr><td>Pressure</td><td>bar</td></tr>
            <tr><td>Temperature</td><td>degree celsius</td></tr>
            <tr><td>%</td><td>percentage</td></tr>
            <tr><td>Electrical Energy</td><td>kilowatt hour</td></tr>
            <tr><td>Acceleration/Deceleration Rate</td><td>metre per second square</td></tr>
            <tr><td>Time</td><td>seconds</td></tr>
            <tr><td>Distance</td><td>kilometre/metre</td></tr>
            <tr><td>Angle</td><td>degree</td></tr>
        </table>
    """, unsafe_allow_html=True)
 
    # display_text_from_pdf()
    #display_pdf('Keyword-Guidelines.pdf')
