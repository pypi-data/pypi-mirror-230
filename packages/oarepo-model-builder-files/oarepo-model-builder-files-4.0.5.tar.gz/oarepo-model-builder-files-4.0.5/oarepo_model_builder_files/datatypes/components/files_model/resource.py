from oarepo_model_builder.datatypes import DataType
from oarepo_model_builder.datatypes.components import ResourceModelComponent
from oarepo_model_builder.datatypes.components.model.utils import set_default

from oarepo_model_builder_files.datatypes import FileDataType


class FilesResourceModelComponent(ResourceModelComponent):
    eligible_datatypes = [FileDataType]
    dependency_remap = ResourceModelComponent

    def before_model_prepare(self, datatype, *, context, **kwargs):
        parent_record_datatype: DataType = context["parent_record"]
        resource_config = set_default(datatype, "resource-config", {})
        parent_record_url = parent_record_datatype.definition["resource-config"][
            "base-url"
        ]
        resource_config.setdefault("base-url", f"{parent_record_url}<pid_value>")
        resource_config.setdefault("base-classes", ["FileResourceConfig"])
        resource_config.setdefault(
            "imports",
            [{"import": "invenio_records_resources.resources.FileResourceConfig"}],
        )
        resource = set_default(datatype, "resource", {})
        resource.setdefault("base-classes", ["FileResource"])
        resource.setdefault(
            "imports",
            [
                {
                    "import": "invenio_records_resources.resources.files.resource.FileResource"
                }
            ],
        )

        super().before_model_prepare(datatype, context=context, **kwargs)
