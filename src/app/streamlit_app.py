import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
from agents.basic_mission_data import BasicMissionData
from agents.technical_data import TechnicalData
from agents.launch_data import LaunchData
from agents.cost_and_other_data import CostAndOtherData
import json
import re
import io
import pandas as pd

st.set_page_config(page_title="Satellite Data Extraction", layout="wide")

# Sidebar navigation with icons and section dividers
st.sidebar.markdown("""
<style>
.sidebar-title {
    font-size: 1.3em;
    font-weight: bold;
    margin-bottom: 0.5em;
}
.sidebar-section {
    margin-bottom: 1.5em;
}
.sidebar-radio label {
    font-size: 1.1em;
    padding-left: 0.5em;
}
</style>
""", unsafe_allow_html=True)

st.sidebar.markdown('<div class="sidebar-title">🛰️ Satellite Data App</div>', unsafe_allow_html=True)

st.sidebar.markdown('<div class="sidebar-section">🔎 <b>Navigation</b></div>', unsafe_allow_html=True)
page = st.sidebar.radio(
    "",
    (
        "🏠 Home",
        "📝 Basic Mission Data",
        "🔬 Technical Data",
        "🚀 Launch Data",
        "💰 Cost & Other Data"
    ),
    key="sidebar_radio"
)

st.sidebar.markdown('<div class="sidebar-section">🛰️ <b>Satellite Name</b></div>', unsafe_allow_html=True)
satellite_name = st.sidebar.text_input("", value="Aditya-L1", key="sidebar_satellite_name", help="Enter the name of the satellite you want to query.")

st.sidebar.markdown('<hr style="margin: 1em 0;">', unsafe_allow_html=True)
st.sidebar.info("Select a section and enter a satellite name to get started!", icon="ℹ️")

# Session state for results and thoughts
if 'results' not in st.session_state:
    st.session_state['results'] = {
        'basic': None,
        'technical': None,
        'launch': None,
        'cost': None
    }
if 'thoughts' not in st.session_state:
    st.session_state['thoughts'] = {
        'basic': None,
        'technical': None,
        'launch': None,
        'cost': None
    }

# --- AGENT STOP BUTTON LOGIC ---
if 'stop_agent' not in st.session_state:
    st.session_state['stop_agent'] = False

if 'basic_running' not in st.session_state:
    st.session_state['basic_running'] = False

# Add running state flags for other agents
if 'technical_running' not in st.session_state:
    st.session_state['technical_running'] = False
if 'launch_running' not in st.session_state:
    st.session_state['launch_running'] = False
if 'cost_running' not in st.session_state:
    st.session_state['cost_running'] = False

def stop_agent():
    st.session_state['stop_agent'] = True

def reset_stop_agent():
    st.session_state['stop_agent'] = False

def run_agent(agent, key):
    result = agent.call(satellite_name)
    # Try to extract agent's thinking (if present)
    thoughts = None
    if 'raw_output' in result and result['raw_output']:
        import re
        pattern = r"(Thought:.*?)(?=Final Answer:|$)"
        matches = re.findall(pattern, result['raw_output'], re.DOTALL)
        if matches:
            thoughts = '\n---\n'.join([m.strip() for m in matches])
        else:
            thoughts = result['raw_output']
    st.session_state['results'][key] = result
    st.session_state['thoughts'][key] = thoughts

def render_links(data):
    if not isinstance(data, dict):
        return
    url_pattern = re.compile(r"https?://[\w\.-]+(?:/[\w\./\-\?&=%#]*)?")
    for key, value in data.items():
        if isinstance(value, str) and url_pattern.match(value):
            st.markdown(f"[{key.replace('_', ' ').title()}]({value})", unsafe_allow_html=True)

def format_key(key):
    # Convert snake_case or camelCase to Title Case with spaces
    key = re.sub(r'(_|-)+', ' ', key)  # snake_case or kebab-case to spaces
    key = re.sub(r'([a-z])([A-Z])', r'\1 \2', key)  # camelCase to spaces
    return key.strip().title()

