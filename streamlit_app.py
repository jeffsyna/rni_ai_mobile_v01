import urllib.request
import json
import os
import ssl
import streamlit as st
import time
from urllib.error import HTTPError
import requests
from typing import Dict, Optional

def allowSelfSignedHttps(allowed):
    """
    Bypass server certificate verification on client side
    """
    if allowed and not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None):
        ssl._create_default_https_context = ssl._create_unverified_context

def get_crunchbase_data(company_name: str, crunchbase_api_key: str) -> Optional[Dict]:
    """
    Crunchbase API를 통해 회사 정보를 가져오는 함수
    """
    base_url = "https://api.crunchbase.com/api/v4"
    headers = {
        "accept": "application/json",
        "x-cb-user-key": crunchbase_api_key
    }
    
    try:
        # 회사 검색
        search_url = f"{base_url}/autocompletes"
        params = {
            "query": company_name,
            "collection_types": "organizations",
            "limit": 1
        }
        
        response = requests.get(search_url, headers=headers, params=params)
        response.raise_for_status()
        search_data = response.json()
        
        if not search_data.get("entities"):
            return None
            
        # 회사 UUID 가져오기
        org_uuid = search_data["entities"][0].get("identifier", {}).get("uuid")
        if not org_uuid:
            return None
            
        # 상세 정보 조회 (모든 필요한 정보를 한 번에 요청)
        detail_url = f"{base_url}/entities/organizations/{org_uuid}"
        params = {
            "field_ids": [
                "name", "short_description", "founded_on", "location_identifiers",
                "funding_total", "operating_status", "categories", "company_type",
                "revenue_range", "last_funding_type", "num_employees_enum",
                "website", "linkedin", "twitter", "facebook",
                "funding_rounds", "funding_rounds.announced_on",
                "funding_rounds.money_raised", "funding_rounds.investment_type",
                "funding_rounds.investors", "funding_rounds.investor_identifiers"
            ]
        }
        
        detail_response = requests.get(detail_url, headers=headers, params=params)
        detail_response.raise_for_status()
        company_data = detail_response.json()
        
        if not company_data:
            return None
            
        return company_data
        
    except requests.exceptions.RequestException as e:
        st.error(f"Crunchbase API 호출 중 오류 발생: {str(e)}")
        return None

def format_crunchbase_data(data: Dict) -> str:
    """
    Crunchbase API 데이터를 챗봇 시스템 메시지 형식으로 변환
    """
    if not data:
        return "회사 정보를 찾을 수 없습니다."
    
    properties = data.get("properties", {})
    
    # 펀딩 라운드 정보 처리
    funding_rounds = properties.get("funding_rounds", [])
    latest_round = funding_rounds[0] if funding_rounds else {}
    
    # 투자자 정보 처리
    investors = []
    if latest_round:
        investors = latest_round.get("investors", [])
    
    formatted_data = {
        "Company Overview": {
            "Company Name": properties.get("name", "N/A"),
            "Year Founded": properties.get("founded_on", "N/A"),
            "Location": properties.get("location_identifiers", [{}])[0].get("value", "N/A") if properties.get("location_identifiers") else "N/A",
            "Industry": ", ".join([cat.get("value", "") for cat in properties.get("categories", [])]),
            "Website": properties.get("website", {}).get("value", "N/A"),
            "Description": properties.get("short_description", "N/A")
        },
        "Funding Details": {
            "Stage": properties.get("last_funding_type", "N/A"),
            "Total Amount": properties.get("funding_total", {}).get("value_usd", "N/A"),
            "Latest Round": {
                "Date": latest_round.get("announced_on", "N/A"),
                "Type": latest_round.get("investment_type", "N/A"),
                "Amount": latest_round.get("money_raised", {}).get("value_usd", "N/A")
            },
            "Key Investors": [inv.get("name", "") for inv in investors[:5]]
        },
        "Financial Data": {
            "Revenue Range": properties.get("revenue_range", "N/A"),
            "Employee Count": properties.get("num_employees_enum", "N/A"),
            "Operating Status": properties.get("operating_status", "N/A")
        },
        "Social Media": {
            "LinkedIn": properties.get("linkedin", {}).get("value", "N/A"),
            "Twitter": properties.get("twitter", {}).get("value", "N/A"),
            "Facebook": properties.get("facebook", {}).get("value", "N/A")
        }
    }
    
    return json.dumps(formatted_data, indent=2, ensure_ascii=False)

