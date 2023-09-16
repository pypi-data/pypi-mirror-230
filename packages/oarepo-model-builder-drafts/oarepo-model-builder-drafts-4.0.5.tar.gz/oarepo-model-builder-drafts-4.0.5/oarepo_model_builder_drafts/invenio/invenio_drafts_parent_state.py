from oarepo_model_builder.invenio.invenio_base import InvenioBaseClassPythonBuilder


class InvenioDraftsParentStateBuilder(InvenioBaseClassPythonBuilder):
    TYPE = "invenio_drafts_parent_state"
    section = "draft-parent-record-state"
    template = "drafts-parent-state"

    def finish(self, **extra_kwargs):
        super().finish(parent_record=self.current_model.parent_record, **extra_kwargs)
