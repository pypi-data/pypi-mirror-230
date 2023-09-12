from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar

import attr

if TYPE_CHECKING:
    from ..models.event_type_import_open_api_in_spec import EventTypeImportOpenApiInSpec


T = TypeVar("T", bound="EventTypeImportOpenApiIn")


@attr.s(auto_attribs=True)
class EventTypeImportOpenApiIn:
    """
    Attributes:
        spec (EventTypeImportOpenApiInSpec):  Example: {'components': {'schemas': {'Pet': {'properties': {'id':
            {'format': 'int64', 'type': 'integer'}, 'name': {'type': 'string'}, 'tag': {'type': 'string'}}, 'required':
            ['id', 'name']}}}, 'info': {'title': 'Webhook Example', 'version': '1.0.0'}, 'openapi': '3.1.0', 'webhooks':
            {'pet.new': {'post': {'requestBody': {'content': {'application/json': {'schema': {'$ref':
            '#/components/schemas/Pet'}}}, 'description': 'Information about a new pet in the system'}, 'responses': {'200':
            {'description': 'Return a 200 status to indicate that the data was received successfully'}}}}}}.
    """

    spec: "EventTypeImportOpenApiInSpec"
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        spec = self.spec

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "spec": spec,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        spec = d.pop("spec")

        event_type_import_open_api_in = cls(
            spec=spec,
        )

        event_type_import_open_api_in.additional_properties = d
        return event_type_import_open_api_in

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
