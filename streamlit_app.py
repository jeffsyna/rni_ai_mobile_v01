import os
import json
import ssl
import urllib.request
import streamlit as st
from dotenv import load_dotenv

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
        load_dotenv()
        
        # Configuration
        self.url = os.getenv('AZURE_ML_INFERENCE_URL', 'https://rni-ai-assistance-lhlbq.eastus2.inference.ml.azure.com/score')
        self.api_key = os.getenv('AZURE_ML_API_KEY', 'CsSaJ6GYCy9H2XKb3hK43IYrddBl8WHS')
        
        # Enable self-signed HTTPS if needed
        allowSelfSignedHttps(True)
        
        if not self.api_key:
            raise ValueError("Azure ML API key is required")

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
                "input_text": user_input
            }
            body = str.encode(json.dumps(data))

            # Prepare headers
            headers = {
                'Content-Type': 'application/json', 
                'Authorization': f'Bearer {self.api_key}'
            }

            # Create request
            req = urllib.request.Request(self.url, body, headers)

            # Send request
            with urllib.request.urlopen(req) as response:
                result = response.read().decode('utf-8')
                return json.loads(result).get('output_text', 'No response received')

        except urllib.error.HTTPError as error:
            error_message = f"Request failed with status code: {error.code}\n"
            error_message += f"Error details: {error.read().decode('utf-8')}"
            return error_message
        except Exception as e:
            return f"An error occurred: {str(e)}"

def main():
    """
    Streamlit application for interactive Azure ML chatbot
    """
    st.set_page_config(page_title="RNI AI Assistant", page_icon="🤖")
    st.title("R&I AI Assistant with Azure ML")
    st.write("AI 어시스턴트와 대화를 시작해보세요!")

    # Initialize chatbot and session state
    chatbot = AzureMLChatbot()
    
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

if __name__ == "__main__":
    main()
