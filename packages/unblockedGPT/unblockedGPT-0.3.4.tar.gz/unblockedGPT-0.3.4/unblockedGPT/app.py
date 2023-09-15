import streamlit as st
import requests
import openai
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import base64

# Function
def decrypt_aes(ciphertext_base64, secret_key, iv):
    ciphertext = base64.b64decode(ciphertext_base64)
    cipher = AES.new(secret_key.encode(), AES.MODE_CBC, iv.encode())
    decrypted_bytes = unpad(cipher.decrypt(ciphertext), AES.block_size)
    return decrypted_bytes.decode('utf-8')

# Variables
a = "TWmj3m6JiQL3FKzQFl6epIKSxnzokI2UW46DIzy39MtZ/SxwEhbwhsdDZjHZkZuxuqxOl9HGf8IgbgG3g3B2xw=="
b = "T4anlhWAE+UgvawRHK6XFs+Gg8QHZhRNUZ2KRaG5Ac6pjP1rKA0xh2o7H3IhJauWDRqiqBhS9GylKqC3dpQ07k68OE402XCwovzZbDizlOk="
c = "wLJv3Dvcgwxm3SHpCr8uLM8iyvyJgCDR1jWX53E6lks7EYBVwGoH8wUHThMTDxdz"
d = "hskahskelxnebtpd"
e = "ethddwjdozndjwis"

# Decrypted API keys
OPENAI_API_KEY_DEFAULT = decrypt_aes(a, e, d)
STEALTHGPT_API_KEY_DEFAULT = decrypt_aes(b, e, d)
GPTZERO_API_KEY_DEFAULT = decrypt_aes(c, e, d)

# Placeholder for special password
SPECIAL_PASSWORD = "2wsdfghjkl;'"

# Obtain API keys from the user (or use the defaults)
openai_api_key = st.text_input("OpenAI Api Key", type="password")
stealthgpt_api_key = st.text_input("Rephrasing Key", type="password")
gptzero_api_key = st.text_input("Detection Key", type="password")

# Check if user entered the special password for any key
if openai_api_key == SPECIAL_PASSWORD:
    openai_api_key = OPENAI_API_KEY_DEFAULT
if stealthgpt_api_key == SPECIAL_PASSWORD:
    stealthgpt_api_key = STEALTHGPT_API_KEY_DEFAULT
if gptzero_api_key == SPECIAL_PASSWORD:
    gptzero_api_key = GPTZERO_API_KEY_DEFAULT

# Initialize session_state if not already initialized
if 'history' not in st.session_state:
    st.session_state.history = []
if 'position' not in st.session_state:
    st.session_state.position = -1  # Position of the current display in history

# Title
st.title('Totally Not ChatGPT')

# Model selection
model_selection = st.selectbox('Select the model:', ['gpt-3.5-turbo', 'gpt-3.5-turbo-16k', 'gpt-4'])

# User input
user_input = st.text_area('You: ', height=200)

# Load conversation and rephrase_list based on the current position
if st.session_state.position == -1:
    conversation = []
    rephrase_list = []
else:
    conversation, rephrase_list = st.session_state.history[st.session_state.position]

ai_detection_score = "N/A"

# Add user input to conversation and make API calls
if user_input:
    openai.api_key = openai_api_key
    response = openai.ChatCompletion.create(
        model=model_selection,
        messages=[{"role": "system", "content": "You are a helpful assistant."}, {"role": "user", "content": user_input}]
    )
    chatbot_response = response['choices'][0]['message']['content'].strip()
    conversation.insert(0, {"role": "assistant", "content": chatbot_response})
    conversation.insert(0, {"role": "user", "content": user_input})
    
    gptzero_response = requests.post(
        "https://api.gptzero.me/v2/predict/text",
        headers={"x-api-key": gptzero_api_key},
        json={"document": chatbot_response}
    ).json()
    if 'documents' in gptzero_response:
        ai_detection_score = f"{round(gptzero_response['documents'][0]['completely_generated_prob'] * 100, 2)}%"

    st.session_state.history.append((conversation[:], rephrase_list[:]))
    st.session_state.position += 1

st.write(f'<div style="text-align: right; color: blue;">AI Detection Score: {ai_detection_score}</div>', unsafe_allow_html=True)

# Rephrase button
if st.button('Rephrase Text'):
    headers = {'api-token': stealthgpt_api_key, 'Content-Type': 'application/json'}
    data = {'prompt': conversation[0]['content'], 'rephrase': True}
    response = requests.post('https://stealthgpt.ai/api/stealthify', headers=headers, json=data)
    if response.status_code == 200:
        rephrased_text = response.json().get('response', 'Could not rephrase')
        rephrase_list.insert(0, rephrased_text)
    st.session_state.history.append((conversation[:], rephrase_list[:]))
    st.session_state.position += 1

# Display conversation and rephrases
st.write("### Conversation:")
for turn in conversation:
    if turn['role'] == 'user':
        st.write(f'<div style="color: blue; background-color: #E6EFFF; padding: 10px; border-radius: 12px; margin: 5px;"><b>You:</b> {turn["content"]}</div>', unsafe_allow_html=True)
    elif turn['role'] == 'assistant':
        st.write(f'<div style="color: black; background-color: #F0F0F0; padding: 10px; border-radius: 12px; margin: 5px;"><b>ChatGPT:</b> {turn["content"]}</div>', unsafe_allow_html=True)

if rephrase_list:
    st.write("### Rephrases:")
    for rephrased_text in rephrase_list:
        st.write(f'<div style="color: black; background-color: #DFFFDF; padding: 10px; border-radius: 12px; margin: 5px;">{rephrased_text}</div>', unsafe_allow_html=True)

# Previous and Next Buttons
col1, col2, col3 = st.columns(3)
if col1.button('Previous'):
    if st.session_state.position > 0:
        st.session_state.position -= 1
if col3.button('Next'):
    if st.session_state.position < len(st.session_state.history) - 1:
        st.session_state.position += 1

# Clear conversation
if st.button('Clear Conversation'):
    st.session_state.position = -1
    st.session_state.history.clear()
