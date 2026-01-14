import time
import uuid
from flask import g, request, jsonify
from werkzeug.exceptions import HTTPException


def register_observability(app):
    @app.before_request
    def _start_request():
        g.request_start_time = time.time()
        g.request_id = request.headers.get("X-Request-Id") or uuid.uuid4().hex

    @app.after_request
    def _end_request(response):
        request_id = getattr(g, "request_id", None)
        if request_id:
            response.headers["X-Request-Id"] = request_id

        if request.path.startswith("/api"):
            start = getattr(g, "request_start_time", None)
            duration_ms = None
            if start is not None:
                duration_ms = round((time.time() - start) * 1000, 2)

            app.logger.info(
                "request",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.path,
                    "status": response.status_code,
                    "duration_ms": duration_ms,
                    "remote_addr": request.headers.get("X-Forwarded-For", request.remote_addr),
                },
            )
        return response

    @app.errorhandler(Exception)
    def _handle_error(err):
        if request.path.startswith("/api"):
            request_id = getattr(g, "request_id", None)
            if isinstance(err, HTTPException):
                payload = {"error": err.name, "message": err.description, "request_id": request_id}
                return jsonify(payload), err.code

            app.logger.exception(
                "unhandled_exception",
                extra={"request_id": request_id, "path": request.path, "method": request.method},
            )
            return jsonify({"error": "Internal Server Error", "message": "Internal server error", "request_id": request_id}), 500

        raise err

