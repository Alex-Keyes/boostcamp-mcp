import os
import asyncio
import getpass
from dotenv import load_dotenv, set_key
from pathlib import Path
from boostcampapi import BoostcampAPI, LoginFailedException

# Load existing .env if it exists
env_path = Path(".env")
load_dotenv(dotenv_path=env_path)

async def login():
    print(f"--- Boostcamp API Login (Library Wrapper) ---")
    
    email = input("Email: ")
    password = getpass.getpass("Password: ")

    try:
        api = BoostcampAPI()
        # The library method returns None but sets api.token internally
        await api.login(email, password)
        
        if api.token:
            # Save to .env file
            if not env_path.exists():
                env_path.touch()
            
            set_key(str(env_path), "BOOSTCAMP_AUTH_TOKEN", api.token)
            print("\n✅ Login successful!")
            print(f"Token saved to {env_path.absolute()}")
        else:
            print("\n❌ Login failed: No token found after login attempt.")
                
    except LoginFailedException as e:
        print(f"\n❌ Login failed: {str(e)}")
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")

def main():
    asyncio.run(login())

if __name__ == "__main__":
    main()
