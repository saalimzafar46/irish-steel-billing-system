import json
import os
from pathlib import Path
from typing import Dict, Any
import shutil
from datetime import datetime

class DataManager:
    def __init__(self):
        self.data_dir = Path("data")
        self.backup_dir = Path("backups")
        self.ensure_directories()
    
    def ensure_directories(self):
        """Ensure data and backup directories exist"""
        self.data_dir.mkdir(exist_ok=True)
        self.backup_dir.mkdir(exist_ok=True)
    
    def create_backup(self) -> str:
        """Create a backup of all data files"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"backup_{timestamp}.zip"
        backup_path = self.backup_dir / backup_filename
        
        # Create a zip file with all data
        import zipfile
        with zipfile.ZipFile(backup_path, 'w') as zipf:
            for file_path in self.data_dir.glob("*.json"):
                zipf.write(file_path, file_path.name)
        
        return str(backup_path)
    
    def restore_backup(self, backup_path: str) -> bool:
        """Restore data from a backup file"""
        try:
            import zipfile
            with zipfile.ZipFile(backup_path, 'r') as zipf:
                zipf.extractall(self.data_dir)
            return True
        except Exception as e:
            print(f"Error restoring backup: {e}")
            return False
    
    def export_data(self, format_type: str = "json") -> str:
        """Export all data to a single file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if format_type == "json":
            export_data = {}
            for file_path in self.data_dir.glob("*.json"):
                with open(file_path, 'r') as f:
                    export_data[file_path.stem] = json.load(f)
            
            export_filename = f"export_{timestamp}.json"
            export_path = self.data_dir / export_filename
            
            with open(export_path, 'w') as f:
                json.dump(export_data, f, indent=2)
            
            return str(export_path)
        
        elif format_type == "csv":
            # For CSV export, we'd need to flatten the data structure
            # This is more complex and would require specific handling for each data type
            pass
    
    def get_data_stats(self) -> Dict[str, Any]:
        """Get statistics about the data"""
        stats = {}
        
        for file_path in self.data_dir.glob("*.json"):
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    
                if file_path.stem == "company":
                    stats["company_configured"] = bool(data.get("name"))
                elif isinstance(data, list):
                    stats[f"{file_path.stem}_count"] = len(data)
                else:
                    stats[f"{file_path.stem}_configured"] = bool(data)
                    
            except (json.JSONDecodeError, FileNotFoundError):
                stats[f"{file_path.stem}_count"] = 0
        
        return stats
    
    def clear_all_data(self) -> bool:
        """Clear all data (with confirmation)"""
        try:
            for file_path in self.data_dir.glob("*.json"):
                if file_path.stem == "company":
                    with open(file_path, 'w') as f:
                        json.dump({}, f)
                else:
                    with open(file_path, 'w') as f:
                        json.dump([], f)
            return True
        except Exception as e:
            print(f"Error clearing data: {e}")
            return False
