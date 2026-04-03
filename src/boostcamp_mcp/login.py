import os
import httpx
import getpass
from dotenv import load_dotenv, set_key
from pathlib import Path

# Load existing .env if it exists
env_path = Path(".env")
load_dotenv(dotenv_path=env_path)

API_URL = os.getenv("BOOSTCAMP_API_URL", "http://localhost:5000/api/v1")

async def login():
    print(f"--- Boostcamp API Login ---")
    print(f"Connecting to: {API_URL}")
    
    email = input("Email: ")
    password = getpass.getpass("Password: ")

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{API_URL}/auth/login",
                json={"email": email, "password": password}
            )
            
            if response.status_code == 200:
                data = response.json()
                token = data.get("token")
                
                if token:
                    # Save to .env file
                    if not env_path.exists():
                        env_path.touch()
                    
                    set_key(str(env_path), "BOOSTCAMP_AUTH_TOKEN", token)
                    print("\n✅ Login successful!")
                    print(f"Token saved to {env_path.absolute()}")
                else:
                    print("\n❌ Error: Token not found in response.")
            else:
                error_data = response.json()
                print(f"\n❌ Login failed ({response.status_code}): {error_data.get('error', 'Unknown error')}")
                
    except Exception as e:
        print(f"\n❌ Connection error: {str(e)}")

def main():
    import asyncio
    asyncio.run(login())

if __name__ == "__main__":
    main()
