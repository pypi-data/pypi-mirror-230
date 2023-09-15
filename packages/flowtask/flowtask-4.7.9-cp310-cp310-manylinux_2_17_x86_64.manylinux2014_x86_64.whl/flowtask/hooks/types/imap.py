from typing import Union, Optional
import imaplib
import threading
import time
from functools import partial
import ssl
from flowtask.exceptions import ComponentError
from flowtask.components.azureauth import AzureAuth
from .watch import BaseWatchdog, BaseWatcher


class ImapWatcher(BaseWatcher):
    def __init__(
        self,
        host: str,
        port: int,
        user: str,
        password: str,
        mailbox='INBOX',
        use_ssl: bool = True,
        interval=60,
        authmech: str = None,
        search: Optional[Union[str, dict, list]] = None,
        **kwargs
    ):
        super(ImapWatcher, self).__init__(**kwargs)
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.mailbox = mailbox
        self.interval = interval
        self.authmech = authmech
        self.use_ssl = use_ssl
        self.search = search

    def close_watcher(self):
        self.imap_server.logout()

    def connect(self):
        if self.use_ssl is True:
            sslcontext = ssl.create_default_context()
            server = partial(
                imaplib.IMAP4_SSL,
                self.host,
                self.port,
                timeout=10,
                ssl_context=sslcontext
            )
        else:
            server = partial(
                imaplib.IMAP4,
                self.host,
                self.port,
                timeout=10
            )
        try:
            self.imap_server = server()
            if self.authmech is not None:
                try:
                    azure = AzureAuth()  # default values
                    result, msg = self.imap_server.authenticate(
                        self.authmech,
                        lambda x: azure.binary_token(
                            self.user, self.password
                        )
                    )
                    if result != 'OK':
                        raise ComponentError(
                            f'IMAP: Wrong response: {result} message={msg}'
                        )
                except AttributeError as err:
                    raise ComponentError(
                        f'Login Forbidden, wrong username or password: {err}'
                    ) from err
            else:
                ## making the server login:
                r = self.imap_server.login(self.user, self.password)
                if r.result == 'NO':
                    raise ComponentError(
                        f'Login Forbidden, Server Disconnected: {r}'
                    )
            ### Select Mailbox
            self.imap_server.select(self.mailbox)
        except Exception as exc:
            raise ComponentError(
                f"Could not connect to IMAP Server {self.host}:{self.port}: {exc}"
            ) from exc

    def run(self):
        self.connect()
        while not self.stop_event.is_set():
            try:
                result, data = self.imap_server.search(None, 'UNSEEN')
                if result == 'OK':
                    unseen_emails = len(data[0].split())
                    print(
                        f"Found {unseen_emails} unseen emails in {self.mailbox}"
                    )
                    self.parent.call_actions()
            except Exception as e:
                print(f"An error occurred while checking the mailbox: {e}")
                # Reconnect if an error occurs
                self.connect()
            # Wait for the interval, but allow the sleep to be interrupted by the signal
            try:
                for _ in range(self.interval):
                    if self.stop_event.is_set():
                        break
                    time.sleep(1)
            except KeyboardInterrupt:
                break


class IMAPWatchdog(BaseWatchdog):

    def create_watcher(self, *args, **kwargs) -> BaseWatcher:
        credentials = kwargs.pop('credentials', {})
        self.mailbox = kwargs.pop('mailbox', 'INBOX')
        interval = kwargs.pop('interval', 60)
        authmech = credentials.pop('authmech', None)
        search = kwargs.pop('search', None)
        self.credentials = self.set_credentials(credentials)
        return ImapWatcher(
            **self.credentials,
            mailbox=self.mailbox,
            interval=interval,
            authmech=authmech,
            search=search,
            **kwargs
        )
