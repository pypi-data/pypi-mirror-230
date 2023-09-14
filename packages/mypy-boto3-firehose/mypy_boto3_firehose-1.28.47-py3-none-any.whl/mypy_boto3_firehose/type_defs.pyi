"""
Type annotations for firehose service type definitions.

[Open documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_firehose/type_defs/)

Usage::

    ```python
    from mypy_boto3_firehose.type_defs import AmazonOpenSearchServerlessBufferingHintsTypeDef

    data: AmazonOpenSearchServerlessBufferingHintsTypeDef = ...
    ```
"""
import sys
from datetime import datetime
from typing import IO, Any, Dict, List, Mapping, Sequence, Union

from botocore.response import StreamingBody

from .literals import (
    AmazonOpenSearchServerlessS3BackupModeType,
    AmazonopensearchserviceIndexRotationPeriodType,
    AmazonopensearchserviceS3BackupModeType,
    CompressionFormatType,
    ContentEncodingType,
    DefaultDocumentIdFormatType,
    DeliveryStreamEncryptionStatusType,
    DeliveryStreamFailureTypeType,
    DeliveryStreamStatusType,
    DeliveryStreamTypeType,
    ElasticsearchIndexRotationPeriodType,
    ElasticsearchS3BackupModeType,
    HECEndpointTypeType,
    HttpEndpointS3BackupModeType,
    KeyTypeType,
    OrcCompressionType,
    OrcFormatVersionType,
    ParquetCompressionType,
    ParquetWriterVersionType,
    ProcessorParameterNameType,
    ProcessorTypeType,
    RedshiftS3BackupModeType,
    S3BackupModeType,
    SplunkS3BackupModeType,
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
    "AmazonOpenSearchServerlessBufferingHintsTypeDef",
    "AmazonOpenSearchServerlessRetryOptionsTypeDef",
    "CloudWatchLoggingOptionsTypeDef",
    "VpcConfigurationTypeDef",
    "VpcConfigurationDescriptionTypeDef",
    "AmazonopensearchserviceBufferingHintsTypeDef",
    "AmazonopensearchserviceRetryOptionsTypeDef",
    "DocumentIdOptionsTypeDef",
    "BlobTypeDef",
    "BufferingHintsTypeDef",
    "CopyCommandTypeDef",
    "DeliveryStreamEncryptionConfigurationInputTypeDef",
    "KinesisStreamSourceConfigurationTypeDef",
    "TagTypeDef",
    "ResponseMetadataTypeDef",
    "SchemaConfigurationTypeDef",
    "DeleteDeliveryStreamInputRequestTypeDef",
    "FailureDescriptionTypeDef",
    "DescribeDeliveryStreamInputRequestTypeDef",
    "HiveJsonSerDeTypeDef",
    "OpenXJsonSerDeTypeDef",
    "RetryOptionsTypeDef",
    "ElasticsearchBufferingHintsTypeDef",
    "ElasticsearchRetryOptionsTypeDef",
    "KMSEncryptionConfigTypeDef",
    "HttpEndpointBufferingHintsTypeDef",
    "HttpEndpointCommonAttributeTypeDef",
    "HttpEndpointConfigurationTypeDef",
    "HttpEndpointDescriptionTypeDef",
    "HttpEndpointRetryOptionsTypeDef",
    "KinesisStreamSourceDescriptionTypeDef",
    "ListDeliveryStreamsInputRequestTypeDef",
    "ListTagsForDeliveryStreamInputRequestTypeDef",
    "OrcSerDeTypeDef",
    "ParquetSerDeTypeDef",
    "ProcessorParameterTypeDef",
    "PutRecordBatchResponseEntryTypeDef",
    "RedshiftRetryOptionsTypeDef",
    "SplunkRetryOptionsTypeDef",
    "StopDeliveryStreamEncryptionInputRequestTypeDef",
    "UntagDeliveryStreamInputRequestTypeDef",
    "RecordTypeDef",
    "StartDeliveryStreamEncryptionInputRequestTypeDef",
    "TagDeliveryStreamInputRequestTypeDef",
    "CreateDeliveryStreamOutputTypeDef",
    "ListDeliveryStreamsOutputTypeDef",
    "ListTagsForDeliveryStreamOutputTypeDef",
    "PutRecordOutputTypeDef",
    "DeliveryStreamEncryptionConfigurationTypeDef",
    "DeserializerTypeDef",
    "DynamicPartitioningConfigurationTypeDef",
    "EncryptionConfigurationTypeDef",
    "HttpEndpointRequestConfigurationTypeDef",
    "SourceDescriptionTypeDef",
    "SerializerTypeDef",
    "ProcessorTypeDef",
    "PutRecordBatchOutputTypeDef",
    "PutRecordBatchInputRequestTypeDef",
    "PutRecordInputRequestTypeDef",
    "InputFormatConfigurationTypeDef",
    "S3DestinationConfigurationTypeDef",
    "S3DestinationDescriptionTypeDef",
    "S3DestinationUpdateTypeDef",
    "OutputFormatConfigurationTypeDef",
    "ProcessingConfigurationTypeDef",
    "DataFormatConversionConfigurationTypeDef",
    "AmazonOpenSearchServerlessDestinationConfigurationTypeDef",
    "AmazonOpenSearchServerlessDestinationDescriptionTypeDef",
    "AmazonOpenSearchServerlessDestinationUpdateTypeDef",
    "AmazonopensearchserviceDestinationConfigurationTypeDef",
    "AmazonopensearchserviceDestinationDescriptionTypeDef",
    "AmazonopensearchserviceDestinationUpdateTypeDef",
    "ElasticsearchDestinationConfigurationTypeDef",
    "ElasticsearchDestinationDescriptionTypeDef",
    "ElasticsearchDestinationUpdateTypeDef",
    "HttpEndpointDestinationConfigurationTypeDef",
    "HttpEndpointDestinationDescriptionTypeDef",
    "HttpEndpointDestinationUpdateTypeDef",
    "RedshiftDestinationConfigurationTypeDef",
    "RedshiftDestinationDescriptionTypeDef",
    "RedshiftDestinationUpdateTypeDef",
    "SplunkDestinationConfigurationTypeDef",
    "SplunkDestinationDescriptionTypeDef",
    "SplunkDestinationUpdateTypeDef",
    "ExtendedS3DestinationConfigurationTypeDef",
    "ExtendedS3DestinationDescriptionTypeDef",
    "ExtendedS3DestinationUpdateTypeDef",
    "CreateDeliveryStreamInputRequestTypeDef",
    "DestinationDescriptionTypeDef",
    "UpdateDestinationInputRequestTypeDef",
    "DeliveryStreamDescriptionTypeDef",
    "DescribeDeliveryStreamOutputTypeDef",
)

