import json
from dataclasses import dataclass, field
import os
from typing import Iterable, Iterator, Union

from pydantic.fields import Field

from datahub.configuration.common import ConfigModel
from datahub.ingestion.api.decorators import (
    SupportStatus,
    config_class,
    platform_name,
    support_status,
)
from datahub.ingestion.api.source import Source, SourceReport
from datahub.ingestion.api.workunit import MetadataWorkUnit, UsageStatsWorkUnit
from datahub.metadata.com.linkedin.pegasus2avro.mxe import (
    MetadataChangeEvent,
    MetadataChangeProposal,
)
from datahub.metadata.schema_classes import UsageAggregationClass
import requests
from datahub.ingestion.api.common import PipelineContext
from datahub.emitter.mcp import MetadataChangeProposalWrapper
from datahub.metadata.schema_classes import (
    ChangeTypeClass,
    GlobalTagsClass,

    TagAssociationClass,
)

import logging
import time

from datahub.emitter.mce_builder import make_tag_urn
from datahub.emitter.mcp import MetadataChangeProposalWrapper

# read-modify-write requires access to the DataHubGraph (RestEmitter is not enough)
from datahub.ingestion.graph.client import DatahubClientConfig, DataHubGraph

# Imports for metadata model classes
from datahub.metadata.schema_classes import (
    AuditStampClass,
    ChangeTypeClass,
    EditableSchemaFieldInfoClass,
    EditableSchemaMetadataClass,
    GlobalTagsClass,
    TagAssociationClass,
)

# Inspired by dataset_add_column_tag.py


def get_simple_field_path_from_v2_field_path(field_path: str) -> str:
    """A helper function to extract simple . path notation from the v2 field path"""
    if not field_path.startswith("[version=2.0]"):
        # not a v2, we assume this is a simple path
        return field_path
        # this is a v2 field path
    tokens = [
        t for t in field_path.split(".") if not (t.startswith("[") or t.endswith("]"))
    ]

    return ".".join(tokens)


class FormalSourceConfig(ConfigModel):
    client_id: str = Field(description="Client ID.")
    secret_key: str = Field(description="Secret Key.")
    datastore_id: str = Field(description="ID of the Formal Sidecar.")

    dataset_urn: str = Field(
        description="URN of a Datahub Dataset, ie the Datahub URN of a Postgres Table.")
    datahub_gms_endpoint: str = Field(
        description="Datahub GMS endpoint, eg 'http://localhost:8080'.")


