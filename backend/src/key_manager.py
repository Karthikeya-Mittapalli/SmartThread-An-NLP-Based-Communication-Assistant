import os
from dotenv import load_dotenv

load_dotenv()

class KeyManager:
    def __init__(self):
        """
        Loads all OPENROUTER_API_KEY_* from the environment
        and prepares them for round-robin rotation.
        """
        self.api_keys = []
        # Dynamically load all keys that match the pattern
        for key, value in os.environ.items():
            if key.startswith("OPENROUTER_API_KEY_"):
                self.api_keys.append(value)
        
        if not self.api_keys:
            raise ValueError("No OPENROUTER_API_KEY_* found in your .env file.")
            
        self.current_index = 0
        print(f"[KeyManager] Loaded {len(self.api_keys)} API keys successfully.")

    def get_key(self) -> str:
        """
        Returns the next API key in the rotation. 🔄
        """
        # Get the key at the current index
        key = self.api_keys[self.current_index]
        
        # Move to the next index, wrapping around if necessary
        self.current_index = (self.current_index + 1) % len(self.api_keys)
        
        return key

# Create a single, shared instance of the manager
key_manager = KeyManager()