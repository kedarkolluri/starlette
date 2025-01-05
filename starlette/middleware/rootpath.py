# starlette/middleware/rootpath.py
from starlette.types import ASGIApp, Message, Receive, Scope, Send

class RootPathStrippingMiddleware:
    def __init__(self, app: ASGIApp, root_path: str) -> None:
        self.app = app
        self.root_path = root_path.rstrip("/")  # Ensure no trailing slash

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":  # Only handle HTTP requests
            await self.app(scope, receive, send)
            return

        path = scope["path"]
        current_root_path = scope.get("root_path", "")
        if path.startswith(current_root_path):
            # Store original path in case it's needed
            scope["original_path"] = path
            # Strip the root_path
            scope["path"] = path[len(current_root_path):] or "/"

        await self.app(scope, receive, send)
