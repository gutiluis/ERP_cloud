# file: api/errors.py
# descr: client error handlers


from flask import render_template, request, jsonify


def register_error_handlers(app):
    @app.errorhandler(400)
    def bad_request(e):
        """Handle HTTP 400 Bad Request errors."""
        if (
            request.accept_mimetypes.accept_json
            and not request.accept_mimetypes.accept_html
        ):
            return jsonify({"error": "bad request"}), 400

        return render_template("400.html"), 400

    @app.errorhandler(401)
    def unauthorized(e):
        """Handle HTTP 401 Unauthorized errors."""
        if (
            request.accept_mimetypes.accept_json
            and not request.accept_mimetypes.accept_html
        ):
            return jsonify({"error": "unauthorized"}), 401

        return render_template("401.html"), 401

    @app.errorhandler(404)
    def page_not_found(e):
        """Handle HTTP 404 Not Found errors."""
        if (
            request.accept_mimetypes.accept_json
            and not request.accept_mimetypes.accept_html
        ):
            return jsonify({"error": "not found"}), 404

        return render_template("404.html"), 404

    @app.errorhandler(405)
    def method_not_allowed(e):
        """Handle HTTP 405 Method Not Allowed errors."""
        if (
            request.accept_mimetypes.accept_json
            and not request.accept_mimetypes.accept_html
        ):
            return jsonify({"error": "method not allowed"}), 405

        return render_template("405.html"), 405

    @app.errorhandler(500)
    def internal_server_error(e):
        """Handle HTTP 500 Internal Server Error responses."""
        if (
            request.accept_mimetypes.accept_json
            and not request.accept_mimetypes.accept_html
        ):
            return jsonify({"error": "internal server error"}), 500

        return render_template("500.html"), 500


def forbidden(message):
    """API error handler for status code 403"""
    response = jsonify({"error": "forbidden", "message": message})
    response.status_code = 403
    return response
