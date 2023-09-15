"""
Type annotations for lookoutequipment service type definitions.

[Open documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_lookoutequipment/type_defs/)

Usage::

    ```python
    from mypy_boto3_lookoutequipment.type_defs import CategoricalValuesTypeDef

    data: CategoricalValuesTypeDef = ...
    ```
"""
import sys
from datetime import datetime
from typing import Dict, List, Sequence, Union

from .literals import (
    AutoPromotionResultType,
    DatasetStatusType,
    DataUploadFrequencyType,
    InferenceDataImportStrategyType,
    InferenceExecutionStatusType,
    InferenceSchedulerStatusType,
    IngestionJobStatusType,
    LabelRatingType,
    LatestInferenceResultType,
    ModelPromoteModeType,
    ModelStatusType,
    ModelVersionSourceTypeType,
    ModelVersionStatusType,
    MonotonicityType,
    RetrainingSchedulerStatusType,
    StatisticalIssueStatusType,
    TargetSamplingRateType,
)

if sys.version_info >= (3, 12):
    from typing import NotRequired
else:
    from typing_extensions import NotRequired
if sys.version_info >= (3, 12):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict

__all__ = (
    "CategoricalValuesTypeDef",
    "CountPercentTypeDef",
    "DatasetSchemaTypeDef",
    "TagTypeDef",
    "ResponseMetadataTypeDef",
    "TimestampTypeDef",
    "DataPreProcessingConfigurationTypeDef",
    "DuplicateTimestampsTypeDef",
    "InvalidSensorDataTypeDef",
    "MissingSensorDataTypeDef",
    "UnsupportedTimestampsTypeDef",
    "DatasetSummaryTypeDef",
    "DeleteDatasetRequestRequestTypeDef",
    "DeleteInferenceSchedulerRequestRequestTypeDef",
    "DeleteLabelGroupRequestRequestTypeDef",
    "DeleteLabelRequestRequestTypeDef",
    "DeleteModelRequestRequestTypeDef",
    "DeleteResourcePolicyRequestRequestTypeDef",
    "DeleteRetrainingSchedulerRequestRequestTypeDef",
    "DescribeDataIngestionJobRequestRequestTypeDef",
    "DescribeDatasetRequestRequestTypeDef",
    "DescribeInferenceSchedulerRequestRequestTypeDef",
    "DescribeLabelGroupRequestRequestTypeDef",
    "DescribeLabelRequestRequestTypeDef",
    "DescribeModelRequestRequestTypeDef",
    "DescribeModelVersionRequestRequestTypeDef",
    "DescribeResourcePolicyRequestRequestTypeDef",
    "DescribeRetrainingSchedulerRequestRequestTypeDef",
    "InferenceEventSummaryTypeDef",
    "S3ObjectTypeDef",
    "InferenceInputNameConfigurationTypeDef",
    "InferenceS3InputConfigurationTypeDef",
    "InferenceS3OutputConfigurationTypeDef",
    "InferenceSchedulerSummaryTypeDef",
    "IngestionS3InputConfigurationTypeDef",
    "MissingCompleteSensorDataTypeDef",
    "SensorsWithShortDateRangeTypeDef",
    "LabelGroupSummaryTypeDef",
    "LabelSummaryTypeDef",
    "LabelsS3InputConfigurationTypeDef",
    "LargeTimestampGapsTypeDef",
    "ListDataIngestionJobsRequestRequestTypeDef",
    "ListDatasetsRequestRequestTypeDef",
    "ListInferenceSchedulersRequestRequestTypeDef",
    "ListLabelGroupsRequestRequestTypeDef",
    "ModelVersionSummaryTypeDef",
    "ListModelsRequestRequestTypeDef",
    "ModelSummaryTypeDef",
    "ListRetrainingSchedulersRequestRequestTypeDef",
    "RetrainingSchedulerSummaryTypeDef",
    "ListSensorStatisticsRequestRequestTypeDef",
    "ListTagsForResourceRequestRequestTypeDef",
    "MonotonicValuesTypeDef",
    "MultipleOperatingModesTypeDef",
    "PutResourcePolicyRequestRequestTypeDef",
    "StartInferenceSchedulerRequestRequestTypeDef",
    "StartRetrainingSchedulerRequestRequestTypeDef",
    "StopInferenceSchedulerRequestRequestTypeDef",
    "StopRetrainingSchedulerRequestRequestTypeDef",
    "UntagResourceRequestRequestTypeDef",
    "UpdateActiveModelVersionRequestRequestTypeDef",
    "UpdateLabelGroupRequestRequestTypeDef",
    "CreateDatasetRequestRequestTypeDef",
    "CreateLabelGroupRequestRequestTypeDef",
    "ImportDatasetRequestRequestTypeDef",
    "TagResourceRequestRequestTypeDef",
    "CreateDatasetResponseTypeDef",
    "CreateInferenceSchedulerResponseTypeDef",
    "CreateLabelGroupResponseTypeDef",
    "CreateLabelResponseTypeDef",
    "CreateModelResponseTypeDef",
    "CreateRetrainingSchedulerResponseTypeDef",
    "DescribeLabelGroupResponseTypeDef",
    "DescribeLabelResponseTypeDef",
    "DescribeResourcePolicyResponseTypeDef",
    "DescribeRetrainingSchedulerResponseTypeDef",
    "EmptyResponseMetadataTypeDef",
    "ImportDatasetResponseTypeDef",
    "ImportModelVersionResponseTypeDef",
    "ListTagsForResourceResponseTypeDef",
    "PutResourcePolicyResponseTypeDef",
    "StartDataIngestionJobResponseTypeDef",
    "StartInferenceSchedulerResponseTypeDef",
    "StartRetrainingSchedulerResponseTypeDef",
    "StopInferenceSchedulerResponseTypeDef",
    "StopRetrainingSchedulerResponseTypeDef",
    "UpdateActiveModelVersionResponseTypeDef",
    "CreateLabelRequestRequestTypeDef",
    "CreateRetrainingSchedulerRequestRequestTypeDef",
    "ListInferenceEventsRequestRequestTypeDef",
    "ListInferenceExecutionsRequestRequestTypeDef",
    "ListLabelsRequestRequestTypeDef",
    "ListModelVersionsRequestRequestTypeDef",
    "UpdateRetrainingSchedulerRequestRequestTypeDef",
    "ListDatasetsResponseTypeDef",
    "ListInferenceEventsResponseTypeDef",
    "IngestedFilesSummaryTypeDef",
    "InferenceInputConfigurationTypeDef",
    "InferenceOutputConfigurationTypeDef",
    "ListInferenceSchedulersResponseTypeDef",
    "IngestionInputConfigurationTypeDef",
    "InsufficientSensorDataTypeDef",
    "ListLabelGroupsResponseTypeDef",
    "ListLabelsResponseTypeDef",
    "LabelsInputConfigurationTypeDef",
    "ListModelVersionsResponseTypeDef",
    "ListModelsResponseTypeDef",
    "ListRetrainingSchedulersResponseTypeDef",
    "SensorStatisticsSummaryTypeDef",
    "CreateInferenceSchedulerRequestRequestTypeDef",
    "DescribeInferenceSchedulerResponseTypeDef",
    "InferenceExecutionSummaryTypeDef",
    "UpdateInferenceSchedulerRequestRequestTypeDef",
    "DataIngestionJobSummaryTypeDef",
    "StartDataIngestionJobRequestRequestTypeDef",
    "DataQualitySummaryTypeDef",
    "CreateModelRequestRequestTypeDef",
    "DescribeModelResponseTypeDef",
    "DescribeModelVersionResponseTypeDef",
    "ImportModelVersionRequestRequestTypeDef",
    "UpdateModelRequestRequestTypeDef",
    "ListSensorStatisticsResponseTypeDef",
    "ListInferenceExecutionsResponseTypeDef",
    "ListDataIngestionJobsResponseTypeDef",
    "DescribeDataIngestionJobResponseTypeDef",
    "DescribeDatasetResponseTypeDef",
)

