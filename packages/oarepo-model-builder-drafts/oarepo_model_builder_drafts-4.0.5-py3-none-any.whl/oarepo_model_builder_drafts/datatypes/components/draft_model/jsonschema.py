from oarepo_model_builder.datatypes.components import JSONSchemaModelComponent
from oarepo_model_builder.datatypes.components.model.utils import set_default

from oarepo_model_builder_drafts.datatypes import DraftDataType


class DraftJSONSchemaModelComponent(JSONSchemaModelComponent):
    eligible_datatypes = [DraftDataType]
    dependency_remap = JSONSchemaModelComponent

    def before_model_prepare(self, datatype, *, context, **kwargs):
        parent_datatype = context["parent_record"].definition

        json_schema = set_default(datatype, "json-schema-settings", {})
        json_schema.setdefault(
            "alias", parent_datatype["json-schema-settings"]["alias"]
        )

        json_schema.setdefault(
            "module",
            parent_datatype["json-schema-settings"]["module"],
        )
        json_schema.setdefault(
            "name",
            parent_datatype["json-schema-settings"]["name"],
        )

        json_schema.setdefault(
            "file",
            parent_datatype["json-schema-settings"]["file"],
        )

        super().before_model_prepare(datatype, context=context, **kwargs)
