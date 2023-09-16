from oarepo_model_builder.builders import OutputBuilder
from oarepo_model_builder.outputs.cfg import CFGOutput


class InvenioDraftsSetupCfgBuilder(OutputBuilder):
    TYPE = "invenio_drafts_setup_cfg"

    def finish(self):
        super().finish()

        output: CFGOutput = self.builder.get_output("cfg", "setup.cfg")

        output.add_dependency("invenio-drafts-resources", ">=1.0.4")
