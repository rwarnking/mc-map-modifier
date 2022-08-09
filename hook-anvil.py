# https://github.com/vaexio/vaex/issues/1823
from pathlib import Path

import anvil

datas = [(Path(anvil.__path__[0]) / "legacy_blocks.json", "anvil")]
