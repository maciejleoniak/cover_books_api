from flask import jsonify, request
from main import GoogleAPIService

google_api_service = GoogleAPIService()


def configure_routes(app):
    @app.route("/get-book-thumbnail", methods=["GET"])
    def get_book_thumbnail():
        """
        Endpoint to get book cover thumbnails by ISBN.
        """
        isbn = request.args.get("isbn")
        if not isbn:
            google_api_service.increment_error_count()
            return jsonify({"error": "ISBN is required"}), 400

        try:
            book_thumbnail_dict = google_api_service.fetch_and_save_book_thumbnail(isbn)
            if not book_thumbnail_dict:
                google_api_service.increment_error_count()
                return jsonify({"message": "No thumbnail found for the provided ISBN"}), 404
            return jsonify({"message": "Thumbnail fetched successfully", "data": book_thumbnail_dict}), 200
        except Exception as e:
            return handle_exception(e)

    @app.route("/get-book-thumbnails", methods=["POST"])
    def get_book_thumbnails():
        """
        Endpoint to get multiple book cover thumbnails by ISBN-13 list.
        """
        data = request.get_json()
        if not data or "isbn_13_list" not in data:
            google_api_service.increment_error_count()
            return jsonify({"error": "No ISBN-13 list provided"}), 400

        isbn_13_list = data.get("isbn_13_list", [])
        if not isbn_13_list:
            google_api_service.increment_error_count()
            return jsonify({"error": "ISBN-13 list is empty"}), 400

        try:
            result = google_api_service.fetch_and_save_book_thumbnails(isbn_13_list)
            return jsonify(result), 200
        except Exception as e:
            return handle_exception(e)
        
    @app.route('/stats')
    def get_stats():
        stats = google_api_service.get_statistics()
        return jsonify(stats)


def handle_exception(exception: Exception):
    """
    Handle exceptions and return a JSON response with a 500 status code.
    """
    google_api_service.increment_error_count()
    return jsonify({"error": str(exception)}), 500