CategoricalValuesTypeDef = TypedDict(
    "CategoricalValuesTypeDef",
    {
        "Status": StatisticalIssueStatusType,
        "NumberOfCategory": NotRequired[int],
    },
)

CountPercentTypeDef = TypedDict(
    "CountPercentTypeDef",
    {
        "Count": int,
        "Percentage": float,
    },
)

DatasetSchemaTypeDef = TypedDict(
    "DatasetSchemaTypeDef",
    {
        "InlineDataSchema": NotRequired[str],
    },
)

TagTypeDef = TypedDict(
    "TagTypeDef",
    {
        "Key": str,
        "Value": str,
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

TimestampTypeDef = Union[datetime, str]
DataPreProcessingConfigurationTypeDef = TypedDict(
    "DataPreProcessingConfigurationTypeDef",
    {
        "TargetSamplingRate": NotRequired[TargetSamplingRateType],
    },
)

DuplicateTimestampsTypeDef = TypedDict(
    "DuplicateTimestampsTypeDef",
    {
        "TotalNumberOfDuplicateTimestamps": int,
    },
)

InvalidSensorDataTypeDef = TypedDict(
    "InvalidSensorDataTypeDef",
    {
        "AffectedSensorCount": int,
        "TotalNumberOfInvalidValues": int,
    },
)

MissingSensorDataTypeDef = TypedDict(
    "MissingSensorDataTypeDef",
    {
        "AffectedSensorCount": int,
        "TotalNumberOfMissingValues": int,
    },
)

UnsupportedTimestampsTypeDef = TypedDict(
    "UnsupportedTimestampsTypeDef",
    {
        "TotalNumberOfUnsupportedTimestamps": int,
    },
)

DatasetSummaryTypeDef = TypedDict(
    "DatasetSummaryTypeDef",
    {
        "DatasetName": NotRequired[str],
        "DatasetArn": NotRequired[str],
        "Status": NotRequired[DatasetStatusType],
        "CreatedAt": NotRequired[datetime],
    },
)

DeleteDatasetRequestRequestTypeDef = TypedDict(
    "DeleteDatasetRequestRequestTypeDef",
    {
        "DatasetName": str,
    },
)

DeleteInferenceSchedulerRequestRequestTypeDef = TypedDict(
    "DeleteInferenceSchedulerRequestRequestTypeDef",
    {
        "InferenceSchedulerName": str,
    },
)

DeleteLabelGroupRequestRequestTypeDef = TypedDict(
    "DeleteLabelGroupRequestRequestTypeDef",
    {
        "LabelGroupName": str,
    },
)

DeleteLabelRequestRequestTypeDef = TypedDict(
    "DeleteLabelRequestRequestTypeDef",
    {
        "LabelGroupName": str,
        "LabelId": str,
    },
)

DeleteModelRequestRequestTypeDef = TypedDict(
    "DeleteModelRequestRequestTypeDef",
    {
        "ModelName": str,
    },
)

DeleteResourcePolicyRequestRequestTypeDef = TypedDict(
    "DeleteResourcePolicyRequestRequestTypeDef",
    {
        "ResourceArn": str,
    },
)

DeleteRetrainingSchedulerRequestRequestTypeDef = TypedDict(
    "DeleteRetrainingSchedulerRequestRequestTypeDef",
    {
        "ModelName": str,
    },
)

DescribeDataIngestionJobRequestRequestTypeDef = TypedDict(
    "DescribeDataIngestionJobRequestRequestTypeDef",
    {
        "JobId": str,
    },
)

DescribeDatasetRequestRequestTypeDef = TypedDict(
    "DescribeDatasetRequestRequestTypeDef",
    {
        "DatasetName": str,
    },
)

DescribeInferenceSchedulerRequestRequestTypeDef = TypedDict(
    "DescribeInferenceSchedulerRequestRequestTypeDef",
    {
        "InferenceSchedulerName": str,
    },
)

DescribeLabelGroupRequestRequestTypeDef = TypedDict(
    "DescribeLabelGroupRequestRequestTypeDef",
    {
        "LabelGroupName": str,
    },
)

DescribeLabelRequestRequestTypeDef = TypedDict(
    "DescribeLabelRequestRequestTypeDef",
    {
        "LabelGroupName": str,
        "LabelId": str,
    },
)

DescribeModelRequestRequestTypeDef = TypedDict(
    "DescribeModelRequestRequestTypeDef",
    {
        "ModelName": str,
    },
)

DescribeModelVersionRequestRequestTypeDef = TypedDict(
    "DescribeModelVersionRequestRequestTypeDef",
    {
        "ModelName": str,
        "ModelVersion": int,
    },
)

DescribeResourcePolicyRequestRequestTypeDef = TypedDict(
    "DescribeResourcePolicyRequestRequestTypeDef",
    {
        "ResourceArn": str,
    },
)

DescribeRetrainingSchedulerRequestRequestTypeDef = TypedDict(
    "DescribeRetrainingSchedulerRequestRequestTypeDef",
    {
        "ModelName": str,
    },
)

InferenceEventSummaryTypeDef = TypedDict(
    "InferenceEventSummaryTypeDef",
    {
        "InferenceSchedulerArn": NotRequired[str],
        "InferenceSchedulerName": NotRequired[str],
        "EventStartTime": NotRequired[datetime],
        "EventEndTime": NotRequired[datetime],
        "Diagnostics": NotRequired[str],
        "EventDurationInSeconds": NotRequired[int],
    },
)

S3ObjectTypeDef = TypedDict(
    "S3ObjectTypeDef",
    {
        "Bucket": str,
        "Key": str,
    },
)

InferenceInputNameConfigurationTypeDef = TypedDict(
    "InferenceInputNameConfigurationTypeDef",
    {
        "TimestampFormat": NotRequired[str],
        "ComponentTimestampDelimiter": NotRequired[str],
    },
)

InferenceS3InputConfigurationTypeDef = TypedDict(
    "InferenceS3InputConfigurationTypeDef",
    {
        "Bucket": str,
        "Prefix": NotRequired[str],
    },
)

InferenceS3OutputConfigurationTypeDef = TypedDict(
    "InferenceS3OutputConfigurationTypeDef",
    {
        "Bucket": str,
        "Prefix": NotRequired[str],
    },
)

InferenceSchedulerSummaryTypeDef = TypedDict(
    "InferenceSchedulerSummaryTypeDef",
    {
        "ModelName": NotRequired[str],
        "ModelArn": NotRequired[str],
        "InferenceSchedulerName": NotRequired[str],
        "InferenceSchedulerArn": NotRequired[str],
        "Status": NotRequired[InferenceSchedulerStatusType],
        "DataDelayOffsetInMinutes": NotRequired[int],
        "DataUploadFrequency": NotRequired[DataUploadFrequencyType],
        "LatestInferenceResult": NotRequired[LatestInferenceResultType],
    },
)

IngestionS3InputConfigurationTypeDef = TypedDict(
    "IngestionS3InputConfigurationTypeDef",
    {
        "Bucket": str,
        "Prefix": NotRequired[str],
        "KeyPattern": NotRequired[str],
    },
)

MissingCompleteSensorDataTypeDef = TypedDict(
    "MissingCompleteSensorDataTypeDef",
    {
        "AffectedSensorCount": int,
    },
)

SensorsWithShortDateRangeTypeDef = TypedDict(
    "SensorsWithShortDateRangeTypeDef",
    {
        "AffectedSensorCount": int,
    },
)

LabelGroupSummaryTypeDef = TypedDict(
    "LabelGroupSummaryTypeDef",
    {
        "LabelGroupName": NotRequired[str],
        "LabelGroupArn": NotRequired[str],
        "CreatedAt": NotRequired[datetime],
        "UpdatedAt": NotRequired[datetime],
    },
)

LabelSummaryTypeDef = TypedDict(
    "LabelSummaryTypeDef",
    {
        "LabelGroupName": NotRequired[str],
        "LabelId": NotRequired[str],
        "LabelGroupArn": NotRequired[str],
        "StartTime": NotRequired[datetime],
        "EndTime": NotRequired[datetime],
        "Rating": NotRequired[LabelRatingType],
        "FaultCode": NotRequired[str],
        "Equipment": NotRequired[str],
        "CreatedAt": NotRequired[datetime],
    },
)

LabelsS3InputConfigurationTypeDef = TypedDict(
    "LabelsS3InputConfigurationTypeDef",
    {
        "Bucket": str,
        "Prefix": NotRequired[str],
    },
)

LargeTimestampGapsTypeDef = TypedDict(
    "LargeTimestampGapsTypeDef",
    {
        "Status": StatisticalIssueStatusType,
        "NumberOfLargeTimestampGaps": NotRequired[int],
        "MaxTimestampGapInDays": NotRequired[int],
    },
)

ListDataIngestionJobsRequestRequestTypeDef = TypedDict(
    "ListDataIngestionJobsRequestRequestTypeDef",
    {
        "DatasetName": NotRequired[str],
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
        "Status": NotRequired[IngestionJobStatusType],
    },
)

ListDatasetsRequestRequestTypeDef = TypedDict(
    "ListDatasetsRequestRequestTypeDef",
    {
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
        "DatasetNameBeginsWith": NotRequired[str],
    },
)

ListInferenceSchedulersRequestRequestTypeDef = TypedDict(
    "ListInferenceSchedulersRequestRequestTypeDef",
    {
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
        "InferenceSchedulerNameBeginsWith": NotRequired[str],
        "ModelName": NotRequired[str],
        "Status": NotRequired[InferenceSchedulerStatusType],
    },
)

ListLabelGroupsRequestRequestTypeDef = TypedDict(
    "ListLabelGroupsRequestRequestTypeDef",
    {
        "LabelGroupNameBeginsWith": NotRequired[str],
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
    },
)

ModelVersionSummaryTypeDef = TypedDict(
    "ModelVersionSummaryTypeDef",
    {
        "ModelName": NotRequired[str],
        "ModelArn": NotRequired[str],
        "ModelVersion": NotRequired[int],
        "ModelVersionArn": NotRequired[str],
        "CreatedAt": NotRequired[datetime],
        "Status": NotRequired[ModelVersionStatusType],
        "SourceType": NotRequired[ModelVersionSourceTypeType],
    },
)

ListModelsRequestRequestTypeDef = TypedDict(
    "ListModelsRequestRequestTypeDef",
    {
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
        "Status": NotRequired[ModelStatusType],
        "ModelNameBeginsWith": NotRequired[str],
        "DatasetNameBeginsWith": NotRequired[str],
    },
)

ModelSummaryTypeDef = TypedDict(
    "ModelSummaryTypeDef",
    {
        "ModelName": NotRequired[str],
        "ModelArn": NotRequired[str],
        "DatasetName": NotRequired[str],
        "DatasetArn": NotRequired[str],
        "Status": NotRequired[ModelStatusType],
        "CreatedAt": NotRequired[datetime],
        "ActiveModelVersion": NotRequired[int],
        "ActiveModelVersionArn": NotRequired[str],
        "LatestScheduledRetrainingStatus": NotRequired[ModelVersionStatusType],
        "LatestScheduledRetrainingModelVersion": NotRequired[int],
        "LatestScheduledRetrainingStartTime": NotRequired[datetime],
        "NextScheduledRetrainingStartDate": NotRequired[datetime],
        "RetrainingSchedulerStatus": NotRequired[RetrainingSchedulerStatusType],
    },
)

ListRetrainingSchedulersRequestRequestTypeDef = TypedDict(
    "ListRetrainingSchedulersRequestRequestTypeDef",
    {
        "ModelNameBeginsWith": NotRequired[str],
        "Status": NotRequired[RetrainingSchedulerStatusType],
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
    },
)

RetrainingSchedulerSummaryTypeDef = TypedDict(
    "RetrainingSchedulerSummaryTypeDef",
    {
        "ModelName": NotRequired[str],
        "ModelArn": NotRequired[str],
        "Status": NotRequired[RetrainingSchedulerStatusType],
        "RetrainingStartDate": NotRequired[datetime],
        "RetrainingFrequency": NotRequired[str],
        "LookbackWindow": NotRequired[str],
    },
)

ListSensorStatisticsRequestRequestTypeDef = TypedDict(
    "ListSensorStatisticsRequestRequestTypeDef",
    {
        "DatasetName": str,
        "IngestionJobId": NotRequired[str],
        "MaxResults": NotRequired[int],
        "NextToken": NotRequired[str],
    },
)

ListTagsForResourceRequestRequestTypeDef = TypedDict(
    "ListTagsForResourceRequestRequestTypeDef",
    {
        "ResourceArn": str,
    },
)

MonotonicValuesTypeDef = TypedDict(
    "MonotonicValuesTypeDef",
    {
        "Status": StatisticalIssueStatusType,
        "Monotonicity": NotRequired[MonotonicityType],
    },
)

MultipleOperatingModesTypeDef = TypedDict(
    "MultipleOperatingModesTypeDef",
    {
        "Status": StatisticalIssueStatusType,
    },
)

PutResourcePolicyRequestRequestTypeDef = TypedDict(
    "PutResourcePolicyRequestRequestTypeDef",
    {
        "ResourceArn": str,
        "ResourcePolicy": str,
        "ClientToken": str,
        "PolicyRevisionId": NotRequired[str],
    },
)

StartInferenceSchedulerRequestRequestTypeDef = TypedDict(
    "StartInferenceSchedulerRequestRequestTypeDef",
    {
        "InferenceSchedulerName": str,
    },
)

StartRetrainingSchedulerRequestRequestTypeDef = TypedDict(
    "StartRetrainingSchedulerRequestRequestTypeDef",
    {
        "ModelName": str,
    },
)

StopInferenceSchedulerRequestRequestTypeDef = TypedDict(
    "StopInferenceSchedulerRequestRequestTypeDef",
    {
        "InferenceSchedulerName": str,
    },
)

StopRetrainingSchedulerRequestRequestTypeDef = TypedDict(
    "StopRetrainingSchedulerRequestRequestTypeDef",
    {
        "ModelName": str,
    },
)

UntagResourceRequestRequestTypeDef = TypedDict(
    "UntagResourceRequestRequestTypeDef",
    {
        "ResourceArn": str,
        "TagKeys": Sequence[str],
    },
)

UpdateActiveModelVersionRequestRequestTypeDef = TypedDict(
    "UpdateActiveModelVersionRequestRequestTypeDef",
    {
        "ModelName": str,
        "ModelVersion": int,
    },
)

UpdateLabelGroupRequestRequestTypeDef = TypedDict(
    "UpdateLabelGroupRequestRequestTypeDef",
    {
        "LabelGroupName": str,
        "FaultCodes": NotRequired[Sequence[str]],
    },
)

CreateDatasetRequestRequestTypeDef = TypedDict(
    "CreateDatasetRequestRequestTypeDef",
    {
        "DatasetName": str,
        "ClientToken": str,
        "DatasetSchema": NotRequired[DatasetSchemaTypeDef],
        "ServerSideKmsKeyId": NotRequired[str],
        "Tags": NotRequired[Sequence[TagTypeDef]],
    },
)

CreateLabelGroupRequestRequestTypeDef = TypedDict(
    "CreateLabelGroupRequestRequestTypeDef",
    {
        "LabelGroupName": str,
        "ClientToken": str,
        "FaultCodes": NotRequired[Sequence[str]],
        "Tags": NotRequired[Sequence[TagTypeDef]],
    },
)

ImportDatasetRequestRequestTypeDef = TypedDict(
    "ImportDatasetRequestRequestTypeDef",
    {
        "SourceDatasetArn": str,
        "ClientToken": str,
        "DatasetName": NotRequired[str],
        "ServerSideKmsKeyId": NotRequired[str],
        "Tags": NotRequired[Sequence[TagTypeDef]],
    },
)

TagResourceRequestRequestTypeDef = TypedDict(
    "TagResourceRequestRequestTypeDef",
    {
        "ResourceArn": str,
        "Tags": Sequence[TagTypeDef],
    },
)

CreateDatasetResponseTypeDef = TypedDict(
    "CreateDatasetResponseTypeDef",
    {
        "DatasetName": str,
        "DatasetArn": str,
        "Status": DatasetStatusType,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateInferenceSchedulerResponseTypeDef = TypedDict(
    "CreateInferenceSchedulerResponseTypeDef",
    {
        "InferenceSchedulerArn": str,
        "InferenceSchedulerName": str,
        "Status": InferenceSchedulerStatusType,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateLabelGroupResponseTypeDef = TypedDict(
    "CreateLabelGroupResponseTypeDef",
    {
        "LabelGroupName": str,
        "LabelGroupArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateLabelResponseTypeDef = TypedDict(
    "CreateLabelResponseTypeDef",
    {
        "LabelId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateModelResponseTypeDef = TypedDict(
    "CreateModelResponseTypeDef",
    {
        "ModelArn": str,
        "Status": ModelStatusType,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateRetrainingSchedulerResponseTypeDef = TypedDict(
    "CreateRetrainingSchedulerResponseTypeDef",
    {
        "ModelName": str,
        "ModelArn": str,
        "Status": RetrainingSchedulerStatusType,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeLabelGroupResponseTypeDef = TypedDict(
    "DescribeLabelGroupResponseTypeDef",
    {
        "LabelGroupName": str,
        "LabelGroupArn": str,
        "FaultCodes": List[str],
        "CreatedAt": datetime,
        "UpdatedAt": datetime,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeLabelResponseTypeDef = TypedDict(
    "DescribeLabelResponseTypeDef",
    {
        "LabelGroupName": str,
        "LabelGroupArn": str,
        "LabelId": str,
        "StartTime": datetime,
        "EndTime": datetime,
        "Rating": LabelRatingType,
        "FaultCode": str,
        "Notes": str,
        "Equipment": str,
        "CreatedAt": datetime,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeResourcePolicyResponseTypeDef = TypedDict(
    "DescribeResourcePolicyResponseTypeDef",
    {
        "PolicyRevisionId": str,
        "ResourcePolicy": str,
        "CreationTime": datetime,
        "LastModifiedTime": datetime,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeRetrainingSchedulerResponseTypeDef = TypedDict(
    "DescribeRetrainingSchedulerResponseTypeDef",
    {
        "ModelName": str,
        "ModelArn": str,
        "RetrainingStartDate": datetime,
        "RetrainingFrequency": str,
        "LookbackWindow": str,
        "Status": RetrainingSchedulerStatusType,
        "PromoteMode": ModelPromoteModeType,
        "CreatedAt": datetime,
        "UpdatedAt": datetime,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

EmptyResponseMetadataTypeDef = TypedDict(
    "EmptyResponseMetadataTypeDef",
    {
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ImportDatasetResponseTypeDef = TypedDict(
    "ImportDatasetResponseTypeDef",
    {
        "DatasetName": str,
        "DatasetArn": str,
        "Status": DatasetStatusType,
        "JobId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ImportModelVersionResponseTypeDef = TypedDict(
    "ImportModelVersionResponseTypeDef",
    {
        "ModelName": str,
        "ModelArn": str,
        "ModelVersionArn": str,
        "ModelVersion": int,
        "Status": ModelVersionStatusType,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListTagsForResourceResponseTypeDef = TypedDict(
    "ListTagsForResourceResponseTypeDef",
    {
        "Tags": List[TagTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

PutResourcePolicyResponseTypeDef = TypedDict(
    "PutResourcePolicyResponseTypeDef",
    {
        "ResourceArn": str,
        "PolicyRevisionId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

StartDataIngestionJobResponseTypeDef = TypedDict(
    "StartDataIngestionJobResponseTypeDef",
    {
        "JobId": str,
        "Status": IngestionJobStatusType,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

StartInferenceSchedulerResponseTypeDef = TypedDict(
    "StartInferenceSchedulerResponseTypeDef",
    {
        "ModelArn": str,
        "ModelName": str,
        "InferenceSchedulerName": str,
        "InferenceSchedulerArn": str,
        "Status": InferenceSchedulerStatusType,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

StartRetrainingSchedulerResponseTypeDef = TypedDict(
    "StartRetrainingSchedulerResponseTypeDef",
    {
        "ModelName": str,
        "ModelArn": str,
        "Status": RetrainingSchedulerStatusType,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

StopInferenceSchedulerResponseTypeDef = TypedDict(
    "StopInferenceSchedulerResponseTypeDef",
    {
        "ModelArn": str,
        "ModelName": str,
        "InferenceSchedulerName": str,
        "InferenceSchedulerArn": str,
        "Status": InferenceSchedulerStatusType,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

StopRetrainingSchedulerResponseTypeDef = TypedDict(
    "StopRetrainingSchedulerResponseTypeDef",
    {
        "ModelName": str,
        "ModelArn": str,
        "Status": RetrainingSchedulerStatusType,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

UpdateActiveModelVersionResponseTypeDef = TypedDict(
    "UpdateActiveModelVersionResponseTypeDef",
    {
        "ModelName": str,
        "ModelArn": str,
        "CurrentActiveVersion": int,
        "PreviousActiveVersion": int,
        "CurrentActiveVersionArn": str,
        "PreviousActiveVersionArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateLabelRequestRequestTypeDef = TypedDict(
    "CreateLabelRequestRequestTypeDef",
    {
        "LabelGroupName": str,
        "StartTime": TimestampTypeDef,
        "EndTime": TimestampTypeDef,
        "Rating": LabelRatingType,
        "ClientToken": str,
        "FaultCode": NotRequired[str],
        "Notes": NotRequired[str],
        "Equipment": NotRequired[str],
    },
)

CreateRetrainingSchedulerRequestRequestTypeDef = TypedDict(
    "CreateRetrainingSchedulerRequestRequestTypeDef",
    {
        "ModelName": str,
        "RetrainingFrequency": str,
        "LookbackWindow": str,
        "ClientToken": str,
        "RetrainingStartDate": NotRequired[TimestampTypeDef],
        "PromoteMode": NotRequired[ModelPromoteModeType],
    },
)

ListInferenceEventsRequestRequestTypeDef = TypedDict(
    "ListInferenceEventsRequestRequestTypeDef",
    {
        "InferenceSchedulerName": str,
        "IntervalStartTime": TimestampTypeDef,
        "IntervalEndTime": TimestampTypeDef,
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
    },
)

ListInferenceExecutionsRequestRequestTypeDef = TypedDict(
    "ListInferenceExecutionsRequestRequestTypeDef",
    {
        "InferenceSchedulerName": str,
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
        "DataStartTimeAfter": NotRequired[TimestampTypeDef],
        "DataEndTimeBefore": NotRequired[TimestampTypeDef],
        "Status": NotRequired[InferenceExecutionStatusType],
    },
)

ListLabelsRequestRequestTypeDef = TypedDict(
    "ListLabelsRequestRequestTypeDef",
    {
        "LabelGroupName": str,
        "IntervalStartTime": NotRequired[TimestampTypeDef],
        "IntervalEndTime": NotRequired[TimestampTypeDef],
        "FaultCode": NotRequired[str],
        "Equipment": NotRequired[str],
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
    },
)

ListModelVersionsRequestRequestTypeDef = TypedDict(
    "ListModelVersionsRequestRequestTypeDef",
    {
        "ModelName": str,
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
        "Status": NotRequired[ModelVersionStatusType],
        "SourceType": NotRequired[ModelVersionSourceTypeType],
        "CreatedAtEndTime": NotRequired[TimestampTypeDef],
        "CreatedAtStartTime": NotRequired[TimestampTypeDef],
        "MaxModelVersion": NotRequired[int],
        "MinModelVersion": NotRequired[int],
    },
)

UpdateRetrainingSchedulerRequestRequestTypeDef = TypedDict(
    "UpdateRetrainingSchedulerRequestRequestTypeDef",
    {
        "ModelName": str,
        "RetrainingStartDate": NotRequired[TimestampTypeDef],
        "RetrainingFrequency": NotRequired[str],
        "LookbackWindow": NotRequired[str],
        "PromoteMode": NotRequired[ModelPromoteModeType],
    },
)

ListDatasetsResponseTypeDef = TypedDict(
    "ListDatasetsResponseTypeDef",
    {
        "NextToken": str,
        "DatasetSummaries": List[DatasetSummaryTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListInferenceEventsResponseTypeDef = TypedDict(
    "ListInferenceEventsResponseTypeDef",
    {
        "NextToken": str,
        "InferenceEventSummaries": List[InferenceEventSummaryTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

IngestedFilesSummaryTypeDef = TypedDict(
    "IngestedFilesSummaryTypeDef",
    {
        "TotalNumberOfFiles": int,
        "IngestedNumberOfFiles": int,
        "DiscardedFiles": NotRequired[List[S3ObjectTypeDef]],
    },
)

InferenceInputConfigurationTypeDef = TypedDict(
    "InferenceInputConfigurationTypeDef",
    {
        "S3InputConfiguration": NotRequired[InferenceS3InputConfigurationTypeDef],
        "InputTimeZoneOffset": NotRequired[str],
        "InferenceInputNameConfiguration": NotRequired[InferenceInputNameConfigurationTypeDef],
    },
)

InferenceOutputConfigurationTypeDef = TypedDict(
    "InferenceOutputConfigurationTypeDef",
    {
        "S3OutputConfiguration": InferenceS3OutputConfigurationTypeDef,
        "KmsKeyId": NotRequired[str],
    },
)

ListInferenceSchedulersResponseTypeDef = TypedDict(
    "ListInferenceSchedulersResponseTypeDef",
    {
        "NextToken": str,
        "InferenceSchedulerSummaries": List[InferenceSchedulerSummaryTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

IngestionInputConfigurationTypeDef = TypedDict(
    "IngestionInputConfigurationTypeDef",
    {
        "S3InputConfiguration": IngestionS3InputConfigurationTypeDef,
    },
)

InsufficientSensorDataTypeDef = TypedDict(
    "InsufficientSensorDataTypeDef",
    {
        "MissingCompleteSensorData": MissingCompleteSensorDataTypeDef,
        "SensorsWithShortDateRange": SensorsWithShortDateRangeTypeDef,
    },
)

ListLabelGroupsResponseTypeDef = TypedDict(
    "ListLabelGroupsResponseTypeDef",
    {
        "NextToken": str,
        "LabelGroupSummaries": List[LabelGroupSummaryTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListLabelsResponseTypeDef = TypedDict(
    "ListLabelsResponseTypeDef",
    {
        "NextToken": str,
        "LabelSummaries": List[LabelSummaryTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

LabelsInputConfigurationTypeDef = TypedDict(
    "LabelsInputConfigurationTypeDef",
    {
        "S3InputConfiguration": NotRequired[LabelsS3InputConfigurationTypeDef],
        "LabelGroupName": NotRequired[str],
    },
)

ListModelVersionsResponseTypeDef = TypedDict(
    "ListModelVersionsResponseTypeDef",
    {
        "NextToken": str,
        "ModelVersionSummaries": List[ModelVersionSummaryTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListModelsResponseTypeDef = TypedDict(
    "ListModelsResponseTypeDef",
    {
        "NextToken": str,
        "ModelSummaries": List[ModelSummaryTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListRetrainingSchedulersResponseTypeDef = TypedDict(
    "ListRetrainingSchedulersResponseTypeDef",
    {
        "RetrainingSchedulerSummaries": List[RetrainingSchedulerSummaryTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

SensorStatisticsSummaryTypeDef = TypedDict(
    "SensorStatisticsSummaryTypeDef",
    {
        "ComponentName": NotRequired[str],
        "SensorName": NotRequired[str],
        "DataExists": NotRequired[bool],
        "MissingValues": NotRequired[CountPercentTypeDef],
        "InvalidValues": NotRequired[CountPercentTypeDef],
        "InvalidDateEntries": NotRequired[CountPercentTypeDef],
        "DuplicateTimestamps": NotRequired[CountPercentTypeDef],
        "CategoricalValues": NotRequired[CategoricalValuesTypeDef],
        "MultipleOperatingModes": NotRequired[MultipleOperatingModesTypeDef],
        "LargeTimestampGaps": NotRequired[LargeTimestampGapsTypeDef],
        "MonotonicValues": NotRequired[MonotonicValuesTypeDef],
        "DataStartTime": NotRequired[datetime],
        "DataEndTime": NotRequired[datetime],
    },
)

CreateInferenceSchedulerRequestRequestTypeDef = TypedDict(
    "CreateInferenceSchedulerRequestRequestTypeDef",
    {
        "ModelName": str,
        "InferenceSchedulerName": str,
        "DataUploadFrequency": DataUploadFrequencyType,
        "DataInputConfiguration": InferenceInputConfigurationTypeDef,
        "DataOutputConfiguration": InferenceOutputConfigurationTypeDef,
        "RoleArn": str,
        "ClientToken": str,
        "DataDelayOffsetInMinutes": NotRequired[int],
        "ServerSideKmsKeyId": NotRequired[str],
        "Tags": NotRequired[Sequence[TagTypeDef]],
    },
)

DescribeInferenceSchedulerResponseTypeDef = TypedDict(
    "DescribeInferenceSchedulerResponseTypeDef",
    {
        "ModelArn": str,
        "ModelName": str,
        "InferenceSchedulerName": str,
        "InferenceSchedulerArn": str,
        "Status": InferenceSchedulerStatusType,
        "DataDelayOffsetInMinutes": int,
        "DataUploadFrequency": DataUploadFrequencyType,
        "CreatedAt": datetime,
        "UpdatedAt": datetime,
        "DataInputConfiguration": InferenceInputConfigurationTypeDef,
        "DataOutputConfiguration": InferenceOutputConfigurationTypeDef,
        "RoleArn": str,
        "ServerSideKmsKeyId": str,
        "LatestInferenceResult": LatestInferenceResultType,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

InferenceExecutionSummaryTypeDef = TypedDict(
    "InferenceExecutionSummaryTypeDef",
    {
        "ModelName": NotRequired[str],
        "ModelArn": NotRequired[str],
        "InferenceSchedulerName": NotRequired[str],
        "InferenceSchedulerArn": NotRequired[str],
        "ScheduledStartTime": NotRequired[datetime],
        "DataStartTime": NotRequired[datetime],
        "DataEndTime": NotRequired[datetime],
        "DataInputConfiguration": NotRequired[InferenceInputConfigurationTypeDef],
        "DataOutputConfiguration": NotRequired[InferenceOutputConfigurationTypeDef],
        "CustomerResultObject": NotRequired[S3ObjectTypeDef],
        "Status": NotRequired[InferenceExecutionStatusType],
        "FailedReason": NotRequired[str],
        "ModelVersion": NotRequired[int],
        "ModelVersionArn": NotRequired[str],
    },
)

UpdateInferenceSchedulerRequestRequestTypeDef = TypedDict(
    "UpdateInferenceSchedulerRequestRequestTypeDef",
    {
        "InferenceSchedulerName": str,
        "DataDelayOffsetInMinutes": NotRequired[int],
        "DataUploadFrequency": NotRequired[DataUploadFrequencyType],
        "DataInputConfiguration": NotRequired[InferenceInputConfigurationTypeDef],
        "DataOutputConfiguration": NotRequired[InferenceOutputConfigurationTypeDef],
        "RoleArn": NotRequired[str],
    },
)

DataIngestionJobSummaryTypeDef = TypedDict(
    "DataIngestionJobSummaryTypeDef",
    {
        "JobId": NotRequired[str],
        "DatasetName": NotRequired[str],
        "DatasetArn": NotRequired[str],
        "IngestionInputConfiguration": NotRequired[IngestionInputConfigurationTypeDef],
        "Status": NotRequired[IngestionJobStatusType],
    },
)

StartDataIngestionJobRequestRequestTypeDef = TypedDict(
    "StartDataIngestionJobRequestRequestTypeDef",
    {
        "DatasetName": str,
        "IngestionInputConfiguration": IngestionInputConfigurationTypeDef,
        "RoleArn": str,
        "ClientToken": str,
    },
)

DataQualitySummaryTypeDef = TypedDict(
    "DataQualitySummaryTypeDef",
    {
        "InsufficientSensorData": InsufficientSensorDataTypeDef,
        "MissingSensorData": MissingSensorDataTypeDef,
        "InvalidSensorData": InvalidSensorDataTypeDef,
        "UnsupportedTimestamps": UnsupportedTimestampsTypeDef,
        "DuplicateTimestamps": DuplicateTimestampsTypeDef,
    },
)

CreateModelRequestRequestTypeDef = TypedDict(
    "CreateModelRequestRequestTypeDef",
    {
        "ModelName": str,
        "DatasetName": str,
        "ClientToken": str,
        "DatasetSchema": NotRequired[DatasetSchemaTypeDef],
        "LabelsInputConfiguration": NotRequired[LabelsInputConfigurationTypeDef],
        "TrainingDataStartTime": NotRequired[TimestampTypeDef],
        "TrainingDataEndTime": NotRequired[TimestampTypeDef],
        "EvaluationDataStartTime": NotRequired[TimestampTypeDef],
        "EvaluationDataEndTime": NotRequired[TimestampTypeDef],
        "RoleArn": NotRequired[str],
        "DataPreProcessingConfiguration": NotRequired[DataPreProcessingConfigurationTypeDef],
        "ServerSideKmsKeyId": NotRequired[str],
        "Tags": NotRequired[Sequence[TagTypeDef]],
        "OffCondition": NotRequired[str],
    },
)

DescribeModelResponseTypeDef = TypedDict(
    "DescribeModelResponseTypeDef",
    {
        "ModelName": str,
        "ModelArn": str,
        "DatasetName": str,
        "DatasetArn": str,
        "Schema": str,
        "LabelsInputConfiguration": LabelsInputConfigurationTypeDef,
        "TrainingDataStartTime": datetime,
        "TrainingDataEndTime": datetime,
        "EvaluationDataStartTime": datetime,
        "EvaluationDataEndTime": datetime,
        "RoleArn": str,
        "DataPreProcessingConfiguration": DataPreProcessingConfigurationTypeDef,
        "Status": ModelStatusType,
        "TrainingExecutionStartTime": datetime,
        "TrainingExecutionEndTime": datetime,
        "FailedReason": str,
        "ModelMetrics": str,
        "LastUpdatedTime": datetime,
        "CreatedAt": datetime,
        "ServerSideKmsKeyId": str,
        "OffCondition": str,
        "SourceModelVersionArn": str,
        "ImportJobStartTime": datetime,
        "ImportJobEndTime": datetime,
        "ActiveModelVersion": int,
        "ActiveModelVersionArn": str,
        "ModelVersionActivatedAt": datetime,
        "PreviousActiveModelVersion": int,
        "PreviousActiveModelVersionArn": str,
        "PreviousModelVersionActivatedAt": datetime,
        "PriorModelMetrics": str,
        "LatestScheduledRetrainingFailedReason": str,
        "LatestScheduledRetrainingStatus": ModelVersionStatusType,
        "LatestScheduledRetrainingModelVersion": int,
        "LatestScheduledRetrainingStartTime": datetime,
        "LatestScheduledRetrainingAvailableDataInDays": int,
        "NextScheduledRetrainingStartDate": datetime,
        "AccumulatedInferenceDataStartTime": datetime,
        "AccumulatedInferenceDataEndTime": datetime,
        "RetrainingSchedulerStatus": RetrainingSchedulerStatusType,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeModelVersionResponseTypeDef = TypedDict(
    "DescribeModelVersionResponseTypeDef",
    {
        "ModelName": str,
        "ModelArn": str,
        "ModelVersion": int,
        "ModelVersionArn": str,
        "Status": ModelVersionStatusType,
        "SourceType": ModelVersionSourceTypeType,
        "DatasetName": str,
        "DatasetArn": str,
        "Schema": str,
        "LabelsInputConfiguration": LabelsInputConfigurationTypeDef,
        "TrainingDataStartTime": datetime,
        "TrainingDataEndTime": datetime,
        "EvaluationDataStartTime": datetime,
        "EvaluationDataEndTime": datetime,
        "RoleArn": str,
        "DataPreProcessingConfiguration": DataPreProcessingConfigurationTypeDef,
        "TrainingExecutionStartTime": datetime,
        "TrainingExecutionEndTime": datetime,
        "FailedReason": str,
        "ModelMetrics": str,
        "LastUpdatedTime": datetime,
        "CreatedAt": datetime,
        "ServerSideKmsKeyId": str,
        "OffCondition": str,
        "SourceModelVersionArn": str,
        "ImportJobStartTime": datetime,
        "ImportJobEndTime": datetime,
        "ImportedDataSizeInBytes": int,
        "PriorModelMetrics": str,
        "RetrainingAvailableDataInDays": int,
        "AutoPromotionResult": AutoPromotionResultType,
        "AutoPromotionResultReason": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ImportModelVersionRequestRequestTypeDef = TypedDict(
    "ImportModelVersionRequestRequestTypeDef",
    {
        "SourceModelVersionArn": str,
        "DatasetName": str,
        "ClientToken": str,
        "ModelName": NotRequired[str],
        "LabelsInputConfiguration": NotRequired[LabelsInputConfigurationTypeDef],
        "RoleArn": NotRequired[str],
        "ServerSideKmsKeyId": NotRequired[str],
        "Tags": NotRequired[Sequence[TagTypeDef]],
        "InferenceDataImportStrategy": NotRequired[InferenceDataImportStrategyType],
    },
)

UpdateModelRequestRequestTypeDef = TypedDict(
    "UpdateModelRequestRequestTypeDef",
    {
        "ModelName": str,
        "LabelsInputConfiguration": NotRequired[LabelsInputConfigurationTypeDef],
        "RoleArn": NotRequired[str],
    },
)

ListSensorStatisticsResponseTypeDef = TypedDict(
    "ListSensorStatisticsResponseTypeDef",
    {
        "SensorStatisticsSummaries": List[SensorStatisticsSummaryTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListInferenceExecutionsResponseTypeDef = TypedDict(
    "ListInferenceExecutionsResponseTypeDef",
    {
        "NextToken": str,
        "InferenceExecutionSummaries": List[InferenceExecutionSummaryTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListDataIngestionJobsResponseTypeDef = TypedDict(
    "ListDataIngestionJobsResponseTypeDef",
    {
        "NextToken": str,
        "DataIngestionJobSummaries": List[DataIngestionJobSummaryTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeDataIngestionJobResponseTypeDef = TypedDict(
    "DescribeDataIngestionJobResponseTypeDef",
    {
        "JobId": str,
        "DatasetArn": str,
        "IngestionInputConfiguration": IngestionInputConfigurationTypeDef,
        "RoleArn": str,
        "CreatedAt": datetime,
        "Status": IngestionJobStatusType,
        "FailedReason": str,
        "DataQualitySummary": DataQualitySummaryTypeDef,
        "IngestedFilesSummary": IngestedFilesSummaryTypeDef,
        "StatusDetail": str,
        "IngestedDataSize": int,
        "DataStartTime": datetime,
        "DataEndTime": datetime,
        "SourceDatasetArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeDatasetResponseTypeDef = TypedDict(
    "DescribeDatasetResponseTypeDef",
    {
        "DatasetName": str,
        "DatasetArn": str,
        "CreatedAt": datetime,
        "LastUpdatedAt": datetime,
        "Status": DatasetStatusType,
        "Schema": str,
        "ServerSideKmsKeyId": str,
        "IngestionInputConfiguration": IngestionInputConfigurationTypeDef,
        "DataQualitySummary": DataQualitySummaryTypeDef,
        "IngestedFilesSummary": IngestedFilesSummaryTypeDef,
        "RoleArn": str,
        "DataStartTime": datetime,
        "DataEndTime": datetime,
        "SourceDatasetArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
