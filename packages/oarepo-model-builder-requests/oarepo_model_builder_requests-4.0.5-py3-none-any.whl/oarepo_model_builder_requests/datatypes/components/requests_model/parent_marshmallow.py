import marshmallow as ma
from oarepo_model_builder.datatypes import DataTypeComponent, ModelDataType
from oarepo_model_builder.datatypes.components.model.utils import set_default, append_array
from oarepo_model_builder.validation.utils import ImportSchema
from oarepo_model_builder.datatypes.components import DefaultsModelComponent, MarshmallowModelComponent



class ParentMarshmallowClassSchema(ma.Schema):
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

class ParentMarshmallowComponent(DataTypeComponent):
    eligible_datatypes = [ModelDataType]
    depends_on = [DefaultsModelComponent, MarshmallowModelComponent]

    class ModelSchema(ma.Schema):
        parent_record_marshmallow = ma.fields.Nested(
            ParentMarshmallowClassSchema,
            attribute="parent-record-marshmallow",
            data_key="parent-record-marshmallow",
        )

    def before_model_prepare(self, datatype, *, context, **kwargs):
        marshmallow = set_default(datatype, "parent-record-marshmallow", {})
        m_module = marshmallow.setdefault("module", datatype.definition["marshmallow"]["module"])
        marshmallow.setdefault("class", f"{m_module}.GeneratedParentSchema")
        marshmallow.setdefault("generate", True)
        marshmallow.setdefault("base-classes", ["InvenioParentSchema"])
        append_array(datatype, "parent-record-marshmallow", "imports",
                     {
                         "import": "invenio_drafts_resources.services.records.schema.ParentSchema",
                         "alias": "InvenioParentSchema"
                     },
                     )