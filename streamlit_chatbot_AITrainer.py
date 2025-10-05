# Import the necessary libraries
import streamlit as st  # For creating the web app interface
import google.generativeai as genai  # For interacting with the Google Gemini API

# --- 1. Page Configuration and Title ---

# Set the title and a caption for the web page
st.title("💪 Gym & Fitness Consultant")
st.caption("Asisten AI pribadi Anda untuk latihan, nutrisi, dan tujuan kebugaran")

# --- 2. Sidebar for Settings ---

# The sidebar is now simpler, only containing the reset button.
with st.sidebar:
    st.subheader("Controls")
    # Create a button to reset the conversation.
    reset_button = st.button("Reset Conversation", help="Clear all messages and start fresh")

# --- 3. API Key and Model Initialization (MODIFIED SECTION) ---

# Get the API key from Streamlit's secrets management.
try:
    google_api_key = st.secrets["GOOGLE_API_KEY"]
except KeyError:
    # If the key is not found in secrets, show an error and stop.
    st.error("Google AI API Key not found. Please add it to your Streamlit secrets.", icon="🗝️")
    st.stop()

# Initialize the Gemini Model with a system instruction to set its persona.
# This block runs only once per session.
if "gemini_model" not in st.session_state:
    try:
        # Define the persona of the chatbot
        system_instruction = "Anda adalah FitBot, asisten AI yang ramah dan ahli dalam bidang kebugaran, gym, dan nutrisi. Berikan saran yang aman, efektif, dan memotivasi. Selalu prioritaskan keamanan dan sarankan pengguna untuk berkonsultasi dengan profesional untuk nasihat medis. Jawablah selalu dalam Bahasa Indonesia."
        
        # Configure the genai library with the API key
        genai.configure(api_key=google_api_key)

        # Create the model instance with the system instruction
        st.session_state.gemini_model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            system_instruction=system_instruction
        )
    except Exception as e:
        # If the key is invalid or another error occurs, show an error and stop.
        st.error(f"Failed to initialize Gemini model: {e}")
        st.stop()

# --- 4. Chat History Management ---

# Initialize the chat session using the configured model.
if "chat" not in st.session_state:
    # Start a new chat session from the configured model
    st.session_state.chat = st.session_state.gemini_model.start_chat(history=[])

# Initialize the message history (as a list) for display if it doesn't exist.
if "messages" not in st.session_state:
    # Add a welcome message from the assistant
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Halo! Saya FitBot, asisten AI kebugaran pribadi Anda. Tanyakan apa saja tentang rencana latihan, nutrisi, atau tips untuk mencapai tujuan kebugaran Anda! Mari mulai."
        }
    ]

# Handle the reset button click.
if reset_button:
    # If the reset button is clicked, clear the chat object and message history from memory.
    st.session_state.pop("chat", None)
    st.session_state.pop("messages", None)
    # st.rerun() tells Streamlit to refresh the page from the top.
    st.rerun()

# --- 5. Display Past Messages ---

# Loop through every message currently stored in the session state.
for msg in st.session_state.messages:
    # For each message, create a chat message bubble with the appropriate role ("user" or "assistant").
    with st.chat_message(msg["role"]):
        # Display the content of the message using Markdown for nice formatting.
        st.markdown(msg["content"])

# --- 6. Handle User Input and API Communication ---

# Create a chat input box at the bottom of the page.
prompt = st.chat_input("Tanyakan tentang rencana latihan Anda...")

if prompt:
    # 1. Add the user's message to our message history list.
    st.session_state.messages.append({"role": "user", "content": prompt})
    # 2. Display the user's message on the screen immediately for a responsive feel.
    with st.chat_message("user"):
        st.markdown(prompt)

    # 3. Get the assistant's response.
    try:
        # Send the user's prompt to the Gemini API chat session.
        response = st.session_state.chat.send_message(prompt)
        
        # Safely get the text from the response object.
        if hasattr(response, "text"):
            answer = response.text
        else:
            answer = str(response)

    except Exception as e:
        # If any error occurs, create an error message to display to the user.
        answer = f"An error occurred: {e}"
        st.error(answer) # Show error in the app UI as well

    # 4. Display the assistant's response.
    with st.chat_message("assistant"):
        st.markdown(answer)
    # 5. Add the assistant's response to the message history list.
    st.session_state.messages.append({"role": "assistant", "content": answer})