def get_ai_response(user_input: str, api_key: str, crunchbase_api_key: str) -> str:
    """
    Get AI response from the endpoint with retry logic and Crunchbase data integration
    """
    max_retries = 5  # 최대 재시도 횟수 증가
    retry_delay = 2  # seconds
    
    try:
        # Crunchbase 데이터 조회
        company_name = user_input.strip()
        crunchbase_data = get_crunchbase_data(company_name, crunchbase_api_key)
        if crunchbase_data is None:
            return "회사 정보를 찾을 수 없습니다. 회사 이름을 다시 확인해주세요."
            
        formatted_data = format_crunchbase_data(crunchbase_data)
        if formatted_data == "회사 정보를 찾을 수 없습니다.":
            return formatted_data
        
        for attempt in range(max_retries):
            try:
                # Enable SSL bypass
                allowSelfSignedHttps(True)
                
                # Prepare the request
                url = 'https://aisolcopilot7010956395.openai.azure.com/openai/deployments/o1/chat/completions'
                api_version = '2024-12-01-preview'
                
                # Set system message
                system_message = """You are a professional VC investment analyst. Your task is to evaluate the investment potential of a startup using Crunchbase data.  

Analyze the following information and provide an investment assessment:  

- **Company Overview**: {Company Name}, {Year Founded}, {Headquarters Location}, {Industry}  
- **Funding Details**: {Funding Stage}, {Total Funding Amount}, {Key Investors}  
- **Financial Data**: {Revenue Growth Rate}, {Profitability Metrics} (if available)  
- **Competitive Landscape**: {List of Competitors}  
- **Founders & Team**: {Founder Profiles}, {Key Team Members' Backgrounds}  
- **Market Size & Growth Potential**: {Market Growth Rate}, {Key Trends}  
- **Additional Factors**: {Patent Holdings}, {Partnerships}, {Recent Major News}  

Based on this data, answer the following questions:  

1. **Business Model & Profitability Analysis**: What is the company's business model, and is it sustainable?  
2. **Competitive Advantage**: What differentiates this company from its competitors?  
3. **Market Opportunity**: Considering current market trends and growth potential, can this company scale successfully?  
4. **Risk Factors**: What are the key risks associated with this company? (e.g., legal challenges, profitability concerns, competitive pressure)  
5. **Investment Suitability**: Is this company attractive for investment at its current stage? Why or why not?  

*note : always response in Korean"""
                
                # Prepare request data with Crunchbase information
                combined_input = f"Company: {company_name}\nCrunchbase Data:\n{formatted_data}\n\nUser Query: {user_input}"
                
                data = {
                    "messages": [
                        {"role": "system", "content": system_message},
                        {"role": "user", "content": combined_input}
                    ],
                    "max_completion_tokens": 4000,
                    "model": "o1-mini"
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
    
    # Sidebar for API keys
    with st.sidebar:
        st.title("API 설정")
        
        # Azure API Key input
        if 'api_key' not in st.session_state:
            api_key = st.text_input("Azure API Key", type="password")
            if st.button("Azure API 키 저장"):
                st.session_state.api_key = api_key
                st.rerun()
                
        # Crunchbase API Key input
        if 'crunchbase_api_key' not in st.session_state:
            crunchbase_api_key = st.text_input("Crunchbase API Key", type="password")
            if st.button("Crunchbase API 키 저장"):
                st.session_state.crunchbase_api_key = crunchbase_api_key
                st.rerun()
        
        if 'api_key' in st.session_state and 'crunchbase_api_key' in st.session_state:
            st.success("API 키가 설정되었습니다.")
            if st.button("API 키 재설정"):
                del st.session_state.api_key
                del st.session_state.crunchbase_api_key
                st.rerun()
    
    # Main container
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    
    # Notice section
    st.markdown("""
        <div class='notice-box'>
        <h3 style='color: #333333; margin-top: 0;'>⚠️ Notice</h3>
        <p style='color: #666666; margin-bottom: 0;'>등록된 DB 기반으로 최대한 충실하게 답변드리지만 반드시 정확하지는 않습니다.</p>
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
    if user_input and 'api_key' in st.session_state and 'crunchbase_api_key' in st.session_state:
        try:
            with st.chat_message("user"):
                st.write(user_input)
            st.session_state.chat_history.append({"role": "user", "content": user_input})
            
            response = get_ai_response(user_input, st.session_state.api_key, st.session_state.crunchbase_api_key)
            
            with st.chat_message("assistant"):
                st.write(response)
            st.session_state.chat_history.append({"role": "assistant", "content": response})
            
        except Exception as e:
            st.error(f"오류 발생: {str(e)}")
    elif user_input and ('api_key' not in st.session_state or 'crunchbase_api_key' not in st.session_state):
        st.warning("Azure API 키와 Crunchbase API 키를 모두 설정해주세요.")

if __name__ == "__main__":
    main()
