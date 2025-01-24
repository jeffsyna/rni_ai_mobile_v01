import requests
import json
import streamlit as st
from datetime import datetime

# Azure OpenAI Service 설정
AZURE_OPENAI_ENDPOINT = "https://APSWC-DEV-AI-OpenAI.openai.azure.com/openai/deployments/gpt-4-1106/chat/completions?api-version=2024-08-01-preview"
AZURE_OPENAI_KEY = "19ec7b7f1bec46dd91be16c92941a733"
DEPLOYMENT_NAME = "gpt-4-1106"
API_VERSION = "2024-08-01-preview"

# Azure AI Foundry 프롬프트 흐름 설정
PROMPT_FLOW_ENDPOINT = "https://rni-ai-assistance-lhlbq.eastus2.inference.ml.azure.com/score"
PROMPT_FLOW_KEY = "CsSaJ6GYCy9H2XKb3hK43IYrddBl8WHS"

def get_ai_response(user_input):
    try:
        # 1. Azure OpenAI Service 호출
        openai_headers = {
            'Content-Type': 'application/json',
            'api-key': AZURE_OPENAI_KEY
        }
        
        openai_data = {
            "messages": [
                {"role": "system", "content": "You are a helpful AI assistant."},
                {"role": "user", "content": user_input}
            ],
            "temperature": 0.7,
            "max_tokens": 800,
            "model": "gpt-4"
        }
        
        api_url = f"{AZURE_OPENAI_ENDPOINT}/openai/deployments/{DEPLOYMENT_NAME}/chat/completions?api-version={API_VERSION}"
        print(f"Calling API URL: {api_url}")
        
        openai_response = requests.post(
            api_url,
            headers=openai_headers,
            json=openai_data,
            verify=True
        )
        
        print(f"OpenAI Response Status: {openai_response.status_code}")
        print(f"OpenAI Response: {openai_response.text}")
        
        if openai_response.status_code != 200:
            return f"OpenAI Error: {openai_response.status_code} - {openai_response.text}"
        
        ai_response = openai_response.json()['choices'][0]['message']['content']
        
        # 2. 프롬프트 흐름 호출
        flow_headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {PROMPT_FLOW_KEY}'
        }
        
        flow_data = {
            "data": {
                "message": user_input,
                "ai_response": ai_response,
                "deployment": DEPLOYMENT_NAME,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        }
        
        flow_response = requests.post(
            PROMPT_FLOW_ENDPOINT,
            headers=flow_headers,
            json=flow_data,
            verify=True
        )
        
        if flow_response.status_code == 200:
            try:
                return flow_response.json().get('output', ai_response)
            except:
                return ai_response
        else:
            print(f"Prompt Flow Error: {flow_response.status_code} - {flow_response.text}")
            return ai_response
            
    except requests.exceptions.RequestException as e:
        return f"Error: {str(e)}"

# Streamlit UI 구성
st.title("RNI AI Assistant")
st.write("AI 어시스턴트와 대화를 시작해보세요!")

# 채팅 히스토리 초기화
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# 이전 메시지 표시
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# 사용자 입력 처리
if 'user_input' not in st.session_state:
    st.session_state.user_input = ""

user_input = st.text_input("메시지를 입력하세요:", key="input_field")

if st.button("전송") and user_input:
    # 사용자 메시지 표시
    with st.chat_message("user"):
        st.write(user_input)
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    
    # AI 응답 받기
    response = get_ai_response(user_input)
    
    # AI 응답 표시
    with st.chat_message("assistant"):
        st.write(response)
    st.session_state.chat_history.append({"role": "assistant", "content": response})
    
    # 입력창 초기화를 위한 페이지 새로고침
    st.rerun()
