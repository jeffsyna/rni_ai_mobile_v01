import requests

AZURE_OPENAI_ENDPOINT = "https://rniaiproject4657409409.openai.azure.com"
AZURE_OPENAI_KEY = "EjEL2MlZ70BhFT2tyVloS624wLLXT8krtmv9EJu08hIdrR2AHZw5JQQJ99BAACHYHv6XJ3w3AAAAACOGWY3C"

def list_deployments():
    headers = {
        'api-key': AZURE_OPENAI_KEY
    }
    
    try:
        # 다른 API 버전으로 시도
        api_versions = ["2023-12-01-preview", "2023-05-15", "2024-02-15-preview"]
        
        for version in api_versions:
            print(f"\nTrying API version: {version}")
            response = requests.get(
                f"{AZURE_OPENAI_ENDPOINT}/openai/deployments?api-version={version}",
                headers=headers
            )
            
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.text}")
            
            if response.status_code == 200:
                deployments = response.json()
                print("\nDeployed Models:")
                print("-" * 50)
                for deployment in deployments.get('data', []):
                    print(f"Deployment Name: {deployment.get('id')}")
                    print(f"Model: {deployment.get('model')}")
                    print(f"Status: {deployment.get('status')}")
                    print("-" * 50)
                break
            
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    list_deployments() 
