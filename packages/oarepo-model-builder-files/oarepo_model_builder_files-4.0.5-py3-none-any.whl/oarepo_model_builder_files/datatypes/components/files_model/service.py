from oarepo_model_builder.datatypes.components import ServiceModelComponent
from oarepo_model_builder.datatypes.components.model.utils import set_default

from oarepo_model_builder_files.datatypes import FileDataType


class FilesServiceModelComponent(ServiceModelComponent):
    eligible_datatypes = [FileDataType]
    dependency_remap = ServiceModelComponent

    def before_model_prepare(self, datatype, *, context, **kwargs):
        service_config = set_default(datatype, "service-config", {})
        service_config.setdefault(
            "base-classes", ["PermissionsPresetsConfigMixin", "FileServiceConfig"]
        )
        service_config.setdefault(
            "imports",
            [
                {"import": "invenio_records_resources.services.FileServiceConfig"},
                {
                    "import": "oarepo_runtime.config.service.PermissionsPresetsConfigMixin"
                },
            ],
        )

        service = set_default(datatype, "service", {})
        service.setdefault("base-classes", ["FileService"])
        service.setdefault(
            "imports", [{"import": "invenio_records_resources.services.FileService"}]
        )
        super().before_model_prepare(datatype, context=context, **kwargs)
