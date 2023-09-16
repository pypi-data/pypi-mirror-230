from .invenio_requests_parent_marshmallow import InvenioRequestsParentMarshmallowBuilder


class InvenioRequestsParentMarshmallowUiBuilder(InvenioRequestsParentMarshmallowBuilder):
    TYPE = "invenio_requests_parent_marshmallow_ui"
    def get_marshmallow_module(self):
        return self.current_model.definition["ui"]["marshmallow"]["module"]
