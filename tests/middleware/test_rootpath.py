# tests/middleware/test_rootpath.py
import pytest
from starlette.applications import Starlette
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse
from starlette.testclient import TestClient

def test_root_path_stripping_before_cors():
    """
    Verify that root_path stripping happens before CORS middleware processes the request
    """
    app = Starlette()
    
    paths_seen = []
    
    class PathTrackingMiddleware:
        def __init__(self, app):
            self.app = app
            
        async def __call__(self, scope, receive, send):
            paths_seen.append(scope["path"])
            await self.app(scope, receive, send)
    
    # Add middlewares in this order
    app.add_middleware(PathTrackingMiddleware)  # Will see stripped path
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    @app.route("/test")
    async def test_endpoint(request):
        return JSONResponse({"path": request.url.path})
    
    # Create test client that includes root_path in the ASGI scope
    client = TestClient(app, base_url="http://testserver", root_path="/prefix")
    
    # Test OPTIONS request (CORS preflight)
    response = client.options(
        "/test",  # TestClient will prepend the root_path
        headers={
            "Origin": "http://localhost",
            "Access-Control-Request-Method": "POST",
        },
    )
    assert response.status_code == 200
    assert "access-control-allow-origin" in response.headers
    # Verify path was stripped before reaching our tracking middleware
    assert "/test" in paths_seen
    assert "/prefix/test" not in paths_seen
