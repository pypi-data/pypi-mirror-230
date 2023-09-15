"""
Type annotations for entityresolution service type definitions.

[Open documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_entityresolution/type_defs/)

Usage::

    ```python
    from mypy_boto3_entityresolution.type_defs import IncrementalRunConfigTypeDef

    data: IncrementalRunConfigTypeDef = ...
    ```
"""
import sys
from datetime import datetime
from typing import Dict, List, Mapping, Sequence

from .literals import (
    AttributeMatchingModelType,
    JobStatusType,
    ResolutionTypeType,
    SchemaAttributeTypeType,
)

if sys.version_info >= (3, 12):
    from typing import Literal
else:
    from typing_extensions import Literal
if sys.version_info >= (3, 12):
    from typing import NotRequired
else:
    from typing_extensions import NotRequired
if sys.version_info >= (3, 12):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict


__all__ = (
    "IncrementalRunConfigTypeDef",
    "InputSourceTypeDef",
    "ResponseMetadataTypeDef",
    "SchemaInputAttributeTypeDef",
    "DeleteMatchingWorkflowInputRequestTypeDef",
    "DeleteSchemaMappingInputRequestTypeDef",
    "ErrorDetailsTypeDef",
    "GetMatchIdInputRequestTypeDef",
    "GetMatchingJobInputRequestTypeDef",
    "JobMetricsTypeDef",
    "GetMatchingWorkflowInputRequestTypeDef",
    "GetSchemaMappingInputRequestTypeDef",
    "JobSummaryTypeDef",
    "PaginatorConfigTypeDef",
    "ListMatchingJobsInputRequestTypeDef",
    "ListMatchingWorkflowsInputRequestTypeDef",
    "MatchingWorkflowSummaryTypeDef",
    "ListSchemaMappingsInputRequestTypeDef",
    "SchemaMappingSummaryTypeDef",
    "ListTagsForResourceInputRequestTypeDef",
    "OutputAttributeTypeDef",
    "RuleTypeDef",
    "StartMatchingJobInputRequestTypeDef",
    "TagResourceInputRequestTypeDef",
    "UntagResourceInputRequestTypeDef",
    "DeleteMatchingWorkflowOutputTypeDef",
    "DeleteSchemaMappingOutputTypeDef",
    "GetMatchIdOutputTypeDef",
    "ListTagsForResourceOutputTypeDef",
    "StartMatchingJobOutputTypeDef",
    "CreateSchemaMappingInputRequestTypeDef",
    "CreateSchemaMappingOutputTypeDef",
    "GetSchemaMappingOutputTypeDef",
    "GetMatchingJobOutputTypeDef",
    "ListMatchingJobsOutputTypeDef",
    "ListMatchingJobsInputListMatchingJobsPaginateTypeDef",
    "ListMatchingWorkflowsInputListMatchingWorkflowsPaginateTypeDef",
    "ListSchemaMappingsInputListSchemaMappingsPaginateTypeDef",
    "ListMatchingWorkflowsOutputTypeDef",
    "ListSchemaMappingsOutputTypeDef",
    "OutputSourceTypeDef",
    "RuleBasedPropertiesTypeDef",
    "ResolutionTechniquesTypeDef",
    "CreateMatchingWorkflowInputRequestTypeDef",
    "CreateMatchingWorkflowOutputTypeDef",
    "GetMatchingWorkflowOutputTypeDef",
    "UpdateMatchingWorkflowInputRequestTypeDef",
    "UpdateMatchingWorkflowOutputTypeDef",
)

IncrementalRunConfigTypeDef = TypedDict(
    "IncrementalRunConfigTypeDef",
    {
        "incrementalRunType": NotRequired[Literal["IMMEDIATE"]],
    },
)

InputSourceTypeDef = TypedDict(
    "InputSourceTypeDef",
    {
        "inputSourceARN": str,
        "schemaName": str,
        "applyNormalization": NotRequired[bool],
    },
)

