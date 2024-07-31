import os


class Config:
    CACHE_EXPIRATION = int(os.getenv("CACHE_EXPIRATION", 604800))  # 1 week in seconds
    CACHE_NAME = os.getenv("CACHE_NAME", "helpers/google_books_cache")
    RESULTS_FILENAME = os.getenv("RESULTS_FILENAME", "helpers/results.json")
