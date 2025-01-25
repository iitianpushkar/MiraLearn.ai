from pathlib import Path
from typing import Dict, Optional, Union, Any

from .exceptions import FlowError, ValidationError, LoadError
from .models.input import Input
from .models.metadata import Metadata
from .models.model import Model
from .utils.yaml import load_yaml, save_yaml
from .utils.validation import validate_prompt_variables


class Flow:
    """
    A developer-friendly class for managing AI flow configurations.
    Supports intuitive creation, modification, and saving of flows.

    Examples:
        >>> # Create a new flow
        >>> flow = Flow("story-generator")
        >>> flow.add_input("character", "Main character")
        >>> flow.set_model("tric", "llama")

        >>> # Load existing flow
        >>> flow = Flow(source="path/to/flow.yaml")
        >>> flow.metadata.add_tag("creative")
        >>> flow.save("updated_flow.yaml")
    """

    def __init__(
            self,
            name: Optional[str] = None,
            source: Optional[Union[str, Dict[str, Any], Path]] = None
    ):
        """
        Initialize a Flow instance.

        Args:
            name: Optional name for new flow
            source: Optional source to load from (file path or dict)

        Raises:
            LoadError: If source cannot be loaded
        """
        if source:
            self._load_from_source(source)
        else:
            self._init_empty(name or "unnamed-flow")

    def _init_empty(self, name: str) -> None:
        """Initialize an empty flow with default values"""
        self.version = "1.0.0"
        self.metadata = Metadata(
            name=name,
            description="",
            author="",
            tags=[],
            flow_type="primitive"
        )
        self.inputs: Dict[str, Input] = {}
        self.output_type = "string"
        self.model = Model.tric()
        self.dataset_source = None
        self.prompt = ""
        self.readme = ""

    def _load_from_source(self, source: Union[str, Dict[str, Any], Path]) -> None:
        """
        Load flow configuration from source.

        Args:
            source: File path, dictionary, or Path object

        Raises:
            LoadError: If source cannot be loaded or is invalid
        """
        try:
            if isinstance(source, (str, Path)):
                config = load_yaml(Path(source))
            else:
                config = source

            # Load version
            self.version = config.get('version', '1.0.0')

            # Load metadata
            meta = config.get('metadata', {})
            self.metadata = Metadata(
                name=meta.get('name', 'unnamed-flow'),
                description=meta.get('description', ''),
                author=meta.get('author', ''),
                private=meta.get('private', False),
                tags=meta.get('tags', []),
                flow_type=meta.get('flow_type', 'primitive')
            )

            # Load inputs
            self.inputs = {
                name: Input(**spec)
                for name, spec in config.get('inputs', {}).items()
            }

            # Load output configuration
            output_config = config.get('output', {})
            self.output_type = output_config.get('type', 'string')

            # Load model configuration
            model_config = config.get('model', {})
            self.model = Model(
                provider=model_config.get('provider', 'tric'),
                name=model_config.get('name', 'llama')
            )

            # Load dataset configuration
            dataset = config.get('dataset', {})
            self.dataset_source = dataset.get('source') if dataset else None

            # Load prompt
            self.prompt = config.get('prompt', '')

            # Load readme
            self.readme = config.get('readme', '')

        except Exception as e:
            raise LoadError(f"Failed to load flow configuration: {str(e)}")

    def add_input(
            self,
            name: str,
            description: str,
            type: str = "string",
            required: bool = True,
            example: Optional[str] = None
    ) -> 'Flow':
        """
        Add a new input parameter to the flow.

        Args:
            name: Name of the input parameter
            description: Description of the input
            type: Input type (default: "string")
            required: Whether input is required (default: True)
            example: Optional example value

        Returns:
            self for method chaining
        """
        self.inputs[name] = Input(
            type=type,
            description=description,
            required=required,
            example=example
        )
        return self

    def remove_input(self, name: str) -> 'Flow':
        """Remove an input parameter"""
        self.inputs.pop(name, None)
        return self

    def set_prompt(self, prompt: str) -> 'Flow':
        """
        Set the prompt template.

        Args:
            prompt: Prompt template string with {variable} placeholders

        Returns:
            self for method chaining
        """
        self.prompt = prompt
        return self

    def set_model(self, provider: str, name: str) -> 'Flow':
        """
        Set the model configuration.

        Args:
            provider: Model provider (e.g., "tric", "anthropic")
            name: Model name

        Returns:
            self for method chaining
        """
        self.model = Model(provider=provider, name=name)
        return self

    def set_dataset(self, source: str) -> 'Flow':
        """
        Set the dataset source.

        Args:
            source: dataset source identifier

        Returns:
            self for method chaining
        """
        self.dataset_source = source
        return self

    def validate(self) -> bool:
        """
        Validate the flow configuration.

        Returns:
            True if validation passes

        Raises:
            ValidationError: If validation fails
        """
        try:
            # Validate prompt variables
            validate_prompt_variables(self.prompt, self.inputs)

            # Validate required fields
            if not self.metadata.name:
                raise ValidationError("Flow name is required")

            if not self.prompt:
                raise ValidationError("Prompt template is required")

            return True

        except Exception as e:
            raise ValidationError(f"Flow validation failed: {str(e)}")

    def render_prompt(self, **kwargs: str) -> str:
        """
        Render the prompt template with provided variables.

        Args:
            **kwargs: Variable values for the prompt template

        Returns:
            str: Rendered prompt

        Raises:
            ValidationError: If required variables are missing
        """
        # Validate input variables
        required_vars = {
            name for name, spec in self.inputs.items()
            if spec.required
        }
        provided_vars = set(kwargs.keys())
        missing_vars = required_vars - provided_vars

        if missing_vars:
            raise ValidationError(f"Missing required variables: {missing_vars}")

        try:
            return self.prompt.format(**kwargs)
        except KeyError as e:
            raise ValidationError(f"Invalid variable in prompt template: {e}")

    def to_dict(self) -> Dict[str, Any]:
        """Convert flow to dictionary format"""
        config = {
            'version': self.version,
            'metadata': {
                'name': self.metadata.name,
                'description': self.metadata.description,
                'author': self.metadata.author,
                'private': self.metadata.private,
                'tags': self.metadata.tags
            },
            'inputs': {
                name: {
                    'type': input.type,
                    'description': input.description,
                    'required': input.required,
                    'example': input.example
                }
                for name, input in self.inputs.items()
            },
            'output': {
                'name': 'story',
                'type': self.output_type
            },
            'model': {
                'provider': self.model.provider,
                'name': self.model.name
            },
            'prompt': self.prompt,
            'readme': self.readme
        }

        # Add optional dataset configuration
        if self.dataset_source:
            config['dataset'] = {'source': self.dataset_source}

        return config

    def save(self, path: Union[str, Path]) -> None:
        """
        Save flow to YAML file.

        Args:
            path: Path to save the YAML file

        Raises:
            LoadError: If saving fails
        """
        save_yaml(self.to_dict(), Path(path))

    def describe(self) -> str:
        """
        Get a human-readable description of the flow.

        Returns:
            str: Formatted description of the flow configuration
        """
        parts = [
            f"Flow: {self.metadata.name}",
            f"Description: {self.metadata.description}",
            f"Author: {self.metadata.author}",
            f"Tags: {', '.join(self.metadata.tags)}",
            "\nInputs:",
        ]

        for name, input_spec in self.inputs.items():
            required = "(required)" if input_spec.required else "(optional)"
            example = f" (example: {input_spec.example})" if input_spec.example else ""
            parts.append(f"  - {name} {required}: {input_spec.description}{example}")

        parts.extend([
            f"\nModel: {self.model.provider}/{self.model.name}",
            f"Dataset source: {self.dataset_source or 'None'}",
            "\nPrompt:",
            self.prompt,
            "\nReadme:",
            self.readme
        ])

        return "\n".join(parts)

    def clone(self, author, flow_name) -> 'Flow':
        """Create a deep copy of the flow"""
        new_flow = Flow()
        new_flow._load_from_source(self.to_dict())
        return new_flow
