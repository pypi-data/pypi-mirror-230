from .invenio_requests_parent_marshmallow_link import InvenioRequestsParentMarshmallowLinkBuilder


class InvenioRequestsParentMarshmallowLinkUiBuilder(InvenioRequestsParentMarshmallowLinkBuilder):
    TYPE = "invenio_requests_parent_marshmallow_link_ui"
    def _get_output_module(self):
        return self.current_model.definition["ui"]["marshmallow"]["module"]
    def _get_marshmallow(self):
        return self.current_model.definition["ui"]["marshmallow"]
