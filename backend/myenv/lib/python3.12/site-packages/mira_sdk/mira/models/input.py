from dataclasses import dataclass
from typing import Optional


@dataclass
class Input:
    type: str
    description: str
    required: bool = True
    example: Optional[str] = None

    def make_optional(self):
        """Make this input optional"""
        self.required = False
        return self

    def set_example(self, example: str):
        """Set an example value"""
        self.example = example
        return self
