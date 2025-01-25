from dataclasses import dataclass, field
from typing import List


@dataclass
class Metadata:
    name: str
    description: str
    author: str
    flow_type: str
    private: bool = False
    tags: List[str] = field(default_factory=list)
    

    def add_tag(self, tag: str):
        """Add a new tag"""
        if tag not in self.tags:
            self.tags.append(tag)
        return self

    def remove_tag(self, tag: str):
        """Remove a tag"""
        if tag in self.tags:
            self.tags.remove(tag)
        return self
