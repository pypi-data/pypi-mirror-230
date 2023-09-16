from oarepo_model_builder.datatypes.components import RecordMetadataModelComponent
from oarepo_model_builder.datatypes.components.model.utils import (
    append_array,
    place_after,
    set_default,
)

from oarepo_model_builder_files.datatypes import FileDataType


class FilesRecordMetadataModelComponent(RecordMetadataModelComponent):
    eligible_datatypes = [FileDataType]
    dependency_remap = RecordMetadataModelComponent

    def before_model_prepare(self, datatype, *, context, **kwargs):
        record_metadata = set_default(datatype, "record-metadata", {})
        record_metadata.setdefault("use-versioning", False)
        super().before_model_prepare(datatype, context=context, **kwargs)
        place_after(
            datatype,
            "record-metadata",
            "base-classes",
            "RecordMetadataBase",
            "FileRecordModelMixin",
        )
        append_array(
            datatype,
            "record-metadata",
            "imports",
            {"import": "invenio_records_resources.records.FileRecordModelMixin"},
        )
