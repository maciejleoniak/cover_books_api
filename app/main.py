import json
import logging
import os

import requests
import requests_cache
from config import Config
from requests.exceptions import RequestException
from datetime import datetime, timedelta

class GoogleAPIService:
    """A service class for fetching and caching book thumbnails from the Google Books API."""

    def __init__(self):
        self.cache_name = Config.CACHE_NAME
        self.cache_expiration = Config.CACHE_EXPIRATION
        self.results_filename = Config.RESULTS_FILENAME

        self.api_hits = 0
        self.cache_hits = 0
        self.error_count = 0
        self.start_time = datetime.now()
        

        # Ensure the cache directory exists
        os.makedirs(os.path.dirname(self.cache_name), exist_ok=True)
        # Install cache
        requests_cache.install_cache(
            self.cache_name,
            backend="sqlite",
            expire_after=self.cache_expiration,
        )


    def search_books_by_isbn(self, isbn):
        """Search books by ISBN using Google Books API."""
        query = f"isbn:{isbn}"
        url = f"https://www.googleapis.com/books/v1/volumes?q={query}"
        params = {"fields": "kind,items(volumeInfo/title),items(volumeInfo/subtitle),items(volumeInfo/imageLinks),items(volumeInfo/industryIdentifiers)"}
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()

            if hasattr(response, "from_cache") and response.from_cache:
                self.cache_hits += 1
                logging.info("Response from cache for ISBN: %s", isbn)
            else:
                self.api_hits += 1
                logging.info("Response from API for ISBN: %s", isbn)

            return response.json()
        except RequestException as e:
            self.error_count += 1
            logging.error("Error fetching data for ISBN %s: %s", isbn, e)
            return {}

    def get_statistics(self):
        """Return the current statistics of API and cache hits."""
        current_time = datetime.now()
        uptime = current_time - self.start_time
        cache_expiration_time = self.start_time + timedelta(seconds=self.cache_expiration)
        cache_countdown = cache_expiration_time - current_time if cache_expiration_time > current_time else timedelta(seconds=0)
        
        return {
            "api_hits": self.api_hits,
            "cache_hits": self.cache_hits,
            "error_count": self.error_count,
            "service_start_time": self.start_time.isoformat(),
            "uptime": str(uptime),
            "tcache_countdown": str(cache_countdown)
        }


    def increment_error_count(self):
        """Increment the error count."""
        self.error_count += 1


    def _extract_isbn_thumbnail_dict(self, response):
        """Extract ISBN-13 and thumbnail URL from the API response."""
        isbn_thumbnail_dict = {}
        items = response.get("items", [])

        for item in items:
            volume_info = item.get("volumeInfo", {})
            industry_identifiers = volume_info.get("industryIdentifiers", [])
            image_links = volume_info.get("imageLinks", {})
            thumbnail = image_links.get("thumbnail")

            for identifier in industry_identifiers:
                isbn_type = identifier.get("type")
                isbn = identifier.get("identifier")
                if isbn_type == "ISBN_13" and thumbnail:
                    isbn_thumbnail_dict[isbn] = thumbnail

        return isbn_thumbnail_dict

    def _load_existing_data(self):
        """Load existing data from the JSON file."""
        if os.path.exists(self.results_filename):
            with open(self.results_filename, "r") as file:
                try:
                    return json.load(file)
                except json.JSONDecodeError:
                    self.error_count += 1
                    logging.error("Error decoding JSON from file")
                    return {}
        return {}

    def _save_data(self, data):
        """Save data to the JSON file."""
        with open(self.results_filename, "w") as file:
            json.dump(data, file, indent=4)

    def fetch_and_save_book_thumbnail(self, isbn):
        """Fetch book thumbnails and save them to the JSON file."""
        all_isbn_thumbnail_dict = self._load_existing_data()

        book = self.search_books_by_isbn(isbn)
        isbn_thumbnail_dict = self._extract_isbn_thumbnail_dict(book)
        all_isbn_thumbnail_dict.update(isbn_thumbnail_dict)

        self._save_data(all_isbn_thumbnail_dict)

        return isbn_thumbnail_dict

    def fetch_and_save_book_thumbnails(self, isbn_13_list):
        """
        Fetch list of books and save book thumbnails to the JSON file.
        """
        all_isbn_thumbnail_dict = {}

        for isbn in isbn_13_list:
            if book := self.search_books_by_isbn(isbn):
                isbn_thumbnail_dict = self._extract_isbn_thumbnail_dict(book)
                all_isbn_thumbnail_dict.update(isbn_thumbnail_dict)

        existing_data = self._load_existing_data()
        existing_data.update(all_isbn_thumbnail_dict)
        self._save_data(existing_data)

        return all_isbn_thumbnail_dict


# Set up logging
logging.basicConfig(level=logging.INFO)
