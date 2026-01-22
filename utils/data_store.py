import json
import os
from datetime import datetime
from pathlib import Path
from utils.logger import get_logger

logger = get_logger(__name__)

class DataStore:
    """Manage persistent storage with backup support"""
    
    def __init__(self, data_file='storage/data.json'):
        self.data_file = Path(data_file)
        self.backup_dir = self.data_file.parent / 'backup'
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.data_file.parent.mkdir(parents=True, exist_ok=True)
        
    def load(self):
        """Load data from file"""
        try:
            if self.data_file.exists():
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    logger.info(f"Loaded data from {self.data_file}")
                    return data
            else:
                logger.warning(f"Data file not found: {self.data_file}, creating new")
                return {"layers": []}
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            # Try to restore from backup
            return self._restore_from_backup()
    
    def save(self, data):
        """Save data to file with backup"""
        try:
            # Create backup before saving
            if self.data_file.exists():
                self._create_backup()
            
            # Save data
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved data to {self.data_file}")
        except Exception as e:
            logger.error(f"Error saving data: {e}")
            raise
    
    def _create_backup(self):
        """Create a timestamped backup"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_file = self.backup_dir / f"data_backup_{timestamp}.json"
            
            with open(self.data_file, 'r', encoding='utf-8') as src:
                with open(backup_file, 'w', encoding='utf-8') as dst:
                    dst.write(src.read())
            
            logger.debug(f"Created backup: {backup_file}")
            
            # Keep only last 10 backups
            self._cleanup_old_backups(keep=10)
        except Exception as e:
            logger.warning(f"Failed to create backup: {e}")
    
    def _cleanup_old_backups(self, keep=10):
        """Remove old backup files"""
        try:
            backups = sorted(self.backup_dir.glob('data_backup_*.json'), reverse=True)
            for old_backup in backups[keep:]:
                old_backup.unlink()
                logger.debug(f"Removed old backup: {old_backup}")
        except Exception as e:
            logger.warning(f"Error cleaning up backups: {e}")
    
    def _restore_from_backup(self):
        """Restore from most recent backup"""
        try:
            backups = sorted(self.backup_dir.glob('data_backup_*.json'), reverse=True)
            if backups:
                backup_file = backups[0]
                with open(backup_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                logger.warning(f"Restored data from backup: {backup_file}")
                return data
            else:
                logger.error("No backup files found")
                return {"layers": []}
        except Exception as e:
            logger.error(f"Error restoring from backup: {e}")
            return {"layers": []}
