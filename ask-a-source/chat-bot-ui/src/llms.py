import streamlit as st
import requests
import json
import logging
import time
from datetime import datetime
import pickle
import os

# Configure logging (Kubernetes-friendly)
def setup_logging():
    """Setup logging with fallback for containerized environments"""
    handlers = [logging.StreamHandler()]  # Always log to stdout/stderr
    
    # Try to add file handler, but don't fail if filesystem is read-only
    try:
        log_file = os.path.join(os.getcwd(), 'llms_app.log')
        handlers.append(logging.FileHandler(log_file))
    except (PermissionError, OSError):
        # In Kubernetes, filesystem might be read-only
        pass
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=handlers
    )
    return logging.getLogger(__name__)

logger = setup_logging()

# Page configuration
st.set_page_config(
    page_title="Chat Interface",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: 900;
        color: #ffffff;
        text-align: center;
        margin-bottom: 2rem;
        padding: 1.5rem;
        background: linear-gradient(135deg, #87CEEB, #4682B4);
        border-radius: 15px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .section-header {
        font-size: 1.6rem;
        font-weight: 800;
        color: #ffffff;
        padding: 1rem;
        background: linear-gradient(135deg, #ADD8E6, #4682B4);
        border-radius: 10px;
        margin: 1rem 0;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .sidebar-header {
        font-size: 1.4rem;
        font-weight: 700;
        color: #ffffff;
        padding: 0.8rem;
        background: linear-gradient(135deg, #B0E0E6, #4682B4);
        border-radius: 8px;
        margin: 0.5rem 0;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.2);
    }
    
    .query-history-container {
        max-height: 400px;
        overflow-y: auto;
        border: 1px solid #e9ecef;
        border-radius: 8px;
        background-color: #ffffff;
    }
    
    .query-history-item {
        background-color: #ffffff;
        padding: 0.75rem;
        border-bottom: 1px solid #e9ecef;
        cursor: pointer;
        transition: all 0.2s ease;
        text-align: left;
        display: block;
        width: 100%;
        border: none;
        font-size: 0.9rem;
        line-height: 1.4;
    }
    
    .query-history-item:hover {
        background-color: #f8f9fa;
        border-left: 3px solid #4682B4;
        padding-left: 0.7rem;
    }
    
    .query-history-item:last-child {
        border-bottom: none;
    }
    
    .query-preview {
        color: #2c3e50;
        font-weight: 500;
        margin-bottom: 0.3rem;
        display: block;
    }
    
    .query-meta {
        color: #6c757d;
        font-size: 0.8rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .query-model {
        background-color: #e9ecef;
        padding: 0.2rem 0.5rem;
        border-radius: 12px;
        font-size: 0.7rem;
        font-weight: 600;
    }
    
    .stSelectbox > div > div {
        background-color: #f8f9fa;
    }
    
    .stTextArea > div > div > textarea {
        background-color: #f8f9fa;
        border: 2px solid #e9ecef;
        border-radius: 8px;
    }
    
    .response-container {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #1f77b4;
        margin: 1rem 0;
    }
    
    .reference-item {
        background-color: #ffffff;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #dee2e6;
        margin: 0.5rem 0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    
    .error-container {
        background-color: #f8d7da;
        color: #721c24;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #dc3545;
        margin: 1rem 0;
    }
    
    .loading-spinner {
        display: flex;
        justify-content: center;
        align-items: center;
        padding: 2rem;
    }
    
    .response-header {
        font-size: 1.5rem;
        font-weight: 700;
        color: #ffffff;
        padding: 0.8rem;
        background: linear-gradient(135deg, #87CEEB, #4682B4);
        border-radius: 8px;
        margin: 1rem 0;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.2);
    }
    
    .query-header {
        font-size: 1.4rem;
        font-weight: 700;
        color: #2c3e50;
        margin: 1.5rem 0 0.8rem 0;
        padding: 0.5rem 0;
        border-bottom: 3px solid #4682B4;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

def load_query_history():
    """Load query history from file"""
    try:
        if os.path.exists('query_history.pkl'):
            with open('query_history.pkl', 'rb') as f:
                return pickle.load(f)
    except Exception as e:
        logger.error(f"Error loading query history: {e}")
    return []

def save_query_history(history):
    """Save query history to file"""
    try:
        with open('query_history.pkl', 'wb') as f:
            pickle.dump(history, f)
    except Exception as e:
        logger.error(f"Error saving query history: {e}")

def add_to_query_history(query, model):
    """Add a query to history"""
    history = load_query_history()
    
    # Create query entry
    query_entry = {
        'query': query,
        'model': model,
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # Remove duplicate if exists
    history = [h for h in history if h['query'] != query]
    
    # Add to beginning of list
    history.insert(0, query_entry)
    
    # Keep only last 15 queries
    history = history[:15]
    
    save_query_history(history)
    return history

def log_error(error_msg, exception=None):
    """Log errors with timestamp and details"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if exception:
        logger.error(f"{timestamp} - {error_msg}: {str(exception)}")
    else:
        logger.error(f"{timestamp} - {error_msg}")

def validate_inputs(user_text, model):
    """Validate user inputs"""
    errors = []
    
    if not user_text or not user_text.strip():
        errors.append("Please enter a query")
    
    if len(user_text.strip()) < 3:
        errors.append("Query must be at least 3 characters long")
    
    if not model:
        errors.append("Please select a model")
    
    return errors

def display_loading_spinner():
    """Display a loading spinner"""
    return st.empty()

def make_api_request(user_text, model, system, includellms, llmsfileref):
    """Make API request with proper error handling"""
    try:
        logger.info(f"Making API request with model: {model}")
        
        payload = {
            "input": user_text,
            "model": model,
            "systemtext": system,
            "includellms": includellms,
            "llmsfileref": llmsfileref
        }
        
        response = requests.post(
            "http://jarvis-api-app.aws-k8s-d.abbvienet.com/api/llmscheck",
            json=payload,
            timeout=90,
            headers={'Content-Type': 'application/json'}
        )
        
        logger.info(f"API response status: {response.status_code}")
        
        if response.status_code == 200:
            print(response.json())
            return response.json(), None
        else:
            error_msg = f"API returned status {response.status_code}: {response.text}"
            log_error(error_msg)
            return None, error_msg
            
    except requests.exceptions.Timeout:
        error_msg = "Request timed out. Please try again."
        log_error(error_msg)
        return None, error_msg
    except requests.exceptions.ConnectionError:
        error_msg = "Failed to connect to API. Please ensure the server is running."
        log_error(error_msg)
        return None, error_msg
    except Exception as e:
        error_msg = "An unexpected error occurred"
        log_error(error_msg, e)
        return None, f"{error_msg}: {str(e)}"

def display_response(response_data):
    """Display API response in a formatted way"""
    print(response_data.get('sources', ''))
    
    if not response_data:
        return
    
    # Display main content
    contentdata = response_data.get('completion', '')
    content = contentdata.get('content', '')
    if content:
        st.markdown('<div class="response-header">🤖 AI Response</div>', unsafe_allow_html=True)
        st.markdown('<div class="response-container">', unsafe_allow_html=True)
        st.markdown(content)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Display references
    references = contentdata.get('references', [])
    if references:
        st.markdown('<div class="response-header">📚 References</div>', unsafe_allow_html=True)
        
        for i, ref in enumerate(references, 1):
            with st.expander(f"Reference {i}: {ref.get('filename', 'Unknown')}"):
                col1, col2 = st.columns([1, 3])
                
                with col1:
                    st.metric("Relevance Score", f"{ref.get('score', 0):.3f}")
                
                with col2:
                    st.markdown("**Content:**")
                    st.text(ref.get('text', 'No content available'))

def display_response_parsed(response_data):
    """Display API response with parsed JSON structure for RAG responses"""
    if not response_data:
        return
    
    # Display document statistics
    documents_used = response_data.get('documents_used', 0)
    total_documents_found = response_data.get('total_documents_found', 0)
    document_scores = response_data.get('document_scores', [])
    
   
    
    # Display main response
    response_content = response_data.get('response', '')
    if response_content:
        st.markdown('<div class="response-header">🤖 AI Response</div>', unsafe_allow_html=True)
        st.markdown('<div class="response-container">', unsafe_allow_html=True)
        st.markdown(response_content)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Display original RAG response if available
    original_rag_response = response_data.get('original_rag_response', '')
    if original_rag_response:
        with st.expander("🔍 Original RAG Response"):
            st.markdown(original_rag_response)
    
    if documents_used > 0 or total_documents_found > 0:
        st.markdown('<div class="response-header">📊 Document Statistics</div>', unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Documents Used", documents_used)
        with col2:
            st.metric("Total Found", total_documents_found)
        with col3:
            if document_scores:
                avg_score = sum(document_scores) / len(document_scores)
                st.metric("Avg Relevance", f"{avg_score:.3f}")
    # Display sources with scores
    sources = response_data.get('sources', [])
    if sources:
        st.markdown('<div class="response-header">📚 Sources</div>', unsafe_allow_html=True)
        
        for i, source in enumerate(sources):
            # Parse source string to extract filename and score
            # Expected format: "Document X: filename.md (Score: 0.XXX)"
            source_parts = source.split(' (Score: ')
            source_name = source_parts[0] if source_parts else source
            score = None
            
            if len(source_parts) > 1:
                try:
                    score = float(source_parts[1].rstrip(')'))
                except ValueError:
                    pass
            
            with st.expander(f"Source {i+1}: {source_name}"):
                if score is not None:
                    st.metric("Relevance Score", f"{score:.3f}")
                else:
                    st.info("Score not available")
                
                # Display document score from document_scores array if available
                if i < len(document_scores):
                    st.metric("Document Score", f"{document_scores[i]:.5f}")

# Main UI
st.markdown('<h1 class="main-header">🤖 Query Interface</h1>', unsafe_allow_html=True)

# Initialize session state for selected query
if 'selected_query' not in st.session_state:
    st.session_state.selected_query = ""

# Sidebar for configuration
with st.sidebar:
    st.markdown('<div class="sidebar-header">⚙️ Configuration</div>', unsafe_allow_html=True)
    
    # Tree structure display using expanders
    with st.expander("🤖 Select AI Model", expanded=True):
        default_models = [
            "openai:gpt-4o-mini",
            "anthropic:claude-3-sonnet",
            "anthropic:claude-3-haiku",
            "anthropic:claude-3-opus",
            "anthropic:claude-3.5-sonnet",
            "anthropic:claude-3.5-haiku"
        ]
        
        model = st.selectbox(
            "Model",
            default_models,
            help="Choose the AI model for your query",
            label_visibility="collapsed"
        )
        
        # Display selected model in tree format
        st.markdown("**Selected:**")
        st.markdown(f"└── {model}")
    
    with st.expander("🏷️ Brand", expanded=True):
        # Include LLMS option
        includellms = "Yes"
        #includellms = st.radio(
        #    "📄 Include llms.txt",
        #    ["Yes", "No"],
        #    help="Whether to include llms.txt in the search context"
        #)
        
        # LLMS file reference
        llmsfileref = st.radio(
            "Brand Selection",
            ["Rinvoq"],
            help="Select which LLMS file to reference",
            label_visibility="collapsed"
        )
        
        # Display selected brand in tree format
        st.markdown("**Selected:**")
        st.markdown(f"└── {llmsfileref}")
    
    # Query History Section
    st.markdown("---")
    st.markdown('<div class="sidebar-header">📝 Query History</div>', unsafe_allow_html=True)
    
    query_history = load_query_history()
    
    if query_history:
        st.markdown("**Recent Queries:**")
        
        # Create a scrollable container for the query history list
        with st.container():
            st.markdown('<div class="query-history-container">', unsafe_allow_html=True)
            
            for i, entry in enumerate(query_history[:15]):  # Show last 15 queries
                query_preview = entry['query'][:60] + "..." if len(entry['query']) > 60 else entry['query']
                model_short = entry['model'].split(':')[-1]
                
                # Create a column layout for better alignment
                col1, col2 = st.columns([4, 1])
                
                with col1:
                    # Use markdown for the query preview with left alignment
                    st.markdown(f"""
                    <div style="text-align: left; margin-bottom: 0.2rem;">
                        <strong style="color: #2c3e50; font-size: 0.9rem;">{query_preview}</strong>
                    </div>
                    <div style="text-align: left; color: #6c757d; font-size: 0.75rem;">
                        {entry['timestamp']} • <span style="background-color: #e9ecef; padding: 0.1rem 0.4rem; border-radius: 8px; font-weight: 600;">{model_short}</span>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    if st.button(
                        "📋",
                        key=f"history_{i}",
                        help=f"Click to use this query:\n\n{entry['query']}",
                        use_container_width=True
                    ):
                        st.session_state.selected_query = entry['query']
                        st.rerun()
                
                # Add a subtle separator
                if i < len(query_history[:15]) - 1:
                    st.markdown('<hr style="margin: 0.5rem 0; border: none; border-top: 1px solid #e9ecef;">', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Clear history button
        if st.button("🗑️ Clear History", type="secondary"):
            save_query_history([])
            st.rerun()
    else:
        st.info("No previous queries found")
    
    # API Status indicator
    st.markdown("---")
    st.markdown('<div class="sidebar-header">🔗 API Status</div>', unsafe_allow_html=True)
    try:
        # Quick health check (with very short timeout)
        health_response = requests.get("http://127.0.0.1:5000/", timeout=2)
        if health_response.status_code == 200:
            st.success("✅ API Connected")
        else:
            st.warning("⚠️ API Issues")
    except:
        st.error("❌ API Offline")

# Main content area
#col1, col2 = st.columns([2, 1])
col1, = st.columns([3])
with col1:
    # System prompt
    #system = st.text_area(
    #    "🎯 System Prompt (Optional)",
    #    value="You are a helpful assistant. The above is necessary context for the conversation. Include important safety information as separate paragraph. Also include source urls for the information.",
    #    height=100,
    #    help="Customize the AI's behavior and response style"
    #)
    system = ""
    # User query - populate with selected query from history if available
    default_query = st.session_state.selected_query if st.session_state.selected_query else ""
   
    # Add H3 header for the query section
    st.markdown('<h3 class="query-header">💬 Your Query</h3>', unsafe_allow_html=True)
    
    user_text = st.text_area(
        "Query Input",
        value=default_query,
        height=200,
        placeholder="Ask your question here...",
        help="Enter your question or prompt for the AI model",
        label_visibility="collapsed"
    )
    
    # Don't clear the selected query immediately - let it persist until after submission

#with col2:
    #st.markdown("### 📊 Query")
    #st.info("Enter a query and click on submit to get results")
    #if user_text:
    #    word_count = len(user_text.split())
    #    char_count = len(user_text)
    #    st.metric("Words", word_count)
    #    st.metric("Characters", char_count)
    #else:
    #    st.info("Enter a query to see statistics")

# Submit section
#st.markdown("---")
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    submit_button = st.button(
        "🚀 Submit Query",
        type="primary",
        use_container_width=True,
        help="Send your query to the selected AI model"
    )

# Handle submission
if submit_button:
    # Validate inputs
    validation_errors = validate_inputs(user_text, model)
    
    if validation_errors:
        for error in validation_errors:
            st.error(f"❌ {error}")
        logger.warning(f"Validation failed: {validation_errors}")
    else:
        # Show loading spinner
        loading_placeholder = st.empty()
        
        with loading_placeholder.container():
            st.markdown("""
            <div class="loading-spinner">
                <div style="text-align: center;">
                    <h3>🔄 Processing your query...</h3>
                    <p>Please wait while we get your response from the AI model.</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Add a progress bar
            progress_bar = st.progress(0)
            for i in range(100):
                time.sleep(0.01)  # Small delay for visual effect
                progress_bar.progress(i + 1)
        
        # Make API request
        start_time = time.time()
        response_data, error = make_api_request(user_text, model, system, includellms, llmsfileref)
        end_time = time.time()
        
        # Clear loading spinner
        loading_placeholder.empty()
        
        if error:
            st.markdown(f'<div class="error-container"><strong>❌ Error:</strong> {error}</div>', 
                       unsafe_allow_html=True)
        else:
            # Add query to history
            add_to_query_history(user_text, model)
            
            # Clear the selected query after successful submission
            if st.session_state.selected_query:
                st.session_state.selected_query = ""
            
            # Display success metrics
            response_time = end_time - start_time
            st.success(f"✅ Query processed successfully in {response_time:.2f} seconds")
            print(response_data)
            # Display response
            #display_response(response_data)
            display_response_parsed(response_data)
            
            # Log successful request
            logger.info(f"Successful API request - Model: {model}, Response time: {response_time:.2f}s")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; color: #666; padding: 1rem;">
        <small>AI Model Query Interface | Built with Streamlit | 
        <a href="#" style="color: #1f77b4;">Documentation</a> | 
        <a href="#" style="color: #1f77b4;">Support</a>
        </small>
    </div>
    """, 
    unsafe_allow_html=True
)