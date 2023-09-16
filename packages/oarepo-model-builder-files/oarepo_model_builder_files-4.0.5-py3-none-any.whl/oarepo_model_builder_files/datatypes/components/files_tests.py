from oarepo_model_builder.datatypes import DataTypeComponent, ModelDataType
from oarepo_model_builder_tests.datatypes.components import ModelTestComponent


class FilesModelTestComponent(DataTypeComponent):
    eligible_datatypes = [ModelDataType]
    depends_on = [ModelTestComponent]

    def process_files_tests(self, datatype, section, **extra_kwargs):
        section.fixtures = {}
        section.constants = {"skip_continous_disable_files_test": False}
