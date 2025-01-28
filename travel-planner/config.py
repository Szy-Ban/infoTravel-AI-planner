import os

from dotenv import load_dotenv
import os

# load .env file
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY","")
POI_DATA_FILE = "csvjson.json"

# OpenAI config
GPT_MODEL = "gpt-3.5-turbo"
MAX_TOKENS = 1000
TEMPERATURE = 0.7

# Travel planner config
DEFAULT_DAILY_ACTIVITIES = 3
MIN_ACTIVITIES_PER_DAY = 1
MAX_ACTIVITIES_PER_DAY = 5
DEFAULT_TRIP_DURATION = 3
MAX_TRIP_DURATION = 14

# Time config
DEFAULT_START_TIME = "09:00"
DEFAULT_END_TIME = "18:00"
BREAK_DURATION = 60  # min