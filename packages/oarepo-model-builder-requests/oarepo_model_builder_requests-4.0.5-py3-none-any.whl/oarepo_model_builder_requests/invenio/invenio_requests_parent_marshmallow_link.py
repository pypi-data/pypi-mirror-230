from oarepo_model_builder.invenio.invenio_base import InvenioBaseClassPythonBuilder


class InvenioRequestsParentMarshmallowLinkBuilder(InvenioBaseClassPythonBuilder):
    TYPE = "invenio_requests_parent_marshmallow_link"
    section = "parent-record-marshmallow"
    template = "requests-parent-marshmallow-link"

    def _get_marshmallow(self):
        return self.current_model.definition["marshmallow"]
    def finish(self, **extra_kwargs):
        # for now the ma schema for parent is generated only when requests are present
        if "draft-parent-record" not in self.current_model.definition or getattr(self.current_model.definition, "requests", None):
            return
        super().finish(marshmallow=self._get_marshmallow(), **extra_kwargs)