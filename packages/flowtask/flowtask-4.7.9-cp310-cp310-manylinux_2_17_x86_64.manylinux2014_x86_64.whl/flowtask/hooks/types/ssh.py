import time
import paramiko
from navconfig.logging import logging
from .watch import BaseWatchdog, BaseWatcher


logging.getLogger('paramiko').setLevel(logging.WARNING)


class SFTPWatcher(BaseWatcher):
    def __init__(
        self,
        host: str,
        port: int,
        username: str,
        password: str,
        path: str,
        interval=300,
        **kwargs
    ):
        super(SFTPWatcher, self).__init__(**kwargs)
        self.host = host
        self.port = port
        self.user = username
        self.password = password
        self.interval = interval
        self.path = path

    def close_watcher(self):
        pass

    def run(self):
        while not self.stop_event.is_set():
            try:
                # Connect to the SSH server
                ssh_client = paramiko.SSHClient()
                ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh_client.connect(
                    self.host,
                    port=self.port,
                    username=self.user,
                    password=self.password
                )
                # Connect to the SFTP server
                sftp_client = ssh_client.open_sftp()
                # Check if the file or directory exists
                try:
                    stat = sftp_client.stat(self.path)
                    print(f"Found {self.path} on {self.host}:")
                    print(f"  - Size: {stat.st_size} bytes")
                    print(f"  - Permissions: {oct(stat.st_mode)}")
                    print(f"  - Last modified: {time.ctime(stat.st_mtime)}")
                except FileNotFoundError:
                    print(
                        f"{self.path} not found on {self.host}"
                    )
                # Disconnect
                sftp_client.close()
                ssh_client.close()
            except Exception as e:
                print(
                    f"An error occurred while checking the server: {e}"
                )
                continue

            # Wait for the interval, but check the stop_event every second
            for _ in range(self.interval):
                if self.stop_event.is_set():
                    break
                time.sleep(1)

class SFTPWatchdog(BaseWatchdog):

    def create_watcher(self, *args, **kwargs) -> BaseWatcher:
        credentials = kwargs.pop('credentials', {})
        path = kwargs.pop('path', None)
        interval = kwargs.pop('interval', 300)
        self.credentials = self.set_credentials(credentials)
        return SFTPWatcher(
            **self.credentials,
            path=path,
            interval=interval
        )
