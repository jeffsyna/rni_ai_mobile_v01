import os
import json
import ssl
import urllib.request
import streamlit as st
import traceback

def allowSelfSignedHttps(allowed):
    """
    Bypass server certificate verification on client side
    """
    if allowed and not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None):
        ssl._create_default_https_context = ssl._create_unverified_context

class AzureMLChatbot:
    def __init__(self):
        """
        Initialize Azure ML inference endpoint chatbot
        """
        # Configuration
        self.url = 'https://ai-sol-prompthon-vwdxk.eastus2.inference.ml.azure.com/score'
        self.api_key = 'tBGuiknYLuYK503TTnFO0uaPRt9mm1yc'
        self.deployment_name = 'ai-sol-prompthon-vwdxk-1'
        
        # Enable self-signed HTTPS if needed
        allowSelfSignedHttps(True)
        
        if not self.api_key:
            raise ValueError("API key is required")

    def get_ai_response(self, user_input: str) -> str:
        """
        Generate AI response using Azure ML inference endpoint

        Args:
            user_input (str): User's message

        Returns:
            str: AI-generated response
        """
        try:
            # Prepare request data
            data = {
                "messages": [
                    {"role": "user", "content": user_input}
                ]
            }
            
            print(f"Request data: {json.dumps(data, ensure_ascii=False)}")  # 요청 데이터 로깅
            body = str.encode(json.dumps(data))

            # Prepare headers
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.api_key}',
                'azureml-model-deployment': self.deployment_name
            }

            # Create request
            req = urllib.request.Request(self.url, body, headers)

            # Send request
            with urllib.request.urlopen(req) as response:
                result = response.read().decode('utf-8')
                print(f"Raw response: {result}")  # 응답 로깅
                
                # JSON 파싱 및 응답 추출
                try:
                    parsed_result = json.loads(result)
                    return str(parsed_result)
                except json.JSONDecodeError:
                    return f"JSON 디코딩 오류: {result}"

        except urllib.error.HTTPError as error:
            error_message = f"요청 실패 - 상태 코드: {error.code}\n"
            error_message += f"오류 세부 정보: {error.read().decode('utf-8')}"
            print(error_message)
            return error_message
        except Exception as e:
            error_trace = traceback.format_exc()
            print(f"예외 발생: {str(e)}")
            print(f"트레이스백: {error_trace}")
            return f"오류 발생: {str(e)}"

def main():
    """
    Streamlit application for interactive Azure ML chatbot
    """
    st.set_page_config(page_title="AI Solution Prompthon", page_icon="🤖")
    st.title("AI Solution Prompthon Assistant")
    st.write("AI 어시스턴트와 대화를 시작해보세요!")

    # 디버깅 정보 표시
    st.sidebar.title("디버깅 정보")
    st.sidebar.write("Inference URL: https://ai-sol-prompthon-vwdxk.eastus2.inference.ml.azure.com/score")
    st.sidebar.write("Deployment: ai-sol-prompthon-vwdxk-1")

    # API 키 입력
    if 'api_key' not in st.session_state:
        st.sidebar.title("API 키 설정")
        api_key = st.sidebar.text_input("API Key", type="password")
        if st.sidebar.button("설정 저장"):
            st.session_state.api_key = api_key
            st.rerun()

    # Initialize chatbot and session state
    try:
        chatbot = AzureMLChatbot()
        if 'api_key' in st.session_state:
            chatbot.api_key = st.session_state.api_key
    except Exception as init_error:
        st.error(f"챗봇 초기화 오류: {str(init_error)}")
        return
    
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []

    # Display chat history
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # User input form
    with st.form(key="chat_form", clear_on_submit=True):
        user_input = st.text_input("메시지를 입력하세요:", key="input_field")
        submit_button = st.form_submit_button("전송")
        
        if submit_button and user_input:
            try:
                # User message
                with st.chat_message("user"):
                    st.write(user_input)
                st.session_state.chat_history.append({"role": "user", "content": user_input})
                
                # AI response
                response = chatbot.get_ai_response(user_input)
                
                # Assistant message
                with st.chat_message("assistant"):
                    st.write(response)
                st.session_state.chat_history.append({"role": "assistant", "content": response})
                
                st.rerun()
            except Exception as chat_error:
                st.error(f"대화 처리 중 오류 발생: {str(chat_error)}")

if __name__ == "__main__":
    main()
