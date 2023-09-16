from oarepo_model_builder.datatypes import DataTypeComponent, datatypes, ModelDataType
from oarepo_model_builder.datatypes.components import MappingModelComponent, DefaultsModelComponent, \
    RecordModelComponent, JSONSchemaModelComponent

import copy

class DraftMappingModelComponent(MappingModelComponent):
    eligible_datatypes = [ModelDataType]
    depends_on = [
        DefaultsModelComponent,
        RecordModelComponent,
        JSONSchemaModelComponent,
    ]
    dependency_remap = MappingModelComponent

    def process_mapping(self, datatype, section, **kwargs):
        if self.is_draft_profile:
            section.children["expires_at"] = datatypes.get_datatype(
                datatype,
                {
                    "type": "datetime",
                    "sample": {"skip": True},
                    "marshmallow": {"read": False, "write": False},
                    "ui": {"marshmallow": {"read": False, "write": False}},
                },
                "expires_at",
                datatype.model,
                datatype.schema,
            )
            section.children["expires_at"].prepare(context={})
            section.children["fork_version_id"] = datatypes.get_datatype(
                datatype,
                {
                    "type": "integer",
                    "sample": {"skip": True},
                    "marshmallow": {"read": False, "write": False},
                    "ui": {"marshmallow": {"read": False, "write": False}},
                },
                "fork_version_id",
                datatype.model,
                datatype.schema,
            )
            section.children["fork_version_id"].prepare(context={})

    def before_model_prepare(self, datatype, *, context, **kwargs):
        self.is_draft_profile = context["profile"] == "draft"
        if context["profile"] == "record" and "mapping" in datatype.definition:
            self.mapping_default = copy.deepcopy(datatype.definition["mapping"])

        if self.is_draft_profile and hasattr(self, "mapping_default"): #in case the draft profile is ran before record profile, it should be on parent record that is before before_model_prepare is called?
            mapping = datatype.definition.get("mapping", {}) | self.mapping_default
            datatype.definition["mapping"] = mapping

        super().before_model_prepare(datatype, context=context, **kwargs)
