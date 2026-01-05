"""
Financial Detective - Streamlit Frontend
Web UI for extracting knowledge graphs from financial documents
"""

import streamlit as st
import os
import json
import tempfile
from pathlib import Path
from financial_detective import FinancialDetective
import base64

st.set_page_config(
    page_title="Financial Detective",
    page_icon="🕵️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    :root {
        --primary: #1f77b4;
        --secondary: #ff7f0e;
        --success: #2ca02c;
        --danger: #d62728;
        --text: #1e293b;
        --gray: #64748b;
        --border: #e2e8f0;
    }
    
    * { font-family: 'Inter', sans-serif; }
    
    .main .block-container {
        padding: 2rem 1rem;
        max-width: 1200px;
    }
    
    h1 {
        color: var(--primary) !important;
        font-weight: 700 !important;
        font-size: 2.5rem !important;
        text-align: center;
        margin-bottom: 0.5rem !important;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, var(--primary), var(--secondary)) !important;
        color: white !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        padding: 0.7rem 1.5rem !important;
        border: none !important;
        box-shadow: 0 2px 8px rgba(31, 119, 180, 0.2) !important;
        transition: all 0.2s !important;
    }
    
    .stButton > button:hover {
        box-shadow: 0 4px 12px rgba(31, 119, 180, 0.35) !important;
        transform: translateY(-1px) !important;
    }
    
    .metric-card {
        background: white;
        border-radius: 10px;
        padding: 1rem;
        border: 1px solid var(--border);
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
    }
    
    .entity-card {
        background: #f8f9fa;
        border-radius: 8px;
        padding: 0.8rem;
        margin-bottom: 0.5rem;
        border-left: 4px solid var(--primary);
    }
    
    .relationship-card {
        background: #fff5e6;
        border-radius: 8px;
        padding: 0.8rem;
        margin-bottom: 0.5rem;
        border-left: 4px solid var(--secondary);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'graph_data' not in st.session_state:
    st.session_state.graph_data = None
if 'extraction_complete' not in st.session_state:
    st.session_state.extraction_complete = False

def check_api_key(provider: str) -> bool:
    """Check if API key is available"""
    if provider == "groq":
        return bool(os.getenv("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY", None))
    else:
        return bool(os.getenv("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY", None))

def get_api_key(provider: str) -> str:
    """Get API key from secrets or environment"""
    try:
        if provider == "groq":
            return st.secrets.get("GROQ_API_KEY") or os.getenv("GROQ_API_KEY", "")
        else:
            return st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY", "")
    except:
        if provider == "groq":
            return os.getenv("GROQ_API_KEY", "")
        else:
            return os.getenv("OPENAI_API_KEY", "")

# Header
st.title("🕵️ Financial Detective")
st.markdown("<p style='text-align: center; color: var(--gray); font-size: 1.1rem;'>Extract Knowledge Graphs from Financial Documents</p>", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # API Provider Selection
    api_provider = st.radio(
        "LLM Provider",
        ["groq", "openai"],
        help="Groq (faster, free tier) or OpenAI GPT-4o (more accurate)"
    )
    
    # API Key Status
    has_key = check_api_key(api_provider)
    if has_key:
        st.success(f"✅ {api_provider.upper()} API Key Found")
    else:
        st.error(f"❌ {api_provider.upper()} API Key Not Found")
        st.info(f"Please set {api_provider.upper()}_API_KEY in environment or Streamlit secrets")
    
    st.divider()
    
    # Options
    st.header("📊 Visualization Options")
    generate_viz = st.checkbox("Generate NetworkX Visualization", value=True)
    generate_mermaid = st.checkbox("Generate Mermaid Chart", value=True)
    
    st.divider()
    
    # Info
    st.info("""
    **How it works:**
    1. Upload or paste your financial document
    2. Select LLM provider
    3. Click "Extract Knowledge Graph"
    4. View results and download outputs
    """)

# Main Content
tab1, tab2, tab3 = st.tabs(["📄 Input", "📊 Results", "📥 Downloads"])

with tab1:
    st.header("Upload or Paste Document")
    
    # Input method selection
    input_method = st.radio(
        "Choose input method:",
        ["Upload File", "Paste Text"],
        horizontal=True
    )
    
    text_content = None
    
    if input_method == "Upload File":
        uploaded_file = st.file_uploader(
            "Upload a text file",
            type=['txt'],
            help="Upload a .txt file containing financial document text"
        )
        
        if uploaded_file is not None:
            text_content = uploaded_file.read().decode('utf-8')
            st.success(f"✅ File uploaded: {uploaded_file.name} ({len(text_content)} characters)")
            
            with st.expander("📄 Preview uploaded content"):
                st.text_area("Content preview", text_content[:1000] + "..." if len(text_content) > 1000 else text_content, height=200)
    
    else:  # Paste Text
        text_content = st.text_area(
            "Paste your financial document text here:",
            height=400,
            placeholder="Paste the text from your annual report, financial statement, or other document here..."
        )
        
        if text_content:
            st.info(f"📝 {len(text_content)} characters entered")
    
    # Extract button
    if text_content and has_key:
        st.divider()
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            extract_button = st.button(
                "🔍 Extract Knowledge Graph",
                type="primary",
                use_container_width=True
            )
        
        if extract_button:
            # Save text to temp file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as tmp_file:
                tmp_file.write(text_content)
                tmp_file_path = tmp_file.name
            
            try:
                # Initialize detector
                api_key = get_api_key(api_provider)
                detector = FinancialDetective(api_provider=api_provider, api_key=api_key)
                
                # Show progress
                with st.spinner(f"🤖 Extracting entities and relationships using {api_provider.upper()}..."):
                    graph_data = detector.extract_knowledge_graph(tmp_file_path)
                
                # Store in session state
                st.session_state.graph_data = graph_data
                st.session_state.extraction_complete = True
                
                st.success("✅ Extraction complete!")
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ Error during extraction: {str(e)}")
                st.exception(e)
            finally:
                # Cleanup temp file
                if os.path.exists(tmp_file_path):
                    os.unlink(tmp_file_path)
    
    elif text_content and not has_key:
        st.warning("⚠️ Please configure API key in sidebar to proceed")

with tab2:
    st.header("📊 Extraction Results")
    
    if st.session_state.extraction_complete and st.session_state.graph_data:
        graph_data = st.session_state.graph_data
        
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Entities", len(graph_data['entities']))
        
        with col2:
            companies = sum(1 for e in graph_data['entities'] if e['type'] == 'Company')
            st.metric("Companies", companies)
        
        with col3:
            amounts = sum(1 for e in graph_data['entities'] if e['type'] == 'Amount')
            st.metric("Amounts", amounts)
        
        with col4:
            st.metric("Relationships", len(graph_data['relationships']))
        
        st.divider()
        
        # Entities section
        st.subheader("🏢 Entities")
        
        # Filter by type
        entity_types = st.multiselect(
            "Filter by type:",
            ["Company", "RiskFactor", "Amount"],
            default=["Company", "RiskFactor", "Amount"]
        )
        
        filtered_entities = [e for e in graph_data['entities'] if e['type'] in entity_types]
        
        for entity in filtered_entities:
            type_emoji = {
                "Company": "🏢",
                "RiskFactor": "⚠️",
                "Amount": "💰"
            }.get(entity['type'], "📌")
            
            with st.expander(f"{type_emoji} {entity['name']} ({entity['type']})"):
                st.json(entity)
        
        st.divider()
        
        # Relationships section
        st.subheader("🔗 Relationships")
        
        for rel in graph_data['relationships']:
            # Find source and target names
            source_name = next((e['name'] for e in graph_data['entities'] if e['id'] == rel['source']), rel['source'])
            target_name = next((e['name'] for e in graph_data['entities'] if e['id'] == rel['target']), rel['target'])
            
            st.markdown(f"**{source_name}** --[{rel['type']}]--> **{target_name}**")
            with st.expander("Details"):
                st.json(rel)
        
        st.divider()
        
        # Visualizations
        if generate_viz or generate_mermaid:
            st.subheader("📈 Visualizations")
            
            if generate_viz:
                try:
                    # Generate visualization
                    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_viz:
                        tmp_viz_path = tmp_viz.name
                    
                    detector = FinancialDetective(api_provider=api_provider, api_key=get_api_key(api_provider))
                    detector.visualize_graph(graph_data, tmp_viz_path)
                    
                    # Display image
                    st.image(tmp_viz_path, caption="Knowledge Graph Visualization (NetworkX)")
                    
                    # Cleanup
                    if os.path.exists(tmp_viz_path):
                        os.unlink(tmp_viz_path)
                except Exception as e:
                    st.error(f"Error generating visualization: {e}")
            
            if generate_mermaid:
                try:
                    # Generate Mermaid chart
                    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as tmp_mermaid:
                        tmp_mermaid_path = tmp_mermaid.name
                    
                    detector = FinancialDetective(api_provider=api_provider, api_key=get_api_key(api_provider))
                    detector.generate_mermaid_chart(graph_data, tmp_mermaid_path)
                    
                    # Read and display
                    with open(tmp_mermaid_path, 'r', encoding='utf-8') as f:
                        mermaid_content = f.read()
                    
                    st.markdown("### Mermaid Chart")
                    st.code(mermaid_content, language='markdown')
                    st.info("💡 Copy the Mermaid code above and paste it into https://mermaid.live to view the interactive chart")
                    
                    # Cleanup
                    if os.path.exists(tmp_mermaid_path):
                        os.unlink(tmp_mermaid_path)
                except Exception as e:
                    st.error(f"Error generating Mermaid chart: {e}")
        
        # Full JSON view
        st.divider()
        st.subheader("📋 Full JSON Output")
        with st.expander("View complete JSON"):
            st.json(graph_data)
    
    else:
        st.info("👆 Go to the 'Input' tab to upload a document and extract a knowledge graph")

with tab3:
    st.header("📥 Download Outputs")
    
    if st.session_state.extraction_complete and st.session_state.graph_data:
        graph_data = st.session_state.graph_data
        
        # JSON download
        json_str = json.dumps(graph_data, indent=2, ensure_ascii=False)
        st.download_button(
            label="⬇️ Download JSON (graph_output.json)",
            data=json_str,
            file_name="graph_output.json",
            mime="application/json",
            use_container_width=True
        )
        
        # Generate and download visualization if requested
        if generate_viz:
            try:
                with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_viz:
                    tmp_viz_path = tmp_viz.name
                
                detector = FinancialDetective(api_provider=api_provider, api_key=get_api_key(api_provider))
                detector.visualize_graph(graph_data, tmp_viz_path)
                
                with open(tmp_viz_path, 'rb') as f:
                    viz_bytes = f.read()
                
                st.download_button(
                    label="⬇️ Download Visualization (graph_visualization.png)",
                    data=viz_bytes,
                    file_name="graph_visualization.png",
                    mime="image/png",
                    use_container_width=True
                )
                
                if os.path.exists(tmp_viz_path):
                    os.unlink(tmp_viz_path)
            except Exception as e:
                st.error(f"Error generating visualization: {e}")
        
        # Generate and download Mermaid if requested
        if generate_mermaid:
            try:
                with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as tmp_mermaid:
                    tmp_mermaid_path = tmp_mermaid.name
                
                detector = FinancialDetective(api_provider=api_provider, api_key=get_api_key(api_provider))
                detector.generate_mermaid_chart(graph_data, tmp_mermaid_path)
                
                with open(tmp_mermaid_path, 'r', encoding='utf-8') as f:
                    mermaid_content = f.read()
                
                st.download_button(
                    label="⬇️ Download Mermaid Chart (graph_mermaid.md)",
                    data=mermaid_content,
                    file_name="graph_mermaid.md",
                    mime="text/markdown",
                    use_container_width=True
                )
                
                if os.path.exists(tmp_mermaid_path):
                    os.unlink(tmp_mermaid_path)
            except Exception as e:
                st.error(f"Error generating Mermaid chart: {e}")
        
        st.success("✅ All outputs ready for download!")
    
    else:
        st.info("👆 Extract a knowledge graph first to download outputs")

# Footer
st.divider()
st.markdown(
    "<p style='text-align: center; color: var(--gray); font-size: 0.9rem;'>"
    "Powered by LLM-based extraction • No regex required • Valid JSON schema"
    "</p>",
    unsafe_allow_html=True
)

