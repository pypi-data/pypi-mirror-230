from oarepo_model_builder.datatypes import DataType
from oarepo_model_builder.datatypes.components import PIDModelComponent
from oarepo_model_builder.datatypes.components.model.pid import process_pid_type
from oarepo_model_builder.datatypes.components.model.utils import set_default

from oarepo_model_builder_files.datatypes import FileDataType


class FilesPIDModelComponent(PIDModelComponent):
    eligible_datatypes = [FileDataType]
    dependency_remap = PIDModelComponent

    def before_model_prepare(self, datatype, *, context, **kwargs):
        pid = set_default(datatype, "pid", {})
        parent_record_datatype: DataType = context["parent_record"]
        pid.setdefault(
            "type",
            process_pid_type(parent_record_datatype.definition["pid"]["type"] + "File"),
        )
        super().before_model_prepare(datatype, context=context, **kwargs)
