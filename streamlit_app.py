import urllib.request
import json
import os
import ssl
import streamlit as st
import time
from urllib.error import HTTPError

def allowSelfSignedHttps(allowed):
    """
    Bypass server certificate verification on client side
    """
    if allowed and not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None):
        ssl._create_default_https_context = ssl._create_unverified_context

def get_ai_response(user_input: str, api_key: str) -> str:
    """
    Get AI response from the endpoint with retry logic
    """
    max_retries = 5
    retry_delay = 2  # seconds
    
    try:
        for attempt in range(max_retries):
            try:
                # Enable SSL bypass
                allowSelfSignedHttps(True)
                
                # Prepare the request
                url = 'https://DeepSeek-R1-sqlbu.eastus2.models.ai.azure.com/chat/completions'
                api_version = '2024-02-15-preview'
                
                # Set system message
                system_message = """You are a professional VC investment analyst. Your task is to evaluate the investment potential of a startup.

Based on the company name provided, analyze and answer the following questions:

1. **Business Model & Profitability Analysis**: What is the company's business model, and is it sustainable?
2. **Competitive Advantage**: What differentiates this company from its competitors?
3. **Market Opportunity**: Considering current market trends and growth potential, can this company scale successfully?
4. **Risk Factors**: What are the key risks associated with this company?
5. **Investment Suitability**: Is this company attractive for investment at its current stage? Why or why not?

*note : always response in Korean"""
                
                data = {
                    "messages": [
                        {"role": "system", "content": system_message},
                        {"role": "user", "content": user_input}
                    ],
                    "temperature": 0.7,
                    "max_tokens": 2000,
                    "model": "DeepSeek-R1-sqlbu"
                }
                body = str.encode(json.dumps(data))
                
                # Prepare headers
                headers = {
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {api_key}'
                }
                
                # Create and send request
                full_url = f"{url}?api-version={api_version}"
                req = urllib.request.Request(full_url, body, headers)
                
                try:
                    # Get response
                    with urllib.request.urlopen(req) as response:
                        result = response.read()
                        try:
                            response_data = json.loads(result.decode('utf-8'))
                            if 'choices' in response_data and len(response_data['choices']) > 0:
                                return response_data['choices'][0]['message']['content']
                            else:
                                return "API 응답에서 유효한 응답을 찾을 수 없습니다."
                        except json.JSONDecodeError as je:
                            st.error(f"JSON 파싱 오류: {str(je)}")
                            return "응답 데이터 처리 중 오류가 발생했습니다."
                except urllib.error.HTTPError as error:
                    error_info = error.read().decode("utf8", 'ignore')
                    try:
                        error_data = json.loads(error_info) if error_info else {}
                    except json.JSONDecodeError:
                        error_data = {}
                    
                    if error.code == 429:  # Rate limit exceeded
                        retry_after = float(error.headers.get('retry-after', retry_delay))
                        error_message = f"요청 한도 초과 - {retry_after}초 후 재시도합니다... (시도 {attempt + 1}/{max_retries})"
                        st.warning(error_message)
                        time.sleep(retry_after)
                        continue
                    elif error.code == 500 and attempt < max_retries - 1:
                        error_message = f"서버 오류 발생 - {attempt + 1}번째 시도 실패. {retry_delay}초 후 재시도합니다..."
                        st.warning(error_message)
                        time.sleep(retry_delay)
                        retry_delay *= 2  # 지수 백오프
                        continue
                    else:
                        error_message = f"요청 실패 - 상태 코드: {error.code}\n"
                        if error_data.get('error', {}).get('message'):
                            error_message += f"오류 메시지: {error_data['error']['message']}\n"
                        return error_message
                        
            except Exception as e:
                if attempt < max_retries - 1:
                    error_message = f"오류 발생 - {attempt + 1}번째 시도 실패. {retry_delay}초 후 재시도합니다..."
                    st.warning(error_message)
                    time.sleep(retry_delay)
                    retry_delay *= 2  # 지수 백오프
                    continue
                return f"오류 발생: {str(e)}"
        
        return "최대 재시도 횟수를 초과했습니다. 잠시 후 다시 시도해주세요."
        
    except Exception as e:
        return f"처리 중 오류가 발생했습니다: {str(e)}"

