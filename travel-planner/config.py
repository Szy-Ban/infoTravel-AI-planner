import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

# Wybór dostawcy modelu (LLM_PROVIDER):
#   "openai-3.5"    => GPT-3.5-turbo
#   "openai-4"      => GPT-4
#   "openai-4o-mini"=> GPT-4o-mini ("gpt-4o-mini-2024-07-18")
#   "huggingface"   => lokalny model HF
#   "groq"          => Groq LLama
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai-4o-mini")

OPENAI_4O_MINI_MODEL = "gpt-4o-mini"

HUGGINGFACE_LLAMA_MODEL = "meta-llama/Llama-2-7b-chat-hf"

POI_DATA_FILE = "csvjson.json"

MAX_TOKENS = 1000
TEMPERATURE = 0.7


DEFAULT_DAILY_ACTIVITIES = 3
MIN_ACTIVITIES_PER_DAY = 1
MAX_ACTIVITIES_PER_DAY = 5
DEFAULT_TRIP_DURATION = 3
MAX_TRIP_DURATION = 14

DEFAULT_START_TIME = "09:00"
DEFAULT_END_TIME = "18:00"
BREAK_DURATION = 60  # min
