import os

from contentalchemy.images.sync_api.snapper import HTMLSnapper as SyncHTMLSnapper
from contentalchemy.images.async_api.snapper import HTMLSnapper as AsyncHTMLSnapper

headless_url = os.environ.get("CA_HEADLESS_URL", "")
default_html_snapper = SyncHTMLSnapper(browser_endpoint=headless_url)
default_async_html_snapper = AsyncHTMLSnapper(browser_endpoint=headless_url)

__version__ = "0.1.0"
__all__ = [
    "headless_url",
    "default_html_snapper",
    "default_async_html_snapper",
]
