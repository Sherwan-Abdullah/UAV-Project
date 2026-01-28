import paramiko
import time
import os

# --- Configuration: Details for the REMOTE server you are fetching FROM ---
HOSTNAME = 'the _IP_of the _server'
PORT = 62
USERNAME = 'user_name'
PASSWORD = 'password' 

# Define the paths: 'remote' is the source (on server), 'local' is the destination (on the Jetson)
FILE_TRANSFERS = [
    {
        'remote': '/home/s338a494_a/Documents/lte_log.txt',
        'local': 'lte_log.txt'
    },
    {
        'remote': '/home/s338a494_a/Documents/nping_log.txt',
        'local': 'nping_log.txt'
    },
    {
        'remote': '/home/s338a494_a/Documents/iperf3_log.txt',
        'local': 'iperf3_log.txt'
    }
]

INTERVAL = 2  
CONNECTION_TIMEOUT = 30
MAX_RETRIES = 3

class PersistentSSHFetcher:
    def __init__(self):
        self.ssh_client = None
        self.sftp_client = None
        self.connected = False
    
    def connect(self):
        try:
            if self.ssh_client:
                self.disconnect()
            
            self.ssh_client = paramiko.SSHClient()
            self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            print(f"Connecting to {HOSTNAME} to fetch files...")
            self.ssh_client.connect(
                hostname=HOSTNAME,
                port=PORT,
                username=USERNAME,
                password=PASSWORD,
                timeout=CONNECTION_TIMEOUT
            )
            
            self.sftp_client = self.ssh_client.open_sftp()
            self.connected = True
            print("✅ Connected and ready to download!")
            return True
            
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            self.connected = False
            return False
    
    def disconnect(self):
        if self.sftp_client: self.sftp_client.close()
        if self.ssh_client: self.ssh_client.close()
        self.connected = False
        print("Connection closed.")

    def remote_file_exists(self, path):
        """Check if the file exists on the server"""
        try:
            self.sftp_client.stat(path)
            return True
        except FileNotFoundError:
            return False

    def fetch_files(self):
        """Download all specified files from server to local machine"""
        if not self.connected:
            if not self.connect():
                return 0
        
        fetch_success = 0
        
        for file_config in FILE_TRANSFERS:
            remote_path = file_config['remote']
            local_path = file_config['local']
            
            if self.remote_file_exists(remote_path):
                try:
                    print(f"Fetching '{os.path.basename(remote_path)}'...")
                    
                    # Changed from .put() to .get()
                    self.sftp_client.get(remote_path, local_path)
                    
                    print(f"✅ Saved to {local_path}")
                    fetch_success += 1
                except Exception as e:
                    print(f"❌ ERROR fetching {remote_path}: {e}")
                    self.connected = False
            else:
                print(f"⚠️  WARNING: Remote file not found: {remote_path}")
        
        return fetch_success

def main():
    fetcher = PersistentSSHFetcher()
    print("--- Starting Continuous Multi-File Fetch (Server -> Client) ---")
    
    try:
        while True:
            files_retrieved = fetcher.fetch_files()
            print(f"Cycle complete. {files_retrieved} files updated. Waiting {INTERVAL}s...\n")
            time.sleep(INTERVAL)
    except KeyboardInterrupt:
        print("\n🛑 Stopped by user")
    finally:
        fetcher.disconnect()

if __name__ == "__main__":
    main()