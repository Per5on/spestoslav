"""Enforce a streaming upload cap, including chunked requests, before spooling."""

from fastapi import HTTPException
from starlette.responses import JSONResponse


class ReceiptUploadLimit:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if (
            scope["type"] != "http"
            or scope["method"] != "POST"
            or scope.get("path") != "/api/v1/receipts"
        ):
            return await self.app(scope, receive, send)
        maximum = 9 * 1024 * 1024
        headers = dict(scope.get("headers", []))
        try:
            if int(headers.get(b"content-length", b"0")) > maximum:
                return await JSONResponse(
                    {"detail": "Receipt upload exceeds size limit"}, status_code=413
                )(scope, receive, send)
        except ValueError:
            return await JSONResponse(
                {"detail": "Invalid content length"}, status_code=400
            )(scope, receive, send)
        size = 0

        async def bounded_receive():
            nonlocal size
            message = await receive()
            size += len(message.get("body", b""))
            if size > maximum:
                raise HTTPException(413, "Receipt upload exceeds size limit")
            return message

        await self.app(scope, bounded_receive, send)
