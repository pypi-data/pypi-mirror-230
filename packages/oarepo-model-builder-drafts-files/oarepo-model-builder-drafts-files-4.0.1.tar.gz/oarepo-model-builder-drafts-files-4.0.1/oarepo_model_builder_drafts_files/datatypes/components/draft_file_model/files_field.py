from oarepo_model_builder.datatypes.components import RecordModelComponent
from oarepo_model_builder.datatypes.components.model.utils import set_default
from oarepo_model_builder.utils.python_name import base_name
from oarepo_model_builder_files.datatypes import FileDataType
from oarepo_model_builder_files.datatypes.components import FilesFieldModelComponent


class DraftFilesFieldModelComponent(FilesFieldModelComponent):
    eligible_datatypes = [FileDataType]
    depends_on = [RecordModelComponent]
    dependency_remap = FilesFieldModelComponent

    def before_model_prepare(self, datatype, *, context, **kwargs):
        if context["profile"] not in {"files", "draft_files"}:
            return
        files_field = set_default(datatype, "files-field", {})
        if context["profile"] == "draft_files":
            record_class = datatype.definition["record"]["class"]
            files_field.setdefault("file-class", base_name(record_class))
            files_field.setdefault("field-args", ["store=False", "delete=False"])
            files_field.setdefault(
                "imports",
                [
                    {
                        "import": "invenio_records_resources.records.systemfields.FilesField"
                    },
                    {"import": record_class},
                ],
            )

        if context["profile"] == "files":
            files_field.setdefault(
                "field-args", ["store=False", "create=False", "delete=False"]
            )

        super().before_model_prepare(datatype, context=context, **kwargs)
