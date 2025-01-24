import requests
import json
import streamlit as st
from datetime import datetime

# Azure OpenAI Service 설정
AZURE_OPENAI_ENDPOINT = "https://rniaiproject4657409409.openai.azure.com/openai/deployments/gpt-4/chat/completions?api-version=2024-08-01-preview"
AZURE_OPENAI_KEY = "EjEL2MlZ70BhFT2tyVloS624wLLXT8krtmv9EJu08hIdrR2AHZw5JQQJ99BAACHYHv6XJ3w3AAAAACOGWY3C"
DEPLOYMENT_NAME = "gpt-4"
API_VERSION = "2024-08-01-preview"

def get_ai_response(user_input):
    try:
        # Azure OpenAI Service 호출
        headers = {
            'Content-Type': 'application/json',
            'api-key': AZURE_OPENAI_KEY
        }
        
        data = {
            "messages": [
                {"role": "system", "content": "You are a helpful AI assistant."},
                {"role": "user", "content": user_input}
            ],
            "temperature": 0.7,
            "max_tokens": 800
        }
        
        # URL 구조 수정
        api_url = f"{AZURE_OPENAI_ENDPOINT}/openai/deployments/{DEPLOYMENT_NAME}/chat/completions?api-version={API_VERSION}"
        print(f"Calling API URL: {api_url}")
        print(f"Request Headers: {headers}")
        print(f"Request Data: {json.dumps(data, ensure_ascii=False)}")
        
        response = requests.post(
            api_url,
            headers=headers,
            json=data,
            verify=True
        )
        
        print(f"Response Status: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        else:
            error_message = f"Error: {response.status_code}"
            try:
                error_detail = response.json()
                error_message += f" - {json.dumps(error_detail, ensure_ascii=False)}"
            except:
                error_message += f" - {response.text}"
            return error_message
            
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

# 채팅 입력 폼 생성
with st.form(key="chat_form", clear_on_submit=True):
    user_input = st.text_input("메시지를 입력하세요:", key="input_field")
    submit_button = st.form_submit_button("전송")

    if submit_button and user_input:
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
        
        # 페이지 새로고침
        st.rerun()
