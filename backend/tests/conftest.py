import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Use a throwaway SQLite DB for the API test suite so it never touches
# a real dev/prod database.
os.environ.setdefault("DATABASE_URL", "sqlite:///./test_growth_intel.db")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret")
os.environ.setdefault("OPENAI_API_KEY", "")
