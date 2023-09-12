from enum import Enum


class TransformationTemplateKind(str, Enum):
    CUSTOM = "Custom"

    def __str__(self) -> str:
        return str(self.value)
