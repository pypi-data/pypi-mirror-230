"""
Types.

Many types of Hooks Services.
"""
from .base import BaseHook
from .fs import FSWatchdog
from .web import WebHook
from .upload import UploadHook
from .imap import IMAPWatchdog

__all__ = (
    'BaseHook',
    'FSWatchdog',
    'WebHook',
    'UploadHook',
    'IMAPWatchdog',
)
