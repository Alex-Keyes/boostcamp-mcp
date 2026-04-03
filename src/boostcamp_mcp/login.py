import os
import asyncio
import getpass
from dotenv import load_dotenv, set_key
from pathlib import Path
from boostcampapi import BoostcampAPI

# Load existing .env if it exists
env_path = Path(".env")
load_dotenv(dotenv_path=env_path)

async def login():
    print(f"--- Boostcamp API Login (Library Wrapper) ---")
    
    email = input("Email: ")
    password = getpass.getpass("Password: ")

    try:
        api = BoostcampAPI()
        # Attempt to login using the library's built-in method
        token = await api.login(email, password)
        
        if token:
            # Save to .env file
            if not env_path.exists():
                env_path.touch()
            
            set_key(str(env_path), "BOOSTCAMP_AUTH_TOKEN", token)
            print("\n✅ Login successful!")
            print(f"Token saved to {env_path.absolute()}")
        else:
            print("\n❌ Login failed: No token returned. Please check your credentials.")
                
    except Exception as e:
        print(f"\n❌ Login error: {str(e)}")

def main():
    asyncio.run(login())

if __name__ == "__main__":
    main()
