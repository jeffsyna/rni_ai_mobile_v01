import urllib.request
import json
import os
import ssl
import streamlit as st

def allowSelfSignedHttps(allowed):
    """
    Bypass server certificate verification on client side
    """
    if allowed and not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None):
        ssl._create_default_https_context = ssl._create_unverified_context

def get_ai_response(user_input: str, api_key: str) -> str:
    """
    Get AI response from the endpoint
    """
    try:
        # Enable SSL bypass
        allowSelfSignedHttps(True)
        
        # Prepare the request
        url = 'https://ai-sol-prompthon-vwdxk.eastus2.inference.ml.azure.com/score'
        
        # Prepare request data
        data = {
            "input": user_input
        }
        body = str.encode(json.dumps(data))
        
        # Prepare headers
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_key}'
        }
        
        # Create and send request
        req = urllib.request.Request(url, body, headers)
        
        # Get response
        with urllib.request.urlopen(req) as response:
            result = response.read()
            return result.decode('utf-8')
            
    except urllib.error.HTTPError as error:
        error_message = f"요청 실패 - 상태 코드: {error.code}\n"
        error_message += f"오류 정보: {error.info()}\n"
        error_message += error.read().decode("utf8", 'ignore')
        return error_message
    except Exception as e:
        return f"오류 발생: {str(e)}"

def main():
    # Page config
    st.set_page_config(page_title="AI Solution Prompthon", page_icon="🤖")
    st.title("AI Solution Prompthon Assistant")
    st.write("AI 어시스턴트와 대화를 시작해보세요!")
    
    # Sidebar for API key
    st.sidebar.title("설정")
    if 'api_key' not in st.session_state:
        api_key = st.sidebar.text_input("API Key", type="password")
        if st.sidebar.button("설정 저장"):
            st.session_state.api_key = api_key
            st.rerun()
    
    # Initialize chat history
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    # Display chat history
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    
    # Chat input
    with st.form(key="chat_form", clear_on_submit=True):
        user_input = st.text_input("메시지를 입력하세요:", key="input_field")
        submit_button = st.form_submit_button("전송")
        
        if submit_button and user_input and 'api_key' in st.session_state:
            try:
                # Display user message
                with st.chat_message("user"):
                    st.write(user_input)
                st.session_state.chat_history.append({"role": "user", "content": user_input})
                
                # Get and display AI response
                response = get_ai_response(user_input, st.session_state.api_key)
                
                with st.chat_message("assistant"):
                    st.write(response)
                st.session_state.chat_history.append({"role": "assistant", "content": response})
                
                st.rerun()
            except Exception as e:
                st.error(f"오류 발생: {str(e)}")
        elif submit_button and not 'api_key' in st.session_state:
            st.warning("API 키를 먼저 설정해주세요.")

if __name__ == "__main__":
    main()
