"""
Routes package for API endpoints
"""
# Import routers for re-export
try:
    from .analyze_routes import router as analyze_router
    from .market_data_routes import router as market_data_router
except ImportError as e:
    # This will be caught during application startup
    import logging
    logging.getLogger(__name__).error(f"Error importing routes: {str(e)}") 