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
        # Keep credentials out of the library's session file. The MCP provider
        # reads tokens from .env instead.
        await api.login(email, password, save_session=False)
        
        if api.token:
            refresh_token = getattr(api, "_refresh_token", None)
            if not isinstance(refresh_token, str) or not refresh_token:
                print("\n❌ Login failed: No refresh token returned. Update dependencies with 'uv sync --upgrade-package boostcampapi' and try again.")
                return
            # Save to .env file
            if not env_path.exists():
                env_path.touch(mode=0o600)
            
            set_key(str(env_path), "BOOSTCAMP_AUTH_TOKEN", api.token)
            set_key(str(env_path), "BOOSTCAMP_REFRESH_TOKEN", refresh_token)
            print("\n✅ Login successful!")
            print(f"Tokens saved to {env_path.absolute()}; ID tokens will refresh automatically.")
        else:
            print("\n❌ Login failed: No token found after login attempt.")
                
    except LoginFailedException:
        print("\n❌ Login failed: Check your email and password and try again.")
    except Exception:
        print("\n❌ Login failed: Check connectivity and that .env is writable, then try again.")

def main():
    asyncio.run(login())

if __name__ == "__main__":
    main()
