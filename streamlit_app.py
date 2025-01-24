import requests

AZURE_OPENAI_ENDPOINT = "https://rniaiproject4657409409.openai.azure.com"
AZURE_OPENAI_KEY = "EjEL2MlZ70BhFT2tyVloS624wLLXT8krtmv9EJu08hIdrR2AHZw5JQQJ99BAACHYHv6XJ3w3AAAAACOGWY3C"

def list_deployments():
    headers = {
        'api-key': AZURE_OPENAI_KEY
    }
    
    try:
        response = requests.get(
            f"{AZURE_OPENAI_ENDPOINT}/openai/deployments?api-version=2023-05-15",
            headers=headers
        )
        
        if response.status_code == 200:
            deployments = response.json()
            print("\nDeployed Models:")
            print("-" * 50)
            for deployment in deployments['data']:
                print(f"Deployment Name: {deployment['id']}")
                print(f"Model: {deployment['model']}")
                print(f"Status: {deployment['status']}")
                print("-" * 50)
        else:
            print(f"Error: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    list_deployments() 
