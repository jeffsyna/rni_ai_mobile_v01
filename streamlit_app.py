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
- 트라넥사민산 (code: 6006650, content: 0.5%)
- Whitegen EX (code: 6008784, content: 0.01%)
- 삼백초추출물 (code: 6016434, content: 0.0001%)
- Ascorbic Acid Fine powder (code: 6018508, content: 0.7812%)
- New 닥나무뿌리추출물 (code: 6018603, content: 0.1%)
- COS-VCE-K (code: 6020206, content: 0.01%)
- AgelyticS (code: 6026723, content: 0.005%)
[Additional whitening ingredients omitted for brevity]

Moisturizing:
- UREA(NEW) (code: 6006081, content: 1%)
- Ceramide PC-104 (code: 6010270, content: 0.0002%)
- Ceramide PC-102 (code: 6010271, content: 0.0002%)
- Glyacid 70 HP (code: 6010544, content: 0.0001%)
- Red Pine Needle (code: 6025370, content: 0.3%)
- VERI-ENT MOISTURIZING WATER_10 (code: 6026185, content: 0.01%)
- FERULIC ACID (code: 6026240, content: 0.01%)]
[Additional moisturizing ingredients omitted for brevity]

Pores/Sebum:
- Houttuynia Powder (code: 6023106, content: 0.1%)
- Jade Sphere (code: 6023814, content: 0.01%)
- JM-MUD (code: 6023897, content: 0.1%)
- Volcanic Sphere (code: 6025074, content: 0.01%)
- JEJU VOLCANIC ASH 2 (code: 6025600, content: 0.01%)
- SALICYLIC ACID (code: 6000362, content: 0.4%)
[Additional pore/sebum ingredients omitted for brevity]

Wrinkles/Elasticity:
- L-ARGININE (code: 6005767, content: 0.0012%)
- New EGCG-200 (code: 6026318, content: 1%)
- HumaColl21® 2% Solution (code: 6026333, content: 0.02%)
- Adenosine (code: 6026519, content: 0.02%)
- CAMELLIA F (code: 6026553, content: 0.0001%)
- LactoPDRN (code: 6026575, content: 0.6%)
- SUPER COLLAGEN (code: 6026648, content: 0.0025%)
- AgeRefect (code: 6026649, content: 0.0003%)
- CYLASPHERE RETINOL 10S (code: 6026656, content: 0.0005%)
- CO2LLAGENEER (code: 6026684, content: 0.1%)
- Hi-Aqua™ FL (code: 6026745, content: 0.005%)
- Green Tea Infusion (code: 6026750, content: 0.1%)
- DOUBLE SQUEEZE GREEN TEA WATER (code: 6026848, content: 0.01%)]
[Additional wrinkle/elasticity ingredients omitted for brevity]

