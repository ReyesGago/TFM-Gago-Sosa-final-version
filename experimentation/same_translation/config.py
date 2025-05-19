import os

# API Keys
OPENAI_API_KEY = "**OPENAI_API_KEY**"
GEMINI_API_KEY = "**GEMINI_API_KEY**"
TOGETHER_API_KEY = "**TOGETHER_API_KEY**"

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS_DIR = os.path.join(BASE_DIR, "same_translation")

# Example file paths
CSV_PATHS = {
    "es_en": "../context_recopilation_test_es_en.csv",
    "en_es": "../context_recopilation_test_en_es.csv",
    "es_ba": "../context_recopilation_test_es_ba.csv",
    "en_ba": "../context_recopilation_test_en_ba.csv"
}

# Garaterm corpus paths
GARATERM_PATHS = {
    "ba_es": r"../context_recopilation_test_ba_es.csv",
    "ba_en": r"../context_recopilation_test_ba_en.csv",
}

# Output directories
OUTPUT_DIRS = {
    "gpt": os.path.join(RESULTS_DIR, "gpt/results_gpt/"),
    "llama": os.path.join(RESULTS_DIR, "llama/results_llama/"),
    "gemini": os.path.join(RESULTS_DIR, "gemini/results_gemini/"),
    "latxa": os.path.join(RESULTS_DIR, "latxa/results_latxa/"),
}

# Latxa model configuration
LATXA_MODEL = "Latxa-Llama-3.1-70B-Instruct-exp_2_101"
LATXA_HOST = "158.227.114.118"
LATXA_PORT = 8002
LATXA_URL = f"http://{LATXA_HOST}:{LATXA_PORT}/v1/chat/completions"