@platform_name("Formal")
@config_class(FormalSourceConfig)
@support_status(SupportStatus.INCUBATING)
@dataclass
class FormalSource(Source):
    """
    This plugin pulls metadata from a Formal Data Inventory.
    """

    config: FormalSourceConfig
    report: SourceReport = field(default_factory=SourceReport)

    # def __init__(self, config: FormalSourceConfig, ctx: PipelineContext):
    #     super().__init__(ctx)
    #     self.config = config

    @classmethod
    def create(cls, config_dict, ctx):
        config = FormalSourceConfig.parse_obj(config_dict)
        return cls(ctx, config)

    def get_workunits(self) -> Iterable[Union[MetadataWorkUnit, UsageStatsWorkUnit]]:
        BASE_URL = "https://api.formalcloud.net"
        if os.getenv('PLUGIN_ENV') == "development":
            BASE_URL = "http://localhost:4000"

        my_headers = {'client_id': self.config.client_id,
                      'api_key': self.config.secret_key}
        response = requests.get(
            BASE_URL + "/admin/inventory/flat", headers=my_headers)
        res = response.json()
        inv = res['inventory']

        dataset_details = self.config.dataset_urn.split("(")[1].split(")")[0]
        dataset_path = dataset_details.split(",")[1]

        dataset_database = dataset_path.split(".")[0]
        dataset_schema = dataset_path.split(".")[1]
        dataset_table = dataset_path.split(".")[2]

        dataset_urn = self.config.dataset_urn
        graph = DataHubGraph(DatahubClientConfig(
            server=(self.config.datahub_gms_endpoint or "http://localhost:8080")))

        current_editable_schema_metadata = graph.get_aspect_v2(
            entity_urn=dataset_urn,
            aspect="editableSchemaMetadata",
            aspect_type=EditableSchemaMetadataClass,
        )

        for inv_item in inv:
            if not inv_item['datastore_id'] or inv_item['datastore_id'] != self.config.datastore_id:
                continue

            # data_label migration
            if not inv_item['data_label']:
                continue

            if not inv_item['path'] or len(inv_item['path'].split(".")) != 4:
                continue

            # TODO allow user to specify these in config, so they don't need to be equivalent to dataset_{}
            inv_split_path = inv_item['path'].split(".")
            inv_database = inv_split_path[0]
            inv_schema = inv_split_path[1]
            inv_table = inv_split_path[2]
            inv_field = inv_split_path[3]


            # Mismatch paths despite configuration
            if inv_database != dataset_database or inv_schema != dataset_schema or inv_table != dataset_table:
                continue

            # data_label migration
            # Process data labels
            data_label = inv_item['data_label']
            
            if data_label != "formal_spacer_empty_set":
                tag_urn = make_tag_urn(data_label)
                # Some pre-built objects to help all the conditional pathways
                tag_association_to_add = TagAssociationClass(tag=tag_urn)

                tags_aspect_to_set = GlobalTagsClass(tags=[tag_association_to_add])
                field_info_to_set = EditableSchemaFieldInfoClass(
                    fieldPath=inv_field, globalTags=tags_aspect_to_set
                )

                # Work from editable schema
                need_write = False
                field_match = False
                if current_editable_schema_metadata:
                    for fieldInfo in current_editable_schema_metadata.editableSchemaFieldInfo:
                        simpleRes = get_simple_field_path_from_v2_field_path(fieldInfo.fieldPath) 
                        if simpleRes == inv_field:
                            # we have some editable schema metadata for this field
                            field_match = True
                            if fieldInfo.globalTags:
                                if tag_urn not in [x.tag for x in fieldInfo.globalTags.tags]:
                                    # this tag is not present
                                    fieldInfo.globalTags.tags.append(
                                        tag_association_to_add)
                                    need_write = True
                            else:
                                fieldInfo.globalTags = tags_aspect_to_set
                                need_write = True

                    if not field_match:
                        # this field isn't present in the editable schema metadata aspect, add it
                        field_info = field_info_to_set
                        current_editable_schema_metadata.editableSchemaFieldInfo.append(
                            field_info)
                        need_write = True

                else:
                    # create a brand new editable schema metadata aspect
                    now = int(time.time() * 1000)  # milliseconds since epoch
                    current_timestamp = AuditStampClass(
                        time=now, actor="urn:li:corpuser:ingestion")
                    current_editable_schema_metadata = EditableSchemaMetadataClass(
                        editableSchemaFieldInfo=[field_info_to_set],
                        created=current_timestamp,
                    )
                    need_write = True

                if need_write:
                    mcp = MetadataChangeProposalWrapper(
                        entityType="dataset",
                        changeType=ChangeTypeClass.UPSERT,
                        entityUrn=self.config.dataset_urn,
                        aspectName="editableSchemaMetadata",
                        aspect=current_editable_schema_metadata,
                    )
                    wu = MetadataWorkUnit(
                        id=f"tags-to-{self.config.dataset_urn}", mcp=mcp)
                    self.report.report_workunit(wu)

                    yield wu
                else:
                    log = logging.getLogger(__name__)
                    logging.basicConfig(level=logging.INFO)

                    log.info(f"Tag {tag_urn} already attached to column {inv_field}, omitting write")

    def get_report(self):
        return self.report

    def close(self):
        pass
