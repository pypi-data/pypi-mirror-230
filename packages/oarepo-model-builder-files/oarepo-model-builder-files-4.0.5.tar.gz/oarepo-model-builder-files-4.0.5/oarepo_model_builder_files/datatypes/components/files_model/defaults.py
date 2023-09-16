from oarepo_model_builder.datatypes import DataType
from oarepo_model_builder.datatypes.components import DefaultsModelComponent
from oarepo_model_builder.datatypes.components.model.utils import set_default

from oarepo_model_builder_files.datatypes import FileDataType


class FilesDefaultsModelComponent(DefaultsModelComponent):
    eligible_datatypes = [FileDataType]
    dependency_remap = DefaultsModelComponent

    def before_model_prepare(self, datatype, *, context, **kwargs):
        parent_record_datatype: DataType = context["parent_record"]

        parent_record_prefix = parent_record_datatype.definition["module"]["prefix"]
        parent_record_alias = parent_record_datatype.definition["module"]["alias"]

        module = set_default(datatype, "module", {})
        module.setdefault(
            "qualified", parent_record_datatype.definition["module"]["qualified"]
        )
        module.setdefault("prefix", f"{parent_record_prefix}File")
        module.setdefault("alias", f"{parent_record_alias}_file")
        super().before_model_prepare(datatype, context=context, **kwargs)
