from oarepo_model_builder.datatypes import DataType
from oarepo_model_builder.datatypes.components import PermissionsModelComponent
from oarepo_model_builder.datatypes.components.model.utils import set_default

from oarepo_model_builder_files.datatypes import FileDataType


class FilesPermissionsModelComponent(PermissionsModelComponent):
    eligible_datatypes = [FileDataType]
    dependency_remap = PermissionsModelComponent

    def before_model_prepare(self, datatype, *, context, **kwargs):
        parent_record_datatype: DataType = context["parent_record"]
        permissions = set_default(datatype, "permissions", {})
        permissions.setdefault(
            "class", parent_record_datatype.definition["permissions"]["class"]
        )
        permissions.setdefault("generate", False)
        super().before_model_prepare(datatype, context=context, **kwargs)
