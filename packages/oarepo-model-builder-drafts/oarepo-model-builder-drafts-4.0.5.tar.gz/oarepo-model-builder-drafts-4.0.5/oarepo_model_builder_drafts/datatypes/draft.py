import marshmallow as ma
from oarepo_model_builder.datatypes import ModelDataType


class DraftDataType(ModelDataType):
    model_type = "draft_record"

    class ModelSchema(ModelDataType.ModelSchema):
        type = ma.fields.Str(
            load_default="draft_record",
            required=False,
            validate=ma.validate.Equal("draft_record"),
        )

    def prepare(self, context):
        self.parent_record = context["parent_record"]
        super().prepare(context)
