from typing import List, Optional, TypedDict

import yaml


class ConfigDict(TypedDict):
    accounts: List[str]
    max_posts_per_account: Optional[int]
    output_dir: Optional[str]
    period: Optional[str]


def load_config(path) -> ConfigDict:
    with open(path) as f:
        return yaml.safe_load(f)