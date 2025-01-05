# tests/middleware/test_rootpath.py

import pytest
from starlette.applications import Starlette
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse
from starlette.testclient import TestClient

def test_root_path_stripping_before_cors():
    app = Starlette(root_path="/prefix")
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    @app.route("/test")
    async def test_endpoint(request):
        return JSONResponse({"path": request.url.path})
    
    client = TestClient(app)
    
    # Test OPTIONS request (CORS preflight)
    response = client.options(
        "/prefix/test",
        headers={
            "Origin": "http://localhost",
            "Access-Control-Request-Method": "POST",
        },
    )
    assert response.status_code == 200
    assert "access-control-allow-origin" in response.headers
    
    # Test regular request
    response = client.get("/prefix/test")
    assert response.status_code == 200
    assert response.json()["path"] == "/test"

def test_root_path_stripping_preserves_original_path():
    app = Starlette(root_path="/prefix")
    
    @app.route("/test")
    async def test_endpoint(request):
        return JSONResponse({
            "path": request.url.path,
            "original_path": request.scope.get("original_path")
        })
    
    client = TestClient(app)
    response = client.get("/prefix/test")
    assert response.status_code == 200
    assert response.json() == {
        "path": "/test",
        "original_path": "/prefix/test"
    }

def test_root_path_stripping_handles_multiple_segments():
    app = Starlette(root_path="/prefix/v1")
    
    @app.route("/test")
    async def test_endpoint(request):
        return JSONResponse({"path": request.url.path})
    
    client = TestClient(app)
    response = client.get("/prefix/v1/test")
    assert response.status_code == 200
    assert response.json()["path"] == "/test"
