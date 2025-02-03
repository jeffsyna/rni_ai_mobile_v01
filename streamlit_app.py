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

def get_ai_response(user_input: str, api_key: str, query_type: str) -> str:
    """
    Get AI response from the endpoint
    """
    try:
        # Enable SSL bypass
        allowSelfSignedHttps(True)
        
        # Prepare the request
        url = 'https://APSWC-DEV-AI-OpenAI.openai.azure.com/openai/deployments/gpt-4o/chat/completions'
        api_version = '2024-08-01-preview'
        
        # Set system message based on query type
        if query_type == "general":
            system_message = "You are a helpful AI assistant for R&I department. Please provide clear and concise answers in Korean to general questions about research and innovation."
        else:  # product
            system_message = """You are a specialized AI assistant for cosmetic product planning and development in R&I department. Please provide detailed guidance and professional insights in Korean about product planning, market analysis, and innovation strategies.

For cosmetic product development, consider the following active ingredients and their contents:

Exfoliation:
- PURASAL SPF 60 (code: 6000285, content: 0.25%)
- PINK PLUM VINEGAR (code: 6026077, content: 0.1%)

Whitening:
- Niacinamide PC (code: 6000029, content: 2%)
- 트라넥사민산(TRANEXAMIC ACID) (code: 6006650, content: 0.5%)
[Additional whitening ingredients omitted for brevity]

Moisturizing:
- UREA(NEW) (code: 6006081, content: 1%)
- Ceramide PC-104 (code: 6010270, content: 0.0002%)
[Additional moisturizing ingredients omitted for brevity]

Pores/Sebum:
- Houttuynia Powder (code: 6023106, content: 0.1%)
- Jade Sphere (code: 6023814, content: 0.01%)
[Additional pore/sebum ingredients omitted for brevity]

Wrinkles/Elasticity:
- L-ARGININE (code: 6005767, content: 0.0012%)
- New EGCG-200(5%) (code: 6026318, content: 1%)
[Additional wrinkle/elasticity ingredients omitted for brevity]

Soothing:
- ORGANIC ALOE VERA EXTRACT D (code: 6019146, content: 1%)
- JEJU GREEN CALMING COMPLEX (code: 6020894, content: 0.1%)
[Additional soothing ingredients omitted for brevity]

When creating product plans, include:
1. Product Name
2. Product Concept
3. Target Consumer (age/gender/lifestyle)
4. Customer Pain Points
5. Competitive Situation
6. Key Ingredients and Features (with codes and contents)
7. Product Formulation (table with codes, names, contents, functions)
8. Design Concept
9. Future Growth Potential
10. Points to Improve
11. Differentiation Strategy

For formulations, follow these guidelines:
- Toner: Purified water, moisturizer, efficacy ingredient, viscosity modifier
- Lotion/Emulsion: Purified water, moisturizer, efficacy ingredient, emulsifier, viscosity modifier
- Essence: Purified water, moisturizer, efficacy ingredient, viscosity modifier
- Serum: Purified water, moisturizer, efficacy ingredient, emulsifier, viscosity modifier
- Cream: Purified water, moisturizer, efficacy ingredient, emulsifier, emulsifying stabilizer, viscosity modifier

Use at least two active ingredients from the provided list and adjust contents according to function."""
        
        # Prepare request data
        data = {
            "messages": [
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_input}
            ],
            "temperature": 0.7,
            "max_tokens": 2000  # Increased for longer responses
        }
        body = str.encode(json.dumps(data))
        
        # Prepare headers
        headers = {
            'Content-Type': 'application/json',
            'api-key': api_key
        }
        
        # Create and send request
        full_url = f"{url}?api-version={api_version}"
        req = urllib.request.Request(full_url, body, headers)
        
        # Get response
        with urllib.request.urlopen(req) as response:
            result = response.read()
            response_data = json.loads(result.decode('utf-8'))
            return response_data['choices'][0]['message']['content']
            
    except urllib.error.HTTPError as error:
        error_message = f"요청 실패 - 상태 코드: {error.code}\n"
        error_message += f"오류 정보: {error.info()}\n"
        error_message += error.read().decode("utf8", 'ignore')
        return error_message
    except Exception as e:
        return f"오류 발생: {str(e)}"

def main():
    # Page config
    st.set_page_config(page_title="R&I AI assistance", page_icon="🤖", layout="wide")
    
    # Title with custom styling
    st.markdown("""
        <h1 style='text-align: center; color: #2e4053;'>R&I AI assistance</h1>
        <p style='text-align: center; color: #566573;'>제품 기획 도우미 by NSY</p>
        """, unsafe_allow_html=True)
    
    # Notice section
    st.markdown("""
        <div style='background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin-bottom: 20px;'>
        <h3 style='color: #c0392b;'>⚠️ Notice</h3>
        <p>등록된 DB 기반으로 최대한 충실하게 답변드리지만 반드시 정확하지는 않습니다.</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Tip section
    st.markdown("""
        <div style='background-color: #ebf5fb; padding: 15px; border-radius: 5px; margin-bottom: 20px;'>
        <h3 style='color: #2874a6;'>💡 TIP</h3>
        <p>질의 전 반드시 아래 탭에서 일반 질문인지 제품기획인지 선택해주세요. 제품기획은 제품 기획안 작성만 대답 가능합니다.</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Query type selection
    col1, col2 = st.columns(2)
    with col1:
        general_selected = st.button("일반 질문", use_container_width=True, 
            help="일반적인 문의사항에 대해 질문하실 수 있습니다.")
    with col2:
        product_selected = st.button("제품 기획", use_container_width=True,
            help="제품 기획과 관련된 문의사항에 대해 질문하실 수 있습니다.")
    
    # Store selected type in session state
    if general_selected:
        st.session_state.query_type = "general"
    elif product_selected:
        st.session_state.query_type = "product"
    
    # Sidebar for API key
    with st.sidebar:
        st.title("설정")
        if 'api_key' not in st.session_state:
            api_key = st.text_input("API Key", type="password")
            if st.button("설정 저장"):
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
    if 'query_type' in st.session_state:
        with st.form(key="chat_form", clear_on_submit=True):
            user_input = st.text_input(
                "메시지를 입력하세요:",
                key="input_field",
                placeholder=f"{'일반 질문' if st.session_state.query_type == 'general' else '제품 기획'} 모드에서 질문하실 수 있습니다."
            )
            submit_button = st.form_submit_button("전송")
            
            if submit_button and user_input and 'api_key' in st.session_state:
                try:
                    # Display user message
                    with st.chat_message("user"):
                        st.write(user_input)
                    st.session_state.chat_history.append({"role": "user", "content": user_input})
                    
                    # Get and display AI response
                    response = get_ai_response(user_input, st.session_state.api_key, st.session_state.query_type)
                    
                    with st.chat_message("assistant"):
                        st.write(response)
                    st.session_state.chat_history.append({"role": "assistant", "content": response})
                    
                    st.rerun()
                except Exception as e:
                    st.error(f"오류 발생: {str(e)}")
            elif submit_button and not 'api_key' in st.session_state:
                st.warning("API 키를 먼저 설정해주세요.")
    else:
        st.info("위의 '일반 질문' 또는 '제품 기획' 버튼을 클릭하여 질문 유형을 선택해주세요.")

if __name__ == "__main__":
    main()