ResponseMetadataTypeDef = TypedDict(
    "ResponseMetadataTypeDef",
    {
        "RequestId": str,
        "HostId": str,
        "HTTPStatusCode": int,
        "HTTPHeaders": Dict[str, str],
        "RetryAttempts": int,
    },
)

SchemaInputAttributeTypeDef = TypedDict(
    "SchemaInputAttributeTypeDef",
    {
        "fieldName": str,
        "type": SchemaAttributeTypeType,
        "groupName": NotRequired[str],
        "matchKey": NotRequired[str],
    },
)

DeleteMatchingWorkflowInputRequestTypeDef = TypedDict(
    "DeleteMatchingWorkflowInputRequestTypeDef",
    {
        "workflowName": str,
    },
)

DeleteSchemaMappingInputRequestTypeDef = TypedDict(
    "DeleteSchemaMappingInputRequestTypeDef",
    {
        "schemaName": str,
    },
)

ErrorDetailsTypeDef = TypedDict(
    "ErrorDetailsTypeDef",
    {
        "errorMessage": NotRequired[str],
    },
)

GetMatchIdInputRequestTypeDef = TypedDict(
    "GetMatchIdInputRequestTypeDef",
    {
        "record": Mapping[str, str],
        "workflowName": str,
    },
)

GetMatchingJobInputRequestTypeDef = TypedDict(
    "GetMatchingJobInputRequestTypeDef",
    {
        "jobId": str,
        "workflowName": str,
    },
)

JobMetricsTypeDef = TypedDict(
    "JobMetricsTypeDef",
    {
        "inputRecords": NotRequired[int],
        "matchIDs": NotRequired[int],
        "recordsNotProcessed": NotRequired[int],
        "totalRecordsProcessed": NotRequired[int],
    },
)

GetMatchingWorkflowInputRequestTypeDef = TypedDict(
    "GetMatchingWorkflowInputRequestTypeDef",
    {
        "workflowName": str,
    },
)

GetSchemaMappingInputRequestTypeDef = TypedDict(
    "GetSchemaMappingInputRequestTypeDef",
    {
        "schemaName": str,
    },
)

JobSummaryTypeDef = TypedDict(
    "JobSummaryTypeDef",
    {
        "jobId": str,
        "startTime": datetime,
        "status": JobStatusType,
        "endTime": NotRequired[datetime],
    },
)

PaginatorConfigTypeDef = TypedDict(
    "PaginatorConfigTypeDef",
    {
        "MaxItems": NotRequired[int],
        "PageSize": NotRequired[int],
        "StartingToken": NotRequired[str],
    },
)

ListMatchingJobsInputRequestTypeDef = TypedDict(
    "ListMatchingJobsInputRequestTypeDef",
    {
        "workflowName": str,
        "maxResults": NotRequired[int],
        "nextToken": NotRequired[str],
    },
)

ListMatchingWorkflowsInputRequestTypeDef = TypedDict(
    "ListMatchingWorkflowsInputRequestTypeDef",
    {
        "maxResults": NotRequired[int],
        "nextToken": NotRequired[str],
    },
)

MatchingWorkflowSummaryTypeDef = TypedDict(
    "MatchingWorkflowSummaryTypeDef",
    {
        "createdAt": datetime,
        "updatedAt": datetime,
        "workflowArn": str,
        "workflowName": str,
    },
)

ListSchemaMappingsInputRequestTypeDef = TypedDict(
    "ListSchemaMappingsInputRequestTypeDef",
    {
        "maxResults": NotRequired[int],
        "nextToken": NotRequired[str],
    },
)

SchemaMappingSummaryTypeDef = TypedDict(
    "SchemaMappingSummaryTypeDef",
    {
        "createdAt": datetime,
        "schemaArn": str,
        "schemaName": str,
        "updatedAt": datetime,
    },
)