AmazonOpenSearchServerlessBufferingHintsTypeDef = TypedDict(
    "AmazonOpenSearchServerlessBufferingHintsTypeDef",
    {
        "IntervalInSeconds": NotRequired[int],
        "SizeInMBs": NotRequired[int],
    },
)

AmazonOpenSearchServerlessRetryOptionsTypeDef = TypedDict(
    "AmazonOpenSearchServerlessRetryOptionsTypeDef",
    {
        "DurationInSeconds": NotRequired[int],
    },
)

CloudWatchLoggingOptionsTypeDef = TypedDict(
    "CloudWatchLoggingOptionsTypeDef",
    {
        "Enabled": NotRequired[bool],
        "LogGroupName": NotRequired[str],
        "LogStreamName": NotRequired[str],
    },
)

VpcConfigurationTypeDef = TypedDict(
    "VpcConfigurationTypeDef",
    {
        "SubnetIds": Sequence[str],
        "RoleARN": str,
        "SecurityGroupIds": Sequence[str],
    },
)

VpcConfigurationDescriptionTypeDef = TypedDict(
    "VpcConfigurationDescriptionTypeDef",
    {
        "SubnetIds": List[str],
        "RoleARN": str,
        "SecurityGroupIds": List[str],
        "VpcId": str,
    },
)

AmazonopensearchserviceBufferingHintsTypeDef = TypedDict(
    "AmazonopensearchserviceBufferingHintsTypeDef",
    {
        "IntervalInSeconds": NotRequired[int],
        "SizeInMBs": NotRequired[int],
    },
)

AmazonopensearchserviceRetryOptionsTypeDef = TypedDict(
    "AmazonopensearchserviceRetryOptionsTypeDef",
    {
        "DurationInSeconds": NotRequired[int],
    },
)

DocumentIdOptionsTypeDef = TypedDict(
    "DocumentIdOptionsTypeDef",
    {
        "DefaultDocumentIdFormat": DefaultDocumentIdFormatType,
    },
)

BlobTypeDef = Union[str, bytes, IO[Any], StreamingBody]
BufferingHintsTypeDef = TypedDict(
    "BufferingHintsTypeDef",
    {
        "SizeInMBs": NotRequired[int],
        "IntervalInSeconds": NotRequired[int],
    },
)

CopyCommandTypeDef = TypedDict(
    "CopyCommandTypeDef",
    {
        "DataTableName": str,
        "DataTableColumns": NotRequired[str],
        "CopyOptions": NotRequired[str],
    },
)

DeliveryStreamEncryptionConfigurationInputTypeDef = TypedDict(
    "DeliveryStreamEncryptionConfigurationInputTypeDef",
    {
        "KeyType": KeyTypeType,
        "KeyARN": NotRequired[str],
    },
)

KinesisStreamSourceConfigurationTypeDef = TypedDict(
    "KinesisStreamSourceConfigurationTypeDef",
    {
        "KinesisStreamARN": str,
        "RoleARN": str,
    },
)

