import tiktoken
import os
from typing import Dict, List, Tuple

class TokenEstimator:
    def __init__(self, model_name: str = "gpt-4"):
        self.encoder = tiktoken.encoding_for_model(model_name)
    
    def estimate_tokens(self, text: str) -> int:
        return len(self.encoder.encode(text))
    
    def estimate_file_tokens(self, file_path: str) -> int:
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return self.estimate_tokens(f.read())
        except:
            return 0
    
    def estimate_codebase_tokens(self, files: List[Dict]) -> int:
        total = 0
        for file_data in files:
            if 'content' in file_data:
                total += self.estimate_tokens(file_data['content'])
            else:
                total += file_data.get('size', 0) // 4  # Rough estimate
        return total