ListTagsForResourceInputRequestTypeDef = TypedDict(
    "ListTagsForResourceInputRequestTypeDef",
    {
        "resourceArn": str,
    },
)

OutputAttributeTypeDef = TypedDict(
    "OutputAttributeTypeDef",
    {
        "name": str,
        "hashed": NotRequired[bool],
    },
)

RuleTypeDef = TypedDict(
    "RuleTypeDef",
    {
        "matchingKeys": Sequence[str],
        "ruleName": str,
    },
)

StartMatchingJobInputRequestTypeDef = TypedDict(
    "StartMatchingJobInputRequestTypeDef",
    {
        "workflowName": str,
    },
)

TagResourceInputRequestTypeDef = TypedDict(
    "TagResourceInputRequestTypeDef",
    {
        "resourceArn": str,
        "tags": Mapping[str, str],
    },
)

UntagResourceInputRequestTypeDef = TypedDict(
    "UntagResourceInputRequestTypeDef",
    {
        "resourceArn": str,
        "tagKeys": Sequence[str],
    },
)

DeleteMatchingWorkflowOutputTypeDef = TypedDict(
    "DeleteMatchingWorkflowOutputTypeDef",
    {
        "message": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DeleteSchemaMappingOutputTypeDef = TypedDict(
    "DeleteSchemaMappingOutputTypeDef",
    {
        "message": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

GetMatchIdOutputTypeDef = TypedDict(
    "GetMatchIdOutputTypeDef",
    {
        "matchId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListTagsForResourceOutputTypeDef = TypedDict(
    "ListTagsForResourceOutputTypeDef",
    {
        "tags": Dict[str, str],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

StartMatchingJobOutputTypeDef = TypedDict(
    "StartMatchingJobOutputTypeDef",
    {
        "jobId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateSchemaMappingInputRequestTypeDef = TypedDict(
    "CreateSchemaMappingInputRequestTypeDef",
    {
        "mappedInputFields": Sequence[SchemaInputAttributeTypeDef],
        "schemaName": str,
        "description": NotRequired[str],
        "tags": NotRequired[Mapping[str, str]],
    },
)

CreateSchemaMappingOutputTypeDef = TypedDict(
    "CreateSchemaMappingOutputTypeDef",
    {
        "description": str,
        "mappedInputFields": List[SchemaInputAttributeTypeDef],
        "schemaArn": str,
        "schemaName": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

GetSchemaMappingOutputTypeDef = TypedDict(
    "GetSchemaMappingOutputTypeDef",
    {
        "createdAt": datetime,
        "description": str,
        "mappedInputFields": List[SchemaInputAttributeTypeDef],
        "schemaArn": str,
        "schemaName": str,
        "tags": Dict[str, str],
        "updatedAt": datetime,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

GetMatchingJobOutputTypeDef = TypedDict(
    "GetMatchingJobOutputTypeDef",
    {
        "endTime": datetime,
        "errorDetails": ErrorDetailsTypeDef,
        "jobId": str,
        "metrics": JobMetricsTypeDef,
        "startTime": datetime,
        "status": JobStatusType,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListMatchingJobsOutputTypeDef = TypedDict(
    "ListMatchingJobsOutputTypeDef",
    {
        "jobs": List[JobSummaryTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListMatchingJobsInputListMatchingJobsPaginateTypeDef = TypedDict(
    "ListMatchingJobsInputListMatchingJobsPaginateTypeDef",
    {
        "workflowName": str,
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)

ListMatchingWorkflowsInputListMatchingWorkflowsPaginateTypeDef = TypedDict(
    "ListMatchingWorkflowsInputListMatchingWorkflowsPaginateTypeDef",
    {
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)

ListSchemaMappingsInputListSchemaMappingsPaginateTypeDef = TypedDict(
    "ListSchemaMappingsInputListSchemaMappingsPaginateTypeDef",
    {
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)

ListMatchingWorkflowsOutputTypeDef = TypedDict(
    "ListMatchingWorkflowsOutputTypeDef",
    {
        "nextToken": str,
        "workflowSummaries": List[MatchingWorkflowSummaryTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListSchemaMappingsOutputTypeDef = TypedDict(
    "ListSchemaMappingsOutputTypeDef",
    {
        "nextToken": str,
        "schemaList": List[SchemaMappingSummaryTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

OutputSourceTypeDef = TypedDict(
    "OutputSourceTypeDef",
    {
        "output": Sequence[OutputAttributeTypeDef],
        "outputS3Path": str,
        "KMSArn": NotRequired[str],
        "applyNormalization": NotRequired[bool],
    },
)

RuleBasedPropertiesTypeDef = TypedDict(
    "RuleBasedPropertiesTypeDef",
    {
        "attributeMatchingModel": AttributeMatchingModelType,
        "rules": Sequence[RuleTypeDef],
    },
)

ResolutionTechniquesTypeDef = TypedDict(
    "ResolutionTechniquesTypeDef",
    {
        "resolutionType": ResolutionTypeType,
        "ruleBasedProperties": NotRequired[RuleBasedPropertiesTypeDef],
    },
)

CreateMatchingWorkflowInputRequestTypeDef = TypedDict(
    "CreateMatchingWorkflowInputRequestTypeDef",
    {
        "inputSourceConfig": Sequence[InputSourceTypeDef],
        "outputSourceConfig": Sequence[OutputSourceTypeDef],
        "resolutionTechniques": ResolutionTechniquesTypeDef,
        "roleArn": str,
        "workflowName": str,
        "description": NotRequired[str],
        "incrementalRunConfig": NotRequired[IncrementalRunConfigTypeDef],
        "tags": NotRequired[Mapping[str, str]],
    },
)

CreateMatchingWorkflowOutputTypeDef = TypedDict(
    "CreateMatchingWorkflowOutputTypeDef",
    {
        "description": str,
        "incrementalRunConfig": IncrementalRunConfigTypeDef,
        "inputSourceConfig": List[InputSourceTypeDef],
        "outputSourceConfig": List[OutputSourceTypeDef],
        "resolutionTechniques": ResolutionTechniquesTypeDef,
        "roleArn": str,
        "workflowArn": str,
        "workflowName": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

GetMatchingWorkflowOutputTypeDef = TypedDict(
    "GetMatchingWorkflowOutputTypeDef",
    {
        "createdAt": datetime,
        "description": str,
        "incrementalRunConfig": IncrementalRunConfigTypeDef,
        "inputSourceConfig": List[InputSourceTypeDef],
        "outputSourceConfig": List[OutputSourceTypeDef],
        "resolutionTechniques": ResolutionTechniquesTypeDef,
        "roleArn": str,
        "tags": Dict[str, str],
        "updatedAt": datetime,
        "workflowArn": str,
        "workflowName": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

UpdateMatchingWorkflowInputRequestTypeDef = TypedDict(
    "UpdateMatchingWorkflowInputRequestTypeDef",
    {
        "inputSourceConfig": Sequence[InputSourceTypeDef],
        "outputSourceConfig": Sequence[OutputSourceTypeDef],
        "resolutionTechniques": ResolutionTechniquesTypeDef,
        "roleArn": str,
        "workflowName": str,
        "description": NotRequired[str],
        "incrementalRunConfig": NotRequired[IncrementalRunConfigTypeDef],
    },
)

UpdateMatchingWorkflowOutputTypeDef = TypedDict(
    "UpdateMatchingWorkflowOutputTypeDef",
    {
        "description": str,
        "incrementalRunConfig": IncrementalRunConfigTypeDef,
        "inputSourceConfig": List[InputSourceTypeDef],
        "outputSourceConfig": List[OutputSourceTypeDef],
        "resolutionTechniques": ResolutionTechniquesTypeDef,
        "roleArn": str,
        "workflowName": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
