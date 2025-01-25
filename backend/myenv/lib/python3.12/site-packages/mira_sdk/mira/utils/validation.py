from typing import Dict, Any
from ..exceptions import ValidationError
from ..models.input import Input


def validate_prompt_variables(prompt: str, inputs: Dict[str, Input]) -> None:
    """Validate that all required input variables are used in the prompt"""
    input_vars = set(inputs.keys())
    prompt_vars = {
        var.strip('{}') for var in prompt.split('{')[1:]
        if '}' in var
    }

    missing_vars = set(
        name for name, input in inputs.items()
        if input.required and name not in prompt_vars
    )

    if missing_vars:
        raise ValidationError(
            f"Required input variables {missing_vars} are not used in the prompt template"
        )
