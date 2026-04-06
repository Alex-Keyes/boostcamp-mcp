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
    print("--- Boostcamp API Login ---")

    # Check for stored credentials
    email = os.getenv("BOOSTCAMP_EMAIL", "")
    password = os.getenv("BOOSTCAMP_PASSWORD", "")

    if email and password:
        print(f"Using stored credentials for {email}")
    else:
        email = input("Email: ")
        password = getpass.getpass("Password: ")

    try:
        api = BoostcampAPI()
        await api.login(email, password)

        if api.token:
            if not env_path.exists():
                env_path.touch()

            set_key(str(env_path), "BOOSTCAMP_EMAIL", email)
            set_key(str(env_path), "BOOSTCAMP_PASSWORD", password)
            set_key(str(env_path), "BOOSTCAMP_AUTH_TOKEN", api.token)
            print("\n✅ Login successful!")
            print(f"Credentials and token saved to {env_path.absolute()}")
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
