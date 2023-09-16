from oarepo_model_builder_files.builders.parent_builder import InvenioFilesParentBuilder


class TestResourcesBuilder(InvenioFilesParentBuilder):
    TYPE = "invenio_files_drats_test_files_resources"
    template = "draft-files-test-file-resources"

    def _get_output_module(self):
        return f'{self.current_model.definition["tests"]["module"]}.files.test_file_resources'
