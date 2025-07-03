import os
from typing import Optional, List

def read_txt_file(file_path: str, encoding: str = 'utf-8') -> Optional[str]:
    try:
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            return None
            
        with open(file_path, 'r', encoding=encoding) as file:
            return file.read()
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return None