TagTypeDef = TypedDict(
    "TagTypeDef",
    {
        "Key": str,
        "Value": NotRequired[str],
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

SchemaConfigurationTypeDef = TypedDict(
    "SchemaConfigurationTypeDef",
    {
        "RoleARN": NotRequired[str],
        "CatalogId": NotRequired[str],
        "DatabaseName": NotRequired[str],
        "TableName": NotRequired[str],
        "Region": NotRequired[str],
        "VersionId": NotRequired[str],
    },
)

DeleteDeliveryStreamInputRequestTypeDef = TypedDict(
    "DeleteDeliveryStreamInputRequestTypeDef",
    {
        "DeliveryStreamName": str,
        "AllowForceDelete": NotRequired[bool],
    },
)

FailureDescriptionTypeDef = TypedDict(
    "FailureDescriptionTypeDef",
    {
        "Type": DeliveryStreamFailureTypeType,
        "Details": str,
    },
)

DescribeDeliveryStreamInputRequestTypeDef = TypedDict(
    "DescribeDeliveryStreamInputRequestTypeDef",
    {
        "DeliveryStreamName": str,
        "Limit": NotRequired[int],
        "ExclusiveStartDestinationId": NotRequired[str],
    },
)

HiveJsonSerDeTypeDef = TypedDict(
    "HiveJsonSerDeTypeDef",
    {
        "TimestampFormats": NotRequired[Sequence[str]],
    },
)

OpenXJsonSerDeTypeDef = TypedDict(
    "OpenXJsonSerDeTypeDef",
    {
        "ConvertDotsInJsonKeysToUnderscores": NotRequired[bool],
        "CaseInsensitive": NotRequired[bool],
        "ColumnToJsonKeyMappings": NotRequired[Mapping[str, str]],
    },
)

RetryOptionsTypeDef = TypedDict(
    "RetryOptionsTypeDef",
    {
        "DurationInSeconds": NotRequired[int],
    },
)

ElasticsearchBufferingHintsTypeDef = TypedDict(
    "ElasticsearchBufferingHintsTypeDef",
    {
        "IntervalInSeconds": NotRequired[int],
        "SizeInMBs": NotRequired[int],
    },
)

ElasticsearchRetryOptionsTypeDef = TypedDict(
    "ElasticsearchRetryOptionsTypeDef",
    {
        "DurationInSeconds": NotRequired[int],
    },
)

KMSEncryptionConfigTypeDef = TypedDict(
    "KMSEncryptionConfigTypeDef",
    {
        "AWSKMSKeyARN": str,
    },
)

HttpEndpointBufferingHintsTypeDef = TypedDict(
    "HttpEndpointBufferingHintsTypeDef",
    {
        "SizeInMBs": NotRequired[int],
        "IntervalInSeconds": NotRequired[int],
    },
)

HttpEndpointCommonAttributeTypeDef = TypedDict(
    "HttpEndpointCommonAttributeTypeDef",
    {
        "AttributeName": str,
        "AttributeValue": str,
    },
)

HttpEndpointConfigurationTypeDef = TypedDict(
    "HttpEndpointConfigurationTypeDef",
    {
        "Url": str,
        "Name": NotRequired[str],
        "AccessKey": NotRequired[str],
    },
)

HttpEndpointDescriptionTypeDef = TypedDict(
    "HttpEndpointDescriptionTypeDef",
    {
        "Url": NotRequired[str],
        "Name": NotRequired[str],
    },
)

HttpEndpointRetryOptionsTypeDef = TypedDict(
    "HttpEndpointRetryOptionsTypeDef",
    {
        "DurationInSeconds": NotRequired[int],
    },
)

KinesisStreamSourceDescriptionTypeDef = TypedDict(
    "KinesisStreamSourceDescriptionTypeDef",
    {
        "KinesisStreamARN": NotRequired[str],
        "RoleARN": NotRequired[str],
        "DeliveryStartTimestamp": NotRequired[datetime],
    },
)

ListDeliveryStreamsInputRequestTypeDef = TypedDict(
    "ListDeliveryStreamsInputRequestTypeDef",
    {
        "Limit": NotRequired[int],
        "DeliveryStreamType": NotRequired[DeliveryStreamTypeType],
        "ExclusiveStartDeliveryStreamName": NotRequired[str],
    },
)

ListTagsForDeliveryStreamInputRequestTypeDef = TypedDict(
    "ListTagsForDeliveryStreamInputRequestTypeDef",
    {
        "DeliveryStreamName": str,
        "ExclusiveStartTagKey": NotRequired[str],
        "Limit": NotRequired[int],
    },
)

OrcSerDeTypeDef = TypedDict(
    "OrcSerDeTypeDef",
    {
        "StripeSizeBytes": NotRequired[int],
        "BlockSizeBytes": NotRequired[int],
        "RowIndexStride": NotRequired[int],
        "EnablePadding": NotRequired[bool],
        "PaddingTolerance": NotRequired[float],
        "Compression": NotRequired[OrcCompressionType],
        "BloomFilterColumns": NotRequired[Sequence[str]],
        "BloomFilterFalsePositiveProbability": NotRequired[float],
        "DictionaryKeyThreshold": NotRequired[float],
        "FormatVersion": NotRequired[OrcFormatVersionType],
    },
)

ParquetSerDeTypeDef = TypedDict(
    "ParquetSerDeTypeDef",
    {
        "BlockSizeBytes": NotRequired[int],
        "PageSizeBytes": NotRequired[int],
        "Compression": NotRequired[ParquetCompressionType],
        "EnableDictionaryCompression": NotRequired[bool],
        "MaxPaddingBytes": NotRequired[int],
        "WriterVersion": NotRequired[ParquetWriterVersionType],
    },
)

ProcessorParameterTypeDef = TypedDict(
    "ProcessorParameterTypeDef",
    {
        "ParameterName": ProcessorParameterNameType,
        "ParameterValue": str,
    },
)

PutRecordBatchResponseEntryTypeDef = TypedDict(
    "PutRecordBatchResponseEntryTypeDef",
    {
        "RecordId": NotRequired[str],
        "ErrorCode": NotRequired[str],
        "ErrorMessage": NotRequired[str],
    },
)

RedshiftRetryOptionsTypeDef = TypedDict(
    "RedshiftRetryOptionsTypeDef",
    {
        "DurationInSeconds": NotRequired[int],
    },
)

SplunkRetryOptionsTypeDef = TypedDict(
    "SplunkRetryOptionsTypeDef",
    {
        "DurationInSeconds": NotRequired[int],
    },
)

StopDeliveryStreamEncryptionInputRequestTypeDef = TypedDict(
    "StopDeliveryStreamEncryptionInputRequestTypeDef",
    {
        "DeliveryStreamName": str,
    },
)

UntagDeliveryStreamInputRequestTypeDef = TypedDict(
    "UntagDeliveryStreamInputRequestTypeDef",
    {
        "DeliveryStreamName": str,
        "TagKeys": Sequence[str],
    },
)

RecordTypeDef = TypedDict(
    "RecordTypeDef",
    {
        "Data": BlobTypeDef,
    },
)

StartDeliveryStreamEncryptionInputRequestTypeDef = TypedDict(
    "StartDeliveryStreamEncryptionInputRequestTypeDef",
    {
        "DeliveryStreamName": str,
        "DeliveryStreamEncryptionConfigurationInput": NotRequired[
            DeliveryStreamEncryptionConfigurationInputTypeDef
        ],
    },
)

TagDeliveryStreamInputRequestTypeDef = TypedDict(
    "TagDeliveryStreamInputRequestTypeDef",
    {
        "DeliveryStreamName": str,
        "Tags": Sequence[TagTypeDef],
    },
)

CreateDeliveryStreamOutputTypeDef = TypedDict(
    "CreateDeliveryStreamOutputTypeDef",
    {
        "DeliveryStreamARN": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListDeliveryStreamsOutputTypeDef = TypedDict(
    "ListDeliveryStreamsOutputTypeDef",
    {
        "DeliveryStreamNames": List[str],
        "HasMoreDeliveryStreams": bool,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListTagsForDeliveryStreamOutputTypeDef = TypedDict(
    "ListTagsForDeliveryStreamOutputTypeDef",
    {
        "Tags": List[TagTypeDef],
        "HasMoreTags": bool,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

PutRecordOutputTypeDef = TypedDict(
    "PutRecordOutputTypeDef",
    {
        "RecordId": str,
        "Encrypted": bool,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DeliveryStreamEncryptionConfigurationTypeDef = TypedDict(
    "DeliveryStreamEncryptionConfigurationTypeDef",
    {
        "KeyARN": NotRequired[str],
        "KeyType": NotRequired[KeyTypeType],
        "Status": NotRequired[DeliveryStreamEncryptionStatusType],
        "FailureDescription": NotRequired[FailureDescriptionTypeDef],
    },
)

DeserializerTypeDef = TypedDict(
    "DeserializerTypeDef",
    {
        "OpenXJsonSerDe": NotRequired[OpenXJsonSerDeTypeDef],
        "HiveJsonSerDe": NotRequired[HiveJsonSerDeTypeDef],
    },
)

DynamicPartitioningConfigurationTypeDef = TypedDict(
    "DynamicPartitioningConfigurationTypeDef",
    {
        "RetryOptions": NotRequired[RetryOptionsTypeDef],
        "Enabled": NotRequired[bool],
    },
)

EncryptionConfigurationTypeDef = TypedDict(
    "EncryptionConfigurationTypeDef",
    {
        "NoEncryptionConfig": NotRequired[Literal["NoEncryption"]],
        "KMSEncryptionConfig": NotRequired[KMSEncryptionConfigTypeDef],
    },
)

HttpEndpointRequestConfigurationTypeDef = TypedDict(
    "HttpEndpointRequestConfigurationTypeDef",
    {
        "ContentEncoding": NotRequired[ContentEncodingType],
        "CommonAttributes": NotRequired[Sequence[HttpEndpointCommonAttributeTypeDef]],
    },
)

SourceDescriptionTypeDef = TypedDict(
    "SourceDescriptionTypeDef",
    {
        "KinesisStreamSourceDescription": NotRequired[KinesisStreamSourceDescriptionTypeDef],
    },
)

SerializerTypeDef = TypedDict(
    "SerializerTypeDef",
    {
        "ParquetSerDe": NotRequired[ParquetSerDeTypeDef],
        "OrcSerDe": NotRequired[OrcSerDeTypeDef],
    },
)

ProcessorTypeDef = TypedDict(
    "ProcessorTypeDef",
    {
        "Type": ProcessorTypeType,
        "Parameters": NotRequired[Sequence[ProcessorParameterTypeDef]],
    },
)

PutRecordBatchOutputTypeDef = TypedDict(
    "PutRecordBatchOutputTypeDef",
    {
        "FailedPutCount": int,
        "Encrypted": bool,
        "RequestResponses": List[PutRecordBatchResponseEntryTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

PutRecordBatchInputRequestTypeDef = TypedDict(
    "PutRecordBatchInputRequestTypeDef",
    {
        "DeliveryStreamName": str,
        "Records": Sequence[RecordTypeDef],
    },
)

PutRecordInputRequestTypeDef = TypedDict(
    "PutRecordInputRequestTypeDef",
    {
        "DeliveryStreamName": str,
        "Record": RecordTypeDef,
    },
)

InputFormatConfigurationTypeDef = TypedDict(
    "InputFormatConfigurationTypeDef",
    {
        "Deserializer": NotRequired[DeserializerTypeDef],
    },
)

S3DestinationConfigurationTypeDef = TypedDict(
    "S3DestinationConfigurationTypeDef",
    {
        "RoleARN": str,
        "BucketARN": str,
        "Prefix": NotRequired[str],
        "ErrorOutputPrefix": NotRequired[str],
        "BufferingHints": NotRequired[BufferingHintsTypeDef],
        "CompressionFormat": NotRequired[CompressionFormatType],
        "EncryptionConfiguration": NotRequired[EncryptionConfigurationTypeDef],
        "CloudWatchLoggingOptions": NotRequired[CloudWatchLoggingOptionsTypeDef],
    },
)

S3DestinationDescriptionTypeDef = TypedDict(
    "S3DestinationDescriptionTypeDef",
    {
        "RoleARN": str,
        "BucketARN": str,
        "BufferingHints": BufferingHintsTypeDef,
        "CompressionFormat": CompressionFormatType,
        "EncryptionConfiguration": EncryptionConfigurationTypeDef,
        "Prefix": NotRequired[str],
        "ErrorOutputPrefix": NotRequired[str],
        "CloudWatchLoggingOptions": NotRequired[CloudWatchLoggingOptionsTypeDef],
    },
)

S3DestinationUpdateTypeDef = TypedDict(
    "S3DestinationUpdateTypeDef",
    {
        "RoleARN": NotRequired[str],
        "BucketARN": NotRequired[str],
        "Prefix": NotRequired[str],
        "ErrorOutputPrefix": NotRequired[str],
        "BufferingHints": NotRequired[BufferingHintsTypeDef],
        "CompressionFormat": NotRequired[CompressionFormatType],
        "EncryptionConfiguration": NotRequired[EncryptionConfigurationTypeDef],
        "CloudWatchLoggingOptions": NotRequired[CloudWatchLoggingOptionsTypeDef],
    },
)

OutputFormatConfigurationTypeDef = TypedDict(
    "OutputFormatConfigurationTypeDef",
    {
        "Serializer": NotRequired[SerializerTypeDef],
    },
)

ProcessingConfigurationTypeDef = TypedDict(
    "ProcessingConfigurationTypeDef",
    {
        "Enabled": NotRequired[bool],
        "Processors": NotRequired[Sequence[ProcessorTypeDef]],
    },
)

DataFormatConversionConfigurationTypeDef = TypedDict(
    "DataFormatConversionConfigurationTypeDef",
    {
        "SchemaConfiguration": NotRequired[SchemaConfigurationTypeDef],
        "InputFormatConfiguration": NotRequired[InputFormatConfigurationTypeDef],
        "OutputFormatConfiguration": NotRequired[OutputFormatConfigurationTypeDef],
        "Enabled": NotRequired[bool],
    },
)

AmazonOpenSearchServerlessDestinationConfigurationTypeDef = TypedDict(
    "AmazonOpenSearchServerlessDestinationConfigurationTypeDef",
    {
        "RoleARN": str,
        "IndexName": str,
        "S3Configuration": S3DestinationConfigurationTypeDef,
        "CollectionEndpoint": NotRequired[str],
        "BufferingHints": NotRequired[AmazonOpenSearchServerlessBufferingHintsTypeDef],
        "RetryOptions": NotRequired[AmazonOpenSearchServerlessRetryOptionsTypeDef],
        "S3BackupMode": NotRequired[AmazonOpenSearchServerlessS3BackupModeType],
        "ProcessingConfiguration": NotRequired[ProcessingConfigurationTypeDef],
        "CloudWatchLoggingOptions": NotRequired[CloudWatchLoggingOptionsTypeDef],
        "VpcConfiguration": NotRequired[VpcConfigurationTypeDef],
    },
)

AmazonOpenSearchServerlessDestinationDescriptionTypeDef = TypedDict(
    "AmazonOpenSearchServerlessDestinationDescriptionTypeDef",
    {
        "RoleARN": NotRequired[str],
        "CollectionEndpoint": NotRequired[str],
        "IndexName": NotRequired[str],
        "BufferingHints": NotRequired[AmazonOpenSearchServerlessBufferingHintsTypeDef],
        "RetryOptions": NotRequired[AmazonOpenSearchServerlessRetryOptionsTypeDef],
        "S3BackupMode": NotRequired[AmazonOpenSearchServerlessS3BackupModeType],
        "S3DestinationDescription": NotRequired[S3DestinationDescriptionTypeDef],
        "ProcessingConfiguration": NotRequired[ProcessingConfigurationTypeDef],
        "CloudWatchLoggingOptions": NotRequired[CloudWatchLoggingOptionsTypeDef],
        "VpcConfigurationDescription": NotRequired[VpcConfigurationDescriptionTypeDef],
    },
)

AmazonOpenSearchServerlessDestinationUpdateTypeDef = TypedDict(
    "AmazonOpenSearchServerlessDestinationUpdateTypeDef",
    {
        "RoleARN": NotRequired[str],
        "CollectionEndpoint": NotRequired[str],
        "IndexName": NotRequired[str],
        "BufferingHints": NotRequired[AmazonOpenSearchServerlessBufferingHintsTypeDef],
        "RetryOptions": NotRequired[AmazonOpenSearchServerlessRetryOptionsTypeDef],
        "S3Update": NotRequired[S3DestinationUpdateTypeDef],
        "ProcessingConfiguration": NotRequired[ProcessingConfigurationTypeDef],
        "CloudWatchLoggingOptions": NotRequired[CloudWatchLoggingOptionsTypeDef],
    },
)

AmazonopensearchserviceDestinationConfigurationTypeDef = TypedDict(
    "AmazonopensearchserviceDestinationConfigurationTypeDef",
    {
        "RoleARN": str,
        "IndexName": str,
        "S3Configuration": S3DestinationConfigurationTypeDef,
        "DomainARN": NotRequired[str],
        "ClusterEndpoint": NotRequired[str],
        "TypeName": NotRequired[str],
        "IndexRotationPeriod": NotRequired[AmazonopensearchserviceIndexRotationPeriodType],
        "BufferingHints": NotRequired[AmazonopensearchserviceBufferingHintsTypeDef],
        "RetryOptions": NotRequired[AmazonopensearchserviceRetryOptionsTypeDef],
        "S3BackupMode": NotRequired[AmazonopensearchserviceS3BackupModeType],
        "ProcessingConfiguration": NotRequired[ProcessingConfigurationTypeDef],
        "CloudWatchLoggingOptions": NotRequired[CloudWatchLoggingOptionsTypeDef],
        "VpcConfiguration": NotRequired[VpcConfigurationTypeDef],
        "DocumentIdOptions": NotRequired[DocumentIdOptionsTypeDef],
    },
)

AmazonopensearchserviceDestinationDescriptionTypeDef = TypedDict(
    "AmazonopensearchserviceDestinationDescriptionTypeDef",
    {
        "RoleARN": NotRequired[str],
        "DomainARN": NotRequired[str],
        "ClusterEndpoint": NotRequired[str],
        "IndexName": NotRequired[str],
        "TypeName": NotRequired[str],
        "IndexRotationPeriod": NotRequired[AmazonopensearchserviceIndexRotationPeriodType],
        "BufferingHints": NotRequired[AmazonopensearchserviceBufferingHintsTypeDef],
        "RetryOptions": NotRequired[AmazonopensearchserviceRetryOptionsTypeDef],
        "S3BackupMode": NotRequired[AmazonopensearchserviceS3BackupModeType],
        "S3DestinationDescription": NotRequired[S3DestinationDescriptionTypeDef],
        "ProcessingConfiguration": NotRequired[ProcessingConfigurationTypeDef],
        "CloudWatchLoggingOptions": NotRequired[CloudWatchLoggingOptionsTypeDef],
        "VpcConfigurationDescription": NotRequired[VpcConfigurationDescriptionTypeDef],
        "DocumentIdOptions": NotRequired[DocumentIdOptionsTypeDef],
    },
)

AmazonopensearchserviceDestinationUpdateTypeDef = TypedDict(
    "AmazonopensearchserviceDestinationUpdateTypeDef",
    {
        "RoleARN": NotRequired[str],
        "DomainARN": NotRequired[str],
        "ClusterEndpoint": NotRequired[str],
        "IndexName": NotRequired[str],
        "TypeName": NotRequired[str],
        "IndexRotationPeriod": NotRequired[AmazonopensearchserviceIndexRotationPeriodType],
        "BufferingHints": NotRequired[AmazonopensearchserviceBufferingHintsTypeDef],
        "RetryOptions": NotRequired[AmazonopensearchserviceRetryOptionsTypeDef],
        "S3Update": NotRequired[S3DestinationUpdateTypeDef],
        "ProcessingConfiguration": NotRequired[ProcessingConfigurationTypeDef],
        "CloudWatchLoggingOptions": NotRequired[CloudWatchLoggingOptionsTypeDef],
        "DocumentIdOptions": NotRequired[DocumentIdOptionsTypeDef],
    },
)

ElasticsearchDestinationConfigurationTypeDef = TypedDict(
    "ElasticsearchDestinationConfigurationTypeDef",
    {
        "RoleARN": str,
        "IndexName": str,
        "S3Configuration": S3DestinationConfigurationTypeDef,
        "DomainARN": NotRequired[str],
        "ClusterEndpoint": NotRequired[str],
        "TypeName": NotRequired[str],
        "IndexRotationPeriod": NotRequired[ElasticsearchIndexRotationPeriodType],
        "BufferingHints": NotRequired[ElasticsearchBufferingHintsTypeDef],
        "RetryOptions": NotRequired[ElasticsearchRetryOptionsTypeDef],
        "S3BackupMode": NotRequired[ElasticsearchS3BackupModeType],
        "ProcessingConfiguration": NotRequired[ProcessingConfigurationTypeDef],
        "CloudWatchLoggingOptions": NotRequired[CloudWatchLoggingOptionsTypeDef],
        "VpcConfiguration": NotRequired[VpcConfigurationTypeDef],
        "DocumentIdOptions": NotRequired[DocumentIdOptionsTypeDef],
    },
)

ElasticsearchDestinationDescriptionTypeDef = TypedDict(
    "ElasticsearchDestinationDescriptionTypeDef",
    {
        "RoleARN": NotRequired[str],
        "DomainARN": NotRequired[str],
        "ClusterEndpoint": NotRequired[str],
        "IndexName": NotRequired[str],
        "TypeName": NotRequired[str],
        "IndexRotationPeriod": NotRequired[ElasticsearchIndexRotationPeriodType],
        "BufferingHints": NotRequired[ElasticsearchBufferingHintsTypeDef],
        "RetryOptions": NotRequired[ElasticsearchRetryOptionsTypeDef],
        "S3BackupMode": NotRequired[ElasticsearchS3BackupModeType],
        "S3DestinationDescription": NotRequired[S3DestinationDescriptionTypeDef],
        "ProcessingConfiguration": NotRequired[ProcessingConfigurationTypeDef],
        "CloudWatchLoggingOptions": NotRequired[CloudWatchLoggingOptionsTypeDef],
        "VpcConfigurationDescription": NotRequired[VpcConfigurationDescriptionTypeDef],
        "DocumentIdOptions": NotRequired[DocumentIdOptionsTypeDef],
    },
)

ElasticsearchDestinationUpdateTypeDef = TypedDict(
    "ElasticsearchDestinationUpdateTypeDef",
    {
        "RoleARN": NotRequired[str],
        "DomainARN": NotRequired[str],
        "ClusterEndpoint": NotRequired[str],
        "IndexName": NotRequired[str],
        "TypeName": NotRequired[str],
        "IndexRotationPeriod": NotRequired[ElasticsearchIndexRotationPeriodType],
        "BufferingHints": NotRequired[ElasticsearchBufferingHintsTypeDef],
        "RetryOptions": NotRequired[ElasticsearchRetryOptionsTypeDef],
        "S3Update": NotRequired[S3DestinationUpdateTypeDef],
        "ProcessingConfiguration": NotRequired[ProcessingConfigurationTypeDef],
        "CloudWatchLoggingOptions": NotRequired[CloudWatchLoggingOptionsTypeDef],
        "DocumentIdOptions": NotRequired[DocumentIdOptionsTypeDef],
    },
)

HttpEndpointDestinationConfigurationTypeDef = TypedDict(
    "HttpEndpointDestinationConfigurationTypeDef",
    {
        "EndpointConfiguration": HttpEndpointConfigurationTypeDef,
        "S3Configuration": S3DestinationConfigurationTypeDef,
        "BufferingHints": NotRequired[HttpEndpointBufferingHintsTypeDef],
        "CloudWatchLoggingOptions": NotRequired[CloudWatchLoggingOptionsTypeDef],
        "RequestConfiguration": NotRequired[HttpEndpointRequestConfigurationTypeDef],
        "ProcessingConfiguration": NotRequired[ProcessingConfigurationTypeDef],
        "RoleARN": NotRequired[str],
        "RetryOptions": NotRequired[HttpEndpointRetryOptionsTypeDef],
        "S3BackupMode": NotRequired[HttpEndpointS3BackupModeType],
    },
)

HttpEndpointDestinationDescriptionTypeDef = TypedDict(
    "HttpEndpointDestinationDescriptionTypeDef",
    {
        "EndpointConfiguration": NotRequired[HttpEndpointDescriptionTypeDef],
        "BufferingHints": NotRequired[HttpEndpointBufferingHintsTypeDef],
        "CloudWatchLoggingOptions": NotRequired[CloudWatchLoggingOptionsTypeDef],
        "RequestConfiguration": NotRequired[HttpEndpointRequestConfigurationTypeDef],
        "ProcessingConfiguration": NotRequired[ProcessingConfigurationTypeDef],
        "RoleARN": NotRequired[str],
        "RetryOptions": NotRequired[HttpEndpointRetryOptionsTypeDef],
        "S3BackupMode": NotRequired[HttpEndpointS3BackupModeType],
        "S3DestinationDescription": NotRequired[S3DestinationDescriptionTypeDef],
    },
)

HttpEndpointDestinationUpdateTypeDef = TypedDict(
    "HttpEndpointDestinationUpdateTypeDef",
    {
        "EndpointConfiguration": NotRequired[HttpEndpointConfigurationTypeDef],
        "BufferingHints": NotRequired[HttpEndpointBufferingHintsTypeDef],
        "CloudWatchLoggingOptions": NotRequired[CloudWatchLoggingOptionsTypeDef],
        "RequestConfiguration": NotRequired[HttpEndpointRequestConfigurationTypeDef],
        "ProcessingConfiguration": NotRequired[ProcessingConfigurationTypeDef],
        "RoleARN": NotRequired[str],
        "RetryOptions": NotRequired[HttpEndpointRetryOptionsTypeDef],
        "S3BackupMode": NotRequired[HttpEndpointS3BackupModeType],
        "S3Update": NotRequired[S3DestinationUpdateTypeDef],
    },
)

RedshiftDestinationConfigurationTypeDef = TypedDict(
    "RedshiftDestinationConfigurationTypeDef",
    {
        "RoleARN": str,
        "ClusterJDBCURL": str,
        "CopyCommand": CopyCommandTypeDef,
        "Username": str,
        "Password": str,
        "S3Configuration": S3DestinationConfigurationTypeDef,
        "RetryOptions": NotRequired[RedshiftRetryOptionsTypeDef],
        "ProcessingConfiguration": NotRequired[ProcessingConfigurationTypeDef],
        "S3BackupMode": NotRequired[RedshiftS3BackupModeType],
        "S3BackupConfiguration": NotRequired[S3DestinationConfigurationTypeDef],
        "CloudWatchLoggingOptions": NotRequired[CloudWatchLoggingOptionsTypeDef],
    },
)

RedshiftDestinationDescriptionTypeDef = TypedDict(
    "RedshiftDestinationDescriptionTypeDef",
    {
        "RoleARN": str,
        "ClusterJDBCURL": str,
        "CopyCommand": CopyCommandTypeDef,
        "Username": str,
        "S3DestinationDescription": S3DestinationDescriptionTypeDef,
        "RetryOptions": NotRequired[RedshiftRetryOptionsTypeDef],
        "ProcessingConfiguration": NotRequired[ProcessingConfigurationTypeDef],
        "S3BackupMode": NotRequired[RedshiftS3BackupModeType],
        "S3BackupDescription": NotRequired[S3DestinationDescriptionTypeDef],
        "CloudWatchLoggingOptions": NotRequired[CloudWatchLoggingOptionsTypeDef],
    },
)

RedshiftDestinationUpdateTypeDef = TypedDict(
    "RedshiftDestinationUpdateTypeDef",
    {
        "RoleARN": NotRequired[str],
        "ClusterJDBCURL": NotRequired[str],
        "CopyCommand": NotRequired[CopyCommandTypeDef],
        "Username": NotRequired[str],
        "Password": NotRequired[str],
        "RetryOptions": NotRequired[RedshiftRetryOptionsTypeDef],
        "S3Update": NotRequired[S3DestinationUpdateTypeDef],
        "ProcessingConfiguration": NotRequired[ProcessingConfigurationTypeDef],
        "S3BackupMode": NotRequired[RedshiftS3BackupModeType],
        "S3BackupUpdate": NotRequired[S3DestinationUpdateTypeDef],
        "CloudWatchLoggingOptions": NotRequired[CloudWatchLoggingOptionsTypeDef],
    },
)

SplunkDestinationConfigurationTypeDef = TypedDict(
    "SplunkDestinationConfigurationTypeDef",
    {
        "HECEndpoint": str,
        "HECEndpointType": HECEndpointTypeType,
        "HECToken": str,
        "S3Configuration": S3DestinationConfigurationTypeDef,
        "HECAcknowledgmentTimeoutInSeconds": NotRequired[int],
        "RetryOptions": NotRequired[SplunkRetryOptionsTypeDef],
        "S3BackupMode": NotRequired[SplunkS3BackupModeType],
        "ProcessingConfiguration": NotRequired[ProcessingConfigurationTypeDef],
        "CloudWatchLoggingOptions": NotRequired[CloudWatchLoggingOptionsTypeDef],
    },
)

SplunkDestinationDescriptionTypeDef = TypedDict(
    "SplunkDestinationDescriptionTypeDef",
    {
        "HECEndpoint": NotRequired[str],
        "HECEndpointType": NotRequired[HECEndpointTypeType],
        "HECToken": NotRequired[str],
        "HECAcknowledgmentTimeoutInSeconds": NotRequired[int],
        "RetryOptions": NotRequired[SplunkRetryOptionsTypeDef],
        "S3BackupMode": NotRequired[SplunkS3BackupModeType],
        "S3DestinationDescription": NotRequired[S3DestinationDescriptionTypeDef],
        "ProcessingConfiguration": NotRequired[ProcessingConfigurationTypeDef],
        "CloudWatchLoggingOptions": NotRequired[CloudWatchLoggingOptionsTypeDef],
    },
)

SplunkDestinationUpdateTypeDef = TypedDict(
    "SplunkDestinationUpdateTypeDef",
    {
        "HECEndpoint": NotRequired[str],
        "HECEndpointType": NotRequired[HECEndpointTypeType],
        "HECToken": NotRequired[str],
        "HECAcknowledgmentTimeoutInSeconds": NotRequired[int],
        "RetryOptions": NotRequired[SplunkRetryOptionsTypeDef],
        "S3BackupMode": NotRequired[SplunkS3BackupModeType],
        "S3Update": NotRequired[S3DestinationUpdateTypeDef],
        "ProcessingConfiguration": NotRequired[ProcessingConfigurationTypeDef],
        "CloudWatchLoggingOptions": NotRequired[CloudWatchLoggingOptionsTypeDef],
    },
)

ExtendedS3DestinationConfigurationTypeDef = TypedDict(
    "ExtendedS3DestinationConfigurationTypeDef",
    {
        "RoleARN": str,
        "BucketARN": str,
        "Prefix": NotRequired[str],
        "ErrorOutputPrefix": NotRequired[str],
        "BufferingHints": NotRequired[BufferingHintsTypeDef],
        "CompressionFormat": NotRequired[CompressionFormatType],
        "EncryptionConfiguration": NotRequired[EncryptionConfigurationTypeDef],
        "CloudWatchLoggingOptions": NotRequired[CloudWatchLoggingOptionsTypeDef],
        "ProcessingConfiguration": NotRequired[ProcessingConfigurationTypeDef],
        "S3BackupMode": NotRequired[S3BackupModeType],
        "S3BackupConfiguration": NotRequired[S3DestinationConfigurationTypeDef],
        "DataFormatConversionConfiguration": NotRequired[DataFormatConversionConfigurationTypeDef],
        "DynamicPartitioningConfiguration": NotRequired[DynamicPartitioningConfigurationTypeDef],
    },
)

ExtendedS3DestinationDescriptionTypeDef = TypedDict(
    "ExtendedS3DestinationDescriptionTypeDef",
    {
        "RoleARN": str,
        "BucketARN": str,
        "BufferingHints": BufferingHintsTypeDef,
        "CompressionFormat": CompressionFormatType,
        "EncryptionConfiguration": EncryptionConfigurationTypeDef,
        "Prefix": NotRequired[str],
        "ErrorOutputPrefix": NotRequired[str],
        "CloudWatchLoggingOptions": NotRequired[CloudWatchLoggingOptionsTypeDef],
        "ProcessingConfiguration": NotRequired[ProcessingConfigurationTypeDef],
        "S3BackupMode": NotRequired[S3BackupModeType],
        "S3BackupDescription": NotRequired[S3DestinationDescriptionTypeDef],
        "DataFormatConversionConfiguration": NotRequired[DataFormatConversionConfigurationTypeDef],
        "DynamicPartitioningConfiguration": NotRequired[DynamicPartitioningConfigurationTypeDef],
    },
)

ExtendedS3DestinationUpdateTypeDef = TypedDict(
    "ExtendedS3DestinationUpdateTypeDef",
    {
        "RoleARN": NotRequired[str],
        "BucketARN": NotRequired[str],
        "Prefix": NotRequired[str],
        "ErrorOutputPrefix": NotRequired[str],
        "BufferingHints": NotRequired[BufferingHintsTypeDef],
        "CompressionFormat": NotRequired[CompressionFormatType],
        "EncryptionConfiguration": NotRequired[EncryptionConfigurationTypeDef],
        "CloudWatchLoggingOptions": NotRequired[CloudWatchLoggingOptionsTypeDef],
        "ProcessingConfiguration": NotRequired[ProcessingConfigurationTypeDef],
        "S3BackupMode": NotRequired[S3BackupModeType],
        "S3BackupUpdate": NotRequired[S3DestinationUpdateTypeDef],
        "DataFormatConversionConfiguration": NotRequired[DataFormatConversionConfigurationTypeDef],
        "DynamicPartitioningConfiguration": NotRequired[DynamicPartitioningConfigurationTypeDef],
    },
)

CreateDeliveryStreamInputRequestTypeDef = TypedDict(
    "CreateDeliveryStreamInputRequestTypeDef",
    {
        "DeliveryStreamName": str,
        "DeliveryStreamType": NotRequired[DeliveryStreamTypeType],
        "KinesisStreamSourceConfiguration": NotRequired[KinesisStreamSourceConfigurationTypeDef],
        "DeliveryStreamEncryptionConfigurationInput": NotRequired[
            DeliveryStreamEncryptionConfigurationInputTypeDef
        ],
        "S3DestinationConfiguration": NotRequired[S3DestinationConfigurationTypeDef],
        "ExtendedS3DestinationConfiguration": NotRequired[
            ExtendedS3DestinationConfigurationTypeDef
        ],
        "RedshiftDestinationConfiguration": NotRequired[RedshiftDestinationConfigurationTypeDef],
        "ElasticsearchDestinationConfiguration": NotRequired[
            ElasticsearchDestinationConfigurationTypeDef
        ],
        "AmazonopensearchserviceDestinationConfiguration": NotRequired[
            AmazonopensearchserviceDestinationConfigurationTypeDef
        ],
        "SplunkDestinationConfiguration": NotRequired[SplunkDestinationConfigurationTypeDef],
        "HttpEndpointDestinationConfiguration": NotRequired[
            HttpEndpointDestinationConfigurationTypeDef
        ],
        "Tags": NotRequired[Sequence[TagTypeDef]],
        "AmazonOpenSearchServerlessDestinationConfiguration": NotRequired[
            AmazonOpenSearchServerlessDestinationConfigurationTypeDef
        ],
    },
)

DestinationDescriptionTypeDef = TypedDict(
    "DestinationDescriptionTypeDef",
    {
        "DestinationId": str,
        "S3DestinationDescription": NotRequired[S3DestinationDescriptionTypeDef],
        "ExtendedS3DestinationDescription": NotRequired[ExtendedS3DestinationDescriptionTypeDef],
        "RedshiftDestinationDescription": NotRequired[RedshiftDestinationDescriptionTypeDef],
        "ElasticsearchDestinationDescription": NotRequired[
            ElasticsearchDestinationDescriptionTypeDef
        ],
        "AmazonopensearchserviceDestinationDescription": NotRequired[
            AmazonopensearchserviceDestinationDescriptionTypeDef
        ],
        "SplunkDestinationDescription": NotRequired[SplunkDestinationDescriptionTypeDef],
        "HttpEndpointDestinationDescription": NotRequired[
            HttpEndpointDestinationDescriptionTypeDef
        ],
        "AmazonOpenSearchServerlessDestinationDescription": NotRequired[
            AmazonOpenSearchServerlessDestinationDescriptionTypeDef
        ],
    },
)

UpdateDestinationInputRequestTypeDef = TypedDict(
    "UpdateDestinationInputRequestTypeDef",
    {
        "DeliveryStreamName": str,
        "CurrentDeliveryStreamVersionId": str,
        "DestinationId": str,
        "S3DestinationUpdate": NotRequired[S3DestinationUpdateTypeDef],
        "ExtendedS3DestinationUpdate": NotRequired[ExtendedS3DestinationUpdateTypeDef],
        "RedshiftDestinationUpdate": NotRequired[RedshiftDestinationUpdateTypeDef],
        "ElasticsearchDestinationUpdate": NotRequired[ElasticsearchDestinationUpdateTypeDef],
        "AmazonopensearchserviceDestinationUpdate": NotRequired[
            AmazonopensearchserviceDestinationUpdateTypeDef
        ],
        "SplunkDestinationUpdate": NotRequired[SplunkDestinationUpdateTypeDef],
        "HttpEndpointDestinationUpdate": NotRequired[HttpEndpointDestinationUpdateTypeDef],
        "AmazonOpenSearchServerlessDestinationUpdate": NotRequired[
            AmazonOpenSearchServerlessDestinationUpdateTypeDef
        ],
    },
)

DeliveryStreamDescriptionTypeDef = TypedDict(
    "DeliveryStreamDescriptionTypeDef",
    {
        "DeliveryStreamName": str,
        "DeliveryStreamARN": str,
        "DeliveryStreamStatus": DeliveryStreamStatusType,
        "DeliveryStreamType": DeliveryStreamTypeType,
        "VersionId": str,
        "Destinations": List[DestinationDescriptionTypeDef],
        "HasMoreDestinations": bool,
        "FailureDescription": NotRequired[FailureDescriptionTypeDef],
        "DeliveryStreamEncryptionConfiguration": NotRequired[
            DeliveryStreamEncryptionConfigurationTypeDef
        ],
        "CreateTimestamp": NotRequired[datetime],
        "LastUpdateTimestamp": NotRequired[datetime],
        "Source": NotRequired[SourceDescriptionTypeDef],
    },
)

DescribeDeliveryStreamOutputTypeDef = TypedDict(
    "DescribeDeliveryStreamOutputTypeDef",
    {
        "DeliveryStreamDescription": DeliveryStreamDescriptionTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
