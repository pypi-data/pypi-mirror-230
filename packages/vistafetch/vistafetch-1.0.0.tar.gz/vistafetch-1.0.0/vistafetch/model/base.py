"""Basic model definitions.

These are not defined to are used directly but to server for further modelling.

"""
from typing import Any, Dict

from pydantic import BaseModel, ConfigDict

__all__ = [
    "VistaEntity",
]


def _snake_to_camel_case(snake_case_string: str) -> str:
    """Convert a string in snake_case format to camelCase style.

    Args:
    ----
    snake_case_string: str
        string in snake_case format

    Returns:
    -------
    str

    """
    tokens = snake_case_string.split("_")

    return tokens[0] + "".join(t.title() for t in tokens[1:])


class VistaEntity(BaseModel):
    """Basic vista entity representation.

    This class serves as a common base class for several model classes of this library.

    Attributes
    ----------
        model_config: ConfigDict
            Config object to specify the behavior of the model class.
            Read more at [Pydantic's docs](https://docs.pydantic.dev/latest/usage/model_config/).

    """

    model_config = ConfigDict(alias_generator=_snake_to_camel_case, extra="allow")

    def as_json(self) -> str:
        """Return the entity as JSON string.

        This method returns the attributes of the entity data model as JSON string.
        It excludes additional parameters that are returned by the API but not modelled.
        Use `extra()` to get access to additional price-related data.

        Returns
        -------
            model_json: The model instance represented as JSON string
        """
        # By default, Pydantic includes additional parameters as well in the JSON dump
        # https://github.com/pydantic/pydantic/issues/6150
        # Therefore, we need to exclude them by hand
        return self.model_dump_json(
            exclude=set(self.model_extra.keys() if self.model_extra else [])
        )

    @property
    def extra(self) -> Dict[str, Any]:
        """Additional data returned by the API but not covered by this model.

        Extra data is exactly as returned by the API,
        no modifications are applied.

        Returns
        -------
            extra: dictionary containing additional data.
        """
        return self.model_extra if self.model_extra else {}