Soothing:
- ORGANIC ALOE VERA EXTRACT D (code: 6019146, content: 1%)
- JEJU GREEN CALMING COMPLEX (code: 6020894, content: 0.1%)
- New AP sprout complex (code: 6024707, content: 0.1%)
- Anasensyl-LS 9322 (code: 6024795, content: 0.01%)
- MATRICARIA LIQUID EXTRACT (code: 6026065, content: 0.02%)]
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
            background-color: #fff2f0;
            padding: 10px;
            border-radius: 8px;
            margin: 10px auto;
            border: 1px solid #ffccc7;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            width: 600px;
        }
        
        .tip-box {
            background-color: #f0f5ff;
            padding: 10px;
            border-radius: 8px;
            margin: 10px auto;
            border: 1px solid #d6e4ff;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            width: 600px;
        }
        
        /* Chat history container */
        .chat-history-container {
            flex-grow: 1;
            overflow-y: auto;
            margin-bottom: 80px;
            padding: 20px;
            background-color: transparent !important;
        }
        
        /* Chat input container */
        .chat-input-container {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            height: 70px;
            padding: 10px;
            background: transparent;
            z-index: 1000;
            width: 600px;
            margin: 0 auto;
        }
        
        /* Chat input styling */
        .stChatInput {
            width: 600px !important;
            margin: 0 auto;
        }
        
        /* Remove default streamlit styles */
        .stChatInput > div {
            background: transparent !important;
            border: none !important;
            width: 600px !important;
        }
        
        /* Style the actual input element */
        .stChatInput input {
            border: 1px solid #e0e0e0 !important;
            border-radius: 8px !important;
            background: white !important;
            padding: 8px 12px !important;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05) !important;
            width: 600px !important;
        }
        
        /* Remove any additional backgrounds */
        div[data-testid="stChatInput"] {
            background: transparent !important;
            width: 600px !important;
        }
        
        /* Message styling */
        .stChatMessage {
            background-color: white;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            margin-bottom: 15px;
            padding: 15px;
            max-width: 800px;
            margin-left: auto;
            margin-right: auto;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }
        
        [data-testid="user-message"] {
            background-color: #e3f2fd !important;
            border-color: #90caf9;
        }
        
        [data-testid="assistant-message"] {
            background-color: #f5f5f5 !important;
            border-color: #e0e0e0;
        }
        
        /* Sidebar styling */
        .css-1d391kg {
            width: 15rem;
            padding: 2rem 1rem;
        }
        
        /* Hide unnecessary elements */
        .stDeployButton, footer {
            display: none;
        }
        
        /* Force transparent background on all containers */
        .element-container, .stMarkdown, .stChatMessageContent {
            background-color: transparent !important;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Initialize session state
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    if 'current_tab' not in st.session_state:
        st.session_state.current_tab = "general"
    
    # Sidebar for API key and query type selection
    with st.sidebar:
        st.title("설정")
        
        # API Key input
        if 'api_key' not in st.session_state:
            api_key = st.text_input("API Key", type="password")
            if st.button("설정 저장"):
                st.session_state.api_key = api_key
                st.rerun()
        else:
            st.success("API 키가 설정되었습니다.")
            if st.button("API 키 재설정"):
                del st.session_state.api_key
                st.rerun()
        
        st.markdown("---")  # Divider
        
        # Query type selection
        st.subheader("문의 유형 선택")
        selected_tab = st.radio("", ["일반 문의", "제품 기획"], key="query_type", 
                              help="문의 유형을 선택해주세요")
        
        if selected_tab == "일반 문의":
            st.session_state.current_tab = "general"
        else:
            st.session_state.current_tab = "product"
            st.markdown("""
                <div style='background-color: #fff3e0; padding: 10px; border-radius: 5px; border: 1px solid #ffe0b2;'>
                ⚠️ 제품기획안 생성만 가능합니다.
                </div>
                """, unsafe_allow_html=True)
    
    # Main container
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    
    # Notice section
    st.markdown("""
        <div class='notice-box'>
        <h3 style='color: #cf1322; margin-top: 0;'>⚠️ Notice</h3>
        <p style='color: #cf1322; margin-bottom: 0;'>등록된 DB 기반으로 최대한 충실하게 답변드리지만 반드시 정확하지는 않습니다.</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Tip section
    st.markdown("""
        <div class='tip-box'>
        <h3 style='color: #1890ff; margin-top: 0;'>💡 TIP</h3>
        <p style='color: #1890ff; margin-bottom: 0;'>질의 전 반드시 왼쪽 설정에서 일반 질문인지 제품기획인지 선택해주세요.</p>
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
    if st.session_state.current_tab == "general":
        placeholder = "일반적인 문의사항에 대해 질문해주세요:"
    else:
        placeholder = "제품 기획과 관련된 문의사항에 대해 질문해주세요:"
    user_input = st.chat_input(placeholder)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

    # Handle chat input
    if user_input and 'api_key' in st.session_state:
        try:
            with st.chat_message("user"):
                st.write(user_input)
            st.session_state.chat_history.append({"role": "user", "content": user_input})
            
            response = get_ai_response(user_input, st.session_state.api_key, st.session_state.current_tab)
            
            with st.chat_message("assistant"):
                st.write(response)
            st.session_state.chat_history.append({"role": "assistant", "content": response})
            
        except Exception as e:
            st.error(f"오류 발생: {str(e)}")
    elif user_input and 'api_key' not in st.session_state:
        st.warning("API 키를 먼저 설정해주세요.")

if __name__ == "__main__":
    main()
