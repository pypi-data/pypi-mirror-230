import marshmallow as ma
from oarepo_model_builder.datatypes import DataTypeComponent, ModelDataType
from oarepo_model_builder.datatypes.components.model.utils import set_default
from oarepo_model_builder.validation.utils import ImportSchema

from . import RequestsComponent


class RecordResolverClassSchema(ma.Schema):
    class Meta:
        unknown = ma.RAISE

    generate = ma.fields.Bool()
    class_ = ma.fields.Str(
        attribute="class",
        data_key="class",
    )
    base_classes = ma.fields.List(
        ma.fields.Str(),
        attribute="base-classes",
        data_key="base-classes",
    )
    extra_code = ma.fields.Str(
        attribute="extra-code",
        data_key="extra-code",
    )
    module = ma.fields.String(metadata={"doc": "Class module"})
    imports = ma.fields.List(
        ma.fields.Nested(ImportSchema), metadata={"doc": "List of python imports"}
    )
    custom_proxy_class = ma.fields.Str(
        attribute="custom-proxy-class",
        data_key="custom-proxy-class",
    )
    skip = ma.fields.Boolean()


class RecordResolverComponent(DataTypeComponent):
    eligible_datatypes = [ModelDataType]
    depends_on = [RequestsComponent]

    class ModelSchema(ma.Schema):
        record_resolver = ma.fields.Nested(
            RecordResolverClassSchema,
            attribute="record-resolver",
            data_key="record-resolver",
        )

    def before_model_prepare(self, datatype, *, context, **kwargs):
        module = datatype.definition["module"]["qualified"]
        profile_module = context["profile_module"]

        record_resolver = set_default(datatype, "record-resolver", {})

        if not datatype.definition[
            "requests"
        ]:  # resolver is now used only in requests, therefore do not generate if requests are not present
            record_resolver.setdefault("generate", False)
            record_resolver.setdefault("skip", True)
            return

        record_resolver.setdefault("generate", True)
        resolver_module = record_resolver.setdefault(
            "module", f"{module}.{profile_module}.requests.resolvers"
        )
        record_resolver.setdefault(
            "class",
            f"{resolver_module}.{datatype.definition['module']['prefix']}Resolver",
        )
        record_resolver.setdefault(
            "base-classes",
            ["RecordResolver"],
        )
        record_resolver.setdefault(
            "imports",
            [
                {
                    "import": "invenio_records_resources.references.RecordResolver",
                },
            ],
        )

        if context["profile"] in ("draft", "draft_files"):
            record_resolver.setdefault(
                "custom-proxy-class", "oarepo_runtime.resolvers.DraftProxy"
            )
