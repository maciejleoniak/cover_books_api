import json
import logging
import os

import requests
import requests_cache
from config import Config
from requests.exceptions import RequestException


class GoogleAPIService:
    '''
    A service class for interacting with the Google Books API to search for books by ISBN 
    and save book thumbnails to a local JSON file with caching capabilities.
    '''
    def __init__(self):
        self.cache_name = Config.CACHE_NAME
        self.cache_expiration = Config.CACHE_EXPIRATION
        self.results_filename = Config.RESULTS_FILENAME

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
        params = {
            "fields": "kind,items(volumeInfo/title),items(volumeInfo/subtitle),items(volumeInfo/imageLinks),items(volumeInfo/industryIdentifiers)"
        }
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            if hasattr(response, "from_cache") and response.from_cache:
                logging.info("Response from cache")
            else:
                logging.info("Response from API")
            return response.json()
        except RequestException as e:
            logging.error(f"Error fetching data: {e}")
            return {}

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
                    logging.error("Error decoding JSON from file")
                    return {}
        return {}

    def _save_data(self, data):
        """Save data to the JSON file."""
        with open(self.results_filename, "w") as file:
            json.dump(data, file, indent=4)

    def fetch_and_save_book_thumbnails(self, isbn):
        """Fetch book thumbnails and save them to the JSON file."""
        all_isbn_thumbnail_dict = self._load_existing_data()

        book = self.search_books_by_isbn(isbn)
        isbn_thumbnail_dict = self._extract_isbn_thumbnail_dict(book)
        all_isbn_thumbnail_dict.update(isbn_thumbnail_dict)

        self._save_data(all_isbn_thumbnail_dict)

        return isbn_thumbnail_dict


# Set up logging
logging.basicConfig(level=logging.INFO)
