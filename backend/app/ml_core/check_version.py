import os
import google.generativeai as genai
from dotenv import load_dotenv

# 1. Load the Key
load_dotenv()
key = os.getenv("GOOGLE_API_KEY")

print(f"🔑 Key Loaded: {str(key)[:10]}... (hidden)")

# 2. Configure Google AI
try:
    genai.configure(api_key=key)
    print("✅ Configuration successful. Fetching models...")
    
    # 3. List Models
    models = list(genai.list_models())
    if not models:
        print("❌ No models returned. Check API Key permissions.")
    else:
        print("\n👇 AVAILABLE MODELS (Copy one of these exactly):")
        for m in models:
            if 'generateContent' in m.supported_generation_methods:
                # We strip 'models/' to make it easier to copy
                clean_name = m.name.replace("models/", "")
                print(f"   • {clean_name}")

except Exception as e:
    print(f"\n❌ CRASH: {e}")