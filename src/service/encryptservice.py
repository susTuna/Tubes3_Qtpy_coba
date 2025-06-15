from ..database.models import SessionLocal, ApplicationDetail, ApplicantProfile
from ..encryption.CAE import CAE
from ..config.config import ENCRYPTION_PASSWORD
import base64
from sqlalchemy import text

class EncryptService:
    def __init__(self):
        self.cae = CAE()
        self.password = ENCRYPTION_PASSWORD
        self.db = None
    
    def is_encrypted(self, text):
        """Check if text is already encrypted"""
        if not text:
            return False
        try:
            decoded = base64.b64decode(text)
            if len(decoded) >= self.cae.salt_bytes:
                return True
        except Exception:
            return False
        return False
    
    def get_db(self):
        """Get database session, creating one if needed"""
        if self.db is None:
            self.db = SessionLocal()
        return self.db
    
    def close_db(self):
        """Close database connection if open"""
        if self.db:
            self.db.close()
            self.db = None
    
    def encrypt_text(self, text):
        """Encrypt a single text value if not already encrypted"""
        if not text or self.is_encrypted(text):
            return text
        return self.cae.encrypt(text, self.password)
    
    def encrypt_batch(self, batch_size=100, progress_callback=None):
        """Encrypt in smaller batches to avoid memory issues"""
        db = self.get_db()
        try:
            encryption_count = 0
            encrypted_count = 0
            
            # Process application details in batches
            total_apps = db.query(ApplicationDetail).count()
            for offset in range(0, total_apps, batch_size):
                applications = db.query(ApplicationDetail).limit(batch_size).offset(offset).all()
                
                for app in applications:
                    if app.cv_path:
                        if not self.is_encrypted(app.cv_path):
                            app.cv_path = self.encrypt_text(app.cv_path)
                            encryption_count += 1
                        else:
                            encrypted_count += 1
                
                db.commit()
                if progress_callback:
                    progress_callback(offset + len(applications), total_apps, 
                                    f"Encrypted {offset + len(applications)}/{total_apps} applications")
            
            # Process applicant profiles in batches
            total_applicants = db.query(ApplicantProfile).count()
            fields_to_encrypt = ['first_name', 'last_name', 'address', 'phone_number']
            
            for offset in range(0, total_applicants, batch_size):
                applicants = db.query(ApplicantProfile).limit(batch_size).offset(offset).all()
                
                for applicant in applicants:
                    for field in fields_to_encrypt:
                        value = getattr(applicant, field, None)
                        if value:
                            if not self.is_encrypted(value):
                                setattr(applicant, field, self.encrypt_text(value))
                                encryption_count += 1
                            else:
                                encrypted_count += 1
                db.execute(text(f"ALTER TABLE ApplicantProfile MODIFY COLUMN {field} TEXT"))
                db.commit()
                if progress_callback:
                    progress_callback(offset + len(applicants), total_applicants, 
                                    f"Encrypted {offset + len(applicants)}/{total_applicants} applicants")
            
            print(f"Encryption completed: {encryption_count} items encrypted, {encrypted_count} items were already encrypted.")
            return encryption_count, encrypted_count
            
        except Exception as e:
            db.rollback()
            print(f"Encryption failed: {str(e)}")
            raise
        finally:
            self.close_db()

    def encrypt(self, progress_callback=None):
        """Legacy method for compatibility"""
        return self.encrypt_batch(progress_callback=progress_callback)

    def decrypt(self, text):
        """Safely decrypt text if it's encrypted"""
        if not text or not self.is_encrypted(text):
            return text
        try:
            return self.cae.decrypt(text, self.password)
        except Exception:
            # Return original if decryption fails
            return text