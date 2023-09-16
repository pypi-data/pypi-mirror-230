import marshmallow as ma
from oarepo_model_builder.datatypes import (
    DataType,
    DataTypeComponent,
    Import,
    ModelDataType,
    Section,
)
from oarepo_model_builder.datatypes.components import DefaultsModelComponent
from oarepo_model_builder.datatypes.components.model.utils import set_default
from oarepo_model_builder.datatypes.model import Link


def get_draft_file_schema():
    from ..draft_file import DraftFileDataType

    return DraftFileDataType.validator()


class DraftFileComponent(DataTypeComponent):
    eligible_datatypes = [ModelDataType]
    affects = [DefaultsModelComponent]

    class ModelSchema(ma.Schema):
        draft_files = ma.fields.Nested(
            get_draft_file_schema, data_key="draft-files", attribute="draft-files"
        )

    def process_mb_invenio_record_service_config(self, *, datatype, section, **kwargs):
        if self.is_draft_files_profile:
            # override class as it has to be a parent class
            section.config.setdefault("record", {})[
                "class"
            ] = datatype.parent_record.definition["record"]["class"]

    def process_links(self, datatype, section: Section, **kwargs):
        def add_backslah_if_missing(url):
            if url[-1] != "/":
                url += "/"
            return url

        url_prefix = add_backslah_if_missing(
            datatype.definition["resource-config"]["base-url"].replace(
                "<pid_value>", "{id}"
            )
        )

        if self.is_record_profile:
            has_files = "files" in datatype.definition
            if not has_files:
                return
            try:
                files_url_prefix = add_backslah_if_missing(
                    datatype.definition["files"]["resource-config"]["base-url"].replace(
                        "<pid_value>", "{id}"
                    )
                )
            except KeyError:
                files_url_prefix = f"{url_prefix}{{id}}/"
            try:
                draft_files_url_prefix = add_backslah_if_missing(
                    datatype.definition["draft-files"]["resource-config"][
                        "base-url"
                    ].replace("<pid_value>", "{id}")
                )
            except KeyError:
                draft_files_url_prefix = f"{url_prefix}{{id}}/draft/"
            for link in section.config["links_item"]:
                if link.name == "files":
                    section.config["links_item"].remove(link)
            section.config["links_item"].append(
                Link(
                    name="files",
                    link_class="ConditionalLink",
                    link_args=[
                        "cond=is_record",
                        f'if_=RecordLink("{{+api}}{files_url_prefix}files")',
                        f'else_=RecordLink("{{+api}}{draft_files_url_prefix}files")',
                    ],
                    imports=[
                        Import("invenio_records_resources.services.ConditionalLink"),
                        Import("invenio_records_resources.services.RecordLink"),
                        Import(
                            "invenio_drafts_resources.services.records.config.is_record"
                        ),
                    ],
                )
            ),

        if self.is_draft_files_profile:
            if "links_search" in section.config:
                section.config.pop("links_search")
            # remove normal links and add
            section.config["file_links_list"] = [
                Link(
                    name="self",
                    link_class="RecordLink",
                    link_args=[f'"{{+api}}{url_prefix}files"'],
                    imports=[Import("invenio_records_resources.services.RecordLink")],
                ),
            ]

            section.config.pop("links_item")
            section.config["file_links_item"] = [
                Link(
                    name="self",
                    link_class="FileLink",
                    link_args=[f'"{{+api}}{url_prefix}files/{{key}}"'],
                    imports=[
                        Import("invenio_records_resources.services.FileLink")
                    ],  # NOSONAR
                ),
                Link(
                    name="content",
                    link_class="FileLink",
                    link_args=[f'"{{+api}}{url_prefix}files/{{key}}/content"'],
                    imports=[Import("invenio_records_resources.services.FileLink")],
                ),
                Link(
                    name="commit",
                    link_class="FileLink",
                    link_args=[f'"{{+api}}{url_prefix}files/{{key}}/commit"'],
                    imports=[Import("invenio_records_resources.services.FileLink")],
                ),
            ]

    def before_model_prepare(self, datatype, *, context, **kwargs):
        self.is_draft_files_profile = context["profile"] == "draft_files"
        self.is_record_profile = context["profile"] == "record"
        if not context["profile"] == "draft_files":
            return

        parent_record_datatype: DataType = context["parent_record"]
        datatype.parent_record = parent_record_datatype

        set_default(datatype, "search-options", {}).setdefault("skip", True)
        set_default(datatype, "json-schema-settings", {}).setdefault("skip", True)
        set_default(datatype, "mapping-settings", {}).setdefault("skip", True)
        set_default(datatype, "record-dumper", {}).setdefault("skip", True)
