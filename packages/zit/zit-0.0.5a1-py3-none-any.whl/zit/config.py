import logging
import os
from pathlib import Path

from rich.logging import RichHandler

ZITRC_FILE = Path(os.path.expanduser("~/.zitrc"))
REGISTRY_ENDPOINT = "https://www.api.zityspace.cn/registry"
WS_FORMULA_PUBLISH_ENDPOINT = "wss://www.api.zityspace.cn/registry/formula/publish"
WS_FORMULA_INSTALL_ENDPOINT = "wss://www.api.zityspace.cn/registry/formula/install"
AUTH_PUBLIC_ENDPOINT = "https://www.api.zityspace.cn/auth/public"


logging.basicConfig(level="INFO", format="%(message)s", handlers=[RichHandler(rich_tracebacks=True)])
logger = logging.getLogger(__name__)

logging.getLogger("httpx").setLevel(logging.WARNING)
