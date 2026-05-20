# Import streamlit for UI
import streamlit as st

# Import Groq for AI API
from groq import Groq

# Import PyPDF2 to read PDFs
import PyPDF2

# Set page title
st.title("🤖 Jarvis AI ")

st.markdown("""
<style>
/* Main background */
.stApp {
    background-color: #0d0d0d;
}

/* Sidebar background */
[data-testid="stSidebar"] {
    background-color: #1a1a1a;
}

/* Title styling */
h1 {
    color: #00ff88;
    font-family: 'Courier New', monospace;
    text-align: center;
}

/* Chat input */
[data-testid="stChatInput"] {
    background-color: #1a1a1a;
    border: 1px solid #00ff88;
    border-radius: 10px;
}

/* Buttons */
.stButton button {
    background-color: #00ff88;
    color: #0d0d0d;
    border-radius: 8px;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)


# Create Groq client with API key
client = Groq(api_key="")

# Set model name
mo = "llama-3.3-70b-versatile"

# First run — create message list with system prompt
# Subsequent runs — already exists, skip
if "message" not in st.session_state:
    st.session_state.message = [{"role": "system", "content": "You are a helpful assistant named Jarvis."}]

# First run — set pdf_loaded to False
if "pdf_loaded" not in st.session_state:
    st.session_state.pdf_loaded = False

# Everything inside this block goes in sidebar
with st.sidebar:

    # File upload widget — accepts jpg, png, pdf, txt
    file = st.file_uploader("Upload file", type=["jpg", "png", "pdf", "txt"])

    # If user uploaded a file
    if file:

        # If it's a PDF
        if file.type == "application/pdf":

            # Only read it once, not on every rerun
            if not st.session_state.pdf_loaded:

                # Create PDF reader object
                reader = PyPDF2.PdfReader(file)

                # Empty string to collect text
                text = ""

                # Loop through all pages and extract text
                for page in reader.pages:
                    text += page.extract_text()

                # Insert PDF as system message at index 1
                # Index 0 is main system prompt, so insert after it
                st.session_state.message.insert(1, {"role": "system", "content": f"You have access to this document. Use it only when relevant:\n{text}"})

                # Mark PDF as loaded so we don't reload it
                st.session_state.pdf_loaded = True

                # Show success message in sidebar
                st.sidebar.success("PDF loaded!")

        # If it's an image — display it in sidebar
        elif file.type.startswith("image"):
            st.image(file)

    # Text input for custom system prompt
    cust = st.text_input("Set custom role")

    # If Apply button clicked
    if st.button("Apply"):

        # Replace system prompt at index 0
        st.session_state.message[0] = {"role": "system", "content": cust}

        # Show confirmation message in chat
        st.session_state.message.append({"role": "assistant", "content": f"Got it! I will now behave as: {cust}"})

        # Force rerun to clear the text input
        st.rerun()
    
# Clear chat button
clear = st.button("Clear chat")

# If clicked — reset everything
if clear:
    st.session_state.message = [{"role": "system", "content": "You are a helpful assistant named Jarvis."}]
    st.session_state.pdf_loaded = False
    st.rerun()

# Display all old messages first
for ms in st.session_state.message:

    # Skip system messages
    
    if ms["role"] == "system":
          continue
    avatar = "🤖" if ms["role"] == "assistant" else "👤"
    #chat bubble based on role
    with st.chat_message(ms["role"], avatar=avatar):
        st.write(ms["content"])

# Chat input — sticks to bottom automatically
inp = st.chat_input("Enter the message")

# If user typed something
if inp:

    # Add user message to history
    st.session_state.message.append({"role": "user", "content": inp})

    # Show user message immediately
    with st.chat_message("user",avatar="👤"):
        st.write(inp)

    # Call Groq API with stream=True
    res = client.chat.completions.create(
        model=mo,
        messages=st.session_state.message,
        stream=True
    )

    # Show assistant bubble and stream reply word by word
    with st.chat_message("assistant",avatar="🤖"):
        reply = st.write_stream(
            # Generator — yields one chunk at a time
            chunk.choices[0].delta.content
            for chunk in res
            if chunk.choices[0].delta.content  # skip empty chunks
        )

    # Save completed reply to history
    st.session_state.message.append({"role": "assistant", "content": reply})
