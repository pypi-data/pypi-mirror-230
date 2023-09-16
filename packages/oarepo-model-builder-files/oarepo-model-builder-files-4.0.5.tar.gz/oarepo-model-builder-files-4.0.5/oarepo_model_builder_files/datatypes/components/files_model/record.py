from oarepo_model_builder.datatypes import DataType
from oarepo_model_builder.datatypes.components import RecordModelComponent
from oarepo_model_builder.datatypes.components.model.utils import set_default

from oarepo_model_builder_files.datatypes import FileDataType


class FilesRecordModelComponent(RecordModelComponent):
    eligible_datatypes = [FileDataType]
    dependency_remap = RecordModelComponent

    def before_model_prepare(self, datatype, *, context, **kwargs):
        parent_record_datatype: DataType = context["parent_record"]
        parent_record_prefix = parent_record_datatype.definition["module"]["prefix"]

        record = set_default(datatype, "record", {})
        record.setdefault("class", f"{parent_record_prefix}File")
        record.setdefault("base-classes", ["FileRecord"])
        record.setdefault(
            "imports", [{"import": "invenio_records_resources.records.api.FileRecord"}]
        )
        super().before_model_prepare(datatype, context=context, **kwargs)
