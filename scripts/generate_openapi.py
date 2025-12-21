import json
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.main import app

def generate_openapi():
    openapi_schema = app.openapi()
    
    output_path = os.path.join(os.path.dirname(__file__), '..', 'openapi.json')
    with open(output_path, 'w') as f:
        json.dump(openapi_schema, f, indent=2)
    
    print(f"OpenAPI specification generated at {output_path}")

if __name__ == "__main__":
    generate_openapi()
