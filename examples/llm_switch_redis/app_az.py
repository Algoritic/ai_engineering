import streamlit as st
from openai import AzureOpenAI
import redis
import os

# Set environment variables for Azure OpenAI
os.environ["OPENAI_TYPE"] = "azure"
os.environ["AZURE_OPENAI_ENDPOINT"] = st.secrets["AZURE_OPENAI_ENDPOINT"]  # Your Azure OpenAI endpoint
os.environ["AZURE_OPENAI_API_KEY"] = st.secrets["AZURE_OPENAI_API_KEY"]  # Your Azure OpenAI API key
os.environ["OPENAI_API_VERSION"] = st.secrets["AZURE_OPENAI_API_VERSION"]  # Your API version, e.g., "2023-05-15"

# Initialize Redis connection
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

# Initialize Azure OpenAI client
client = AzureOpenAI()

# Initialize session state for chat history and model switch counter
if "messages" not in st.session_state:
    st.session_state.messages = []
if "model_switch_counter" not in st.session_state:
    st.session_state.model_switch_counter = 0

# Function to generate response from Azure OpenAI API
def generate_response(prompt, deployment_name):
    response = client.chat.completions.create(
        model=deployment_name,  # Use deployment name instead of model name
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

    # Choose deployment name based on counter value
    if current_counter <= 2:
        deployment_name = st.secrets["AZURE_OPENAI_DEPLOYMENT_NAME_GPT4O"]  # Your GPT-4o deployment name
    else:
        deployment_name = st.secrets["AZURE_OPENAI_DEPLOYMENT_NAME_GPT4O_MINI"]  # Your GPT--4o mini deployment name

    # Generate response and add it to chat history
    response = generate_response(prompt, deployment_name)
    st.session_state.messages.append({"role": "assistant", "content": response})

    # Display assistant response
    with st.chat_message("assistant"):
        st.markdown(response)
        st.write("model used", deployment_name)