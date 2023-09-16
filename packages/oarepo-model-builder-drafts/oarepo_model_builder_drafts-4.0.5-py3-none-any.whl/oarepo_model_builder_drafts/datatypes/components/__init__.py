from .draft import DraftComponent
from .draft_model import (
    DraftDefaultsModelComponent,
    DraftJSONSchemaModelComponent,
    DraftMappingModelComponent,
    DraftParentComponent,
    DraftPIDModelComponent,
    DraftRecordMetadataModelComponent,
    DraftRecordModelComponent,
    DraftResourceModelComponent,
    DraftServiceModelComponent,
)
from .draft_tests import DraftModelTestComponent

DRAFT_COMPONENTS = [
    DraftParentComponent,
    DraftComponent,
    DraftRecordModelComponent,
    DraftRecordMetadataModelComponent,
    DraftPIDModelComponent,
    DraftDefaultsModelComponent,
    DraftJSONSchemaModelComponent,
    DraftModelTestComponent,
    DraftMappingModelComponent,
    DraftResourceModelComponent,
    DraftServiceModelComponent,
]
