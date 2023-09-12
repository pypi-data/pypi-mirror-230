from typing import Any, Dict, List, Type, TypeVar, Union, cast

import attr

from ..types import UNSET, Unset

T = TypeVar("T", bound="TemplateIn")


@attr.s(auto_attribs=True)
class TemplateIn:
    """
    Attributes:
        logo (str):
        name (str):
        transformation (str):
        description (Union[Unset, str]):  Default: ''.
        feature_flag (Union[Unset, None, str]):  Example: cool-new-feature.
        filter_types (Union[Unset, None, List[str]]):  Example: ['user.signup', 'user.deleted'].
        instructions (Union[Unset, str]):  Default: ''.
        instructions_link (Union[Unset, None, str]):
    """

    logo: str
    name: str
    transformation: str
    description: Union[Unset, str] = ""
    feature_flag: Union[Unset, None, str] = UNSET
    filter_types: Union[Unset, None, List[str]] = UNSET
    instructions: Union[Unset, str] = ""
    instructions_link: Union[Unset, None, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        logo = self.logo
        name = self.name
        transformation = self.transformation
        description = self.description
        feature_flag = self.feature_flag
        filter_types: Union[Unset, None, List[str]] = UNSET
        if not isinstance(self.filter_types, Unset):
            if self.filter_types is None:
                filter_types = None
            else:
                filter_types = self.filter_types

        instructions = self.instructions
        instructions_link = self.instructions_link

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "logo": logo,
                "name": name,
                "transformation": transformation,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description
        if feature_flag is not UNSET:
            field_dict["featureFlag"] = feature_flag
        if filter_types is not UNSET:
            field_dict["filterTypes"] = filter_types
        if instructions is not UNSET:
            field_dict["instructions"] = instructions
        if instructions_link is not UNSET:
            field_dict["instructionsLink"] = instructions_link

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        logo = d.pop("logo")

        name = d.pop("name")

        transformation = d.pop("transformation")

        description = d.pop("description", UNSET)

        feature_flag = d.pop("featureFlag", UNSET)

        filter_types = cast(List[str], d.pop("filterTypes", UNSET))

        instructions = d.pop("instructions", UNSET)

        instructions_link = d.pop("instructionsLink", UNSET)

        template_in = cls(
            logo=logo,
            name=name,
            transformation=transformation,
            description=description,
            feature_flag=feature_flag,
            filter_types=filter_types,
            instructions=instructions,
            instructions_link=instructions_link,
        )

        template_in.additional_properties = d
        return template_in

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