def pretty_print_dict_table(d, indent=0):
    rows = []
    for key, value in d.items():
        display_key = format_key(key)
        cell_style = f"vertical-align:top; font-weight:bold; padding-left:{indent*16}px; padding: 0.5em 0.7em;"
        value_style = "padding: 0.5em 0.7em;"
        if isinstance(value, dict):
            nested = pretty_print_dict_table(value, indent + 1)
            rows.append(f"<tr><td style='{cell_style}'>{display_key}:</td><td style='{value_style}'>{nested}</td></tr>")
        elif isinstance(value, str) and value.startswith("http"):
            rows.append(f"<tr><td style='{cell_style}'>{display_key}:</td><td style='{value_style}'><a href='{value}' target='_blank'>{value}</a></td></tr>")
        else:
            rows.append(f"<tr><td style='{cell_style}'>{display_key}:</td><td style='{value_style}'>{value}</td></tr>")
    table = "<table style='width:100%; border-collapse:separate; border-spacing:0 0.3em;'>" + "".join(rows) + "</table>"
    return table

if page.startswith("🏠"):
    st.markdown("""
    <div style="display: flex; align-items: center; justify-content: space-between;">
        <div>
            <h1 style="margin-bottom: 0.2em;">🛰️ Satellite Data Extraction Chatbot</h1>
            <h3 style="color: #4F8BF9; margin-top: 0;">Your AI-powered tool for satellite research and insights</h3>
        </div>
        <img src="https://images.unsplash.com/photo-1464983953574-0892a716854b?auto=format&fit=crop&w=400&q=80" style="border-radius: 1em; margin-left: 2em; max-height: 120px;"/>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("""
    <div style="font-size: 1.15em; margin-top: 1em;">
    Welcome to the <b>Satellite Data Extraction Chatbot</b>! This app lets you:
    <ul>
        <li>🔍 <b>Search for any satellite</b> by name</li>
        <li>📝 <b>Extract mission, technical, launch, and cost data</b> using advanced AI agents</li>
        <li>👀 <b>See the agent's reasoning</b> for transparency</li>
        <li>💡 <b>Get results in a clean, organized format</b></li>
    </ul>
    <b>How to use:</b> Enter a satellite name in the sidebar, then use the navigation to run each agent. Each section has a button to run the agent, a dropdown to view the agent's reasoning, and a clear, formatted display of the extracted data.
    </div>
    <br>
    <div style="
        background: #232946;
        border-radius: 1em;
        padding: 1.3em 1.5em;
        margin-top: 1.2em;
        color: #f4f4f8;
        font-weight: 500;
        box-shadow: 0 2px 8px rgba(30,40,60,0.10);
        display: flex;
        align-items: flex-start;
        gap: 1em;
    ">
        <span style="font-size: 2em; line-height: 1;">💡</span>
        <div style="font-size: 1.08em;">
            <b style="color: #a1a7bb;">Tip:</b> Try satellites like 
            <span style='display: inline-block; background: #35374b; color: #f4f4f8; border-radius: 0.4em; padding: 0.13em 0.5em; font-size: 1em; margin-right: 0.2em;'>Aditya-L1</span>
            <span style='display: inline-block; background: #35374b; color: #f4f4f8; border-radius: 0.4em; padding: 0.13em 0.5em; font-size: 1em; margin-right: 0.2em;'>Cartosat-3</span>
            <span style='display: inline-block; background: #35374b; color: #f4f4f8; border-radius: 0.4em; padding: 0.13em 0.5em; font-size: 1em; margin-right: 0.2em;'>Chandrayaan-3</span>
            <span style='display: inline-block; background: #35374b; color: #f4f4f8; border-radius: 0.4em; padding: 0.13em 0.5em; font-size: 1em; margin-right: 0.2em;'>Sentinel-2A</span>
            <span style='display: inline-block; background: #35374b; color: #f4f4f8; border-radius: 0.4em; padding: 0.13em 0.5em; font-size: 1em;'>Hubble</span>, etc.
        </div>
    </div>
    <br>
    <div style="text-align: center; margin-top: 2em;">
        <a href="https://github.com/your-repo" target="_blank" style="color: #a1a7bb; font-weight: bold; text-decoration: none;">🌐 View on GitHub</a>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    st.caption("Developed with ❤️ using Streamlit and LangChain agents. UI will be enhanced with more features soon!")

if page.startswith("📝"):
    st.header("📝 Basic Mission Data")
    st.info("Extracts general mission details, orbit, and payload info.", icon="🛰️")
    st.markdown("<hr>", unsafe_allow_html=True)
    col1, col2 = st.columns([2,1])
    run_pressed = col1.button("Run Basic Mission Agent", key="run_basic", use_container_width=True)
    stop_pressed = col2.button("Stop Agent", key="stop_basic", use_container_width=True)
    if run_pressed:
        reset_stop_agent()
        st.session_state['basic_running'] = True
        with st.spinner("Running Basic Mission Data Agent..."):
            run_agent(BasicMissionData(), 'basic')
        st.session_state['basic_running'] = False
    if stop_pressed:
        stop_agent()
    # Show message if agent was stopped
    if st.session_state.get('stop_agent') and run_pressed:
        st.warning("🛑 You have stopped the agent execution.")
    if st.session_state.get('basic_running', False):
        st.info("⏳ Agent is running in the background. Please wait...")
    if st.session_state['results']['basic']:
        with st.expander("Show Agent's Thinking (Basic Mission Data)", expanded=False):
            raw_output = st.session_state['results']['basic'].get('raw_output')
            if raw_output:
                st.code(raw_output, language="markdown")
            else:
                st.code(st.session_state['thoughts']['basic'] or "No reasoning available.", language="markdown")
        st.subheader("Extracted Data:")
        st.markdown(pretty_print_dict_table(st.session_state['results']['basic']), unsafe_allow_html=True)
        # Download section
        result = st.session_state['results']['basic']
        if isinstance(result, dict):
            # Remove raw_output and error fields for CSV
            csv_data = {k: v for k, v in result.items() if k not in ('raw_output', 'error', 'satellite_name')}
            df = pd.DataFrame([csv_data])
            csv_buffer = io.StringIO()
            df.to_csv(csv_buffer, index=False)
            st.download_button(
                label="Download as CSV",
                data=csv_buffer.getvalue(),
                file_name=f"basic_mission_data_{satellite_name}.csv",
                mime="text/csv"
            )

if page.startswith("🔬"):
    st.header("🔬 Technical Data")
    st.info("Extracts sensor specs, spectral bands, and technological breakthroughs.", icon="🔬")
    st.markdown("<hr>", unsafe_allow_html=True)
    col1, col2 = st.columns([2,1])
    run_pressed = col1.button("Run Technical Data Agent", key="run_technical", use_container_width=True)
    stop_pressed = col2.button("Stop Agent", key="stop_technical", use_container_width=True)
    if run_pressed:
        reset_stop_agent()
        st.session_state['technical_running'] = True
        with st.spinner("Running Technical Data Agent..."):
            run_agent(TechnicalData(), 'technical')
        st.session_state['technical_running'] = False
    if stop_pressed:
        stop_agent()
    if st.session_state.get('stop_agent') and run_pressed:
        st.warning("🛑 You have stopped the agent execution.")
    if st.session_state.get('technical_running', False):
        st.info("⏳ Agent is running in the background. Please wait...")
    if st.session_state['results']['technical']:
        with st.expander("Show Agent's Thinking (Technical Data)", expanded=False):
            raw_output = st.session_state['results']['technical'].get('raw_output')
            if raw_output:
                st.code(raw_output, language="markdown")
            else:
                st.code(st.session_state['thoughts']['technical'] or "No reasoning available.", language="markdown")
        st.subheader("Extracted Data:")
        st.markdown(pretty_print_dict_table(st.session_state['results']['technical']), unsafe_allow_html=True)
        # Download section
        result = st.session_state['results']['technical']
        if isinstance(result, dict):
            csv_data = {k: v for k, v in result.items() if k not in ('raw_output', 'error', 'satellite_name')}
            df = pd.DataFrame([csv_data])
            csv_buffer = io.StringIO()
            df.to_csv(csv_buffer, index=False)
            st.download_button(
                label="Download as CSV",
                data=csv_buffer.getvalue(),
                file_name=f"technical_data_{satellite_name}.csv",
                mime="text/csv"
            )

if page.startswith("🚀"):
    st.header("🚀 Launch Data")
    st.info("Extracts launch mass, success, and reusability details.", icon="🚀")
    st.markdown("<hr>", unsafe_allow_html=True)
    col1, col2 = st.columns([2,1])
    run_pressed = col1.button("Run Launch Data Agent", key="run_launch", use_container_width=True)
    stop_pressed = col2.button("Stop Agent", key="stop_launch", use_container_width=True)
    if run_pressed:
        reset_stop_agent()
        st.session_state['launch_running'] = True
        with st.spinner("Running Launch Data Agent..."):
            run_agent(LaunchData(), 'launch')
        st.session_state['launch_running'] = False
    if stop_pressed:
        stop_agent()
    if st.session_state.get('stop_agent') and run_pressed:
        st.warning("🛑 You have stopped the agent execution.")
    if st.session_state.get('launch_running', False):
        st.info("⏳ Agent is running in the background. Please wait...")
    if st.session_state['results']['launch']:
        with st.expander("Show Agent's Thinking (Launch Data)", expanded=False):
            raw_output = st.session_state['results']['launch'].get('raw_output')
            if raw_output:
                st.code(raw_output, language="markdown")
            else:
                st.code(st.session_state['thoughts']['launch'] or "No reasoning available.", language="markdown")
        st.subheader("Extracted Data:")
        st.markdown(pretty_print_dict_table(st.session_state['results']['launch']), unsafe_allow_html=True)
        # Download section
        result = st.session_state['results']['launch']
        if isinstance(result, dict):
            csv_data = {k: v for k, v in result.items() if k not in ('raw_output', 'error', 'satellite_name')}
            df = pd.DataFrame([csv_data])
            csv_buffer = io.StringIO()
            df.to_csv(csv_buffer, index=False)
            st.download_button(
                label="Download as CSV",
                data=csv_buffer.getvalue(),
                file_name=f"launch_data_{satellite_name}.csv",
                mime="text/csv"
            )

if page.startswith("💰"):
    st.header("💰 Cost & Other Data")
    st.info("Extracts mission cost, launch cost, vehicle type, and launch date.", icon="💰")
    st.markdown("<hr>", unsafe_allow_html=True)
    col1, col2 = st.columns([2,1])
    run_pressed = col1.button("Run Cost & Other Data Agent", key="run_cost", use_container_width=True)
    stop_pressed = col2.button("Stop Agent", key="stop_cost", use_container_width=True)
    if run_pressed:
        reset_stop_agent()
        st.session_state['cost_running'] = True
        with st.spinner("Running Cost & Other Data Agent..."):
            run_agent(CostAndOtherData(), 'cost')
        st.session_state['cost_running'] = False
    if stop_pressed:
        stop_agent()
    if st.session_state.get('stop_agent') and run_pressed:
        st.warning("🛑 You have stopped the agent execution.")
    if st.session_state.get('cost_running', False):
        st.info("⏳ Agent is running in the background. Please wait...")
    if st.session_state['results']['cost']:
        with st.expander("Show Agent's Thinking (Cost & Other Data)", expanded=False):
            raw_output = st.session_state['results']['cost'].get('raw_output')
            if raw_output:
                st.code(raw_output, language="markdown")
            else:
                st.code(st.session_state['thoughts']['cost'] or "No reasoning available.", language="markdown")
        st.subheader("Extracted Data:")
        st.markdown(pretty_print_dict_table(st.session_state['results']['cost']), unsafe_allow_html=True)
        # Download section
        result = st.session_state['results']['cost']
        if isinstance(result, dict):
            csv_data = {k: v for k, v in result.items() if k not in ('raw_output', 'error', 'satellite_name')}
            df = pd.DataFrame([csv_data])
            csv_buffer = io.StringIO()
            df.to_csv(csv_buffer, index=False)
            st.download_button(
                label="Download as CSV",
                data=csv_buffer.getvalue(),
                file_name=f"cost_data_{satellite_name}.csv",
                mime="text/csv"
            )
