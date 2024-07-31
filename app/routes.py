from flask import jsonify, request
from main import GoogleAPIService

google_api_service = GoogleAPIService()


def configure_routes(app):
    @app.route("/get_book_cover", methods=["GET"])
    def get_book_cover():
        """
        Endpoint to get book cover thumbnails by ISBN.
        """
        isbn = request.args.get("isbn")
        if not isbn:
            return jsonify({"error": "ISBN is required"}), 400

        try:
            # Fetch book thumbnail using the GoogleAPIService
            book_thumbnail_dict = google_api_service.fetch_and_save_book_thumbnails(
                isbn
            )
            if not book_thumbnail_dict:
                return (
                    jsonify({"message": "No thumbnail found for the provided ISBN"}),
                    404,
                )
            return (
                jsonify(
                    {
                        "message": "Thumbnail fetched successfully",
                        "data": book_thumbnail_dict,
                    }
                ),
                200,
            )
        except Exception as e:
            return jsonify({"error": str(e)}), 500
