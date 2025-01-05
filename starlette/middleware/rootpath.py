# starlette/middleware/rootpath.py
from starlette.types import ASGIApp, Message, Receive, Scope, Send

class RootPathStrippingMiddleware:
    def __init__(self, app: ASGIApp, root_path: str) -> None:
        self.app = app
        self.root_path = root_path.rstrip("/")

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        path = scope["path"]
        if path.startswith(self.root_path):
            scope["original_path"] = path
            scope["path"] = path[len(self.root_path):] or "/"

        await self.app(scope, receive, send)
