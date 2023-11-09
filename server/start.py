import uvicorn
import os
from dotenv import load_dotenv

if __name__ == "__main__":
    dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
    if os.path.exists(dotenv_path):
        load_dotenv(dotenv_path)
    uvicorn.run(
        "main:app",
        port=8000,
        reload=True,
        log_level="info",
        forwarded_allow_ips="*",
        proxy_headers=True,
    )
