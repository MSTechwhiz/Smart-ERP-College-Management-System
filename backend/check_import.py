import sys
import os
sys.path.insert(0, os.getcwd())
try:
    from app.main import app
    print("Import successful!")
    print(f"App routes: {[r.path for r in app.routes if hasattr(r, 'path')]}")
except Exception as e:
    print(f"Import failed: {e}")
    import traceback
    traceback.print_exc()
