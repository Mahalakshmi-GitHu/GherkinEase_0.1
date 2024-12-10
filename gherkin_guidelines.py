import streamlit as st
import base64

def display_pdf(file_path):
    with open(file_path, 'rb') as pdf_file:
        pdf_data = pdf_file.read()
        base64_pdf = base64.b64encode(pdf_data).decode('utf-8')
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)

def show_gherkin_guidelines():
    
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
        <h1 class="gradient-text">Gherkin Guidelines</h1>
                <p1 class>Follow these guidelines when writing scenarios.</p1>
 
        <h2><strong>Pre-test</strong></h2>
        <p>Pretest needs to be a scenario type only, and we cannot use the scenario outline type for pretest.</p>
        <p><strong>Example:</strong> Given the "average state of charge of high voltage battery" is "in between" "30 to 80" percentage.</p>
 
        <h2>Rules</h2>
        <ul>
            <li><strong>"Given"</strong> followed by <strong>"And"</strong> to be used for defining the pretest.</li>
        </ul>
 
        <h2><strong>Drive Cycle</strong></h2>
        <h3>Format</h3>
        <ul>
            <li>Given ....</li>
            <li>And ......</li>
            <li>And ....</li>
        </ul>
 
        <h3>Rules</h3>
        <ul>
            <li><strong>"Given"</strong> followed by <strong>"And"</strong> to be used for defining the drive cycle.</li>
        </ul>
 
        <h2><strong>Success Criteria</strong></h2>
        <h3>Guidelines and Rules: Success Criteria Definitions - Draft</h3>
        <p><strong>Format:</strong></p>
        <ul>
            <li>Given the "average state of charge of high voltage battery" is "in between" "30 to 80" percentage</li>
            <li>And ......</li>
            <li>And .....</li>
            <li>When ....</li>
            <li>Then .....</li>
        </ul>
 
        <h2>Rules</h2>
        <ol>
            <li>No multiple <strong>"When"</strong> allowed.</li>
            <li>The same keyword is not allowed in <strong>"Given"</strong> and <strong>"When"</strong>.</li>
            <li>The duration used in <strong>"When"</strong> should be effective to all the <strong>"Then/s"</strong>. This should account for the slowest signal. BUT if the signals need to be checked at various rates (e.g. signal A is to be checked after 0.5 sec while signal B is to be checked after 1 sec), split the tests into multiple tests as in <a href="https://example-link-1">PETM-30259</a> and <a href="https://example-link-2">PETM-34452</a>.</li>
        </ol>
 
        <h2>Check where the keyword definitions checks are continuous</h2>
        <ul>
            <li>Given keyword A is "value 1"</li>
            <li>When Keyword B is "value 1"</li>
            <li>Then keyword C is "value 1"</li>
        </ul>
 
        <h2>Rules</h2>
        <ol>
            <li>The keyword does not repeat in the scenario/scenario outline.</li>
            <li>Shapes should be followed while developing Mindmaps using Lucid Chart Tool.</li>
        </ol>
        """, unsafe_allow_html=True)
 
    # Display the image
    st.image("Format.png", caption="Gherkin Workflow", width=600)
 
    st.markdown("""
        <h2>Guidelines for Keyword</h2>
        <ol>
            <li>Does the keyword look like something that already checks in the library?</li>
            <li>Where is the keyword being used in the tests (Drive cycle or success criteria or both)?</li>
            <li>How is the keyword used (<strong>Given</strong>, <strong>When</strong>, <strong>Then</strong>)?</li>
            <li>Is there a trigger point that needs to happen when the check occurs, or is it a continuous check?</li>
            <li>Is the keyword associated with driver actions/test actions, or is it the system response?</li>
            <li>Is this keyword also used elsewhere, and will it work for all?</li>
            <li>What is the composition of that keyword?</li>
            <li>How is the keyword derived? Is it referring to legacy test step descriptions or using the official documentation?</li>
            <li>Keyword list maintenance - update the keyword details during 3 amigos.</li>
            <li>Understand if the keyword is associated with driver actions or vehicle/system or environmental conditions.</li>
            <li>Check/validate with the consumers (verification group/feature system owners) if the keywords and scenarios make sense.</li>
            <li>Fully understand and decompose keywords - how it looks, works, readability, etc.</li>
        </ol>
 
        <h2>Mandatory: Move Xray test case from in-progress to under review</h2>
        <ol>
            <li>Technical review needs to be completed.</li>
            <li>Quality review should be completed.</li>
            <li>All the keywords used in test case development should be approved in the 3-amigos session.</li>
        </ol>
 
        <h2>Golden Rules for Keyword Driven Testing</h2>
        <p>For more details, refer to <a href="https://jlrglobal.sharepoint.com/sites/IntegrationTestingTestOpsChapters_GRP/SitePages/Golden-Rules-for-Keyword-Driven-Testing.aspx">Golden Rules for Keyword Driven Testing</a>.</p>
 
        <p>For SPIKE - Gherkin - Keyword Architecture, click <a href="https://example-spike-link">here</a>.</p>
    """, unsafe_allow_html=True)
 