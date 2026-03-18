import os
import re

def get_routes(filepath):
    routes = set()
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        # matches @app.get("/path") or @router.post("/path")
        pattern = r'@(?:app|api_router|router)\.(?:get|post|put|delete|patch)\("([^"]+)"'
        matches = re.findall(pattern, content)
        for m in matches:
            routes.add(m)
    return routes

if __name__ == "__main__":
    server_routes = get_routes("server.py")
    
    app_routes = set()
    routes_dir = os.path.join("app", "routes")
    for filename in os.listdir(routes_dir):
        if filename.endswith(".py"):
            filepath = os.path.join(routes_dir, filename)
            app_routes.update(get_routes(filepath))
            
    print(f"Routes in server.py: {len(server_routes)}")
    print(f"Routes in app/routes: {len(app_routes)}")
    
    missing_in_app = server_routes - app_routes
    if missing_in_app:
        print("\nRoutes in server.py BUT NOT IN app/routes:")
        for r in sorted(missing_in_app):
            print(f"  {r}")
    else:
        print("\nAll routes from server.py are present in app/routes!")
        
    missing_in_server = app_routes - server_routes
    if missing_in_server:
        print("\nNote: There are routes in app/routes that were not in server.py (which is fine).")
