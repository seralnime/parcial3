import os
from dotenv import load_dotenv
from urllib.parse import urlparse
import psycopg2

# Load environment variables
load_dotenv()

url = os.getenv("DATABASE_URL")
if not url:
    print("❌ DATABASE_URL not found in .env")
    exit(1)

try:
    # Parse the URL safely
    parsed = urlparse(url)
    
    print("--- Connection Details Analysis ---")
    print(f"Host: {parsed.hostname}")
    print(f"Port: {parsed.port}")
    print(f"Username: {parsed.username}")
    print("Password: [HIDDEN]")
    print(f"Database: {parsed.path[1:] if parsed.path else ''}")
    
    # Check for Supabase Pooler specific requirements
    if parsed.port == 6543:
        print("\n[!] Detected Supabase Transaction Pooler (port 6543)")
        if parsed.username and "." not in parsed.username:
            print("❌ ERROR: When using port 6543, the username MUST be in the format 'postgres.[project-ref]'.")
            print(f"   Current username '{parsed.username}' seems to be missing the project reference.")
            print("   Example: postgres.abcdefghijklm")
        else:
            print("✅ Username format looks correct for port 6543 (contains a dot).")
    elif parsed.port == 5432:
        print("\n[i] Detected Direct Connection (port 5432)")
        print("   Standard 'postgres' username is usually correct here.")
    
    print("\n--- Attempting Connection ---")
    conn = psycopg2.connect(url)
    print("✅ Connection SUCCESSFUL!")
    conn.close()

except Exception as e:
    print(f"❌ Connection FAILED: {e}")
