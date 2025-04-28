"""
Trading Indicator App - FastAPI backend
"""
import logging
import traceback
import json
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse
import numpy as np

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import routes
from routes import analyze_routes, market_data_routes

# Custom JSON encoder for numpy types
class NumpyEncoder(json.JSONEncoder):
    """Custom JSON encoder for numpy types"""
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            # Handle NaN, Infinity, and extremely small values
            if np.isnan(obj) or np.isinf(obj) or abs(obj) < 1e-10:
                return None
            return float(obj)
        elif isinstance(obj, np.ndarray):
            # Handle arrays with NaN values
            processed_array = obj.tolist()
            # Recursively handle nested arrays
            if isinstance(processed_array, list):
                for i, val in enumerate(processed_array):
                    if isinstance(val, float) and (np.isnan(val) or np.isinf(val) or abs(val) < 1e-10):
                        processed_array[i] = None
            return processed_array
        elif isinstance(obj, np.bool_):
            return bool(obj)
        elif obj is None:
            return None
        return json.JSONEncoder.default(self, obj)

# Create a custom JSONResponse class that uses our encoder
class CustomJSONResponse(JSONResponse):
    def render(self, content) -> bytes:
        return json.dumps(
            content,
            ensure_ascii=False,
            allow_nan=False,
            indent=None,
            separators=(",", ":"),
            cls=NumpyEncoder,
        ).encode("utf-8")

# Create the main FastAPI app
app = FastAPI(
    title="Trading Indicator API",
    description="API for technical analysis and trading signals",
    version="1.0.0",
    default_response_class=CustomJSONResponse
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root endpoints
@app.get("/")
async def root():
    """Root endpoint for status check"""
    return {"message": "Trading Indicator API is running"}

@app.get("/api")
async def api_root():
    """Root endpoint for API status check"""
    return {"status": "ok", "message": "Trading Indicator API is running"}

# Include API routers
app.include_router(analyze_routes.router)
app.include_router(market_data_routes.router)

# Error handlers
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler for unhandled errors"""
    logger.error(f"Unhandled exception: {str(exc)}\n{traceback.format_exc()}")
    return JSONResponse(
        status_code=500,
        content={"detail": f"An unexpected error occurred: {str(exc)}"}
    )

if __name__ == "__main__":
    import uvicorn
    
    # Apply uvicorn patch if needed
    try:
        from uvicorn_patch import patch_uvicorn
        patch_applied = patch_uvicorn()
        if patch_applied:
            logger.info("Applied uvicorn patch for numpy compatibility")
        else:
            logger.warning("Uvicorn patch not applied - may encounter issues with numpy")
    except Exception as e:
        logger.warning(f"Could not apply uvicorn patch: {str(e)}")
    
    # Run the app
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)