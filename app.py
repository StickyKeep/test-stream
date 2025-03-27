import streamlit as st
import anthropic
import time
from datetime import datetime

# Set page configuration
st.set_page_config(
    page_title="Terminal CV",
    page_icon="🖥️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS for retro terminal look
st.markdown("""
<style>
    /* General page styling */
    .stApp {
        background-color: #000000;
    }
    
    /* Terminal container */
    .terminal-container {
        background-color: #0a0a0a;
        border: 2px solid #33ff33;
        border-radius: 10px;
        padding: 20px;
        font-family: 'Courier New', monospace;
        color: #33ff33;
        height: 70vh;
        overflow-y: auto;
        margin-bottom: 20px;
        position: relative;
        box-shadow: 0 0 20px rgba(51, 255, 51, 0.3);
    }
    
    /* Scanline effect */
    .terminal-container::before {
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: linear-gradient(
            rgba(18, 16, 16, 0) 50%, 
            rgba(0, 0, 0, 0.25) 50%
        );
        background-size: 100% 4px;
        pointer-events: none;
        z-index: 1;
    }
    
    /* Text coloring */
    .terminal-output {
        white-space: pre-wrap;
        word-wrap: break-word;
    }
    
    .terminal-user {
        color: #33ff33;
    }
    
    .terminal-system {
        color: #1e90ff;
    }
    
    .terminal-assistant {
        color: #33ff33;
    }
    
    .terminal-error {
        color: #ff5555;
    }
    
    /* Header */
    .terminal-header {
        color: #33ff33;
        border-bottom: 1px solid #33ff33;
        padding-bottom: 10px;
        margin-bottom: 15px;
        display: flex;
        justify-content: space-between;
    }
    
    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display:none;}
    
    /* Input field */
    .stTextInput > div > div > input {
        background-color: #0a0a0a;
        color: #33ff33;
        border: 1px solid #33ff33;
        border-radius: 5px;
        font-family: 'Courier New', monospace;
    }
    
    /* Text input label */
    .stTextInput > label {
        color: #33ff33;
        font-family: 'Courier New', monospace;
    }
    
    /* Sidebar */
    .css-1d391kg {
        background-color: #0a0a0a;
    }
    
    .sidebar .sidebar-content {
        background-color: #0a0a0a;
    }
    
    /* ASCII art */
    .ascii-art {
        font-family: monospace;
        white-space: pre;
        line-height: 1.2;
        margin: 20px 0;
        text-align: center;
    }
    
    /* API key input */
    .api-key-input {
        background-color: #0a0a0a;
        border: 1px solid #33ff33;
        color: #33ff33;
        padding: 10px;
        font-family: 'Courier New', monospace;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# ASCII art for welcome screen
ASCII_ART = """
   _____  _    _    _______          _           _     
  / ____|| |  | |  |__   __|        | |         (_)    
 | |     | |  | |     | | ___ _ _ _  | |     _ __ _  __ _  _ 
 | |     | |  | |     | |/ _ | '_  \\ | |    | '__| |/ _\` |/ _ \\
 | |____ | |__| |     | |  __| | | | | |____| |  | | (_| |  __/
  \\_____| \\____/      |_|\\___|_| |_| |______|_|  |_|\\__,_|\\___|
"""

# Personal CV information
CV_INFO = """
# CV Information

## Personal Details
Name: [Your Name]
Email: [Your Email]
Location: [Your Location]
Portfolio: [Your Website]

## Professional Summary
[A brief summary of your professional experience and skills]

## Work Experience
### [Company Name] - [Position]
[Date Range]

- [Achievement or responsibility]
- [Achievement or responsibility]
- [Achievement or responsibility]

### [Previous Company] - [Position]
[Date Range]

- [Achievement or responsibility]
- [Achievement or responsibility]

## Education
### [Degree] - [Institution]
[Date Range]

## Skills
- [Skill Category 1]: [Skills]
- [Skill Category 2]: [Skills]
- [Skill Category 3]: [Skills]

## Projects
### [Project Name]
[Brief description]
Technologies: [Technologies used]

### [Project Name]
[Brief description]
Technologies: [Technologies used]

## Achievements
- [Achievement 1]
- [Achievement 2]

## Interests
[Your personal or professional interests]
"""

# Demo mode responses
DEMO_RESPONSES = {
    "HELP": "Available commands:\n\nHELP - Display this help message\nCV - Show full CV summary\nSKILLS - List skills and expertise\nEXPERIENCE - Show work history\nEDUCATION - Show educational background\nPROJECTS - List notable projects\nCONTACT - Display contact information\nABOUT - About this terminal\nCLEAR - Clear the terminal",
    "CV": "CV SUMMARY\n\nName: [Your Name]\nLocation: [Your Location]\n\nProfessional Summary:\n[Professional summary placeholder]\n\nExperience:\n- [Company] - [Position] ([Date range])\n- [Previous company] - [Position] ([Date range])\n\nEducation:\n- [Degree], [Institution] ([Year])\n\nSkills:\n- [Major skill categories]\n\nType EXPERIENCE, EDUCATION, or SKILLS for more details.",
    "SKILLS": "SKILLS\n\n[Skill Category 1]:\n- [Specific skills]\n\n[Skill Category 2]:\n- [Specific skills]\n\n[Skill Category 3]:\n- [Specific skills]",
    "EXPERIENCE": "WORK EXPERIENCE\n\n[Company Name] - [Position]\n[Date Range]\n\n- [Achievement or responsibility]\n- [Achievement or responsibility]\n- [Achievement or responsibility]\n\n[Previous Company] - [Position]\n[Date Range]\n\n- [Achievement or responsibility]\n- [Achievement or responsibility]",
    "EDUCATION": "EDUCATION\n\n[Degree] - [Institution]\n[Date Range]\n\n- [Notable achievement or detail]\n- [Notable achievement or detail]",
    "PROJECTS": "PROJECTS\n\n[Project Name]\n[Brief description]\nTechnologies: [Technologies used]\n\n[Project Name]\n[Brief description]\nTechnologies: [Technologies used]",
    "CONTACT": "CONTACT INFORMATION\n\nEmail: [Your Email]\nWebsite: [Your Website]\n[Any other contact methods]",
    "ABOUT": "ABOUT THIS TERMINAL\n\nThis is a retro-style terminal CV interface.\nIt uses Claude AI to answer questions about me.\n\nCreated using Streamlit and Python.\nRunning in demo mode without API connection.",
}

# Initialize session state for conversation history
if 'messages' not in st.session_state:
    st.session_state.messages = []

# Initialize session state for conversation with Claude
if 'conversation' not in st.session_state:
    st.session_state.conversation = []

# Initialize session state for demo mode
if 'demo_mode' not in st.session_state:
    st.session_state.demo_mode = True

# Sidebar for settings
with st.sidebar:
    st.title("Settings")
    
    # API key input
    api_key = st.text_input("Claude API Key", type="password", key="api_key")
    
    # Mode selection
    if st.button("Save API Key"):
        if api_key:
            st.session_state.demo_mode = False
            st.success("API key saved! Using Claude API.")
        else:
            st.session_state.demo_mode = True
            st.warning("No API key provided. Using demo mode.")
    
    # Demo mode button
    if st.button("Use Demo Mode"):
        st.session_state.demo_mode = True
        st.info("Demo mode activated. Using pre-defined responses.")
    
    st.markdown("---")
    st.markdown("### About")
    st.markdown("This is a retro terminal-style CV interface.")
    st.markdown("Created with Streamlit and Claude API.")
    st.markdown("© 2025")

# Terminal header
terminal_header = """
<div class="terminal-header">
    <div>PERSONAL TERMINAL v1.0</div>
    <div>{}</div>
</div>
""".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

# Display terminal container
st.markdown('<div class="terminal-container">', unsafe_allow_html=True)
st.markdown(terminal_header, unsafe_allow_html=True)

# Display ASCII art
st.markdown(f'<div class="ascii-art">{ASCII_ART}</div>', unsafe_allow_html=True)

# Display welcome message if no messages yet
if not st.session_state.messages:
    st.markdown('<div class="terminal-system">INITIALIZING PERSONAL CV TERMINAL...</div>', unsafe_allow_html=True)
    st.markdown('<div class="terminal-system">Type HELP for available commands</div>', unsafe_allow_html=True)

# Display conversation history
for message in st.session_state.messages:
    role_class = f"terminal-{message['role']}"
    text = message['content'].replace('\n', '<br>')
    st.markdown(f'<div class="{role_class}">{text}</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# Input field
user_input = st.text_input("Enter command:", key="user_input")

# Process input when submitted
if user_input:
    # Special command: CLEAR
    if user_input.upper() == "CLEAR":
        st.session_state.messages = []
        st.experimental_rerun()
    
    # Add user message to display
    st.session_state.messages.append({"role": "user", "content": f"> {user_input}"})
    
    # Add to Claude conversation
    st.session_state.conversation.append({"role": "user", "content": user_input})
    
    # Process in demo mode or with Claude API
    if st.session_state.demo_mode:
        time.sleep(0.5)  # Simulate processing time
        command = user_input.upper()
        
        if command in DEMO_RESPONSES:
            response = DEMO_RESPONSES[command]
        else:
            response = "I don't understand that command. Type HELP for available commands."
            
            if command != user_input.upper():  # Not a command
                response = "I'll try to answer that query...\n\nThis is demo mode, so I can only respond to basic commands. For a full interactive experience, please set up your Claude API key in the settings panel."
    else:
        try:
            # Use Claude API
            client = anthropic.Anthropic(api_key=api_key)
            
            message = client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=1024,
                system=f"You are a retro terminal CV interface. You have access to the following information about the person:\n\n{CV_INFO}\n\nYour responses should be concise and formatted for a terminal interface. Use simple formatting, avoid complex markdown. Respond to queries about the person's experience, skills, education, and background using the information provided. If asked something not in the CV, say you don't have that information in your database. For commands, respond to at least: HELP, CV, SKILLS, EXPERIENCE, EDUCATION, CONTACT, PROJECTS, ABOUT. Help command should list available commands.",
                messages=st.session_state.conversation[-10:]  # Keep context manageable
            )
            
            response = message.content[0].text
            
        except Exception as e:
            response = f"ERROR: Unable to connect to Claude API. {str(e)}"
            st.error(f"API Error: {str(e)}")
            
            # Fallback to demo mode for HELP command
            if user_input.upper() == "HELP":
                response = DEMO_RESPONSES["HELP"]
    
    # Add response to conversation history
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.session_state.conversation.append({"role": "assistant", "content": response})
    
    # Rerun to update display
    st.experimental_rerun()
