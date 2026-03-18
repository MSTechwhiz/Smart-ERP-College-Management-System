import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path

def backup_mongodb():
    mongo_url = os.environ.get("MONGO_URL")
    db_name = os.environ.get("DB_NAME", "college_db")
    backup_dir = Path("./backups")
    backup_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    backup_file = backup_dir / f"{db_name}_backup_{timestamp}"
    
    print(f"Starting backup for {db_name}...")
    
    try:
        # Use mongodump for full database backup
        command = [
            "mongodump",
            f"--uri={mongo_url}",
            f"--db={db_name}",
            f"--out={backup_file}"
        ]
        
        subprocess.run(command, check=True)
        print(f"Backup successful: {backup_file}")
        
        # Retention Policy: Delete backups older than 7 days
        retention_days = 7
        now = time.time()
        for b in backup_dir.iterdir():
            if b.is_dir() and (now - b.stat().st_mtime) > (retention_days * 86400):
                print(f"Deleting old backup: {b}")
                import shutil
                shutil.rmtree(b)
                
    except Exception as e:
        print(f"Backup failed: {e}")

if __name__ == "__main__":
    import time
    backup_mongodb()
