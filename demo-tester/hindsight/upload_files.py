#!/usr/bin/env python3
"""
Upload memory files to hindsight bank via files/retain endpoint,
then use reflect for consolidation.
"""
import json
import os
import urllib.request
import uuid

HINDSIGHT_URL = "http://127.0.0.1:8888"
BANK_ID = "demo-tester"

def main():
    mem_dir = os.path.expanduser("~/.hermes/profiles/demo-tester/memories")
    memory_md = open(os.path.join(mem_dir, "MEMORY.md")).read()
    user_md = open(os.path.join(mem_dir, "USER.md")).read()

    # Step 1: Try to retain via files/retain as multipart
    # Build the multipart form data
    boundary = f"----{uuid.uuid4().hex}"
    
    request_body = b""
    
    # File 1: MEMORY.md
    request_body += f"--{boundary}\r\n".encode()
    request_body += b'Content-Disposition: form-data; name="files"; filename="MEMORY.md"\r\n'
    request_body += b"Content-Type: text/markdown\r\n\r\n"
    request_body += memory_md.encode()
    request_body += b"\r\n"
    
    # File 2: USER.md
    request_body += f"--{boundary}\r\n".encode()
    request_body += b'Content-Disposition: form-data; name="files"; filename="USER.md"\r\n'
    request_body += b"Content-Type: text/markdown\r\n\r\n"
    request_body += user_md.encode()
    request_body += b"\r\n"
    
    # Metadata
    request_meta = json.dumps({
        "document_tags": ["agent_memory", "operational"],
        "parser": "markitdown"
    })
    request_body += f"--{boundary}\r\n".encode()
    request_body += b'Content-Disposition: form-data; name="request"\r\n'
    request_body += b"Content-Type: application/json\r\n\r\n"
    request_body += request_meta.encode()
    request_body += b"\r\n"
    
    request_body += f"--{boundary}--\r\n".encode()
    
    url = f"{HINDSIGHT_URL}/v1/default/banks/{BANK_ID}/files/retain"
    req = urllib.request.Request(url, data=request_body, headers={"Content-Type": f"multipart/form-data; boundary={boundary}"})
    
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            result = json.loads(resp.read())
        print(json.dumps(result, indent=2))
    except urllib.error.HTTPError as e:
        print(f"HTTP Error {e.code}: {e.read().decode()[:500]}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
