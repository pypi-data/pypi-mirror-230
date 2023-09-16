import marshmallow as ma
from oarepo_model_builder.datatypes import DataTypeComponent, ModelDataType
from oarepo_model_builder.datatypes.components import DefaultsModelComponent, MarshmallowModelComponent
from oarepo_model_builder.datatypes.components.model.utils import set_default, append_array
from oarepo_model_builder.utils.camelcase import camel_case, snake_case
from oarepo_model_builder.validation.utils import ImportSchema


class RequestActionSchema(ma.Schema):
    class Meta:
        unknown = ma.RAISE

    module = ma.fields.String(metadata={"doc": "Class module"})
    class_ = ma.fields.String(
        attribute="class",
        data_key="class",
    )
    generate = ma.fields.Bool()
    base_classes = ma.fields.List(
        ma.fields.Str(),
        attribute="base-classes",
        data_key="base-classes",
        metadata={"doc": "Request action base classes"},
    )
    # module = ma.fields.String(metadata={"doc": "Class module"})
    imports = ma.fields.List(
        ma.fields.Nested(ImportSchema), metadata={"doc": "List of python imports"}
    )


class RequestTypeSchema(ma.Schema):
    class Meta:
        unknown = ma.RAISE

    module = ma.fields.String(metadata={"doc": "Class module"})
    class_ = ma.fields.String(
        attribute="class",
        data_key="class",
    )
    generate = ma.fields.Bool()
    base_classes = ma.fields.List(
        ma.fields.Str(),
        attribute="base-classes",
        data_key="base-classes",
        metadata={"doc": "RequestType base classes"},
    )
    parent_actions = ma.fields.String(
        attribute="parent-actions", data_key="parent-actions"
    )
    imports = ma.fields.List(
        ma.fields.Nested(ImportSchema), metadata={"doc": "List of python imports"}
    )
    id_ = ma.fields.String(
        attribute="id", data_key="id"
    )
class ParentMarshmallowSchema(ma.Schema):
    module = ma.fields.String(metadata={"doc": "Class module"})
    class_ = ma.fields.String(
        attribute="class",
        data_key="class",
    )
    generate = ma.fields.Bool()
    base_classes = ma.fields.List(
        ma.fields.Str(),
        attribute="base-classes",
        data_key="base-classes",
        metadata={"doc": "base classes"},
    )
    imports = ma.fields.List(
        ma.fields.Nested(ImportSchema), metadata={"doc": "List of python imports"}
    )

class ParentMarshmallowRequestSchema(ma.Schema):
    parent_field = ma.fields.String(data_key="parent-field", attribute="parent-field")
    schema_class = ma.fields.String(data_key="schema-class", attribute="schema-class")
    imports = ma.fields.List(
        ma.fields.Nested(ImportSchema), metadata={"doc": "List of python imports"}
    )
    module = ma.fields.String(metadata={"doc": "Class module"})
    generate = ma.fields.Bool()




class RequestSchema(ma.Schema):
    module = ma.fields.String(metadata={"doc": "Class module"})
    type = ma.fields.Nested(RequestTypeSchema)
    actions = ma.fields.Dict(
        keys=ma.fields.Str(), values=ma.fields.Nested(RequestActionSchema)
    )
    parent_schema = ma.fields.Nested(ParentMarshmallowRequestSchema, data_key="parent-marshmallow", attribute="parent-marshmallow")





class RequestsComponent(DataTypeComponent):
    eligible_datatypes = [ModelDataType]
    depends_on = [DefaultsModelComponent, MarshmallowModelComponent]

    class ModelSchema(ma.Schema):
        requests = ma.fields.Dict(
            keys=ma.fields.Str(),
            values=ma.fields.Nested(RequestSchema),
            attribute="requests",
            data_key="requests",
        )

    def before_model_prepare(self, datatype, *, context, **kwargs):
        module = datatype.definition["module"]["qualified"]
        profile_module = context["profile_module"]

        requests = set_default(datatype, "requests", {})

        for request_name, request_input_data in requests.items():
            request_module = f"{module}.{profile_module}.requests.{snake_case(request_name).replace('-', '_')}"

            # type
            request_type = request_input_data.setdefault("type", {})
            request_type_module = request_type.setdefault(
                "module", f"{request_module}.types"
            )
            request_type.setdefault(
                "class",
                f"{request_type_module}.{camel_case(request_name)}RequestType",
            )
            request_type.setdefault("generate", True)
            request_type.setdefault("base-classes", ["RequestType"])  # accept action
            request_type.setdefault(
                "imports",
                [
                    {
                        "import": "invenio_requests.customizations.RequestType",
                    },
                ],
            )
            request_type.setdefault(
                "parent-actions",
                f"**{request_type['base-classes'][0]}.available_actions",
            )
            request_type.setdefault(
                "id", snake_case(request_name).replace("-","_")
            )

            # parent schema
            marshmallow = request_input_data.setdefault("parent-marshmallow", {})
            marshmallow.setdefault("parent-field", snake_case(request_name).replace("-", "_"))
            marshmallow.setdefault("schema-class", "invenio_requests.services.schemas.NoneReceiverGenericRequestSchema")
            marshmallow.setdefault("module", datatype.definition["marshmallow"]["module"])
            marshmallow.setdefault("generate", True)
            append_array(datatype, "requests", request_name, "parent-marshmallow", "imports",
                         {
                             "import": "oarepo_requests.schemas.marshmallow.NoneReceiverGenericRequestSchema"
                         }
                         )



            # todo this needs to be updated if other types of actions are considered
            request_actions = request_input_data.setdefault("actions", {"approve": {}})
            for action_name, action_input_data in request_actions.items():
                request_action_module = action_input_data.setdefault(
                    "module", f"{request_module}.actions"
                )
                action_input_data.setdefault(
                    "class",
                    f"{request_action_module}.{camel_case(request_name)}RequestAcceptAction",
                )
                action_input_data.setdefault("generate", True)
                action_input_data.setdefault(
                    "base-classes", ["AcceptAction"]
                )  # accept action
                action_input_data.setdefault(
                    "imports",
                    [
                        {
                            "import": "invenio_requests.customizations.AcceptAction",
                        },
                    ],
                )
