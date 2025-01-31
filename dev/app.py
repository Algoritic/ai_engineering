import streamlit as st
from openai import OpenAI
import redis

# Initialize Redis connection
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

# Initialize OpenAI client
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Initialize session state for chat history and model switch counter
if "messages" not in st.session_state:
    st.session_state.messages = []
if "model_switch_counter" not in st.session_state:
    st.session_state.model_switch_counter = 0

# Function to generate response from OpenAI API
def generate_response(prompt, model):
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

# Streamlit app
st.title("LLM Model Switcher Demo")

# Display chat messages from history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Get user input
if prompt := st.chat_input("What is up?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Increment model switch counter in Redis
    redis_client.incr("model_switch_counter")
    current_counter = int(redis_client.get("model_switch_counter"))

    # Choose model based on counter value
    if current_counter <= 2:
        model = "gpt-4"  # Use gpt-4 for the first two responses
    else:
        model = "gpt-3.5-turbo"  # Switch to gpt-3.5-turbo after two responses

    # Generate response and add it to chat history
    response = generate_response(prompt, model)
    st.session_state.messages.append({"role": "assistant", "content": response})

    # Display assistant response
    with st.chat_message("assistant"):
        st.markdown(response)