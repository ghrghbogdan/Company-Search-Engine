import ollama
import json
from systemprompt import get_system_prompt

class FilterGenerator:
    """Filter generator using Llama-3.2-3B"""
    
    def __init__(self):
        self.model = "llama3.2:3b"
        print("Initialized FilterGenerator with model:", self.model)

    def get_logic_filters(self, query):
        system_prompt = get_system_prompt()
        response = ollama.generate(
            model=self.model,
            system=system_prompt,
            prompt=query,
            format="json",
            options={"temperature": 0}
        )
        
        try:
            raw_data = json.loads(response['response'])
            def clean_none(d):
                if not isinstance(d, dict):
                    return d
                return {k: clean_none(v) for k, v in d.items() if v is not None}
            return clean_none(raw_data)
        except Exception as e:
            print(f"Parsing error: {e}")
            return {}
