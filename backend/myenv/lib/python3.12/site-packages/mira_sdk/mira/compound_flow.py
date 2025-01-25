from pathlib import Path
from typing import Any, Dict, Optional, Union

from mira_sdk.mira.utils.yaml import load_yaml


class CompoundFlow:
    def __init__(
            self,
            source: Optional[Union[str, Dict[str, Any], Path]] = None
        ):
        self._load_from_source(source)

    def _load_from_source(self, source: Union[str, Dict[str, Any], Path]) -> None:
        if isinstance(source, (str, Path)):
            self.config = load_yaml(Path(source))
        else:
            self.config = source
