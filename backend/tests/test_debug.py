import sys
import os

def test_debug_path(client):
    print(f"\nCWD: {os.getcwd()}")
    print(f"File: {__file__}")
    print(f"Path: {sys.path}")
    
    from app.core.database import get_db
    from app.main import app
    
    override = app.dependency_overrides.get(get_db)
    print(f"Override for get_db: {override}")
    assert override is not None
    assert True