def main():
    # Page config
    st.set_page_config(page_title="Startup Investment Analyzer", page_icon="🔍", layout="wide")
    
    # Custom CSS for layout
    st.markdown("""
        <style>
        /* Global background fix */
        .st-emotion-cache-1y4p8pa {
            background-color: transparent !important;
        }
        
        .st-emotion-cache-1v0mbdj > div {
            background-color: transparent !important;
        }
        
        /* Main container styling */
        .main-container {
            position: fixed;
            top: 0;
            left: 15rem;
            right: 0;
            bottom: 0;
            padding: 20px;
            display: flex;
            flex-direction: column;
            background-color: transparent !important;
        }
        
        /* Notice and Tip styling */
        .notice-box {
            background-color: #f5f5f5;
            padding: 10px;
            border-radius: 8px;
            margin: 10px auto;
            border: 1px solid #e0e0e0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            width: 600px;
        }
        
        /* Success message styling */
        .st-success {
            background-color: #f5f5f5 !important;
            color: #333333 !important;
            border: 1px solid #e0e0e0 !important;
        }
        
        /* Warning message styling */
        .st-warning {
            background-color: #f8f8f8 !important;
            color: #666666 !important;
            border: 1px solid #e0e0e0 !important;
        }
        
        /* Error message styling */
        .st-error {
            background-color: #f0f0f0 !important;
            color: #333333 !important;
            border: 1px solid #d0d0d0 !important;
        }
        
        /* Chat message styling */
        .st-chat-message {
            background-color: #ffffff !important;
            border: 1px solid #e0e0e0 !important;
            box-shadow: 0 1px 2px rgba(0,0,0,0.05) !important;
        }
        
        /* User message styling */
        [data-testid="user-message"] {
            background-color: #f8f8f8 !important;
            border: 1px solid #e0e0e0 !important;
        }
        
        /* Assistant message styling */
        [data-testid="assistant-message"] {
            background-color: #ffffff !important;
            border: 1px solid #e0e0e0 !important;
        }
        
        /* Input field styling */
        .stTextInput > div > div > input {
            border: 1px solid #e0e0e0 !important;
            color: #333333 !important;
        }
        
        /* Button styling */
        .stButton > button {
            background-color: #333333 !important;
            color: #ffffff !important;
            border: none !important;
        }
        
        .stButton > button:hover {
            background-color: #666666 !important;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Initialize session state
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    if 'current_tab' not in st.session_state:
        st.session_state.current_tab = "general"
    
    # Sidebar for API key
    with st.sidebar:
        st.title("API 설정")
        
        # Azure API Key input
        if 'api_key' not in st.session_state:
            api_key = st.text_input("Azure API Key", type="password")
            if st.button("API 키 저장"):
                st.session_state.api_key = api_key
                st.rerun()
        
        if 'api_key' in st.session_state:
            st.success("API 키가 설정되었습니다.")
            if st.button("API 키 재설정"):
                del st.session_state.api_key
                st.rerun()
    
    # Main container
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    
    # Notice section
    st.markdown("""
        <div class='notice-box'>
        <h3 style='color: #333333; margin-top: 0;'>⚠️ VC with AI Notice</h3>
        <p style='color: #666666; margin-bottom: 0;'>AI 모델을 활용한 추론 기반으로 답변드리기 때문에 생성에 시간이 걸릴 수 있습니다.</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Chat history container
    st.markdown('<div class="chat-history-container">', unsafe_allow_html=True)
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Chat input container
    st.markdown('<div class="chat-input-container">', unsafe_allow_html=True)
    user_input = st.chat_input("분석하고 싶은 스타트업 이름을 입력하세요:")
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

    # Handle chat input
    if user_input and 'api_key' in st.session_state:
        try:
            with st.chat_message("user"):
                st.write(user_input)
            st.session_state.chat_history.append({"role": "user", "content": user_input})
            
            response = get_ai_response(user_input, st.session_state.api_key)
            
            with st.chat_message("assistant"):
                st.write(response)
            st.session_state.chat_history.append({"role": "assistant", "content": response})
            
        except Exception as e:
            st.error(f"오류 발생: {str(e)}")
    elif user_input and 'api_key' not in st.session_state:
        st.warning("Azure API 키를 설정해주세요.")

if __name__ == "__main__":
    main()
