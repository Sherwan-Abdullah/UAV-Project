import paramiko
import time
import os

# --- Configuration: Please fill in your details here ---
HOSTNAME = 'put_the_IP'
PORT = 62
USERNAME = 'user_name'
# WARNING: Storing your password in a script is insecure.
PASSWORD = 'password' 

# Define the local and remote file paths for all files
FILE_TRANSFERS = [
    {
        'local': 'lte_log.txt',
        'remote': '/home/s338a494_a/Documents/lte_log.txt'
    },
    {
        'local': 'nping_log.txt',
        'remote': '/home/s338a494_a/Documents/nping_log.txt'
    },
    {
        'local': 'iperf3_log.txt',
        'remote': '/home/s338a494_a/Documents/iperf3_log.txt'
    }
]

# Time interval in seconds between each upload cycle
INTERVAL = 2  # X seconds

# Connection timeout settings
CONNECTION_TIMEOUT = 30
MAX_RETRIES = 3

# Behavior when no files exist: 'continue' or 'stop'
NO_FILES_BEHAVIOR = 'continue'

class PersistentSSHUploader:
    def __init__(self):
        self.ssh_client = None
        self.sftp_client = None
        self.connected = False
    
    def connect(self):
        """Establish SSH/SFTP connection"""
        try:
            if self.ssh_client:
                self.disconnect()
            
            self.ssh_client = paramiko.SSHClient()
            self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            print(f"Connecting to {HOSTNAME}...")
            self.ssh_client.connect(
                hostname=HOSTNAME,
                port=PORT,
                username=USERNAME,
                password=PASSWORD,
                timeout=CONNECTION_TIMEOUT,
                banner_timeout=CONNECTION_TIMEOUT
            )
            
            self.sftp_client = self.ssh_client.open_sftp()
            self.connected = True
            print("✅ Connected successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            self.connected = False
            return False
    
    def disconnect(self):
        """Close SSH/SFTP connection"""
        if self.sftp_client:
            self.sftp_client.close()
            self.sftp_client = None
        if self.ssh_client:
            self.ssh_client.close()
            self.ssh_client = None
        self.connected = False
        print("Connection closed.")
    
    def is_connected(self):
        """Check if connection is still alive"""
        if not self.connected or not self.ssh_client:
            return False
        try:
            # Test connection with a simple command
            self.ssh_client.exec_command('echo test', timeout=5)
            return True
        except:
            self.connected = False
            return False
    
    def upload_files(self):
        """Upload all specified files using existing connection"""
        if not self.is_connected():
            if not self.connect():
                return 0
        
        upload_success = 0
        
        # Check which files exist
        files_to_upload = []
        for file_config in FILE_TRANSFERS:
            if os.path.exists(file_config['local']):
                files_to_upload.append(file_config)
            else:
                print(f"⚠️  WARNING: Local file not found at '{file_config['local']}' - skipping")
        
        if not files_to_upload:
            print("❌ No files available for upload")
            return 0
        
        # Upload each file
        for file_config in files_to_upload:
            local_path = file_config['local']
            remote_path = file_config['remote']
            
            try:
                print(f"Uploading '{local_path}' to '{remote_path}'...")
                
                # Add timeout for file transfer
                start_time = time.time()
                self.sftp_client.put(local_path, remote_path)
                elapsed_time = time.time() - start_time
                
                print(f"✅ {os.path.basename(local_path)} uploaded successfully! ({elapsed_time:.2f}s)")
                upload_success += 1
                
            except Exception as file_error:
                print(f"❌ ERROR uploading {os.path.basename(local_path)}: {file_error}")
                # If upload fails, try to reconnect for next attempt
                self.connected = False
        
        print(f"Upload cycle completed: {upload_success}/{len(FILE_TRANSFERS)} files transferred")
        return upload_success

def main():
    uploader = PersistentSSHUploader()
    
    print("--- Starting Continuous Multi-File Upload with Persistent Connection ---")
    print(f"Upload interval: {INTERVAL} seconds")
    print(f"Connection timeout: {CONNECTION_TIMEOUT} seconds")
    print("-" * 60)
    
    consecutive_failures = 0
    
    try:
        while True:
            start_time = time.time()
            
            files_uploaded = uploader.upload_files()
            
            elapsed_time = time.time() - start_time
            print(f"Upload cycle took {elapsed_time:.2f} seconds")
            
            if files_uploaded == 0:
                consecutive_failures += 1
                if consecutive_failures >= MAX_RETRIES and NO_FILES_BEHAVIOR == 'stop':
                    print(f"Max retries ({MAX_RETRIES}) reached. Exiting.")
                    break
            else:
                consecutive_failures = 0
            
            print(f"Waiting for {INTERVAL} seconds...\n")
            time.sleep(INTERVAL)
            
    except KeyboardInterrupt:
        print("\n🛑 Script stopped by user")
    finally:
        uploader.disconnect()

if __name__ == "__main__":
    main()
