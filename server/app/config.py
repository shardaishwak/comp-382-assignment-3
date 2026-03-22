import os


class Config:
    SECRET_KEY = os.environ.get("FLASK_SECRET_KEY", "pcp-dev-secret-key")
    CORS_ORIGIN = os.environ.get("CORS_ORIGIN", "http://localhost:3000") # Assuming that NextJS is running on 3000