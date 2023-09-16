"""
Type annotations for sagemaker service type definitions.

[Open documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_sagemaker/type_defs/)

Usage::

    ```python
    from mypy_boto3_sagemaker.type_defs import ActionSourceTypeDef

    data: ActionSourceTypeDef = ...
    ```
"""
import sys
from datetime import datetime
from typing import Any, Dict, List, Mapping, Sequence, Union

from .literals import (
    ActionStatusType,
    AggregationTransformationValueType,
    AlgorithmSortByType,
    AlgorithmStatusType,
    AppImageConfigSortKeyType,
    AppInstanceTypeType,
    AppNetworkAccessTypeType,
    AppSecurityGroupManagementType,
    AppStatusType,
    AppTypeType,
    ArtifactSourceIdTypeType,
    AssemblyTypeType,
    AssociationEdgeTypeType,
    AsyncNotificationTopicTypesType,
    AthenaResultCompressionTypeType,
    AthenaResultFormatType,
    AuthModeType,
    AutoMLAlgorithmType,
    AutoMLChannelTypeType,
    AutoMLJobObjectiveTypeType,
    AutoMLJobSecondaryStatusType,
    AutoMLJobStatusType,
    AutoMLMetricEnumType,
    AutoMLMetricExtendedEnumType,
    AutoMLModeType,
    AutoMLProblemTypeConfigNameType,
    AutoMLProcessingUnitType,
    AutoMLS3DataTypeType,
    AutoMLSortByType,
    AutoMLSortOrderType,
    AwsManagedHumanLoopRequestSourceType,
    BatchStrategyType,
    BooleanOperatorType,
    CandidateSortByType,
    CandidateStatusType,
    CandidateStepTypeType,
    CapacitySizeTypeType,
    CaptureModeType,
    CaptureStatusType,
    ClarifyFeatureTypeType,
    ClarifyTextGranularityType,
    ClarifyTextLanguageType,
    CodeRepositorySortByType,
    CodeRepositorySortOrderType,
    CompilationJobStatusType,
    CompleteOnConvergenceType,
    CompressionTypeType,
    ConditionOutcomeType,
    ContainerModeType,
    ContentClassifierType,
    CrossAccountFilterOptionType,
    DataDistributionTypeType,
    DataSourceNameType,
    DetailedAlgorithmStatusType,
    DetailedModelPackageStatusType,
    DeviceDeploymentStatusType,
    DeviceSubsetTypeType,
    DirectInternetAccessType,
    DirectionType,
    DomainStatusType,
    EdgePackagingJobStatusType,
    EdgePresetDeploymentStatusType,
    EndpointConfigSortKeyType,
    EndpointSortKeyType,
    EndpointStatusType,
    ExecutionRoleIdentityConfigType,
    ExecutionStatusType,
    FailureHandlingPolicyType,
    FeatureGroupSortByType,
    FeatureGroupSortOrderType,
    FeatureGroupStatusType,
    FeatureStatusType,
    FeatureTypeType,
    FileSystemAccessModeType,
    FileSystemTypeType,
    FillingTypeType,
    FlatInvocationsType,
    FlowDefinitionStatusType,
    FrameworkType,
    HubContentSortByType,
    HubContentStatusType,
    HubContentTypeType,
    HubSortByType,
    HubStatusType,
    HumanTaskUiStatusType,
    HyperParameterScalingTypeType,
    HyperParameterTuningJobObjectiveTypeType,
    HyperParameterTuningJobSortByOptionsType,
    HyperParameterTuningJobStatusType,
    HyperParameterTuningJobStrategyTypeType,
    HyperParameterTuningJobWarmStartTypeType,
    ImageSortByType,
    ImageSortOrderType,
    ImageStatusType,
    ImageVersionSortByType,
    ImageVersionSortOrderType,
    ImageVersionStatusType,
    InferenceExecutionModeType,
    InferenceExperimentStatusType,
    InferenceExperimentStopDesiredStateType,
    InputModeType,
    InstanceTypeType,
    JobTypeType,
    JoinSourceType,
    LabelingJobStatusType,
    LastUpdateStatusValueType,
    LineageTypeType,
    ListCompilationJobsSortByType,
    ListDeviceFleetsSortByType,
    ListEdgeDeploymentPlansSortByType,
    ListEdgePackagingJobsSortByType,
    ListInferenceRecommendationsJobsSortByType,
    ListWorkforcesSortByOptionsType,
    ListWorkteamsSortByOptionsType,
    MetricSetSourceType,
    ModelApprovalStatusType,
    ModelCacheSettingType,
    ModelCardExportJobSortByType,
    ModelCardExportJobSortOrderType,
    ModelCardExportJobStatusType,
    ModelCardProcessingStatusType,
    ModelCardSortByType,
    ModelCardSortOrderType,
    ModelCardStatusType,
    ModelCompressionTypeType,
    ModelMetadataFilterTypeType,
    ModelPackageGroupSortByType,
    ModelPackageGroupStatusType,
    ModelPackageSortByType,
    ModelPackageStatusType,
    ModelPackageTypeType,
    ModelSortKeyType,
    ModelVariantActionType,
    ModelVariantStatusType,
    MonitoringAlertHistorySortKeyType,
    MonitoringAlertStatusType,
    MonitoringExecutionSortKeyType,
    MonitoringJobDefinitionSortKeyType,
    MonitoringProblemTypeType,
    MonitoringScheduleSortKeyType,
    MonitoringTypeType,
    NotebookInstanceAcceleratorTypeType,
    NotebookInstanceLifecycleConfigSortKeyType,
    NotebookInstanceLifecycleConfigSortOrderType,
    NotebookInstanceSortKeyType,
    NotebookInstanceSortOrderType,
    NotebookInstanceStatusType,
    NotebookOutputOptionType,
    ObjectiveStatusType,
    OfflineStoreStatusValueType,
    OperatorType,
    OrderKeyType,
    OutputCompressionTypeType,
    ParameterTypeType,
    PipelineExecutionStatusType,
    ProblemTypeType,
    ProcessingInstanceTypeType,
    ProcessingJobStatusType,
    ProcessingS3CompressionTypeType,
    ProcessingS3DataDistributionTypeType,
    ProcessingS3DataTypeType,
    ProcessingS3InputModeType,
    ProcessingS3UploadModeType,
    ProcessorType,
    ProductionVariantAcceleratorTypeType,
    ProductionVariantInstanceTypeType,
    ProfilingStatusType,
    ProjectSortByType,
    ProjectSortOrderType,
    ProjectStatusType,
    RecommendationJobStatusType,
    RecommendationJobSupportedEndpointTypeType,
    RecommendationJobTypeType,
    RecommendationStatusType,
    RecordWrapperType,
    RedshiftResultCompressionTypeType,
    RedshiftResultFormatType,
    RepositoryAccessModeType,
    ResourceCatalogSortOrderType,
    ResourceTypeType,
    RetentionTypeType,
    RootAccessType,
    RStudioServerProAccessStatusType,
    RStudioServerProUserGroupType,
    RuleEvaluationStatusType,
    S3DataDistributionType,
    S3DataTypeType,
    S3ModelDataTypeType,
    SagemakerServicecatalogStatusType,
    ScheduleStatusType,
    SearchSortOrderType,
    SecondaryStatusType,
    SkipModelValidationType,
    SortActionsByType,
    SortAssociationsByType,
    SortByType,
    SortContextsByType,
    SortExperimentsByType,
    SortInferenceExperimentsByType,
    SortLineageGroupsByType,
    SortOrderType,
    SortPipelineExecutionsByType,
    SortPipelinesByType,
    SortTrialComponentsByType,
    SortTrialsByType,
    SpaceSortKeyType,
    SpaceStatusType,
    SplitTypeType,
    StageStatusType,
    StatisticType,
    StepStatusType,
    StudioLifecycleConfigAppTypeType,
    StudioLifecycleConfigSortKeyType,
    TableFormatType,
    TargetDeviceType,
    TargetPlatformAcceleratorType,
    TargetPlatformArchType,
    TargetPlatformOsType,
    TrafficRoutingConfigTypeType,
    TrafficTypeType,
    TrainingInputModeType,
    TrainingInstanceTypeType,
    TrainingJobEarlyStoppingTypeType,
    TrainingJobSortByOptionsType,
    TrainingJobStatusType,
    TrainingRepositoryAccessModeType,
    TransformInstanceTypeType,
    TransformJobStatusType,
    TrialComponentPrimaryStatusType,
    TtlDurationUnitType,
    UserProfileSortKeyType,
    UserProfileStatusType,
    VariantPropertyTypeType,
    VariantStatusType,
    VendorGuidanceType,
    WarmPoolResourceStatusType,
    WorkforceStatusType,
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
    "ActionSourceTypeDef",
    "AddAssociationRequestRequestTypeDef",
    "ResponseMetadataTypeDef",
    "TagTypeDef",
    "AgentVersionTypeDef",
    "AlarmTypeDef",
    "MetricDefinitionTypeDef",
    "AlgorithmStatusItemTypeDef",
    "AlgorithmSummaryTypeDef",
    "AnnotationConsolidationConfigTypeDef",
    "AppDetailsTypeDef",
    "AppSpecificationPaginatorTypeDef",
    "AppSpecificationTypeDef",
    "ArtifactSourceTypeTypeDef",
    "AssociateTrialComponentRequestRequestTypeDef",
    "AsyncInferenceClientConfigTypeDef",
    "AsyncInferenceNotificationConfigTypeDef",
    "AthenaDatasetDefinitionTypeDef",
    "AutoMLAlgorithmConfigTypeDef",
    "AutoMLCandidateStepTypeDef",
    "AutoMLContainerDefinitionTypeDef",
    "FinalAutoMLJobObjectiveMetricTypeDef",
    "AutoMLS3DataSourceTypeDef",
    "AutoMLDataSplitConfigTypeDef",
    "AutoMLJobArtifactsTypeDef",
    "AutoMLJobCompletionCriteriaTypeDef",
    "AutoMLJobObjectiveTypeDef",
    "AutoMLJobStepMetadataTypeDef",
    "AutoMLPartialFailureReasonTypeDef",
    "AutoMLOutputDataConfigTypeDef",
    "TabularResolvedAttributesTypeDef",
    "VpcConfigTypeDef",
    "AutoParameterTypeDef",
    "AutotuneTypeDef",
    "BatchDataCaptureConfigTypeDef",
    "BatchDescribeModelPackageErrorTypeDef",
    "BatchDescribeModelPackageInputRequestTypeDef",
    "BestObjectiveNotImprovingTypeDef",
    "MetricsSourceTypeDef",
    "CacheHitResultTypeDef",
    "OutputParameterTypeDef",
    "CandidateArtifactLocationsTypeDef",
    "MetricDatumTypeDef",
    "IdentityProviderOAuthSettingTypeDef",
    "ModelRegisterSettingsTypeDef",
    "TimeSeriesForecastingSettingsTypeDef",
    "WorkspaceSettingsTypeDef",
    "CapacitySizeTypeDef",
    "CaptureContentTypeHeaderTypeDef",
    "CaptureOptionTypeDef",
    "CategoricalParameterRangePaginatorTypeDef",
    "CategoricalParameterRangeSpecificationTypeDef",
    "CategoricalParameterRangeTypeDef",
    "CategoricalParameterTypeDef",
    "ShuffleConfigTypeDef",
    "ChannelSpecificationTypeDef",
    "CheckpointConfigTypeDef",
    "ClarifyCheckStepMetadataTypeDef",
    "ClarifyInferenceConfigTypeDef",
    "ClarifyShapBaselineConfigTypeDef",
    "ClarifyTextConfigTypeDef",
    "GitConfigTypeDef",
    "CodeRepositoryTypeDef",
    "CognitoConfigTypeDef",
    "CognitoMemberDefinitionTypeDef",
    "CollectionConfigurationPaginatorTypeDef",
    "CollectionConfigurationTypeDef",
    "CompilationJobSummaryTypeDef",
    "ConditionStepMetadataTypeDef",
    "MultiModelConfigTypeDef",
    "ContextSourceTypeDef",
    "ContinuousParameterRangeSpecificationTypeDef",
    "ContinuousParameterRangeTypeDef",
    "ConvergenceDetectedTypeDef",
    "MetadataPropertiesTypeDef",
    "ResourceSpecTypeDef",
    "ModelDeployConfigTypeDef",
    "InputConfigTypeDef",
    "NeoVpcConfigTypeDef",
    "StoppingConditionTypeDef",
    "DataQualityAppSpecificationTypeDef",
    "MonitoringStoppingConditionTypeDef",
    "EdgeOutputConfigTypeDef",
    "EdgeDeploymentModelConfigTypeDef",
    "FeatureDefinitionTypeDef",
    "FlowDefinitionOutputConfigTypeDef",
    "HumanLoopRequestSourceTypeDef",
    "HubS3StorageConfigTypeDef",
    "UiTemplateTypeDef",
    "CreateImageVersionRequestRequestTypeDef",
    "LabelingJobOutputConfigTypeDef",
    "LabelingJobStoppingConditionsTypeDef",
    "ModelBiasAppSpecificationTypeDef",
    "ModelCardExportOutputConfigTypeDef",
    "ModelCardSecurityConfigTypeDef",
    "ModelExplainabilityAppSpecificationTypeDef",
    "InferenceExecutionConfigTypeDef",
    "ModelQualityAppSpecificationTypeDef",
    "InstanceMetadataServiceConfigurationTypeDef",
    "NotebookInstanceLifecycleHookTypeDef",
    "ParallelismConfigurationTypeDef",
    "PipelineDefinitionS3LocationTypeDef",
    "CreatePresignedDomainUrlRequestRequestTypeDef",
    "CreatePresignedNotebookInstanceUrlInputRequestTypeDef",
    "ExperimentConfigTypeDef",
    "ProcessingStoppingConditionTypeDef",
    "DebugRuleConfigurationTypeDef",
    "OutputDataConfigTypeDef",
    "ProfilerConfigTypeDef",
    "ProfilerRuleConfigurationTypeDef",
    "RetryStrategyTypeDef",
    "TensorBoardOutputConfigTypeDef",
    "DataProcessingTypeDef",
    "ModelClientConfigTypeDef",
    "TransformOutputTypeDef",
    "TransformResourcesTypeDef",
    "TimestampTypeDef",
    "TrialComponentArtifactTypeDef",
    "TrialComponentParameterValueTypeDef",
    "TrialComponentStatusTypeDef",
    "OidcConfigTypeDef",
    "SourceIpConfigTypeDef",
    "WorkforceVpcConfigRequestTypeDef",
    "NotificationConfigurationTypeDef",
    "CustomImageTypeDef",
    "CustomizedMetricSpecificationTypeDef",
    "DataCaptureConfigSummaryTypeDef",
    "DataCatalogConfigTypeDef",
    "MonitoringConstraintsResourceTypeDef",
    "MonitoringStatisticsResourceTypeDef",
    "EndpointInputTypeDef",
    "FileSystemDataSourceTypeDef",
    "S3DataSourcePaginatorTypeDef",
    "S3DataSourceTypeDef",
    "RedshiftDatasetDefinitionTypeDef",
    "DebugRuleConfigurationPaginatorTypeDef",
    "DebugRuleEvaluationStatusTypeDef",
    "DeleteActionRequestRequestTypeDef",
    "DeleteAlgorithmInputRequestTypeDef",
    "DeleteAppImageConfigRequestRequestTypeDef",
    "DeleteAppRequestRequestTypeDef",
    "DeleteAssociationRequestRequestTypeDef",
    "DeleteCodeRepositoryInputRequestTypeDef",
    "DeleteContextRequestRequestTypeDef",
    "DeleteDataQualityJobDefinitionRequestRequestTypeDef",
    "DeleteDeviceFleetRequestRequestTypeDef",
    "RetentionPolicyTypeDef",
    "DeleteEdgeDeploymentPlanRequestRequestTypeDef",
    "DeleteEdgeDeploymentStageRequestRequestTypeDef",
    "DeleteEndpointConfigInputRequestTypeDef",
    "DeleteEndpointInputRequestTypeDef",
    "DeleteExperimentRequestRequestTypeDef",
    "DeleteFeatureGroupRequestRequestTypeDef",
    "DeleteFlowDefinitionRequestRequestTypeDef",
    "DeleteHubContentRequestRequestTypeDef",
    "DeleteHubRequestRequestTypeDef",
    "DeleteHumanTaskUiRequestRequestTypeDef",
    "DeleteImageRequestRequestTypeDef",
    "DeleteImageVersionRequestRequestTypeDef",
    "DeleteInferenceExperimentRequestRequestTypeDef",
    "DeleteModelBiasJobDefinitionRequestRequestTypeDef",
    "DeleteModelCardRequestRequestTypeDef",
    "DeleteModelExplainabilityJobDefinitionRequestRequestTypeDef",
    "DeleteModelInputRequestTypeDef",
    "DeleteModelPackageGroupInputRequestTypeDef",
    "DeleteModelPackageGroupPolicyInputRequestTypeDef",
    "DeleteModelPackageInputRequestTypeDef",
    "DeleteModelQualityJobDefinitionRequestRequestTypeDef",
    "DeleteMonitoringScheduleRequestRequestTypeDef",
    "DeleteNotebookInstanceInputRequestTypeDef",
    "DeleteNotebookInstanceLifecycleConfigInputRequestTypeDef",
    "DeletePipelineRequestRequestTypeDef",
    "DeleteProjectInputRequestTypeDef",
    "DeleteSpaceRequestRequestTypeDef",
    "DeleteStudioLifecycleConfigRequestRequestTypeDef",
    "DeleteTagsInputRequestTypeDef",
    "DeleteTrialComponentRequestRequestTypeDef",
    "DeleteTrialRequestRequestTypeDef",
    "DeleteUserProfileRequestRequestTypeDef",
    "DeleteWorkforceRequestRequestTypeDef",
    "DeleteWorkteamRequestRequestTypeDef",
    "DeployedImageTypeDef",
    "RealTimeInferenceRecommendationTypeDef",
    "DeviceSelectionConfigTypeDef",
    "EdgeDeploymentConfigTypeDef",
    "EdgeDeploymentStatusTypeDef",
    "DeregisterDevicesRequestRequestTypeDef",
    "DerivedInformationTypeDef",
    "DescribeActionRequestRequestTypeDef",
    "DescribeAlgorithmInputRequestTypeDef",
    "DescribeAppImageConfigRequestRequestTypeDef",
    "DescribeAppRequestRequestTypeDef",
    "DescribeArtifactRequestRequestTypeDef",
    "DescribeAutoMLJobRequestRequestTypeDef",
    "ModelDeployResultTypeDef",
    "DescribeAutoMLJobV2RequestRequestTypeDef",
    "DescribeCodeRepositoryInputRequestTypeDef",
    "DescribeCompilationJobRequestRequestTypeDef",
    "ModelArtifactsTypeDef",
    "ModelDigestsTypeDef",
    "DescribeContextRequestRequestTypeDef",
    "DescribeDataQualityJobDefinitionRequestRequestTypeDef",
    "DescribeDeviceFleetRequestRequestTypeDef",
    "DescribeDeviceRequestRequestTypeDef",
    "EdgeModelTypeDef",
    "DescribeDomainRequestRequestTypeDef",
    "DescribeEdgeDeploymentPlanRequestRequestTypeDef",
    "DescribeEdgePackagingJobRequestRequestTypeDef",
    "EdgePresetDeploymentOutputTypeDef",
    "DescribeEndpointConfigInputRequestTypeDef",
    "WaiterConfigTypeDef",
    "DescribeEndpointInputRequestTypeDef",
    "DescribeExperimentRequestRequestTypeDef",
    "ExperimentSourceTypeDef",
    "DescribeFeatureGroupRequestRequestTypeDef",
    "LastUpdateStatusTypeDef",
    "OfflineStoreStatusTypeDef",
    "DescribeFeatureMetadataRequestRequestTypeDef",
    "FeatureParameterTypeDef",
    "DescribeFlowDefinitionRequestRequestTypeDef",
    "DescribeHubContentRequestRequestTypeDef",
    "HubContentDependencyTypeDef",
    "DescribeHubRequestRequestTypeDef",
    "DescribeHumanTaskUiRequestRequestTypeDef",
    "UiTemplateInfoTypeDef",
    "DescribeHyperParameterTuningJobRequestRequestTypeDef",
    "HyperParameterTuningJobCompletionDetailsTypeDef",
    "HyperParameterTuningJobConsumedResourcesTypeDef",
    "ObjectiveStatusCountersTypeDef",
    "TrainingJobStatusCountersTypeDef",
    "DescribeImageRequestRequestTypeDef",
    "DescribeImageVersionRequestRequestTypeDef",
    "DescribeInferenceExperimentRequestRequestTypeDef",
    "EndpointMetadataTypeDef",
    "DescribeInferenceRecommendationsJobRequestRequestTypeDef",
    "DescribeLabelingJobRequestRequestTypeDef",
    "LabelCountersTypeDef",
    "LabelingJobOutputTypeDef",
    "DescribeLineageGroupRequestRequestTypeDef",
    "DescribeModelBiasJobDefinitionRequestRequestTypeDef",
    "DescribeModelCardExportJobRequestRequestTypeDef",
    "ModelCardExportArtifactsTypeDef",
    "DescribeModelCardRequestRequestTypeDef",
    "DescribeModelExplainabilityJobDefinitionRequestRequestTypeDef",
    "DescribeModelInputRequestTypeDef",
    "DescribeModelPackageGroupInputRequestTypeDef",
    "DescribeModelPackageInputRequestTypeDef",
    "DescribeModelQualityJobDefinitionRequestRequestTypeDef",
    "DescribeMonitoringScheduleRequestRequestTypeDef",
    "MonitoringExecutionSummaryTypeDef",
    "DescribeNotebookInstanceInputRequestTypeDef",
    "DescribeNotebookInstanceLifecycleConfigInputRequestTypeDef",
    "DescribePipelineDefinitionForExecutionRequestRequestTypeDef",
    "DescribePipelineExecutionRequestRequestTypeDef",
    "PipelineExperimentConfigTypeDef",
    "DescribePipelineRequestRequestTypeDef",
    "DescribeProcessingJobRequestRequestTypeDef",
    "DescribeProjectInputRequestTypeDef",
    "ServiceCatalogProvisionedProductDetailsTypeDef",
    "DescribeSpaceRequestRequestTypeDef",
    "DescribeStudioLifecycleConfigRequestRequestTypeDef",
    "DescribeSubscribedWorkteamRequestRequestTypeDef",
    "SubscribedWorkteamTypeDef",
    "DescribeTrainingJobRequestRequestTypeDef",
    "MetricDataTypeDef",
    "ProfilerRuleEvaluationStatusTypeDef",
    "SecondaryStatusTransitionTypeDef",
    "WarmPoolStatusTypeDef",
    "DescribeTransformJobRequestRequestTypeDef",
    "DescribeTrialComponentRequestRequestTypeDef",
    "TrialComponentMetricSummaryTypeDef",
    "TrialComponentSourceTypeDef",
    "DescribeTrialRequestRequestTypeDef",
    "TrialSourceTypeDef",
    "DescribeUserProfileRequestRequestTypeDef",
    "DescribeWorkforceRequestRequestTypeDef",
    "DescribeWorkteamRequestRequestTypeDef",
    "ProductionVariantServerlessUpdateConfigTypeDef",
    "DeviceDeploymentSummaryTypeDef",
    "DeviceFleetSummaryTypeDef",
    "DeviceStatsTypeDef",
    "EdgeModelSummaryTypeDef",
    "DeviceTypeDef",
    "DisassociateTrialComponentRequestRequestTypeDef",
    "DomainDetailsTypeDef",
    "FileSourceTypeDef",
    "EMRStepMetadataTypeDef",
    "EdgeDeploymentPlanSummaryTypeDef",
    "EdgeModelStatTypeDef",
    "EdgePackagingJobSummaryTypeDef",
    "EdgeTypeDef",
    "EndpointConfigSummaryTypeDef",
    "EndpointInfoTypeDef",
    "ProductionVariantServerlessConfigTypeDef",
    "InferenceMetricsTypeDef",
    "EndpointSummaryTypeDef",
    "EnvironmentParameterTypeDef",
    "FailStepMetadataTypeDef",
    "FileSystemConfigTypeDef",
    "FilterTypeDef",
    "FinalHyperParameterTuningJobObjectiveMetricTypeDef",
    "FlowDefinitionSummaryTypeDef",
    "GetDeviceFleetReportRequestRequestTypeDef",
    "GetLineageGroupPolicyRequestRequestTypeDef",
    "GetModelPackageGroupPolicyInputRequestTypeDef",
    "ScalingPolicyObjectiveTypeDef",
    "ScalingPolicyMetricTypeDef",
    "PropertyNameSuggestionTypeDef",
    "GitConfigForUpdateTypeDef",
    "HolidayConfigAttributesTypeDef",
    "HubContentInfoTypeDef",
    "HubInfoTypeDef",
    "HumanLoopActivationConditionsConfigTypeDef",
    "UiConfigTypeDef",
    "HumanTaskUiSummaryTypeDef",
    "HyperParameterTuningJobObjectiveTypeDef",
    "VpcConfigPaginatorTypeDef",
    "HyperParameterTuningInstanceConfigTypeDef",
    "ResourceLimitsTypeDef",
    "HyperbandStrategyConfigTypeDef",
    "ParentHyperParameterTuningJobTypeDef",
    "IamIdentityTypeDef",
    "RepositoryAuthConfigTypeDef",
    "ImageTypeDef",
    "ImageVersionTypeDef",
    "InferenceExperimentSchedulePaginatorTypeDef",
    "RecommendationMetricsTypeDef",
    "InferenceRecommendationsJobTypeDef",
    "InstanceGroupTypeDef",
    "IntegerParameterRangeSpecificationTypeDef",
    "IntegerParameterRangeTypeDef",
    "KernelSpecTypeDef",
    "LabelCountersForWorkteamTypeDef",
    "LabelingJobDataAttributesPaginatorTypeDef",
    "LabelingJobDataAttributesTypeDef",
    "LabelingJobS3DataSourceTypeDef",
    "LabelingJobSnsDataSourceTypeDef",
    "LineageGroupSummaryTypeDef",
    "PaginatorConfigTypeDef",
    "ListAliasesRequestRequestTypeDef",
    "ListAppsRequestRequestTypeDef",
    "ListCandidatesForAutoMLJobRequestRequestTypeDef",
    "MonitoringJobDefinitionSummaryTypeDef",
    "ListDomainsRequestRequestTypeDef",
    "ListInferenceRecommendationsJobStepsRequestRequestTypeDef",
    "ModelCardExportJobSummaryTypeDef",
    "ModelCardVersionSummaryTypeDef",
    "ModelCardSummaryTypeDef",
    "ModelMetadataSummaryTypeDef",
    "ModelPackageGroupSummaryTypeDef",
    "ModelPackageSummaryTypeDef",
    "ModelSummaryTypeDef",
    "MonitoringAlertHistorySummaryTypeDef",
    "ListMonitoringAlertsRequestRequestTypeDef",
    "MonitoringScheduleSummaryTypeDef",
    "NotebookInstanceLifecycleConfigSummaryTypeDef",
    "NotebookInstanceSummaryTypeDef",
    "ListPipelineExecutionStepsRequestRequestTypeDef",
    "PipelineExecutionSummaryTypeDef",
    "ListPipelineParametersForExecutionRequestRequestTypeDef",
    "ParameterTypeDef",
    "PipelineSummaryTypeDef",
    "ProcessingJobSummaryTypeDef",
    "ProjectSummaryTypeDef",
    "ResourceCatalogTypeDef",
    "ListSpacesRequestRequestTypeDef",
    "SpaceDetailsTypeDef",
    "ListStageDevicesRequestRequestTypeDef",
    "StudioLifecycleConfigDetailsTypeDef",
    "ListSubscribedWorkteamsRequestRequestTypeDef",
    "ListTagsInputRequestTypeDef",
    "ListTrainingJobsForHyperParameterTuningJobRequestRequestTypeDef",
    "TransformJobSummaryTypeDef",
    "ListUserProfilesRequestRequestTypeDef",
    "UserProfileDetailsTypeDef",
    "ListWorkforcesRequestRequestTypeDef",
    "ListWorkteamsRequestRequestTypeDef",
    "OidcMemberDefinitionPaginatorTypeDef",
    "OidcMemberDefinitionTypeDef",
    "PredefinedMetricSpecificationTypeDef",
    "MonitoringGroundTruthS3InputTypeDef",
    "ModelDashboardEndpointTypeDef",
    "ModelDashboardIndicatorActionTypeDef",
    "S3ModelDataSourceTypeDef",
    "RealTimeInferenceConfigTypeDef",
    "ModelInputTypeDef",
    "ModelLatencyThresholdTypeDef",
    "ModelMetadataFilterTypeDef",
    "ModelPackageStatusItemTypeDef",
    "ModelStepMetadataTypeDef",
    "MonitoringAppSpecificationPaginatorTypeDef",
    "MonitoringAppSpecificationTypeDef",
    "MonitoringClusterConfigTypeDef",
    "MonitoringCsvDatasetFormatTypeDef",
    "MonitoringJsonDatasetFormatTypeDef",
    "MonitoringS3OutputTypeDef",
    "ScheduleConfigTypeDef",
    "S3StorageConfigTypeDef",
    "OidcConfigForResponseTypeDef",
    "OnlineStoreSecurityConfigTypeDef",
    "TtlDurationTypeDef",
    "TargetPlatformTypeDef",
    "ParentTypeDef",
    "ProductionVariantStatusTypeDef",
    "PhaseTypeDef",
    "ProcessingJobStepMetadataTypeDef",
    "QualityCheckStepMetadataTypeDef",
    "RegisterModelStepMetadataTypeDef",
    "TrainingJobStepMetadataTypeDef",
    "TransformJobStepMetadataTypeDef",
    "TuningJobStepMetaDataTypeDef",
    "SelectiveExecutionResultTypeDef",
    "ProcessingClusterConfigTypeDef",
    "ProcessingFeatureStoreOutputTypeDef",
    "ProcessingS3InputTypeDef",
    "ProcessingS3OutputTypeDef",
    "ProductionVariantCoreDumpConfigTypeDef",
    "ProfilerConfigForUpdateTypeDef",
    "ProfilerConfigPaginatorTypeDef",
    "PropertyNameQueryTypeDef",
    "ProvisioningParameterTypeDef",
    "USDTypeDef",
    "PutModelPackageGroupPolicyInputRequestTypeDef",
    "VertexTypeDef",
    "RStudioServerProAppSettingsTypeDef",
    "RecommendationJobCompiledOutputConfigTypeDef",
    "RecommendationJobPayloadConfigTypeDef",
    "RecommendationJobResourceLimitTypeDef",
    "RecommendationJobVpcConfigTypeDef",
    "RenderableTaskTypeDef",
    "RenderingErrorTypeDef",
    "ResourceConfigForUpdateTypeDef",
    "SearchRequestRequestTypeDef",
    "SelectedStepTypeDef",
    "SendPipelineExecutionStepFailureRequestRequestTypeDef",
    "ShadowModelVariantConfigTypeDef",
    "SharingSettingsTypeDef",
    "SourceAlgorithmTypeDef",
    "SourceIpConfigPaginatorTypeDef",
    "StairsTypeDef",
    "StartEdgeDeploymentStageRequestRequestTypeDef",
    "StartInferenceExperimentRequestRequestTypeDef",
    "StartMonitoringScheduleRequestRequestTypeDef",
    "StartNotebookInstanceInputRequestTypeDef",
    "StopAutoMLJobRequestRequestTypeDef",
    "StopCompilationJobRequestRequestTypeDef",
    "StopEdgeDeploymentStageRequestRequestTypeDef",
    "StopEdgePackagingJobRequestRequestTypeDef",
    "StopHyperParameterTuningJobRequestRequestTypeDef",
    "StopInferenceRecommendationsJobRequestRequestTypeDef",
    "StopLabelingJobRequestRequestTypeDef",
    "StopMonitoringScheduleRequestRequestTypeDef",
    "StopNotebookInstanceInputRequestTypeDef",
    "StopPipelineExecutionRequestRequestTypeDef",
    "StopProcessingJobRequestRequestTypeDef",
    "StopTrainingJobRequestRequestTypeDef",
    "StopTransformJobRequestRequestTypeDef",
    "TimeSeriesConfigTypeDef",
    "TimeSeriesTransformationsTypeDef",
    "TrainingRepositoryAuthConfigTypeDef",
    "TransformS3DataSourceTypeDef",
    "UpdateActionRequestRequestTypeDef",
    "UpdateArtifactRequestRequestTypeDef",
    "UpdateContextRequestRequestTypeDef",
    "VariantPropertyTypeDef",
    "UpdateExperimentRequestRequestTypeDef",
    "UpdateHubRequestRequestTypeDef",
    "UpdateImageRequestRequestTypeDef",
    "UpdateImageVersionRequestRequestTypeDef",
    "UpdateModelCardRequestRequestTypeDef",
    "UpdateMonitoringAlertRequestRequestTypeDef",
    "UpdateTrialRequestRequestTypeDef",
    "WorkforceVpcConfigResponseTypeDef",
    "ActionSummaryTypeDef",
    "AddAssociationResponseTypeDef",
    "AssociateTrialComponentResponseTypeDef",
    "CreateActionResponseTypeDef",
    "CreateAlgorithmOutputTypeDef",
    "CreateAppImageConfigResponseTypeDef",
    "CreateAppResponseTypeDef",
    "CreateArtifactResponseTypeDef",
    "CreateAutoMLJobResponseTypeDef",
    "CreateAutoMLJobV2ResponseTypeDef",
    "CreateCodeRepositoryOutputTypeDef",
    "CreateCompilationJobResponseTypeDef",
    "CreateContextResponseTypeDef",
    "CreateDataQualityJobDefinitionResponseTypeDef",
    "CreateDomainResponseTypeDef",
    "CreateEdgeDeploymentPlanResponseTypeDef",
    "CreateEndpointConfigOutputTypeDef",
    "CreateEndpointOutputTypeDef",
    "CreateExperimentResponseTypeDef",
    "CreateFeatureGroupResponseTypeDef",
    "CreateFlowDefinitionResponseTypeDef",
    "CreateHubResponseTypeDef",
    "CreateHumanTaskUiResponseTypeDef",
    "CreateHyperParameterTuningJobResponseTypeDef",
    "CreateImageResponseTypeDef",
    "CreateImageVersionResponseTypeDef",
    "CreateInferenceExperimentResponseTypeDef",
    "CreateInferenceRecommendationsJobResponseTypeDef",
    "CreateLabelingJobResponseTypeDef",
    "CreateModelBiasJobDefinitionResponseTypeDef",
    "CreateModelCardExportJobResponseTypeDef",
    "CreateModelCardResponseTypeDef",
    "CreateModelExplainabilityJobDefinitionResponseTypeDef",
    "CreateModelOutputTypeDef",
    "CreateModelPackageGroupOutputTypeDef",
    "CreateModelPackageOutputTypeDef",
    "CreateModelQualityJobDefinitionResponseTypeDef",
    "CreateMonitoringScheduleResponseTypeDef",
    "CreateNotebookInstanceLifecycleConfigOutputTypeDef",
    "CreateNotebookInstanceOutputTypeDef",
    "CreatePipelineResponseTypeDef",
    "CreatePresignedDomainUrlResponseTypeDef",
    "CreatePresignedNotebookInstanceUrlOutputTypeDef",
    "CreateProcessingJobResponseTypeDef",
    "CreateProjectOutputTypeDef",
    "CreateSpaceResponseTypeDef",
    "CreateStudioLifecycleConfigResponseTypeDef",
    "CreateTrainingJobResponseTypeDef",
    "CreateTransformJobResponseTypeDef",
    "CreateTrialComponentResponseTypeDef",
    "CreateTrialResponseTypeDef",
    "CreateUserProfileResponseTypeDef",
    "CreateWorkforceResponseTypeDef",
    "CreateWorkteamResponseTypeDef",
    "DeleteActionResponseTypeDef",
    "DeleteArtifactResponseTypeDef",
    "DeleteAssociationResponseTypeDef",
    "DeleteContextResponseTypeDef",
    "DeleteExperimentResponseTypeDef",
    "DeleteInferenceExperimentResponseTypeDef",
    "DeletePipelineResponseTypeDef",
    "DeleteTrialComponentResponseTypeDef",
    "DeleteTrialResponseTypeDef",
    "DeleteWorkteamResponseTypeDef",
    "DescribeImageResponseTypeDef",
    "DescribeImageVersionResponseTypeDef",
    "DescribePipelineDefinitionForExecutionResponseTypeDef",
    "DescribeStudioLifecycleConfigResponseTypeDef",
    "DisassociateTrialComponentResponseTypeDef",
    "EmptyResponseMetadataTypeDef",
    "GetLineageGroupPolicyResponseTypeDef",
    "GetModelPackageGroupPolicyOutputTypeDef",
    "GetSagemakerServicecatalogPortfolioStatusOutputTypeDef",
    "ImportHubContentResponseTypeDef",
    "ListAliasesResponseTypeDef",
    "PutModelPackageGroupPolicyOutputTypeDef",
    "RetryPipelineExecutionResponseTypeDef",
    "SendPipelineExecutionStepFailureResponseTypeDef",
    "SendPipelineExecutionStepSuccessResponseTypeDef",
    "StartInferenceExperimentResponseTypeDef",
    "StartPipelineExecutionResponseTypeDef",
    "StopInferenceExperimentResponseTypeDef",
    "StopPipelineExecutionResponseTypeDef",
    "UpdateActionResponseTypeDef",
    "UpdateAppImageConfigResponseTypeDef",
    "UpdateArtifactResponseTypeDef",
    "UpdateCodeRepositoryOutputTypeDef",
    "UpdateContextResponseTypeDef",
    "UpdateDomainResponseTypeDef",
    "UpdateEndpointOutputTypeDef",
    "UpdateEndpointWeightsAndCapacitiesOutputTypeDef",
    "UpdateExperimentResponseTypeDef",
    "UpdateFeatureGroupResponseTypeDef",
    "UpdateHubResponseTypeDef",
    "UpdateImageResponseTypeDef",
    "UpdateImageVersionResponseTypeDef",
    "UpdateInferenceExperimentResponseTypeDef",
    "UpdateModelCardResponseTypeDef",
    "UpdateModelPackageOutputTypeDef",
    "UpdateMonitoringAlertResponseTypeDef",
    "UpdateMonitoringScheduleResponseTypeDef",
    "UpdatePipelineExecutionResponseTypeDef",
    "UpdatePipelineResponseTypeDef",
    "UpdateProjectOutputTypeDef",
    "UpdateSpaceResponseTypeDef",
    "UpdateTrainingJobResponseTypeDef",
    "UpdateTrialComponentResponseTypeDef",
    "UpdateTrialResponseTypeDef",
    "UpdateUserProfileResponseTypeDef",
    "AddTagsInputRequestTypeDef",
    "AddTagsOutputTypeDef",
    "CreateExperimentRequestRequestTypeDef",
    "CreateImageRequestRequestTypeDef",
    "CreateModelPackageGroupInputRequestTypeDef",
    "CreateStudioLifecycleConfigRequestRequestTypeDef",
    "ImportHubContentRequestRequestTypeDef",
    "ListTagsOutputTypeDef",
    "AutoRollbackConfigTypeDef",
    "HyperParameterAlgorithmSpecificationPaginatorTypeDef",
    "HyperParameterAlgorithmSpecificationTypeDef",
    "AlgorithmStatusDetailsTypeDef",
    "ListAlgorithmsOutputTypeDef",
    "ListAppsResponseTypeDef",
    "ArtifactSourcePaginatorTypeDef",
    "ArtifactSourceTypeDef",
    "AsyncInferenceOutputConfigTypeDef",
    "AutoMLCandidateGenerationConfigTypeDef",
    "CandidateGenerationConfigTypeDef",
    "AutoMLDataSourceTypeDef",
    "ImageClassificationJobConfigTypeDef",
    "TextClassificationJobConfigTypeDef",
    "ResolvedAttributesTypeDef",
    "AutoMLJobSummaryTypeDef",
    "AutoMLProblemTypeResolvedAttributesTypeDef",
    "AutoMLSecurityConfigTypeDef",
    "LabelingJobResourceConfigTypeDef",
    "MonitoringNetworkConfigTypeDef",
    "NetworkConfigTypeDef",
    "BiasTypeDef",
    "DriftCheckModelDataQualityTypeDef",
    "DriftCheckModelQualityTypeDef",
    "ExplainabilityTypeDef",
    "ModelDataQualityTypeDef",
    "ModelQualityTypeDef",
    "CallbackStepMetadataTypeDef",
    "LambdaStepMetadataTypeDef",
    "SendPipelineExecutionStepSuccessRequestRequestTypeDef",
    "CandidatePropertiesTypeDef",
    "CanvasAppSettingsTypeDef",
    "RollingUpdatePolicyTypeDef",
    "TrafficRoutingConfigTypeDef",
    "InferenceExperimentDataStorageConfigTypeDef",
    "DataCaptureConfigTypeDef",
    "EnvironmentParameterRangesTypeDef",
    "ClarifyShapConfigTypeDef",
    "CodeRepositorySummaryTypeDef",
    "CreateCodeRepositoryInputRequestTypeDef",
    "DescribeCodeRepositoryOutputTypeDef",
    "DebugHookConfigPaginatorTypeDef",
    "DebugHookConfigTypeDef",
    "ListCompilationJobsResponseTypeDef",
    "ContextSummaryTypeDef",
    "CreateContextRequestRequestTypeDef",
    "TuningJobCompletionCriteriaTypeDef",
    "CreateActionRequestRequestTypeDef",
    "CreateTrialRequestRequestTypeDef",
    "CreateAppRequestRequestTypeDef",
    "DescribeAppResponseTypeDef",
    "JupyterServerAppSettingsTypeDef",
    "RStudioServerProDomainSettingsForUpdateTypeDef",
    "RStudioServerProDomainSettingsTypeDef",
    "TensorBoardAppSettingsTypeDef",
    "CreateDeviceFleetRequestRequestTypeDef",
    "CreateEdgePackagingJobRequestRequestTypeDef",
    "DescribeDeviceFleetResponseTypeDef",
    "UpdateDeviceFleetRequestRequestTypeDef",
    "CreateHubRequestRequestTypeDef",
    "DescribeHubResponseTypeDef",
    "CreateHumanTaskUiRequestRequestTypeDef",
    "CreateModelCardExportJobRequestRequestTypeDef",
    "CreateModelCardRequestRequestTypeDef",
    "CreateNotebookInstanceInputRequestTypeDef",
    "DescribeNotebookInstanceOutputTypeDef",
    "UpdateNotebookInstanceInputRequestTypeDef",
    "CreateNotebookInstanceLifecycleConfigInputRequestTypeDef",
    "DescribeNotebookInstanceLifecycleConfigOutputTypeDef",
    "UpdateNotebookInstanceLifecycleConfigInputRequestTypeDef",
    "RetryPipelineExecutionRequestRequestTypeDef",
    "UpdatePipelineExecutionRequestRequestTypeDef",
    "CreatePipelineRequestRequestTypeDef",
    "UpdatePipelineRequestRequestTypeDef",
    "InferenceExperimentScheduleTypeDef",
    "ListActionsRequestRequestTypeDef",
    "ListAlgorithmsInputRequestTypeDef",
    "ListAppImageConfigsRequestRequestTypeDef",
    "ListArtifactsRequestRequestTypeDef",
    "ListAssociationsRequestRequestTypeDef",
    "ListAutoMLJobsRequestRequestTypeDef",
    "ListCodeRepositoriesInputRequestTypeDef",
    "ListCompilationJobsRequestRequestTypeDef",
    "ListContextsRequestRequestTypeDef",
    "ListDataQualityJobDefinitionsRequestRequestTypeDef",
    "ListDeviceFleetsRequestRequestTypeDef",
    "ListDevicesRequestRequestTypeDef",
    "ListEdgeDeploymentPlansRequestRequestTypeDef",
    "ListEdgePackagingJobsRequestRequestTypeDef",
    "ListEndpointConfigsInputRequestTypeDef",
    "ListEndpointsInputRequestTypeDef",
    "ListExperimentsRequestRequestTypeDef",
    "ListFeatureGroupsRequestRequestTypeDef",
    "ListFlowDefinitionsRequestRequestTypeDef",
    "ListHubContentVersionsRequestRequestTypeDef",
    "ListHubContentsRequestRequestTypeDef",
    "ListHubsRequestRequestTypeDef",
    "ListHumanTaskUisRequestRequestTypeDef",
    "ListHyperParameterTuningJobsRequestRequestTypeDef",
    "ListImageVersionsRequestRequestTypeDef",
    "ListImagesRequestRequestTypeDef",
    "ListInferenceExperimentsRequestRequestTypeDef",
    "ListInferenceRecommendationsJobsRequestRequestTypeDef",
    "ListLabelingJobsForWorkteamRequestRequestTypeDef",
    "ListLabelingJobsRequestRequestTypeDef",
    "ListLineageGroupsRequestRequestTypeDef",
    "ListModelBiasJobDefinitionsRequestRequestTypeDef",
    "ListModelCardExportJobsRequestRequestTypeDef",
    "ListModelCardVersionsRequestRequestTypeDef",
    "ListModelCardsRequestRequestTypeDef",
    "ListModelExplainabilityJobDefinitionsRequestRequestTypeDef",
    "ListModelPackageGroupsInputRequestTypeDef",
    "ListModelPackagesInputRequestTypeDef",
    "ListModelQualityJobDefinitionsRequestRequestTypeDef",
    "ListModelsInputRequestTypeDef",
    "ListMonitoringAlertHistoryRequestRequestTypeDef",
    "ListMonitoringExecutionsRequestRequestTypeDef",
    "ListMonitoringSchedulesRequestRequestTypeDef",
    "ListNotebookInstanceLifecycleConfigsInputRequestTypeDef",
    "ListNotebookInstancesInputRequestTypeDef",
    "ListPipelineExecutionsRequestRequestTypeDef",
    "ListPipelinesRequestRequestTypeDef",
    "ListProcessingJobsRequestRequestTypeDef",
    "ListProjectsInputRequestTypeDef",
    "ListResourceCatalogsRequestRequestTypeDef",
    "ListStudioLifecycleConfigsRequestRequestTypeDef",
    "ListTrainingJobsRequestRequestTypeDef",
    "ListTransformJobsRequestRequestTypeDef",
    "ListTrialComponentsRequestRequestTypeDef",
    "ListTrialsRequestRequestTypeDef",
    "QueryFiltersTypeDef",
    "CreateTrialComponentRequestRequestTypeDef",
    "UpdateTrialComponentRequestRequestTypeDef",
    "CreateWorkforceRequestRequestTypeDef",
    "UpdateWorkforceRequestRequestTypeDef",
    "KernelGatewayAppSettingsTypeDef",
    "RSessionAppSettingsTypeDef",
    "ModelBiasBaselineConfigTypeDef",
    "ModelExplainabilityBaselineConfigTypeDef",
    "ModelQualityBaselineConfigTypeDef",
    "DataQualityBaselineConfigTypeDef",
    "MonitoringBaselineConfigTypeDef",
    "DataSourcePaginatorTypeDef",
    "DataSourceTypeDef",
    "DatasetDefinitionTypeDef",
    "DeleteDomainRequestRequestTypeDef",
    "DeploymentRecommendationTypeDef",
    "DeploymentStageTypeDef",
    "DeploymentStageStatusSummaryTypeDef",
    "DescribeDeviceResponseTypeDef",
    "DescribeEdgePackagingJobResponseTypeDef",
    "DescribeEndpointInputEndpointDeletedWaitTypeDef",
    "DescribeEndpointInputEndpointInServiceWaitTypeDef",
    "DescribeImageRequestImageCreatedWaitTypeDef",
    "DescribeImageRequestImageDeletedWaitTypeDef",
    "DescribeImageRequestImageUpdatedWaitTypeDef",
    "DescribeImageVersionRequestImageVersionCreatedWaitTypeDef",
    "DescribeImageVersionRequestImageVersionDeletedWaitTypeDef",
    "DescribeNotebookInstanceInputNotebookInstanceDeletedWaitTypeDef",
    "DescribeNotebookInstanceInputNotebookInstanceInServiceWaitTypeDef",
    "DescribeNotebookInstanceInputNotebookInstanceStoppedWaitTypeDef",
    "DescribeProcessingJobRequestProcessingJobCompletedOrStoppedWaitTypeDef",
    "DescribeTrainingJobRequestTrainingJobCompletedOrStoppedWaitTypeDef",
    "DescribeTransformJobRequestTransformJobCompletedOrStoppedWaitTypeDef",
    "ExperimentSummaryTypeDef",
    "FeatureGroupSummaryTypeDef",
    "DescribeFeatureMetadataResponseTypeDef",
    "FeatureMetadataTypeDef",
    "UpdateFeatureMetadataRequestRequestTypeDef",
    "DescribeHubContentResponseTypeDef",
    "DescribeHumanTaskUiResponseTypeDef",
    "DescribeModelCardExportJobResponseTypeDef",
    "ListMonitoringExecutionsResponseTypeDef",
    "DescribeSubscribedWorkteamResponseTypeDef",
    "ListSubscribedWorkteamsResponseTypeDef",
    "TrainingJobSummaryTypeDef",
    "TrialSummaryTypeDef",
    "DesiredWeightAndCapacityTypeDef",
    "ListStageDevicesResponseTypeDef",
    "ListDeviceFleetsResponseTypeDef",
    "DeviceSummaryTypeDef",
    "RegisterDevicesRequestRequestTypeDef",
    "UpdateDevicesRequestRequestTypeDef",
    "ListDomainsResponseTypeDef",
    "DriftCheckBiasTypeDef",
    "DriftCheckExplainabilityTypeDef",
    "ListEdgeDeploymentPlansResponseTypeDef",
    "GetDeviceFleetReportResponseTypeDef",
    "ListEdgePackagingJobsResponseTypeDef",
    "ListEndpointConfigsOutputTypeDef",
    "EndpointOutputConfigurationTypeDef",
    "EndpointPerformanceTypeDef",
    "ListEndpointsOutputTypeDef",
    "ModelConfigurationTypeDef",
    "NestedFiltersTypeDef",
    "HyperParameterTrainingJobSummaryTypeDef",
    "ListFlowDefinitionsResponseTypeDef",
    "GetScalingConfigurationRecommendationRequestRequestTypeDef",
    "GetSearchSuggestionsResponseTypeDef",
    "UpdateCodeRepositoryInputRequestTypeDef",
    "ListHubContentVersionsResponseTypeDef",
    "ListHubContentsResponseTypeDef",
    "ListHubsResponseTypeDef",
    "HumanLoopActivationConfigTypeDef",
    "ListHumanTaskUisResponseTypeDef",
    "NetworkConfigPaginatorTypeDef",
    "HyperParameterTuningResourceConfigPaginatorTypeDef",
    "HyperParameterTuningResourceConfigTypeDef",
    "HyperParameterTuningJobSummaryTypeDef",
    "HyperParameterTuningJobStrategyConfigTypeDef",
    "HyperParameterTuningJobWarmStartConfigPaginatorTypeDef",
    "HyperParameterTuningJobWarmStartConfigTypeDef",
    "UserContextTypeDef",
    "ImageConfigTypeDef",
    "ListImagesResponseTypeDef",
    "ListImageVersionsResponseTypeDef",
    "InferenceExperimentSummaryPaginatorTypeDef",
    "ListInferenceRecommendationsJobsResponseTypeDef",
    "ResourceConfigPaginatorTypeDef",
    "ResourceConfigTypeDef",
    "ParameterRangeTypeDef",
    "ParameterRangesPaginatorTypeDef",
    "ParameterRangesTypeDef",
    "KernelGatewayImageConfigPaginatorTypeDef",
    "KernelGatewayImageConfigTypeDef",
    "LabelingJobForWorkteamSummaryTypeDef",
    "LabelingJobDataSourceTypeDef",
    "ListLineageGroupsResponseTypeDef",
    "ListActionsRequestListActionsPaginateTypeDef",
    "ListAlgorithmsInputListAlgorithmsPaginateTypeDef",
    "ListAliasesRequestListAliasesPaginateTypeDef",
    "ListAppImageConfigsRequestListAppImageConfigsPaginateTypeDef",
    "ListAppsRequestListAppsPaginateTypeDef",
    "ListArtifactsRequestListArtifactsPaginateTypeDef",
    "ListAssociationsRequestListAssociationsPaginateTypeDef",
    "ListAutoMLJobsRequestListAutoMLJobsPaginateTypeDef",
    "ListCandidatesForAutoMLJobRequestListCandidatesForAutoMLJobPaginateTypeDef",
    "ListCodeRepositoriesInputListCodeRepositoriesPaginateTypeDef",
    "ListCompilationJobsRequestListCompilationJobsPaginateTypeDef",
    "ListContextsRequestListContextsPaginateTypeDef",
    "ListDataQualityJobDefinitionsRequestListDataQualityJobDefinitionsPaginateTypeDef",
    "ListDeviceFleetsRequestListDeviceFleetsPaginateTypeDef",
    "ListDevicesRequestListDevicesPaginateTypeDef",
    "ListDomainsRequestListDomainsPaginateTypeDef",
    "ListEdgeDeploymentPlansRequestListEdgeDeploymentPlansPaginateTypeDef",
    "ListEdgePackagingJobsRequestListEdgePackagingJobsPaginateTypeDef",
    "ListEndpointConfigsInputListEndpointConfigsPaginateTypeDef",
    "ListEndpointsInputListEndpointsPaginateTypeDef",
    "ListExperimentsRequestListExperimentsPaginateTypeDef",
    "ListFeatureGroupsRequestListFeatureGroupsPaginateTypeDef",
    "ListFlowDefinitionsRequestListFlowDefinitionsPaginateTypeDef",
    "ListHumanTaskUisRequestListHumanTaskUisPaginateTypeDef",
    "ListHyperParameterTuningJobsRequestListHyperParameterTuningJobsPaginateTypeDef",
    "ListImageVersionsRequestListImageVersionsPaginateTypeDef",
    "ListImagesRequestListImagesPaginateTypeDef",
    "ListInferenceExperimentsRequestListInferenceExperimentsPaginateTypeDef",
    "ListInferenceRecommendationsJobStepsRequestListInferenceRecommendationsJobStepsPaginateTypeDef",
    "ListInferenceRecommendationsJobsRequestListInferenceRecommendationsJobsPaginateTypeDef",
    "ListLabelingJobsForWorkteamRequestListLabelingJobsForWorkteamPaginateTypeDef",
    "ListLabelingJobsRequestListLabelingJobsPaginateTypeDef",
    "ListLineageGroupsRequestListLineageGroupsPaginateTypeDef",
    "ListModelBiasJobDefinitionsRequestListModelBiasJobDefinitionsPaginateTypeDef",
    "ListModelCardExportJobsRequestListModelCardExportJobsPaginateTypeDef",
    "ListModelCardVersionsRequestListModelCardVersionsPaginateTypeDef",
    "ListModelCardsRequestListModelCardsPaginateTypeDef",
    "ListModelExplainabilityJobDefinitionsRequestListModelExplainabilityJobDefinitionsPaginateTypeDef",
    "ListModelPackageGroupsInputListModelPackageGroupsPaginateTypeDef",
    "ListModelPackagesInputListModelPackagesPaginateTypeDef",
    "ListModelQualityJobDefinitionsRequestListModelQualityJobDefinitionsPaginateTypeDef",
    "ListModelsInputListModelsPaginateTypeDef",
    "ListMonitoringAlertHistoryRequestListMonitoringAlertHistoryPaginateTypeDef",
    "ListMonitoringAlertsRequestListMonitoringAlertsPaginateTypeDef",
    "ListMonitoringExecutionsRequestListMonitoringExecutionsPaginateTypeDef",
    "ListMonitoringSchedulesRequestListMonitoringSchedulesPaginateTypeDef",
    "ListNotebookInstanceLifecycleConfigsInputListNotebookInstanceLifecycleConfigsPaginateTypeDef",
    "ListNotebookInstancesInputListNotebookInstancesPaginateTypeDef",
    "ListPipelineExecutionStepsRequestListPipelineExecutionStepsPaginateTypeDef",
    "ListPipelineExecutionsRequestListPipelineExecutionsPaginateTypeDef",
    "ListPipelineParametersForExecutionRequestListPipelineParametersForExecutionPaginateTypeDef",
    "ListPipelinesRequestListPipelinesPaginateTypeDef",
    "ListProcessingJobsRequestListProcessingJobsPaginateTypeDef",
    "ListResourceCatalogsRequestListResourceCatalogsPaginateTypeDef",
    "ListSpacesRequestListSpacesPaginateTypeDef",
    "ListStageDevicesRequestListStageDevicesPaginateTypeDef",
    "ListStudioLifecycleConfigsRequestListStudioLifecycleConfigsPaginateTypeDef",
    "ListSubscribedWorkteamsRequestListSubscribedWorkteamsPaginateTypeDef",
    "ListTagsInputListTagsPaginateTypeDef",
    "ListTrainingJobsForHyperParameterTuningJobRequestListTrainingJobsForHyperParameterTuningJobPaginateTypeDef",
    "ListTrainingJobsRequestListTrainingJobsPaginateTypeDef",
    "ListTransformJobsRequestListTransformJobsPaginateTypeDef",
    "ListTrialComponentsRequestListTrialComponentsPaginateTypeDef",
    "ListTrialsRequestListTrialsPaginateTypeDef",
    "ListUserProfilesRequestListUserProfilesPaginateTypeDef",
    "ListWorkforcesRequestListWorkforcesPaginateTypeDef",
    "ListWorkteamsRequestListWorkteamsPaginateTypeDef",
    "ListDataQualityJobDefinitionsResponseTypeDef",
    "ListModelBiasJobDefinitionsResponseTypeDef",
    "ListModelExplainabilityJobDefinitionsResponseTypeDef",
    "ListModelQualityJobDefinitionsResponseTypeDef",
    "ListModelCardExportJobsResponseTypeDef",
    "ListModelCardVersionsResponseTypeDef",
    "ListModelCardsResponseTypeDef",
    "ListModelMetadataResponseTypeDef",
    "ListModelPackageGroupsOutputTypeDef",
    "ListModelPackagesOutputTypeDef",
    "ListModelsOutputTypeDef",
    "ListMonitoringAlertHistoryResponseTypeDef",
    "ListMonitoringSchedulesResponseTypeDef",
    "ListNotebookInstanceLifecycleConfigsOutputTypeDef",
    "ListNotebookInstancesOutputTypeDef",
    "ListPipelineExecutionsResponseTypeDef",
    "ListPipelineParametersForExecutionResponseTypeDef",
    "ListPipelinesResponseTypeDef",
    "ListProcessingJobsResponseTypeDef",
    "ListProjectsOutputTypeDef",
    "ListResourceCatalogsResponseTypeDef",
    "ListSpacesResponseTypeDef",
    "ListStudioLifecycleConfigsResponseTypeDef",
    "ListTransformJobsResponseTypeDef",
    "ListUserProfilesResponseTypeDef",
    "MemberDefinitionPaginatorTypeDef",
    "MemberDefinitionTypeDef",
    "MetricSpecificationTypeDef",
    "MonitoringAlertActionsTypeDef",
    "ModelDataSourceTypeDef",
    "ModelInfrastructureConfigTypeDef",
    "ModelPackageContainerDefinitionTypeDef",
    "RecommendationJobStoppingConditionsTypeDef",
    "ModelMetadataSearchExpressionTypeDef",
    "ModelPackageStatusDetailsTypeDef",
    "MonitoringResourcesTypeDef",
    "MonitoringDatasetFormatPaginatorTypeDef",
    "MonitoringDatasetFormatTypeDef",
    "MonitoringOutputTypeDef",
    "OfflineStoreConfigTypeDef",
    "OnlineStoreConfigTypeDef",
    "OnlineStoreConfigUpdateTypeDef",
    "OutputConfigTypeDef",
    "PendingProductionVariantSummaryTypeDef",
    "ProductionVariantSummaryTypeDef",
    "ProcessingResourcesTypeDef",
    "ProcessingOutputTypeDef",
    "ProductionVariantTypeDef",
    "SuggestionQueryTypeDef",
    "ServiceCatalogProvisioningDetailsPaginatorTypeDef",
    "ServiceCatalogProvisioningDetailsTypeDef",
    "ServiceCatalogProvisioningUpdateDetailsTypeDef",
    "PublicWorkforceTaskPriceTypeDef",
    "QueryLineageResponseTypeDef",
    "RecommendationJobOutputConfigTypeDef",
    "RecommendationJobContainerConfigTypeDef",
    "RenderUiTemplateRequestRequestTypeDef",
    "RenderUiTemplateResponseTypeDef",
    "UpdateTrainingJobRequestRequestTypeDef",
    "SelectiveExecutionConfigTypeDef",
    "ShadowModeConfigTypeDef",
    "SourceAlgorithmSpecificationPaginatorTypeDef",
    "SourceAlgorithmSpecificationTypeDef",
    "TrafficPatternTypeDef",
    "TimeSeriesForecastingJobConfigTypeDef",
    "TrainingImageConfigTypeDef",
    "TransformDataSourceTypeDef",
    "WorkforcePaginatorTypeDef",
    "WorkforceTypeDef",
    "ListActionsResponseTypeDef",
    "ArtifactSummaryPaginatorTypeDef",
    "ArtifactSummaryTypeDef",
    "CreateArtifactRequestRequestTypeDef",
    "DeleteArtifactRequestRequestTypeDef",
    "AsyncInferenceConfigTypeDef",
    "TabularJobConfigTypeDef",
    "AutoMLChannelTypeDef",
    "AutoMLJobChannelTypeDef",
    "ListAutoMLJobsResponseTypeDef",
    "AutoMLResolvedAttributesTypeDef",
    "AutoMLJobConfigTypeDef",
    "LabelingJobAlgorithmsConfigTypeDef",
    "ModelMetricsTypeDef",
    "PipelineExecutionStepMetadataTypeDef",
    "AutoMLCandidateTypeDef",
    "BlueGreenUpdatePolicyTypeDef",
    "EndpointInputConfigurationTypeDef",
    "ClarifyExplainerConfigTypeDef",
    "ListCodeRepositoriesOutputTypeDef",
    "ListContextsResponseTypeDef",
    "DomainSettingsForUpdateTypeDef",
    "DomainSettingsTypeDef",
    "InferenceExperimentSummaryTypeDef",
    "QueryLineageRequestRequestTypeDef",
    "DefaultSpaceSettingsTypeDef",
    "SpaceSettingsTypeDef",
    "UserSettingsTypeDef",
    "ChannelPaginatorTypeDef",
    "ChannelTypeDef",
    "ProcessingInputTypeDef",
    "CreateEdgeDeploymentPlanRequestRequestTypeDef",
    "CreateEdgeDeploymentStageRequestRequestTypeDef",
    "DescribeEdgeDeploymentPlanResponseTypeDef",
    "ListExperimentsResponseTypeDef",
    "ListFeatureGroupsResponseTypeDef",
    "ListTrainingJobsResponseTypeDef",
    "ListTrialsResponseTypeDef",
    "UpdateEndpointWeightsAndCapacitiesInputRequestTypeDef",
    "ListDevicesResponseTypeDef",
    "DriftCheckBaselinesTypeDef",
    "InferenceRecommendationTypeDef",
    "RecommendationJobInferenceBenchmarkTypeDef",
    "SearchExpressionTypeDef",
    "ListTrainingJobsForHyperParameterTuningJobResponseTypeDef",
    "ListHyperParameterTuningJobsResponseTypeDef",
    "AssociationSummaryTypeDef",
    "DescribeActionResponseTypeDef",
    "DescribeArtifactResponseTypeDef",
    "DescribeContextResponseTypeDef",
    "DescribeExperimentResponseTypeDef",
    "DescribeLineageGroupResponseTypeDef",
    "DescribeModelCardResponseTypeDef",
    "DescribeModelPackageGroupOutputTypeDef",
    "DescribePipelineResponseTypeDef",
    "DescribeTrialComponentResponseTypeDef",
    "DescribeTrialResponseTypeDef",
    "ExperimentTypeDef",
    "ModelCardTypeDef",
    "ModelDashboardModelCardTypeDef",
    "ModelPackageGroupTypeDef",
    "PipelineTypeDef",
    "TrialComponentSimpleSummaryTypeDef",
    "TrialComponentSummaryTypeDef",
    "ListInferenceExperimentsResponsePaginatorTypeDef",
    "HyperParameterSpecificationTypeDef",
    "HyperParameterTuningJobConfigPaginatorTypeDef",
    "HyperParameterTuningJobConfigTypeDef",
    "AppImageConfigDetailsPaginatorTypeDef",
    "AppImageConfigDetailsTypeDef",
    "CreateAppImageConfigRequestRequestTypeDef",
    "DescribeAppImageConfigResponseTypeDef",
    "UpdateAppImageConfigRequestRequestTypeDef",
    "ListLabelingJobsForWorkteamResponseTypeDef",
    "LabelingJobInputConfigPaginatorTypeDef",
    "LabelingJobInputConfigTypeDef",
    "WorkteamPaginatorTypeDef",
    "CreateWorkteamRequestRequestTypeDef",
    "UpdateWorkteamRequestRequestTypeDef",
    "WorkteamTypeDef",
    "TargetTrackingScalingPolicyConfigurationTypeDef",
    "MonitoringAlertSummaryTypeDef",
    "ContainerDefinitionPaginatorTypeDef",
    "ContainerDefinitionTypeDef",
    "ModelVariantConfigSummaryTypeDef",
    "ModelVariantConfigTypeDef",
    "AdditionalInferenceSpecificationDefinitionPaginatorTypeDef",
    "AdditionalInferenceSpecificationDefinitionTypeDef",
    "InferenceSpecificationTypeDef",
    "ListModelMetadataRequestListModelMetadataPaginateTypeDef",
    "ListModelMetadataRequestRequestTypeDef",
    "BatchTransformInputPaginatorTypeDef",
    "BatchTransformInputTypeDef",
    "MonitoringOutputConfigPaginatorTypeDef",
    "MonitoringOutputConfigTypeDef",
    "CreateFeatureGroupRequestRequestTypeDef",
    "DescribeFeatureGroupResponseTypeDef",
    "FeatureGroupTypeDef",
    "UpdateFeatureGroupRequestRequestTypeDef",
    "CreateCompilationJobRequestRequestTypeDef",
    "DescribeCompilationJobResponseTypeDef",
    "PendingDeploymentSummaryTypeDef",
    "ProcessingOutputConfigPaginatorTypeDef",
    "ProcessingOutputConfigTypeDef",
    "GetSearchSuggestionsRequestRequestTypeDef",
    "ProjectPaginatorTypeDef",
    "CreateProjectInputRequestTypeDef",
    "DescribeProjectOutputTypeDef",
    "ProjectTypeDef",
    "UpdateProjectInputRequestTypeDef",
    "HumanLoopConfigTypeDef",
    "HumanTaskConfigTypeDef",
    "DescribePipelineExecutionResponseTypeDef",
    "PipelineExecutionTypeDef",
    "StartPipelineExecutionRequestRequestTypeDef",
    "AlgorithmSpecificationPaginatorTypeDef",
    "AlgorithmSpecificationTypeDef",
    "TransformInputTypeDef",
    "ListWorkforcesResponsePaginatorTypeDef",
    "DescribeWorkforceResponseTypeDef",
    "ListWorkforcesResponseTypeDef",
    "UpdateWorkforceResponseTypeDef",
    "ListArtifactsResponsePaginatorTypeDef",
    "ListArtifactsResponseTypeDef",
    "AutoMLProblemTypeConfigTypeDef",
    "CreateAutoMLJobRequestRequestTypeDef",
    "PipelineExecutionStepTypeDef",
    "DescribeAutoMLJobResponseTypeDef",
    "ListCandidatesForAutoMLJobResponseTypeDef",
    "DeploymentConfigTypeDef",
    "RecommendationJobInputConfigTypeDef",
    "ExplainerConfigTypeDef",
    "ListInferenceExperimentsResponseTypeDef",
    "CreateSpaceRequestRequestTypeDef",
    "DescribeSpaceResponseTypeDef",
    "UpdateSpaceRequestRequestTypeDef",
    "CreateDomainRequestRequestTypeDef",
    "CreateUserProfileRequestRequestTypeDef",
    "DescribeDomainResponseTypeDef",
    "DescribeUserProfileResponseTypeDef",
    "UpdateDomainRequestRequestTypeDef",
    "UpdateUserProfileRequestRequestTypeDef",
    "HyperParameterTrainingJobDefinitionPaginatorTypeDef",
    "HyperParameterTrainingJobDefinitionTypeDef",
    "TrainingJobDefinitionTypeDef",
    "InferenceRecommendationsJobStepTypeDef",
    "SearchRequestSearchPaginateTypeDef",
    "ListAssociationsResponseTypeDef",
    "TrialTypeDef",
    "ListTrialComponentsResponseTypeDef",
    "TrainingSpecificationTypeDef",
    "ListAppImageConfigsResponsePaginatorTypeDef",
    "ListAppImageConfigsResponseTypeDef",
    "LabelingJobSummaryPaginatorTypeDef",
    "LabelingJobSummaryTypeDef",
    "ListWorkteamsResponsePaginatorTypeDef",
    "DescribeWorkteamResponseTypeDef",
    "ListWorkteamsResponseTypeDef",
    "UpdateWorkteamResponseTypeDef",
    "ScalingPolicyTypeDef",
    "ListMonitoringAlertsResponseTypeDef",
    "ModelPaginatorTypeDef",
    "CreateModelInputRequestTypeDef",
    "DescribeModelOutputTypeDef",
    "ModelTypeDef",
    "DescribeInferenceExperimentResponseTypeDef",
    "CreateInferenceExperimentRequestRequestTypeDef",
    "StopInferenceExperimentRequestRequestTypeDef",
    "UpdateInferenceExperimentRequestRequestTypeDef",
    "UpdateModelPackageInputRequestTypeDef",
    "BatchDescribeModelPackageSummaryTypeDef",
    "MonitoringInputPaginatorTypeDef",
    "DataQualityJobInputTypeDef",
    "ModelBiasJobInputTypeDef",
    "ModelExplainabilityJobInputTypeDef",
    "ModelQualityJobInputTypeDef",
    "MonitoringInputTypeDef",
    "ProcessingJobPaginatorTypeDef",
    "CreateProcessingJobRequestRequestTypeDef",
    "DescribeProcessingJobResponseTypeDef",
    "ProcessingJobTypeDef",
    "CreateFlowDefinitionRequestRequestTypeDef",
    "DescribeFlowDefinitionResponseTypeDef",
    "CreateLabelingJobRequestRequestTypeDef",
    "DescribeLabelingJobResponseTypeDef",
    "TrainingJobPaginatorTypeDef",
    "CreateTrainingJobRequestRequestTypeDef",
    "DescribeTrainingJobResponseTypeDef",
    "TrainingJobTypeDef",
    "CreateTransformJobRequestRequestTypeDef",
    "DescribeTransformJobResponseTypeDef",
    "TransformJobDefinitionPaginatorTypeDef",
    "TransformJobDefinitionTypeDef",
    "TransformJobTypeDef",
    "CreateAutoMLJobV2RequestRequestTypeDef",
    "DescribeAutoMLJobV2ResponseTypeDef",
    "ListPipelineExecutionStepsResponseTypeDef",
    "CreateEndpointInputRequestTypeDef",
    "UpdateEndpointInputRequestTypeDef",
    "CreateInferenceRecommendationsJobRequestRequestTypeDef",
    "DescribeInferenceRecommendationsJobResponseTypeDef",
    "CreateEndpointConfigInputRequestTypeDef",
    "DescribeEndpointConfigOutputTypeDef",
    "DescribeEndpointOutputTypeDef",
    "HyperParameterTuningJobSearchEntityPaginatorTypeDef",
    "CreateHyperParameterTuningJobRequestRequestTypeDef",
    "DescribeHyperParameterTuningJobResponseTypeDef",
    "HyperParameterTuningJobSearchEntityTypeDef",
    "ListInferenceRecommendationsJobStepsResponseTypeDef",
    "ListLabelingJobsResponsePaginatorTypeDef",
    "ListLabelingJobsResponseTypeDef",
    "DynamicScalingConfigurationTypeDef",
    "BatchDescribeModelPackageOutputTypeDef",
    "MonitoringJobDefinitionPaginatorTypeDef",
    "CreateDataQualityJobDefinitionRequestRequestTypeDef",
    "DescribeDataQualityJobDefinitionResponseTypeDef",
    "CreateModelBiasJobDefinitionRequestRequestTypeDef",
    "DescribeModelBiasJobDefinitionResponseTypeDef",
    "CreateModelExplainabilityJobDefinitionRequestRequestTypeDef",
    "DescribeModelExplainabilityJobDefinitionResponseTypeDef",
    "CreateModelQualityJobDefinitionRequestRequestTypeDef",
    "DescribeModelQualityJobDefinitionResponseTypeDef",
    "MonitoringJobDefinitionTypeDef",
    "ModelPackageValidationProfilePaginatorTypeDef",
    "AlgorithmValidationProfileTypeDef",
    "ModelPackageValidationProfileTypeDef",
    "TrialComponentSourceDetailPaginatorTypeDef",
    "TrialComponentSourceDetailTypeDef",
    "GetScalingConfigurationRecommendationResponseTypeDef",
    "MonitoringScheduleConfigPaginatorTypeDef",
    "MonitoringScheduleConfigTypeDef",
    "ModelPackageValidationSpecificationPaginatorTypeDef",
    "AlgorithmValidationSpecificationTypeDef",
    "ModelPackageValidationSpecificationTypeDef",
    "TrialComponentPaginatorTypeDef",
    "TrialComponentTypeDef",
    "ModelDashboardMonitoringSchedulePaginatorTypeDef",
    "MonitoringSchedulePaginatorTypeDef",
    "CreateMonitoringScheduleRequestRequestTypeDef",
    "DescribeMonitoringScheduleResponseTypeDef",
    "ModelDashboardMonitoringScheduleTypeDef",
    "MonitoringScheduleTypeDef",
    "UpdateMonitoringScheduleRequestRequestTypeDef",
    "ModelPackagePaginatorTypeDef",
    "CreateAlgorithmInputRequestTypeDef",
    "DescribeAlgorithmOutputTypeDef",
    "CreateModelPackageInputRequestTypeDef",
    "DescribeModelPackageOutputTypeDef",
    "ModelPackageTypeDef",
    "ModelDashboardModelPaginatorTypeDef",
    "EndpointPaginatorTypeDef",
    "ModelDashboardModelTypeDef",
    "EndpointTypeDef",
    "SearchRecordPaginatorTypeDef",
    "SearchRecordTypeDef",
    "SearchResponsePaginatorTypeDef",
    "SearchResponseTypeDef",
)

ActionSourceTypeDef = TypedDict(
    "ActionSourceTypeDef",
    {
        "SourceUri": str,
        "SourceType": NotRequired[str],
        "SourceId": NotRequired[str],
    },
)

AddAssociationRequestRequestTypeDef = TypedDict(
    "AddAssociationRequestRequestTypeDef",
    {
        "SourceArn": str,
        "DestinationArn": str,
        "AssociationType": NotRequired[AssociationEdgeTypeType],
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

TagTypeDef = TypedDict(
    "TagTypeDef",
    {
        "Key": str,
        "Value": str,
    },
)

AgentVersionTypeDef = TypedDict(
    "AgentVersionTypeDef",
    {
        "Version": str,
        "AgentCount": int,
    },
)

AlarmTypeDef = TypedDict(
    "AlarmTypeDef",
    {
        "AlarmName": NotRequired[str],
    },
)

MetricDefinitionTypeDef = TypedDict(
    "MetricDefinitionTypeDef",
    {
        "Name": str,
        "Regex": str,
    },
)

AlgorithmStatusItemTypeDef = TypedDict(
    "AlgorithmStatusItemTypeDef",
    {
        "Name": str,
        "Status": DetailedAlgorithmStatusType,
        "FailureReason": NotRequired[str],
    },
)

AlgorithmSummaryTypeDef = TypedDict(
    "AlgorithmSummaryTypeDef",
    {
        "AlgorithmName": str,
        "AlgorithmArn": str,
        "CreationTime": datetime,
        "AlgorithmStatus": AlgorithmStatusType,
        "AlgorithmDescription": NotRequired[str],
    },
)

AnnotationConsolidationConfigTypeDef = TypedDict(
    "AnnotationConsolidationConfigTypeDef",
    {
        "AnnotationConsolidationLambdaArn": str,
    },
)

AppDetailsTypeDef = TypedDict(
    "AppDetailsTypeDef",
    {
        "DomainId": NotRequired[str],
        "UserProfileName": NotRequired[str],
        "AppType": NotRequired[AppTypeType],
        "AppName": NotRequired[str],
        "Status": NotRequired[AppStatusType],
        "CreationTime": NotRequired[datetime],
        "SpaceName": NotRequired[str],
    },
)

AppSpecificationPaginatorTypeDef = TypedDict(
    "AppSpecificationPaginatorTypeDef",
    {
        "ImageUri": str,
        "ContainerEntrypoint": NotRequired[List[str]],
        "ContainerArguments": NotRequired[List[str]],
    },
)

AppSpecificationTypeDef = TypedDict(
    "AppSpecificationTypeDef",
    {
        "ImageUri": str,
        "ContainerEntrypoint": NotRequired[Sequence[str]],
        "ContainerArguments": NotRequired[Sequence[str]],
    },
)

ArtifactSourceTypeTypeDef = TypedDict(
    "ArtifactSourceTypeTypeDef",
    {
        "SourceIdType": ArtifactSourceIdTypeType,
        "Value": str,
    },
)

AssociateTrialComponentRequestRequestTypeDef = TypedDict(
    "AssociateTrialComponentRequestRequestTypeDef",
    {
        "TrialComponentName": str,
        "TrialName": str,
    },
)

AsyncInferenceClientConfigTypeDef = TypedDict(
    "AsyncInferenceClientConfigTypeDef",
    {
        "MaxConcurrentInvocationsPerInstance": NotRequired[int],
    },
)

AsyncInferenceNotificationConfigTypeDef = TypedDict(
    "AsyncInferenceNotificationConfigTypeDef",
    {
        "SuccessTopic": NotRequired[str],
        "ErrorTopic": NotRequired[str],
        "IncludeInferenceResponseIn": NotRequired[Sequence[AsyncNotificationTopicTypesType]],
    },
)

AthenaDatasetDefinitionTypeDef = TypedDict(
    "AthenaDatasetDefinitionTypeDef",
    {
        "Catalog": str,
        "Database": str,
        "QueryString": str,
        "OutputS3Uri": str,
        "OutputFormat": AthenaResultFormatType,
        "WorkGroup": NotRequired[str],
        "KmsKeyId": NotRequired[str],
        "OutputCompression": NotRequired[AthenaResultCompressionTypeType],
    },
)

AutoMLAlgorithmConfigTypeDef = TypedDict(
    "AutoMLAlgorithmConfigTypeDef",
    {
        "AutoMLAlgorithms": Sequence[AutoMLAlgorithmType],
    },
)

AutoMLCandidateStepTypeDef = TypedDict(
    "AutoMLCandidateStepTypeDef",
    {
        "CandidateStepType": CandidateStepTypeType,
        "CandidateStepArn": str,
        "CandidateStepName": str,
    },
)

AutoMLContainerDefinitionTypeDef = TypedDict(
    "AutoMLContainerDefinitionTypeDef",
    {
        "Image": str,
        "ModelDataUrl": str,
        "Environment": NotRequired[Dict[str, str]],
    },
)

FinalAutoMLJobObjectiveMetricTypeDef = TypedDict(
    "FinalAutoMLJobObjectiveMetricTypeDef",
    {
        "MetricName": AutoMLMetricEnumType,
        "Value": float,
        "Type": NotRequired[AutoMLJobObjectiveTypeType],
        "StandardMetricName": NotRequired[AutoMLMetricEnumType],
    },
)

AutoMLS3DataSourceTypeDef = TypedDict(
    "AutoMLS3DataSourceTypeDef",
    {
        "S3DataType": AutoMLS3DataTypeType,
        "S3Uri": str,
    },
)

AutoMLDataSplitConfigTypeDef = TypedDict(
    "AutoMLDataSplitConfigTypeDef",
    {
        "ValidationFraction": NotRequired[float],
    },
)

AutoMLJobArtifactsTypeDef = TypedDict(
    "AutoMLJobArtifactsTypeDef",
    {
        "CandidateDefinitionNotebookLocation": NotRequired[str],
        "DataExplorationNotebookLocation": NotRequired[str],
    },
)

AutoMLJobCompletionCriteriaTypeDef = TypedDict(
    "AutoMLJobCompletionCriteriaTypeDef",
    {
        "MaxCandidates": NotRequired[int],
        "MaxRuntimePerTrainingJobInSeconds": NotRequired[int],
        "MaxAutoMLJobRuntimeInSeconds": NotRequired[int],
    },
)

AutoMLJobObjectiveTypeDef = TypedDict(
    "AutoMLJobObjectiveTypeDef",
    {
        "MetricName": AutoMLMetricEnumType,
    },
)

AutoMLJobStepMetadataTypeDef = TypedDict(
    "AutoMLJobStepMetadataTypeDef",
    {
        "Arn": NotRequired[str],
    },
)

AutoMLPartialFailureReasonTypeDef = TypedDict(
    "AutoMLPartialFailureReasonTypeDef",
    {
        "PartialFailureMessage": NotRequired[str],
    },
)

AutoMLOutputDataConfigTypeDef = TypedDict(
    "AutoMLOutputDataConfigTypeDef",
    {
        "S3OutputPath": str,
        "KmsKeyId": NotRequired[str],
    },
)

TabularResolvedAttributesTypeDef = TypedDict(
    "TabularResolvedAttributesTypeDef",
    {
        "ProblemType": NotRequired[ProblemTypeType],
    },
)

VpcConfigTypeDef = TypedDict(
    "VpcConfigTypeDef",
    {
        "SecurityGroupIds": Sequence[str],
        "Subnets": Sequence[str],
    },
)

AutoParameterTypeDef = TypedDict(
    "AutoParameterTypeDef",
    {
        "Name": str,
        "ValueHint": str,
    },
)

AutotuneTypeDef = TypedDict(
    "AutotuneTypeDef",
    {
        "Mode": Literal["Enabled"],
    },
)

BatchDataCaptureConfigTypeDef = TypedDict(
    "BatchDataCaptureConfigTypeDef",
    {
        "DestinationS3Uri": str,
        "KmsKeyId": NotRequired[str],
        "GenerateInferenceId": NotRequired[bool],
    },
)

BatchDescribeModelPackageErrorTypeDef = TypedDict(
    "BatchDescribeModelPackageErrorTypeDef",
    {
        "ErrorCode": str,
        "ErrorResponse": str,
    },
)

BatchDescribeModelPackageInputRequestTypeDef = TypedDict(
    "BatchDescribeModelPackageInputRequestTypeDef",
    {
        "ModelPackageArnList": Sequence[str],
    },
)

BestObjectiveNotImprovingTypeDef = TypedDict(
    "BestObjectiveNotImprovingTypeDef",
    {
        "MaxNumberOfTrainingJobsNotImproving": NotRequired[int],
    },
)

MetricsSourceTypeDef = TypedDict(
    "MetricsSourceTypeDef",
    {
        "ContentType": str,
        "S3Uri": str,
        "ContentDigest": NotRequired[str],
    },
)

CacheHitResultTypeDef = TypedDict(
    "CacheHitResultTypeDef",
    {
        "SourcePipelineExecutionArn": NotRequired[str],
    },
)

OutputParameterTypeDef = TypedDict(
    "OutputParameterTypeDef",
    {
        "Name": str,
        "Value": str,
    },
)

CandidateArtifactLocationsTypeDef = TypedDict(
    "CandidateArtifactLocationsTypeDef",
    {
        "Explainability": str,
        "ModelInsights": NotRequired[str],
        "BacktestResults": NotRequired[str],
    },
)

MetricDatumTypeDef = TypedDict(
    "MetricDatumTypeDef",
    {
        "MetricName": NotRequired[AutoMLMetricEnumType],
        "Value": NotRequired[float],
        "Set": NotRequired[MetricSetSourceType],
        "StandardMetricName": NotRequired[AutoMLMetricExtendedEnumType],
    },
)

IdentityProviderOAuthSettingTypeDef = TypedDict(
    "IdentityProviderOAuthSettingTypeDef",
    {
        "DataSourceName": NotRequired[DataSourceNameType],
        "Status": NotRequired[FeatureStatusType],
        "SecretArn": NotRequired[str],
    },
)

ModelRegisterSettingsTypeDef = TypedDict(
    "ModelRegisterSettingsTypeDef",
    {
        "Status": NotRequired[FeatureStatusType],
        "CrossAccountModelRegisterRoleArn": NotRequired[str],
    },
)

TimeSeriesForecastingSettingsTypeDef = TypedDict(
    "TimeSeriesForecastingSettingsTypeDef",
    {
        "Status": NotRequired[FeatureStatusType],
        "AmazonForecastRoleArn": NotRequired[str],
    },
)

WorkspaceSettingsTypeDef = TypedDict(
    "WorkspaceSettingsTypeDef",
    {
        "S3ArtifactPath": NotRequired[str],
        "S3KmsKeyId": NotRequired[str],
    },
)

CapacitySizeTypeDef = TypedDict(
    "CapacitySizeTypeDef",
    {
        "Type": CapacitySizeTypeType,
        "Value": int,
    },
)

CaptureContentTypeHeaderTypeDef = TypedDict(
    "CaptureContentTypeHeaderTypeDef",
    {
        "CsvContentTypes": NotRequired[Sequence[str]],
        "JsonContentTypes": NotRequired[Sequence[str]],
    },
)

CaptureOptionTypeDef = TypedDict(
    "CaptureOptionTypeDef",
    {
        "CaptureMode": CaptureModeType,
    },
)

CategoricalParameterRangePaginatorTypeDef = TypedDict(
    "CategoricalParameterRangePaginatorTypeDef",
    {
        "Name": str,
        "Values": List[str],
    },
)

CategoricalParameterRangeSpecificationTypeDef = TypedDict(
    "CategoricalParameterRangeSpecificationTypeDef",
    {
        "Values": Sequence[str],
    },
)

CategoricalParameterRangeTypeDef = TypedDict(
    "CategoricalParameterRangeTypeDef",
    {
        "Name": str,
        "Values": Sequence[str],
    },
)

CategoricalParameterTypeDef = TypedDict(
    "CategoricalParameterTypeDef",
    {
        "Name": str,
        "Value": Sequence[str],
    },
)

ShuffleConfigTypeDef = TypedDict(
    "ShuffleConfigTypeDef",
    {
        "Seed": int,
    },
)

ChannelSpecificationTypeDef = TypedDict(
    "ChannelSpecificationTypeDef",
    {
        "Name": str,
        "SupportedContentTypes": Sequence[str],
        "SupportedInputModes": Sequence[TrainingInputModeType],
        "Description": NotRequired[str],
        "IsRequired": NotRequired[bool],
        "SupportedCompressionTypes": NotRequired[Sequence[CompressionTypeType]],
    },
)

CheckpointConfigTypeDef = TypedDict(
    "CheckpointConfigTypeDef",
    {
        "S3Uri": str,
        "LocalPath": NotRequired[str],
    },
)

ClarifyCheckStepMetadataTypeDef = TypedDict(
    "ClarifyCheckStepMetadataTypeDef",
    {
        "CheckType": NotRequired[str],
        "BaselineUsedForDriftCheckConstraints": NotRequired[str],
        "CalculatedBaselineConstraints": NotRequired[str],
        "ModelPackageGroupName": NotRequired[str],
        "ViolationReport": NotRequired[str],
        "CheckJobArn": NotRequired[str],
        "SkipCheck": NotRequired[bool],
        "RegisterNewBaseline": NotRequired[bool],
    },
)

ClarifyInferenceConfigTypeDef = TypedDict(
    "ClarifyInferenceConfigTypeDef",
    {
        "FeaturesAttribute": NotRequired[str],
        "ContentTemplate": NotRequired[str],
        "MaxRecordCount": NotRequired[int],
        "MaxPayloadInMB": NotRequired[int],
        "ProbabilityIndex": NotRequired[int],
        "LabelIndex": NotRequired[int],
        "ProbabilityAttribute": NotRequired[str],
        "LabelAttribute": NotRequired[str],
        "LabelHeaders": NotRequired[Sequence[str]],
        "FeatureHeaders": NotRequired[Sequence[str]],
        "FeatureTypes": NotRequired[Sequence[ClarifyFeatureTypeType]],
    },
)

ClarifyShapBaselineConfigTypeDef = TypedDict(
    "ClarifyShapBaselineConfigTypeDef",
    {
        "MimeType": NotRequired[str],
        "ShapBaseline": NotRequired[str],
        "ShapBaselineUri": NotRequired[str],
    },
)

ClarifyTextConfigTypeDef = TypedDict(
    "ClarifyTextConfigTypeDef",
    {
        "Language": ClarifyTextLanguageType,
        "Granularity": ClarifyTextGranularityType,
    },
)

GitConfigTypeDef = TypedDict(
    "GitConfigTypeDef",
    {
        "RepositoryUrl": str,
        "Branch": NotRequired[str],
        "SecretArn": NotRequired[str],
    },
)

CodeRepositoryTypeDef = TypedDict(
    "CodeRepositoryTypeDef",
    {
        "RepositoryUrl": str,
    },
)

CognitoConfigTypeDef = TypedDict(
    "CognitoConfigTypeDef",
    {
        "UserPool": str,
        "ClientId": str,
    },
)

CognitoMemberDefinitionTypeDef = TypedDict(
    "CognitoMemberDefinitionTypeDef",
    {
        "UserPool": str,
        "UserGroup": str,
        "ClientId": str,
    },
)

CollectionConfigurationPaginatorTypeDef = TypedDict(
    "CollectionConfigurationPaginatorTypeDef",
    {
        "CollectionName": NotRequired[str],
        "CollectionParameters": NotRequired[Dict[str, str]],
    },
)

CollectionConfigurationTypeDef = TypedDict(
    "CollectionConfigurationTypeDef",
    {
        "CollectionName": NotRequired[str],
        "CollectionParameters": NotRequired[Mapping[str, str]],
    },
)

CompilationJobSummaryTypeDef = TypedDict(
    "CompilationJobSummaryTypeDef",
    {
        "CompilationJobName": str,
        "CompilationJobArn": str,
        "CreationTime": datetime,
        "CompilationJobStatus": CompilationJobStatusType,
        "CompilationStartTime": NotRequired[datetime],
        "CompilationEndTime": NotRequired[datetime],
        "CompilationTargetDevice": NotRequired[TargetDeviceType],
        "CompilationTargetPlatformOs": NotRequired[TargetPlatformOsType],
        "CompilationTargetPlatformArch": NotRequired[TargetPlatformArchType],
        "CompilationTargetPlatformAccelerator": NotRequired[TargetPlatformAcceleratorType],
        "LastModifiedTime": NotRequired[datetime],
    },
)

ConditionStepMetadataTypeDef = TypedDict(
    "ConditionStepMetadataTypeDef",
    {
        "Outcome": NotRequired[ConditionOutcomeType],
    },
)

MultiModelConfigTypeDef = TypedDict(
    "MultiModelConfigTypeDef",
    {
        "ModelCacheSetting": NotRequired[ModelCacheSettingType],
    },
)

ContextSourceTypeDef = TypedDict(
    "ContextSourceTypeDef",
    {
        "SourceUri": str,
        "SourceType": NotRequired[str],
        "SourceId": NotRequired[str],
    },
)

ContinuousParameterRangeSpecificationTypeDef = TypedDict(
    "ContinuousParameterRangeSpecificationTypeDef",
    {
        "MinValue": str,
        "MaxValue": str,
    },
)

ContinuousParameterRangeTypeDef = TypedDict(
    "ContinuousParameterRangeTypeDef",
    {
        "Name": str,
        "MinValue": str,
        "MaxValue": str,
        "ScalingType": NotRequired[HyperParameterScalingTypeType],
    },
)

ConvergenceDetectedTypeDef = TypedDict(
    "ConvergenceDetectedTypeDef",
    {
        "CompleteOnConvergence": NotRequired[CompleteOnConvergenceType],
    },
)

MetadataPropertiesTypeDef = TypedDict(
    "MetadataPropertiesTypeDef",
    {
        "CommitId": NotRequired[str],
        "Repository": NotRequired[str],
        "GeneratedBy": NotRequired[str],
        "ProjectId": NotRequired[str],
    },
)

ResourceSpecTypeDef = TypedDict(
    "ResourceSpecTypeDef",
    {
        "SageMakerImageArn": NotRequired[str],
        "SageMakerImageVersionArn": NotRequired[str],
        "InstanceType": NotRequired[AppInstanceTypeType],
        "LifecycleConfigArn": NotRequired[str],
    },
)

ModelDeployConfigTypeDef = TypedDict(
    "ModelDeployConfigTypeDef",
    {
        "AutoGenerateEndpointName": NotRequired[bool],
        "EndpointName": NotRequired[str],
    },
)

InputConfigTypeDef = TypedDict(
    "InputConfigTypeDef",
    {
        "S3Uri": str,
        "Framework": FrameworkType,
        "DataInputConfig": NotRequired[str],
        "FrameworkVersion": NotRequired[str],
    },
)

NeoVpcConfigTypeDef = TypedDict(
    "NeoVpcConfigTypeDef",
    {
        "SecurityGroupIds": Sequence[str],
        "Subnets": Sequence[str],
    },
)

StoppingConditionTypeDef = TypedDict(
    "StoppingConditionTypeDef",
    {
        "MaxRuntimeInSeconds": NotRequired[int],
        "MaxWaitTimeInSeconds": NotRequired[int],
    },
)

DataQualityAppSpecificationTypeDef = TypedDict(
    "DataQualityAppSpecificationTypeDef",
    {
        "ImageUri": str,
        "ContainerEntrypoint": NotRequired[Sequence[str]],
        "ContainerArguments": NotRequired[Sequence[str]],
        "RecordPreprocessorSourceUri": NotRequired[str],
        "PostAnalyticsProcessorSourceUri": NotRequired[str],
        "Environment": NotRequired[Mapping[str, str]],
    },
)

MonitoringStoppingConditionTypeDef = TypedDict(
    "MonitoringStoppingConditionTypeDef",
    {
        "MaxRuntimeInSeconds": int,
    },
)

EdgeOutputConfigTypeDef = TypedDict(
    "EdgeOutputConfigTypeDef",
    {
        "S3OutputLocation": str,
        "KmsKeyId": NotRequired[str],
        "PresetDeploymentType": NotRequired[Literal["GreengrassV2Component"]],
        "PresetDeploymentConfig": NotRequired[str],
    },
)

EdgeDeploymentModelConfigTypeDef = TypedDict(
    "EdgeDeploymentModelConfigTypeDef",
    {
        "ModelHandle": str,
        "EdgePackagingJobName": str,
    },
)

FeatureDefinitionTypeDef = TypedDict(
    "FeatureDefinitionTypeDef",
    {
        "FeatureName": NotRequired[str],
        "FeatureType": NotRequired[FeatureTypeType],
    },
)

FlowDefinitionOutputConfigTypeDef = TypedDict(
    "FlowDefinitionOutputConfigTypeDef",
    {
        "S3OutputPath": str,
        "KmsKeyId": NotRequired[str],
    },
)

HumanLoopRequestSourceTypeDef = TypedDict(
    "HumanLoopRequestSourceTypeDef",
    {
        "AwsManagedHumanLoopRequestSource": AwsManagedHumanLoopRequestSourceType,
    },
)

HubS3StorageConfigTypeDef = TypedDict(
    "HubS3StorageConfigTypeDef",
    {
        "S3OutputPath": NotRequired[str],
    },
)

UiTemplateTypeDef = TypedDict(
    "UiTemplateTypeDef",
    {
        "Content": str,
    },
)

CreateImageVersionRequestRequestTypeDef = TypedDict(
    "CreateImageVersionRequestRequestTypeDef",
    {
        "BaseImage": str,
        "ClientToken": str,
        "ImageName": str,
        "Aliases": NotRequired[Sequence[str]],
        "VendorGuidance": NotRequired[VendorGuidanceType],
        "JobType": NotRequired[JobTypeType],
        "MLFramework": NotRequired[str],
        "ProgrammingLang": NotRequired[str],
        "Processor": NotRequired[ProcessorType],
        "Horovod": NotRequired[bool],
        "ReleaseNotes": NotRequired[str],
    },
)

LabelingJobOutputConfigTypeDef = TypedDict(
    "LabelingJobOutputConfigTypeDef",
    {
        "S3OutputPath": str,
        "KmsKeyId": NotRequired[str],
        "SnsTopicArn": NotRequired[str],
    },
)

LabelingJobStoppingConditionsTypeDef = TypedDict(
    "LabelingJobStoppingConditionsTypeDef",
    {
        "MaxHumanLabeledObjectCount": NotRequired[int],
        "MaxPercentageOfInputDatasetLabeled": NotRequired[int],
    },
)

ModelBiasAppSpecificationTypeDef = TypedDict(
    "ModelBiasAppSpecificationTypeDef",
    {
        "ImageUri": str,
        "ConfigUri": str,
        "Environment": NotRequired[Mapping[str, str]],
    },
)

ModelCardExportOutputConfigTypeDef = TypedDict(
    "ModelCardExportOutputConfigTypeDef",
    {
        "S3OutputPath": str,
    },
)

ModelCardSecurityConfigTypeDef = TypedDict(
    "ModelCardSecurityConfigTypeDef",
    {
        "KmsKeyId": NotRequired[str],
    },
)

ModelExplainabilityAppSpecificationTypeDef = TypedDict(
    "ModelExplainabilityAppSpecificationTypeDef",
    {
        "ImageUri": str,
        "ConfigUri": str,
        "Environment": NotRequired[Mapping[str, str]],
    },
)

InferenceExecutionConfigTypeDef = TypedDict(
    "InferenceExecutionConfigTypeDef",
    {
        "Mode": InferenceExecutionModeType,
    },
)

ModelQualityAppSpecificationTypeDef = TypedDict(
    "ModelQualityAppSpecificationTypeDef",
    {
        "ImageUri": str,
        "ContainerEntrypoint": NotRequired[Sequence[str]],
        "ContainerArguments": NotRequired[Sequence[str]],
        "RecordPreprocessorSourceUri": NotRequired[str],
        "PostAnalyticsProcessorSourceUri": NotRequired[str],
        "ProblemType": NotRequired[MonitoringProblemTypeType],
        "Environment": NotRequired[Mapping[str, str]],
    },
)

InstanceMetadataServiceConfigurationTypeDef = TypedDict(
    "InstanceMetadataServiceConfigurationTypeDef",
    {
        "MinimumInstanceMetadataServiceVersion": str,
    },
)

NotebookInstanceLifecycleHookTypeDef = TypedDict(
    "NotebookInstanceLifecycleHookTypeDef",
    {
        "Content": NotRequired[str],
    },
)

ParallelismConfigurationTypeDef = TypedDict(
    "ParallelismConfigurationTypeDef",
    {
        "MaxParallelExecutionSteps": int,
    },
)

PipelineDefinitionS3LocationTypeDef = TypedDict(
    "PipelineDefinitionS3LocationTypeDef",
    {
        "Bucket": str,
        "ObjectKey": str,
        "VersionId": NotRequired[str],
    },
)

CreatePresignedDomainUrlRequestRequestTypeDef = TypedDict(
    "CreatePresignedDomainUrlRequestRequestTypeDef",
    {
        "DomainId": str,
        "UserProfileName": str,
        "SessionExpirationDurationInSeconds": NotRequired[int],
        "ExpiresInSeconds": NotRequired[int],
        "SpaceName": NotRequired[str],
    },
)

CreatePresignedNotebookInstanceUrlInputRequestTypeDef = TypedDict(
    "CreatePresignedNotebookInstanceUrlInputRequestTypeDef",
    {
        "NotebookInstanceName": str,
        "SessionExpirationDurationInSeconds": NotRequired[int],
    },
)

ExperimentConfigTypeDef = TypedDict(
    "ExperimentConfigTypeDef",
    {
        "ExperimentName": NotRequired[str],
        "TrialName": NotRequired[str],
        "TrialComponentDisplayName": NotRequired[str],
        "RunName": NotRequired[str],
    },
)

ProcessingStoppingConditionTypeDef = TypedDict(
    "ProcessingStoppingConditionTypeDef",
    {
        "MaxRuntimeInSeconds": int,
    },
)

DebugRuleConfigurationTypeDef = TypedDict(
    "DebugRuleConfigurationTypeDef",
    {
        "RuleConfigurationName": str,
        "RuleEvaluatorImage": str,
        "LocalPath": NotRequired[str],
        "S3OutputPath": NotRequired[str],
        "InstanceType": NotRequired[ProcessingInstanceTypeType],
        "VolumeSizeInGB": NotRequired[int],
        "RuleParameters": NotRequired[Mapping[str, str]],
    },
)

OutputDataConfigTypeDef = TypedDict(
    "OutputDataConfigTypeDef",
    {
        "S3OutputPath": str,
        "KmsKeyId": NotRequired[str],
        "CompressionType": NotRequired[OutputCompressionTypeType],
    },
)

ProfilerConfigTypeDef = TypedDict(
    "ProfilerConfigTypeDef",
    {
        "S3OutputPath": NotRequired[str],
        "ProfilingIntervalInMilliseconds": NotRequired[int],
        "ProfilingParameters": NotRequired[Mapping[str, str]],
        "DisableProfiler": NotRequired[bool],
    },
)

ProfilerRuleConfigurationTypeDef = TypedDict(
    "ProfilerRuleConfigurationTypeDef",
    {
        "RuleConfigurationName": str,
        "RuleEvaluatorImage": str,
        "LocalPath": NotRequired[str],
        "S3OutputPath": NotRequired[str],
        "InstanceType": NotRequired[ProcessingInstanceTypeType],
        "VolumeSizeInGB": NotRequired[int],
        "RuleParameters": NotRequired[Mapping[str, str]],
    },
)

RetryStrategyTypeDef = TypedDict(
    "RetryStrategyTypeDef",
    {
        "MaximumRetryAttempts": int,
    },
)

TensorBoardOutputConfigTypeDef = TypedDict(
    "TensorBoardOutputConfigTypeDef",
    {
        "S3OutputPath": str,
        "LocalPath": NotRequired[str],
    },
)

DataProcessingTypeDef = TypedDict(
    "DataProcessingTypeDef",
    {
        "InputFilter": NotRequired[str],
        "OutputFilter": NotRequired[str],
        "JoinSource": NotRequired[JoinSourceType],
    },
)

ModelClientConfigTypeDef = TypedDict(
    "ModelClientConfigTypeDef",
    {
        "InvocationsTimeoutInSeconds": NotRequired[int],
        "InvocationsMaxRetries": NotRequired[int],
    },
)

TransformOutputTypeDef = TypedDict(
    "TransformOutputTypeDef",
    {
        "S3OutputPath": str,
        "Accept": NotRequired[str],
        "AssembleWith": NotRequired[AssemblyTypeType],
        "KmsKeyId": NotRequired[str],
    },
)

TransformResourcesTypeDef = TypedDict(
    "TransformResourcesTypeDef",
    {
        "InstanceType": TransformInstanceTypeType,
        "InstanceCount": int,
        "VolumeKmsKeyId": NotRequired[str],
    },
)

TimestampTypeDef = Union[datetime, str]
TrialComponentArtifactTypeDef = TypedDict(
    "TrialComponentArtifactTypeDef",
    {
        "Value": str,
        "MediaType": NotRequired[str],
    },
)

TrialComponentParameterValueTypeDef = TypedDict(
    "TrialComponentParameterValueTypeDef",
    {
        "StringValue": NotRequired[str],
        "NumberValue": NotRequired[float],
    },
)

TrialComponentStatusTypeDef = TypedDict(
    "TrialComponentStatusTypeDef",
    {
        "PrimaryStatus": NotRequired[TrialComponentPrimaryStatusType],
        "Message": NotRequired[str],
    },
)

OidcConfigTypeDef = TypedDict(
    "OidcConfigTypeDef",
    {
        "ClientId": str,
        "ClientSecret": str,
        "Issuer": str,
        "AuthorizationEndpoint": str,
        "TokenEndpoint": str,
        "UserInfoEndpoint": str,
        "LogoutEndpoint": str,
        "JwksUri": str,
    },
)

SourceIpConfigTypeDef = TypedDict(
    "SourceIpConfigTypeDef",
    {
        "Cidrs": Sequence[str],
    },
)

WorkforceVpcConfigRequestTypeDef = TypedDict(
    "WorkforceVpcConfigRequestTypeDef",
    {
        "VpcId": NotRequired[str],
        "SecurityGroupIds": NotRequired[Sequence[str]],
        "Subnets": NotRequired[Sequence[str]],
    },
)

NotificationConfigurationTypeDef = TypedDict(
    "NotificationConfigurationTypeDef",
    {
        "NotificationTopicArn": NotRequired[str],
    },
)

CustomImageTypeDef = TypedDict(
    "CustomImageTypeDef",
    {
        "ImageName": str,
        "AppImageConfigName": str,
        "ImageVersionNumber": NotRequired[int],
    },
)

CustomizedMetricSpecificationTypeDef = TypedDict(
    "CustomizedMetricSpecificationTypeDef",
    {
        "MetricName": NotRequired[str],
        "Namespace": NotRequired[str],
        "Statistic": NotRequired[StatisticType],
    },
)

DataCaptureConfigSummaryTypeDef = TypedDict(
    "DataCaptureConfigSummaryTypeDef",
    {
        "EnableCapture": bool,
        "CaptureStatus": CaptureStatusType,
        "CurrentSamplingPercentage": int,
        "DestinationS3Uri": str,
        "KmsKeyId": str,
    },
)

DataCatalogConfigTypeDef = TypedDict(
    "DataCatalogConfigTypeDef",
    {
        "TableName": str,
        "Catalog": str,
        "Database": str,
    },
)

MonitoringConstraintsResourceTypeDef = TypedDict(
    "MonitoringConstraintsResourceTypeDef",
    {
        "S3Uri": NotRequired[str],
    },
)

MonitoringStatisticsResourceTypeDef = TypedDict(
    "MonitoringStatisticsResourceTypeDef",
    {
        "S3Uri": NotRequired[str],
    },
)

EndpointInputTypeDef = TypedDict(
    "EndpointInputTypeDef",
    {
        "EndpointName": str,
        "LocalPath": str,
        "S3InputMode": NotRequired[ProcessingS3InputModeType],
        "S3DataDistributionType": NotRequired[ProcessingS3DataDistributionTypeType],
        "FeaturesAttribute": NotRequired[str],
        "InferenceAttribute": NotRequired[str],
        "ProbabilityAttribute": NotRequired[str],
        "ProbabilityThresholdAttribute": NotRequired[float],
        "StartTimeOffset": NotRequired[str],
        "EndTimeOffset": NotRequired[str],
    },
)

FileSystemDataSourceTypeDef = TypedDict(
    "FileSystemDataSourceTypeDef",
    {
        "FileSystemId": str,
        "FileSystemAccessMode": FileSystemAccessModeType,
        "FileSystemType": FileSystemTypeType,
        "DirectoryPath": str,
    },
)

S3DataSourcePaginatorTypeDef = TypedDict(
    "S3DataSourcePaginatorTypeDef",
    {
        "S3DataType": S3DataTypeType,
        "S3Uri": str,
        "S3DataDistributionType": NotRequired[S3DataDistributionType],
        "AttributeNames": NotRequired[List[str]],
        "InstanceGroupNames": NotRequired[List[str]],
    },
)

S3DataSourceTypeDef = TypedDict(
    "S3DataSourceTypeDef",
    {
        "S3DataType": S3DataTypeType,
        "S3Uri": str,
        "S3DataDistributionType": NotRequired[S3DataDistributionType],
        "AttributeNames": NotRequired[Sequence[str]],
        "InstanceGroupNames": NotRequired[Sequence[str]],
    },
)

RedshiftDatasetDefinitionTypeDef = TypedDict(
    "RedshiftDatasetDefinitionTypeDef",
    {
        "ClusterId": str,
        "Database": str,
        "DbUser": str,
        "QueryString": str,
        "ClusterRoleArn": str,
        "OutputS3Uri": str,
        "OutputFormat": RedshiftResultFormatType,
        "KmsKeyId": NotRequired[str],
        "OutputCompression": NotRequired[RedshiftResultCompressionTypeType],
    },
)

DebugRuleConfigurationPaginatorTypeDef = TypedDict(
    "DebugRuleConfigurationPaginatorTypeDef",
    {
        "RuleConfigurationName": str,
        "RuleEvaluatorImage": str,
        "LocalPath": NotRequired[str],
        "S3OutputPath": NotRequired[str],
        "InstanceType": NotRequired[ProcessingInstanceTypeType],
        "VolumeSizeInGB": NotRequired[int],
        "RuleParameters": NotRequired[Dict[str, str]],
    },
)

DebugRuleEvaluationStatusTypeDef = TypedDict(
    "DebugRuleEvaluationStatusTypeDef",
    {
        "RuleConfigurationName": NotRequired[str],
        "RuleEvaluationJobArn": NotRequired[str],
        "RuleEvaluationStatus": NotRequired[RuleEvaluationStatusType],
        "StatusDetails": NotRequired[str],
        "LastModifiedTime": NotRequired[datetime],
    },
)

DeleteActionRequestRequestTypeDef = TypedDict(
    "DeleteActionRequestRequestTypeDef",
    {
        "ActionName": str,
    },
)

DeleteAlgorithmInputRequestTypeDef = TypedDict(
    "DeleteAlgorithmInputRequestTypeDef",
    {
        "AlgorithmName": str,
    },
)

DeleteAppImageConfigRequestRequestTypeDef = TypedDict(
    "DeleteAppImageConfigRequestRequestTypeDef",
    {
        "AppImageConfigName": str,
    },
)

DeleteAppRequestRequestTypeDef = TypedDict(
    "DeleteAppRequestRequestTypeDef",
    {
        "DomainId": str,
        "AppType": AppTypeType,
        "AppName": str,
        "UserProfileName": NotRequired[str],
        "SpaceName": NotRequired[str],
    },
)

DeleteAssociationRequestRequestTypeDef = TypedDict(
    "DeleteAssociationRequestRequestTypeDef",
    {
        "SourceArn": str,
        "DestinationArn": str,
    },
)

DeleteCodeRepositoryInputRequestTypeDef = TypedDict(
    "DeleteCodeRepositoryInputRequestTypeDef",
    {
        "CodeRepositoryName": str,
    },
)

DeleteContextRequestRequestTypeDef = TypedDict(
    "DeleteContextRequestRequestTypeDef",
    {
        "ContextName": str,
    },
)

DeleteDataQualityJobDefinitionRequestRequestTypeDef = TypedDict(
    "DeleteDataQualityJobDefinitionRequestRequestTypeDef",
    {
        "JobDefinitionName": str,
    },
)

DeleteDeviceFleetRequestRequestTypeDef = TypedDict(
    "DeleteDeviceFleetRequestRequestTypeDef",
    {
        "DeviceFleetName": str,
    },
)

RetentionPolicyTypeDef = TypedDict(
    "RetentionPolicyTypeDef",
    {
        "HomeEfsFileSystem": NotRequired[RetentionTypeType],
    },
)

DeleteEdgeDeploymentPlanRequestRequestTypeDef = TypedDict(
    "DeleteEdgeDeploymentPlanRequestRequestTypeDef",
    {
        "EdgeDeploymentPlanName": str,
    },
)

DeleteEdgeDeploymentStageRequestRequestTypeDef = TypedDict(
    "DeleteEdgeDeploymentStageRequestRequestTypeDef",
    {
        "EdgeDeploymentPlanName": str,
        "StageName": str,
    },
)

DeleteEndpointConfigInputRequestTypeDef = TypedDict(
    "DeleteEndpointConfigInputRequestTypeDef",
    {
        "EndpointConfigName": str,
    },
)

DeleteEndpointInputRequestTypeDef = TypedDict(
    "DeleteEndpointInputRequestTypeDef",
    {
        "EndpointName": str,
    },
)

DeleteExperimentRequestRequestTypeDef = TypedDict(
    "DeleteExperimentRequestRequestTypeDef",
    {
        "ExperimentName": str,
    },
)

DeleteFeatureGroupRequestRequestTypeDef = TypedDict(
    "DeleteFeatureGroupRequestRequestTypeDef",
    {
        "FeatureGroupName": str,
    },
)

DeleteFlowDefinitionRequestRequestTypeDef = TypedDict(
    "DeleteFlowDefinitionRequestRequestTypeDef",
    {
        "FlowDefinitionName": str,
    },
)

DeleteHubContentRequestRequestTypeDef = TypedDict(
    "DeleteHubContentRequestRequestTypeDef",
    {
        "HubName": str,
        "HubContentType": HubContentTypeType,
        "HubContentName": str,
        "HubContentVersion": str,
    },
)

DeleteHubRequestRequestTypeDef = TypedDict(
    "DeleteHubRequestRequestTypeDef",
    {
        "HubName": str,
    },
)

DeleteHumanTaskUiRequestRequestTypeDef = TypedDict(
    "DeleteHumanTaskUiRequestRequestTypeDef",
    {
        "HumanTaskUiName": str,
    },
)

DeleteImageRequestRequestTypeDef = TypedDict(
    "DeleteImageRequestRequestTypeDef",
    {
        "ImageName": str,
    },
)

DeleteImageVersionRequestRequestTypeDef = TypedDict(
    "DeleteImageVersionRequestRequestTypeDef",
    {
        "ImageName": str,
        "Version": NotRequired[int],
        "Alias": NotRequired[str],
    },
)

DeleteInferenceExperimentRequestRequestTypeDef = TypedDict(
    "DeleteInferenceExperimentRequestRequestTypeDef",
    {
        "Name": str,
    },
)

DeleteModelBiasJobDefinitionRequestRequestTypeDef = TypedDict(
    "DeleteModelBiasJobDefinitionRequestRequestTypeDef",
    {
        "JobDefinitionName": str,
    },
)

DeleteModelCardRequestRequestTypeDef = TypedDict(
    "DeleteModelCardRequestRequestTypeDef",
    {
        "ModelCardName": str,
    },
)

DeleteModelExplainabilityJobDefinitionRequestRequestTypeDef = TypedDict(
    "DeleteModelExplainabilityJobDefinitionRequestRequestTypeDef",
    {
        "JobDefinitionName": str,
    },
)

DeleteModelInputRequestTypeDef = TypedDict(
    "DeleteModelInputRequestTypeDef",
    {
        "ModelName": str,
    },
)

DeleteModelPackageGroupInputRequestTypeDef = TypedDict(
    "DeleteModelPackageGroupInputRequestTypeDef",
    {
        "ModelPackageGroupName": str,
    },
)

DeleteModelPackageGroupPolicyInputRequestTypeDef = TypedDict(
    "DeleteModelPackageGroupPolicyInputRequestTypeDef",
    {
        "ModelPackageGroupName": str,
    },
)

DeleteModelPackageInputRequestTypeDef = TypedDict(
    "DeleteModelPackageInputRequestTypeDef",
    {
        "ModelPackageName": str,
    },
)

DeleteModelQualityJobDefinitionRequestRequestTypeDef = TypedDict(
    "DeleteModelQualityJobDefinitionRequestRequestTypeDef",
    {
        "JobDefinitionName": str,
    },
)

DeleteMonitoringScheduleRequestRequestTypeDef = TypedDict(
    "DeleteMonitoringScheduleRequestRequestTypeDef",
    {
        "MonitoringScheduleName": str,
    },
)

DeleteNotebookInstanceInputRequestTypeDef = TypedDict(
    "DeleteNotebookInstanceInputRequestTypeDef",
    {
        "NotebookInstanceName": str,
    },
)

DeleteNotebookInstanceLifecycleConfigInputRequestTypeDef = TypedDict(
    "DeleteNotebookInstanceLifecycleConfigInputRequestTypeDef",
    {
        "NotebookInstanceLifecycleConfigName": str,
    },
)

DeletePipelineRequestRequestTypeDef = TypedDict(
    "DeletePipelineRequestRequestTypeDef",
    {
        "PipelineName": str,
        "ClientRequestToken": str,
    },
)

DeleteProjectInputRequestTypeDef = TypedDict(
    "DeleteProjectInputRequestTypeDef",
    {
        "ProjectName": str,
    },
)

DeleteSpaceRequestRequestTypeDef = TypedDict(
    "DeleteSpaceRequestRequestTypeDef",
    {
        "DomainId": str,
        "SpaceName": str,
    },
)

DeleteStudioLifecycleConfigRequestRequestTypeDef = TypedDict(
    "DeleteStudioLifecycleConfigRequestRequestTypeDef",
    {
        "StudioLifecycleConfigName": str,
    },
)

DeleteTagsInputRequestTypeDef = TypedDict(
    "DeleteTagsInputRequestTypeDef",
    {
        "ResourceArn": str,
        "TagKeys": Sequence[str],
    },
)

DeleteTrialComponentRequestRequestTypeDef = TypedDict(
    "DeleteTrialComponentRequestRequestTypeDef",
    {
        "TrialComponentName": str,
    },
)

DeleteTrialRequestRequestTypeDef = TypedDict(
    "DeleteTrialRequestRequestTypeDef",
    {
        "TrialName": str,
    },
)

DeleteUserProfileRequestRequestTypeDef = TypedDict(
    "DeleteUserProfileRequestRequestTypeDef",
    {
        "DomainId": str,
        "UserProfileName": str,
    },
)

DeleteWorkforceRequestRequestTypeDef = TypedDict(
    "DeleteWorkforceRequestRequestTypeDef",
    {
        "WorkforceName": str,
    },
)

DeleteWorkteamRequestRequestTypeDef = TypedDict(
    "DeleteWorkteamRequestRequestTypeDef",
    {
        "WorkteamName": str,
    },
)

DeployedImageTypeDef = TypedDict(
    "DeployedImageTypeDef",
    {
        "SpecifiedImage": NotRequired[str],
        "ResolvedImage": NotRequired[str],
        "ResolutionTime": NotRequired[datetime],
    },
)

RealTimeInferenceRecommendationTypeDef = TypedDict(
    "RealTimeInferenceRecommendationTypeDef",
    {
        "RecommendationId": str,
        "InstanceType": ProductionVariantInstanceTypeType,
        "Environment": NotRequired[Dict[str, str]],
    },
)

DeviceSelectionConfigTypeDef = TypedDict(
    "DeviceSelectionConfigTypeDef",
    {
        "DeviceSubsetType": DeviceSubsetTypeType,
        "Percentage": NotRequired[int],
        "DeviceNames": NotRequired[Sequence[str]],
        "DeviceNameContains": NotRequired[str],
    },
)

EdgeDeploymentConfigTypeDef = TypedDict(
    "EdgeDeploymentConfigTypeDef",
    {
        "FailureHandlingPolicy": FailureHandlingPolicyType,
    },
)

EdgeDeploymentStatusTypeDef = TypedDict(
    "EdgeDeploymentStatusTypeDef",
    {
        "StageStatus": StageStatusType,
        "EdgeDeploymentSuccessInStage": int,
        "EdgeDeploymentPendingInStage": int,
        "EdgeDeploymentFailedInStage": int,
        "EdgeDeploymentStatusMessage": NotRequired[str],
        "EdgeDeploymentStageStartTime": NotRequired[datetime],
    },
)

DeregisterDevicesRequestRequestTypeDef = TypedDict(
    "DeregisterDevicesRequestRequestTypeDef",
    {
        "DeviceFleetName": str,
        "DeviceNames": Sequence[str],
    },
)

DerivedInformationTypeDef = TypedDict(
    "DerivedInformationTypeDef",
    {
        "DerivedDataInputConfig": NotRequired[str],
    },
)

DescribeActionRequestRequestTypeDef = TypedDict(
    "DescribeActionRequestRequestTypeDef",
    {
        "ActionName": str,
    },
)

DescribeAlgorithmInputRequestTypeDef = TypedDict(
    "DescribeAlgorithmInputRequestTypeDef",
    {
        "AlgorithmName": str,
    },
)

DescribeAppImageConfigRequestRequestTypeDef = TypedDict(
    "DescribeAppImageConfigRequestRequestTypeDef",
    {
        "AppImageConfigName": str,
    },
)

DescribeAppRequestRequestTypeDef = TypedDict(
    "DescribeAppRequestRequestTypeDef",
    {
        "DomainId": str,
        "AppType": AppTypeType,
        "AppName": str,
        "UserProfileName": NotRequired[str],
        "SpaceName": NotRequired[str],
    },
)

DescribeArtifactRequestRequestTypeDef = TypedDict(
    "DescribeArtifactRequestRequestTypeDef",
    {
        "ArtifactArn": str,
    },
)

DescribeAutoMLJobRequestRequestTypeDef = TypedDict(
    "DescribeAutoMLJobRequestRequestTypeDef",
    {
        "AutoMLJobName": str,
    },
)

ModelDeployResultTypeDef = TypedDict(
    "ModelDeployResultTypeDef",
    {
        "EndpointName": NotRequired[str],
    },
)

DescribeAutoMLJobV2RequestRequestTypeDef = TypedDict(
    "DescribeAutoMLJobV2RequestRequestTypeDef",
    {
        "AutoMLJobName": str,
    },
)

DescribeCodeRepositoryInputRequestTypeDef = TypedDict(
    "DescribeCodeRepositoryInputRequestTypeDef",
    {
        "CodeRepositoryName": str,
    },
)

DescribeCompilationJobRequestRequestTypeDef = TypedDict(
    "DescribeCompilationJobRequestRequestTypeDef",
    {
        "CompilationJobName": str,
    },
)

ModelArtifactsTypeDef = TypedDict(
    "ModelArtifactsTypeDef",
    {
        "S3ModelArtifacts": str,
    },
)

ModelDigestsTypeDef = TypedDict(
    "ModelDigestsTypeDef",
    {
        "ArtifactDigest": NotRequired[str],
    },
)

DescribeContextRequestRequestTypeDef = TypedDict(
    "DescribeContextRequestRequestTypeDef",
    {
        "ContextName": str,
    },
)

DescribeDataQualityJobDefinitionRequestRequestTypeDef = TypedDict(
    "DescribeDataQualityJobDefinitionRequestRequestTypeDef",
    {
        "JobDefinitionName": str,
    },
)

DescribeDeviceFleetRequestRequestTypeDef = TypedDict(
    "DescribeDeviceFleetRequestRequestTypeDef",
    {
        "DeviceFleetName": str,
    },
)

DescribeDeviceRequestRequestTypeDef = TypedDict(
    "DescribeDeviceRequestRequestTypeDef",
    {
        "DeviceName": str,
        "DeviceFleetName": str,
        "NextToken": NotRequired[str],
    },
)

EdgeModelTypeDef = TypedDict(
    "EdgeModelTypeDef",
    {
        "ModelName": str,
        "ModelVersion": str,
        "LatestSampleTime": NotRequired[datetime],
        "LatestInference": NotRequired[datetime],
    },
)

DescribeDomainRequestRequestTypeDef = TypedDict(
    "DescribeDomainRequestRequestTypeDef",
    {
        "DomainId": str,
    },
)

DescribeEdgeDeploymentPlanRequestRequestTypeDef = TypedDict(
    "DescribeEdgeDeploymentPlanRequestRequestTypeDef",
    {
        "EdgeDeploymentPlanName": str,
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
    },
)

DescribeEdgePackagingJobRequestRequestTypeDef = TypedDict(
    "DescribeEdgePackagingJobRequestRequestTypeDef",
    {
        "EdgePackagingJobName": str,
    },
)

EdgePresetDeploymentOutputTypeDef = TypedDict(
    "EdgePresetDeploymentOutputTypeDef",
    {
        "Type": Literal["GreengrassV2Component"],
        "Artifact": NotRequired[str],
        "Status": NotRequired[EdgePresetDeploymentStatusType],
        "StatusMessage": NotRequired[str],
    },
)

DescribeEndpointConfigInputRequestTypeDef = TypedDict(
    "DescribeEndpointConfigInputRequestTypeDef",
    {
        "EndpointConfigName": str,
    },
)

WaiterConfigTypeDef = TypedDict(
    "WaiterConfigTypeDef",
    {
        "Delay": NotRequired[int],
        "MaxAttempts": NotRequired[int],
    },
)

DescribeEndpointInputRequestTypeDef = TypedDict(
    "DescribeEndpointInputRequestTypeDef",
    {
        "EndpointName": str,
    },
)

DescribeExperimentRequestRequestTypeDef = TypedDict(
    "DescribeExperimentRequestRequestTypeDef",
    {
        "ExperimentName": str,
    },
)

ExperimentSourceTypeDef = TypedDict(
    "ExperimentSourceTypeDef",
    {
        "SourceArn": str,
        "SourceType": NotRequired[str],
    },
)

DescribeFeatureGroupRequestRequestTypeDef = TypedDict(
    "DescribeFeatureGroupRequestRequestTypeDef",
    {
        "FeatureGroupName": str,
        "NextToken": NotRequired[str],
    },
)

LastUpdateStatusTypeDef = TypedDict(
    "LastUpdateStatusTypeDef",
    {
        "Status": LastUpdateStatusValueType,
        "FailureReason": NotRequired[str],
    },
)

OfflineStoreStatusTypeDef = TypedDict(
    "OfflineStoreStatusTypeDef",
    {
        "Status": OfflineStoreStatusValueType,
        "BlockedReason": NotRequired[str],
    },
)

DescribeFeatureMetadataRequestRequestTypeDef = TypedDict(
    "DescribeFeatureMetadataRequestRequestTypeDef",
    {
        "FeatureGroupName": str,
        "FeatureName": str,
    },
)

FeatureParameterTypeDef = TypedDict(
    "FeatureParameterTypeDef",
    {
        "Key": NotRequired[str],
        "Value": NotRequired[str],
    },
)

DescribeFlowDefinitionRequestRequestTypeDef = TypedDict(
    "DescribeFlowDefinitionRequestRequestTypeDef",
    {
        "FlowDefinitionName": str,
    },
)

DescribeHubContentRequestRequestTypeDef = TypedDict(
    "DescribeHubContentRequestRequestTypeDef",
    {
        "HubName": str,
        "HubContentType": HubContentTypeType,
        "HubContentName": str,
        "HubContentVersion": NotRequired[str],
    },
)

HubContentDependencyTypeDef = TypedDict(
    "HubContentDependencyTypeDef",
    {
        "DependencyOriginPath": NotRequired[str],
        "DependencyCopyPath": NotRequired[str],
    },
)

DescribeHubRequestRequestTypeDef = TypedDict(
    "DescribeHubRequestRequestTypeDef",
    {
        "HubName": str,
    },
)

DescribeHumanTaskUiRequestRequestTypeDef = TypedDict(
    "DescribeHumanTaskUiRequestRequestTypeDef",
    {
        "HumanTaskUiName": str,
    },
)

UiTemplateInfoTypeDef = TypedDict(
    "UiTemplateInfoTypeDef",
    {
        "Url": NotRequired[str],
        "ContentSha256": NotRequired[str],
    },
)

DescribeHyperParameterTuningJobRequestRequestTypeDef = TypedDict(
    "DescribeHyperParameterTuningJobRequestRequestTypeDef",
    {
        "HyperParameterTuningJobName": str,
    },
)

HyperParameterTuningJobCompletionDetailsTypeDef = TypedDict(
    "HyperParameterTuningJobCompletionDetailsTypeDef",
    {
        "NumberOfTrainingJobsObjectiveNotImproving": NotRequired[int],
        "ConvergenceDetectedTime": NotRequired[datetime],
    },
)

HyperParameterTuningJobConsumedResourcesTypeDef = TypedDict(
    "HyperParameterTuningJobConsumedResourcesTypeDef",
    {
        "RuntimeInSeconds": NotRequired[int],
    },
)

ObjectiveStatusCountersTypeDef = TypedDict(
    "ObjectiveStatusCountersTypeDef",
    {
        "Succeeded": NotRequired[int],
        "Pending": NotRequired[int],
        "Failed": NotRequired[int],
    },
)

TrainingJobStatusCountersTypeDef = TypedDict(
    "TrainingJobStatusCountersTypeDef",
    {
        "Completed": NotRequired[int],
        "InProgress": NotRequired[int],
        "RetryableError": NotRequired[int],
        "NonRetryableError": NotRequired[int],
        "Stopped": NotRequired[int],
    },
)

DescribeImageRequestRequestTypeDef = TypedDict(
    "DescribeImageRequestRequestTypeDef",
    {
        "ImageName": str,
    },
)

DescribeImageVersionRequestRequestTypeDef = TypedDict(
    "DescribeImageVersionRequestRequestTypeDef",
    {
        "ImageName": str,
        "Version": NotRequired[int],
        "Alias": NotRequired[str],
    },
)

DescribeInferenceExperimentRequestRequestTypeDef = TypedDict(
    "DescribeInferenceExperimentRequestRequestTypeDef",
    {
        "Name": str,
    },
)

EndpointMetadataTypeDef = TypedDict(
    "EndpointMetadataTypeDef",
    {
        "EndpointName": str,
        "EndpointConfigName": NotRequired[str],
        "EndpointStatus": NotRequired[EndpointStatusType],
        "FailureReason": NotRequired[str],
    },
)

DescribeInferenceRecommendationsJobRequestRequestTypeDef = TypedDict(
    "DescribeInferenceRecommendationsJobRequestRequestTypeDef",
    {
        "JobName": str,
    },
)

DescribeLabelingJobRequestRequestTypeDef = TypedDict(
    "DescribeLabelingJobRequestRequestTypeDef",
    {
        "LabelingJobName": str,
    },
)

LabelCountersTypeDef = TypedDict(
    "LabelCountersTypeDef",
    {
        "TotalLabeled": NotRequired[int],
        "HumanLabeled": NotRequired[int],
        "MachineLabeled": NotRequired[int],
        "FailedNonRetryableError": NotRequired[int],
        "Unlabeled": NotRequired[int],
    },
)

LabelingJobOutputTypeDef = TypedDict(
    "LabelingJobOutputTypeDef",
    {
        "OutputDatasetS3Uri": str,
        "FinalActiveLearningModelArn": NotRequired[str],
    },
)

DescribeLineageGroupRequestRequestTypeDef = TypedDict(
    "DescribeLineageGroupRequestRequestTypeDef",
    {
        "LineageGroupName": str,
    },
)

DescribeModelBiasJobDefinitionRequestRequestTypeDef = TypedDict(
    "DescribeModelBiasJobDefinitionRequestRequestTypeDef",
    {
        "JobDefinitionName": str,
    },
)

DescribeModelCardExportJobRequestRequestTypeDef = TypedDict(
    "DescribeModelCardExportJobRequestRequestTypeDef",
    {
        "ModelCardExportJobArn": str,
    },
)

ModelCardExportArtifactsTypeDef = TypedDict(
    "ModelCardExportArtifactsTypeDef",
    {
        "S3ExportArtifacts": str,
    },
)

DescribeModelCardRequestRequestTypeDef = TypedDict(
    "DescribeModelCardRequestRequestTypeDef",
    {
        "ModelCardName": str,
        "ModelCardVersion": NotRequired[int],
    },
)

DescribeModelExplainabilityJobDefinitionRequestRequestTypeDef = TypedDict(
    "DescribeModelExplainabilityJobDefinitionRequestRequestTypeDef",
    {
        "JobDefinitionName": str,
    },
)

DescribeModelInputRequestTypeDef = TypedDict(
    "DescribeModelInputRequestTypeDef",
    {
        "ModelName": str,
    },
)

DescribeModelPackageGroupInputRequestTypeDef = TypedDict(
    "DescribeModelPackageGroupInputRequestTypeDef",
    {
        "ModelPackageGroupName": str,
    },
)

DescribeModelPackageInputRequestTypeDef = TypedDict(
    "DescribeModelPackageInputRequestTypeDef",
    {
        "ModelPackageName": str,
    },
)

DescribeModelQualityJobDefinitionRequestRequestTypeDef = TypedDict(
    "DescribeModelQualityJobDefinitionRequestRequestTypeDef",
    {
        "JobDefinitionName": str,
    },
)

DescribeMonitoringScheduleRequestRequestTypeDef = TypedDict(
    "DescribeMonitoringScheduleRequestRequestTypeDef",
    {
        "MonitoringScheduleName": str,
    },
)

MonitoringExecutionSummaryTypeDef = TypedDict(
    "MonitoringExecutionSummaryTypeDef",
    {
        "MonitoringScheduleName": str,
        "ScheduledTime": datetime,
        "CreationTime": datetime,
        "LastModifiedTime": datetime,
        "MonitoringExecutionStatus": ExecutionStatusType,
        "ProcessingJobArn": NotRequired[str],
        "EndpointName": NotRequired[str],
        "FailureReason": NotRequired[str],
        "MonitoringJobDefinitionName": NotRequired[str],
        "MonitoringType": NotRequired[MonitoringTypeType],
    },
)

DescribeNotebookInstanceInputRequestTypeDef = TypedDict(
    "DescribeNotebookInstanceInputRequestTypeDef",
    {
        "NotebookInstanceName": str,
    },
)

DescribeNotebookInstanceLifecycleConfigInputRequestTypeDef = TypedDict(
    "DescribeNotebookInstanceLifecycleConfigInputRequestTypeDef",
    {
        "NotebookInstanceLifecycleConfigName": str,
    },
)

DescribePipelineDefinitionForExecutionRequestRequestTypeDef = TypedDict(
    "DescribePipelineDefinitionForExecutionRequestRequestTypeDef",
    {
        "PipelineExecutionArn": str,
    },
)

DescribePipelineExecutionRequestRequestTypeDef = TypedDict(
    "DescribePipelineExecutionRequestRequestTypeDef",
    {
        "PipelineExecutionArn": str,
    },
)

PipelineExperimentConfigTypeDef = TypedDict(
    "PipelineExperimentConfigTypeDef",
    {
        "ExperimentName": NotRequired[str],
        "TrialName": NotRequired[str],
    },
)

DescribePipelineRequestRequestTypeDef = TypedDict(
    "DescribePipelineRequestRequestTypeDef",
    {
        "PipelineName": str,
    },
)

DescribeProcessingJobRequestRequestTypeDef = TypedDict(
    "DescribeProcessingJobRequestRequestTypeDef",
    {
        "ProcessingJobName": str,
    },
)

DescribeProjectInputRequestTypeDef = TypedDict(
    "DescribeProjectInputRequestTypeDef",
    {
        "ProjectName": str,
    },
)

ServiceCatalogProvisionedProductDetailsTypeDef = TypedDict(
    "ServiceCatalogProvisionedProductDetailsTypeDef",
    {
        "ProvisionedProductId": NotRequired[str],
        "ProvisionedProductStatusMessage": NotRequired[str],
    },
)

DescribeSpaceRequestRequestTypeDef = TypedDict(
    "DescribeSpaceRequestRequestTypeDef",
    {
        "DomainId": str,
        "SpaceName": str,
    },
)

DescribeStudioLifecycleConfigRequestRequestTypeDef = TypedDict(
    "DescribeStudioLifecycleConfigRequestRequestTypeDef",
    {
        "StudioLifecycleConfigName": str,
    },
)

DescribeSubscribedWorkteamRequestRequestTypeDef = TypedDict(
    "DescribeSubscribedWorkteamRequestRequestTypeDef",
    {
        "WorkteamArn": str,
    },
)

SubscribedWorkteamTypeDef = TypedDict(
    "SubscribedWorkteamTypeDef",
    {
        "WorkteamArn": str,
        "MarketplaceTitle": NotRequired[str],
        "SellerName": NotRequired[str],
        "MarketplaceDescription": NotRequired[str],
        "ListingId": NotRequired[str],
    },
)

DescribeTrainingJobRequestRequestTypeDef = TypedDict(
    "DescribeTrainingJobRequestRequestTypeDef",
    {
        "TrainingJobName": str,
    },
)

MetricDataTypeDef = TypedDict(
    "MetricDataTypeDef",
    {
        "MetricName": NotRequired[str],
        "Value": NotRequired[float],
        "Timestamp": NotRequired[datetime],
    },
)

ProfilerRuleEvaluationStatusTypeDef = TypedDict(
    "ProfilerRuleEvaluationStatusTypeDef",
    {
        "RuleConfigurationName": NotRequired[str],
        "RuleEvaluationJobArn": NotRequired[str],
        "RuleEvaluationStatus": NotRequired[RuleEvaluationStatusType],
        "StatusDetails": NotRequired[str],
        "LastModifiedTime": NotRequired[datetime],
    },
)

SecondaryStatusTransitionTypeDef = TypedDict(
    "SecondaryStatusTransitionTypeDef",
    {
        "Status": SecondaryStatusType,
        "StartTime": datetime,
        "EndTime": NotRequired[datetime],
        "StatusMessage": NotRequired[str],
    },
)

WarmPoolStatusTypeDef = TypedDict(
    "WarmPoolStatusTypeDef",
    {
        "Status": WarmPoolResourceStatusType,
        "ResourceRetainedBillableTimeInSeconds": NotRequired[int],
        "ReusedByJob": NotRequired[str],
    },
)

DescribeTransformJobRequestRequestTypeDef = TypedDict(
    "DescribeTransformJobRequestRequestTypeDef",
    {
        "TransformJobName": str,
    },
)

DescribeTrialComponentRequestRequestTypeDef = TypedDict(
    "DescribeTrialComponentRequestRequestTypeDef",
    {
        "TrialComponentName": str,
    },
)

TrialComponentMetricSummaryTypeDef = TypedDict(
    "TrialComponentMetricSummaryTypeDef",
    {
        "MetricName": NotRequired[str],
        "SourceArn": NotRequired[str],
        "TimeStamp": NotRequired[datetime],
        "Max": NotRequired[float],
        "Min": NotRequired[float],
        "Last": NotRequired[float],
        "Count": NotRequired[int],
        "Avg": NotRequired[float],
        "StdDev": NotRequired[float],
    },
)

TrialComponentSourceTypeDef = TypedDict(
    "TrialComponentSourceTypeDef",
    {
        "SourceArn": str,
        "SourceType": NotRequired[str],
    },
)

DescribeTrialRequestRequestTypeDef = TypedDict(
    "DescribeTrialRequestRequestTypeDef",
    {
        "TrialName": str,
    },
)

TrialSourceTypeDef = TypedDict(
    "TrialSourceTypeDef",
    {
        "SourceArn": str,
        "SourceType": NotRequired[str],
    },
)

DescribeUserProfileRequestRequestTypeDef = TypedDict(
    "DescribeUserProfileRequestRequestTypeDef",
    {
        "DomainId": str,
        "UserProfileName": str,
    },
)

DescribeWorkforceRequestRequestTypeDef = TypedDict(
    "DescribeWorkforceRequestRequestTypeDef",
    {
        "WorkforceName": str,
    },
)

DescribeWorkteamRequestRequestTypeDef = TypedDict(
    "DescribeWorkteamRequestRequestTypeDef",
    {
        "WorkteamName": str,
    },
)

ProductionVariantServerlessUpdateConfigTypeDef = TypedDict(
    "ProductionVariantServerlessUpdateConfigTypeDef",
    {
        "MaxConcurrency": NotRequired[int],
        "ProvisionedConcurrency": NotRequired[int],
    },
)

DeviceDeploymentSummaryTypeDef = TypedDict(
    "DeviceDeploymentSummaryTypeDef",
    {
        "EdgeDeploymentPlanArn": str,
        "EdgeDeploymentPlanName": str,
        "StageName": str,
        "DeviceName": str,
        "DeviceArn": str,
        "DeployedStageName": NotRequired[str],
        "DeviceFleetName": NotRequired[str],
        "DeviceDeploymentStatus": NotRequired[DeviceDeploymentStatusType],
        "DeviceDeploymentStatusMessage": NotRequired[str],
        "Description": NotRequired[str],
        "DeploymentStartTime": NotRequired[datetime],
    },
)

DeviceFleetSummaryTypeDef = TypedDict(
    "DeviceFleetSummaryTypeDef",
    {
        "DeviceFleetArn": str,
        "DeviceFleetName": str,
        "CreationTime": NotRequired[datetime],
        "LastModifiedTime": NotRequired[datetime],
    },
)

DeviceStatsTypeDef = TypedDict(
    "DeviceStatsTypeDef",
    {
        "ConnectedDeviceCount": int,
        "RegisteredDeviceCount": int,
    },
)

EdgeModelSummaryTypeDef = TypedDict(
    "EdgeModelSummaryTypeDef",
    {
        "ModelName": str,
        "ModelVersion": str,
    },
)

DeviceTypeDef = TypedDict(
    "DeviceTypeDef",
    {
        "DeviceName": str,
        "Description": NotRequired[str],
        "IotThingName": NotRequired[str],
    },
)

DisassociateTrialComponentRequestRequestTypeDef = TypedDict(
    "DisassociateTrialComponentRequestRequestTypeDef",
    {
        "TrialComponentName": str,
        "TrialName": str,
    },
)

DomainDetailsTypeDef = TypedDict(
    "DomainDetailsTypeDef",
    {
        "DomainArn": NotRequired[str],
        "DomainId": NotRequired[str],
        "DomainName": NotRequired[str],
        "Status": NotRequired[DomainStatusType],
        "CreationTime": NotRequired[datetime],
        "LastModifiedTime": NotRequired[datetime],
        "Url": NotRequired[str],
    },
)

FileSourceTypeDef = TypedDict(
    "FileSourceTypeDef",
    {
        "S3Uri": str,
        "ContentType": NotRequired[str],
        "ContentDigest": NotRequired[str],
    },
)

EMRStepMetadataTypeDef = TypedDict(
    "EMRStepMetadataTypeDef",
    {
        "ClusterId": NotRequired[str],
        "StepId": NotRequired[str],
        "StepName": NotRequired[str],
        "LogFilePath": NotRequired[str],
    },
)

EdgeDeploymentPlanSummaryTypeDef = TypedDict(
    "EdgeDeploymentPlanSummaryTypeDef",
    {
        "EdgeDeploymentPlanArn": str,
        "EdgeDeploymentPlanName": str,
        "DeviceFleetName": str,
        "EdgeDeploymentSuccess": int,
        "EdgeDeploymentPending": int,
        "EdgeDeploymentFailed": int,
        "CreationTime": NotRequired[datetime],
        "LastModifiedTime": NotRequired[datetime],
    },
)

EdgeModelStatTypeDef = TypedDict(
    "EdgeModelStatTypeDef",
    {
        "ModelName": str,
        "ModelVersion": str,
        "OfflineDeviceCount": int,
        "ConnectedDeviceCount": int,
        "ActiveDeviceCount": int,
        "SamplingDeviceCount": int,
    },
)

EdgePackagingJobSummaryTypeDef = TypedDict(
    "EdgePackagingJobSummaryTypeDef",
    {
        "EdgePackagingJobArn": str,
        "EdgePackagingJobName": str,
        "EdgePackagingJobStatus": EdgePackagingJobStatusType,
        "CompilationJobName": NotRequired[str],
        "ModelName": NotRequired[str],
        "ModelVersion": NotRequired[str],
        "CreationTime": NotRequired[datetime],
        "LastModifiedTime": NotRequired[datetime],
    },
)

EdgeTypeDef = TypedDict(
    "EdgeTypeDef",
    {
        "SourceArn": NotRequired[str],
        "DestinationArn": NotRequired[str],
        "AssociationType": NotRequired[AssociationEdgeTypeType],
    },
)

EndpointConfigSummaryTypeDef = TypedDict(
    "EndpointConfigSummaryTypeDef",
    {
        "EndpointConfigName": str,
        "EndpointConfigArn": str,
        "CreationTime": datetime,
    },
)

EndpointInfoTypeDef = TypedDict(
    "EndpointInfoTypeDef",
    {
        "EndpointName": str,
    },
)

ProductionVariantServerlessConfigTypeDef = TypedDict(
    "ProductionVariantServerlessConfigTypeDef",
    {
        "MemorySizeInMB": int,
        "MaxConcurrency": int,
        "ProvisionedConcurrency": NotRequired[int],
    },
)

InferenceMetricsTypeDef = TypedDict(
    "InferenceMetricsTypeDef",
    {
        "MaxInvocations": int,
        "ModelLatency": int,
    },
)

EndpointSummaryTypeDef = TypedDict(
    "EndpointSummaryTypeDef",
    {
        "EndpointName": str,
        "EndpointArn": str,
        "CreationTime": datetime,
        "LastModifiedTime": datetime,
        "EndpointStatus": EndpointStatusType,
    },
)

EnvironmentParameterTypeDef = TypedDict(
    "EnvironmentParameterTypeDef",
    {
        "Key": str,
        "ValueType": str,
        "Value": str,
    },
)

FailStepMetadataTypeDef = TypedDict(
    "FailStepMetadataTypeDef",
    {
        "ErrorMessage": NotRequired[str],
    },
)

FileSystemConfigTypeDef = TypedDict(
    "FileSystemConfigTypeDef",
    {
        "MountPath": NotRequired[str],
        "DefaultUid": NotRequired[int],
        "DefaultGid": NotRequired[int],
    },
)

FilterTypeDef = TypedDict(
    "FilterTypeDef",
    {
        "Name": str,
        "Operator": NotRequired[OperatorType],
        "Value": NotRequired[str],
    },
)

FinalHyperParameterTuningJobObjectiveMetricTypeDef = TypedDict(
    "FinalHyperParameterTuningJobObjectiveMetricTypeDef",
    {
        "MetricName": str,
        "Value": float,
        "Type": NotRequired[HyperParameterTuningJobObjectiveTypeType],
    },
)

FlowDefinitionSummaryTypeDef = TypedDict(
    "FlowDefinitionSummaryTypeDef",
    {
        "FlowDefinitionName": str,
        "FlowDefinitionArn": str,
        "FlowDefinitionStatus": FlowDefinitionStatusType,
        "CreationTime": datetime,
        "FailureReason": NotRequired[str],
    },
)

GetDeviceFleetReportRequestRequestTypeDef = TypedDict(
    "GetDeviceFleetReportRequestRequestTypeDef",
    {
        "DeviceFleetName": str,
    },
)

GetLineageGroupPolicyRequestRequestTypeDef = TypedDict(
    "GetLineageGroupPolicyRequestRequestTypeDef",
    {
        "LineageGroupName": str,
    },
)

GetModelPackageGroupPolicyInputRequestTypeDef = TypedDict(
    "GetModelPackageGroupPolicyInputRequestTypeDef",
    {
        "ModelPackageGroupName": str,
    },
)

ScalingPolicyObjectiveTypeDef = TypedDict(
    "ScalingPolicyObjectiveTypeDef",
    {
        "MinInvocationsPerMinute": NotRequired[int],
        "MaxInvocationsPerMinute": NotRequired[int],
    },
)

ScalingPolicyMetricTypeDef = TypedDict(
    "ScalingPolicyMetricTypeDef",
    {
        "InvocationsPerInstance": NotRequired[int],
        "ModelLatency": NotRequired[int],
    },
)

PropertyNameSuggestionTypeDef = TypedDict(
    "PropertyNameSuggestionTypeDef",
    {
        "PropertyName": NotRequired[str],
    },
)

GitConfigForUpdateTypeDef = TypedDict(
    "GitConfigForUpdateTypeDef",
    {
        "SecretArn": NotRequired[str],
    },
)

HolidayConfigAttributesTypeDef = TypedDict(
    "HolidayConfigAttributesTypeDef",
    {
        "CountryCode": NotRequired[str],
    },
)

HubContentInfoTypeDef = TypedDict(
    "HubContentInfoTypeDef",
    {
        "HubContentName": str,
        "HubContentArn": str,
        "HubContentVersion": str,
        "HubContentType": HubContentTypeType,
        "DocumentSchemaVersion": str,
        "HubContentStatus": HubContentStatusType,
        "CreationTime": datetime,
        "HubContentDisplayName": NotRequired[str],
        "HubContentDescription": NotRequired[str],
        "HubContentSearchKeywords": NotRequired[List[str]],
    },
)

HubInfoTypeDef = TypedDict(
    "HubInfoTypeDef",
    {
        "HubName": str,
        "HubArn": str,
        "HubStatus": HubStatusType,
        "CreationTime": datetime,
        "LastModifiedTime": datetime,
        "HubDisplayName": NotRequired[str],
        "HubDescription": NotRequired[str],
        "HubSearchKeywords": NotRequired[List[str]],
    },
)

HumanLoopActivationConditionsConfigTypeDef = TypedDict(
    "HumanLoopActivationConditionsConfigTypeDef",
    {
        "HumanLoopActivationConditions": str,
    },
)

UiConfigTypeDef = TypedDict(
    "UiConfigTypeDef",
    {
        "UiTemplateS3Uri": NotRequired[str],
        "HumanTaskUiArn": NotRequired[str],
    },
)

HumanTaskUiSummaryTypeDef = TypedDict(
    "HumanTaskUiSummaryTypeDef",
    {
        "HumanTaskUiName": str,
        "HumanTaskUiArn": str,
        "CreationTime": datetime,
    },
)

HyperParameterTuningJobObjectiveTypeDef = TypedDict(
    "HyperParameterTuningJobObjectiveTypeDef",
    {
        "Type": HyperParameterTuningJobObjectiveTypeType,
        "MetricName": str,
    },
)

VpcConfigPaginatorTypeDef = TypedDict(
    "VpcConfigPaginatorTypeDef",
    {
        "SecurityGroupIds": List[str],
        "Subnets": List[str],
    },
)

HyperParameterTuningInstanceConfigTypeDef = TypedDict(
    "HyperParameterTuningInstanceConfigTypeDef",
    {
        "InstanceType": TrainingInstanceTypeType,
        "InstanceCount": int,
        "VolumeSizeInGB": int,
    },
)

ResourceLimitsTypeDef = TypedDict(
    "ResourceLimitsTypeDef",
    {
        "MaxParallelTrainingJobs": int,
        "MaxNumberOfTrainingJobs": NotRequired[int],
        "MaxRuntimeInSeconds": NotRequired[int],
    },
)

HyperbandStrategyConfigTypeDef = TypedDict(
    "HyperbandStrategyConfigTypeDef",
    {
        "MinResource": NotRequired[int],
        "MaxResource": NotRequired[int],
    },
)

ParentHyperParameterTuningJobTypeDef = TypedDict(
    "ParentHyperParameterTuningJobTypeDef",
    {
        "HyperParameterTuningJobName": NotRequired[str],
    },
)

IamIdentityTypeDef = TypedDict(
    "IamIdentityTypeDef",
    {
        "Arn": NotRequired[str],
        "PrincipalId": NotRequired[str],
        "SourceIdentity": NotRequired[str],
    },
)

RepositoryAuthConfigTypeDef = TypedDict(
    "RepositoryAuthConfigTypeDef",
    {
        "RepositoryCredentialsProviderArn": str,
    },
)

ImageTypeDef = TypedDict(
    "ImageTypeDef",
    {
        "CreationTime": datetime,
        "ImageArn": str,
        "ImageName": str,
        "ImageStatus": ImageStatusType,
        "LastModifiedTime": datetime,
        "Description": NotRequired[str],
        "DisplayName": NotRequired[str],
        "FailureReason": NotRequired[str],
    },
)

ImageVersionTypeDef = TypedDict(
    "ImageVersionTypeDef",
    {
        "CreationTime": datetime,
        "ImageArn": str,
        "ImageVersionArn": str,
        "ImageVersionStatus": ImageVersionStatusType,
        "LastModifiedTime": datetime,
        "Version": int,
        "FailureReason": NotRequired[str],
    },
)

InferenceExperimentSchedulePaginatorTypeDef = TypedDict(
    "InferenceExperimentSchedulePaginatorTypeDef",
    {
        "StartTime": NotRequired[datetime],
        "EndTime": NotRequired[datetime],
    },
)

RecommendationMetricsTypeDef = TypedDict(
    "RecommendationMetricsTypeDef",
    {
        "CostPerHour": float,
        "CostPerInference": float,
        "MaxInvocations": int,
        "ModelLatency": int,
        "CpuUtilization": NotRequired[float],
        "MemoryUtilization": NotRequired[float],
        "ModelSetupTime": NotRequired[int],
    },
)

InferenceRecommendationsJobTypeDef = TypedDict(
    "InferenceRecommendationsJobTypeDef",
    {
        "JobName": str,
        "JobDescription": str,
        "JobType": RecommendationJobTypeType,
        "JobArn": str,
        "Status": RecommendationJobStatusType,
        "CreationTime": datetime,
        "RoleArn": str,
        "LastModifiedTime": datetime,
        "CompletionTime": NotRequired[datetime],
        "FailureReason": NotRequired[str],
        "ModelName": NotRequired[str],
        "SamplePayloadUrl": NotRequired[str],
        "ModelPackageVersionArn": NotRequired[str],
    },
)

InstanceGroupTypeDef = TypedDict(
    "InstanceGroupTypeDef",
    {
        "InstanceType": TrainingInstanceTypeType,
        "InstanceCount": int,
        "InstanceGroupName": str,
    },
)

IntegerParameterRangeSpecificationTypeDef = TypedDict(
    "IntegerParameterRangeSpecificationTypeDef",
    {
        "MinValue": str,
        "MaxValue": str,
    },
)

IntegerParameterRangeTypeDef = TypedDict(
    "IntegerParameterRangeTypeDef",
    {
        "Name": str,
        "MinValue": str,
        "MaxValue": str,
        "ScalingType": NotRequired[HyperParameterScalingTypeType],
    },
)

KernelSpecTypeDef = TypedDict(
    "KernelSpecTypeDef",
    {
        "Name": str,
        "DisplayName": NotRequired[str],
    },
)

LabelCountersForWorkteamTypeDef = TypedDict(
    "LabelCountersForWorkteamTypeDef",
    {
        "HumanLabeled": NotRequired[int],
        "PendingHuman": NotRequired[int],
        "Total": NotRequired[int],
    },
)

LabelingJobDataAttributesPaginatorTypeDef = TypedDict(
    "LabelingJobDataAttributesPaginatorTypeDef",
    {
        "ContentClassifiers": NotRequired[List[ContentClassifierType]],
    },
)

LabelingJobDataAttributesTypeDef = TypedDict(
    "LabelingJobDataAttributesTypeDef",
    {
        "ContentClassifiers": NotRequired[Sequence[ContentClassifierType]],
    },
)

LabelingJobS3DataSourceTypeDef = TypedDict(
    "LabelingJobS3DataSourceTypeDef",
    {
        "ManifestS3Uri": str,
    },
)

LabelingJobSnsDataSourceTypeDef = TypedDict(
    "LabelingJobSnsDataSourceTypeDef",
    {
        "SnsTopicArn": str,
    },
)

LineageGroupSummaryTypeDef = TypedDict(
    "LineageGroupSummaryTypeDef",
    {
        "LineageGroupArn": NotRequired[str],
        "LineageGroupName": NotRequired[str],
        "DisplayName": NotRequired[str],
        "CreationTime": NotRequired[datetime],
        "LastModifiedTime": NotRequired[datetime],
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

ListAliasesRequestRequestTypeDef = TypedDict(
    "ListAliasesRequestRequestTypeDef",
    {
        "ImageName": str,
        "Alias": NotRequired[str],
        "Version": NotRequired[int],
        "MaxResults": NotRequired[int],
        "NextToken": NotRequired[str],
    },
)

ListAppsRequestRequestTypeDef = TypedDict(
    "ListAppsRequestRequestTypeDef",
    {
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
        "SortOrder": NotRequired[SortOrderType],
        "SortBy": NotRequired[Literal["CreationTime"]],
        "DomainIdEquals": NotRequired[str],
        "UserProfileNameEquals": NotRequired[str],
        "SpaceNameEquals": NotRequired[str],
    },
)

ListCandidatesForAutoMLJobRequestRequestTypeDef = TypedDict(
    "ListCandidatesForAutoMLJobRequestRequestTypeDef",
    {
        "AutoMLJobName": str,
        "StatusEquals": NotRequired[CandidateStatusType],
        "CandidateNameEquals": NotRequired[str],
        "SortOrder": NotRequired[AutoMLSortOrderType],
        "SortBy": NotRequired[CandidateSortByType],
        "MaxResults": NotRequired[int],
        "NextToken": NotRequired[str],
    },
)

MonitoringJobDefinitionSummaryTypeDef = TypedDict(
    "MonitoringJobDefinitionSummaryTypeDef",
    {
        "MonitoringJobDefinitionName": str,
        "MonitoringJobDefinitionArn": str,
        "CreationTime": datetime,
        "EndpointName": str,
    },
)

ListDomainsRequestRequestTypeDef = TypedDict(
    "ListDomainsRequestRequestTypeDef",
    {
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
    },
)

ListInferenceRecommendationsJobStepsRequestRequestTypeDef = TypedDict(
    "ListInferenceRecommendationsJobStepsRequestRequestTypeDef",
    {
        "JobName": str,
        "Status": NotRequired[RecommendationJobStatusType],
        "StepType": NotRequired[Literal["BENCHMARK"]],
        "MaxResults": NotRequired[int],
        "NextToken": NotRequired[str],
    },
)

ModelCardExportJobSummaryTypeDef = TypedDict(
    "ModelCardExportJobSummaryTypeDef",
    {
        "ModelCardExportJobName": str,
        "ModelCardExportJobArn": str,
        "Status": ModelCardExportJobStatusType,
        "ModelCardName": str,
        "ModelCardVersion": int,
        "CreatedAt": datetime,
        "LastModifiedAt": datetime,
    },
)

ModelCardVersionSummaryTypeDef = TypedDict(
    "ModelCardVersionSummaryTypeDef",
    {
        "ModelCardName": str,
        "ModelCardArn": str,
        "ModelCardStatus": ModelCardStatusType,
        "ModelCardVersion": int,
        "CreationTime": datetime,
        "LastModifiedTime": NotRequired[datetime],
    },
)

ModelCardSummaryTypeDef = TypedDict(
    "ModelCardSummaryTypeDef",
    {
        "ModelCardName": str,
        "ModelCardArn": str,
        "ModelCardStatus": ModelCardStatusType,
        "CreationTime": datetime,
        "LastModifiedTime": NotRequired[datetime],
    },
)

ModelMetadataSummaryTypeDef = TypedDict(
    "ModelMetadataSummaryTypeDef",
    {
        "Domain": str,
        "Framework": str,
        "Task": str,
        "Model": str,
        "FrameworkVersion": str,
    },
)

ModelPackageGroupSummaryTypeDef = TypedDict(
    "ModelPackageGroupSummaryTypeDef",
    {
        "ModelPackageGroupName": str,
        "ModelPackageGroupArn": str,
        "CreationTime": datetime,
        "ModelPackageGroupStatus": ModelPackageGroupStatusType,
        "ModelPackageGroupDescription": NotRequired[str],
    },
)

ModelPackageSummaryTypeDef = TypedDict(
    "ModelPackageSummaryTypeDef",
    {
        "ModelPackageName": str,
        "ModelPackageArn": str,
        "CreationTime": datetime,
        "ModelPackageStatus": ModelPackageStatusType,
        "ModelPackageGroupName": NotRequired[str],
        "ModelPackageVersion": NotRequired[int],
        "ModelPackageDescription": NotRequired[str],
        "ModelApprovalStatus": NotRequired[ModelApprovalStatusType],
    },
)

ModelSummaryTypeDef = TypedDict(
    "ModelSummaryTypeDef",
    {
        "ModelName": str,
        "ModelArn": str,
        "CreationTime": datetime,
    },
)

MonitoringAlertHistorySummaryTypeDef = TypedDict(
    "MonitoringAlertHistorySummaryTypeDef",
    {
        "MonitoringScheduleName": str,
        "MonitoringAlertName": str,
        "CreationTime": datetime,
        "AlertStatus": MonitoringAlertStatusType,
    },
)

ListMonitoringAlertsRequestRequestTypeDef = TypedDict(
    "ListMonitoringAlertsRequestRequestTypeDef",
    {
        "MonitoringScheduleName": str,
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
    },
)

MonitoringScheduleSummaryTypeDef = TypedDict(
    "MonitoringScheduleSummaryTypeDef",
    {
        "MonitoringScheduleName": str,
        "MonitoringScheduleArn": str,
        "CreationTime": datetime,
        "LastModifiedTime": datetime,
        "MonitoringScheduleStatus": ScheduleStatusType,
        "EndpointName": NotRequired[str],
        "MonitoringJobDefinitionName": NotRequired[str],
        "MonitoringType": NotRequired[MonitoringTypeType],
    },
)

NotebookInstanceLifecycleConfigSummaryTypeDef = TypedDict(
    "NotebookInstanceLifecycleConfigSummaryTypeDef",
    {
        "NotebookInstanceLifecycleConfigName": str,
        "NotebookInstanceLifecycleConfigArn": str,
        "CreationTime": NotRequired[datetime],
        "LastModifiedTime": NotRequired[datetime],
    },
)

NotebookInstanceSummaryTypeDef = TypedDict(
    "NotebookInstanceSummaryTypeDef",
    {
        "NotebookInstanceName": str,
        "NotebookInstanceArn": str,
        "NotebookInstanceStatus": NotRequired[NotebookInstanceStatusType],
        "Url": NotRequired[str],
        "InstanceType": NotRequired[InstanceTypeType],
        "CreationTime": NotRequired[datetime],
        "LastModifiedTime": NotRequired[datetime],
        "NotebookInstanceLifecycleConfigName": NotRequired[str],
        "DefaultCodeRepository": NotRequired[str],
        "AdditionalCodeRepositories": NotRequired[List[str]],
    },
)

ListPipelineExecutionStepsRequestRequestTypeDef = TypedDict(
    "ListPipelineExecutionStepsRequestRequestTypeDef",
    {
        "PipelineExecutionArn": NotRequired[str],
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
        "SortOrder": NotRequired[SortOrderType],
    },
)

PipelineExecutionSummaryTypeDef = TypedDict(
    "PipelineExecutionSummaryTypeDef",
    {
        "PipelineExecutionArn": NotRequired[str],
        "StartTime": NotRequired[datetime],
        "PipelineExecutionStatus": NotRequired[PipelineExecutionStatusType],
        "PipelineExecutionDescription": NotRequired[str],
        "PipelineExecutionDisplayName": NotRequired[str],
        "PipelineExecutionFailureReason": NotRequired[str],
    },
)

ListPipelineParametersForExecutionRequestRequestTypeDef = TypedDict(
    "ListPipelineParametersForExecutionRequestRequestTypeDef",
    {
        "PipelineExecutionArn": str,
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
    },
)

ParameterTypeDef = TypedDict(
    "ParameterTypeDef",
    {
        "Name": str,
        "Value": str,
    },
)

PipelineSummaryTypeDef = TypedDict(
    "PipelineSummaryTypeDef",
    {
        "PipelineArn": NotRequired[str],
        "PipelineName": NotRequired[str],
        "PipelineDisplayName": NotRequired[str],
        "PipelineDescription": NotRequired[str],
        "RoleArn": NotRequired[str],
        "CreationTime": NotRequired[datetime],
        "LastModifiedTime": NotRequired[datetime],
        "LastExecutionTime": NotRequired[datetime],
    },
)

ProcessingJobSummaryTypeDef = TypedDict(
    "ProcessingJobSummaryTypeDef",
    {
        "ProcessingJobName": str,
        "ProcessingJobArn": str,
        "CreationTime": datetime,
        "ProcessingJobStatus": ProcessingJobStatusType,
        "ProcessingEndTime": NotRequired[datetime],
        "LastModifiedTime": NotRequired[datetime],
        "FailureReason": NotRequired[str],
        "ExitMessage": NotRequired[str],
    },
)

ProjectSummaryTypeDef = TypedDict(
    "ProjectSummaryTypeDef",
    {
        "ProjectName": str,
        "ProjectArn": str,
        "ProjectId": str,
        "CreationTime": datetime,
        "ProjectStatus": ProjectStatusType,
        "ProjectDescription": NotRequired[str],
    },
)

ResourceCatalogTypeDef = TypedDict(
    "ResourceCatalogTypeDef",
    {
        "ResourceCatalogArn": str,
        "ResourceCatalogName": str,
        "Description": str,
        "CreationTime": datetime,
    },
)

ListSpacesRequestRequestTypeDef = TypedDict(
    "ListSpacesRequestRequestTypeDef",
    {
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
        "SortOrder": NotRequired[SortOrderType],
        "SortBy": NotRequired[SpaceSortKeyType],
        "DomainIdEquals": NotRequired[str],
        "SpaceNameContains": NotRequired[str],
    },
)

SpaceDetailsTypeDef = TypedDict(
    "SpaceDetailsTypeDef",
    {
        "DomainId": NotRequired[str],
        "SpaceName": NotRequired[str],
        "Status": NotRequired[SpaceStatusType],
        "CreationTime": NotRequired[datetime],
        "LastModifiedTime": NotRequired[datetime],
    },
)

ListStageDevicesRequestRequestTypeDef = TypedDict(
    "ListStageDevicesRequestRequestTypeDef",
    {
        "EdgeDeploymentPlanName": str,
        "StageName": str,
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
        "ExcludeDevicesDeployedInOtherStage": NotRequired[bool],
    },
)

StudioLifecycleConfigDetailsTypeDef = TypedDict(
    "StudioLifecycleConfigDetailsTypeDef",
    {
        "StudioLifecycleConfigArn": NotRequired[str],
        "StudioLifecycleConfigName": NotRequired[str],
        "CreationTime": NotRequired[datetime],
        "LastModifiedTime": NotRequired[datetime],
        "StudioLifecycleConfigAppType": NotRequired[StudioLifecycleConfigAppTypeType],
    },
)

ListSubscribedWorkteamsRequestRequestTypeDef = TypedDict(
    "ListSubscribedWorkteamsRequestRequestTypeDef",
    {
        "NameContains": NotRequired[str],
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
    },
)

ListTagsInputRequestTypeDef = TypedDict(
    "ListTagsInputRequestTypeDef",
    {
        "ResourceArn": str,
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
    },
)

ListTrainingJobsForHyperParameterTuningJobRequestRequestTypeDef = TypedDict(
    "ListTrainingJobsForHyperParameterTuningJobRequestRequestTypeDef",
    {
        "HyperParameterTuningJobName": str,
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
        "StatusEquals": NotRequired[TrainingJobStatusType],
        "SortBy": NotRequired[TrainingJobSortByOptionsType],
        "SortOrder": NotRequired[SortOrderType],
    },
)

TransformJobSummaryTypeDef = TypedDict(
    "TransformJobSummaryTypeDef",
    {
        "TransformJobName": str,
        "TransformJobArn": str,
        "CreationTime": datetime,
        "TransformJobStatus": TransformJobStatusType,
        "TransformEndTime": NotRequired[datetime],
        "LastModifiedTime": NotRequired[datetime],
        "FailureReason": NotRequired[str],
    },
)

ListUserProfilesRequestRequestTypeDef = TypedDict(
    "ListUserProfilesRequestRequestTypeDef",
    {
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
        "SortOrder": NotRequired[SortOrderType],
        "SortBy": NotRequired[UserProfileSortKeyType],
        "DomainIdEquals": NotRequired[str],
        "UserProfileNameContains": NotRequired[str],
    },
)

UserProfileDetailsTypeDef = TypedDict(
    "UserProfileDetailsTypeDef",
    {
        "DomainId": NotRequired[str],
        "UserProfileName": NotRequired[str],
        "Status": NotRequired[UserProfileStatusType],
        "CreationTime": NotRequired[datetime],
        "LastModifiedTime": NotRequired[datetime],
    },
)

ListWorkforcesRequestRequestTypeDef = TypedDict(
    "ListWorkforcesRequestRequestTypeDef",
    {
        "SortBy": NotRequired[ListWorkforcesSortByOptionsType],
        "SortOrder": NotRequired[SortOrderType],
        "NameContains": NotRequired[str],
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
    },
)

ListWorkteamsRequestRequestTypeDef = TypedDict(
    "ListWorkteamsRequestRequestTypeDef",
    {
        "SortBy": NotRequired[ListWorkteamsSortByOptionsType],
        "SortOrder": NotRequired[SortOrderType],
        "NameContains": NotRequired[str],
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
    },
)

OidcMemberDefinitionPaginatorTypeDef = TypedDict(
    "OidcMemberDefinitionPaginatorTypeDef",
    {
        "Groups": List[str],
    },
)

OidcMemberDefinitionTypeDef = TypedDict(
    "OidcMemberDefinitionTypeDef",
    {
        "Groups": Sequence[str],
    },
)

PredefinedMetricSpecificationTypeDef = TypedDict(
    "PredefinedMetricSpecificationTypeDef",
    {
        "PredefinedMetricType": NotRequired[str],
    },
)

MonitoringGroundTruthS3InputTypeDef = TypedDict(
    "MonitoringGroundTruthS3InputTypeDef",
    {
        "S3Uri": NotRequired[str],
    },
)

ModelDashboardEndpointTypeDef = TypedDict(
    "ModelDashboardEndpointTypeDef",
    {
        "EndpointName": str,
        "EndpointArn": str,
        "CreationTime": datetime,
        "LastModifiedTime": datetime,
        "EndpointStatus": EndpointStatusType,
    },
)

ModelDashboardIndicatorActionTypeDef = TypedDict(
    "ModelDashboardIndicatorActionTypeDef",
    {
        "Enabled": NotRequired[bool],
    },
)

S3ModelDataSourceTypeDef = TypedDict(
    "S3ModelDataSourceTypeDef",
    {
        "S3Uri": str,
        "S3DataType": S3ModelDataTypeType,
        "CompressionType": ModelCompressionTypeType,
    },
)

RealTimeInferenceConfigTypeDef = TypedDict(
    "RealTimeInferenceConfigTypeDef",
    {
        "InstanceType": InstanceTypeType,
        "InstanceCount": int,
    },
)

ModelInputTypeDef = TypedDict(
    "ModelInputTypeDef",
    {
        "DataInputConfig": str,
    },
)

ModelLatencyThresholdTypeDef = TypedDict(
    "ModelLatencyThresholdTypeDef",
    {
        "Percentile": NotRequired[str],
        "ValueInMilliseconds": NotRequired[int],
    },
)

ModelMetadataFilterTypeDef = TypedDict(
    "ModelMetadataFilterTypeDef",
    {
        "Name": ModelMetadataFilterTypeType,
        "Value": str,
    },
)

ModelPackageStatusItemTypeDef = TypedDict(
    "ModelPackageStatusItemTypeDef",
    {
        "Name": str,
        "Status": DetailedModelPackageStatusType,
        "FailureReason": NotRequired[str],
    },
)

ModelStepMetadataTypeDef = TypedDict(
    "ModelStepMetadataTypeDef",
    {
        "Arn": NotRequired[str],
    },
)

MonitoringAppSpecificationPaginatorTypeDef = TypedDict(
    "MonitoringAppSpecificationPaginatorTypeDef",
    {
        "ImageUri": str,
        "ContainerEntrypoint": NotRequired[List[str]],
        "ContainerArguments": NotRequired[List[str]],
        "RecordPreprocessorSourceUri": NotRequired[str],
        "PostAnalyticsProcessorSourceUri": NotRequired[str],
    },
)

MonitoringAppSpecificationTypeDef = TypedDict(
    "MonitoringAppSpecificationTypeDef",
    {
        "ImageUri": str,
        "ContainerEntrypoint": NotRequired[Sequence[str]],
        "ContainerArguments": NotRequired[Sequence[str]],
        "RecordPreprocessorSourceUri": NotRequired[str],
        "PostAnalyticsProcessorSourceUri": NotRequired[str],
    },
)

MonitoringClusterConfigTypeDef = TypedDict(
    "MonitoringClusterConfigTypeDef",
    {
        "InstanceCount": int,
        "InstanceType": ProcessingInstanceTypeType,
        "VolumeSizeInGB": int,
        "VolumeKmsKeyId": NotRequired[str],
    },
)

MonitoringCsvDatasetFormatTypeDef = TypedDict(
    "MonitoringCsvDatasetFormatTypeDef",
    {
        "Header": NotRequired[bool],
    },
)

MonitoringJsonDatasetFormatTypeDef = TypedDict(
    "MonitoringJsonDatasetFormatTypeDef",
    {
        "Line": NotRequired[bool],
    },
)

MonitoringS3OutputTypeDef = TypedDict(
    "MonitoringS3OutputTypeDef",
    {
        "S3Uri": str,
        "LocalPath": str,
        "S3UploadMode": NotRequired[ProcessingS3UploadModeType],
    },
)

ScheduleConfigTypeDef = TypedDict(
    "ScheduleConfigTypeDef",
    {
        "ScheduleExpression": str,
    },
)

S3StorageConfigTypeDef = TypedDict(
    "S3StorageConfigTypeDef",
    {
        "S3Uri": str,
        "KmsKeyId": NotRequired[str],
        "ResolvedOutputS3Uri": NotRequired[str],
    },
)

OidcConfigForResponseTypeDef = TypedDict(
    "OidcConfigForResponseTypeDef",
    {
        "ClientId": NotRequired[str],
        "Issuer": NotRequired[str],
        "AuthorizationEndpoint": NotRequired[str],
        "TokenEndpoint": NotRequired[str],
        "UserInfoEndpoint": NotRequired[str],
        "LogoutEndpoint": NotRequired[str],
        "JwksUri": NotRequired[str],
    },
)

OnlineStoreSecurityConfigTypeDef = TypedDict(
    "OnlineStoreSecurityConfigTypeDef",
    {
        "KmsKeyId": NotRequired[str],
    },
)

TtlDurationTypeDef = TypedDict(
    "TtlDurationTypeDef",
    {
        "Unit": NotRequired[TtlDurationUnitType],
        "Value": NotRequired[int],
    },
)

TargetPlatformTypeDef = TypedDict(
    "TargetPlatformTypeDef",
    {
        "Os": TargetPlatformOsType,
        "Arch": TargetPlatformArchType,
        "Accelerator": NotRequired[TargetPlatformAcceleratorType],
    },
)

ParentTypeDef = TypedDict(
    "ParentTypeDef",
    {
        "TrialName": NotRequired[str],
        "ExperimentName": NotRequired[str],
    },
)

ProductionVariantStatusTypeDef = TypedDict(
    "ProductionVariantStatusTypeDef",
    {
        "Status": VariantStatusType,
        "StatusMessage": NotRequired[str],
        "StartTime": NotRequired[datetime],
    },
)

PhaseTypeDef = TypedDict(
    "PhaseTypeDef",
    {
        "InitialNumberOfUsers": NotRequired[int],
        "SpawnRate": NotRequired[int],
        "DurationInSeconds": NotRequired[int],
    },
)

ProcessingJobStepMetadataTypeDef = TypedDict(
    "ProcessingJobStepMetadataTypeDef",
    {
        "Arn": NotRequired[str],
    },
)

QualityCheckStepMetadataTypeDef = TypedDict(
    "QualityCheckStepMetadataTypeDef",
    {
        "CheckType": NotRequired[str],
        "BaselineUsedForDriftCheckStatistics": NotRequired[str],
        "BaselineUsedForDriftCheckConstraints": NotRequired[str],
        "CalculatedBaselineStatistics": NotRequired[str],
        "CalculatedBaselineConstraints": NotRequired[str],
        "ModelPackageGroupName": NotRequired[str],
        "ViolationReport": NotRequired[str],
        "CheckJobArn": NotRequired[str],
        "SkipCheck": NotRequired[bool],
        "RegisterNewBaseline": NotRequired[bool],
    },
)

RegisterModelStepMetadataTypeDef = TypedDict(
    "RegisterModelStepMetadataTypeDef",
    {
        "Arn": NotRequired[str],
    },
)

TrainingJobStepMetadataTypeDef = TypedDict(
    "TrainingJobStepMetadataTypeDef",
    {
        "Arn": NotRequired[str],
    },
)

TransformJobStepMetadataTypeDef = TypedDict(
    "TransformJobStepMetadataTypeDef",
    {
        "Arn": NotRequired[str],
    },
)

TuningJobStepMetaDataTypeDef = TypedDict(
    "TuningJobStepMetaDataTypeDef",
    {
        "Arn": NotRequired[str],
    },
)

SelectiveExecutionResultTypeDef = TypedDict(
    "SelectiveExecutionResultTypeDef",
    {
        "SourcePipelineExecutionArn": NotRequired[str],
    },
)

ProcessingClusterConfigTypeDef = TypedDict(
    "ProcessingClusterConfigTypeDef",
    {
        "InstanceCount": int,
        "InstanceType": ProcessingInstanceTypeType,
        "VolumeSizeInGB": int,
        "VolumeKmsKeyId": NotRequired[str],
    },
)

ProcessingFeatureStoreOutputTypeDef = TypedDict(
    "ProcessingFeatureStoreOutputTypeDef",
    {
        "FeatureGroupName": str,
    },
)

ProcessingS3InputTypeDef = TypedDict(
    "ProcessingS3InputTypeDef",
    {
        "S3Uri": str,
        "S3DataType": ProcessingS3DataTypeType,
        "LocalPath": NotRequired[str],
        "S3InputMode": NotRequired[ProcessingS3InputModeType],
        "S3DataDistributionType": NotRequired[ProcessingS3DataDistributionTypeType],
        "S3CompressionType": NotRequired[ProcessingS3CompressionTypeType],
    },
)

ProcessingS3OutputTypeDef = TypedDict(
    "ProcessingS3OutputTypeDef",
    {
        "S3Uri": str,
        "LocalPath": str,
        "S3UploadMode": ProcessingS3UploadModeType,
    },
)

ProductionVariantCoreDumpConfigTypeDef = TypedDict(
    "ProductionVariantCoreDumpConfigTypeDef",
    {
        "DestinationS3Uri": str,
        "KmsKeyId": NotRequired[str],
    },
)

ProfilerConfigForUpdateTypeDef = TypedDict(
    "ProfilerConfigForUpdateTypeDef",
    {
        "S3OutputPath": NotRequired[str],
        "ProfilingIntervalInMilliseconds": NotRequired[int],
        "ProfilingParameters": NotRequired[Mapping[str, str]],
        "DisableProfiler": NotRequired[bool],
    },
)

ProfilerConfigPaginatorTypeDef = TypedDict(
    "ProfilerConfigPaginatorTypeDef",
    {
        "S3OutputPath": NotRequired[str],
        "ProfilingIntervalInMilliseconds": NotRequired[int],
        "ProfilingParameters": NotRequired[Dict[str, str]],
        "DisableProfiler": NotRequired[bool],
    },
)

PropertyNameQueryTypeDef = TypedDict(
    "PropertyNameQueryTypeDef",
    {
        "PropertyNameHint": str,
    },
)

ProvisioningParameterTypeDef = TypedDict(
    "ProvisioningParameterTypeDef",
    {
        "Key": NotRequired[str],
        "Value": NotRequired[str],
    },
)

USDTypeDef = TypedDict(
    "USDTypeDef",
    {
        "Dollars": NotRequired[int],
        "Cents": NotRequired[int],
        "TenthFractionsOfACent": NotRequired[int],
    },
)

PutModelPackageGroupPolicyInputRequestTypeDef = TypedDict(
    "PutModelPackageGroupPolicyInputRequestTypeDef",
    {
        "ModelPackageGroupName": str,
        "ResourcePolicy": str,
    },
)

VertexTypeDef = TypedDict(
    "VertexTypeDef",
    {
        "Arn": NotRequired[str],
        "Type": NotRequired[str],
        "LineageType": NotRequired[LineageTypeType],
    },
)

RStudioServerProAppSettingsTypeDef = TypedDict(
    "RStudioServerProAppSettingsTypeDef",
    {
        "AccessStatus": NotRequired[RStudioServerProAccessStatusType],
        "UserGroup": NotRequired[RStudioServerProUserGroupType],
    },
)

RecommendationJobCompiledOutputConfigTypeDef = TypedDict(
    "RecommendationJobCompiledOutputConfigTypeDef",
    {
        "S3OutputUri": NotRequired[str],
    },
)

RecommendationJobPayloadConfigTypeDef = TypedDict(
    "RecommendationJobPayloadConfigTypeDef",
    {
        "SamplePayloadUrl": NotRequired[str],
        "SupportedContentTypes": NotRequired[Sequence[str]],
    },
)

RecommendationJobResourceLimitTypeDef = TypedDict(
    "RecommendationJobResourceLimitTypeDef",
    {
        "MaxNumberOfTests": NotRequired[int],
        "MaxParallelOfTests": NotRequired[int],
    },
)

RecommendationJobVpcConfigTypeDef = TypedDict(
    "RecommendationJobVpcConfigTypeDef",
    {
        "SecurityGroupIds": Sequence[str],
        "Subnets": Sequence[str],
    },
)

RenderableTaskTypeDef = TypedDict(
    "RenderableTaskTypeDef",
    {
        "Input": str,
    },
)

RenderingErrorTypeDef = TypedDict(
    "RenderingErrorTypeDef",
    {
        "Code": str,
        "Message": str,
    },
)

ResourceConfigForUpdateTypeDef = TypedDict(
    "ResourceConfigForUpdateTypeDef",
    {
        "KeepAlivePeriodInSeconds": int,
    },
)

SearchRequestRequestTypeDef = TypedDict(
    "SearchRequestRequestTypeDef",
    {
        "Resource": ResourceTypeType,
        "SearchExpression": NotRequired["SearchExpressionTypeDef"],
        "SortBy": NotRequired[str],
        "SortOrder": NotRequired[SearchSortOrderType],
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
        "CrossAccountFilterOption": NotRequired[CrossAccountFilterOptionType],
    },
)

SelectedStepTypeDef = TypedDict(
    "SelectedStepTypeDef",
    {
        "StepName": str,
    },
)

SendPipelineExecutionStepFailureRequestRequestTypeDef = TypedDict(
    "SendPipelineExecutionStepFailureRequestRequestTypeDef",
    {
        "CallbackToken": str,
        "FailureReason": NotRequired[str],
        "ClientRequestToken": NotRequired[str],
    },
)

ShadowModelVariantConfigTypeDef = TypedDict(
    "ShadowModelVariantConfigTypeDef",
    {
        "ShadowModelVariantName": str,
        "SamplingPercentage": int,
    },
)

SharingSettingsTypeDef = TypedDict(
    "SharingSettingsTypeDef",
    {
        "NotebookOutputOption": NotRequired[NotebookOutputOptionType],
        "S3OutputPath": NotRequired[str],
        "S3KmsKeyId": NotRequired[str],
    },
)

SourceAlgorithmTypeDef = TypedDict(
    "SourceAlgorithmTypeDef",
    {
        "AlgorithmName": str,
        "ModelDataUrl": NotRequired[str],
    },
)

SourceIpConfigPaginatorTypeDef = TypedDict(
    "SourceIpConfigPaginatorTypeDef",
    {
        "Cidrs": List[str],
    },
)

StairsTypeDef = TypedDict(
    "StairsTypeDef",
    {
        "DurationInSeconds": NotRequired[int],
        "NumberOfSteps": NotRequired[int],
        "UsersPerStep": NotRequired[int],
    },
)

StartEdgeDeploymentStageRequestRequestTypeDef = TypedDict(
    "StartEdgeDeploymentStageRequestRequestTypeDef",
    {
        "EdgeDeploymentPlanName": str,
        "StageName": str,
    },
)

StartInferenceExperimentRequestRequestTypeDef = TypedDict(
    "StartInferenceExperimentRequestRequestTypeDef",
    {
        "Name": str,
    },
)

StartMonitoringScheduleRequestRequestTypeDef = TypedDict(
    "StartMonitoringScheduleRequestRequestTypeDef",
    {
        "MonitoringScheduleName": str,
    },
)

StartNotebookInstanceInputRequestTypeDef = TypedDict(
    "StartNotebookInstanceInputRequestTypeDef",
    {
        "NotebookInstanceName": str,
    },
)

StopAutoMLJobRequestRequestTypeDef = TypedDict(
    "StopAutoMLJobRequestRequestTypeDef",
    {
        "AutoMLJobName": str,
    },
)

StopCompilationJobRequestRequestTypeDef = TypedDict(
    "StopCompilationJobRequestRequestTypeDef",
    {
        "CompilationJobName": str,
    },
)

StopEdgeDeploymentStageRequestRequestTypeDef = TypedDict(
    "StopEdgeDeploymentStageRequestRequestTypeDef",
    {
        "EdgeDeploymentPlanName": str,
        "StageName": str,
    },
)

StopEdgePackagingJobRequestRequestTypeDef = TypedDict(
    "StopEdgePackagingJobRequestRequestTypeDef",
    {
        "EdgePackagingJobName": str,
    },
)

StopHyperParameterTuningJobRequestRequestTypeDef = TypedDict(
    "StopHyperParameterTuningJobRequestRequestTypeDef",
    {
        "HyperParameterTuningJobName": str,
    },
)

StopInferenceRecommendationsJobRequestRequestTypeDef = TypedDict(
    "StopInferenceRecommendationsJobRequestRequestTypeDef",
    {
        "JobName": str,
    },
)

StopLabelingJobRequestRequestTypeDef = TypedDict(
    "StopLabelingJobRequestRequestTypeDef",
    {
        "LabelingJobName": str,
    },
)

StopMonitoringScheduleRequestRequestTypeDef = TypedDict(
    "StopMonitoringScheduleRequestRequestTypeDef",
    {
        "MonitoringScheduleName": str,
    },
)

StopNotebookInstanceInputRequestTypeDef = TypedDict(
    "StopNotebookInstanceInputRequestTypeDef",
    {
        "NotebookInstanceName": str,
    },
)

StopPipelineExecutionRequestRequestTypeDef = TypedDict(
    "StopPipelineExecutionRequestRequestTypeDef",
    {
        "PipelineExecutionArn": str,
        "ClientRequestToken": str,
    },
)

StopProcessingJobRequestRequestTypeDef = TypedDict(
    "StopProcessingJobRequestRequestTypeDef",
    {
        "ProcessingJobName": str,
    },
)

StopTrainingJobRequestRequestTypeDef = TypedDict(
    "StopTrainingJobRequestRequestTypeDef",
    {
        "TrainingJobName": str,
    },
)

StopTransformJobRequestRequestTypeDef = TypedDict(
    "StopTransformJobRequestRequestTypeDef",
    {
        "TransformJobName": str,
    },
)

TimeSeriesConfigTypeDef = TypedDict(
    "TimeSeriesConfigTypeDef",
    {
        "TargetAttributeName": str,
        "TimestampAttributeName": str,
        "ItemIdentifierAttributeName": str,
        "GroupingAttributeNames": NotRequired[Sequence[str]],
    },
)

TimeSeriesTransformationsTypeDef = TypedDict(
    "TimeSeriesTransformationsTypeDef",
    {
        "Filling": NotRequired[Mapping[str, Mapping[FillingTypeType, str]]],
        "Aggregation": NotRequired[Mapping[str, AggregationTransformationValueType]],
    },
)

TrainingRepositoryAuthConfigTypeDef = TypedDict(
    "TrainingRepositoryAuthConfigTypeDef",
    {
        "TrainingRepositoryCredentialsProviderArn": str,
    },
)

TransformS3DataSourceTypeDef = TypedDict(
    "TransformS3DataSourceTypeDef",
    {
        "S3DataType": S3DataTypeType,
        "S3Uri": str,
    },
)

UpdateActionRequestRequestTypeDef = TypedDict(
    "UpdateActionRequestRequestTypeDef",
    {
        "ActionName": str,
        "Description": NotRequired[str],
        "Status": NotRequired[ActionStatusType],
        "Properties": NotRequired[Mapping[str, str]],
        "PropertiesToRemove": NotRequired[Sequence[str]],
    },
)

UpdateArtifactRequestRequestTypeDef = TypedDict(
    "UpdateArtifactRequestRequestTypeDef",
    {
        "ArtifactArn": str,
        "ArtifactName": NotRequired[str],
        "Properties": NotRequired[Mapping[str, str]],
        "PropertiesToRemove": NotRequired[Sequence[str]],
    },
)

UpdateContextRequestRequestTypeDef = TypedDict(
    "UpdateContextRequestRequestTypeDef",
    {
        "ContextName": str,
        "Description": NotRequired[str],
        "Properties": NotRequired[Mapping[str, str]],
        "PropertiesToRemove": NotRequired[Sequence[str]],
    },
)

VariantPropertyTypeDef = TypedDict(
    "VariantPropertyTypeDef",
    {
        "VariantPropertyType": VariantPropertyTypeType,
    },
)

UpdateExperimentRequestRequestTypeDef = TypedDict(
    "UpdateExperimentRequestRequestTypeDef",
    {
        "ExperimentName": str,
        "DisplayName": NotRequired[str],
        "Description": NotRequired[str],
    },
)

UpdateHubRequestRequestTypeDef = TypedDict(
    "UpdateHubRequestRequestTypeDef",
    {
        "HubName": str,
        "HubDescription": NotRequired[str],
        "HubDisplayName": NotRequired[str],
        "HubSearchKeywords": NotRequired[Sequence[str]],
    },
)

UpdateImageRequestRequestTypeDef = TypedDict(
    "UpdateImageRequestRequestTypeDef",
    {
        "ImageName": str,
        "DeleteProperties": NotRequired[Sequence[str]],
        "Description": NotRequired[str],
        "DisplayName": NotRequired[str],
        "RoleArn": NotRequired[str],
    },
)

UpdateImageVersionRequestRequestTypeDef = TypedDict(
    "UpdateImageVersionRequestRequestTypeDef",
    {
        "ImageName": str,
        "Alias": NotRequired[str],
        "Version": NotRequired[int],
        "AliasesToAdd": NotRequired[Sequence[str]],
        "AliasesToDelete": NotRequired[Sequence[str]],
        "VendorGuidance": NotRequired[VendorGuidanceType],
        "JobType": NotRequired[JobTypeType],
        "MLFramework": NotRequired[str],
        "ProgrammingLang": NotRequired[str],
        "Processor": NotRequired[ProcessorType],
        "Horovod": NotRequired[bool],
        "ReleaseNotes": NotRequired[str],
    },
)

UpdateModelCardRequestRequestTypeDef = TypedDict(
    "UpdateModelCardRequestRequestTypeDef",
    {
        "ModelCardName": str,
        "Content": NotRequired[str],
        "ModelCardStatus": NotRequired[ModelCardStatusType],
    },
)

UpdateMonitoringAlertRequestRequestTypeDef = TypedDict(
    "UpdateMonitoringAlertRequestRequestTypeDef",
    {
        "MonitoringScheduleName": str,
        "MonitoringAlertName": str,
        "DatapointsToAlert": int,
        "EvaluationPeriod": int,
    },
)

UpdateTrialRequestRequestTypeDef = TypedDict(
    "UpdateTrialRequestRequestTypeDef",
    {
        "TrialName": str,
        "DisplayName": NotRequired[str],
    },
)

WorkforceVpcConfigResponseTypeDef = TypedDict(
    "WorkforceVpcConfigResponseTypeDef",
    {
        "VpcId": str,
        "SecurityGroupIds": List[str],
        "Subnets": List[str],
        "VpcEndpointId": NotRequired[str],
    },
)

ActionSummaryTypeDef = TypedDict(
    "ActionSummaryTypeDef",
    {
        "ActionArn": NotRequired[str],
        "ActionName": NotRequired[str],
        "Source": NotRequired[ActionSourceTypeDef],
        "ActionType": NotRequired[str],
        "Status": NotRequired[ActionStatusType],
        "CreationTime": NotRequired[datetime],
        "LastModifiedTime": NotRequired[datetime],
    },
)

AddAssociationResponseTypeDef = TypedDict(
    "AddAssociationResponseTypeDef",
    {
        "SourceArn": str,
        "DestinationArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

AssociateTrialComponentResponseTypeDef = TypedDict(
    "AssociateTrialComponentResponseTypeDef",
    {
        "TrialComponentArn": str,
        "TrialArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateActionResponseTypeDef = TypedDict(
    "CreateActionResponseTypeDef",
    {
        "ActionArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateAlgorithmOutputTypeDef = TypedDict(
    "CreateAlgorithmOutputTypeDef",
    {
        "AlgorithmArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateAppImageConfigResponseTypeDef = TypedDict(
    "CreateAppImageConfigResponseTypeDef",
    {
        "AppImageConfigArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateAppResponseTypeDef = TypedDict(
    "CreateAppResponseTypeDef",
    {
        "AppArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateArtifactResponseTypeDef = TypedDict(
    "CreateArtifactResponseTypeDef",
    {
        "ArtifactArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateAutoMLJobResponseTypeDef = TypedDict(
    "CreateAutoMLJobResponseTypeDef",
    {
        "AutoMLJobArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateAutoMLJobV2ResponseTypeDef = TypedDict(
    "CreateAutoMLJobV2ResponseTypeDef",
    {
        "AutoMLJobArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateCodeRepositoryOutputTypeDef = TypedDict(
    "CreateCodeRepositoryOutputTypeDef",
    {
        "CodeRepositoryArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateCompilationJobResponseTypeDef = TypedDict(
    "CreateCompilationJobResponseTypeDef",
    {
        "CompilationJobArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateContextResponseTypeDef = TypedDict(
    "CreateContextResponseTypeDef",
    {
        "ContextArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateDataQualityJobDefinitionResponseTypeDef = TypedDict(
    "CreateDataQualityJobDefinitionResponseTypeDef",
    {
        "JobDefinitionArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateDomainResponseTypeDef = TypedDict(
    "CreateDomainResponseTypeDef",
    {
        "DomainArn": str,
        "Url": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateEdgeDeploymentPlanResponseTypeDef = TypedDict(
    "CreateEdgeDeploymentPlanResponseTypeDef",
    {
        "EdgeDeploymentPlanArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateEndpointConfigOutputTypeDef = TypedDict(
    "CreateEndpointConfigOutputTypeDef",
    {
        "EndpointConfigArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateEndpointOutputTypeDef = TypedDict(
    "CreateEndpointOutputTypeDef",
    {
        "EndpointArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateExperimentResponseTypeDef = TypedDict(
    "CreateExperimentResponseTypeDef",
    {
        "ExperimentArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateFeatureGroupResponseTypeDef = TypedDict(
    "CreateFeatureGroupResponseTypeDef",
    {
        "FeatureGroupArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateFlowDefinitionResponseTypeDef = TypedDict(
    "CreateFlowDefinitionResponseTypeDef",
    {
        "FlowDefinitionArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateHubResponseTypeDef = TypedDict(
    "CreateHubResponseTypeDef",
    {
        "HubArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateHumanTaskUiResponseTypeDef = TypedDict(
    "CreateHumanTaskUiResponseTypeDef",
    {
        "HumanTaskUiArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateHyperParameterTuningJobResponseTypeDef = TypedDict(
    "CreateHyperParameterTuningJobResponseTypeDef",
    {
        "HyperParameterTuningJobArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateImageResponseTypeDef = TypedDict(
    "CreateImageResponseTypeDef",
    {
        "ImageArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateImageVersionResponseTypeDef = TypedDict(
    "CreateImageVersionResponseTypeDef",
    {
        "ImageVersionArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateInferenceExperimentResponseTypeDef = TypedDict(
    "CreateInferenceExperimentResponseTypeDef",
    {
        "InferenceExperimentArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateInferenceRecommendationsJobResponseTypeDef = TypedDict(
    "CreateInferenceRecommendationsJobResponseTypeDef",
    {
        "JobArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateLabelingJobResponseTypeDef = TypedDict(
    "CreateLabelingJobResponseTypeDef",
    {
        "LabelingJobArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateModelBiasJobDefinitionResponseTypeDef = TypedDict(
    "CreateModelBiasJobDefinitionResponseTypeDef",
    {
        "JobDefinitionArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateModelCardExportJobResponseTypeDef = TypedDict(
    "CreateModelCardExportJobResponseTypeDef",
    {
        "ModelCardExportJobArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateModelCardResponseTypeDef = TypedDict(
    "CreateModelCardResponseTypeDef",
    {
        "ModelCardArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateModelExplainabilityJobDefinitionResponseTypeDef = TypedDict(
    "CreateModelExplainabilityJobDefinitionResponseTypeDef",
    {
        "JobDefinitionArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateModelOutputTypeDef = TypedDict(
    "CreateModelOutputTypeDef",
    {
        "ModelArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateModelPackageGroupOutputTypeDef = TypedDict(
    "CreateModelPackageGroupOutputTypeDef",
    {
        "ModelPackageGroupArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateModelPackageOutputTypeDef = TypedDict(
    "CreateModelPackageOutputTypeDef",
    {
        "ModelPackageArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateModelQualityJobDefinitionResponseTypeDef = TypedDict(
    "CreateModelQualityJobDefinitionResponseTypeDef",
    {
        "JobDefinitionArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateMonitoringScheduleResponseTypeDef = TypedDict(
    "CreateMonitoringScheduleResponseTypeDef",
    {
        "MonitoringScheduleArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateNotebookInstanceLifecycleConfigOutputTypeDef = TypedDict(
    "CreateNotebookInstanceLifecycleConfigOutputTypeDef",
    {
        "NotebookInstanceLifecycleConfigArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateNotebookInstanceOutputTypeDef = TypedDict(
    "CreateNotebookInstanceOutputTypeDef",
    {
        "NotebookInstanceArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreatePipelineResponseTypeDef = TypedDict(
    "CreatePipelineResponseTypeDef",
    {
        "PipelineArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreatePresignedDomainUrlResponseTypeDef = TypedDict(
    "CreatePresignedDomainUrlResponseTypeDef",
    {
        "AuthorizedUrl": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreatePresignedNotebookInstanceUrlOutputTypeDef = TypedDict(
    "CreatePresignedNotebookInstanceUrlOutputTypeDef",
    {
        "AuthorizedUrl": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateProcessingJobResponseTypeDef = TypedDict(
    "CreateProcessingJobResponseTypeDef",
    {
        "ProcessingJobArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateProjectOutputTypeDef = TypedDict(
    "CreateProjectOutputTypeDef",
    {
        "ProjectArn": str,
        "ProjectId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateSpaceResponseTypeDef = TypedDict(
    "CreateSpaceResponseTypeDef",
    {
        "SpaceArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateStudioLifecycleConfigResponseTypeDef = TypedDict(
    "CreateStudioLifecycleConfigResponseTypeDef",
    {
        "StudioLifecycleConfigArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateTrainingJobResponseTypeDef = TypedDict(
    "CreateTrainingJobResponseTypeDef",
    {
        "TrainingJobArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateTransformJobResponseTypeDef = TypedDict(
    "CreateTransformJobResponseTypeDef",
    {
        "TransformJobArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateTrialComponentResponseTypeDef = TypedDict(
    "CreateTrialComponentResponseTypeDef",
    {
        "TrialComponentArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateTrialResponseTypeDef = TypedDict(
    "CreateTrialResponseTypeDef",
    {
        "TrialArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateUserProfileResponseTypeDef = TypedDict(
    "CreateUserProfileResponseTypeDef",
    {
        "UserProfileArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateWorkforceResponseTypeDef = TypedDict(
    "CreateWorkforceResponseTypeDef",
    {
        "WorkforceArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateWorkteamResponseTypeDef = TypedDict(
    "CreateWorkteamResponseTypeDef",
    {
        "WorkteamArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DeleteActionResponseTypeDef = TypedDict(
    "DeleteActionResponseTypeDef",
    {
        "ActionArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DeleteArtifactResponseTypeDef = TypedDict(
    "DeleteArtifactResponseTypeDef",
    {
        "ArtifactArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DeleteAssociationResponseTypeDef = TypedDict(
    "DeleteAssociationResponseTypeDef",
    {
        "SourceArn": str,
        "DestinationArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DeleteContextResponseTypeDef = TypedDict(
    "DeleteContextResponseTypeDef",
    {
        "ContextArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DeleteExperimentResponseTypeDef = TypedDict(
    "DeleteExperimentResponseTypeDef",
    {
        "ExperimentArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DeleteInferenceExperimentResponseTypeDef = TypedDict(
    "DeleteInferenceExperimentResponseTypeDef",
    {
        "InferenceExperimentArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DeletePipelineResponseTypeDef = TypedDict(
    "DeletePipelineResponseTypeDef",
    {
        "PipelineArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DeleteTrialComponentResponseTypeDef = TypedDict(
    "DeleteTrialComponentResponseTypeDef",
    {
        "TrialComponentArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DeleteTrialResponseTypeDef = TypedDict(
    "DeleteTrialResponseTypeDef",
    {
        "TrialArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DeleteWorkteamResponseTypeDef = TypedDict(
    "DeleteWorkteamResponseTypeDef",
    {
        "Success": bool,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeImageResponseTypeDef = TypedDict(
    "DescribeImageResponseTypeDef",
    {
        "CreationTime": datetime,
        "Description": str,
        "DisplayName": str,
        "FailureReason": str,
        "ImageArn": str,
        "ImageName": str,
        "ImageStatus": ImageStatusType,
        "LastModifiedTime": datetime,
        "RoleArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeImageVersionResponseTypeDef = TypedDict(
    "DescribeImageVersionResponseTypeDef",
    {
        "BaseImage": str,
        "ContainerImage": str,
        "CreationTime": datetime,
        "FailureReason": str,
        "ImageArn": str,
        "ImageVersionArn": str,
        "ImageVersionStatus": ImageVersionStatusType,
        "LastModifiedTime": datetime,
        "Version": int,
        "VendorGuidance": VendorGuidanceType,
        "JobType": JobTypeType,
        "MLFramework": str,
        "ProgrammingLang": str,
        "Processor": ProcessorType,
        "Horovod": bool,
        "ReleaseNotes": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribePipelineDefinitionForExecutionResponseTypeDef = TypedDict(
    "DescribePipelineDefinitionForExecutionResponseTypeDef",
    {
        "PipelineDefinition": str,
        "CreationTime": datetime,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeStudioLifecycleConfigResponseTypeDef = TypedDict(
    "DescribeStudioLifecycleConfigResponseTypeDef",
    {
        "StudioLifecycleConfigArn": str,
        "StudioLifecycleConfigName": str,
        "CreationTime": datetime,
        "LastModifiedTime": datetime,
        "StudioLifecycleConfigContent": str,
        "StudioLifecycleConfigAppType": StudioLifecycleConfigAppTypeType,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DisassociateTrialComponentResponseTypeDef = TypedDict(
    "DisassociateTrialComponentResponseTypeDef",
    {
        "TrialComponentArn": str,
        "TrialArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

EmptyResponseMetadataTypeDef = TypedDict(
    "EmptyResponseMetadataTypeDef",
    {
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

GetLineageGroupPolicyResponseTypeDef = TypedDict(
    "GetLineageGroupPolicyResponseTypeDef",
    {
        "LineageGroupArn": str,
        "ResourcePolicy": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

GetModelPackageGroupPolicyOutputTypeDef = TypedDict(
    "GetModelPackageGroupPolicyOutputTypeDef",
    {
        "ResourcePolicy": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

GetSagemakerServicecatalogPortfolioStatusOutputTypeDef = TypedDict(
    "GetSagemakerServicecatalogPortfolioStatusOutputTypeDef",
    {
        "Status": SagemakerServicecatalogStatusType,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ImportHubContentResponseTypeDef = TypedDict(
    "ImportHubContentResponseTypeDef",
    {
        "HubArn": str,
        "HubContentArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListAliasesResponseTypeDef = TypedDict(
    "ListAliasesResponseTypeDef",
    {
        "SageMakerImageVersionAliases": List[str],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

PutModelPackageGroupPolicyOutputTypeDef = TypedDict(
    "PutModelPackageGroupPolicyOutputTypeDef",
    {
        "ModelPackageGroupArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

RetryPipelineExecutionResponseTypeDef = TypedDict(
    "RetryPipelineExecutionResponseTypeDef",
    {
        "PipelineExecutionArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

SendPipelineExecutionStepFailureResponseTypeDef = TypedDict(
    "SendPipelineExecutionStepFailureResponseTypeDef",
    {
        "PipelineExecutionArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

SendPipelineExecutionStepSuccessResponseTypeDef = TypedDict(
    "SendPipelineExecutionStepSuccessResponseTypeDef",
    {
        "PipelineExecutionArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

StartInferenceExperimentResponseTypeDef = TypedDict(
    "StartInferenceExperimentResponseTypeDef",
    {
        "InferenceExperimentArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

StartPipelineExecutionResponseTypeDef = TypedDict(
    "StartPipelineExecutionResponseTypeDef",
    {
        "PipelineExecutionArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

StopInferenceExperimentResponseTypeDef = TypedDict(
    "StopInferenceExperimentResponseTypeDef",
    {
        "InferenceExperimentArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

StopPipelineExecutionResponseTypeDef = TypedDict(
    "StopPipelineExecutionResponseTypeDef",
    {
        "PipelineExecutionArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

UpdateActionResponseTypeDef = TypedDict(
    "UpdateActionResponseTypeDef",
    {
        "ActionArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

UpdateAppImageConfigResponseTypeDef = TypedDict(
    "UpdateAppImageConfigResponseTypeDef",
    {
        "AppImageConfigArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

UpdateArtifactResponseTypeDef = TypedDict(
    "UpdateArtifactResponseTypeDef",
    {
        "ArtifactArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

UpdateCodeRepositoryOutputTypeDef = TypedDict(
    "UpdateCodeRepositoryOutputTypeDef",
    {
        "CodeRepositoryArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

UpdateContextResponseTypeDef = TypedDict(
    "UpdateContextResponseTypeDef",
    {
        "ContextArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

UpdateDomainResponseTypeDef = TypedDict(
    "UpdateDomainResponseTypeDef",
    {
        "DomainArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

UpdateEndpointOutputTypeDef = TypedDict(
    "UpdateEndpointOutputTypeDef",
    {
        "EndpointArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

UpdateEndpointWeightsAndCapacitiesOutputTypeDef = TypedDict(
    "UpdateEndpointWeightsAndCapacitiesOutputTypeDef",
    {
        "EndpointArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

UpdateExperimentResponseTypeDef = TypedDict(
    "UpdateExperimentResponseTypeDef",
    {
        "ExperimentArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

UpdateFeatureGroupResponseTypeDef = TypedDict(
    "UpdateFeatureGroupResponseTypeDef",
    {
        "FeatureGroupArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

UpdateHubResponseTypeDef = TypedDict(
    "UpdateHubResponseTypeDef",
    {
        "HubArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

UpdateImageResponseTypeDef = TypedDict(
    "UpdateImageResponseTypeDef",
    {
        "ImageArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

UpdateImageVersionResponseTypeDef = TypedDict(
    "UpdateImageVersionResponseTypeDef",
    {
        "ImageVersionArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

UpdateInferenceExperimentResponseTypeDef = TypedDict(
    "UpdateInferenceExperimentResponseTypeDef",
    {
        "InferenceExperimentArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

UpdateModelCardResponseTypeDef = TypedDict(
    "UpdateModelCardResponseTypeDef",
    {
        "ModelCardArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

UpdateModelPackageOutputTypeDef = TypedDict(
    "UpdateModelPackageOutputTypeDef",
    {
        "ModelPackageArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

UpdateMonitoringAlertResponseTypeDef = TypedDict(
    "UpdateMonitoringAlertResponseTypeDef",
    {
        "MonitoringScheduleArn": str,
        "MonitoringAlertName": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

UpdateMonitoringScheduleResponseTypeDef = TypedDict(
    "UpdateMonitoringScheduleResponseTypeDef",
    {
        "MonitoringScheduleArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

UpdatePipelineExecutionResponseTypeDef = TypedDict(
    "UpdatePipelineExecutionResponseTypeDef",
    {
        "PipelineExecutionArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

UpdatePipelineResponseTypeDef = TypedDict(
    "UpdatePipelineResponseTypeDef",
    {
        "PipelineArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

UpdateProjectOutputTypeDef = TypedDict(
    "UpdateProjectOutputTypeDef",
    {
        "ProjectArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

UpdateSpaceResponseTypeDef = TypedDict(
    "UpdateSpaceResponseTypeDef",
    {
        "SpaceArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

UpdateTrainingJobResponseTypeDef = TypedDict(
    "UpdateTrainingJobResponseTypeDef",
    {
        "TrainingJobArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

UpdateTrialComponentResponseTypeDef = TypedDict(
    "UpdateTrialComponentResponseTypeDef",
    {
        "TrialComponentArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

UpdateTrialResponseTypeDef = TypedDict(
    "UpdateTrialResponseTypeDef",
    {
        "TrialArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

UpdateUserProfileResponseTypeDef = TypedDict(
    "UpdateUserProfileResponseTypeDef",
    {
        "UserProfileArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

AddTagsInputRequestTypeDef = TypedDict(
    "AddTagsInputRequestTypeDef",
    {
        "ResourceArn": str,
        "Tags": Sequence[TagTypeDef],
    },
)

AddTagsOutputTypeDef = TypedDict(
    "AddTagsOutputTypeDef",
    {
        "Tags": List[TagTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateExperimentRequestRequestTypeDef = TypedDict(
    "CreateExperimentRequestRequestTypeDef",
    {
        "ExperimentName": str,
        "DisplayName": NotRequired[str],
        "Description": NotRequired[str],
        "Tags": NotRequired[Sequence[TagTypeDef]],
    },
)

CreateImageRequestRequestTypeDef = TypedDict(
    "CreateImageRequestRequestTypeDef",
    {
        "ImageName": str,
        "RoleArn": str,
        "Description": NotRequired[str],
        "DisplayName": NotRequired[str],
        "Tags": NotRequired[Sequence[TagTypeDef]],
    },
)

CreateModelPackageGroupInputRequestTypeDef = TypedDict(
    "CreateModelPackageGroupInputRequestTypeDef",
    {
        "ModelPackageGroupName": str,
        "ModelPackageGroupDescription": NotRequired[str],
        "Tags": NotRequired[Sequence[TagTypeDef]],
    },
)

CreateStudioLifecycleConfigRequestRequestTypeDef = TypedDict(
    "CreateStudioLifecycleConfigRequestRequestTypeDef",
    {
        "StudioLifecycleConfigName": str,
        "StudioLifecycleConfigContent": str,
        "StudioLifecycleConfigAppType": StudioLifecycleConfigAppTypeType,
        "Tags": NotRequired[Sequence[TagTypeDef]],
    },
)

ImportHubContentRequestRequestTypeDef = TypedDict(
    "ImportHubContentRequestRequestTypeDef",
    {
        "HubContentName": str,
        "HubContentType": HubContentTypeType,
        "DocumentSchemaVersion": str,
        "HubName": str,
        "HubContentDocument": str,
        "HubContentVersion": NotRequired[str],
        "HubContentDisplayName": NotRequired[str],
        "HubContentDescription": NotRequired[str],
        "HubContentMarkdown": NotRequired[str],
        "HubContentSearchKeywords": NotRequired[Sequence[str]],
        "Tags": NotRequired[Sequence[TagTypeDef]],
    },
)

ListTagsOutputTypeDef = TypedDict(
    "ListTagsOutputTypeDef",
    {
        "Tags": List[TagTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

AutoRollbackConfigTypeDef = TypedDict(
    "AutoRollbackConfigTypeDef",
    {
        "Alarms": NotRequired[Sequence[AlarmTypeDef]],
    },
)

HyperParameterAlgorithmSpecificationPaginatorTypeDef = TypedDict(
    "HyperParameterAlgorithmSpecificationPaginatorTypeDef",
    {
        "TrainingInputMode": TrainingInputModeType,
        "TrainingImage": NotRequired[str],
        "AlgorithmName": NotRequired[str],
        "MetricDefinitions": NotRequired[List[MetricDefinitionTypeDef]],
    },
)

HyperParameterAlgorithmSpecificationTypeDef = TypedDict(
    "HyperParameterAlgorithmSpecificationTypeDef",
    {
        "TrainingInputMode": TrainingInputModeType,
        "TrainingImage": NotRequired[str],
        "AlgorithmName": NotRequired[str],
        "MetricDefinitions": NotRequired[Sequence[MetricDefinitionTypeDef]],
    },
)

AlgorithmStatusDetailsTypeDef = TypedDict(
    "AlgorithmStatusDetailsTypeDef",
    {
        "ValidationStatuses": NotRequired[List[AlgorithmStatusItemTypeDef]],
        "ImageScanStatuses": NotRequired[List[AlgorithmStatusItemTypeDef]],
    },
)

ListAlgorithmsOutputTypeDef = TypedDict(
    "ListAlgorithmsOutputTypeDef",
    {
        "AlgorithmSummaryList": List[AlgorithmSummaryTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListAppsResponseTypeDef = TypedDict(
    "ListAppsResponseTypeDef",
    {
        "Apps": List[AppDetailsTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ArtifactSourcePaginatorTypeDef = TypedDict(
    "ArtifactSourcePaginatorTypeDef",
    {
        "SourceUri": str,
        "SourceTypes": NotRequired[List[ArtifactSourceTypeTypeDef]],
    },
)

ArtifactSourceTypeDef = TypedDict(
    "ArtifactSourceTypeDef",
    {
        "SourceUri": str,
        "SourceTypes": NotRequired[Sequence[ArtifactSourceTypeTypeDef]],
    },
)

AsyncInferenceOutputConfigTypeDef = TypedDict(
    "AsyncInferenceOutputConfigTypeDef",
    {
        "KmsKeyId": NotRequired[str],
        "S3OutputPath": NotRequired[str],
        "NotificationConfig": NotRequired[AsyncInferenceNotificationConfigTypeDef],
        "S3FailurePath": NotRequired[str],
    },
)

AutoMLCandidateGenerationConfigTypeDef = TypedDict(
    "AutoMLCandidateGenerationConfigTypeDef",
    {
        "FeatureSpecificationS3Uri": NotRequired[str],
        "AlgorithmsConfig": NotRequired[Sequence[AutoMLAlgorithmConfigTypeDef]],
    },
)

CandidateGenerationConfigTypeDef = TypedDict(
    "CandidateGenerationConfigTypeDef",
    {
        "AlgorithmsConfig": NotRequired[Sequence[AutoMLAlgorithmConfigTypeDef]],
    },
)

AutoMLDataSourceTypeDef = TypedDict(
    "AutoMLDataSourceTypeDef",
    {
        "S3DataSource": AutoMLS3DataSourceTypeDef,
    },
)

ImageClassificationJobConfigTypeDef = TypedDict(
    "ImageClassificationJobConfigTypeDef",
    {
        "CompletionCriteria": NotRequired[AutoMLJobCompletionCriteriaTypeDef],
    },
)

TextClassificationJobConfigTypeDef = TypedDict(
    "TextClassificationJobConfigTypeDef",
    {
        "ContentColumn": str,
        "TargetLabelColumn": str,
        "CompletionCriteria": NotRequired[AutoMLJobCompletionCriteriaTypeDef],
    },
)

ResolvedAttributesTypeDef = TypedDict(
    "ResolvedAttributesTypeDef",
    {
        "AutoMLJobObjective": NotRequired[AutoMLJobObjectiveTypeDef],
        "ProblemType": NotRequired[ProblemTypeType],
        "CompletionCriteria": NotRequired[AutoMLJobCompletionCriteriaTypeDef],
    },
)

AutoMLJobSummaryTypeDef = TypedDict(
    "AutoMLJobSummaryTypeDef",
    {
        "AutoMLJobName": str,
        "AutoMLJobArn": str,
        "AutoMLJobStatus": AutoMLJobStatusType,
        "AutoMLJobSecondaryStatus": AutoMLJobSecondaryStatusType,
        "CreationTime": datetime,
        "LastModifiedTime": datetime,
        "EndTime": NotRequired[datetime],
        "FailureReason": NotRequired[str],
        "PartialFailureReasons": NotRequired[List[AutoMLPartialFailureReasonTypeDef]],
    },
)

AutoMLProblemTypeResolvedAttributesTypeDef = TypedDict(
    "AutoMLProblemTypeResolvedAttributesTypeDef",
    {
        "TabularResolvedAttributes": NotRequired[TabularResolvedAttributesTypeDef],
    },
)

AutoMLSecurityConfigTypeDef = TypedDict(
    "AutoMLSecurityConfigTypeDef",
    {
        "VolumeKmsKeyId": NotRequired[str],
        "EnableInterContainerTrafficEncryption": NotRequired[bool],
        "VpcConfig": NotRequired[VpcConfigTypeDef],
    },
)

LabelingJobResourceConfigTypeDef = TypedDict(
    "LabelingJobResourceConfigTypeDef",
    {
        "VolumeKmsKeyId": NotRequired[str],
        "VpcConfig": NotRequired[VpcConfigTypeDef],
    },
)

MonitoringNetworkConfigTypeDef = TypedDict(
    "MonitoringNetworkConfigTypeDef",
    {
        "EnableInterContainerTrafficEncryption": NotRequired[bool],
        "EnableNetworkIsolation": NotRequired[bool],
        "VpcConfig": NotRequired[VpcConfigTypeDef],
    },
)

NetworkConfigTypeDef = TypedDict(
    "NetworkConfigTypeDef",
    {
        "EnableInterContainerTrafficEncryption": NotRequired[bool],
        "EnableNetworkIsolation": NotRequired[bool],
        "VpcConfig": NotRequired[VpcConfigTypeDef],
    },
)

BiasTypeDef = TypedDict(
    "BiasTypeDef",
    {
        "Report": NotRequired[MetricsSourceTypeDef],
        "PreTrainingReport": NotRequired[MetricsSourceTypeDef],
        "PostTrainingReport": NotRequired[MetricsSourceTypeDef],
    },
)

DriftCheckModelDataQualityTypeDef = TypedDict(
    "DriftCheckModelDataQualityTypeDef",
    {
        "Statistics": NotRequired[MetricsSourceTypeDef],
        "Constraints": NotRequired[MetricsSourceTypeDef],
    },
)

DriftCheckModelQualityTypeDef = TypedDict(
    "DriftCheckModelQualityTypeDef",
    {
        "Statistics": NotRequired[MetricsSourceTypeDef],
        "Constraints": NotRequired[MetricsSourceTypeDef],
    },
)

ExplainabilityTypeDef = TypedDict(
    "ExplainabilityTypeDef",
    {
        "Report": NotRequired[MetricsSourceTypeDef],
    },
)

ModelDataQualityTypeDef = TypedDict(
    "ModelDataQualityTypeDef",
    {
        "Statistics": NotRequired[MetricsSourceTypeDef],
        "Constraints": NotRequired[MetricsSourceTypeDef],
    },
)

ModelQualityTypeDef = TypedDict(
    "ModelQualityTypeDef",
    {
        "Statistics": NotRequired[MetricsSourceTypeDef],
        "Constraints": NotRequired[MetricsSourceTypeDef],
    },
)

CallbackStepMetadataTypeDef = TypedDict(
    "CallbackStepMetadataTypeDef",
    {
        "CallbackToken": NotRequired[str],
        "SqsQueueUrl": NotRequired[str],
        "OutputParameters": NotRequired[List[OutputParameterTypeDef]],
    },
)

LambdaStepMetadataTypeDef = TypedDict(
    "LambdaStepMetadataTypeDef",
    {
        "Arn": NotRequired[str],
        "OutputParameters": NotRequired[List[OutputParameterTypeDef]],
    },
)

SendPipelineExecutionStepSuccessRequestRequestTypeDef = TypedDict(
    "SendPipelineExecutionStepSuccessRequestRequestTypeDef",
    {
        "CallbackToken": str,
        "OutputParameters": NotRequired[Sequence[OutputParameterTypeDef]],
        "ClientRequestToken": NotRequired[str],
    },
)

CandidatePropertiesTypeDef = TypedDict(
    "CandidatePropertiesTypeDef",
    {
        "CandidateArtifactLocations": NotRequired[CandidateArtifactLocationsTypeDef],
        "CandidateMetrics": NotRequired[List[MetricDatumTypeDef]],
    },
)

CanvasAppSettingsTypeDef = TypedDict(
    "CanvasAppSettingsTypeDef",
    {
        "TimeSeriesForecastingSettings": NotRequired[TimeSeriesForecastingSettingsTypeDef],
        "ModelRegisterSettings": NotRequired[ModelRegisterSettingsTypeDef],
        "WorkspaceSettings": NotRequired[WorkspaceSettingsTypeDef],
        "IdentityProviderOAuthSettings": NotRequired[Sequence[IdentityProviderOAuthSettingTypeDef]],
    },
)

RollingUpdatePolicyTypeDef = TypedDict(
    "RollingUpdatePolicyTypeDef",
    {
        "MaximumBatchSize": CapacitySizeTypeDef,
        "WaitIntervalInSeconds": int,
        "MaximumExecutionTimeoutInSeconds": NotRequired[int],
        "RollbackMaximumBatchSize": NotRequired[CapacitySizeTypeDef],
    },
)

TrafficRoutingConfigTypeDef = TypedDict(
    "TrafficRoutingConfigTypeDef",
    {
        "Type": TrafficRoutingConfigTypeType,
        "WaitIntervalInSeconds": int,
        "CanarySize": NotRequired[CapacitySizeTypeDef],
        "LinearStepSize": NotRequired[CapacitySizeTypeDef],
    },
)

InferenceExperimentDataStorageConfigTypeDef = TypedDict(
    "InferenceExperimentDataStorageConfigTypeDef",
    {
        "Destination": str,
        "KmsKey": NotRequired[str],
        "ContentType": NotRequired[CaptureContentTypeHeaderTypeDef],
    },
)

DataCaptureConfigTypeDef = TypedDict(
    "DataCaptureConfigTypeDef",
    {
        "InitialSamplingPercentage": int,
        "DestinationS3Uri": str,
        "CaptureOptions": Sequence[CaptureOptionTypeDef],
        "EnableCapture": NotRequired[bool],
        "KmsKeyId": NotRequired[str],
        "CaptureContentTypeHeader": NotRequired[CaptureContentTypeHeaderTypeDef],
    },
)

EnvironmentParameterRangesTypeDef = TypedDict(
    "EnvironmentParameterRangesTypeDef",
    {
        "CategoricalParameterRanges": NotRequired[Sequence[CategoricalParameterTypeDef]],
    },
)

ClarifyShapConfigTypeDef = TypedDict(
    "ClarifyShapConfigTypeDef",
    {
        "ShapBaselineConfig": ClarifyShapBaselineConfigTypeDef,
        "NumberOfSamples": NotRequired[int],
        "UseLogit": NotRequired[bool],
        "Seed": NotRequired[int],
        "TextConfig": NotRequired[ClarifyTextConfigTypeDef],
    },
)

CodeRepositorySummaryTypeDef = TypedDict(
    "CodeRepositorySummaryTypeDef",
    {
        "CodeRepositoryName": str,
        "CodeRepositoryArn": str,
        "CreationTime": datetime,
        "LastModifiedTime": datetime,
        "GitConfig": NotRequired[GitConfigTypeDef],
    },
)

CreateCodeRepositoryInputRequestTypeDef = TypedDict(
    "CreateCodeRepositoryInputRequestTypeDef",
    {
        "CodeRepositoryName": str,
        "GitConfig": GitConfigTypeDef,
        "Tags": NotRequired[Sequence[TagTypeDef]],
    },
)

DescribeCodeRepositoryOutputTypeDef = TypedDict(
    "DescribeCodeRepositoryOutputTypeDef",
    {
        "CodeRepositoryName": str,
        "CodeRepositoryArn": str,
        "CreationTime": datetime,
        "LastModifiedTime": datetime,
        "GitConfig": GitConfigTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DebugHookConfigPaginatorTypeDef = TypedDict(
    "DebugHookConfigPaginatorTypeDef",
    {
        "S3OutputPath": str,
        "LocalPath": NotRequired[str],
        "HookParameters": NotRequired[Dict[str, str]],
        "CollectionConfigurations": NotRequired[List[CollectionConfigurationPaginatorTypeDef]],
    },
)

DebugHookConfigTypeDef = TypedDict(
    "DebugHookConfigTypeDef",
    {
        "S3OutputPath": str,
        "LocalPath": NotRequired[str],
        "HookParameters": NotRequired[Mapping[str, str]],
        "CollectionConfigurations": NotRequired[Sequence[CollectionConfigurationTypeDef]],
    },
)

ListCompilationJobsResponseTypeDef = TypedDict(
    "ListCompilationJobsResponseTypeDef",
    {
        "CompilationJobSummaries": List[CompilationJobSummaryTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ContextSummaryTypeDef = TypedDict(
    "ContextSummaryTypeDef",
    {
        "ContextArn": NotRequired[str],
        "ContextName": NotRequired[str],
        "Source": NotRequired[ContextSourceTypeDef],
        "ContextType": NotRequired[str],
        "CreationTime": NotRequired[datetime],
        "LastModifiedTime": NotRequired[datetime],
    },
)

CreateContextRequestRequestTypeDef = TypedDict(
    "CreateContextRequestRequestTypeDef",
    {
        "ContextName": str,
        "Source": ContextSourceTypeDef,
        "ContextType": str,
        "Description": NotRequired[str],
        "Properties": NotRequired[Mapping[str, str]],
        "Tags": NotRequired[Sequence[TagTypeDef]],
    },
)

TuningJobCompletionCriteriaTypeDef = TypedDict(
    "TuningJobCompletionCriteriaTypeDef",
    {
        "TargetObjectiveMetricValue": NotRequired[float],
        "BestObjectiveNotImproving": NotRequired[BestObjectiveNotImprovingTypeDef],
        "ConvergenceDetected": NotRequired[ConvergenceDetectedTypeDef],
    },
)

CreateActionRequestRequestTypeDef = TypedDict(
    "CreateActionRequestRequestTypeDef",
    {
        "ActionName": str,
        "Source": ActionSourceTypeDef,
        "ActionType": str,
        "Description": NotRequired[str],
        "Status": NotRequired[ActionStatusType],
        "Properties": NotRequired[Mapping[str, str]],
        "MetadataProperties": NotRequired[MetadataPropertiesTypeDef],
        "Tags": NotRequired[Sequence[TagTypeDef]],
    },
)

CreateTrialRequestRequestTypeDef = TypedDict(
    "CreateTrialRequestRequestTypeDef",
    {
        "TrialName": str,
        "ExperimentName": str,
        "DisplayName": NotRequired[str],
        "MetadataProperties": NotRequired[MetadataPropertiesTypeDef],
        "Tags": NotRequired[Sequence[TagTypeDef]],
    },
)

CreateAppRequestRequestTypeDef = TypedDict(
    "CreateAppRequestRequestTypeDef",
    {
        "DomainId": str,
        "AppType": AppTypeType,
        "AppName": str,
        "UserProfileName": NotRequired[str],
        "Tags": NotRequired[Sequence[TagTypeDef]],
        "ResourceSpec": NotRequired[ResourceSpecTypeDef],
        "SpaceName": NotRequired[str],
    },
)

DescribeAppResponseTypeDef = TypedDict(
    "DescribeAppResponseTypeDef",
    {
        "AppArn": str,
        "AppType": AppTypeType,
        "AppName": str,
        "DomainId": str,
        "UserProfileName": str,
        "Status": AppStatusType,
        "LastHealthCheckTimestamp": datetime,
        "LastUserActivityTimestamp": datetime,
        "CreationTime": datetime,
        "FailureReason": str,
        "ResourceSpec": ResourceSpecTypeDef,
        "SpaceName": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

JupyterServerAppSettingsTypeDef = TypedDict(
    "JupyterServerAppSettingsTypeDef",
    {
        "DefaultResourceSpec": NotRequired[ResourceSpecTypeDef],
        "LifecycleConfigArns": NotRequired[Sequence[str]],
        "CodeRepositories": NotRequired[Sequence[CodeRepositoryTypeDef]],
    },
)

RStudioServerProDomainSettingsForUpdateTypeDef = TypedDict(
    "RStudioServerProDomainSettingsForUpdateTypeDef",
    {
        "DomainExecutionRoleArn": str,
        "DefaultResourceSpec": NotRequired[ResourceSpecTypeDef],
        "RStudioConnectUrl": NotRequired[str],
        "RStudioPackageManagerUrl": NotRequired[str],
    },
)

RStudioServerProDomainSettingsTypeDef = TypedDict(
    "RStudioServerProDomainSettingsTypeDef",
    {
        "DomainExecutionRoleArn": str,
        "RStudioConnectUrl": NotRequired[str],
        "RStudioPackageManagerUrl": NotRequired[str],
        "DefaultResourceSpec": NotRequired[ResourceSpecTypeDef],
    },
)

TensorBoardAppSettingsTypeDef = TypedDict(
    "TensorBoardAppSettingsTypeDef",
    {
        "DefaultResourceSpec": NotRequired[ResourceSpecTypeDef],
    },
)

CreateDeviceFleetRequestRequestTypeDef = TypedDict(
    "CreateDeviceFleetRequestRequestTypeDef",
    {
        "DeviceFleetName": str,
        "OutputConfig": EdgeOutputConfigTypeDef,
        "RoleArn": NotRequired[str],
        "Description": NotRequired[str],
        "Tags": NotRequired[Sequence[TagTypeDef]],
        "EnableIotRoleAlias": NotRequired[bool],
    },
)

CreateEdgePackagingJobRequestRequestTypeDef = TypedDict(
    "CreateEdgePackagingJobRequestRequestTypeDef",
    {
        "EdgePackagingJobName": str,
        "CompilationJobName": str,
        "ModelName": str,
        "ModelVersion": str,
        "RoleArn": str,
        "OutputConfig": EdgeOutputConfigTypeDef,
        "ResourceKey": NotRequired[str],
        "Tags": NotRequired[Sequence[TagTypeDef]],
    },
)

DescribeDeviceFleetResponseTypeDef = TypedDict(
    "DescribeDeviceFleetResponseTypeDef",
    {
        "DeviceFleetName": str,
        "DeviceFleetArn": str,
        "OutputConfig": EdgeOutputConfigTypeDef,
        "Description": str,
        "CreationTime": datetime,
        "LastModifiedTime": datetime,
        "RoleArn": str,
        "IotRoleAlias": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

UpdateDeviceFleetRequestRequestTypeDef = TypedDict(
    "UpdateDeviceFleetRequestRequestTypeDef",
    {
        "DeviceFleetName": str,
        "OutputConfig": EdgeOutputConfigTypeDef,
        "RoleArn": NotRequired[str],
        "Description": NotRequired[str],
        "EnableIotRoleAlias": NotRequired[bool],
    },
)

CreateHubRequestRequestTypeDef = TypedDict(
    "CreateHubRequestRequestTypeDef",
    {
        "HubName": str,
        "HubDescription": str,
        "HubDisplayName": NotRequired[str],
        "HubSearchKeywords": NotRequired[Sequence[str]],
        "S3StorageConfig": NotRequired[HubS3StorageConfigTypeDef],
        "Tags": NotRequired[Sequence[TagTypeDef]],
    },
)

DescribeHubResponseTypeDef = TypedDict(
    "DescribeHubResponseTypeDef",
    {
        "HubName": str,
        "HubArn": str,
        "HubDisplayName": str,
        "HubDescription": str,
        "HubSearchKeywords": List[str],
        "S3StorageConfig": HubS3StorageConfigTypeDef,
        "HubStatus": HubStatusType,
        "FailureReason": str,
        "CreationTime": datetime,
        "LastModifiedTime": datetime,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateHumanTaskUiRequestRequestTypeDef = TypedDict(
    "CreateHumanTaskUiRequestRequestTypeDef",
    {
        "HumanTaskUiName": str,
        "UiTemplate": UiTemplateTypeDef,
        "Tags": NotRequired[Sequence[TagTypeDef]],
    },
)

CreateModelCardExportJobRequestRequestTypeDef = TypedDict(
    "CreateModelCardExportJobRequestRequestTypeDef",
    {
        "ModelCardName": str,
        "ModelCardExportJobName": str,
        "OutputConfig": ModelCardExportOutputConfigTypeDef,
        "ModelCardVersion": NotRequired[int],
    },
)

CreateModelCardRequestRequestTypeDef = TypedDict(
    "CreateModelCardRequestRequestTypeDef",
    {
        "ModelCardName": str,
        "Content": str,
        "ModelCardStatus": ModelCardStatusType,
        "SecurityConfig": NotRequired[ModelCardSecurityConfigTypeDef],
        "Tags": NotRequired[Sequence[TagTypeDef]],
    },
)

CreateNotebookInstanceInputRequestTypeDef = TypedDict(
    "CreateNotebookInstanceInputRequestTypeDef",
    {
        "NotebookInstanceName": str,
        "InstanceType": InstanceTypeType,
        "RoleArn": str,
        "SubnetId": NotRequired[str],
        "SecurityGroupIds": NotRequired[Sequence[str]],
        "KmsKeyId": NotRequired[str],
        "Tags": NotRequired[Sequence[TagTypeDef]],
        "LifecycleConfigName": NotRequired[str],
        "DirectInternetAccess": NotRequired[DirectInternetAccessType],
        "VolumeSizeInGB": NotRequired[int],
        "AcceleratorTypes": NotRequired[Sequence[NotebookInstanceAcceleratorTypeType]],
        "DefaultCodeRepository": NotRequired[str],
        "AdditionalCodeRepositories": NotRequired[Sequence[str]],
        "RootAccess": NotRequired[RootAccessType],
        "PlatformIdentifier": NotRequired[str],
        "InstanceMetadataServiceConfiguration": NotRequired[
            InstanceMetadataServiceConfigurationTypeDef
        ],
    },
)

DescribeNotebookInstanceOutputTypeDef = TypedDict(
    "DescribeNotebookInstanceOutputTypeDef",
    {
        "NotebookInstanceArn": str,
        "NotebookInstanceName": str,
        "NotebookInstanceStatus": NotebookInstanceStatusType,
        "FailureReason": str,
        "Url": str,
        "InstanceType": InstanceTypeType,
        "SubnetId": str,
        "SecurityGroups": List[str],
        "RoleArn": str,
        "KmsKeyId": str,
        "NetworkInterfaceId": str,
        "LastModifiedTime": datetime,
        "CreationTime": datetime,
        "NotebookInstanceLifecycleConfigName": str,
        "DirectInternetAccess": DirectInternetAccessType,
        "VolumeSizeInGB": int,
        "AcceleratorTypes": List[NotebookInstanceAcceleratorTypeType],
        "DefaultCodeRepository": str,
        "AdditionalCodeRepositories": List[str],
        "RootAccess": RootAccessType,
        "PlatformIdentifier": str,
        "InstanceMetadataServiceConfiguration": InstanceMetadataServiceConfigurationTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

UpdateNotebookInstanceInputRequestTypeDef = TypedDict(
    "UpdateNotebookInstanceInputRequestTypeDef",
    {
        "NotebookInstanceName": str,
        "InstanceType": NotRequired[InstanceTypeType],
        "RoleArn": NotRequired[str],
        "LifecycleConfigName": NotRequired[str],
        "DisassociateLifecycleConfig": NotRequired[bool],
        "VolumeSizeInGB": NotRequired[int],
        "DefaultCodeRepository": NotRequired[str],
        "AdditionalCodeRepositories": NotRequired[Sequence[str]],
        "AcceleratorTypes": NotRequired[Sequence[NotebookInstanceAcceleratorTypeType]],
        "DisassociateAcceleratorTypes": NotRequired[bool],
        "DisassociateDefaultCodeRepository": NotRequired[bool],
        "DisassociateAdditionalCodeRepositories": NotRequired[bool],
        "RootAccess": NotRequired[RootAccessType],
        "InstanceMetadataServiceConfiguration": NotRequired[
            InstanceMetadataServiceConfigurationTypeDef
        ],
    },
)

CreateNotebookInstanceLifecycleConfigInputRequestTypeDef = TypedDict(
    "CreateNotebookInstanceLifecycleConfigInputRequestTypeDef",
    {
        "NotebookInstanceLifecycleConfigName": str,
        "OnCreate": NotRequired[Sequence[NotebookInstanceLifecycleHookTypeDef]],
        "OnStart": NotRequired[Sequence[NotebookInstanceLifecycleHookTypeDef]],
    },
)

DescribeNotebookInstanceLifecycleConfigOutputTypeDef = TypedDict(
    "DescribeNotebookInstanceLifecycleConfigOutputTypeDef",
    {
        "NotebookInstanceLifecycleConfigArn": str,
        "NotebookInstanceLifecycleConfigName": str,
        "OnCreate": List[NotebookInstanceLifecycleHookTypeDef],
        "OnStart": List[NotebookInstanceLifecycleHookTypeDef],
        "LastModifiedTime": datetime,
        "CreationTime": datetime,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

UpdateNotebookInstanceLifecycleConfigInputRequestTypeDef = TypedDict(
    "UpdateNotebookInstanceLifecycleConfigInputRequestTypeDef",
    {
        "NotebookInstanceLifecycleConfigName": str,
        "OnCreate": NotRequired[Sequence[NotebookInstanceLifecycleHookTypeDef]],
        "OnStart": NotRequired[Sequence[NotebookInstanceLifecycleHookTypeDef]],
    },
)

RetryPipelineExecutionRequestRequestTypeDef = TypedDict(
    "RetryPipelineExecutionRequestRequestTypeDef",
    {
        "PipelineExecutionArn": str,
        "ClientRequestToken": str,
        "ParallelismConfiguration": NotRequired[ParallelismConfigurationTypeDef],
    },
)

UpdatePipelineExecutionRequestRequestTypeDef = TypedDict(
    "UpdatePipelineExecutionRequestRequestTypeDef",
    {
        "PipelineExecutionArn": str,
        "PipelineExecutionDescription": NotRequired[str],
        "PipelineExecutionDisplayName": NotRequired[str],
        "ParallelismConfiguration": NotRequired[ParallelismConfigurationTypeDef],
    },
)

CreatePipelineRequestRequestTypeDef = TypedDict(
    "CreatePipelineRequestRequestTypeDef",
    {
        "PipelineName": str,
        "ClientRequestToken": str,
        "RoleArn": str,
        "PipelineDisplayName": NotRequired[str],
        "PipelineDefinition": NotRequired[str],
        "PipelineDefinitionS3Location": NotRequired[PipelineDefinitionS3LocationTypeDef],
        "PipelineDescription": NotRequired[str],
        "Tags": NotRequired[Sequence[TagTypeDef]],
        "ParallelismConfiguration": NotRequired[ParallelismConfigurationTypeDef],
    },
)

UpdatePipelineRequestRequestTypeDef = TypedDict(
    "UpdatePipelineRequestRequestTypeDef",
    {
        "PipelineName": str,
        "PipelineDisplayName": NotRequired[str],
        "PipelineDefinition": NotRequired[str],
        "PipelineDefinitionS3Location": NotRequired[PipelineDefinitionS3LocationTypeDef],
        "PipelineDescription": NotRequired[str],
        "RoleArn": NotRequired[str],
        "ParallelismConfiguration": NotRequired[ParallelismConfigurationTypeDef],
    },
)

InferenceExperimentScheduleTypeDef = TypedDict(
    "InferenceExperimentScheduleTypeDef",
    {
        "StartTime": NotRequired[TimestampTypeDef],
        "EndTime": NotRequired[TimestampTypeDef],
    },
)

ListActionsRequestRequestTypeDef = TypedDict(
    "ListActionsRequestRequestTypeDef",
    {
        "SourceUri": NotRequired[str],
        "ActionType": NotRequired[str],
        "CreatedAfter": NotRequired[TimestampTypeDef],
        "CreatedBefore": NotRequired[TimestampTypeDef],
        "SortBy": NotRequired[SortActionsByType],
        "SortOrder": NotRequired[SortOrderType],
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
    },
)

ListAlgorithmsInputRequestTypeDef = TypedDict(
    "ListAlgorithmsInputRequestTypeDef",
    {
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "MaxResults": NotRequired[int],
        "NameContains": NotRequired[str],
        "NextToken": NotRequired[str],
        "SortBy": NotRequired[AlgorithmSortByType],
        "SortOrder": NotRequired[SortOrderType],
    },
)

ListAppImageConfigsRequestRequestTypeDef = TypedDict(
    "ListAppImageConfigsRequestRequestTypeDef",
    {
        "MaxResults": NotRequired[int],
        "NextToken": NotRequired[str],
        "NameContains": NotRequired[str],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "ModifiedTimeBefore": NotRequired[TimestampTypeDef],
        "ModifiedTimeAfter": NotRequired[TimestampTypeDef],
        "SortBy": NotRequired[AppImageConfigSortKeyType],
        "SortOrder": NotRequired[SortOrderType],
    },
)

ListArtifactsRequestRequestTypeDef = TypedDict(
    "ListArtifactsRequestRequestTypeDef",
    {
        "SourceUri": NotRequired[str],
        "ArtifactType": NotRequired[str],
        "CreatedAfter": NotRequired[TimestampTypeDef],
        "CreatedBefore": NotRequired[TimestampTypeDef],
        "SortBy": NotRequired[Literal["CreationTime"]],
        "SortOrder": NotRequired[SortOrderType],
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
    },
)

ListAssociationsRequestRequestTypeDef = TypedDict(
    "ListAssociationsRequestRequestTypeDef",
    {
        "SourceArn": NotRequired[str],
        "DestinationArn": NotRequired[str],
        "SourceType": NotRequired[str],
        "DestinationType": NotRequired[str],
        "AssociationType": NotRequired[AssociationEdgeTypeType],
        "CreatedAfter": NotRequired[TimestampTypeDef],
        "CreatedBefore": NotRequired[TimestampTypeDef],
        "SortBy": NotRequired[SortAssociationsByType],
        "SortOrder": NotRequired[SortOrderType],
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
    },
)

ListAutoMLJobsRequestRequestTypeDef = TypedDict(
    "ListAutoMLJobsRequestRequestTypeDef",
    {
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "LastModifiedTimeAfter": NotRequired[TimestampTypeDef],
        "LastModifiedTimeBefore": NotRequired[TimestampTypeDef],
        "NameContains": NotRequired[str],
        "StatusEquals": NotRequired[AutoMLJobStatusType],
        "SortOrder": NotRequired[AutoMLSortOrderType],
        "SortBy": NotRequired[AutoMLSortByType],
        "MaxResults": NotRequired[int],
        "NextToken": NotRequired[str],
    },
)

ListCodeRepositoriesInputRequestTypeDef = TypedDict(
    "ListCodeRepositoriesInputRequestTypeDef",
    {
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "LastModifiedTimeAfter": NotRequired[TimestampTypeDef],
        "LastModifiedTimeBefore": NotRequired[TimestampTypeDef],
        "MaxResults": NotRequired[int],
        "NameContains": NotRequired[str],
        "NextToken": NotRequired[str],
        "SortBy": NotRequired[CodeRepositorySortByType],
        "SortOrder": NotRequired[CodeRepositorySortOrderType],
    },
)

ListCompilationJobsRequestRequestTypeDef = TypedDict(
    "ListCompilationJobsRequestRequestTypeDef",
    {
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "LastModifiedTimeAfter": NotRequired[TimestampTypeDef],
        "LastModifiedTimeBefore": NotRequired[TimestampTypeDef],
        "NameContains": NotRequired[str],
        "StatusEquals": NotRequired[CompilationJobStatusType],
        "SortBy": NotRequired[ListCompilationJobsSortByType],
        "SortOrder": NotRequired[SortOrderType],
    },
)

ListContextsRequestRequestTypeDef = TypedDict(
    "ListContextsRequestRequestTypeDef",
    {
        "SourceUri": NotRequired[str],
        "ContextType": NotRequired[str],
        "CreatedAfter": NotRequired[TimestampTypeDef],
        "CreatedBefore": NotRequired[TimestampTypeDef],
        "SortBy": NotRequired[SortContextsByType],
        "SortOrder": NotRequired[SortOrderType],
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
    },
)

ListDataQualityJobDefinitionsRequestRequestTypeDef = TypedDict(
    "ListDataQualityJobDefinitionsRequestRequestTypeDef",
    {
        "EndpointName": NotRequired[str],
        "SortBy": NotRequired[MonitoringJobDefinitionSortKeyType],
        "SortOrder": NotRequired[SortOrderType],
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
        "NameContains": NotRequired[str],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
    },
)

ListDeviceFleetsRequestRequestTypeDef = TypedDict(
    "ListDeviceFleetsRequestRequestTypeDef",
    {
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "LastModifiedTimeAfter": NotRequired[TimestampTypeDef],
        "LastModifiedTimeBefore": NotRequired[TimestampTypeDef],
        "NameContains": NotRequired[str],
        "SortBy": NotRequired[ListDeviceFleetsSortByType],
        "SortOrder": NotRequired[SortOrderType],
    },
)

ListDevicesRequestRequestTypeDef = TypedDict(
    "ListDevicesRequestRequestTypeDef",
    {
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
        "LatestHeartbeatAfter": NotRequired[TimestampTypeDef],
        "ModelName": NotRequired[str],
        "DeviceFleetName": NotRequired[str],
    },
)

ListEdgeDeploymentPlansRequestRequestTypeDef = TypedDict(
    "ListEdgeDeploymentPlansRequestRequestTypeDef",
    {
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "LastModifiedTimeAfter": NotRequired[TimestampTypeDef],
        "LastModifiedTimeBefore": NotRequired[TimestampTypeDef],
        "NameContains": NotRequired[str],
        "DeviceFleetNameContains": NotRequired[str],
        "SortBy": NotRequired[ListEdgeDeploymentPlansSortByType],
        "SortOrder": NotRequired[SortOrderType],
    },
)

ListEdgePackagingJobsRequestRequestTypeDef = TypedDict(
    "ListEdgePackagingJobsRequestRequestTypeDef",
    {
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "LastModifiedTimeAfter": NotRequired[TimestampTypeDef],
        "LastModifiedTimeBefore": NotRequired[TimestampTypeDef],
        "NameContains": NotRequired[str],
        "ModelNameContains": NotRequired[str],
        "StatusEquals": NotRequired[EdgePackagingJobStatusType],
        "SortBy": NotRequired[ListEdgePackagingJobsSortByType],
        "SortOrder": NotRequired[SortOrderType],
    },
)

ListEndpointConfigsInputRequestTypeDef = TypedDict(
    "ListEndpointConfigsInputRequestTypeDef",
    {
        "SortBy": NotRequired[EndpointConfigSortKeyType],
        "SortOrder": NotRequired[OrderKeyType],
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
        "NameContains": NotRequired[str],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
    },
)

ListEndpointsInputRequestTypeDef = TypedDict(
    "ListEndpointsInputRequestTypeDef",
    {
        "SortBy": NotRequired[EndpointSortKeyType],
        "SortOrder": NotRequired[OrderKeyType],
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
        "NameContains": NotRequired[str],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "LastModifiedTimeBefore": NotRequired[TimestampTypeDef],
        "LastModifiedTimeAfter": NotRequired[TimestampTypeDef],
        "StatusEquals": NotRequired[EndpointStatusType],
    },
)

ListExperimentsRequestRequestTypeDef = TypedDict(
    "ListExperimentsRequestRequestTypeDef",
    {
        "CreatedAfter": NotRequired[TimestampTypeDef],
        "CreatedBefore": NotRequired[TimestampTypeDef],
        "SortBy": NotRequired[SortExperimentsByType],
        "SortOrder": NotRequired[SortOrderType],
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
    },
)

ListFeatureGroupsRequestRequestTypeDef = TypedDict(
    "ListFeatureGroupsRequestRequestTypeDef",
    {
        "NameContains": NotRequired[str],
        "FeatureGroupStatusEquals": NotRequired[FeatureGroupStatusType],
        "OfflineStoreStatusEquals": NotRequired[OfflineStoreStatusValueType],
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "SortOrder": NotRequired[FeatureGroupSortOrderType],
        "SortBy": NotRequired[FeatureGroupSortByType],
        "MaxResults": NotRequired[int],
        "NextToken": NotRequired[str],
    },
)

ListFlowDefinitionsRequestRequestTypeDef = TypedDict(
    "ListFlowDefinitionsRequestRequestTypeDef",
    {
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "SortOrder": NotRequired[SortOrderType],
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
    },
)

ListHubContentVersionsRequestRequestTypeDef = TypedDict(
    "ListHubContentVersionsRequestRequestTypeDef",
    {
        "HubName": str,
        "HubContentType": HubContentTypeType,
        "HubContentName": str,
        "MinVersion": NotRequired[str],
        "MaxSchemaVersion": NotRequired[str],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "SortBy": NotRequired[HubContentSortByType],
        "SortOrder": NotRequired[SortOrderType],
        "MaxResults": NotRequired[int],
        "NextToken": NotRequired[str],
    },
)

ListHubContentsRequestRequestTypeDef = TypedDict(
    "ListHubContentsRequestRequestTypeDef",
    {
        "HubName": str,
        "HubContentType": HubContentTypeType,
        "NameContains": NotRequired[str],
        "MaxSchemaVersion": NotRequired[str],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "SortBy": NotRequired[HubContentSortByType],
        "SortOrder": NotRequired[SortOrderType],
        "MaxResults": NotRequired[int],
        "NextToken": NotRequired[str],
    },
)

ListHubsRequestRequestTypeDef = TypedDict(
    "ListHubsRequestRequestTypeDef",
    {
        "NameContains": NotRequired[str],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "LastModifiedTimeBefore": NotRequired[TimestampTypeDef],
        "LastModifiedTimeAfter": NotRequired[TimestampTypeDef],
        "SortBy": NotRequired[HubSortByType],
        "SortOrder": NotRequired[SortOrderType],
        "MaxResults": NotRequired[int],
        "NextToken": NotRequired[str],
    },
)

ListHumanTaskUisRequestRequestTypeDef = TypedDict(
    "ListHumanTaskUisRequestRequestTypeDef",
    {
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "SortOrder": NotRequired[SortOrderType],
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
    },
)

ListHyperParameterTuningJobsRequestRequestTypeDef = TypedDict(
    "ListHyperParameterTuningJobsRequestRequestTypeDef",
    {
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
        "SortBy": NotRequired[HyperParameterTuningJobSortByOptionsType],
        "SortOrder": NotRequired[SortOrderType],
        "NameContains": NotRequired[str],
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "LastModifiedTimeAfter": NotRequired[TimestampTypeDef],
        "LastModifiedTimeBefore": NotRequired[TimestampTypeDef],
        "StatusEquals": NotRequired[HyperParameterTuningJobStatusType],
    },
)

ListImageVersionsRequestRequestTypeDef = TypedDict(
    "ListImageVersionsRequestRequestTypeDef",
    {
        "ImageName": str,
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "LastModifiedTimeAfter": NotRequired[TimestampTypeDef],
        "LastModifiedTimeBefore": NotRequired[TimestampTypeDef],
        "MaxResults": NotRequired[int],
        "NextToken": NotRequired[str],
        "SortBy": NotRequired[ImageVersionSortByType],
        "SortOrder": NotRequired[ImageVersionSortOrderType],
    },
)

ListImagesRequestRequestTypeDef = TypedDict(
    "ListImagesRequestRequestTypeDef",
    {
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "LastModifiedTimeAfter": NotRequired[TimestampTypeDef],
        "LastModifiedTimeBefore": NotRequired[TimestampTypeDef],
        "MaxResults": NotRequired[int],
        "NameContains": NotRequired[str],
        "NextToken": NotRequired[str],
        "SortBy": NotRequired[ImageSortByType],
        "SortOrder": NotRequired[ImageSortOrderType],
    },
)

ListInferenceExperimentsRequestRequestTypeDef = TypedDict(
    "ListInferenceExperimentsRequestRequestTypeDef",
    {
        "NameContains": NotRequired[str],
        "Type": NotRequired[Literal["ShadowMode"]],
        "StatusEquals": NotRequired[InferenceExperimentStatusType],
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "LastModifiedTimeAfter": NotRequired[TimestampTypeDef],
        "LastModifiedTimeBefore": NotRequired[TimestampTypeDef],
        "SortBy": NotRequired[SortInferenceExperimentsByType],
        "SortOrder": NotRequired[SortOrderType],
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
    },
)

ListInferenceRecommendationsJobsRequestRequestTypeDef = TypedDict(
    "ListInferenceRecommendationsJobsRequestRequestTypeDef",
    {
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "LastModifiedTimeAfter": NotRequired[TimestampTypeDef],
        "LastModifiedTimeBefore": NotRequired[TimestampTypeDef],
        "NameContains": NotRequired[str],
        "StatusEquals": NotRequired[RecommendationJobStatusType],
        "SortBy": NotRequired[ListInferenceRecommendationsJobsSortByType],
        "SortOrder": NotRequired[SortOrderType],
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
        "ModelNameEquals": NotRequired[str],
        "ModelPackageVersionArnEquals": NotRequired[str],
    },
)

ListLabelingJobsForWorkteamRequestRequestTypeDef = TypedDict(
    "ListLabelingJobsForWorkteamRequestRequestTypeDef",
    {
        "WorkteamArn": str,
        "MaxResults": NotRequired[int],
        "NextToken": NotRequired[str],
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "JobReferenceCodeContains": NotRequired[str],
        "SortBy": NotRequired[Literal["CreationTime"]],
        "SortOrder": NotRequired[SortOrderType],
    },
)

ListLabelingJobsRequestRequestTypeDef = TypedDict(
    "ListLabelingJobsRequestRequestTypeDef",
    {
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "LastModifiedTimeAfter": NotRequired[TimestampTypeDef],
        "LastModifiedTimeBefore": NotRequired[TimestampTypeDef],
        "MaxResults": NotRequired[int],
        "NextToken": NotRequired[str],
        "NameContains": NotRequired[str],
        "SortBy": NotRequired[SortByType],
        "SortOrder": NotRequired[SortOrderType],
        "StatusEquals": NotRequired[LabelingJobStatusType],
    },
)

ListLineageGroupsRequestRequestTypeDef = TypedDict(
    "ListLineageGroupsRequestRequestTypeDef",
    {
        "CreatedAfter": NotRequired[TimestampTypeDef],
        "CreatedBefore": NotRequired[TimestampTypeDef],
        "SortBy": NotRequired[SortLineageGroupsByType],
        "SortOrder": NotRequired[SortOrderType],
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
    },
)

ListModelBiasJobDefinitionsRequestRequestTypeDef = TypedDict(
    "ListModelBiasJobDefinitionsRequestRequestTypeDef",
    {
        "EndpointName": NotRequired[str],
        "SortBy": NotRequired[MonitoringJobDefinitionSortKeyType],
        "SortOrder": NotRequired[SortOrderType],
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
        "NameContains": NotRequired[str],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
    },
)

ListModelCardExportJobsRequestRequestTypeDef = TypedDict(
    "ListModelCardExportJobsRequestRequestTypeDef",
    {
        "ModelCardName": str,
        "ModelCardVersion": NotRequired[int],
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "ModelCardExportJobNameContains": NotRequired[str],
        "StatusEquals": NotRequired[ModelCardExportJobStatusType],
        "SortBy": NotRequired[ModelCardExportJobSortByType],
        "SortOrder": NotRequired[ModelCardExportJobSortOrderType],
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
    },
)

ListModelCardVersionsRequestRequestTypeDef = TypedDict(
    "ListModelCardVersionsRequestRequestTypeDef",
    {
        "ModelCardName": str,
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "MaxResults": NotRequired[int],
        "ModelCardStatus": NotRequired[ModelCardStatusType],
        "NextToken": NotRequired[str],
        "SortBy": NotRequired[Literal["Version"]],
        "SortOrder": NotRequired[ModelCardSortOrderType],
    },
)

ListModelCardsRequestRequestTypeDef = TypedDict(
    "ListModelCardsRequestRequestTypeDef",
    {
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "MaxResults": NotRequired[int],
        "NameContains": NotRequired[str],
        "ModelCardStatus": NotRequired[ModelCardStatusType],
        "NextToken": NotRequired[str],
        "SortBy": NotRequired[ModelCardSortByType],
        "SortOrder": NotRequired[ModelCardSortOrderType],
    },
)

ListModelExplainabilityJobDefinitionsRequestRequestTypeDef = TypedDict(
    "ListModelExplainabilityJobDefinitionsRequestRequestTypeDef",
    {
        "EndpointName": NotRequired[str],
        "SortBy": NotRequired[MonitoringJobDefinitionSortKeyType],
        "SortOrder": NotRequired[SortOrderType],
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
        "NameContains": NotRequired[str],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
    },
)

ListModelPackageGroupsInputRequestTypeDef = TypedDict(
    "ListModelPackageGroupsInputRequestTypeDef",
    {
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "MaxResults": NotRequired[int],
        "NameContains": NotRequired[str],
        "NextToken": NotRequired[str],
        "SortBy": NotRequired[ModelPackageGroupSortByType],
        "SortOrder": NotRequired[SortOrderType],
    },
)

ListModelPackagesInputRequestTypeDef = TypedDict(
    "ListModelPackagesInputRequestTypeDef",
    {
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "MaxResults": NotRequired[int],
        "NameContains": NotRequired[str],
        "ModelApprovalStatus": NotRequired[ModelApprovalStatusType],
        "ModelPackageGroupName": NotRequired[str],
        "ModelPackageType": NotRequired[ModelPackageTypeType],
        "NextToken": NotRequired[str],
        "SortBy": NotRequired[ModelPackageSortByType],
        "SortOrder": NotRequired[SortOrderType],
    },
)

ListModelQualityJobDefinitionsRequestRequestTypeDef = TypedDict(
    "ListModelQualityJobDefinitionsRequestRequestTypeDef",
    {
        "EndpointName": NotRequired[str],
        "SortBy": NotRequired[MonitoringJobDefinitionSortKeyType],
        "SortOrder": NotRequired[SortOrderType],
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
        "NameContains": NotRequired[str],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
    },
)

ListModelsInputRequestTypeDef = TypedDict(
    "ListModelsInputRequestTypeDef",
    {
        "SortBy": NotRequired[ModelSortKeyType],
        "SortOrder": NotRequired[OrderKeyType],
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
        "NameContains": NotRequired[str],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
    },
)

ListMonitoringAlertHistoryRequestRequestTypeDef = TypedDict(
    "ListMonitoringAlertHistoryRequestRequestTypeDef",
    {
        "MonitoringScheduleName": NotRequired[str],
        "MonitoringAlertName": NotRequired[str],
        "SortBy": NotRequired[MonitoringAlertHistorySortKeyType],
        "SortOrder": NotRequired[SortOrderType],
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "StatusEquals": NotRequired[MonitoringAlertStatusType],
    },
)

ListMonitoringExecutionsRequestRequestTypeDef = TypedDict(
    "ListMonitoringExecutionsRequestRequestTypeDef",
    {
        "MonitoringScheduleName": NotRequired[str],
        "EndpointName": NotRequired[str],
        "SortBy": NotRequired[MonitoringExecutionSortKeyType],
        "SortOrder": NotRequired[SortOrderType],
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
        "ScheduledTimeBefore": NotRequired[TimestampTypeDef],
        "ScheduledTimeAfter": NotRequired[TimestampTypeDef],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "LastModifiedTimeBefore": NotRequired[TimestampTypeDef],
        "LastModifiedTimeAfter": NotRequired[TimestampTypeDef],
        "StatusEquals": NotRequired[ExecutionStatusType],
        "MonitoringJobDefinitionName": NotRequired[str],
        "MonitoringTypeEquals": NotRequired[MonitoringTypeType],
    },
)

ListMonitoringSchedulesRequestRequestTypeDef = TypedDict(
    "ListMonitoringSchedulesRequestRequestTypeDef",
    {
        "EndpointName": NotRequired[str],
        "SortBy": NotRequired[MonitoringScheduleSortKeyType],
        "SortOrder": NotRequired[SortOrderType],
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
        "NameContains": NotRequired[str],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "LastModifiedTimeBefore": NotRequired[TimestampTypeDef],
        "LastModifiedTimeAfter": NotRequired[TimestampTypeDef],
        "StatusEquals": NotRequired[ScheduleStatusType],
        "MonitoringJobDefinitionName": NotRequired[str],
        "MonitoringTypeEquals": NotRequired[MonitoringTypeType],
    },
)

ListNotebookInstanceLifecycleConfigsInputRequestTypeDef = TypedDict(
    "ListNotebookInstanceLifecycleConfigsInputRequestTypeDef",
    {
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
        "SortBy": NotRequired[NotebookInstanceLifecycleConfigSortKeyType],
        "SortOrder": NotRequired[NotebookInstanceLifecycleConfigSortOrderType],
        "NameContains": NotRequired[str],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "LastModifiedTimeBefore": NotRequired[TimestampTypeDef],
        "LastModifiedTimeAfter": NotRequired[TimestampTypeDef],
    },
)

ListNotebookInstancesInputRequestTypeDef = TypedDict(
    "ListNotebookInstancesInputRequestTypeDef",
    {
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
        "SortBy": NotRequired[NotebookInstanceSortKeyType],
        "SortOrder": NotRequired[NotebookInstanceSortOrderType],
        "NameContains": NotRequired[str],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "LastModifiedTimeBefore": NotRequired[TimestampTypeDef],
        "LastModifiedTimeAfter": NotRequired[TimestampTypeDef],
        "StatusEquals": NotRequired[NotebookInstanceStatusType],
        "NotebookInstanceLifecycleConfigNameContains": NotRequired[str],
        "DefaultCodeRepositoryContains": NotRequired[str],
        "AdditionalCodeRepositoryEquals": NotRequired[str],
    },
)

ListPipelineExecutionsRequestRequestTypeDef = TypedDict(
    "ListPipelineExecutionsRequestRequestTypeDef",
    {
        "PipelineName": str,
        "CreatedAfter": NotRequired[TimestampTypeDef],
        "CreatedBefore": NotRequired[TimestampTypeDef],
        "SortBy": NotRequired[SortPipelineExecutionsByType],
        "SortOrder": NotRequired[SortOrderType],
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
    },
)

ListPipelinesRequestRequestTypeDef = TypedDict(
    "ListPipelinesRequestRequestTypeDef",
    {
        "PipelineNamePrefix": NotRequired[str],
        "CreatedAfter": NotRequired[TimestampTypeDef],
        "CreatedBefore": NotRequired[TimestampTypeDef],
        "SortBy": NotRequired[SortPipelinesByType],
        "SortOrder": NotRequired[SortOrderType],
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
    },
)

ListProcessingJobsRequestRequestTypeDef = TypedDict(
    "ListProcessingJobsRequestRequestTypeDef",
    {
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "LastModifiedTimeAfter": NotRequired[TimestampTypeDef],
        "LastModifiedTimeBefore": NotRequired[TimestampTypeDef],
        "NameContains": NotRequired[str],
        "StatusEquals": NotRequired[ProcessingJobStatusType],
        "SortBy": NotRequired[SortByType],
        "SortOrder": NotRequired[SortOrderType],
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
    },
)

ListProjectsInputRequestTypeDef = TypedDict(
    "ListProjectsInputRequestTypeDef",
    {
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "MaxResults": NotRequired[int],
        "NameContains": NotRequired[str],
        "NextToken": NotRequired[str],
        "SortBy": NotRequired[ProjectSortByType],
        "SortOrder": NotRequired[ProjectSortOrderType],
    },
)

ListResourceCatalogsRequestRequestTypeDef = TypedDict(
    "ListResourceCatalogsRequestRequestTypeDef",
    {
        "NameContains": NotRequired[str],
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "SortOrder": NotRequired[ResourceCatalogSortOrderType],
        "SortBy": NotRequired[Literal["CreationTime"]],
        "MaxResults": NotRequired[int],
        "NextToken": NotRequired[str],
    },
)

ListStudioLifecycleConfigsRequestRequestTypeDef = TypedDict(
    "ListStudioLifecycleConfigsRequestRequestTypeDef",
    {
        "MaxResults": NotRequired[int],
        "NextToken": NotRequired[str],
        "NameContains": NotRequired[str],
        "AppTypeEquals": NotRequired[StudioLifecycleConfigAppTypeType],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "ModifiedTimeBefore": NotRequired[TimestampTypeDef],
        "ModifiedTimeAfter": NotRequired[TimestampTypeDef],
        "SortBy": NotRequired[StudioLifecycleConfigSortKeyType],
        "SortOrder": NotRequired[SortOrderType],
    },
)

ListTrainingJobsRequestRequestTypeDef = TypedDict(
    "ListTrainingJobsRequestRequestTypeDef",
    {
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "LastModifiedTimeAfter": NotRequired[TimestampTypeDef],
        "LastModifiedTimeBefore": NotRequired[TimestampTypeDef],
        "NameContains": NotRequired[str],
        "StatusEquals": NotRequired[TrainingJobStatusType],
        "SortBy": NotRequired[SortByType],
        "SortOrder": NotRequired[SortOrderType],
        "WarmPoolStatusEquals": NotRequired[WarmPoolResourceStatusType],
    },
)

ListTransformJobsRequestRequestTypeDef = TypedDict(
    "ListTransformJobsRequestRequestTypeDef",
    {
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "LastModifiedTimeAfter": NotRequired[TimestampTypeDef],
        "LastModifiedTimeBefore": NotRequired[TimestampTypeDef],
        "NameContains": NotRequired[str],
        "StatusEquals": NotRequired[TransformJobStatusType],
        "SortBy": NotRequired[SortByType],
        "SortOrder": NotRequired[SortOrderType],
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
    },
)

ListTrialComponentsRequestRequestTypeDef = TypedDict(
    "ListTrialComponentsRequestRequestTypeDef",
    {
        "ExperimentName": NotRequired[str],
        "TrialName": NotRequired[str],
        "SourceArn": NotRequired[str],
        "CreatedAfter": NotRequired[TimestampTypeDef],
        "CreatedBefore": NotRequired[TimestampTypeDef],
        "SortBy": NotRequired[SortTrialComponentsByType],
        "SortOrder": NotRequired[SortOrderType],
        "MaxResults": NotRequired[int],
        "NextToken": NotRequired[str],
    },
)

ListTrialsRequestRequestTypeDef = TypedDict(
    "ListTrialsRequestRequestTypeDef",
    {
        "ExperimentName": NotRequired[str],
        "TrialComponentName": NotRequired[str],
        "CreatedAfter": NotRequired[TimestampTypeDef],
        "CreatedBefore": NotRequired[TimestampTypeDef],
        "SortBy": NotRequired[SortTrialsByType],
        "SortOrder": NotRequired[SortOrderType],
        "MaxResults": NotRequired[int],
        "NextToken": NotRequired[str],
    },
)

QueryFiltersTypeDef = TypedDict(
    "QueryFiltersTypeDef",
    {
        "Types": NotRequired[Sequence[str]],
        "LineageTypes": NotRequired[Sequence[LineageTypeType]],
        "CreatedBefore": NotRequired[TimestampTypeDef],
        "CreatedAfter": NotRequired[TimestampTypeDef],
        "ModifiedBefore": NotRequired[TimestampTypeDef],
        "ModifiedAfter": NotRequired[TimestampTypeDef],
        "Properties": NotRequired[Mapping[str, str]],
    },
)

CreateTrialComponentRequestRequestTypeDef = TypedDict(
    "CreateTrialComponentRequestRequestTypeDef",
    {
        "TrialComponentName": str,
        "DisplayName": NotRequired[str],
        "Status": NotRequired[TrialComponentStatusTypeDef],
        "StartTime": NotRequired[TimestampTypeDef],
        "EndTime": NotRequired[TimestampTypeDef],
        "Parameters": NotRequired[Mapping[str, TrialComponentParameterValueTypeDef]],
        "InputArtifacts": NotRequired[Mapping[str, TrialComponentArtifactTypeDef]],
        "OutputArtifacts": NotRequired[Mapping[str, TrialComponentArtifactTypeDef]],
        "MetadataProperties": NotRequired[MetadataPropertiesTypeDef],
        "Tags": NotRequired[Sequence[TagTypeDef]],
    },
)

UpdateTrialComponentRequestRequestTypeDef = TypedDict(
    "UpdateTrialComponentRequestRequestTypeDef",
    {
        "TrialComponentName": str,
        "DisplayName": NotRequired[str],
        "Status": NotRequired[TrialComponentStatusTypeDef],
        "StartTime": NotRequired[TimestampTypeDef],
        "EndTime": NotRequired[TimestampTypeDef],
        "Parameters": NotRequired[Mapping[str, TrialComponentParameterValueTypeDef]],
        "ParametersToRemove": NotRequired[Sequence[str]],
        "InputArtifacts": NotRequired[Mapping[str, TrialComponentArtifactTypeDef]],
        "InputArtifactsToRemove": NotRequired[Sequence[str]],
        "OutputArtifacts": NotRequired[Mapping[str, TrialComponentArtifactTypeDef]],
        "OutputArtifactsToRemove": NotRequired[Sequence[str]],
    },
)

CreateWorkforceRequestRequestTypeDef = TypedDict(
    "CreateWorkforceRequestRequestTypeDef",
    {
        "WorkforceName": str,
        "CognitoConfig": NotRequired[CognitoConfigTypeDef],
        "OidcConfig": NotRequired[OidcConfigTypeDef],
        "SourceIpConfig": NotRequired[SourceIpConfigTypeDef],
        "Tags": NotRequired[Sequence[TagTypeDef]],
        "WorkforceVpcConfig": NotRequired[WorkforceVpcConfigRequestTypeDef],
    },
)

UpdateWorkforceRequestRequestTypeDef = TypedDict(
    "UpdateWorkforceRequestRequestTypeDef",
    {
        "WorkforceName": str,
        "SourceIpConfig": NotRequired[SourceIpConfigTypeDef],
        "OidcConfig": NotRequired[OidcConfigTypeDef],
        "WorkforceVpcConfig": NotRequired[WorkforceVpcConfigRequestTypeDef],
    },
)

KernelGatewayAppSettingsTypeDef = TypedDict(
    "KernelGatewayAppSettingsTypeDef",
    {
        "DefaultResourceSpec": NotRequired[ResourceSpecTypeDef],
        "CustomImages": NotRequired[Sequence[CustomImageTypeDef]],
        "LifecycleConfigArns": NotRequired[Sequence[str]],
    },
)

RSessionAppSettingsTypeDef = TypedDict(
    "RSessionAppSettingsTypeDef",
    {
        "DefaultResourceSpec": NotRequired[ResourceSpecTypeDef],
        "CustomImages": NotRequired[Sequence[CustomImageTypeDef]],
    },
)

ModelBiasBaselineConfigTypeDef = TypedDict(
    "ModelBiasBaselineConfigTypeDef",
    {
        "BaseliningJobName": NotRequired[str],
        "ConstraintsResource": NotRequired[MonitoringConstraintsResourceTypeDef],
    },
)

ModelExplainabilityBaselineConfigTypeDef = TypedDict(
    "ModelExplainabilityBaselineConfigTypeDef",
    {
        "BaseliningJobName": NotRequired[str],
        "ConstraintsResource": NotRequired[MonitoringConstraintsResourceTypeDef],
    },
)

ModelQualityBaselineConfigTypeDef = TypedDict(
    "ModelQualityBaselineConfigTypeDef",
    {
        "BaseliningJobName": NotRequired[str],
        "ConstraintsResource": NotRequired[MonitoringConstraintsResourceTypeDef],
    },
)

DataQualityBaselineConfigTypeDef = TypedDict(
    "DataQualityBaselineConfigTypeDef",
    {
        "BaseliningJobName": NotRequired[str],
        "ConstraintsResource": NotRequired[MonitoringConstraintsResourceTypeDef],
        "StatisticsResource": NotRequired[MonitoringStatisticsResourceTypeDef],
    },
)

MonitoringBaselineConfigTypeDef = TypedDict(
    "MonitoringBaselineConfigTypeDef",
    {
        "BaseliningJobName": NotRequired[str],
        "ConstraintsResource": NotRequired[MonitoringConstraintsResourceTypeDef],
        "StatisticsResource": NotRequired[MonitoringStatisticsResourceTypeDef],
    },
)

DataSourcePaginatorTypeDef = TypedDict(
    "DataSourcePaginatorTypeDef",
    {
        "S3DataSource": NotRequired[S3DataSourcePaginatorTypeDef],
        "FileSystemDataSource": NotRequired[FileSystemDataSourceTypeDef],
    },
)

DataSourceTypeDef = TypedDict(
    "DataSourceTypeDef",
    {
        "S3DataSource": NotRequired[S3DataSourceTypeDef],
        "FileSystemDataSource": NotRequired[FileSystemDataSourceTypeDef],
    },
)

DatasetDefinitionTypeDef = TypedDict(
    "DatasetDefinitionTypeDef",
    {
        "AthenaDatasetDefinition": NotRequired[AthenaDatasetDefinitionTypeDef],
        "RedshiftDatasetDefinition": NotRequired[RedshiftDatasetDefinitionTypeDef],
        "LocalPath": NotRequired[str],
        "DataDistributionType": NotRequired[DataDistributionTypeType],
        "InputMode": NotRequired[InputModeType],
    },
)

DeleteDomainRequestRequestTypeDef = TypedDict(
    "DeleteDomainRequestRequestTypeDef",
    {
        "DomainId": str,
        "RetentionPolicy": NotRequired[RetentionPolicyTypeDef],
    },
)

DeploymentRecommendationTypeDef = TypedDict(
    "DeploymentRecommendationTypeDef",
    {
        "RecommendationStatus": RecommendationStatusType,
        "RealTimeInferenceRecommendations": NotRequired[
            List[RealTimeInferenceRecommendationTypeDef]
        ],
    },
)

DeploymentStageTypeDef = TypedDict(
    "DeploymentStageTypeDef",
    {
        "StageName": str,
        "DeviceSelectionConfig": DeviceSelectionConfigTypeDef,
        "DeploymentConfig": NotRequired[EdgeDeploymentConfigTypeDef],
    },
)

DeploymentStageStatusSummaryTypeDef = TypedDict(
    "DeploymentStageStatusSummaryTypeDef",
    {
        "StageName": str,
        "DeviceSelectionConfig": DeviceSelectionConfigTypeDef,
        "DeploymentConfig": EdgeDeploymentConfigTypeDef,
        "DeploymentStatus": EdgeDeploymentStatusTypeDef,
    },
)

DescribeDeviceResponseTypeDef = TypedDict(
    "DescribeDeviceResponseTypeDef",
    {
        "DeviceArn": str,
        "DeviceName": str,
        "Description": str,
        "DeviceFleetName": str,
        "IotThingName": str,
        "RegistrationTime": datetime,
        "LatestHeartbeat": datetime,
        "Models": List[EdgeModelTypeDef],
        "MaxModels": int,
        "NextToken": str,
        "AgentVersion": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeEdgePackagingJobResponseTypeDef = TypedDict(
    "DescribeEdgePackagingJobResponseTypeDef",
    {
        "EdgePackagingJobArn": str,
        "EdgePackagingJobName": str,
        "CompilationJobName": str,
        "ModelName": str,
        "ModelVersion": str,
        "RoleArn": str,
        "OutputConfig": EdgeOutputConfigTypeDef,
        "ResourceKey": str,
        "EdgePackagingJobStatus": EdgePackagingJobStatusType,
        "EdgePackagingJobStatusMessage": str,
        "CreationTime": datetime,
        "LastModifiedTime": datetime,
        "ModelArtifact": str,
        "ModelSignature": str,
        "PresetDeploymentOutput": EdgePresetDeploymentOutputTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeEndpointInputEndpointDeletedWaitTypeDef = TypedDict(
    "DescribeEndpointInputEndpointDeletedWaitTypeDef",
    {
        "EndpointName": str,
        "WaiterConfig": NotRequired[WaiterConfigTypeDef],
    },
)

DescribeEndpointInputEndpointInServiceWaitTypeDef = TypedDict(
    "DescribeEndpointInputEndpointInServiceWaitTypeDef",
    {
        "EndpointName": str,
        "WaiterConfig": NotRequired[WaiterConfigTypeDef],
    },
)

DescribeImageRequestImageCreatedWaitTypeDef = TypedDict(
    "DescribeImageRequestImageCreatedWaitTypeDef",
    {
        "ImageName": str,
        "WaiterConfig": NotRequired[WaiterConfigTypeDef],
    },
)

DescribeImageRequestImageDeletedWaitTypeDef = TypedDict(
    "DescribeImageRequestImageDeletedWaitTypeDef",
    {
        "ImageName": str,
        "WaiterConfig": NotRequired[WaiterConfigTypeDef],
    },
)

DescribeImageRequestImageUpdatedWaitTypeDef = TypedDict(
    "DescribeImageRequestImageUpdatedWaitTypeDef",
    {
        "ImageName": str,
        "WaiterConfig": NotRequired[WaiterConfigTypeDef],
    },
)

DescribeImageVersionRequestImageVersionCreatedWaitTypeDef = TypedDict(
    "DescribeImageVersionRequestImageVersionCreatedWaitTypeDef",
    {
        "ImageName": str,
        "Version": NotRequired[int],
        "Alias": NotRequired[str],
        "WaiterConfig": NotRequired[WaiterConfigTypeDef],
    },
)

DescribeImageVersionRequestImageVersionDeletedWaitTypeDef = TypedDict(
    "DescribeImageVersionRequestImageVersionDeletedWaitTypeDef",
    {
        "ImageName": str,
        "Version": NotRequired[int],
        "Alias": NotRequired[str],
        "WaiterConfig": NotRequired[WaiterConfigTypeDef],
    },
)

DescribeNotebookInstanceInputNotebookInstanceDeletedWaitTypeDef = TypedDict(
    "DescribeNotebookInstanceInputNotebookInstanceDeletedWaitTypeDef",
    {
        "NotebookInstanceName": str,
        "WaiterConfig": NotRequired[WaiterConfigTypeDef],
    },
)

DescribeNotebookInstanceInputNotebookInstanceInServiceWaitTypeDef = TypedDict(
    "DescribeNotebookInstanceInputNotebookInstanceInServiceWaitTypeDef",
    {
        "NotebookInstanceName": str,
        "WaiterConfig": NotRequired[WaiterConfigTypeDef],
    },
)

DescribeNotebookInstanceInputNotebookInstanceStoppedWaitTypeDef = TypedDict(
    "DescribeNotebookInstanceInputNotebookInstanceStoppedWaitTypeDef",
    {
        "NotebookInstanceName": str,
        "WaiterConfig": NotRequired[WaiterConfigTypeDef],
    },
)

DescribeProcessingJobRequestProcessingJobCompletedOrStoppedWaitTypeDef = TypedDict(
    "DescribeProcessingJobRequestProcessingJobCompletedOrStoppedWaitTypeDef",
    {
        "ProcessingJobName": str,
        "WaiterConfig": NotRequired[WaiterConfigTypeDef],
    },
)

DescribeTrainingJobRequestTrainingJobCompletedOrStoppedWaitTypeDef = TypedDict(
    "DescribeTrainingJobRequestTrainingJobCompletedOrStoppedWaitTypeDef",
    {
        "TrainingJobName": str,
        "WaiterConfig": NotRequired[WaiterConfigTypeDef],
    },
)

DescribeTransformJobRequestTransformJobCompletedOrStoppedWaitTypeDef = TypedDict(
    "DescribeTransformJobRequestTransformJobCompletedOrStoppedWaitTypeDef",
    {
        "TransformJobName": str,
        "WaiterConfig": NotRequired[WaiterConfigTypeDef],
    },
)

ExperimentSummaryTypeDef = TypedDict(
    "ExperimentSummaryTypeDef",
    {
        "ExperimentArn": NotRequired[str],
        "ExperimentName": NotRequired[str],
        "DisplayName": NotRequired[str],
        "ExperimentSource": NotRequired[ExperimentSourceTypeDef],
        "CreationTime": NotRequired[datetime],
        "LastModifiedTime": NotRequired[datetime],
    },
)

FeatureGroupSummaryTypeDef = TypedDict(
    "FeatureGroupSummaryTypeDef",
    {
        "FeatureGroupName": str,
        "FeatureGroupArn": str,
        "CreationTime": datetime,
        "FeatureGroupStatus": NotRequired[FeatureGroupStatusType],
        "OfflineStoreStatus": NotRequired[OfflineStoreStatusTypeDef],
    },
)

DescribeFeatureMetadataResponseTypeDef = TypedDict(
    "DescribeFeatureMetadataResponseTypeDef",
    {
        "FeatureGroupArn": str,
        "FeatureGroupName": str,
        "FeatureName": str,
        "FeatureType": FeatureTypeType,
        "CreationTime": datetime,
        "LastModifiedTime": datetime,
        "Description": str,
        "Parameters": List[FeatureParameterTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

FeatureMetadataTypeDef = TypedDict(
    "FeatureMetadataTypeDef",
    {
        "FeatureGroupArn": NotRequired[str],
        "FeatureGroupName": NotRequired[str],
        "FeatureName": NotRequired[str],
        "FeatureType": NotRequired[FeatureTypeType],
        "CreationTime": NotRequired[datetime],
        "LastModifiedTime": NotRequired[datetime],
        "Description": NotRequired[str],
        "Parameters": NotRequired[List[FeatureParameterTypeDef]],
    },
)

UpdateFeatureMetadataRequestRequestTypeDef = TypedDict(
    "UpdateFeatureMetadataRequestRequestTypeDef",
    {
        "FeatureGroupName": str,
        "FeatureName": str,
        "Description": NotRequired[str],
        "ParameterAdditions": NotRequired[Sequence[FeatureParameterTypeDef]],
        "ParameterRemovals": NotRequired[Sequence[str]],
    },
)

DescribeHubContentResponseTypeDef = TypedDict(
    "DescribeHubContentResponseTypeDef",
    {
        "HubContentName": str,
        "HubContentArn": str,
        "HubContentVersion": str,
        "HubContentType": HubContentTypeType,
        "DocumentSchemaVersion": str,
        "HubName": str,
        "HubArn": str,
        "HubContentDisplayName": str,
        "HubContentDescription": str,
        "HubContentMarkdown": str,
        "HubContentDocument": str,
        "HubContentSearchKeywords": List[str],
        "HubContentDependencies": List[HubContentDependencyTypeDef],
        "HubContentStatus": HubContentStatusType,
        "FailureReason": str,
        "CreationTime": datetime,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeHumanTaskUiResponseTypeDef = TypedDict(
    "DescribeHumanTaskUiResponseTypeDef",
    {
        "HumanTaskUiArn": str,
        "HumanTaskUiName": str,
        "HumanTaskUiStatus": HumanTaskUiStatusType,
        "CreationTime": datetime,
        "UiTemplate": UiTemplateInfoTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeModelCardExportJobResponseTypeDef = TypedDict(
    "DescribeModelCardExportJobResponseTypeDef",
    {
        "ModelCardExportJobName": str,
        "ModelCardExportJobArn": str,
        "Status": ModelCardExportJobStatusType,
        "ModelCardName": str,
        "ModelCardVersion": int,
        "OutputConfig": ModelCardExportOutputConfigTypeDef,
        "CreatedAt": datetime,
        "LastModifiedAt": datetime,
        "FailureReason": str,
        "ExportArtifacts": ModelCardExportArtifactsTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListMonitoringExecutionsResponseTypeDef = TypedDict(
    "ListMonitoringExecutionsResponseTypeDef",
    {
        "MonitoringExecutionSummaries": List[MonitoringExecutionSummaryTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeSubscribedWorkteamResponseTypeDef = TypedDict(
    "DescribeSubscribedWorkteamResponseTypeDef",
    {
        "SubscribedWorkteam": SubscribedWorkteamTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListSubscribedWorkteamsResponseTypeDef = TypedDict(
    "ListSubscribedWorkteamsResponseTypeDef",
    {
        "SubscribedWorkteams": List[SubscribedWorkteamTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

TrainingJobSummaryTypeDef = TypedDict(
    "TrainingJobSummaryTypeDef",
    {
        "TrainingJobName": str,
        "TrainingJobArn": str,
        "CreationTime": datetime,
        "TrainingJobStatus": TrainingJobStatusType,
        "TrainingEndTime": NotRequired[datetime],
        "LastModifiedTime": NotRequired[datetime],
        "WarmPoolStatus": NotRequired[WarmPoolStatusTypeDef],
    },
)

TrialSummaryTypeDef = TypedDict(
    "TrialSummaryTypeDef",
    {
        "TrialArn": NotRequired[str],
        "TrialName": NotRequired[str],
        "DisplayName": NotRequired[str],
        "TrialSource": NotRequired[TrialSourceTypeDef],
        "CreationTime": NotRequired[datetime],
        "LastModifiedTime": NotRequired[datetime],
    },
)

DesiredWeightAndCapacityTypeDef = TypedDict(
    "DesiredWeightAndCapacityTypeDef",
    {
        "VariantName": str,
        "DesiredWeight": NotRequired[float],
        "DesiredInstanceCount": NotRequired[int],
        "ServerlessUpdateConfig": NotRequired[ProductionVariantServerlessUpdateConfigTypeDef],
    },
)

ListStageDevicesResponseTypeDef = TypedDict(
    "ListStageDevicesResponseTypeDef",
    {
        "DeviceDeploymentSummaries": List[DeviceDeploymentSummaryTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListDeviceFleetsResponseTypeDef = TypedDict(
    "ListDeviceFleetsResponseTypeDef",
    {
        "DeviceFleetSummaries": List[DeviceFleetSummaryTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DeviceSummaryTypeDef = TypedDict(
    "DeviceSummaryTypeDef",
    {
        "DeviceName": str,
        "DeviceArn": str,
        "Description": NotRequired[str],
        "DeviceFleetName": NotRequired[str],
        "IotThingName": NotRequired[str],
        "RegistrationTime": NotRequired[datetime],
        "LatestHeartbeat": NotRequired[datetime],
        "Models": NotRequired[List[EdgeModelSummaryTypeDef]],
        "AgentVersion": NotRequired[str],
    },
)

RegisterDevicesRequestRequestTypeDef = TypedDict(
    "RegisterDevicesRequestRequestTypeDef",
    {
        "DeviceFleetName": str,
        "Devices": Sequence[DeviceTypeDef],
        "Tags": NotRequired[Sequence[TagTypeDef]],
    },
)

UpdateDevicesRequestRequestTypeDef = TypedDict(
    "UpdateDevicesRequestRequestTypeDef",
    {
        "DeviceFleetName": str,
        "Devices": Sequence[DeviceTypeDef],
    },
)

ListDomainsResponseTypeDef = TypedDict(
    "ListDomainsResponseTypeDef",
    {
        "Domains": List[DomainDetailsTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DriftCheckBiasTypeDef = TypedDict(
    "DriftCheckBiasTypeDef",
    {
        "ConfigFile": NotRequired[FileSourceTypeDef],
        "PreTrainingConstraints": NotRequired[MetricsSourceTypeDef],
        "PostTrainingConstraints": NotRequired[MetricsSourceTypeDef],
    },
)

DriftCheckExplainabilityTypeDef = TypedDict(
    "DriftCheckExplainabilityTypeDef",
    {
        "Constraints": NotRequired[MetricsSourceTypeDef],
        "ConfigFile": NotRequired[FileSourceTypeDef],
    },
)

ListEdgeDeploymentPlansResponseTypeDef = TypedDict(
    "ListEdgeDeploymentPlansResponseTypeDef",
    {
        "EdgeDeploymentPlanSummaries": List[EdgeDeploymentPlanSummaryTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

GetDeviceFleetReportResponseTypeDef = TypedDict(
    "GetDeviceFleetReportResponseTypeDef",
    {
        "DeviceFleetArn": str,
        "DeviceFleetName": str,
        "OutputConfig": EdgeOutputConfigTypeDef,
        "Description": str,
        "ReportGenerated": datetime,
        "DeviceStats": DeviceStatsTypeDef,
        "AgentVersions": List[AgentVersionTypeDef],
        "ModelStats": List[EdgeModelStatTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListEdgePackagingJobsResponseTypeDef = TypedDict(
    "ListEdgePackagingJobsResponseTypeDef",
    {
        "EdgePackagingJobSummaries": List[EdgePackagingJobSummaryTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListEndpointConfigsOutputTypeDef = TypedDict(
    "ListEndpointConfigsOutputTypeDef",
    {
        "EndpointConfigs": List[EndpointConfigSummaryTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

EndpointOutputConfigurationTypeDef = TypedDict(
    "EndpointOutputConfigurationTypeDef",
    {
        "EndpointName": str,
        "VariantName": str,
        "InstanceType": NotRequired[ProductionVariantInstanceTypeType],
        "InitialInstanceCount": NotRequired[int],
        "ServerlessConfig": NotRequired[ProductionVariantServerlessConfigTypeDef],
    },
)

EndpointPerformanceTypeDef = TypedDict(
    "EndpointPerformanceTypeDef",
    {
        "Metrics": InferenceMetricsTypeDef,
        "EndpointInfo": EndpointInfoTypeDef,
    },
)

ListEndpointsOutputTypeDef = TypedDict(
    "ListEndpointsOutputTypeDef",
    {
        "Endpoints": List[EndpointSummaryTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ModelConfigurationTypeDef = TypedDict(
    "ModelConfigurationTypeDef",
    {
        "InferenceSpecificationName": NotRequired[str],
        "EnvironmentParameters": NotRequired[List[EnvironmentParameterTypeDef]],
        "CompilationJobName": NotRequired[str],
    },
)

NestedFiltersTypeDef = TypedDict(
    "NestedFiltersTypeDef",
    {
        "NestedPropertyName": str,
        "Filters": Sequence[FilterTypeDef],
    },
)

HyperParameterTrainingJobSummaryTypeDef = TypedDict(
    "HyperParameterTrainingJobSummaryTypeDef",
    {
        "TrainingJobName": str,
        "TrainingJobArn": str,
        "CreationTime": datetime,
        "TrainingJobStatus": TrainingJobStatusType,
        "TunedHyperParameters": Dict[str, str],
        "TrainingJobDefinitionName": NotRequired[str],
        "TuningJobName": NotRequired[str],
        "TrainingStartTime": NotRequired[datetime],
        "TrainingEndTime": NotRequired[datetime],
        "FailureReason": NotRequired[str],
        "FinalHyperParameterTuningJobObjectiveMetric": NotRequired[
            FinalHyperParameterTuningJobObjectiveMetricTypeDef
        ],
        "ObjectiveStatus": NotRequired[ObjectiveStatusType],
    },
)

ListFlowDefinitionsResponseTypeDef = TypedDict(
    "ListFlowDefinitionsResponseTypeDef",
    {
        "FlowDefinitionSummaries": List[FlowDefinitionSummaryTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

GetScalingConfigurationRecommendationRequestRequestTypeDef = TypedDict(
    "GetScalingConfigurationRecommendationRequestRequestTypeDef",
    {
        "InferenceRecommendationsJobName": str,
        "RecommendationId": NotRequired[str],
        "EndpointName": NotRequired[str],
        "TargetCpuUtilizationPerCore": NotRequired[int],
        "ScalingPolicyObjective": NotRequired[ScalingPolicyObjectiveTypeDef],
    },
)

GetSearchSuggestionsResponseTypeDef = TypedDict(
    "GetSearchSuggestionsResponseTypeDef",
    {
        "PropertyNameSuggestions": List[PropertyNameSuggestionTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

UpdateCodeRepositoryInputRequestTypeDef = TypedDict(
    "UpdateCodeRepositoryInputRequestTypeDef",
    {
        "CodeRepositoryName": str,
        "GitConfig": NotRequired[GitConfigForUpdateTypeDef],
    },
)

ListHubContentVersionsResponseTypeDef = TypedDict(
    "ListHubContentVersionsResponseTypeDef",
    {
        "HubContentSummaries": List[HubContentInfoTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListHubContentsResponseTypeDef = TypedDict(
    "ListHubContentsResponseTypeDef",
    {
        "HubContentSummaries": List[HubContentInfoTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListHubsResponseTypeDef = TypedDict(
    "ListHubsResponseTypeDef",
    {
        "HubSummaries": List[HubInfoTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

HumanLoopActivationConfigTypeDef = TypedDict(
    "HumanLoopActivationConfigTypeDef",
    {
        "HumanLoopActivationConditionsConfig": HumanLoopActivationConditionsConfigTypeDef,
    },
)

ListHumanTaskUisResponseTypeDef = TypedDict(
    "ListHumanTaskUisResponseTypeDef",
    {
        "HumanTaskUiSummaries": List[HumanTaskUiSummaryTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

NetworkConfigPaginatorTypeDef = TypedDict(
    "NetworkConfigPaginatorTypeDef",
    {
        "EnableInterContainerTrafficEncryption": NotRequired[bool],
        "EnableNetworkIsolation": NotRequired[bool],
        "VpcConfig": NotRequired[VpcConfigPaginatorTypeDef],
    },
)

HyperParameterTuningResourceConfigPaginatorTypeDef = TypedDict(
    "HyperParameterTuningResourceConfigPaginatorTypeDef",
    {
        "InstanceType": NotRequired[TrainingInstanceTypeType],
        "InstanceCount": NotRequired[int],
        "VolumeSizeInGB": NotRequired[int],
        "VolumeKmsKeyId": NotRequired[str],
        "AllocationStrategy": NotRequired[Literal["Prioritized"]],
        "InstanceConfigs": NotRequired[List[HyperParameterTuningInstanceConfigTypeDef]],
    },
)

HyperParameterTuningResourceConfigTypeDef = TypedDict(
    "HyperParameterTuningResourceConfigTypeDef",
    {
        "InstanceType": NotRequired[TrainingInstanceTypeType],
        "InstanceCount": NotRequired[int],
        "VolumeSizeInGB": NotRequired[int],
        "VolumeKmsKeyId": NotRequired[str],
        "AllocationStrategy": NotRequired[Literal["Prioritized"]],
        "InstanceConfigs": NotRequired[Sequence[HyperParameterTuningInstanceConfigTypeDef]],
    },
)

HyperParameterTuningJobSummaryTypeDef = TypedDict(
    "HyperParameterTuningJobSummaryTypeDef",
    {
        "HyperParameterTuningJobName": str,
        "HyperParameterTuningJobArn": str,
        "HyperParameterTuningJobStatus": HyperParameterTuningJobStatusType,
        "Strategy": HyperParameterTuningJobStrategyTypeType,
        "CreationTime": datetime,
        "TrainingJobStatusCounters": TrainingJobStatusCountersTypeDef,
        "ObjectiveStatusCounters": ObjectiveStatusCountersTypeDef,
        "HyperParameterTuningEndTime": NotRequired[datetime],
        "LastModifiedTime": NotRequired[datetime],
        "ResourceLimits": NotRequired[ResourceLimitsTypeDef],
    },
)

HyperParameterTuningJobStrategyConfigTypeDef = TypedDict(
    "HyperParameterTuningJobStrategyConfigTypeDef",
    {
        "HyperbandStrategyConfig": NotRequired[HyperbandStrategyConfigTypeDef],
    },
)

HyperParameterTuningJobWarmStartConfigPaginatorTypeDef = TypedDict(
    "HyperParameterTuningJobWarmStartConfigPaginatorTypeDef",
    {
        "ParentHyperParameterTuningJobs": List[ParentHyperParameterTuningJobTypeDef],
        "WarmStartType": HyperParameterTuningJobWarmStartTypeType,
    },
)

HyperParameterTuningJobWarmStartConfigTypeDef = TypedDict(
    "HyperParameterTuningJobWarmStartConfigTypeDef",
    {
        "ParentHyperParameterTuningJobs": Sequence[ParentHyperParameterTuningJobTypeDef],
        "WarmStartType": HyperParameterTuningJobWarmStartTypeType,
    },
)

UserContextTypeDef = TypedDict(
    "UserContextTypeDef",
    {
        "UserProfileArn": NotRequired[str],
        "UserProfileName": NotRequired[str],
        "DomainId": NotRequired[str],
        "IamIdentity": NotRequired[IamIdentityTypeDef],
    },
)

ImageConfigTypeDef = TypedDict(
    "ImageConfigTypeDef",
    {
        "RepositoryAccessMode": RepositoryAccessModeType,
        "RepositoryAuthConfig": NotRequired[RepositoryAuthConfigTypeDef],
    },
)

ListImagesResponseTypeDef = TypedDict(
    "ListImagesResponseTypeDef",
    {
        "Images": List[ImageTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListImageVersionsResponseTypeDef = TypedDict(
    "ListImageVersionsResponseTypeDef",
    {
        "ImageVersions": List[ImageVersionTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

InferenceExperimentSummaryPaginatorTypeDef = TypedDict(
    "InferenceExperimentSummaryPaginatorTypeDef",
    {
        "Name": str,
        "Type": Literal["ShadowMode"],
        "Status": InferenceExperimentStatusType,
        "CreationTime": datetime,
        "LastModifiedTime": datetime,
        "Schedule": NotRequired[InferenceExperimentSchedulePaginatorTypeDef],
        "StatusReason": NotRequired[str],
        "Description": NotRequired[str],
        "CompletionTime": NotRequired[datetime],
        "RoleArn": NotRequired[str],
    },
)

ListInferenceRecommendationsJobsResponseTypeDef = TypedDict(
    "ListInferenceRecommendationsJobsResponseTypeDef",
    {
        "InferenceRecommendationsJobs": List[InferenceRecommendationsJobTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ResourceConfigPaginatorTypeDef = TypedDict(
    "ResourceConfigPaginatorTypeDef",
    {
        "VolumeSizeInGB": int,
        "InstanceType": NotRequired[TrainingInstanceTypeType],
        "InstanceCount": NotRequired[int],
        "VolumeKmsKeyId": NotRequired[str],
        "InstanceGroups": NotRequired[List[InstanceGroupTypeDef]],
        "KeepAlivePeriodInSeconds": NotRequired[int],
    },
)

ResourceConfigTypeDef = TypedDict(
    "ResourceConfigTypeDef",
    {
        "VolumeSizeInGB": int,
        "InstanceType": NotRequired[TrainingInstanceTypeType],
        "InstanceCount": NotRequired[int],
        "VolumeKmsKeyId": NotRequired[str],
        "InstanceGroups": NotRequired[Sequence[InstanceGroupTypeDef]],
        "KeepAlivePeriodInSeconds": NotRequired[int],
    },
)

ParameterRangeTypeDef = TypedDict(
    "ParameterRangeTypeDef",
    {
        "IntegerParameterRangeSpecification": NotRequired[
            IntegerParameterRangeSpecificationTypeDef
        ],
        "ContinuousParameterRangeSpecification": NotRequired[
            ContinuousParameterRangeSpecificationTypeDef
        ],
        "CategoricalParameterRangeSpecification": NotRequired[
            CategoricalParameterRangeSpecificationTypeDef
        ],
    },
)

ParameterRangesPaginatorTypeDef = TypedDict(
    "ParameterRangesPaginatorTypeDef",
    {
        "IntegerParameterRanges": NotRequired[List[IntegerParameterRangeTypeDef]],
        "ContinuousParameterRanges": NotRequired[List[ContinuousParameterRangeTypeDef]],
        "CategoricalParameterRanges": NotRequired[List[CategoricalParameterRangePaginatorTypeDef]],
        "AutoParameters": NotRequired[List[AutoParameterTypeDef]],
    },
)

ParameterRangesTypeDef = TypedDict(
    "ParameterRangesTypeDef",
    {
        "IntegerParameterRanges": NotRequired[Sequence[IntegerParameterRangeTypeDef]],
        "ContinuousParameterRanges": NotRequired[Sequence[ContinuousParameterRangeTypeDef]],
        "CategoricalParameterRanges": NotRequired[Sequence[CategoricalParameterRangeTypeDef]],
        "AutoParameters": NotRequired[Sequence[AutoParameterTypeDef]],
    },
)

KernelGatewayImageConfigPaginatorTypeDef = TypedDict(
    "KernelGatewayImageConfigPaginatorTypeDef",
    {
        "KernelSpecs": List[KernelSpecTypeDef],
        "FileSystemConfig": NotRequired[FileSystemConfigTypeDef],
    },
)

KernelGatewayImageConfigTypeDef = TypedDict(
    "KernelGatewayImageConfigTypeDef",
    {
        "KernelSpecs": Sequence[KernelSpecTypeDef],
        "FileSystemConfig": NotRequired[FileSystemConfigTypeDef],
    },
)

LabelingJobForWorkteamSummaryTypeDef = TypedDict(
    "LabelingJobForWorkteamSummaryTypeDef",
    {
        "JobReferenceCode": str,
        "WorkRequesterAccountId": str,
        "CreationTime": datetime,
        "LabelingJobName": NotRequired[str],
        "LabelCounters": NotRequired[LabelCountersForWorkteamTypeDef],
        "NumberOfHumanWorkersPerDataObject": NotRequired[int],
    },
)

LabelingJobDataSourceTypeDef = TypedDict(
    "LabelingJobDataSourceTypeDef",
    {
        "S3DataSource": NotRequired[LabelingJobS3DataSourceTypeDef],
        "SnsDataSource": NotRequired[LabelingJobSnsDataSourceTypeDef],
    },
)

ListLineageGroupsResponseTypeDef = TypedDict(
    "ListLineageGroupsResponseTypeDef",
    {
        "LineageGroupSummaries": List[LineageGroupSummaryTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListActionsRequestListActionsPaginateTypeDef = TypedDict(
    "ListActionsRequestListActionsPaginateTypeDef",
    {
        "SourceUri": NotRequired[str],
        "ActionType": NotRequired[str],
        "CreatedAfter": NotRequired[TimestampTypeDef],
        "CreatedBefore": NotRequired[TimestampTypeDef],
        "SortBy": NotRequired[SortActionsByType],
        "SortOrder": NotRequired[SortOrderType],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)

ListAlgorithmsInputListAlgorithmsPaginateTypeDef = TypedDict(
    "ListAlgorithmsInputListAlgorithmsPaginateTypeDef",
    {
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "NameContains": NotRequired[str],
        "SortBy": NotRequired[AlgorithmSortByType],
        "SortOrder": NotRequired[SortOrderType],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)

ListAliasesRequestListAliasesPaginateTypeDef = TypedDict(
    "ListAliasesRequestListAliasesPaginateTypeDef",
    {
        "ImageName": str,
        "Alias": NotRequired[str],
        "Version": NotRequired[int],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)

ListAppImageConfigsRequestListAppImageConfigsPaginateTypeDef = TypedDict(
    "ListAppImageConfigsRequestListAppImageConfigsPaginateTypeDef",
    {
        "NameContains": NotRequired[str],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "ModifiedTimeBefore": NotRequired[TimestampTypeDef],
        "ModifiedTimeAfter": NotRequired[TimestampTypeDef],
        "SortBy": NotRequired[AppImageConfigSortKeyType],
        "SortOrder": NotRequired[SortOrderType],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)

ListAppsRequestListAppsPaginateTypeDef = TypedDict(
    "ListAppsRequestListAppsPaginateTypeDef",
    {
        "SortOrder": NotRequired[SortOrderType],
        "SortBy": NotRequired[Literal["CreationTime"]],
        "DomainIdEquals": NotRequired[str],
        "UserProfileNameEquals": NotRequired[str],
        "SpaceNameEquals": NotRequired[str],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)

ListArtifactsRequestListArtifactsPaginateTypeDef = TypedDict(
    "ListArtifactsRequestListArtifactsPaginateTypeDef",
    {
        "SourceUri": NotRequired[str],
        "ArtifactType": NotRequired[str],
        "CreatedAfter": NotRequired[TimestampTypeDef],
        "CreatedBefore": NotRequired[TimestampTypeDef],
        "SortBy": NotRequired[Literal["CreationTime"]],
        "SortOrder": NotRequired[SortOrderType],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)

ListAssociationsRequestListAssociationsPaginateTypeDef = TypedDict(
    "ListAssociationsRequestListAssociationsPaginateTypeDef",
    {
        "SourceArn": NotRequired[str],
        "DestinationArn": NotRequired[str],
        "SourceType": NotRequired[str],
        "DestinationType": NotRequired[str],
        "AssociationType": NotRequired[AssociationEdgeTypeType],
        "CreatedAfter": NotRequired[TimestampTypeDef],
        "CreatedBefore": NotRequired[TimestampTypeDef],
        "SortBy": NotRequired[SortAssociationsByType],
        "SortOrder": NotRequired[SortOrderType],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)

ListAutoMLJobsRequestListAutoMLJobsPaginateTypeDef = TypedDict(
    "ListAutoMLJobsRequestListAutoMLJobsPaginateTypeDef",
    {
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "LastModifiedTimeAfter": NotRequired[TimestampTypeDef],
        "LastModifiedTimeBefore": NotRequired[TimestampTypeDef],
        "NameContains": NotRequired[str],
        "StatusEquals": NotRequired[AutoMLJobStatusType],
        "SortOrder": NotRequired[AutoMLSortOrderType],
        "SortBy": NotRequired[AutoMLSortByType],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)

ListCandidatesForAutoMLJobRequestListCandidatesForAutoMLJobPaginateTypeDef = TypedDict(
    "ListCandidatesForAutoMLJobRequestListCandidatesForAutoMLJobPaginateTypeDef",
    {
        "AutoMLJobName": str,
        "StatusEquals": NotRequired[CandidateStatusType],
        "CandidateNameEquals": NotRequired[str],
        "SortOrder": NotRequired[AutoMLSortOrderType],
        "SortBy": NotRequired[CandidateSortByType],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)

ListCodeRepositoriesInputListCodeRepositoriesPaginateTypeDef = TypedDict(
    "ListCodeRepositoriesInputListCodeRepositoriesPaginateTypeDef",
    {
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "LastModifiedTimeAfter": NotRequired[TimestampTypeDef],
        "LastModifiedTimeBefore": NotRequired[TimestampTypeDef],
        "NameContains": NotRequired[str],
        "SortBy": NotRequired[CodeRepositorySortByType],
        "SortOrder": NotRequired[CodeRepositorySortOrderType],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)

ListCompilationJobsRequestListCompilationJobsPaginateTypeDef = TypedDict(
    "ListCompilationJobsRequestListCompilationJobsPaginateTypeDef",
    {
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "LastModifiedTimeAfter": NotRequired[TimestampTypeDef],
        "LastModifiedTimeBefore": NotRequired[TimestampTypeDef],
        "NameContains": NotRequired[str],
        "StatusEquals": NotRequired[CompilationJobStatusType],
        "SortBy": NotRequired[ListCompilationJobsSortByType],
        "SortOrder": NotRequired[SortOrderType],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)

ListContextsRequestListContextsPaginateTypeDef = TypedDict(
    "ListContextsRequestListContextsPaginateTypeDef",
    {
        "SourceUri": NotRequired[str],
        "ContextType": NotRequired[str],
        "CreatedAfter": NotRequired[TimestampTypeDef],
        "CreatedBefore": NotRequired[TimestampTypeDef],
        "SortBy": NotRequired[SortContextsByType],
        "SortOrder": NotRequired[SortOrderType],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)

ListDataQualityJobDefinitionsRequestListDataQualityJobDefinitionsPaginateTypeDef = TypedDict(
    "ListDataQualityJobDefinitionsRequestListDataQualityJobDefinitionsPaginateTypeDef",
    {
        "EndpointName": NotRequired[str],
        "SortBy": NotRequired[MonitoringJobDefinitionSortKeyType],
        "SortOrder": NotRequired[SortOrderType],
        "NameContains": NotRequired[str],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)

ListDeviceFleetsRequestListDeviceFleetsPaginateTypeDef = TypedDict(
    "ListDeviceFleetsRequestListDeviceFleetsPaginateTypeDef",
    {
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "LastModifiedTimeAfter": NotRequired[TimestampTypeDef],
        "LastModifiedTimeBefore": NotRequired[TimestampTypeDef],
        "NameContains": NotRequired[str],
        "SortBy": NotRequired[ListDeviceFleetsSortByType],
        "SortOrder": NotRequired[SortOrderType],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)

ListDevicesRequestListDevicesPaginateTypeDef = TypedDict(
    "ListDevicesRequestListDevicesPaginateTypeDef",
    {
        "LatestHeartbeatAfter": NotRequired[TimestampTypeDef],
        "ModelName": NotRequired[str],
        "DeviceFleetName": NotRequired[str],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)

ListDomainsRequestListDomainsPaginateTypeDef = TypedDict(
    "ListDomainsRequestListDomainsPaginateTypeDef",
    {
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)

ListEdgeDeploymentPlansRequestListEdgeDeploymentPlansPaginateTypeDef = TypedDict(
    "ListEdgeDeploymentPlansRequestListEdgeDeploymentPlansPaginateTypeDef",
    {
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "LastModifiedTimeAfter": NotRequired[TimestampTypeDef],
        "LastModifiedTimeBefore": NotRequired[TimestampTypeDef],
        "NameContains": NotRequired[str],
        "DeviceFleetNameContains": NotRequired[str],
        "SortBy": NotRequired[ListEdgeDeploymentPlansSortByType],
        "SortOrder": NotRequired[SortOrderType],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)

ListEdgePackagingJobsRequestListEdgePackagingJobsPaginateTypeDef = TypedDict(
    "ListEdgePackagingJobsRequestListEdgePackagingJobsPaginateTypeDef",
    {
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "LastModifiedTimeAfter": NotRequired[TimestampTypeDef],
        "LastModifiedTimeBefore": NotRequired[TimestampTypeDef],
        "NameContains": NotRequired[str],
        "ModelNameContains": NotRequired[str],
        "StatusEquals": NotRequired[EdgePackagingJobStatusType],
        "SortBy": NotRequired[ListEdgePackagingJobsSortByType],
        "SortOrder": NotRequired[SortOrderType],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)

ListEndpointConfigsInputListEndpointConfigsPaginateTypeDef = TypedDict(
    "ListEndpointConfigsInputListEndpointConfigsPaginateTypeDef",
    {
        "SortBy": NotRequired[EndpointConfigSortKeyType],
        "SortOrder": NotRequired[OrderKeyType],
        "NameContains": NotRequired[str],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)

ListEndpointsInputListEndpointsPaginateTypeDef = TypedDict(
    "ListEndpointsInputListEndpointsPaginateTypeDef",
    {
        "SortBy": NotRequired[EndpointSortKeyType],
        "SortOrder": NotRequired[OrderKeyType],
        "NameContains": NotRequired[str],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "LastModifiedTimeBefore": NotRequired[TimestampTypeDef],
        "LastModifiedTimeAfter": NotRequired[TimestampTypeDef],
        "StatusEquals": NotRequired[EndpointStatusType],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)

ListExperimentsRequestListExperimentsPaginateTypeDef = TypedDict(
    "ListExperimentsRequestListExperimentsPaginateTypeDef",
    {
        "CreatedAfter": NotRequired[TimestampTypeDef],
        "CreatedBefore": NotRequired[TimestampTypeDef],
        "SortBy": NotRequired[SortExperimentsByType],
        "SortOrder": NotRequired[SortOrderType],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)

ListFeatureGroupsRequestListFeatureGroupsPaginateTypeDef = TypedDict(
    "ListFeatureGroupsRequestListFeatureGroupsPaginateTypeDef",
    {
        "NameContains": NotRequired[str],
        "FeatureGroupStatusEquals": NotRequired[FeatureGroupStatusType],
        "OfflineStoreStatusEquals": NotRequired[OfflineStoreStatusValueType],
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "SortOrder": NotRequired[FeatureGroupSortOrderType],
        "SortBy": NotRequired[FeatureGroupSortByType],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)

ListFlowDefinitionsRequestListFlowDefinitionsPaginateTypeDef = TypedDict(
    "ListFlowDefinitionsRequestListFlowDefinitionsPaginateTypeDef",
    {
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "SortOrder": NotRequired[SortOrderType],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)

ListHumanTaskUisRequestListHumanTaskUisPaginateTypeDef = TypedDict(
    "ListHumanTaskUisRequestListHumanTaskUisPaginateTypeDef",
    {
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "SortOrder": NotRequired[SortOrderType],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)

ListHyperParameterTuningJobsRequestListHyperParameterTuningJobsPaginateTypeDef = TypedDict(
    "ListHyperParameterTuningJobsRequestListHyperParameterTuningJobsPaginateTypeDef",
    {
        "SortBy": NotRequired[HyperParameterTuningJobSortByOptionsType],
        "SortOrder": NotRequired[SortOrderType],
        "NameContains": NotRequired[str],
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "LastModifiedTimeAfter": NotRequired[TimestampTypeDef],
        "LastModifiedTimeBefore": NotRequired[TimestampTypeDef],
        "StatusEquals": NotRequired[HyperParameterTuningJobStatusType],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)

ListImageVersionsRequestListImageVersionsPaginateTypeDef = TypedDict(
    "ListImageVersionsRequestListImageVersionsPaginateTypeDef",
    {
        "ImageName": str,
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "LastModifiedTimeAfter": NotRequired[TimestampTypeDef],
        "LastModifiedTimeBefore": NotRequired[TimestampTypeDef],
        "SortBy": NotRequired[ImageVersionSortByType],
        "SortOrder": NotRequired[ImageVersionSortOrderType],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)

ListImagesRequestListImagesPaginateTypeDef = TypedDict(
    "ListImagesRequestListImagesPaginateTypeDef",
    {
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "LastModifiedTimeAfter": NotRequired[TimestampTypeDef],
        "LastModifiedTimeBefore": NotRequired[TimestampTypeDef],
        "NameContains": NotRequired[str],
        "SortBy": NotRequired[ImageSortByType],
        "SortOrder": NotRequired[ImageSortOrderType],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)

ListInferenceExperimentsRequestListInferenceExperimentsPaginateTypeDef = TypedDict(
    "ListInferenceExperimentsRequestListInferenceExperimentsPaginateTypeDef",
    {
        "NameContains": NotRequired[str],
        "Type": NotRequired[Literal["ShadowMode"]],
        "StatusEquals": NotRequired[InferenceExperimentStatusType],
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "LastModifiedTimeAfter": NotRequired[TimestampTypeDef],
        "LastModifiedTimeBefore": NotRequired[TimestampTypeDef],
        "SortBy": NotRequired[SortInferenceExperimentsByType],
        "SortOrder": NotRequired[SortOrderType],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)

ListInferenceRecommendationsJobStepsRequestListInferenceRecommendationsJobStepsPaginateTypeDef = TypedDict(
    "ListInferenceRecommendationsJobStepsRequestListInferenceRecommendationsJobStepsPaginateTypeDef",
    {
        "JobName": str,
        "Status": NotRequired[RecommendationJobStatusType],
        "StepType": NotRequired[Literal["BENCHMARK"]],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)

ListInferenceRecommendationsJobsRequestListInferenceRecommendationsJobsPaginateTypeDef = TypedDict(
    "ListInferenceRecommendationsJobsRequestListInferenceRecommendationsJobsPaginateTypeDef",
    {
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "LastModifiedTimeAfter": NotRequired[TimestampTypeDef],
        "LastModifiedTimeBefore": NotRequired[TimestampTypeDef],
        "NameContains": NotRequired[str],
        "StatusEquals": NotRequired[RecommendationJobStatusType],
        "SortBy": NotRequired[ListInferenceRecommendationsJobsSortByType],
        "SortOrder": NotRequired[SortOrderType],
        "ModelNameEquals": NotRequired[str],
        "ModelPackageVersionArnEquals": NotRequired[str],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)

ListLabelingJobsForWorkteamRequestListLabelingJobsForWorkteamPaginateTypeDef = TypedDict(
    "ListLabelingJobsForWorkteamRequestListLabelingJobsForWorkteamPaginateTypeDef",
    {
        "WorkteamArn": str,
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "JobReferenceCodeContains": NotRequired[str],
        "SortBy": NotRequired[Literal["CreationTime"]],
        "SortOrder": NotRequired[SortOrderType],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)

ListLabelingJobsRequestListLabelingJobsPaginateTypeDef = TypedDict(
    "ListLabelingJobsRequestListLabelingJobsPaginateTypeDef",
    {
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "LastModifiedTimeAfter": NotRequired[TimestampTypeDef],
        "LastModifiedTimeBefore": NotRequired[TimestampTypeDef],
        "NameContains": NotRequired[str],
        "SortBy": NotRequired[SortByType],
        "SortOrder": NotRequired[SortOrderType],
        "StatusEquals": NotRequired[LabelingJobStatusType],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)

ListLineageGroupsRequestListLineageGroupsPaginateTypeDef = TypedDict(
    "ListLineageGroupsRequestListLineageGroupsPaginateTypeDef",
    {
        "CreatedAfter": NotRequired[TimestampTypeDef],
        "CreatedBefore": NotRequired[TimestampTypeDef],
        "SortBy": NotRequired[SortLineageGroupsByType],
        "SortOrder": NotRequired[SortOrderType],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)

ListModelBiasJobDefinitionsRequestListModelBiasJobDefinitionsPaginateTypeDef = TypedDict(
    "ListModelBiasJobDefinitionsRequestListModelBiasJobDefinitionsPaginateTypeDef",
    {
        "EndpointName": NotRequired[str],
        "SortBy": NotRequired[MonitoringJobDefinitionSortKeyType],
        "SortOrder": NotRequired[SortOrderType],
        "NameContains": NotRequired[str],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)

ListModelCardExportJobsRequestListModelCardExportJobsPaginateTypeDef = TypedDict(
    "ListModelCardExportJobsRequestListModelCardExportJobsPaginateTypeDef",
    {
        "ModelCardName": str,
        "ModelCardVersion": NotRequired[int],
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "ModelCardExportJobNameContains": NotRequired[str],
        "StatusEquals": NotRequired[ModelCardExportJobStatusType],
        "SortBy": NotRequired[ModelCardExportJobSortByType],
        "SortOrder": NotRequired[ModelCardExportJobSortOrderType],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)

ListModelCardVersionsRequestListModelCardVersionsPaginateTypeDef = TypedDict(
    "ListModelCardVersionsRequestListModelCardVersionsPaginateTypeDef",
    {
        "ModelCardName": str,
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "ModelCardStatus": NotRequired[ModelCardStatusType],
        "SortBy": NotRequired[Literal["Version"]],
        "SortOrder": NotRequired[ModelCardSortOrderType],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)

ListModelCardsRequestListModelCardsPaginateTypeDef = TypedDict(
    "ListModelCardsRequestListModelCardsPaginateTypeDef",
    {
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "NameContains": NotRequired[str],
        "ModelCardStatus": NotRequired[ModelCardStatusType],
        "SortBy": NotRequired[ModelCardSortByType],
        "SortOrder": NotRequired[ModelCardSortOrderType],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)

ListModelExplainabilityJobDefinitionsRequestListModelExplainabilityJobDefinitionsPaginateTypeDef = TypedDict(
    "ListModelExplainabilityJobDefinitionsRequestListModelExplainabilityJobDefinitionsPaginateTypeDef",
    {
        "EndpointName": NotRequired[str],
        "SortBy": NotRequired[MonitoringJobDefinitionSortKeyType],
        "SortOrder": NotRequired[SortOrderType],
        "NameContains": NotRequired[str],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)

ListModelPackageGroupsInputListModelPackageGroupsPaginateTypeDef = TypedDict(
    "ListModelPackageGroupsInputListModelPackageGroupsPaginateTypeDef",
    {
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "NameContains": NotRequired[str],
        "SortBy": NotRequired[ModelPackageGroupSortByType],
        "SortOrder": NotRequired[SortOrderType],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)

ListModelPackagesInputListModelPackagesPaginateTypeDef = TypedDict(
    "ListModelPackagesInputListModelPackagesPaginateTypeDef",
    {
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "NameContains": NotRequired[str],
        "ModelApprovalStatus": NotRequired[ModelApprovalStatusType],
        "ModelPackageGroupName": NotRequired[str],
        "ModelPackageType": NotRequired[ModelPackageTypeType],
        "SortBy": NotRequired[ModelPackageSortByType],
        "SortOrder": NotRequired[SortOrderType],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)

ListModelQualityJobDefinitionsRequestListModelQualityJobDefinitionsPaginateTypeDef = TypedDict(
    "ListModelQualityJobDefinitionsRequestListModelQualityJobDefinitionsPaginateTypeDef",
    {
        "EndpointName": NotRequired[str],
        "SortBy": NotRequired[MonitoringJobDefinitionSortKeyType],
        "SortOrder": NotRequired[SortOrderType],
        "NameContains": NotRequired[str],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)

ListModelsInputListModelsPaginateTypeDef = TypedDict(
    "ListModelsInputListModelsPaginateTypeDef",
    {
        "SortBy": NotRequired[ModelSortKeyType],
        "SortOrder": NotRequired[OrderKeyType],
        "NameContains": NotRequired[str],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)

ListMonitoringAlertHistoryRequestListMonitoringAlertHistoryPaginateTypeDef = TypedDict(
    "ListMonitoringAlertHistoryRequestListMonitoringAlertHistoryPaginateTypeDef",
    {
        "MonitoringScheduleName": NotRequired[str],
        "MonitoringAlertName": NotRequired[str],
        "SortBy": NotRequired[MonitoringAlertHistorySortKeyType],
        "SortOrder": NotRequired[SortOrderType],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "StatusEquals": NotRequired[MonitoringAlertStatusType],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)

ListMonitoringAlertsRequestListMonitoringAlertsPaginateTypeDef = TypedDict(
    "ListMonitoringAlertsRequestListMonitoringAlertsPaginateTypeDef",
    {
        "MonitoringScheduleName": str,
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)

ListMonitoringExecutionsRequestListMonitoringExecutionsPaginateTypeDef = TypedDict(
    "ListMonitoringExecutionsRequestListMonitoringExecutionsPaginateTypeDef",
    {
        "MonitoringScheduleName": NotRequired[str],
        "EndpointName": NotRequired[str],
        "SortBy": NotRequired[MonitoringExecutionSortKeyType],
        "SortOrder": NotRequired[SortOrderType],
        "ScheduledTimeBefore": NotRequired[TimestampTypeDef],
        "ScheduledTimeAfter": NotRequired[TimestampTypeDef],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "LastModifiedTimeBefore": NotRequired[TimestampTypeDef],
        "LastModifiedTimeAfter": NotRequired[TimestampTypeDef],
        "StatusEquals": NotRequired[ExecutionStatusType],
        "MonitoringJobDefinitionName": NotRequired[str],
        "MonitoringTypeEquals": NotRequired[MonitoringTypeType],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)

ListMonitoringSchedulesRequestListMonitoringSchedulesPaginateTypeDef = TypedDict(
    "ListMonitoringSchedulesRequestListMonitoringSchedulesPaginateTypeDef",
    {
        "EndpointName": NotRequired[str],
        "SortBy": NotRequired[MonitoringScheduleSortKeyType],
        "SortOrder": NotRequired[SortOrderType],
        "NameContains": NotRequired[str],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "LastModifiedTimeBefore": NotRequired[TimestampTypeDef],
        "LastModifiedTimeAfter": NotRequired[TimestampTypeDef],
        "StatusEquals": NotRequired[ScheduleStatusType],
        "MonitoringJobDefinitionName": NotRequired[str],
        "MonitoringTypeEquals": NotRequired[MonitoringTypeType],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)

ListNotebookInstanceLifecycleConfigsInputListNotebookInstanceLifecycleConfigsPaginateTypeDef = TypedDict(
    "ListNotebookInstanceLifecycleConfigsInputListNotebookInstanceLifecycleConfigsPaginateTypeDef",
    {
        "SortBy": NotRequired[NotebookInstanceLifecycleConfigSortKeyType],
        "SortOrder": NotRequired[NotebookInstanceLifecycleConfigSortOrderType],
        "NameContains": NotRequired[str],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "LastModifiedTimeBefore": NotRequired[TimestampTypeDef],
        "LastModifiedTimeAfter": NotRequired[TimestampTypeDef],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)

ListNotebookInstancesInputListNotebookInstancesPaginateTypeDef = TypedDict(
    "ListNotebookInstancesInputListNotebookInstancesPaginateTypeDef",
    {
        "SortBy": NotRequired[NotebookInstanceSortKeyType],
        "SortOrder": NotRequired[NotebookInstanceSortOrderType],
        "NameContains": NotRequired[str],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "LastModifiedTimeBefore": NotRequired[TimestampTypeDef],
        "LastModifiedTimeAfter": NotRequired[TimestampTypeDef],
        "StatusEquals": NotRequired[NotebookInstanceStatusType],
        "NotebookInstanceLifecycleConfigNameContains": NotRequired[str],
        "DefaultCodeRepositoryContains": NotRequired[str],
        "AdditionalCodeRepositoryEquals": NotRequired[str],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)

ListPipelineExecutionStepsRequestListPipelineExecutionStepsPaginateTypeDef = TypedDict(
    "ListPipelineExecutionStepsRequestListPipelineExecutionStepsPaginateTypeDef",
    {
        "PipelineExecutionArn": NotRequired[str],
        "SortOrder": NotRequired[SortOrderType],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)

ListPipelineExecutionsRequestListPipelineExecutionsPaginateTypeDef = TypedDict(
    "ListPipelineExecutionsRequestListPipelineExecutionsPaginateTypeDef",
    {
        "PipelineName": str,
        "CreatedAfter": NotRequired[TimestampTypeDef],
        "CreatedBefore": NotRequired[TimestampTypeDef],
        "SortBy": NotRequired[SortPipelineExecutionsByType],
        "SortOrder": NotRequired[SortOrderType],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)

ListPipelineParametersForExecutionRequestListPipelineParametersForExecutionPaginateTypeDef = TypedDict(
    "ListPipelineParametersForExecutionRequestListPipelineParametersForExecutionPaginateTypeDef",
    {
        "PipelineExecutionArn": str,
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)

ListPipelinesRequestListPipelinesPaginateTypeDef = TypedDict(
    "ListPipelinesRequestListPipelinesPaginateTypeDef",
    {
        "PipelineNamePrefix": NotRequired[str],
        "CreatedAfter": NotRequired[TimestampTypeDef],
        "CreatedBefore": NotRequired[TimestampTypeDef],
        "SortBy": NotRequired[SortPipelinesByType],
        "SortOrder": NotRequired[SortOrderType],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)

ListProcessingJobsRequestListProcessingJobsPaginateTypeDef = TypedDict(
    "ListProcessingJobsRequestListProcessingJobsPaginateTypeDef",
    {
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "LastModifiedTimeAfter": NotRequired[TimestampTypeDef],
        "LastModifiedTimeBefore": NotRequired[TimestampTypeDef],
        "NameContains": NotRequired[str],
        "StatusEquals": NotRequired[ProcessingJobStatusType],
        "SortBy": NotRequired[SortByType],
        "SortOrder": NotRequired[SortOrderType],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)

ListResourceCatalogsRequestListResourceCatalogsPaginateTypeDef = TypedDict(
    "ListResourceCatalogsRequestListResourceCatalogsPaginateTypeDef",
    {
        "NameContains": NotRequired[str],
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "SortOrder": NotRequired[ResourceCatalogSortOrderType],
        "SortBy": NotRequired[Literal["CreationTime"]],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)

ListSpacesRequestListSpacesPaginateTypeDef = TypedDict(
    "ListSpacesRequestListSpacesPaginateTypeDef",
    {
        "SortOrder": NotRequired[SortOrderType],
        "SortBy": NotRequired[SpaceSortKeyType],
        "DomainIdEquals": NotRequired[str],
        "SpaceNameContains": NotRequired[str],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)

ListStageDevicesRequestListStageDevicesPaginateTypeDef = TypedDict(
    "ListStageDevicesRequestListStageDevicesPaginateTypeDef",
    {
        "EdgeDeploymentPlanName": str,
        "StageName": str,
        "ExcludeDevicesDeployedInOtherStage": NotRequired[bool],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)

ListStudioLifecycleConfigsRequestListStudioLifecycleConfigsPaginateTypeDef = TypedDict(
    "ListStudioLifecycleConfigsRequestListStudioLifecycleConfigsPaginateTypeDef",
    {
        "NameContains": NotRequired[str],
        "AppTypeEquals": NotRequired[StudioLifecycleConfigAppTypeType],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "ModifiedTimeBefore": NotRequired[TimestampTypeDef],
        "ModifiedTimeAfter": NotRequired[TimestampTypeDef],
        "SortBy": NotRequired[StudioLifecycleConfigSortKeyType],
        "SortOrder": NotRequired[SortOrderType],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)

ListSubscribedWorkteamsRequestListSubscribedWorkteamsPaginateTypeDef = TypedDict(
    "ListSubscribedWorkteamsRequestListSubscribedWorkteamsPaginateTypeDef",
    {
        "NameContains": NotRequired[str],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)

ListTagsInputListTagsPaginateTypeDef = TypedDict(
    "ListTagsInputListTagsPaginateTypeDef",
    {
        "ResourceArn": str,
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)

ListTrainingJobsForHyperParameterTuningJobRequestListTrainingJobsForHyperParameterTuningJobPaginateTypeDef = TypedDict(
    "ListTrainingJobsForHyperParameterTuningJobRequestListTrainingJobsForHyperParameterTuningJobPaginateTypeDef",
    {
        "HyperParameterTuningJobName": str,
        "StatusEquals": NotRequired[TrainingJobStatusType],
        "SortBy": NotRequired[TrainingJobSortByOptionsType],
        "SortOrder": NotRequired[SortOrderType],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)

ListTrainingJobsRequestListTrainingJobsPaginateTypeDef = TypedDict(
    "ListTrainingJobsRequestListTrainingJobsPaginateTypeDef",
    {
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "LastModifiedTimeAfter": NotRequired[TimestampTypeDef],
        "LastModifiedTimeBefore": NotRequired[TimestampTypeDef],
        "NameContains": NotRequired[str],
        "StatusEquals": NotRequired[TrainingJobStatusType],
        "SortBy": NotRequired[SortByType],
        "SortOrder": NotRequired[SortOrderType],
        "WarmPoolStatusEquals": NotRequired[WarmPoolResourceStatusType],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)

ListTransformJobsRequestListTransformJobsPaginateTypeDef = TypedDict(
    "ListTransformJobsRequestListTransformJobsPaginateTypeDef",
    {
        "CreationTimeAfter": NotRequired[TimestampTypeDef],
        "CreationTimeBefore": NotRequired[TimestampTypeDef],
        "LastModifiedTimeAfter": NotRequired[TimestampTypeDef],
        "LastModifiedTimeBefore": NotRequired[TimestampTypeDef],
        "NameContains": NotRequired[str],
        "StatusEquals": NotRequired[TransformJobStatusType],
        "SortBy": NotRequired[SortByType],
        "SortOrder": NotRequired[SortOrderType],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)

ListTrialComponentsRequestListTrialComponentsPaginateTypeDef = TypedDict(
    "ListTrialComponentsRequestListTrialComponentsPaginateTypeDef",
    {
        "ExperimentName": NotRequired[str],
        "TrialName": NotRequired[str],
        "SourceArn": NotRequired[str],
        "CreatedAfter": NotRequired[TimestampTypeDef],
        "CreatedBefore": NotRequired[TimestampTypeDef],
        "SortBy": NotRequired[SortTrialComponentsByType],
        "SortOrder": NotRequired[SortOrderType],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)

ListTrialsRequestListTrialsPaginateTypeDef = TypedDict(
    "ListTrialsRequestListTrialsPaginateTypeDef",
    {
        "ExperimentName": NotRequired[str],
        "TrialComponentName": NotRequired[str],
        "CreatedAfter": NotRequired[TimestampTypeDef],
        "CreatedBefore": NotRequired[TimestampTypeDef],
        "SortBy": NotRequired[SortTrialsByType],
        "SortOrder": NotRequired[SortOrderType],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)

ListUserProfilesRequestListUserProfilesPaginateTypeDef = TypedDict(
    "ListUserProfilesRequestListUserProfilesPaginateTypeDef",
    {
        "SortOrder": NotRequired[SortOrderType],
        "SortBy": NotRequired[UserProfileSortKeyType],
        "DomainIdEquals": NotRequired[str],
        "UserProfileNameContains": NotRequired[str],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)

ListWorkforcesRequestListWorkforcesPaginateTypeDef = TypedDict(
    "ListWorkforcesRequestListWorkforcesPaginateTypeDef",
    {
        "SortBy": NotRequired[ListWorkforcesSortByOptionsType],
        "SortOrder": NotRequired[SortOrderType],
        "NameContains": NotRequired[str],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)

ListWorkteamsRequestListWorkteamsPaginateTypeDef = TypedDict(
    "ListWorkteamsRequestListWorkteamsPaginateTypeDef",
    {
        "SortBy": NotRequired[ListWorkteamsSortByOptionsType],
        "SortOrder": NotRequired[SortOrderType],
        "NameContains": NotRequired[str],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)

ListDataQualityJobDefinitionsResponseTypeDef = TypedDict(
    "ListDataQualityJobDefinitionsResponseTypeDef",
    {
        "JobDefinitionSummaries": List[MonitoringJobDefinitionSummaryTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListModelBiasJobDefinitionsResponseTypeDef = TypedDict(
    "ListModelBiasJobDefinitionsResponseTypeDef",
    {
        "JobDefinitionSummaries": List[MonitoringJobDefinitionSummaryTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListModelExplainabilityJobDefinitionsResponseTypeDef = TypedDict(
    "ListModelExplainabilityJobDefinitionsResponseTypeDef",
    {
        "JobDefinitionSummaries": List[MonitoringJobDefinitionSummaryTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListModelQualityJobDefinitionsResponseTypeDef = TypedDict(
    "ListModelQualityJobDefinitionsResponseTypeDef",
    {
        "JobDefinitionSummaries": List[MonitoringJobDefinitionSummaryTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListModelCardExportJobsResponseTypeDef = TypedDict(
    "ListModelCardExportJobsResponseTypeDef",
    {
        "ModelCardExportJobSummaries": List[ModelCardExportJobSummaryTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListModelCardVersionsResponseTypeDef = TypedDict(
    "ListModelCardVersionsResponseTypeDef",
    {
        "ModelCardVersionSummaryList": List[ModelCardVersionSummaryTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListModelCardsResponseTypeDef = TypedDict(
    "ListModelCardsResponseTypeDef",
    {
        "ModelCardSummaries": List[ModelCardSummaryTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListModelMetadataResponseTypeDef = TypedDict(
    "ListModelMetadataResponseTypeDef",
    {
        "ModelMetadataSummaries": List[ModelMetadataSummaryTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListModelPackageGroupsOutputTypeDef = TypedDict(
    "ListModelPackageGroupsOutputTypeDef",
    {
        "ModelPackageGroupSummaryList": List[ModelPackageGroupSummaryTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListModelPackagesOutputTypeDef = TypedDict(
    "ListModelPackagesOutputTypeDef",
    {
        "ModelPackageSummaryList": List[ModelPackageSummaryTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListModelsOutputTypeDef = TypedDict(
    "ListModelsOutputTypeDef",
    {
        "Models": List[ModelSummaryTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListMonitoringAlertHistoryResponseTypeDef = TypedDict(
    "ListMonitoringAlertHistoryResponseTypeDef",
    {
        "MonitoringAlertHistory": List[MonitoringAlertHistorySummaryTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListMonitoringSchedulesResponseTypeDef = TypedDict(
    "ListMonitoringSchedulesResponseTypeDef",
    {
        "MonitoringScheduleSummaries": List[MonitoringScheduleSummaryTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListNotebookInstanceLifecycleConfigsOutputTypeDef = TypedDict(
    "ListNotebookInstanceLifecycleConfigsOutputTypeDef",
    {
        "NextToken": str,
        "NotebookInstanceLifecycleConfigs": List[NotebookInstanceLifecycleConfigSummaryTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListNotebookInstancesOutputTypeDef = TypedDict(
    "ListNotebookInstancesOutputTypeDef",
    {
        "NextToken": str,
        "NotebookInstances": List[NotebookInstanceSummaryTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListPipelineExecutionsResponseTypeDef = TypedDict(
    "ListPipelineExecutionsResponseTypeDef",
    {
        "PipelineExecutionSummaries": List[PipelineExecutionSummaryTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListPipelineParametersForExecutionResponseTypeDef = TypedDict(
    "ListPipelineParametersForExecutionResponseTypeDef",
    {
        "PipelineParameters": List[ParameterTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListPipelinesResponseTypeDef = TypedDict(
    "ListPipelinesResponseTypeDef",
    {
        "PipelineSummaries": List[PipelineSummaryTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListProcessingJobsResponseTypeDef = TypedDict(
    "ListProcessingJobsResponseTypeDef",
    {
        "ProcessingJobSummaries": List[ProcessingJobSummaryTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListProjectsOutputTypeDef = TypedDict(
    "ListProjectsOutputTypeDef",
    {
        "ProjectSummaryList": List[ProjectSummaryTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListResourceCatalogsResponseTypeDef = TypedDict(
    "ListResourceCatalogsResponseTypeDef",
    {
        "ResourceCatalogs": List[ResourceCatalogTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListSpacesResponseTypeDef = TypedDict(
    "ListSpacesResponseTypeDef",
    {
        "Spaces": List[SpaceDetailsTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListStudioLifecycleConfigsResponseTypeDef = TypedDict(
    "ListStudioLifecycleConfigsResponseTypeDef",
    {
        "NextToken": str,
        "StudioLifecycleConfigs": List[StudioLifecycleConfigDetailsTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListTransformJobsResponseTypeDef = TypedDict(
    "ListTransformJobsResponseTypeDef",
    {
        "TransformJobSummaries": List[TransformJobSummaryTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListUserProfilesResponseTypeDef = TypedDict(
    "ListUserProfilesResponseTypeDef",
    {
        "UserProfiles": List[UserProfileDetailsTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

MemberDefinitionPaginatorTypeDef = TypedDict(
    "MemberDefinitionPaginatorTypeDef",
    {
        "CognitoMemberDefinition": NotRequired[CognitoMemberDefinitionTypeDef],
        "OidcMemberDefinition": NotRequired[OidcMemberDefinitionPaginatorTypeDef],
    },
)

MemberDefinitionTypeDef = TypedDict(
    "MemberDefinitionTypeDef",
    {
        "CognitoMemberDefinition": NotRequired[CognitoMemberDefinitionTypeDef],
        "OidcMemberDefinition": NotRequired[OidcMemberDefinitionTypeDef],
    },
)

MetricSpecificationTypeDef = TypedDict(
    "MetricSpecificationTypeDef",
    {
        "Predefined": NotRequired[PredefinedMetricSpecificationTypeDef],
        "Customized": NotRequired[CustomizedMetricSpecificationTypeDef],
    },
)

MonitoringAlertActionsTypeDef = TypedDict(
    "MonitoringAlertActionsTypeDef",
    {
        "ModelDashboardIndicator": NotRequired[ModelDashboardIndicatorActionTypeDef],
    },
)

ModelDataSourceTypeDef = TypedDict(
    "ModelDataSourceTypeDef",
    {
        "S3DataSource": S3ModelDataSourceTypeDef,
    },
)

ModelInfrastructureConfigTypeDef = TypedDict(
    "ModelInfrastructureConfigTypeDef",
    {
        "InfrastructureType": Literal["RealTimeInference"],
        "RealTimeInferenceConfig": RealTimeInferenceConfigTypeDef,
    },
)

ModelPackageContainerDefinitionTypeDef = TypedDict(
    "ModelPackageContainerDefinitionTypeDef",
    {
        "Image": str,
        "ContainerHostname": NotRequired[str],
        "ImageDigest": NotRequired[str],
        "ModelDataUrl": NotRequired[str],
        "ProductId": NotRequired[str],
        "Environment": NotRequired[Dict[str, str]],
        "ModelInput": NotRequired[ModelInputTypeDef],
        "Framework": NotRequired[str],
        "FrameworkVersion": NotRequired[str],
        "NearestModelName": NotRequired[str],
    },
)

RecommendationJobStoppingConditionsTypeDef = TypedDict(
    "RecommendationJobStoppingConditionsTypeDef",
    {
        "MaxInvocations": NotRequired[int],
        "ModelLatencyThresholds": NotRequired[Sequence[ModelLatencyThresholdTypeDef]],
        "FlatInvocations": NotRequired[FlatInvocationsType],
    },
)

ModelMetadataSearchExpressionTypeDef = TypedDict(
    "ModelMetadataSearchExpressionTypeDef",
    {
        "Filters": NotRequired[Sequence[ModelMetadataFilterTypeDef]],
    },
)

ModelPackageStatusDetailsTypeDef = TypedDict(
    "ModelPackageStatusDetailsTypeDef",
    {
        "ValidationStatuses": List[ModelPackageStatusItemTypeDef],
        "ImageScanStatuses": NotRequired[List[ModelPackageStatusItemTypeDef]],
    },
)

MonitoringResourcesTypeDef = TypedDict(
    "MonitoringResourcesTypeDef",
    {
        "ClusterConfig": MonitoringClusterConfigTypeDef,
    },
)

MonitoringDatasetFormatPaginatorTypeDef = TypedDict(
    "MonitoringDatasetFormatPaginatorTypeDef",
    {
        "Csv": NotRequired[MonitoringCsvDatasetFormatTypeDef],
        "Json": NotRequired[MonitoringJsonDatasetFormatTypeDef],
        "Parquet": NotRequired[Dict[str, Any]],
    },
)

MonitoringDatasetFormatTypeDef = TypedDict(
    "MonitoringDatasetFormatTypeDef",
    {
        "Csv": NotRequired[MonitoringCsvDatasetFormatTypeDef],
        "Json": NotRequired[MonitoringJsonDatasetFormatTypeDef],
        "Parquet": NotRequired[Mapping[str, Any]],
    },
)

MonitoringOutputTypeDef = TypedDict(
    "MonitoringOutputTypeDef",
    {
        "S3Output": MonitoringS3OutputTypeDef,
    },
)

OfflineStoreConfigTypeDef = TypedDict(
    "OfflineStoreConfigTypeDef",
    {
        "S3StorageConfig": S3StorageConfigTypeDef,
        "DisableGlueTableCreation": NotRequired[bool],
        "DataCatalogConfig": NotRequired[DataCatalogConfigTypeDef],
        "TableFormat": NotRequired[TableFormatType],
    },
)

OnlineStoreConfigTypeDef = TypedDict(
    "OnlineStoreConfigTypeDef",
    {
        "SecurityConfig": NotRequired[OnlineStoreSecurityConfigTypeDef],
        "EnableOnlineStore": NotRequired[bool],
        "TtlDuration": NotRequired[TtlDurationTypeDef],
    },
)

OnlineStoreConfigUpdateTypeDef = TypedDict(
    "OnlineStoreConfigUpdateTypeDef",
    {
        "TtlDuration": NotRequired[TtlDurationTypeDef],
    },
)

OutputConfigTypeDef = TypedDict(
    "OutputConfigTypeDef",
    {
        "S3OutputLocation": str,
        "TargetDevice": NotRequired[TargetDeviceType],
        "TargetPlatform": NotRequired[TargetPlatformTypeDef],
        "CompilerOptions": NotRequired[str],
        "KmsKeyId": NotRequired[str],
    },
)

PendingProductionVariantSummaryTypeDef = TypedDict(
    "PendingProductionVariantSummaryTypeDef",
    {
        "VariantName": str,
        "DeployedImages": NotRequired[List[DeployedImageTypeDef]],
        "CurrentWeight": NotRequired[float],
        "DesiredWeight": NotRequired[float],
        "CurrentInstanceCount": NotRequired[int],
        "DesiredInstanceCount": NotRequired[int],
        "InstanceType": NotRequired[ProductionVariantInstanceTypeType],
        "AcceleratorType": NotRequired[ProductionVariantAcceleratorTypeType],
        "VariantStatus": NotRequired[List[ProductionVariantStatusTypeDef]],
        "CurrentServerlessConfig": NotRequired[ProductionVariantServerlessConfigTypeDef],
        "DesiredServerlessConfig": NotRequired[ProductionVariantServerlessConfigTypeDef],
    },
)

ProductionVariantSummaryTypeDef = TypedDict(
    "ProductionVariantSummaryTypeDef",
    {
        "VariantName": str,
        "DeployedImages": NotRequired[List[DeployedImageTypeDef]],
        "CurrentWeight": NotRequired[float],
        "DesiredWeight": NotRequired[float],
        "CurrentInstanceCount": NotRequired[int],
        "DesiredInstanceCount": NotRequired[int],
        "VariantStatus": NotRequired[List[ProductionVariantStatusTypeDef]],
        "CurrentServerlessConfig": NotRequired[ProductionVariantServerlessConfigTypeDef],
        "DesiredServerlessConfig": NotRequired[ProductionVariantServerlessConfigTypeDef],
    },
)

ProcessingResourcesTypeDef = TypedDict(
    "ProcessingResourcesTypeDef",
    {
        "ClusterConfig": ProcessingClusterConfigTypeDef,
    },
)

ProcessingOutputTypeDef = TypedDict(
    "ProcessingOutputTypeDef",
    {
        "OutputName": str,
        "S3Output": NotRequired[ProcessingS3OutputTypeDef],
        "FeatureStoreOutput": NotRequired[ProcessingFeatureStoreOutputTypeDef],
        "AppManaged": NotRequired[bool],
    },
)

ProductionVariantTypeDef = TypedDict(
    "ProductionVariantTypeDef",
    {
        "VariantName": str,
        "ModelName": str,
        "InitialInstanceCount": NotRequired[int],
        "InstanceType": NotRequired[ProductionVariantInstanceTypeType],
        "InitialVariantWeight": NotRequired[float],
        "AcceleratorType": NotRequired[ProductionVariantAcceleratorTypeType],
        "CoreDumpConfig": NotRequired[ProductionVariantCoreDumpConfigTypeDef],
        "ServerlessConfig": NotRequired[ProductionVariantServerlessConfigTypeDef],
        "VolumeSizeInGB": NotRequired[int],
        "ModelDataDownloadTimeoutInSeconds": NotRequired[int],
        "ContainerStartupHealthCheckTimeoutInSeconds": NotRequired[int],
        "EnableSSMAccess": NotRequired[bool],
    },
)

SuggestionQueryTypeDef = TypedDict(
    "SuggestionQueryTypeDef",
    {
        "PropertyNameQuery": NotRequired[PropertyNameQueryTypeDef],
    },
)

ServiceCatalogProvisioningDetailsPaginatorTypeDef = TypedDict(
    "ServiceCatalogProvisioningDetailsPaginatorTypeDef",
    {
        "ProductId": str,
        "ProvisioningArtifactId": NotRequired[str],
        "PathId": NotRequired[str],
        "ProvisioningParameters": NotRequired[List[ProvisioningParameterTypeDef]],
    },
)

ServiceCatalogProvisioningDetailsTypeDef = TypedDict(
    "ServiceCatalogProvisioningDetailsTypeDef",
    {
        "ProductId": str,
        "ProvisioningArtifactId": NotRequired[str],
        "PathId": NotRequired[str],
        "ProvisioningParameters": NotRequired[Sequence[ProvisioningParameterTypeDef]],
    },
)

ServiceCatalogProvisioningUpdateDetailsTypeDef = TypedDict(
    "ServiceCatalogProvisioningUpdateDetailsTypeDef",
    {
        "ProvisioningArtifactId": NotRequired[str],
        "ProvisioningParameters": NotRequired[Sequence[ProvisioningParameterTypeDef]],
    },
)

PublicWorkforceTaskPriceTypeDef = TypedDict(
    "PublicWorkforceTaskPriceTypeDef",
    {
        "AmountInUsd": NotRequired[USDTypeDef],
    },
)

QueryLineageResponseTypeDef = TypedDict(
    "QueryLineageResponseTypeDef",
    {
        "Vertices": List[VertexTypeDef],
        "Edges": List[EdgeTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

RecommendationJobOutputConfigTypeDef = TypedDict(
    "RecommendationJobOutputConfigTypeDef",
    {
        "KmsKeyId": NotRequired[str],
        "CompiledOutputConfig": NotRequired[RecommendationJobCompiledOutputConfigTypeDef],
    },
)

RecommendationJobContainerConfigTypeDef = TypedDict(
    "RecommendationJobContainerConfigTypeDef",
    {
        "Domain": NotRequired[str],
        "Task": NotRequired[str],
        "Framework": NotRequired[str],
        "FrameworkVersion": NotRequired[str],
        "PayloadConfig": NotRequired[RecommendationJobPayloadConfigTypeDef],
        "NearestModelName": NotRequired[str],
        "SupportedInstanceTypes": NotRequired[Sequence[str]],
        "DataInputConfig": NotRequired[str],
        "SupportedEndpointType": NotRequired[RecommendationJobSupportedEndpointTypeType],
        "SupportedResponseMIMETypes": NotRequired[Sequence[str]],
    },
)

RenderUiTemplateRequestRequestTypeDef = TypedDict(
    "RenderUiTemplateRequestRequestTypeDef",
    {
        "Task": RenderableTaskTypeDef,
        "RoleArn": str,
        "UiTemplate": NotRequired[UiTemplateTypeDef],
        "HumanTaskUiArn": NotRequired[str],
    },
)

RenderUiTemplateResponseTypeDef = TypedDict(
    "RenderUiTemplateResponseTypeDef",
    {
        "RenderedContent": str,
        "Errors": List[RenderingErrorTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

UpdateTrainingJobRequestRequestTypeDef = TypedDict(
    "UpdateTrainingJobRequestRequestTypeDef",
    {
        "TrainingJobName": str,
        "ProfilerConfig": NotRequired[ProfilerConfigForUpdateTypeDef],
        "ProfilerRuleConfigurations": NotRequired[Sequence[ProfilerRuleConfigurationTypeDef]],
        "ResourceConfig": NotRequired[ResourceConfigForUpdateTypeDef],
    },
)

SelectiveExecutionConfigTypeDef = TypedDict(
    "SelectiveExecutionConfigTypeDef",
    {
        "SourcePipelineExecutionArn": str,
        "SelectedSteps": List[SelectedStepTypeDef],
    },
)

ShadowModeConfigTypeDef = TypedDict(
    "ShadowModeConfigTypeDef",
    {
        "SourceModelVariantName": str,
        "ShadowModelVariants": Sequence[ShadowModelVariantConfigTypeDef],
    },
)

SourceAlgorithmSpecificationPaginatorTypeDef = TypedDict(
    "SourceAlgorithmSpecificationPaginatorTypeDef",
    {
        "SourceAlgorithms": List[SourceAlgorithmTypeDef],
    },
)

SourceAlgorithmSpecificationTypeDef = TypedDict(
    "SourceAlgorithmSpecificationTypeDef",
    {
        "SourceAlgorithms": Sequence[SourceAlgorithmTypeDef],
    },
)

TrafficPatternTypeDef = TypedDict(
    "TrafficPatternTypeDef",
    {
        "TrafficType": NotRequired[TrafficTypeType],
        "Phases": NotRequired[Sequence[PhaseTypeDef]],
        "Stairs": NotRequired[StairsTypeDef],
    },
)

TimeSeriesForecastingJobConfigTypeDef = TypedDict(
    "TimeSeriesForecastingJobConfigTypeDef",
    {
        "ForecastFrequency": str,
        "ForecastHorizon": int,
        "TimeSeriesConfig": TimeSeriesConfigTypeDef,
        "FeatureSpecificationS3Uri": NotRequired[str],
        "CompletionCriteria": NotRequired[AutoMLJobCompletionCriteriaTypeDef],
        "ForecastQuantiles": NotRequired[Sequence[str]],
        "Transformations": NotRequired[TimeSeriesTransformationsTypeDef],
        "HolidayConfig": NotRequired[Sequence[HolidayConfigAttributesTypeDef]],
    },
)

TrainingImageConfigTypeDef = TypedDict(
    "TrainingImageConfigTypeDef",
    {
        "TrainingRepositoryAccessMode": TrainingRepositoryAccessModeType,
        "TrainingRepositoryAuthConfig": NotRequired[TrainingRepositoryAuthConfigTypeDef],
    },
)

TransformDataSourceTypeDef = TypedDict(
    "TransformDataSourceTypeDef",
    {
        "S3DataSource": TransformS3DataSourceTypeDef,
    },
)

WorkforcePaginatorTypeDef = TypedDict(
    "WorkforcePaginatorTypeDef",
    {
        "WorkforceName": str,
        "WorkforceArn": str,
        "LastUpdatedDate": NotRequired[datetime],
        "SourceIpConfig": NotRequired[SourceIpConfigPaginatorTypeDef],
        "SubDomain": NotRequired[str],
        "CognitoConfig": NotRequired[CognitoConfigTypeDef],
        "OidcConfig": NotRequired[OidcConfigForResponseTypeDef],
        "CreateDate": NotRequired[datetime],
        "WorkforceVpcConfig": NotRequired[WorkforceVpcConfigResponseTypeDef],
        "Status": NotRequired[WorkforceStatusType],
        "FailureReason": NotRequired[str],
    },
)

WorkforceTypeDef = TypedDict(
    "WorkforceTypeDef",
    {
        "WorkforceName": str,
        "WorkforceArn": str,
        "LastUpdatedDate": NotRequired[datetime],
        "SourceIpConfig": NotRequired[SourceIpConfigTypeDef],
        "SubDomain": NotRequired[str],
        "CognitoConfig": NotRequired[CognitoConfigTypeDef],
        "OidcConfig": NotRequired[OidcConfigForResponseTypeDef],
        "CreateDate": NotRequired[datetime],
        "WorkforceVpcConfig": NotRequired[WorkforceVpcConfigResponseTypeDef],
        "Status": NotRequired[WorkforceStatusType],
        "FailureReason": NotRequired[str],
    },
)

ListActionsResponseTypeDef = TypedDict(
    "ListActionsResponseTypeDef",
    {
        "ActionSummaries": List[ActionSummaryTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ArtifactSummaryPaginatorTypeDef = TypedDict(
    "ArtifactSummaryPaginatorTypeDef",
    {
        "ArtifactArn": NotRequired[str],
        "ArtifactName": NotRequired[str],
        "Source": NotRequired[ArtifactSourcePaginatorTypeDef],
        "ArtifactType": NotRequired[str],
        "CreationTime": NotRequired[datetime],
        "LastModifiedTime": NotRequired[datetime],
    },
)

ArtifactSummaryTypeDef = TypedDict(
    "ArtifactSummaryTypeDef",
    {
        "ArtifactArn": NotRequired[str],
        "ArtifactName": NotRequired[str],
        "Source": NotRequired[ArtifactSourceTypeDef],
        "ArtifactType": NotRequired[str],
        "CreationTime": NotRequired[datetime],
        "LastModifiedTime": NotRequired[datetime],
    },
)

CreateArtifactRequestRequestTypeDef = TypedDict(
    "CreateArtifactRequestRequestTypeDef",
    {
        "Source": ArtifactSourceTypeDef,
        "ArtifactType": str,
        "ArtifactName": NotRequired[str],
        "Properties": NotRequired[Mapping[str, str]],
        "MetadataProperties": NotRequired[MetadataPropertiesTypeDef],
        "Tags": NotRequired[Sequence[TagTypeDef]],
    },
)

DeleteArtifactRequestRequestTypeDef = TypedDict(
    "DeleteArtifactRequestRequestTypeDef",
    {
        "ArtifactArn": NotRequired[str],
        "Source": NotRequired[ArtifactSourceTypeDef],
    },
)

AsyncInferenceConfigTypeDef = TypedDict(
    "AsyncInferenceConfigTypeDef",
    {
        "OutputConfig": AsyncInferenceOutputConfigTypeDef,
        "ClientConfig": NotRequired[AsyncInferenceClientConfigTypeDef],
    },
)

TabularJobConfigTypeDef = TypedDict(
    "TabularJobConfigTypeDef",
    {
        "TargetAttributeName": str,
        "CandidateGenerationConfig": NotRequired[CandidateGenerationConfigTypeDef],
        "CompletionCriteria": NotRequired[AutoMLJobCompletionCriteriaTypeDef],
        "FeatureSpecificationS3Uri": NotRequired[str],
        "Mode": NotRequired[AutoMLModeType],
        "GenerateCandidateDefinitionsOnly": NotRequired[bool],
        "ProblemType": NotRequired[ProblemTypeType],
        "SampleWeightAttributeName": NotRequired[str],
    },
)

AutoMLChannelTypeDef = TypedDict(
    "AutoMLChannelTypeDef",
    {
        "DataSource": AutoMLDataSourceTypeDef,
        "TargetAttributeName": str,
        "CompressionType": NotRequired[CompressionTypeType],
        "ContentType": NotRequired[str],
        "ChannelType": NotRequired[AutoMLChannelTypeType],
        "SampleWeightAttributeName": NotRequired[str],
    },
)

AutoMLJobChannelTypeDef = TypedDict(
    "AutoMLJobChannelTypeDef",
    {
        "ChannelType": NotRequired[AutoMLChannelTypeType],
        "ContentType": NotRequired[str],
        "CompressionType": NotRequired[CompressionTypeType],
        "DataSource": NotRequired[AutoMLDataSourceTypeDef],
    },
)

ListAutoMLJobsResponseTypeDef = TypedDict(
    "ListAutoMLJobsResponseTypeDef",
    {
        "AutoMLJobSummaries": List[AutoMLJobSummaryTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

AutoMLResolvedAttributesTypeDef = TypedDict(
    "AutoMLResolvedAttributesTypeDef",
    {
        "AutoMLJobObjective": NotRequired[AutoMLJobObjectiveTypeDef],
        "CompletionCriteria": NotRequired[AutoMLJobCompletionCriteriaTypeDef],
        "AutoMLProblemTypeResolvedAttributes": NotRequired[
            AutoMLProblemTypeResolvedAttributesTypeDef
        ],
    },
)

AutoMLJobConfigTypeDef = TypedDict(
    "AutoMLJobConfigTypeDef",
    {
        "CompletionCriteria": NotRequired[AutoMLJobCompletionCriteriaTypeDef],
        "SecurityConfig": NotRequired[AutoMLSecurityConfigTypeDef],
        "DataSplitConfig": NotRequired[AutoMLDataSplitConfigTypeDef],
        "CandidateGenerationConfig": NotRequired[AutoMLCandidateGenerationConfigTypeDef],
        "Mode": NotRequired[AutoMLModeType],
    },
)

LabelingJobAlgorithmsConfigTypeDef = TypedDict(
    "LabelingJobAlgorithmsConfigTypeDef",
    {
        "LabelingJobAlgorithmSpecificationArn": str,
        "InitialActiveLearningModelArn": NotRequired[str],
        "LabelingJobResourceConfig": NotRequired[LabelingJobResourceConfigTypeDef],
    },
)

ModelMetricsTypeDef = TypedDict(
    "ModelMetricsTypeDef",
    {
        "ModelQuality": NotRequired[ModelQualityTypeDef],
        "ModelDataQuality": NotRequired[ModelDataQualityTypeDef],
        "Bias": NotRequired[BiasTypeDef],
        "Explainability": NotRequired[ExplainabilityTypeDef],
    },
)

PipelineExecutionStepMetadataTypeDef = TypedDict(
    "PipelineExecutionStepMetadataTypeDef",
    {
        "TrainingJob": NotRequired[TrainingJobStepMetadataTypeDef],
        "ProcessingJob": NotRequired[ProcessingJobStepMetadataTypeDef],
        "TransformJob": NotRequired[TransformJobStepMetadataTypeDef],
        "TuningJob": NotRequired[TuningJobStepMetaDataTypeDef],
        "Model": NotRequired[ModelStepMetadataTypeDef],
        "RegisterModel": NotRequired[RegisterModelStepMetadataTypeDef],
        "Condition": NotRequired[ConditionStepMetadataTypeDef],
        "Callback": NotRequired[CallbackStepMetadataTypeDef],
        "Lambda": NotRequired[LambdaStepMetadataTypeDef],
        "QualityCheck": NotRequired[QualityCheckStepMetadataTypeDef],
        "ClarifyCheck": NotRequired[ClarifyCheckStepMetadataTypeDef],
        "EMR": NotRequired[EMRStepMetadataTypeDef],
        "Fail": NotRequired[FailStepMetadataTypeDef],
        "AutoMLJob": NotRequired[AutoMLJobStepMetadataTypeDef],
    },
)

AutoMLCandidateTypeDef = TypedDict(
    "AutoMLCandidateTypeDef",
    {
        "CandidateName": str,
        "ObjectiveStatus": ObjectiveStatusType,
        "CandidateSteps": List[AutoMLCandidateStepTypeDef],
        "CandidateStatus": CandidateStatusType,
        "CreationTime": datetime,
        "LastModifiedTime": datetime,
        "FinalAutoMLJobObjectiveMetric": NotRequired[FinalAutoMLJobObjectiveMetricTypeDef],
        "InferenceContainers": NotRequired[List[AutoMLContainerDefinitionTypeDef]],
        "EndTime": NotRequired[datetime],
        "FailureReason": NotRequired[str],
        "CandidateProperties": NotRequired[CandidatePropertiesTypeDef],
        "InferenceContainerDefinitions": NotRequired[
            Dict[AutoMLProcessingUnitType, List[AutoMLContainerDefinitionTypeDef]]
        ],
    },
)

BlueGreenUpdatePolicyTypeDef = TypedDict(
    "BlueGreenUpdatePolicyTypeDef",
    {
        "TrafficRoutingConfiguration": TrafficRoutingConfigTypeDef,
        "TerminationWaitInSeconds": NotRequired[int],
        "MaximumExecutionTimeoutInSeconds": NotRequired[int],
    },
)

EndpointInputConfigurationTypeDef = TypedDict(
    "EndpointInputConfigurationTypeDef",
    {
        "InstanceType": NotRequired[ProductionVariantInstanceTypeType],
        "InferenceSpecificationName": NotRequired[str],
        "EnvironmentParameterRanges": NotRequired[EnvironmentParameterRangesTypeDef],
        "ServerlessConfig": NotRequired[ProductionVariantServerlessConfigTypeDef],
    },
)

ClarifyExplainerConfigTypeDef = TypedDict(
    "ClarifyExplainerConfigTypeDef",
    {
        "ShapConfig": ClarifyShapConfigTypeDef,
        "EnableExplanations": NotRequired[str],
        "InferenceConfig": NotRequired[ClarifyInferenceConfigTypeDef],
    },
)

ListCodeRepositoriesOutputTypeDef = TypedDict(
    "ListCodeRepositoriesOutputTypeDef",
    {
        "CodeRepositorySummaryList": List[CodeRepositorySummaryTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListContextsResponseTypeDef = TypedDict(
    "ListContextsResponseTypeDef",
    {
        "ContextSummaries": List[ContextSummaryTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DomainSettingsForUpdateTypeDef = TypedDict(
    "DomainSettingsForUpdateTypeDef",
    {
        "RStudioServerProDomainSettingsForUpdate": NotRequired[
            RStudioServerProDomainSettingsForUpdateTypeDef
        ],
        "ExecutionRoleIdentityConfig": NotRequired[ExecutionRoleIdentityConfigType],
        "SecurityGroupIds": NotRequired[Sequence[str]],
    },
)

DomainSettingsTypeDef = TypedDict(
    "DomainSettingsTypeDef",
    {
        "SecurityGroupIds": NotRequired[Sequence[str]],
        "RStudioServerProDomainSettings": NotRequired[RStudioServerProDomainSettingsTypeDef],
        "ExecutionRoleIdentityConfig": NotRequired[ExecutionRoleIdentityConfigType],
    },
)

InferenceExperimentSummaryTypeDef = TypedDict(
    "InferenceExperimentSummaryTypeDef",
    {
        "Name": str,
        "Type": Literal["ShadowMode"],
        "Status": InferenceExperimentStatusType,
        "CreationTime": datetime,
        "LastModifiedTime": datetime,
        "Schedule": NotRequired[InferenceExperimentScheduleTypeDef],
        "StatusReason": NotRequired[str],
        "Description": NotRequired[str],
        "CompletionTime": NotRequired[datetime],
        "RoleArn": NotRequired[str],
    },
)

QueryLineageRequestRequestTypeDef = TypedDict(
    "QueryLineageRequestRequestTypeDef",
    {
        "StartArns": NotRequired[Sequence[str]],
        "Direction": NotRequired[DirectionType],
        "IncludeEdges": NotRequired[bool],
        "Filters": NotRequired[QueryFiltersTypeDef],
        "MaxDepth": NotRequired[int],
        "MaxResults": NotRequired[int],
        "NextToken": NotRequired[str],
    },
)

DefaultSpaceSettingsTypeDef = TypedDict(
    "DefaultSpaceSettingsTypeDef",
    {
        "ExecutionRole": NotRequired[str],
        "SecurityGroups": NotRequired[Sequence[str]],
        "JupyterServerAppSettings": NotRequired[JupyterServerAppSettingsTypeDef],
        "KernelGatewayAppSettings": NotRequired[KernelGatewayAppSettingsTypeDef],
    },
)

SpaceSettingsTypeDef = TypedDict(
    "SpaceSettingsTypeDef",
    {
        "JupyterServerAppSettings": NotRequired[JupyterServerAppSettingsTypeDef],
        "KernelGatewayAppSettings": NotRequired[KernelGatewayAppSettingsTypeDef],
    },
)

UserSettingsTypeDef = TypedDict(
    "UserSettingsTypeDef",
    {
        "ExecutionRole": NotRequired[str],
        "SecurityGroups": NotRequired[Sequence[str]],
        "SharingSettings": NotRequired[SharingSettingsTypeDef],
        "JupyterServerAppSettings": NotRequired[JupyterServerAppSettingsTypeDef],
        "KernelGatewayAppSettings": NotRequired[KernelGatewayAppSettingsTypeDef],
        "TensorBoardAppSettings": NotRequired[TensorBoardAppSettingsTypeDef],
        "RStudioServerProAppSettings": NotRequired[RStudioServerProAppSettingsTypeDef],
        "RSessionAppSettings": NotRequired[RSessionAppSettingsTypeDef],
        "CanvasAppSettings": NotRequired[CanvasAppSettingsTypeDef],
    },
)

ChannelPaginatorTypeDef = TypedDict(
    "ChannelPaginatorTypeDef",
    {
        "ChannelName": str,
        "DataSource": DataSourcePaginatorTypeDef,
        "ContentType": NotRequired[str],
        "CompressionType": NotRequired[CompressionTypeType],
        "RecordWrapperType": NotRequired[RecordWrapperType],
        "InputMode": NotRequired[TrainingInputModeType],
        "ShuffleConfig": NotRequired[ShuffleConfigTypeDef],
    },
)

ChannelTypeDef = TypedDict(
    "ChannelTypeDef",
    {
        "ChannelName": str,
        "DataSource": DataSourceTypeDef,
        "ContentType": NotRequired[str],
        "CompressionType": NotRequired[CompressionTypeType],
        "RecordWrapperType": NotRequired[RecordWrapperType],
        "InputMode": NotRequired[TrainingInputModeType],
        "ShuffleConfig": NotRequired[ShuffleConfigTypeDef],
    },
)

ProcessingInputTypeDef = TypedDict(
    "ProcessingInputTypeDef",
    {
        "InputName": str,
        "AppManaged": NotRequired[bool],
        "S3Input": NotRequired[ProcessingS3InputTypeDef],
        "DatasetDefinition": NotRequired[DatasetDefinitionTypeDef],
    },
)

CreateEdgeDeploymentPlanRequestRequestTypeDef = TypedDict(
    "CreateEdgeDeploymentPlanRequestRequestTypeDef",
    {
        "EdgeDeploymentPlanName": str,
        "ModelConfigs": Sequence[EdgeDeploymentModelConfigTypeDef],
        "DeviceFleetName": str,
        "Stages": NotRequired[Sequence[DeploymentStageTypeDef]],
        "Tags": NotRequired[Sequence[TagTypeDef]],
    },
)

CreateEdgeDeploymentStageRequestRequestTypeDef = TypedDict(
    "CreateEdgeDeploymentStageRequestRequestTypeDef",
    {
        "EdgeDeploymentPlanName": str,
        "Stages": Sequence[DeploymentStageTypeDef],
    },
)

DescribeEdgeDeploymentPlanResponseTypeDef = TypedDict(
    "DescribeEdgeDeploymentPlanResponseTypeDef",
    {
        "EdgeDeploymentPlanArn": str,
        "EdgeDeploymentPlanName": str,
        "ModelConfigs": List[EdgeDeploymentModelConfigTypeDef],
        "DeviceFleetName": str,
        "EdgeDeploymentSuccess": int,
        "EdgeDeploymentPending": int,
        "EdgeDeploymentFailed": int,
        "Stages": List[DeploymentStageStatusSummaryTypeDef],
        "NextToken": str,
        "CreationTime": datetime,
        "LastModifiedTime": datetime,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListExperimentsResponseTypeDef = TypedDict(
    "ListExperimentsResponseTypeDef",
    {
        "ExperimentSummaries": List[ExperimentSummaryTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListFeatureGroupsResponseTypeDef = TypedDict(
    "ListFeatureGroupsResponseTypeDef",
    {
        "FeatureGroupSummaries": List[FeatureGroupSummaryTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListTrainingJobsResponseTypeDef = TypedDict(
    "ListTrainingJobsResponseTypeDef",
    {
        "TrainingJobSummaries": List[TrainingJobSummaryTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListTrialsResponseTypeDef = TypedDict(
    "ListTrialsResponseTypeDef",
    {
        "TrialSummaries": List[TrialSummaryTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

UpdateEndpointWeightsAndCapacitiesInputRequestTypeDef = TypedDict(
    "UpdateEndpointWeightsAndCapacitiesInputRequestTypeDef",
    {
        "EndpointName": str,
        "DesiredWeightsAndCapacities": Sequence[DesiredWeightAndCapacityTypeDef],
    },
)

ListDevicesResponseTypeDef = TypedDict(
    "ListDevicesResponseTypeDef",
    {
        "DeviceSummaries": List[DeviceSummaryTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DriftCheckBaselinesTypeDef = TypedDict(
    "DriftCheckBaselinesTypeDef",
    {
        "Bias": NotRequired[DriftCheckBiasTypeDef],
        "Explainability": NotRequired[DriftCheckExplainabilityTypeDef],
        "ModelQuality": NotRequired[DriftCheckModelQualityTypeDef],
        "ModelDataQuality": NotRequired[DriftCheckModelDataQualityTypeDef],
    },
)

InferenceRecommendationTypeDef = TypedDict(
    "InferenceRecommendationTypeDef",
    {
        "Metrics": RecommendationMetricsTypeDef,
        "EndpointConfiguration": EndpointOutputConfigurationTypeDef,
        "ModelConfiguration": ModelConfigurationTypeDef,
        "RecommendationId": NotRequired[str],
        "InvocationEndTime": NotRequired[datetime],
        "InvocationStartTime": NotRequired[datetime],
    },
)

RecommendationJobInferenceBenchmarkTypeDef = TypedDict(
    "RecommendationJobInferenceBenchmarkTypeDef",
    {
        "ModelConfiguration": ModelConfigurationTypeDef,
        "Metrics": NotRequired[RecommendationMetricsTypeDef],
        "EndpointConfiguration": NotRequired[EndpointOutputConfigurationTypeDef],
        "FailureReason": NotRequired[str],
        "EndpointMetrics": NotRequired[InferenceMetricsTypeDef],
        "InvocationEndTime": NotRequired[datetime],
        "InvocationStartTime": NotRequired[datetime],
    },
)

SearchExpressionTypeDef = TypedDict(
    "SearchExpressionTypeDef",
    {
        "Filters": NotRequired[Sequence[FilterTypeDef]],
        "NestedFilters": NotRequired[Sequence[NestedFiltersTypeDef]],
        "SubExpressions": NotRequired[Sequence[Dict[str, Any]]],
        "Operator": NotRequired[BooleanOperatorType],
    },
)

ListTrainingJobsForHyperParameterTuningJobResponseTypeDef = TypedDict(
    "ListTrainingJobsForHyperParameterTuningJobResponseTypeDef",
    {
        "TrainingJobSummaries": List[HyperParameterTrainingJobSummaryTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListHyperParameterTuningJobsResponseTypeDef = TypedDict(
    "ListHyperParameterTuningJobsResponseTypeDef",
    {
        "HyperParameterTuningJobSummaries": List[HyperParameterTuningJobSummaryTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

AssociationSummaryTypeDef = TypedDict(
    "AssociationSummaryTypeDef",
    {
        "SourceArn": NotRequired[str],
        "DestinationArn": NotRequired[str],
        "SourceType": NotRequired[str],
        "DestinationType": NotRequired[str],
        "AssociationType": NotRequired[AssociationEdgeTypeType],
        "SourceName": NotRequired[str],
        "DestinationName": NotRequired[str],
        "CreationTime": NotRequired[datetime],
        "CreatedBy": NotRequired[UserContextTypeDef],
    },
)

DescribeActionResponseTypeDef = TypedDict(
    "DescribeActionResponseTypeDef",
    {
        "ActionName": str,
        "ActionArn": str,
        "Source": ActionSourceTypeDef,
        "ActionType": str,
        "Description": str,
        "Status": ActionStatusType,
        "Properties": Dict[str, str],
        "CreationTime": datetime,
        "CreatedBy": UserContextTypeDef,
        "LastModifiedTime": datetime,
        "LastModifiedBy": UserContextTypeDef,
        "MetadataProperties": MetadataPropertiesTypeDef,
        "LineageGroupArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeArtifactResponseTypeDef = TypedDict(
    "DescribeArtifactResponseTypeDef",
    {
        "ArtifactName": str,
        "ArtifactArn": str,
        "Source": ArtifactSourceTypeDef,
        "ArtifactType": str,
        "Properties": Dict[str, str],
        "CreationTime": datetime,
        "CreatedBy": UserContextTypeDef,
        "LastModifiedTime": datetime,
        "LastModifiedBy": UserContextTypeDef,
        "MetadataProperties": MetadataPropertiesTypeDef,
        "LineageGroupArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeContextResponseTypeDef = TypedDict(
    "DescribeContextResponseTypeDef",
    {
        "ContextName": str,
        "ContextArn": str,
        "Source": ContextSourceTypeDef,
        "ContextType": str,
        "Description": str,
        "Properties": Dict[str, str],
        "CreationTime": datetime,
        "CreatedBy": UserContextTypeDef,
        "LastModifiedTime": datetime,
        "LastModifiedBy": UserContextTypeDef,
        "LineageGroupArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeExperimentResponseTypeDef = TypedDict(
    "DescribeExperimentResponseTypeDef",
    {
        "ExperimentName": str,
        "ExperimentArn": str,
        "DisplayName": str,
        "Source": ExperimentSourceTypeDef,
        "Description": str,
        "CreationTime": datetime,
        "CreatedBy": UserContextTypeDef,
        "LastModifiedTime": datetime,
        "LastModifiedBy": UserContextTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeLineageGroupResponseTypeDef = TypedDict(
    "DescribeLineageGroupResponseTypeDef",
    {
        "LineageGroupName": str,
        "LineageGroupArn": str,
        "DisplayName": str,
        "Description": str,
        "CreationTime": datetime,
        "CreatedBy": UserContextTypeDef,
        "LastModifiedTime": datetime,
        "LastModifiedBy": UserContextTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeModelCardResponseTypeDef = TypedDict(
    "DescribeModelCardResponseTypeDef",
    {
        "ModelCardArn": str,
        "ModelCardName": str,
        "ModelCardVersion": int,
        "Content": str,
        "ModelCardStatus": ModelCardStatusType,
        "SecurityConfig": ModelCardSecurityConfigTypeDef,
        "CreationTime": datetime,
        "CreatedBy": UserContextTypeDef,
        "LastModifiedTime": datetime,
        "LastModifiedBy": UserContextTypeDef,
        "ModelCardProcessingStatus": ModelCardProcessingStatusType,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeModelPackageGroupOutputTypeDef = TypedDict(
    "DescribeModelPackageGroupOutputTypeDef",
    {
        "ModelPackageGroupName": str,
        "ModelPackageGroupArn": str,
        "ModelPackageGroupDescription": str,
        "CreationTime": datetime,
        "CreatedBy": UserContextTypeDef,
        "ModelPackageGroupStatus": ModelPackageGroupStatusType,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribePipelineResponseTypeDef = TypedDict(
    "DescribePipelineResponseTypeDef",
    {
        "PipelineArn": str,
        "PipelineName": str,
        "PipelineDisplayName": str,
        "PipelineDefinition": str,
        "PipelineDescription": str,
        "RoleArn": str,
        "PipelineStatus": Literal["Active"],
        "CreationTime": datetime,
        "LastModifiedTime": datetime,
        "LastRunTime": datetime,
        "CreatedBy": UserContextTypeDef,
        "LastModifiedBy": UserContextTypeDef,
        "ParallelismConfiguration": ParallelismConfigurationTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeTrialComponentResponseTypeDef = TypedDict(
    "DescribeTrialComponentResponseTypeDef",
    {
        "TrialComponentName": str,
        "TrialComponentArn": str,
        "DisplayName": str,
        "Source": TrialComponentSourceTypeDef,
        "Status": TrialComponentStatusTypeDef,
        "StartTime": datetime,
        "EndTime": datetime,
        "CreationTime": datetime,
        "CreatedBy": UserContextTypeDef,
        "LastModifiedTime": datetime,
        "LastModifiedBy": UserContextTypeDef,
        "Parameters": Dict[str, TrialComponentParameterValueTypeDef],
        "InputArtifacts": Dict[str, TrialComponentArtifactTypeDef],
        "OutputArtifacts": Dict[str, TrialComponentArtifactTypeDef],
        "MetadataProperties": MetadataPropertiesTypeDef,
        "Metrics": List[TrialComponentMetricSummaryTypeDef],
        "LineageGroupArn": str,
        "Sources": List[TrialComponentSourceTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeTrialResponseTypeDef = TypedDict(
    "DescribeTrialResponseTypeDef",
    {
        "TrialName": str,
        "TrialArn": str,
        "DisplayName": str,
        "ExperimentName": str,
        "Source": TrialSourceTypeDef,
        "CreationTime": datetime,
        "CreatedBy": UserContextTypeDef,
        "LastModifiedTime": datetime,
        "LastModifiedBy": UserContextTypeDef,
        "MetadataProperties": MetadataPropertiesTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ExperimentTypeDef = TypedDict(
    "ExperimentTypeDef",
    {
        "ExperimentName": NotRequired[str],
        "ExperimentArn": NotRequired[str],
        "DisplayName": NotRequired[str],
        "Source": NotRequired[ExperimentSourceTypeDef],
        "Description": NotRequired[str],
        "CreationTime": NotRequired[datetime],
        "CreatedBy": NotRequired[UserContextTypeDef],
        "LastModifiedTime": NotRequired[datetime],
        "LastModifiedBy": NotRequired[UserContextTypeDef],
        "Tags": NotRequired[List[TagTypeDef]],
    },
)

ModelCardTypeDef = TypedDict(
    "ModelCardTypeDef",
    {
        "ModelCardArn": NotRequired[str],
        "ModelCardName": NotRequired[str],
        "ModelCardVersion": NotRequired[int],
        "Content": NotRequired[str],
        "ModelCardStatus": NotRequired[ModelCardStatusType],
        "SecurityConfig": NotRequired[ModelCardSecurityConfigTypeDef],
        "CreationTime": NotRequired[datetime],
        "CreatedBy": NotRequired[UserContextTypeDef],
        "LastModifiedTime": NotRequired[datetime],
        "LastModifiedBy": NotRequired[UserContextTypeDef],
        "Tags": NotRequired[List[TagTypeDef]],
        "ModelId": NotRequired[str],
        "RiskRating": NotRequired[str],
        "ModelPackageGroupName": NotRequired[str],
    },
)

ModelDashboardModelCardTypeDef = TypedDict(
    "ModelDashboardModelCardTypeDef",
    {
        "ModelCardArn": NotRequired[str],
        "ModelCardName": NotRequired[str],
        "ModelCardVersion": NotRequired[int],
        "ModelCardStatus": NotRequired[ModelCardStatusType],
        "SecurityConfig": NotRequired[ModelCardSecurityConfigTypeDef],
        "CreationTime": NotRequired[datetime],
        "CreatedBy": NotRequired[UserContextTypeDef],
        "LastModifiedTime": NotRequired[datetime],
        "LastModifiedBy": NotRequired[UserContextTypeDef],
        "Tags": NotRequired[List[TagTypeDef]],
        "ModelId": NotRequired[str],
        "RiskRating": NotRequired[str],
    },
)

ModelPackageGroupTypeDef = TypedDict(
    "ModelPackageGroupTypeDef",
    {
        "ModelPackageGroupName": NotRequired[str],
        "ModelPackageGroupArn": NotRequired[str],
        "ModelPackageGroupDescription": NotRequired[str],
        "CreationTime": NotRequired[datetime],
        "CreatedBy": NotRequired[UserContextTypeDef],
        "ModelPackageGroupStatus": NotRequired[ModelPackageGroupStatusType],
        "Tags": NotRequired[List[TagTypeDef]],
    },
)

PipelineTypeDef = TypedDict(
    "PipelineTypeDef",
    {
        "PipelineArn": NotRequired[str],
        "PipelineName": NotRequired[str],
        "PipelineDisplayName": NotRequired[str],
        "PipelineDescription": NotRequired[str],
        "RoleArn": NotRequired[str],
        "PipelineStatus": NotRequired[Literal["Active"]],
        "CreationTime": NotRequired[datetime],
        "LastModifiedTime": NotRequired[datetime],
        "LastRunTime": NotRequired[datetime],
        "CreatedBy": NotRequired[UserContextTypeDef],
        "LastModifiedBy": NotRequired[UserContextTypeDef],
        "ParallelismConfiguration": NotRequired[ParallelismConfigurationTypeDef],
        "Tags": NotRequired[List[TagTypeDef]],
    },
)

TrialComponentSimpleSummaryTypeDef = TypedDict(
    "TrialComponentSimpleSummaryTypeDef",
    {
        "TrialComponentName": NotRequired[str],
        "TrialComponentArn": NotRequired[str],
        "TrialComponentSource": NotRequired[TrialComponentSourceTypeDef],
        "CreationTime": NotRequired[datetime],
        "CreatedBy": NotRequired[UserContextTypeDef],
    },
)

TrialComponentSummaryTypeDef = TypedDict(
    "TrialComponentSummaryTypeDef",
    {
        "TrialComponentName": NotRequired[str],
        "TrialComponentArn": NotRequired[str],
        "DisplayName": NotRequired[str],
        "TrialComponentSource": NotRequired[TrialComponentSourceTypeDef],
        "Status": NotRequired[TrialComponentStatusTypeDef],
        "StartTime": NotRequired[datetime],
        "EndTime": NotRequired[datetime],
        "CreationTime": NotRequired[datetime],
        "CreatedBy": NotRequired[UserContextTypeDef],
        "LastModifiedTime": NotRequired[datetime],
        "LastModifiedBy": NotRequired[UserContextTypeDef],
    },
)

ListInferenceExperimentsResponsePaginatorTypeDef = TypedDict(
    "ListInferenceExperimentsResponsePaginatorTypeDef",
    {
        "InferenceExperiments": List[InferenceExperimentSummaryPaginatorTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

HyperParameterSpecificationTypeDef = TypedDict(
    "HyperParameterSpecificationTypeDef",
    {
        "Name": str,
        "Type": ParameterTypeType,
        "Description": NotRequired[str],
        "Range": NotRequired[ParameterRangeTypeDef],
        "IsTunable": NotRequired[bool],
        "IsRequired": NotRequired[bool],
        "DefaultValue": NotRequired[str],
    },
)

HyperParameterTuningJobConfigPaginatorTypeDef = TypedDict(
    "HyperParameterTuningJobConfigPaginatorTypeDef",
    {
        "Strategy": HyperParameterTuningJobStrategyTypeType,
        "ResourceLimits": ResourceLimitsTypeDef,
        "StrategyConfig": NotRequired[HyperParameterTuningJobStrategyConfigTypeDef],
        "HyperParameterTuningJobObjective": NotRequired[HyperParameterTuningJobObjectiveTypeDef],
        "ParameterRanges": NotRequired[ParameterRangesPaginatorTypeDef],
        "TrainingJobEarlyStoppingType": NotRequired[TrainingJobEarlyStoppingTypeType],
        "TuningJobCompletionCriteria": NotRequired[TuningJobCompletionCriteriaTypeDef],
        "RandomSeed": NotRequired[int],
    },
)

HyperParameterTuningJobConfigTypeDef = TypedDict(
    "HyperParameterTuningJobConfigTypeDef",
    {
        "Strategy": HyperParameterTuningJobStrategyTypeType,
        "ResourceLimits": ResourceLimitsTypeDef,
        "StrategyConfig": NotRequired[HyperParameterTuningJobStrategyConfigTypeDef],
        "HyperParameterTuningJobObjective": NotRequired[HyperParameterTuningJobObjectiveTypeDef],
        "ParameterRanges": NotRequired[ParameterRangesTypeDef],
        "TrainingJobEarlyStoppingType": NotRequired[TrainingJobEarlyStoppingTypeType],
        "TuningJobCompletionCriteria": NotRequired[TuningJobCompletionCriteriaTypeDef],
        "RandomSeed": NotRequired[int],
    },
)

AppImageConfigDetailsPaginatorTypeDef = TypedDict(
    "AppImageConfigDetailsPaginatorTypeDef",
    {
        "AppImageConfigArn": NotRequired[str],
        "AppImageConfigName": NotRequired[str],
        "CreationTime": NotRequired[datetime],
        "LastModifiedTime": NotRequired[datetime],
        "KernelGatewayImageConfig": NotRequired[KernelGatewayImageConfigPaginatorTypeDef],
    },
)

AppImageConfigDetailsTypeDef = TypedDict(
    "AppImageConfigDetailsTypeDef",
    {
        "AppImageConfigArn": NotRequired[str],
        "AppImageConfigName": NotRequired[str],
        "CreationTime": NotRequired[datetime],
        "LastModifiedTime": NotRequired[datetime],
        "KernelGatewayImageConfig": NotRequired[KernelGatewayImageConfigTypeDef],
    },
)

CreateAppImageConfigRequestRequestTypeDef = TypedDict(
    "CreateAppImageConfigRequestRequestTypeDef",
    {
        "AppImageConfigName": str,
        "Tags": NotRequired[Sequence[TagTypeDef]],
        "KernelGatewayImageConfig": NotRequired[KernelGatewayImageConfigTypeDef],
    },
)

DescribeAppImageConfigResponseTypeDef = TypedDict(
    "DescribeAppImageConfigResponseTypeDef",
    {
        "AppImageConfigArn": str,
        "AppImageConfigName": str,
        "CreationTime": datetime,
        "LastModifiedTime": datetime,
        "KernelGatewayImageConfig": KernelGatewayImageConfigTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

UpdateAppImageConfigRequestRequestTypeDef = TypedDict(
    "UpdateAppImageConfigRequestRequestTypeDef",
    {
        "AppImageConfigName": str,
        "KernelGatewayImageConfig": NotRequired[KernelGatewayImageConfigTypeDef],
    },
)

ListLabelingJobsForWorkteamResponseTypeDef = TypedDict(
    "ListLabelingJobsForWorkteamResponseTypeDef",
    {
        "LabelingJobSummaryList": List[LabelingJobForWorkteamSummaryTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

LabelingJobInputConfigPaginatorTypeDef = TypedDict(
    "LabelingJobInputConfigPaginatorTypeDef",
    {
        "DataSource": LabelingJobDataSourceTypeDef,
        "DataAttributes": NotRequired[LabelingJobDataAttributesPaginatorTypeDef],
    },
)

LabelingJobInputConfigTypeDef = TypedDict(
    "LabelingJobInputConfigTypeDef",
    {
        "DataSource": LabelingJobDataSourceTypeDef,
        "DataAttributes": NotRequired[LabelingJobDataAttributesTypeDef],
    },
)

WorkteamPaginatorTypeDef = TypedDict(
    "WorkteamPaginatorTypeDef",
    {
        "WorkteamName": str,
        "MemberDefinitions": List[MemberDefinitionPaginatorTypeDef],
        "WorkteamArn": str,
        "Description": str,
        "WorkforceArn": NotRequired[str],
        "ProductListingIds": NotRequired[List[str]],
        "SubDomain": NotRequired[str],
        "CreateDate": NotRequired[datetime],
        "LastUpdatedDate": NotRequired[datetime],
        "NotificationConfiguration": NotRequired[NotificationConfigurationTypeDef],
    },
)

CreateWorkteamRequestRequestTypeDef = TypedDict(
    "CreateWorkteamRequestRequestTypeDef",
    {
        "WorkteamName": str,
        "MemberDefinitions": Sequence[MemberDefinitionTypeDef],
        "Description": str,
        "WorkforceName": NotRequired[str],
        "NotificationConfiguration": NotRequired[NotificationConfigurationTypeDef],
        "Tags": NotRequired[Sequence[TagTypeDef]],
    },
)

UpdateWorkteamRequestRequestTypeDef = TypedDict(
    "UpdateWorkteamRequestRequestTypeDef",
    {
        "WorkteamName": str,
        "MemberDefinitions": NotRequired[Sequence[MemberDefinitionTypeDef]],
        "Description": NotRequired[str],
        "NotificationConfiguration": NotRequired[NotificationConfigurationTypeDef],
    },
)

WorkteamTypeDef = TypedDict(
    "WorkteamTypeDef",
    {
        "WorkteamName": str,
        "MemberDefinitions": List[MemberDefinitionTypeDef],
        "WorkteamArn": str,
        "Description": str,
        "WorkforceArn": NotRequired[str],
        "ProductListingIds": NotRequired[List[str]],
        "SubDomain": NotRequired[str],
        "CreateDate": NotRequired[datetime],
        "LastUpdatedDate": NotRequired[datetime],
        "NotificationConfiguration": NotRequired[NotificationConfigurationTypeDef],
    },
)

TargetTrackingScalingPolicyConfigurationTypeDef = TypedDict(
    "TargetTrackingScalingPolicyConfigurationTypeDef",
    {
        "MetricSpecification": NotRequired[MetricSpecificationTypeDef],
        "TargetValue": NotRequired[float],
    },
)

MonitoringAlertSummaryTypeDef = TypedDict(
    "MonitoringAlertSummaryTypeDef",
    {
        "MonitoringAlertName": str,
        "CreationTime": datetime,
        "LastModifiedTime": datetime,
        "AlertStatus": MonitoringAlertStatusType,
        "DatapointsToAlert": int,
        "EvaluationPeriod": int,
        "Actions": MonitoringAlertActionsTypeDef,
    },
)

ContainerDefinitionPaginatorTypeDef = TypedDict(
    "ContainerDefinitionPaginatorTypeDef",
    {
        "ContainerHostname": NotRequired[str],
        "Image": NotRequired[str],
        "ImageConfig": NotRequired[ImageConfigTypeDef],
        "Mode": NotRequired[ContainerModeType],
        "ModelDataUrl": NotRequired[str],
        "Environment": NotRequired[Dict[str, str]],
        "ModelPackageName": NotRequired[str],
        "InferenceSpecificationName": NotRequired[str],
        "MultiModelConfig": NotRequired[MultiModelConfigTypeDef],
        "ModelDataSource": NotRequired[ModelDataSourceTypeDef],
    },
)

ContainerDefinitionTypeDef = TypedDict(
    "ContainerDefinitionTypeDef",
    {
        "ContainerHostname": NotRequired[str],
        "Image": NotRequired[str],
        "ImageConfig": NotRequired[ImageConfigTypeDef],
        "Mode": NotRequired[ContainerModeType],
        "ModelDataUrl": NotRequired[str],
        "Environment": NotRequired[Mapping[str, str]],
        "ModelPackageName": NotRequired[str],
        "InferenceSpecificationName": NotRequired[str],
        "MultiModelConfig": NotRequired[MultiModelConfigTypeDef],
        "ModelDataSource": NotRequired[ModelDataSourceTypeDef],
    },
)

ModelVariantConfigSummaryTypeDef = TypedDict(
    "ModelVariantConfigSummaryTypeDef",
    {
        "ModelName": str,
        "VariantName": str,
        "InfrastructureConfig": ModelInfrastructureConfigTypeDef,
        "Status": ModelVariantStatusType,
    },
)

ModelVariantConfigTypeDef = TypedDict(
    "ModelVariantConfigTypeDef",
    {
        "ModelName": str,
        "VariantName": str,
        "InfrastructureConfig": ModelInfrastructureConfigTypeDef,
    },
)

AdditionalInferenceSpecificationDefinitionPaginatorTypeDef = TypedDict(
    "AdditionalInferenceSpecificationDefinitionPaginatorTypeDef",
    {
        "Name": str,
        "Containers": List[ModelPackageContainerDefinitionTypeDef],
        "Description": NotRequired[str],
        "SupportedTransformInstanceTypes": NotRequired[List[TransformInstanceTypeType]],
        "SupportedRealtimeInferenceInstanceTypes": NotRequired[
            List[ProductionVariantInstanceTypeType]
        ],
        "SupportedContentTypes": NotRequired[List[str]],
        "SupportedResponseMIMETypes": NotRequired[List[str]],
    },
)

AdditionalInferenceSpecificationDefinitionTypeDef = TypedDict(
    "AdditionalInferenceSpecificationDefinitionTypeDef",
    {
        "Name": str,
        "Containers": Sequence[ModelPackageContainerDefinitionTypeDef],
        "Description": NotRequired[str],
        "SupportedTransformInstanceTypes": NotRequired[Sequence[TransformInstanceTypeType]],
        "SupportedRealtimeInferenceInstanceTypes": NotRequired[
            Sequence[ProductionVariantInstanceTypeType]
        ],
        "SupportedContentTypes": NotRequired[Sequence[str]],
        "SupportedResponseMIMETypes": NotRequired[Sequence[str]],
    },
)

InferenceSpecificationTypeDef = TypedDict(
    "InferenceSpecificationTypeDef",
    {
        "Containers": List[ModelPackageContainerDefinitionTypeDef],
        "SupportedContentTypes": List[str],
        "SupportedResponseMIMETypes": List[str],
        "SupportedTransformInstanceTypes": NotRequired[List[TransformInstanceTypeType]],
        "SupportedRealtimeInferenceInstanceTypes": NotRequired[
            List[ProductionVariantInstanceTypeType]
        ],
    },
)

ListModelMetadataRequestListModelMetadataPaginateTypeDef = TypedDict(
    "ListModelMetadataRequestListModelMetadataPaginateTypeDef",
    {
        "SearchExpression": NotRequired[ModelMetadataSearchExpressionTypeDef],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)

ListModelMetadataRequestRequestTypeDef = TypedDict(
    "ListModelMetadataRequestRequestTypeDef",
    {
        "SearchExpression": NotRequired[ModelMetadataSearchExpressionTypeDef],
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
    },
)

BatchTransformInputPaginatorTypeDef = TypedDict(
    "BatchTransformInputPaginatorTypeDef",
    {
        "DataCapturedDestinationS3Uri": str,
        "DatasetFormat": MonitoringDatasetFormatPaginatorTypeDef,
        "LocalPath": str,
        "S3InputMode": NotRequired[ProcessingS3InputModeType],
        "S3DataDistributionType": NotRequired[ProcessingS3DataDistributionTypeType],
        "FeaturesAttribute": NotRequired[str],
        "InferenceAttribute": NotRequired[str],
        "ProbabilityAttribute": NotRequired[str],
        "ProbabilityThresholdAttribute": NotRequired[float],
        "StartTimeOffset": NotRequired[str],
        "EndTimeOffset": NotRequired[str],
    },
)

BatchTransformInputTypeDef = TypedDict(
    "BatchTransformInputTypeDef",
    {
        "DataCapturedDestinationS3Uri": str,
        "DatasetFormat": MonitoringDatasetFormatTypeDef,
        "LocalPath": str,
        "S3InputMode": NotRequired[ProcessingS3InputModeType],
        "S3DataDistributionType": NotRequired[ProcessingS3DataDistributionTypeType],
        "FeaturesAttribute": NotRequired[str],
        "InferenceAttribute": NotRequired[str],
        "ProbabilityAttribute": NotRequired[str],
        "ProbabilityThresholdAttribute": NotRequired[float],
        "StartTimeOffset": NotRequired[str],
        "EndTimeOffset": NotRequired[str],
    },
)

MonitoringOutputConfigPaginatorTypeDef = TypedDict(
    "MonitoringOutputConfigPaginatorTypeDef",
    {
        "MonitoringOutputs": List[MonitoringOutputTypeDef],
        "KmsKeyId": NotRequired[str],
    },
)

MonitoringOutputConfigTypeDef = TypedDict(
    "MonitoringOutputConfigTypeDef",
    {
        "MonitoringOutputs": Sequence[MonitoringOutputTypeDef],
        "KmsKeyId": NotRequired[str],
    },
)

CreateFeatureGroupRequestRequestTypeDef = TypedDict(
    "CreateFeatureGroupRequestRequestTypeDef",
    {
        "FeatureGroupName": str,
        "RecordIdentifierFeatureName": str,
        "EventTimeFeatureName": str,
        "FeatureDefinitions": Sequence[FeatureDefinitionTypeDef],
        "OnlineStoreConfig": NotRequired[OnlineStoreConfigTypeDef],
        "OfflineStoreConfig": NotRequired[OfflineStoreConfigTypeDef],
        "RoleArn": NotRequired[str],
        "Description": NotRequired[str],
        "Tags": NotRequired[Sequence[TagTypeDef]],
    },
)

DescribeFeatureGroupResponseTypeDef = TypedDict(
    "DescribeFeatureGroupResponseTypeDef",
    {
        "FeatureGroupArn": str,
        "FeatureGroupName": str,
        "RecordIdentifierFeatureName": str,
        "EventTimeFeatureName": str,
        "FeatureDefinitions": List[FeatureDefinitionTypeDef],
        "CreationTime": datetime,
        "LastModifiedTime": datetime,
        "OnlineStoreConfig": OnlineStoreConfigTypeDef,
        "OfflineStoreConfig": OfflineStoreConfigTypeDef,
        "RoleArn": str,
        "FeatureGroupStatus": FeatureGroupStatusType,
        "OfflineStoreStatus": OfflineStoreStatusTypeDef,
        "LastUpdateStatus": LastUpdateStatusTypeDef,
        "FailureReason": str,
        "Description": str,
        "NextToken": str,
        "OnlineStoreTotalSizeBytes": int,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

FeatureGroupTypeDef = TypedDict(
    "FeatureGroupTypeDef",
    {
        "FeatureGroupArn": NotRequired[str],
        "FeatureGroupName": NotRequired[str],
        "RecordIdentifierFeatureName": NotRequired[str],
        "EventTimeFeatureName": NotRequired[str],
        "FeatureDefinitions": NotRequired[List[FeatureDefinitionTypeDef]],
        "CreationTime": NotRequired[datetime],
        "LastModifiedTime": NotRequired[datetime],
        "OnlineStoreConfig": NotRequired[OnlineStoreConfigTypeDef],
        "OfflineStoreConfig": NotRequired[OfflineStoreConfigTypeDef],
        "RoleArn": NotRequired[str],
        "FeatureGroupStatus": NotRequired[FeatureGroupStatusType],
        "OfflineStoreStatus": NotRequired[OfflineStoreStatusTypeDef],
        "LastUpdateStatus": NotRequired[LastUpdateStatusTypeDef],
        "FailureReason": NotRequired[str],
        "Description": NotRequired[str],
        "Tags": NotRequired[List[TagTypeDef]],
    },
)

UpdateFeatureGroupRequestRequestTypeDef = TypedDict(
    "UpdateFeatureGroupRequestRequestTypeDef",
    {
        "FeatureGroupName": str,
        "FeatureAdditions": NotRequired[Sequence[FeatureDefinitionTypeDef]],
        "OnlineStoreConfig": NotRequired[OnlineStoreConfigUpdateTypeDef],
    },
)

CreateCompilationJobRequestRequestTypeDef = TypedDict(
    "CreateCompilationJobRequestRequestTypeDef",
    {
        "CompilationJobName": str,
        "RoleArn": str,
        "OutputConfig": OutputConfigTypeDef,
        "StoppingCondition": StoppingConditionTypeDef,
        "ModelPackageVersionArn": NotRequired[str],
        "InputConfig": NotRequired[InputConfigTypeDef],
        "VpcConfig": NotRequired[NeoVpcConfigTypeDef],
        "Tags": NotRequired[Sequence[TagTypeDef]],
    },
)

DescribeCompilationJobResponseTypeDef = TypedDict(
    "DescribeCompilationJobResponseTypeDef",
    {
        "CompilationJobName": str,
        "CompilationJobArn": str,
        "CompilationJobStatus": CompilationJobStatusType,
        "CompilationStartTime": datetime,
        "CompilationEndTime": datetime,
        "StoppingCondition": StoppingConditionTypeDef,
        "InferenceImage": str,
        "ModelPackageVersionArn": str,
        "CreationTime": datetime,
        "LastModifiedTime": datetime,
        "FailureReason": str,
        "ModelArtifacts": ModelArtifactsTypeDef,
        "ModelDigests": ModelDigestsTypeDef,
        "RoleArn": str,
        "InputConfig": InputConfigTypeDef,
        "OutputConfig": OutputConfigTypeDef,
        "VpcConfig": NeoVpcConfigTypeDef,
        "DerivedInformation": DerivedInformationTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

PendingDeploymentSummaryTypeDef = TypedDict(
    "PendingDeploymentSummaryTypeDef",
    {
        "EndpointConfigName": str,
        "ProductionVariants": NotRequired[List[PendingProductionVariantSummaryTypeDef]],
        "StartTime": NotRequired[datetime],
        "ShadowProductionVariants": NotRequired[List[PendingProductionVariantSummaryTypeDef]],
    },
)

ProcessingOutputConfigPaginatorTypeDef = TypedDict(
    "ProcessingOutputConfigPaginatorTypeDef",
    {
        "Outputs": List[ProcessingOutputTypeDef],
        "KmsKeyId": NotRequired[str],
    },
)

ProcessingOutputConfigTypeDef = TypedDict(
    "ProcessingOutputConfigTypeDef",
    {
        "Outputs": Sequence[ProcessingOutputTypeDef],
        "KmsKeyId": NotRequired[str],
    },
)

GetSearchSuggestionsRequestRequestTypeDef = TypedDict(
    "GetSearchSuggestionsRequestRequestTypeDef",
    {
        "Resource": ResourceTypeType,
        "SuggestionQuery": NotRequired[SuggestionQueryTypeDef],
    },
)

ProjectPaginatorTypeDef = TypedDict(
    "ProjectPaginatorTypeDef",
    {
        "ProjectArn": NotRequired[str],
        "ProjectName": NotRequired[str],
        "ProjectId": NotRequired[str],
        "ProjectDescription": NotRequired[str],
        "ServiceCatalogProvisioningDetails": NotRequired[
            ServiceCatalogProvisioningDetailsPaginatorTypeDef
        ],
        "ServiceCatalogProvisionedProductDetails": NotRequired[
            ServiceCatalogProvisionedProductDetailsTypeDef
        ],
        "ProjectStatus": NotRequired[ProjectStatusType],
        "CreatedBy": NotRequired[UserContextTypeDef],
        "CreationTime": NotRequired[datetime],
        "Tags": NotRequired[List[TagTypeDef]],
        "LastModifiedTime": NotRequired[datetime],
        "LastModifiedBy": NotRequired[UserContextTypeDef],
    },
)

CreateProjectInputRequestTypeDef = TypedDict(
    "CreateProjectInputRequestTypeDef",
    {
        "ProjectName": str,
        "ServiceCatalogProvisioningDetails": ServiceCatalogProvisioningDetailsTypeDef,
        "ProjectDescription": NotRequired[str],
        "Tags": NotRequired[Sequence[TagTypeDef]],
    },
)

DescribeProjectOutputTypeDef = TypedDict(
    "DescribeProjectOutputTypeDef",
    {
        "ProjectArn": str,
        "ProjectName": str,
        "ProjectId": str,
        "ProjectDescription": str,
        "ServiceCatalogProvisioningDetails": ServiceCatalogProvisioningDetailsTypeDef,
        "ServiceCatalogProvisionedProductDetails": ServiceCatalogProvisionedProductDetailsTypeDef,
        "ProjectStatus": ProjectStatusType,
        "CreatedBy": UserContextTypeDef,
        "CreationTime": datetime,
        "LastModifiedTime": datetime,
        "LastModifiedBy": UserContextTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ProjectTypeDef = TypedDict(
    "ProjectTypeDef",
    {
        "ProjectArn": NotRequired[str],
        "ProjectName": NotRequired[str],
        "ProjectId": NotRequired[str],
        "ProjectDescription": NotRequired[str],
        "ServiceCatalogProvisioningDetails": NotRequired[ServiceCatalogProvisioningDetailsTypeDef],
        "ServiceCatalogProvisionedProductDetails": NotRequired[
            ServiceCatalogProvisionedProductDetailsTypeDef
        ],
        "ProjectStatus": NotRequired[ProjectStatusType],
        "CreatedBy": NotRequired[UserContextTypeDef],
        "CreationTime": NotRequired[datetime],
        "Tags": NotRequired[List[TagTypeDef]],
        "LastModifiedTime": NotRequired[datetime],
        "LastModifiedBy": NotRequired[UserContextTypeDef],
    },
)

UpdateProjectInputRequestTypeDef = TypedDict(
    "UpdateProjectInputRequestTypeDef",
    {
        "ProjectName": str,
        "ProjectDescription": NotRequired[str],
        "ServiceCatalogProvisioningUpdateDetails": NotRequired[
            ServiceCatalogProvisioningUpdateDetailsTypeDef
        ],
        "Tags": NotRequired[Sequence[TagTypeDef]],
    },
)

HumanLoopConfigTypeDef = TypedDict(
    "HumanLoopConfigTypeDef",
    {
        "WorkteamArn": str,
        "HumanTaskUiArn": str,
        "TaskTitle": str,
        "TaskDescription": str,
        "TaskCount": int,
        "TaskAvailabilityLifetimeInSeconds": NotRequired[int],
        "TaskTimeLimitInSeconds": NotRequired[int],
        "TaskKeywords": NotRequired[Sequence[str]],
        "PublicWorkforceTaskPrice": NotRequired[PublicWorkforceTaskPriceTypeDef],
    },
)

HumanTaskConfigTypeDef = TypedDict(
    "HumanTaskConfigTypeDef",
    {
        "WorkteamArn": str,
        "UiConfig": UiConfigTypeDef,
        "PreHumanTaskLambdaArn": str,
        "TaskTitle": str,
        "TaskDescription": str,
        "NumberOfHumanWorkersPerDataObject": int,
        "TaskTimeLimitInSeconds": int,
        "AnnotationConsolidationConfig": AnnotationConsolidationConfigTypeDef,
        "TaskKeywords": NotRequired[Sequence[str]],
        "TaskAvailabilityLifetimeInSeconds": NotRequired[int],
        "MaxConcurrentTaskCount": NotRequired[int],
        "PublicWorkforceTaskPrice": NotRequired[PublicWorkforceTaskPriceTypeDef],
    },
)

DescribePipelineExecutionResponseTypeDef = TypedDict(
    "DescribePipelineExecutionResponseTypeDef",
    {
        "PipelineArn": str,
        "PipelineExecutionArn": str,
        "PipelineExecutionDisplayName": str,
        "PipelineExecutionStatus": PipelineExecutionStatusType,
        "PipelineExecutionDescription": str,
        "PipelineExperimentConfig": PipelineExperimentConfigTypeDef,
        "FailureReason": str,
        "CreationTime": datetime,
        "LastModifiedTime": datetime,
        "CreatedBy": UserContextTypeDef,
        "LastModifiedBy": UserContextTypeDef,
        "ParallelismConfiguration": ParallelismConfigurationTypeDef,
        "SelectiveExecutionConfig": SelectiveExecutionConfigTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

PipelineExecutionTypeDef = TypedDict(
    "PipelineExecutionTypeDef",
    {
        "PipelineArn": NotRequired[str],
        "PipelineExecutionArn": NotRequired[str],
        "PipelineExecutionDisplayName": NotRequired[str],
        "PipelineExecutionStatus": NotRequired[PipelineExecutionStatusType],
        "PipelineExecutionDescription": NotRequired[str],
        "PipelineExperimentConfig": NotRequired[PipelineExperimentConfigTypeDef],
        "FailureReason": NotRequired[str],
        "CreationTime": NotRequired[datetime],
        "LastModifiedTime": NotRequired[datetime],
        "CreatedBy": NotRequired[UserContextTypeDef],
        "LastModifiedBy": NotRequired[UserContextTypeDef],
        "ParallelismConfiguration": NotRequired[ParallelismConfigurationTypeDef],
        "PipelineParameters": NotRequired[List[ParameterTypeDef]],
        "SelectiveExecutionConfig": NotRequired[SelectiveExecutionConfigTypeDef],
    },
)

StartPipelineExecutionRequestRequestTypeDef = TypedDict(
    "StartPipelineExecutionRequestRequestTypeDef",
    {
        "PipelineName": str,
        "ClientRequestToken": str,
        "PipelineExecutionDisplayName": NotRequired[str],
        "PipelineParameters": NotRequired[Sequence[ParameterTypeDef]],
        "PipelineExecutionDescription": NotRequired[str],
        "ParallelismConfiguration": NotRequired[ParallelismConfigurationTypeDef],
        "SelectiveExecutionConfig": NotRequired[SelectiveExecutionConfigTypeDef],
    },
)

AlgorithmSpecificationPaginatorTypeDef = TypedDict(
    "AlgorithmSpecificationPaginatorTypeDef",
    {
        "TrainingInputMode": TrainingInputModeType,
        "TrainingImage": NotRequired[str],
        "AlgorithmName": NotRequired[str],
        "MetricDefinitions": NotRequired[List[MetricDefinitionTypeDef]],
        "EnableSageMakerMetricsTimeSeries": NotRequired[bool],
        "ContainerEntrypoint": NotRequired[List[str]],
        "ContainerArguments": NotRequired[List[str]],
        "TrainingImageConfig": NotRequired[TrainingImageConfigTypeDef],
    },
)

AlgorithmSpecificationTypeDef = TypedDict(
    "AlgorithmSpecificationTypeDef",
    {
        "TrainingInputMode": TrainingInputModeType,
        "TrainingImage": NotRequired[str],
        "AlgorithmName": NotRequired[str],
        "MetricDefinitions": NotRequired[Sequence[MetricDefinitionTypeDef]],
        "EnableSageMakerMetricsTimeSeries": NotRequired[bool],
        "ContainerEntrypoint": NotRequired[Sequence[str]],
        "ContainerArguments": NotRequired[Sequence[str]],
        "TrainingImageConfig": NotRequired[TrainingImageConfigTypeDef],
    },
)

TransformInputTypeDef = TypedDict(
    "TransformInputTypeDef",
    {
        "DataSource": TransformDataSourceTypeDef,
        "ContentType": NotRequired[str],
        "CompressionType": NotRequired[CompressionTypeType],
        "SplitType": NotRequired[SplitTypeType],
    },
)

ListWorkforcesResponsePaginatorTypeDef = TypedDict(
    "ListWorkforcesResponsePaginatorTypeDef",
    {
        "Workforces": List[WorkforcePaginatorTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeWorkforceResponseTypeDef = TypedDict(
    "DescribeWorkforceResponseTypeDef",
    {
        "Workforce": WorkforceTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListWorkforcesResponseTypeDef = TypedDict(
    "ListWorkforcesResponseTypeDef",
    {
        "Workforces": List[WorkforceTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

UpdateWorkforceResponseTypeDef = TypedDict(
    "UpdateWorkforceResponseTypeDef",
    {
        "Workforce": WorkforceTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListArtifactsResponsePaginatorTypeDef = TypedDict(
    "ListArtifactsResponsePaginatorTypeDef",
    {
        "ArtifactSummaries": List[ArtifactSummaryPaginatorTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListArtifactsResponseTypeDef = TypedDict(
    "ListArtifactsResponseTypeDef",
    {
        "ArtifactSummaries": List[ArtifactSummaryTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

AutoMLProblemTypeConfigTypeDef = TypedDict(
    "AutoMLProblemTypeConfigTypeDef",
    {
        "ImageClassificationJobConfig": NotRequired[ImageClassificationJobConfigTypeDef],
        "TextClassificationJobConfig": NotRequired[TextClassificationJobConfigTypeDef],
        "TabularJobConfig": NotRequired[TabularJobConfigTypeDef],
        "TimeSeriesForecastingJobConfig": NotRequired[TimeSeriesForecastingJobConfigTypeDef],
    },
)

CreateAutoMLJobRequestRequestTypeDef = TypedDict(
    "CreateAutoMLJobRequestRequestTypeDef",
    {
        "AutoMLJobName": str,
        "InputDataConfig": Sequence[AutoMLChannelTypeDef],
        "OutputDataConfig": AutoMLOutputDataConfigTypeDef,
        "RoleArn": str,
        "ProblemType": NotRequired[ProblemTypeType],
        "AutoMLJobObjective": NotRequired[AutoMLJobObjectiveTypeDef],
        "AutoMLJobConfig": NotRequired[AutoMLJobConfigTypeDef],
        "GenerateCandidateDefinitionsOnly": NotRequired[bool],
        "Tags": NotRequired[Sequence[TagTypeDef]],
        "ModelDeployConfig": NotRequired[ModelDeployConfigTypeDef],
    },
)

PipelineExecutionStepTypeDef = TypedDict(
    "PipelineExecutionStepTypeDef",
    {
        "StepName": NotRequired[str],
        "StepDisplayName": NotRequired[str],
        "StepDescription": NotRequired[str],
        "StartTime": NotRequired[datetime],
        "EndTime": NotRequired[datetime],
        "StepStatus": NotRequired[StepStatusType],
        "CacheHitResult": NotRequired[CacheHitResultTypeDef],
        "AttemptCount": NotRequired[int],
        "FailureReason": NotRequired[str],
        "Metadata": NotRequired[PipelineExecutionStepMetadataTypeDef],
        "SelectiveExecutionResult": NotRequired[SelectiveExecutionResultTypeDef],
    },
)

DescribeAutoMLJobResponseTypeDef = TypedDict(
    "DescribeAutoMLJobResponseTypeDef",
    {
        "AutoMLJobName": str,
        "AutoMLJobArn": str,
        "InputDataConfig": List[AutoMLChannelTypeDef],
        "OutputDataConfig": AutoMLOutputDataConfigTypeDef,
        "RoleArn": str,
        "AutoMLJobObjective": AutoMLJobObjectiveTypeDef,
        "ProblemType": ProblemTypeType,
        "AutoMLJobConfig": AutoMLJobConfigTypeDef,
        "CreationTime": datetime,
        "EndTime": datetime,
        "LastModifiedTime": datetime,
        "FailureReason": str,
        "PartialFailureReasons": List[AutoMLPartialFailureReasonTypeDef],
        "BestCandidate": AutoMLCandidateTypeDef,
        "AutoMLJobStatus": AutoMLJobStatusType,
        "AutoMLJobSecondaryStatus": AutoMLJobSecondaryStatusType,
        "GenerateCandidateDefinitionsOnly": bool,
        "AutoMLJobArtifacts": AutoMLJobArtifactsTypeDef,
        "ResolvedAttributes": ResolvedAttributesTypeDef,
        "ModelDeployConfig": ModelDeployConfigTypeDef,
        "ModelDeployResult": ModelDeployResultTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListCandidatesForAutoMLJobResponseTypeDef = TypedDict(
    "ListCandidatesForAutoMLJobResponseTypeDef",
    {
        "Candidates": List[AutoMLCandidateTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DeploymentConfigTypeDef = TypedDict(
    "DeploymentConfigTypeDef",
    {
        "BlueGreenUpdatePolicy": NotRequired[BlueGreenUpdatePolicyTypeDef],
        "AutoRollbackConfiguration": NotRequired[AutoRollbackConfigTypeDef],
        "RollingUpdatePolicy": NotRequired[RollingUpdatePolicyTypeDef],
    },
)

RecommendationJobInputConfigTypeDef = TypedDict(
    "RecommendationJobInputConfigTypeDef",
    {
        "ModelPackageVersionArn": NotRequired[str],
        "JobDurationInSeconds": NotRequired[int],
        "TrafficPattern": NotRequired[TrafficPatternTypeDef],
        "ResourceLimit": NotRequired[RecommendationJobResourceLimitTypeDef],
        "EndpointConfigurations": NotRequired[Sequence[EndpointInputConfigurationTypeDef]],
        "VolumeKmsKeyId": NotRequired[str],
        "ContainerConfig": NotRequired[RecommendationJobContainerConfigTypeDef],
        "Endpoints": NotRequired[Sequence[EndpointInfoTypeDef]],
        "VpcConfig": NotRequired[RecommendationJobVpcConfigTypeDef],
        "ModelName": NotRequired[str],
    },
)

ExplainerConfigTypeDef = TypedDict(
    "ExplainerConfigTypeDef",
    {
        "ClarifyExplainerConfig": NotRequired[ClarifyExplainerConfigTypeDef],
    },
)

ListInferenceExperimentsResponseTypeDef = TypedDict(
    "ListInferenceExperimentsResponseTypeDef",
    {
        "InferenceExperiments": List[InferenceExperimentSummaryTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateSpaceRequestRequestTypeDef = TypedDict(
    "CreateSpaceRequestRequestTypeDef",
    {
        "DomainId": str,
        "SpaceName": str,
        "Tags": NotRequired[Sequence[TagTypeDef]],
        "SpaceSettings": NotRequired[SpaceSettingsTypeDef],
    },
)

DescribeSpaceResponseTypeDef = TypedDict(
    "DescribeSpaceResponseTypeDef",
    {
        "DomainId": str,
        "SpaceArn": str,
        "SpaceName": str,
        "HomeEfsFileSystemUid": str,
        "Status": SpaceStatusType,
        "LastModifiedTime": datetime,
        "CreationTime": datetime,
        "FailureReason": str,
        "SpaceSettings": SpaceSettingsTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

UpdateSpaceRequestRequestTypeDef = TypedDict(
    "UpdateSpaceRequestRequestTypeDef",
    {
        "DomainId": str,
        "SpaceName": str,
        "SpaceSettings": NotRequired[SpaceSettingsTypeDef],
    },
)

CreateDomainRequestRequestTypeDef = TypedDict(
    "CreateDomainRequestRequestTypeDef",
    {
        "DomainName": str,
        "AuthMode": AuthModeType,
        "DefaultUserSettings": UserSettingsTypeDef,
        "SubnetIds": Sequence[str],
        "VpcId": str,
        "Tags": NotRequired[Sequence[TagTypeDef]],
        "AppNetworkAccessType": NotRequired[AppNetworkAccessTypeType],
        "HomeEfsFileSystemKmsKeyId": NotRequired[str],
        "KmsKeyId": NotRequired[str],
        "AppSecurityGroupManagement": NotRequired[AppSecurityGroupManagementType],
        "DomainSettings": NotRequired[DomainSettingsTypeDef],
        "DefaultSpaceSettings": NotRequired[DefaultSpaceSettingsTypeDef],
    },
)

CreateUserProfileRequestRequestTypeDef = TypedDict(
    "CreateUserProfileRequestRequestTypeDef",
    {
        "DomainId": str,
        "UserProfileName": str,
        "SingleSignOnUserIdentifier": NotRequired[str],
        "SingleSignOnUserValue": NotRequired[str],
        "Tags": NotRequired[Sequence[TagTypeDef]],
        "UserSettings": NotRequired[UserSettingsTypeDef],
    },
)

DescribeDomainResponseTypeDef = TypedDict(
    "DescribeDomainResponseTypeDef",
    {
        "DomainArn": str,
        "DomainId": str,
        "DomainName": str,
        "HomeEfsFileSystemId": str,
        "SingleSignOnManagedApplicationInstanceId": str,
        "Status": DomainStatusType,
        "CreationTime": datetime,
        "LastModifiedTime": datetime,
        "FailureReason": str,
        "AuthMode": AuthModeType,
        "DefaultUserSettings": UserSettingsTypeDef,
        "AppNetworkAccessType": AppNetworkAccessTypeType,
        "HomeEfsFileSystemKmsKeyId": str,
        "SubnetIds": List[str],
        "Url": str,
        "VpcId": str,
        "KmsKeyId": str,
        "DomainSettings": DomainSettingsTypeDef,
        "AppSecurityGroupManagement": AppSecurityGroupManagementType,
        "SecurityGroupIdForDomainBoundary": str,
        "DefaultSpaceSettings": DefaultSpaceSettingsTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeUserProfileResponseTypeDef = TypedDict(
    "DescribeUserProfileResponseTypeDef",
    {
        "DomainId": str,
        "UserProfileArn": str,
        "UserProfileName": str,
        "HomeEfsFileSystemUid": str,
        "Status": UserProfileStatusType,
        "LastModifiedTime": datetime,
        "CreationTime": datetime,
        "FailureReason": str,
        "SingleSignOnUserIdentifier": str,
        "SingleSignOnUserValue": str,
        "UserSettings": UserSettingsTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

UpdateDomainRequestRequestTypeDef = TypedDict(
    "UpdateDomainRequestRequestTypeDef",
    {
        "DomainId": str,
        "DefaultUserSettings": NotRequired[UserSettingsTypeDef],
        "DomainSettingsForUpdate": NotRequired[DomainSettingsForUpdateTypeDef],
        "DefaultSpaceSettings": NotRequired[DefaultSpaceSettingsTypeDef],
        "AppSecurityGroupManagement": NotRequired[AppSecurityGroupManagementType],
    },
)

UpdateUserProfileRequestRequestTypeDef = TypedDict(
    "UpdateUserProfileRequestRequestTypeDef",
    {
        "DomainId": str,
        "UserProfileName": str,
        "UserSettings": NotRequired[UserSettingsTypeDef],
    },
)

HyperParameterTrainingJobDefinitionPaginatorTypeDef = TypedDict(
    "HyperParameterTrainingJobDefinitionPaginatorTypeDef",
    {
        "AlgorithmSpecification": HyperParameterAlgorithmSpecificationPaginatorTypeDef,
        "RoleArn": str,
        "OutputDataConfig": OutputDataConfigTypeDef,
        "StoppingCondition": StoppingConditionTypeDef,
        "DefinitionName": NotRequired[str],
        "TuningObjective": NotRequired[HyperParameterTuningJobObjectiveTypeDef],
        "HyperParameterRanges": NotRequired[ParameterRangesPaginatorTypeDef],
        "StaticHyperParameters": NotRequired[Dict[str, str]],
        "InputDataConfig": NotRequired[List[ChannelPaginatorTypeDef]],
        "VpcConfig": NotRequired[VpcConfigPaginatorTypeDef],
        "ResourceConfig": NotRequired[ResourceConfigPaginatorTypeDef],
        "EnableNetworkIsolation": NotRequired[bool],
        "EnableInterContainerTrafficEncryption": NotRequired[bool],
        "EnableManagedSpotTraining": NotRequired[bool],
        "CheckpointConfig": NotRequired[CheckpointConfigTypeDef],
        "RetryStrategy": NotRequired[RetryStrategyTypeDef],
        "HyperParameterTuningResourceConfig": NotRequired[
            HyperParameterTuningResourceConfigPaginatorTypeDef
        ],
        "Environment": NotRequired[Dict[str, str]],
    },
)

HyperParameterTrainingJobDefinitionTypeDef = TypedDict(
    "HyperParameterTrainingJobDefinitionTypeDef",
    {
        "AlgorithmSpecification": HyperParameterAlgorithmSpecificationTypeDef,
        "RoleArn": str,
        "OutputDataConfig": OutputDataConfigTypeDef,
        "StoppingCondition": StoppingConditionTypeDef,
        "DefinitionName": NotRequired[str],
        "TuningObjective": NotRequired[HyperParameterTuningJobObjectiveTypeDef],
        "HyperParameterRanges": NotRequired[ParameterRangesTypeDef],
        "StaticHyperParameters": NotRequired[Mapping[str, str]],
        "InputDataConfig": NotRequired[Sequence[ChannelTypeDef]],
        "VpcConfig": NotRequired[VpcConfigTypeDef],
        "ResourceConfig": NotRequired[ResourceConfigTypeDef],
        "EnableNetworkIsolation": NotRequired[bool],
        "EnableInterContainerTrafficEncryption": NotRequired[bool],
        "EnableManagedSpotTraining": NotRequired[bool],
        "CheckpointConfig": NotRequired[CheckpointConfigTypeDef],
        "RetryStrategy": NotRequired[RetryStrategyTypeDef],
        "HyperParameterTuningResourceConfig": NotRequired[
            HyperParameterTuningResourceConfigTypeDef
        ],
        "Environment": NotRequired[Mapping[str, str]],
    },
)

TrainingJobDefinitionTypeDef = TypedDict(
    "TrainingJobDefinitionTypeDef",
    {
        "TrainingInputMode": TrainingInputModeType,
        "InputDataConfig": Sequence[ChannelTypeDef],
        "OutputDataConfig": OutputDataConfigTypeDef,
        "ResourceConfig": ResourceConfigTypeDef,
        "StoppingCondition": StoppingConditionTypeDef,
        "HyperParameters": NotRequired[Mapping[str, str]],
    },
)

InferenceRecommendationsJobStepTypeDef = TypedDict(
    "InferenceRecommendationsJobStepTypeDef",
    {
        "StepType": Literal["BENCHMARK"],
        "JobName": str,
        "Status": RecommendationJobStatusType,
        "InferenceBenchmark": NotRequired[RecommendationJobInferenceBenchmarkTypeDef],
    },
)

SearchRequestSearchPaginateTypeDef = TypedDict(
    "SearchRequestSearchPaginateTypeDef",
    {
        "Resource": ResourceTypeType,
        "SearchExpression": NotRequired[SearchExpressionTypeDef],
        "SortBy": NotRequired[str],
        "SortOrder": NotRequired[SearchSortOrderType],
        "CrossAccountFilterOption": NotRequired[CrossAccountFilterOptionType],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)

ListAssociationsResponseTypeDef = TypedDict(
    "ListAssociationsResponseTypeDef",
    {
        "AssociationSummaries": List[AssociationSummaryTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

TrialTypeDef = TypedDict(
    "TrialTypeDef",
    {
        "TrialName": NotRequired[str],
        "TrialArn": NotRequired[str],
        "DisplayName": NotRequired[str],
        "ExperimentName": NotRequired[str],
        "Source": NotRequired[TrialSourceTypeDef],
        "CreationTime": NotRequired[datetime],
        "CreatedBy": NotRequired[UserContextTypeDef],
        "LastModifiedTime": NotRequired[datetime],
        "LastModifiedBy": NotRequired[UserContextTypeDef],
        "MetadataProperties": NotRequired[MetadataPropertiesTypeDef],
        "Tags": NotRequired[List[TagTypeDef]],
        "TrialComponentSummaries": NotRequired[List[TrialComponentSimpleSummaryTypeDef]],
    },
)

ListTrialComponentsResponseTypeDef = TypedDict(
    "ListTrialComponentsResponseTypeDef",
    {
        "TrialComponentSummaries": List[TrialComponentSummaryTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

TrainingSpecificationTypeDef = TypedDict(
    "TrainingSpecificationTypeDef",
    {
        "TrainingImage": str,
        "SupportedTrainingInstanceTypes": Sequence[TrainingInstanceTypeType],
        "TrainingChannels": Sequence[ChannelSpecificationTypeDef],
        "TrainingImageDigest": NotRequired[str],
        "SupportedHyperParameters": NotRequired[Sequence[HyperParameterSpecificationTypeDef]],
        "SupportsDistributedTraining": NotRequired[bool],
        "MetricDefinitions": NotRequired[Sequence[MetricDefinitionTypeDef]],
        "SupportedTuningJobObjectiveMetrics": NotRequired[
            Sequence[HyperParameterTuningJobObjectiveTypeDef]
        ],
    },
)

ListAppImageConfigsResponsePaginatorTypeDef = TypedDict(
    "ListAppImageConfigsResponsePaginatorTypeDef",
    {
        "NextToken": str,
        "AppImageConfigs": List[AppImageConfigDetailsPaginatorTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListAppImageConfigsResponseTypeDef = TypedDict(
    "ListAppImageConfigsResponseTypeDef",
    {
        "NextToken": str,
        "AppImageConfigs": List[AppImageConfigDetailsTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

LabelingJobSummaryPaginatorTypeDef = TypedDict(
    "LabelingJobSummaryPaginatorTypeDef",
    {
        "LabelingJobName": str,
        "LabelingJobArn": str,
        "CreationTime": datetime,
        "LastModifiedTime": datetime,
        "LabelingJobStatus": LabelingJobStatusType,
        "LabelCounters": LabelCountersTypeDef,
        "WorkteamArn": str,
        "PreHumanTaskLambdaArn": str,
        "AnnotationConsolidationLambdaArn": NotRequired[str],
        "FailureReason": NotRequired[str],
        "LabelingJobOutput": NotRequired[LabelingJobOutputTypeDef],
        "InputConfig": NotRequired[LabelingJobInputConfigPaginatorTypeDef],
    },
)

LabelingJobSummaryTypeDef = TypedDict(
    "LabelingJobSummaryTypeDef",
    {
        "LabelingJobName": str,
        "LabelingJobArn": str,
        "CreationTime": datetime,
        "LastModifiedTime": datetime,
        "LabelingJobStatus": LabelingJobStatusType,
        "LabelCounters": LabelCountersTypeDef,
        "WorkteamArn": str,
        "PreHumanTaskLambdaArn": str,
        "AnnotationConsolidationLambdaArn": NotRequired[str],
        "FailureReason": NotRequired[str],
        "LabelingJobOutput": NotRequired[LabelingJobOutputTypeDef],
        "InputConfig": NotRequired[LabelingJobInputConfigTypeDef],
    },
)

ListWorkteamsResponsePaginatorTypeDef = TypedDict(
    "ListWorkteamsResponsePaginatorTypeDef",
    {
        "Workteams": List[WorkteamPaginatorTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeWorkteamResponseTypeDef = TypedDict(
    "DescribeWorkteamResponseTypeDef",
    {
        "Workteam": WorkteamTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListWorkteamsResponseTypeDef = TypedDict(
    "ListWorkteamsResponseTypeDef",
    {
        "Workteams": List[WorkteamTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

UpdateWorkteamResponseTypeDef = TypedDict(
    "UpdateWorkteamResponseTypeDef",
    {
        "Workteam": WorkteamTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ScalingPolicyTypeDef = TypedDict(
    "ScalingPolicyTypeDef",
    {
        "TargetTracking": NotRequired[TargetTrackingScalingPolicyConfigurationTypeDef],
    },
)

ListMonitoringAlertsResponseTypeDef = TypedDict(
    "ListMonitoringAlertsResponseTypeDef",
    {
        "MonitoringAlertSummaries": List[MonitoringAlertSummaryTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ModelPaginatorTypeDef = TypedDict(
    "ModelPaginatorTypeDef",
    {
        "ModelName": NotRequired[str],
        "PrimaryContainer": NotRequired[ContainerDefinitionPaginatorTypeDef],
        "Containers": NotRequired[List[ContainerDefinitionPaginatorTypeDef]],
        "InferenceExecutionConfig": NotRequired[InferenceExecutionConfigTypeDef],
        "ExecutionRoleArn": NotRequired[str],
        "VpcConfig": NotRequired[VpcConfigPaginatorTypeDef],
        "CreationTime": NotRequired[datetime],
        "ModelArn": NotRequired[str],
        "EnableNetworkIsolation": NotRequired[bool],
        "Tags": NotRequired[List[TagTypeDef]],
        "DeploymentRecommendation": NotRequired[DeploymentRecommendationTypeDef],
    },
)

CreateModelInputRequestTypeDef = TypedDict(
    "CreateModelInputRequestTypeDef",
    {
        "ModelName": str,
        "ExecutionRoleArn": str,
        "PrimaryContainer": NotRequired[ContainerDefinitionTypeDef],
        "Containers": NotRequired[Sequence[ContainerDefinitionTypeDef]],
        "InferenceExecutionConfig": NotRequired[InferenceExecutionConfigTypeDef],
        "Tags": NotRequired[Sequence[TagTypeDef]],
        "VpcConfig": NotRequired[VpcConfigTypeDef],
        "EnableNetworkIsolation": NotRequired[bool],
    },
)

DescribeModelOutputTypeDef = TypedDict(
    "DescribeModelOutputTypeDef",
    {
        "ModelName": str,
        "PrimaryContainer": ContainerDefinitionTypeDef,
        "Containers": List[ContainerDefinitionTypeDef],
        "InferenceExecutionConfig": InferenceExecutionConfigTypeDef,
        "ExecutionRoleArn": str,
        "VpcConfig": VpcConfigTypeDef,
        "CreationTime": datetime,
        "ModelArn": str,
        "EnableNetworkIsolation": bool,
        "DeploymentRecommendation": DeploymentRecommendationTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ModelTypeDef = TypedDict(
    "ModelTypeDef",
    {
        "ModelName": NotRequired[str],
        "PrimaryContainer": NotRequired[ContainerDefinitionTypeDef],
        "Containers": NotRequired[List[ContainerDefinitionTypeDef]],
        "InferenceExecutionConfig": NotRequired[InferenceExecutionConfigTypeDef],
        "ExecutionRoleArn": NotRequired[str],
        "VpcConfig": NotRequired[VpcConfigTypeDef],
        "CreationTime": NotRequired[datetime],
        "ModelArn": NotRequired[str],
        "EnableNetworkIsolation": NotRequired[bool],
        "Tags": NotRequired[List[TagTypeDef]],
        "DeploymentRecommendation": NotRequired[DeploymentRecommendationTypeDef],
    },
)

DescribeInferenceExperimentResponseTypeDef = TypedDict(
    "DescribeInferenceExperimentResponseTypeDef",
    {
        "Arn": str,
        "Name": str,
        "Type": Literal["ShadowMode"],
        "Schedule": InferenceExperimentScheduleTypeDef,
        "Status": InferenceExperimentStatusType,
        "StatusReason": str,
        "Description": str,
        "CreationTime": datetime,
        "CompletionTime": datetime,
        "LastModifiedTime": datetime,
        "RoleArn": str,
        "EndpointMetadata": EndpointMetadataTypeDef,
        "ModelVariants": List[ModelVariantConfigSummaryTypeDef],
        "DataStorageConfig": InferenceExperimentDataStorageConfigTypeDef,
        "ShadowModeConfig": ShadowModeConfigTypeDef,
        "KmsKey": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateInferenceExperimentRequestRequestTypeDef = TypedDict(
    "CreateInferenceExperimentRequestRequestTypeDef",
    {
        "Name": str,
        "Type": Literal["ShadowMode"],
        "RoleArn": str,
        "EndpointName": str,
        "ModelVariants": Sequence[ModelVariantConfigTypeDef],
        "ShadowModeConfig": ShadowModeConfigTypeDef,
        "Schedule": NotRequired[InferenceExperimentScheduleTypeDef],
        "Description": NotRequired[str],
        "DataStorageConfig": NotRequired[InferenceExperimentDataStorageConfigTypeDef],
        "KmsKey": NotRequired[str],
        "Tags": NotRequired[Sequence[TagTypeDef]],
    },
)

StopInferenceExperimentRequestRequestTypeDef = TypedDict(
    "StopInferenceExperimentRequestRequestTypeDef",
    {
        "Name": str,
        "ModelVariantActions": Mapping[str, ModelVariantActionType],
        "DesiredModelVariants": NotRequired[Sequence[ModelVariantConfigTypeDef]],
        "DesiredState": NotRequired[InferenceExperimentStopDesiredStateType],
        "Reason": NotRequired[str],
    },
)

UpdateInferenceExperimentRequestRequestTypeDef = TypedDict(
    "UpdateInferenceExperimentRequestRequestTypeDef",
    {
        "Name": str,
        "Schedule": NotRequired[InferenceExperimentScheduleTypeDef],
        "Description": NotRequired[str],
        "ModelVariants": NotRequired[Sequence[ModelVariantConfigTypeDef]],
        "DataStorageConfig": NotRequired[InferenceExperimentDataStorageConfigTypeDef],
        "ShadowModeConfig": NotRequired[ShadowModeConfigTypeDef],
    },
)

UpdateModelPackageInputRequestTypeDef = TypedDict(
    "UpdateModelPackageInputRequestTypeDef",
    {
        "ModelPackageArn": str,
        "ModelApprovalStatus": NotRequired[ModelApprovalStatusType],
        "ApprovalDescription": NotRequired[str],
        "CustomerMetadataProperties": NotRequired[Mapping[str, str]],
        "CustomerMetadataPropertiesToRemove": NotRequired[Sequence[str]],
        "AdditionalInferenceSpecificationsToAdd": NotRequired[
            Sequence[AdditionalInferenceSpecificationDefinitionTypeDef]
        ],
    },
)

BatchDescribeModelPackageSummaryTypeDef = TypedDict(
    "BatchDescribeModelPackageSummaryTypeDef",
    {
        "ModelPackageGroupName": str,
        "ModelPackageArn": str,
        "CreationTime": datetime,
        "InferenceSpecification": InferenceSpecificationTypeDef,
        "ModelPackageStatus": ModelPackageStatusType,
        "ModelPackageVersion": NotRequired[int],
        "ModelPackageDescription": NotRequired[str],
        "ModelApprovalStatus": NotRequired[ModelApprovalStatusType],
    },
)

MonitoringInputPaginatorTypeDef = TypedDict(
    "MonitoringInputPaginatorTypeDef",
    {
        "EndpointInput": NotRequired[EndpointInputTypeDef],
        "BatchTransformInput": NotRequired[BatchTransformInputPaginatorTypeDef],
    },
)

DataQualityJobInputTypeDef = TypedDict(
    "DataQualityJobInputTypeDef",
    {
        "EndpointInput": NotRequired[EndpointInputTypeDef],
        "BatchTransformInput": NotRequired[BatchTransformInputTypeDef],
    },
)

ModelBiasJobInputTypeDef = TypedDict(
    "ModelBiasJobInputTypeDef",
    {
        "GroundTruthS3Input": MonitoringGroundTruthS3InputTypeDef,
        "EndpointInput": NotRequired[EndpointInputTypeDef],
        "BatchTransformInput": NotRequired[BatchTransformInputTypeDef],
    },
)

ModelExplainabilityJobInputTypeDef = TypedDict(
    "ModelExplainabilityJobInputTypeDef",
    {
        "EndpointInput": NotRequired[EndpointInputTypeDef],
        "BatchTransformInput": NotRequired[BatchTransformInputTypeDef],
    },
)

ModelQualityJobInputTypeDef = TypedDict(
    "ModelQualityJobInputTypeDef",
    {
        "GroundTruthS3Input": MonitoringGroundTruthS3InputTypeDef,
        "EndpointInput": NotRequired[EndpointInputTypeDef],
        "BatchTransformInput": NotRequired[BatchTransformInputTypeDef],
    },
)

MonitoringInputTypeDef = TypedDict(
    "MonitoringInputTypeDef",
    {
        "EndpointInput": NotRequired[EndpointInputTypeDef],
        "BatchTransformInput": NotRequired[BatchTransformInputTypeDef],
    },
)

ProcessingJobPaginatorTypeDef = TypedDict(
    "ProcessingJobPaginatorTypeDef",
    {
        "ProcessingInputs": NotRequired[List[ProcessingInputTypeDef]],
        "ProcessingOutputConfig": NotRequired[ProcessingOutputConfigPaginatorTypeDef],
        "ProcessingJobName": NotRequired[str],
        "ProcessingResources": NotRequired[ProcessingResourcesTypeDef],
        "StoppingCondition": NotRequired[ProcessingStoppingConditionTypeDef],
        "AppSpecification": NotRequired[AppSpecificationPaginatorTypeDef],
        "Environment": NotRequired[Dict[str, str]],
        "NetworkConfig": NotRequired[NetworkConfigPaginatorTypeDef],
        "RoleArn": NotRequired[str],
        "ExperimentConfig": NotRequired[ExperimentConfigTypeDef],
        "ProcessingJobArn": NotRequired[str],
        "ProcessingJobStatus": NotRequired[ProcessingJobStatusType],
        "ExitMessage": NotRequired[str],
        "FailureReason": NotRequired[str],
        "ProcessingEndTime": NotRequired[datetime],
        "ProcessingStartTime": NotRequired[datetime],
        "LastModifiedTime": NotRequired[datetime],
        "CreationTime": NotRequired[datetime],
        "MonitoringScheduleArn": NotRequired[str],
        "AutoMLJobArn": NotRequired[str],
        "TrainingJobArn": NotRequired[str],
        "Tags": NotRequired[List[TagTypeDef]],
    },
)

CreateProcessingJobRequestRequestTypeDef = TypedDict(
    "CreateProcessingJobRequestRequestTypeDef",
    {
        "ProcessingJobName": str,
        "ProcessingResources": ProcessingResourcesTypeDef,
        "AppSpecification": AppSpecificationTypeDef,
        "RoleArn": str,
        "ProcessingInputs": NotRequired[Sequence[ProcessingInputTypeDef]],
        "ProcessingOutputConfig": NotRequired[ProcessingOutputConfigTypeDef],
        "StoppingCondition": NotRequired[ProcessingStoppingConditionTypeDef],
        "Environment": NotRequired[Mapping[str, str]],
        "NetworkConfig": NotRequired[NetworkConfigTypeDef],
        "Tags": NotRequired[Sequence[TagTypeDef]],
        "ExperimentConfig": NotRequired[ExperimentConfigTypeDef],
    },
)

DescribeProcessingJobResponseTypeDef = TypedDict(
    "DescribeProcessingJobResponseTypeDef",
    {
        "ProcessingInputs": List[ProcessingInputTypeDef],
        "ProcessingOutputConfig": ProcessingOutputConfigTypeDef,
        "ProcessingJobName": str,
        "ProcessingResources": ProcessingResourcesTypeDef,
        "StoppingCondition": ProcessingStoppingConditionTypeDef,
        "AppSpecification": AppSpecificationTypeDef,
        "Environment": Dict[str, str],
        "NetworkConfig": NetworkConfigTypeDef,
        "RoleArn": str,
        "ExperimentConfig": ExperimentConfigTypeDef,
        "ProcessingJobArn": str,
        "ProcessingJobStatus": ProcessingJobStatusType,
        "ExitMessage": str,
        "FailureReason": str,
        "ProcessingEndTime": datetime,
        "ProcessingStartTime": datetime,
        "LastModifiedTime": datetime,
        "CreationTime": datetime,
        "MonitoringScheduleArn": str,
        "AutoMLJobArn": str,
        "TrainingJobArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ProcessingJobTypeDef = TypedDict(
    "ProcessingJobTypeDef",
    {
        "ProcessingInputs": NotRequired[List[ProcessingInputTypeDef]],
        "ProcessingOutputConfig": NotRequired[ProcessingOutputConfigTypeDef],
        "ProcessingJobName": NotRequired[str],
        "ProcessingResources": NotRequired[ProcessingResourcesTypeDef],
        "StoppingCondition": NotRequired[ProcessingStoppingConditionTypeDef],
        "AppSpecification": NotRequired[AppSpecificationTypeDef],
        "Environment": NotRequired[Dict[str, str]],
        "NetworkConfig": NotRequired[NetworkConfigTypeDef],
        "RoleArn": NotRequired[str],
        "ExperimentConfig": NotRequired[ExperimentConfigTypeDef],
        "ProcessingJobArn": NotRequired[str],
        "ProcessingJobStatus": NotRequired[ProcessingJobStatusType],
        "ExitMessage": NotRequired[str],
        "FailureReason": NotRequired[str],
        "ProcessingEndTime": NotRequired[datetime],
        "ProcessingStartTime": NotRequired[datetime],
        "LastModifiedTime": NotRequired[datetime],
        "CreationTime": NotRequired[datetime],
        "MonitoringScheduleArn": NotRequired[str],
        "AutoMLJobArn": NotRequired[str],
        "TrainingJobArn": NotRequired[str],
        "Tags": NotRequired[List[TagTypeDef]],
    },
)

CreateFlowDefinitionRequestRequestTypeDef = TypedDict(
    "CreateFlowDefinitionRequestRequestTypeDef",
    {
        "FlowDefinitionName": str,
        "HumanLoopConfig": HumanLoopConfigTypeDef,
        "OutputConfig": FlowDefinitionOutputConfigTypeDef,
        "RoleArn": str,
        "HumanLoopRequestSource": NotRequired[HumanLoopRequestSourceTypeDef],
        "HumanLoopActivationConfig": NotRequired[HumanLoopActivationConfigTypeDef],
        "Tags": NotRequired[Sequence[TagTypeDef]],
    },
)

DescribeFlowDefinitionResponseTypeDef = TypedDict(
    "DescribeFlowDefinitionResponseTypeDef",
    {
        "FlowDefinitionArn": str,
        "FlowDefinitionName": str,
        "FlowDefinitionStatus": FlowDefinitionStatusType,
        "CreationTime": datetime,
        "HumanLoopRequestSource": HumanLoopRequestSourceTypeDef,
        "HumanLoopActivationConfig": HumanLoopActivationConfigTypeDef,
        "HumanLoopConfig": HumanLoopConfigTypeDef,
        "OutputConfig": FlowDefinitionOutputConfigTypeDef,
        "RoleArn": str,
        "FailureReason": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateLabelingJobRequestRequestTypeDef = TypedDict(
    "CreateLabelingJobRequestRequestTypeDef",
    {
        "LabelingJobName": str,
        "LabelAttributeName": str,
        "InputConfig": LabelingJobInputConfigTypeDef,
        "OutputConfig": LabelingJobOutputConfigTypeDef,
        "RoleArn": str,
        "HumanTaskConfig": HumanTaskConfigTypeDef,
        "LabelCategoryConfigS3Uri": NotRequired[str],
        "StoppingConditions": NotRequired[LabelingJobStoppingConditionsTypeDef],
        "LabelingJobAlgorithmsConfig": NotRequired[LabelingJobAlgorithmsConfigTypeDef],
        "Tags": NotRequired[Sequence[TagTypeDef]],
    },
)

DescribeLabelingJobResponseTypeDef = TypedDict(
    "DescribeLabelingJobResponseTypeDef",
    {
        "LabelingJobStatus": LabelingJobStatusType,
        "LabelCounters": LabelCountersTypeDef,
        "FailureReason": str,
        "CreationTime": datetime,
        "LastModifiedTime": datetime,
        "JobReferenceCode": str,
        "LabelingJobName": str,
        "LabelingJobArn": str,
        "LabelAttributeName": str,
        "InputConfig": LabelingJobInputConfigTypeDef,
        "OutputConfig": LabelingJobOutputConfigTypeDef,
        "RoleArn": str,
        "LabelCategoryConfigS3Uri": str,
        "StoppingConditions": LabelingJobStoppingConditionsTypeDef,
        "LabelingJobAlgorithmsConfig": LabelingJobAlgorithmsConfigTypeDef,
        "HumanTaskConfig": HumanTaskConfigTypeDef,
        "Tags": List[TagTypeDef],
        "LabelingJobOutput": LabelingJobOutputTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

TrainingJobPaginatorTypeDef = TypedDict(
    "TrainingJobPaginatorTypeDef",
    {
        "TrainingJobName": NotRequired[str],
        "TrainingJobArn": NotRequired[str],
        "TuningJobArn": NotRequired[str],
        "LabelingJobArn": NotRequired[str],
        "AutoMLJobArn": NotRequired[str],
        "ModelArtifacts": NotRequired[ModelArtifactsTypeDef],
        "TrainingJobStatus": NotRequired[TrainingJobStatusType],
        "SecondaryStatus": NotRequired[SecondaryStatusType],
        "FailureReason": NotRequired[str],
        "HyperParameters": NotRequired[Dict[str, str]],
        "AlgorithmSpecification": NotRequired[AlgorithmSpecificationPaginatorTypeDef],
        "RoleArn": NotRequired[str],
        "InputDataConfig": NotRequired[List[ChannelPaginatorTypeDef]],
        "OutputDataConfig": NotRequired[OutputDataConfigTypeDef],
        "ResourceConfig": NotRequired[ResourceConfigPaginatorTypeDef],
        "VpcConfig": NotRequired[VpcConfigPaginatorTypeDef],
        "StoppingCondition": NotRequired[StoppingConditionTypeDef],
        "CreationTime": NotRequired[datetime],
        "TrainingStartTime": NotRequired[datetime],
        "TrainingEndTime": NotRequired[datetime],
        "LastModifiedTime": NotRequired[datetime],
        "SecondaryStatusTransitions": NotRequired[List[SecondaryStatusTransitionTypeDef]],
        "FinalMetricDataList": NotRequired[List[MetricDataTypeDef]],
        "EnableNetworkIsolation": NotRequired[bool],
        "EnableInterContainerTrafficEncryption": NotRequired[bool],
        "EnableManagedSpotTraining": NotRequired[bool],
        "CheckpointConfig": NotRequired[CheckpointConfigTypeDef],
        "TrainingTimeInSeconds": NotRequired[int],
        "BillableTimeInSeconds": NotRequired[int],
        "DebugHookConfig": NotRequired[DebugHookConfigPaginatorTypeDef],
        "ExperimentConfig": NotRequired[ExperimentConfigTypeDef],
        "DebugRuleConfigurations": NotRequired[List[DebugRuleConfigurationPaginatorTypeDef]],
        "TensorBoardOutputConfig": NotRequired[TensorBoardOutputConfigTypeDef],
        "DebugRuleEvaluationStatuses": NotRequired[List[DebugRuleEvaluationStatusTypeDef]],
        "ProfilerConfig": NotRequired[ProfilerConfigPaginatorTypeDef],
        "Environment": NotRequired[Dict[str, str]],
        "RetryStrategy": NotRequired[RetryStrategyTypeDef],
        "Tags": NotRequired[List[TagTypeDef]],
    },
)

CreateTrainingJobRequestRequestTypeDef = TypedDict(
    "CreateTrainingJobRequestRequestTypeDef",
    {
        "TrainingJobName": str,
        "AlgorithmSpecification": AlgorithmSpecificationTypeDef,
        "RoleArn": str,
        "OutputDataConfig": OutputDataConfigTypeDef,
        "ResourceConfig": ResourceConfigTypeDef,
        "StoppingCondition": StoppingConditionTypeDef,
        "HyperParameters": NotRequired[Mapping[str, str]],
        "InputDataConfig": NotRequired[Sequence[ChannelTypeDef]],
        "VpcConfig": NotRequired[VpcConfigTypeDef],
        "Tags": NotRequired[Sequence[TagTypeDef]],
        "EnableNetworkIsolation": NotRequired[bool],
        "EnableInterContainerTrafficEncryption": NotRequired[bool],
        "EnableManagedSpotTraining": NotRequired[bool],
        "CheckpointConfig": NotRequired[CheckpointConfigTypeDef],
        "DebugHookConfig": NotRequired[DebugHookConfigTypeDef],
        "DebugRuleConfigurations": NotRequired[Sequence[DebugRuleConfigurationTypeDef]],
        "TensorBoardOutputConfig": NotRequired[TensorBoardOutputConfigTypeDef],
        "ExperimentConfig": NotRequired[ExperimentConfigTypeDef],
        "ProfilerConfig": NotRequired[ProfilerConfigTypeDef],
        "ProfilerRuleConfigurations": NotRequired[Sequence[ProfilerRuleConfigurationTypeDef]],
        "Environment": NotRequired[Mapping[str, str]],
        "RetryStrategy": NotRequired[RetryStrategyTypeDef],
    },
)

DescribeTrainingJobResponseTypeDef = TypedDict(
    "DescribeTrainingJobResponseTypeDef",
    {
        "TrainingJobName": str,
        "TrainingJobArn": str,
        "TuningJobArn": str,
        "LabelingJobArn": str,
        "AutoMLJobArn": str,
        "ModelArtifacts": ModelArtifactsTypeDef,
        "TrainingJobStatus": TrainingJobStatusType,
        "SecondaryStatus": SecondaryStatusType,
        "FailureReason": str,
        "HyperParameters": Dict[str, str],
        "AlgorithmSpecification": AlgorithmSpecificationTypeDef,
        "RoleArn": str,
        "InputDataConfig": List[ChannelTypeDef],
        "OutputDataConfig": OutputDataConfigTypeDef,
        "ResourceConfig": ResourceConfigTypeDef,
        "VpcConfig": VpcConfigTypeDef,
        "StoppingCondition": StoppingConditionTypeDef,
        "CreationTime": datetime,
        "TrainingStartTime": datetime,
        "TrainingEndTime": datetime,
        "LastModifiedTime": datetime,
        "SecondaryStatusTransitions": List[SecondaryStatusTransitionTypeDef],
        "FinalMetricDataList": List[MetricDataTypeDef],
        "EnableNetworkIsolation": bool,
        "EnableInterContainerTrafficEncryption": bool,
        "EnableManagedSpotTraining": bool,
        "CheckpointConfig": CheckpointConfigTypeDef,
        "TrainingTimeInSeconds": int,
        "BillableTimeInSeconds": int,
        "DebugHookConfig": DebugHookConfigTypeDef,
        "ExperimentConfig": ExperimentConfigTypeDef,
        "DebugRuleConfigurations": List[DebugRuleConfigurationTypeDef],
        "TensorBoardOutputConfig": TensorBoardOutputConfigTypeDef,
        "DebugRuleEvaluationStatuses": List[DebugRuleEvaluationStatusTypeDef],
        "ProfilerConfig": ProfilerConfigTypeDef,
        "ProfilerRuleConfigurations": List[ProfilerRuleConfigurationTypeDef],
        "ProfilerRuleEvaluationStatuses": List[ProfilerRuleEvaluationStatusTypeDef],
        "ProfilingStatus": ProfilingStatusType,
        "RetryStrategy": RetryStrategyTypeDef,
        "Environment": Dict[str, str],
        "WarmPoolStatus": WarmPoolStatusTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

TrainingJobTypeDef = TypedDict(
    "TrainingJobTypeDef",
    {
        "TrainingJobName": NotRequired[str],
        "TrainingJobArn": NotRequired[str],
        "TuningJobArn": NotRequired[str],
        "LabelingJobArn": NotRequired[str],
        "AutoMLJobArn": NotRequired[str],
        "ModelArtifacts": NotRequired[ModelArtifactsTypeDef],
        "TrainingJobStatus": NotRequired[TrainingJobStatusType],
        "SecondaryStatus": NotRequired[SecondaryStatusType],
        "FailureReason": NotRequired[str],
        "HyperParameters": NotRequired[Dict[str, str]],
        "AlgorithmSpecification": NotRequired[AlgorithmSpecificationTypeDef],
        "RoleArn": NotRequired[str],
        "InputDataConfig": NotRequired[List[ChannelTypeDef]],
        "OutputDataConfig": NotRequired[OutputDataConfigTypeDef],
        "ResourceConfig": NotRequired[ResourceConfigTypeDef],
        "VpcConfig": NotRequired[VpcConfigTypeDef],
        "StoppingCondition": NotRequired[StoppingConditionTypeDef],
        "CreationTime": NotRequired[datetime],
        "TrainingStartTime": NotRequired[datetime],
        "TrainingEndTime": NotRequired[datetime],
        "LastModifiedTime": NotRequired[datetime],
        "SecondaryStatusTransitions": NotRequired[List[SecondaryStatusTransitionTypeDef]],
        "FinalMetricDataList": NotRequired[List[MetricDataTypeDef]],
        "EnableNetworkIsolation": NotRequired[bool],
        "EnableInterContainerTrafficEncryption": NotRequired[bool],
        "EnableManagedSpotTraining": NotRequired[bool],
        "CheckpointConfig": NotRequired[CheckpointConfigTypeDef],
        "TrainingTimeInSeconds": NotRequired[int],
        "BillableTimeInSeconds": NotRequired[int],
        "DebugHookConfig": NotRequired[DebugHookConfigTypeDef],
        "ExperimentConfig": NotRequired[ExperimentConfigTypeDef],
        "DebugRuleConfigurations": NotRequired[List[DebugRuleConfigurationTypeDef]],
        "TensorBoardOutputConfig": NotRequired[TensorBoardOutputConfigTypeDef],
        "DebugRuleEvaluationStatuses": NotRequired[List[DebugRuleEvaluationStatusTypeDef]],
        "ProfilerConfig": NotRequired[ProfilerConfigTypeDef],
        "Environment": NotRequired[Dict[str, str]],
        "RetryStrategy": NotRequired[RetryStrategyTypeDef],
        "Tags": NotRequired[List[TagTypeDef]],
    },
)

CreateTransformJobRequestRequestTypeDef = TypedDict(
    "CreateTransformJobRequestRequestTypeDef",
    {
        "TransformJobName": str,
        "ModelName": str,
        "TransformInput": TransformInputTypeDef,
        "TransformOutput": TransformOutputTypeDef,
        "TransformResources": TransformResourcesTypeDef,
        "MaxConcurrentTransforms": NotRequired[int],
        "ModelClientConfig": NotRequired[ModelClientConfigTypeDef],
        "MaxPayloadInMB": NotRequired[int],
        "BatchStrategy": NotRequired[BatchStrategyType],
        "Environment": NotRequired[Mapping[str, str]],
        "DataCaptureConfig": NotRequired[BatchDataCaptureConfigTypeDef],
        "DataProcessing": NotRequired[DataProcessingTypeDef],
        "Tags": NotRequired[Sequence[TagTypeDef]],
        "ExperimentConfig": NotRequired[ExperimentConfigTypeDef],
    },
)

DescribeTransformJobResponseTypeDef = TypedDict(
    "DescribeTransformJobResponseTypeDef",
    {
        "TransformJobName": str,
        "TransformJobArn": str,
        "TransformJobStatus": TransformJobStatusType,
        "FailureReason": str,
        "ModelName": str,
        "MaxConcurrentTransforms": int,
        "ModelClientConfig": ModelClientConfigTypeDef,
        "MaxPayloadInMB": int,
        "BatchStrategy": BatchStrategyType,
        "Environment": Dict[str, str],
        "TransformInput": TransformInputTypeDef,
        "TransformOutput": TransformOutputTypeDef,
        "DataCaptureConfig": BatchDataCaptureConfigTypeDef,
        "TransformResources": TransformResourcesTypeDef,
        "CreationTime": datetime,
        "TransformStartTime": datetime,
        "TransformEndTime": datetime,
        "LabelingJobArn": str,
        "AutoMLJobArn": str,
        "DataProcessing": DataProcessingTypeDef,
        "ExperimentConfig": ExperimentConfigTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

TransformJobDefinitionPaginatorTypeDef = TypedDict(
    "TransformJobDefinitionPaginatorTypeDef",
    {
        "TransformInput": TransformInputTypeDef,
        "TransformOutput": TransformOutputTypeDef,
        "TransformResources": TransformResourcesTypeDef,
        "MaxConcurrentTransforms": NotRequired[int],
        "MaxPayloadInMB": NotRequired[int],
        "BatchStrategy": NotRequired[BatchStrategyType],
        "Environment": NotRequired[Dict[str, str]],
    },
)

TransformJobDefinitionTypeDef = TypedDict(
    "TransformJobDefinitionTypeDef",
    {
        "TransformInput": TransformInputTypeDef,
        "TransformOutput": TransformOutputTypeDef,
        "TransformResources": TransformResourcesTypeDef,
        "MaxConcurrentTransforms": NotRequired[int],
        "MaxPayloadInMB": NotRequired[int],
        "BatchStrategy": NotRequired[BatchStrategyType],
        "Environment": NotRequired[Mapping[str, str]],
    },
)

TransformJobTypeDef = TypedDict(
    "TransformJobTypeDef",
    {
        "TransformJobName": NotRequired[str],
        "TransformJobArn": NotRequired[str],
        "TransformJobStatus": NotRequired[TransformJobStatusType],
        "FailureReason": NotRequired[str],
        "ModelName": NotRequired[str],
        "MaxConcurrentTransforms": NotRequired[int],
        "ModelClientConfig": NotRequired[ModelClientConfigTypeDef],
        "MaxPayloadInMB": NotRequired[int],
        "BatchStrategy": NotRequired[BatchStrategyType],
        "Environment": NotRequired[Dict[str, str]],
        "TransformInput": NotRequired[TransformInputTypeDef],
        "TransformOutput": NotRequired[TransformOutputTypeDef],
        "TransformResources": NotRequired[TransformResourcesTypeDef],
        "CreationTime": NotRequired[datetime],
        "TransformStartTime": NotRequired[datetime],
        "TransformEndTime": NotRequired[datetime],
        "LabelingJobArn": NotRequired[str],
        "AutoMLJobArn": NotRequired[str],
        "DataProcessing": NotRequired[DataProcessingTypeDef],
        "ExperimentConfig": NotRequired[ExperimentConfigTypeDef],
        "Tags": NotRequired[List[TagTypeDef]],
        "DataCaptureConfig": NotRequired[BatchDataCaptureConfigTypeDef],
    },
)

CreateAutoMLJobV2RequestRequestTypeDef = TypedDict(
    "CreateAutoMLJobV2RequestRequestTypeDef",
    {
        "AutoMLJobName": str,
        "AutoMLJobInputDataConfig": Sequence[AutoMLJobChannelTypeDef],
        "OutputDataConfig": AutoMLOutputDataConfigTypeDef,
        "AutoMLProblemTypeConfig": AutoMLProblemTypeConfigTypeDef,
        "RoleArn": str,
        "Tags": NotRequired[Sequence[TagTypeDef]],
        "SecurityConfig": NotRequired[AutoMLSecurityConfigTypeDef],
        "AutoMLJobObjective": NotRequired[AutoMLJobObjectiveTypeDef],
        "ModelDeployConfig": NotRequired[ModelDeployConfigTypeDef],
        "DataSplitConfig": NotRequired[AutoMLDataSplitConfigTypeDef],
    },
)

DescribeAutoMLJobV2ResponseTypeDef = TypedDict(
    "DescribeAutoMLJobV2ResponseTypeDef",
    {
        "AutoMLJobName": str,
        "AutoMLJobArn": str,
        "AutoMLJobInputDataConfig": List[AutoMLJobChannelTypeDef],
        "OutputDataConfig": AutoMLOutputDataConfigTypeDef,
        "RoleArn": str,
        "AutoMLJobObjective": AutoMLJobObjectiveTypeDef,
        "AutoMLProblemTypeConfig": AutoMLProblemTypeConfigTypeDef,
        "CreationTime": datetime,
        "EndTime": datetime,
        "LastModifiedTime": datetime,
        "FailureReason": str,
        "PartialFailureReasons": List[AutoMLPartialFailureReasonTypeDef],
        "BestCandidate": AutoMLCandidateTypeDef,
        "AutoMLJobStatus": AutoMLJobStatusType,
        "AutoMLJobSecondaryStatus": AutoMLJobSecondaryStatusType,
        "ModelDeployConfig": ModelDeployConfigTypeDef,
        "ModelDeployResult": ModelDeployResultTypeDef,
        "DataSplitConfig": AutoMLDataSplitConfigTypeDef,
        "SecurityConfig": AutoMLSecurityConfigTypeDef,
        "AutoMLJobArtifacts": AutoMLJobArtifactsTypeDef,
        "ResolvedAttributes": AutoMLResolvedAttributesTypeDef,
        "AutoMLProblemTypeConfigName": AutoMLProblemTypeConfigNameType,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListPipelineExecutionStepsResponseTypeDef = TypedDict(
    "ListPipelineExecutionStepsResponseTypeDef",
    {
        "PipelineExecutionSteps": List[PipelineExecutionStepTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateEndpointInputRequestTypeDef = TypedDict(
    "CreateEndpointInputRequestTypeDef",
    {
        "EndpointName": str,
        "EndpointConfigName": str,
        "DeploymentConfig": NotRequired[DeploymentConfigTypeDef],
        "Tags": NotRequired[Sequence[TagTypeDef]],
    },
)

UpdateEndpointInputRequestTypeDef = TypedDict(
    "UpdateEndpointInputRequestTypeDef",
    {
        "EndpointName": str,
        "EndpointConfigName": str,
        "RetainAllVariantProperties": NotRequired[bool],
        "ExcludeRetainedVariantProperties": NotRequired[Sequence[VariantPropertyTypeDef]],
        "DeploymentConfig": NotRequired[DeploymentConfigTypeDef],
        "RetainDeploymentConfig": NotRequired[bool],
    },
)

CreateInferenceRecommendationsJobRequestRequestTypeDef = TypedDict(
    "CreateInferenceRecommendationsJobRequestRequestTypeDef",
    {
        "JobName": str,
        "JobType": RecommendationJobTypeType,
        "RoleArn": str,
        "InputConfig": RecommendationJobInputConfigTypeDef,
        "JobDescription": NotRequired[str],
        "StoppingConditions": NotRequired[RecommendationJobStoppingConditionsTypeDef],
        "OutputConfig": NotRequired[RecommendationJobOutputConfigTypeDef],
        "Tags": NotRequired[Sequence[TagTypeDef]],
    },
)

DescribeInferenceRecommendationsJobResponseTypeDef = TypedDict(
    "DescribeInferenceRecommendationsJobResponseTypeDef",
    {
        "JobName": str,
        "JobDescription": str,
        "JobType": RecommendationJobTypeType,
        "JobArn": str,
        "RoleArn": str,
        "Status": RecommendationJobStatusType,
        "CreationTime": datetime,
        "CompletionTime": datetime,
        "LastModifiedTime": datetime,
        "FailureReason": str,
        "InputConfig": RecommendationJobInputConfigTypeDef,
        "StoppingConditions": RecommendationJobStoppingConditionsTypeDef,
        "InferenceRecommendations": List[InferenceRecommendationTypeDef],
        "EndpointPerformances": List[EndpointPerformanceTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateEndpointConfigInputRequestTypeDef = TypedDict(
    "CreateEndpointConfigInputRequestTypeDef",
    {
        "EndpointConfigName": str,
        "ProductionVariants": Sequence[ProductionVariantTypeDef],
        "DataCaptureConfig": NotRequired[DataCaptureConfigTypeDef],
        "Tags": NotRequired[Sequence[TagTypeDef]],
        "KmsKeyId": NotRequired[str],
        "AsyncInferenceConfig": NotRequired[AsyncInferenceConfigTypeDef],
        "ExplainerConfig": NotRequired[ExplainerConfigTypeDef],
        "ShadowProductionVariants": NotRequired[Sequence[ProductionVariantTypeDef]],
    },
)

DescribeEndpointConfigOutputTypeDef = TypedDict(
    "DescribeEndpointConfigOutputTypeDef",
    {
        "EndpointConfigName": str,
        "EndpointConfigArn": str,
        "ProductionVariants": List[ProductionVariantTypeDef],
        "DataCaptureConfig": DataCaptureConfigTypeDef,
        "KmsKeyId": str,
        "CreationTime": datetime,
        "AsyncInferenceConfig": AsyncInferenceConfigTypeDef,
        "ExplainerConfig": ExplainerConfigTypeDef,
        "ShadowProductionVariants": List[ProductionVariantTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DescribeEndpointOutputTypeDef = TypedDict(
    "DescribeEndpointOutputTypeDef",
    {
        "EndpointName": str,
        "EndpointArn": str,
        "EndpointConfigName": str,
        "ProductionVariants": List[ProductionVariantSummaryTypeDef],
        "DataCaptureConfig": DataCaptureConfigSummaryTypeDef,
        "EndpointStatus": EndpointStatusType,
        "FailureReason": str,
        "CreationTime": datetime,
        "LastModifiedTime": datetime,
        "LastDeploymentConfig": DeploymentConfigTypeDef,
        "AsyncInferenceConfig": AsyncInferenceConfigTypeDef,
        "PendingDeploymentSummary": PendingDeploymentSummaryTypeDef,
        "ExplainerConfig": ExplainerConfigTypeDef,
        "ShadowProductionVariants": List[ProductionVariantSummaryTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

HyperParameterTuningJobSearchEntityPaginatorTypeDef = TypedDict(
    "HyperParameterTuningJobSearchEntityPaginatorTypeDef",
    {
        "HyperParameterTuningJobName": NotRequired[str],
        "HyperParameterTuningJobArn": NotRequired[str],
        "HyperParameterTuningJobConfig": NotRequired[HyperParameterTuningJobConfigPaginatorTypeDef],
        "TrainingJobDefinition": NotRequired[HyperParameterTrainingJobDefinitionPaginatorTypeDef],
        "TrainingJobDefinitions": NotRequired[
            List[HyperParameterTrainingJobDefinitionPaginatorTypeDef]
        ],
        "HyperParameterTuningJobStatus": NotRequired[HyperParameterTuningJobStatusType],
        "CreationTime": NotRequired[datetime],
        "HyperParameterTuningEndTime": NotRequired[datetime],
        "LastModifiedTime": NotRequired[datetime],
        "TrainingJobStatusCounters": NotRequired[TrainingJobStatusCountersTypeDef],
        "ObjectiveStatusCounters": NotRequired[ObjectiveStatusCountersTypeDef],
        "BestTrainingJob": NotRequired[HyperParameterTrainingJobSummaryTypeDef],
        "OverallBestTrainingJob": NotRequired[HyperParameterTrainingJobSummaryTypeDef],
        "WarmStartConfig": NotRequired[HyperParameterTuningJobWarmStartConfigPaginatorTypeDef],
        "FailureReason": NotRequired[str],
        "Tags": NotRequired[List[TagTypeDef]],
        "TuningJobCompletionDetails": NotRequired[HyperParameterTuningJobCompletionDetailsTypeDef],
        "ConsumedResources": NotRequired[HyperParameterTuningJobConsumedResourcesTypeDef],
    },
)

CreateHyperParameterTuningJobRequestRequestTypeDef = TypedDict(
    "CreateHyperParameterTuningJobRequestRequestTypeDef",
    {
        "HyperParameterTuningJobName": str,
        "HyperParameterTuningJobConfig": HyperParameterTuningJobConfigTypeDef,
        "TrainingJobDefinition": NotRequired[HyperParameterTrainingJobDefinitionTypeDef],
        "TrainingJobDefinitions": NotRequired[Sequence[HyperParameterTrainingJobDefinitionTypeDef]],
        "WarmStartConfig": NotRequired[HyperParameterTuningJobWarmStartConfigTypeDef],
        "Tags": NotRequired[Sequence[TagTypeDef]],
        "Autotune": NotRequired[AutotuneTypeDef],
    },
)

DescribeHyperParameterTuningJobResponseTypeDef = TypedDict(
    "DescribeHyperParameterTuningJobResponseTypeDef",
    {
        "HyperParameterTuningJobName": str,
        "HyperParameterTuningJobArn": str,
        "HyperParameterTuningJobConfig": HyperParameterTuningJobConfigTypeDef,
        "TrainingJobDefinition": HyperParameterTrainingJobDefinitionTypeDef,
        "TrainingJobDefinitions": List[HyperParameterTrainingJobDefinitionTypeDef],
        "HyperParameterTuningJobStatus": HyperParameterTuningJobStatusType,
        "CreationTime": datetime,
        "HyperParameterTuningEndTime": datetime,
        "LastModifiedTime": datetime,
        "TrainingJobStatusCounters": TrainingJobStatusCountersTypeDef,
        "ObjectiveStatusCounters": ObjectiveStatusCountersTypeDef,
        "BestTrainingJob": HyperParameterTrainingJobSummaryTypeDef,
        "OverallBestTrainingJob": HyperParameterTrainingJobSummaryTypeDef,
        "WarmStartConfig": HyperParameterTuningJobWarmStartConfigTypeDef,
        "FailureReason": str,
        "TuningJobCompletionDetails": HyperParameterTuningJobCompletionDetailsTypeDef,
        "ConsumedResources": HyperParameterTuningJobConsumedResourcesTypeDef,
        "Autotune": AutotuneTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

HyperParameterTuningJobSearchEntityTypeDef = TypedDict(
    "HyperParameterTuningJobSearchEntityTypeDef",
    {
        "HyperParameterTuningJobName": NotRequired[str],
        "HyperParameterTuningJobArn": NotRequired[str],
        "HyperParameterTuningJobConfig": NotRequired[HyperParameterTuningJobConfigTypeDef],
        "TrainingJobDefinition": NotRequired[HyperParameterTrainingJobDefinitionTypeDef],
        "TrainingJobDefinitions": NotRequired[List[HyperParameterTrainingJobDefinitionTypeDef]],
        "HyperParameterTuningJobStatus": NotRequired[HyperParameterTuningJobStatusType],
        "CreationTime": NotRequired[datetime],
        "HyperParameterTuningEndTime": NotRequired[datetime],
        "LastModifiedTime": NotRequired[datetime],
        "TrainingJobStatusCounters": NotRequired[TrainingJobStatusCountersTypeDef],
        "ObjectiveStatusCounters": NotRequired[ObjectiveStatusCountersTypeDef],
        "BestTrainingJob": NotRequired[HyperParameterTrainingJobSummaryTypeDef],
        "OverallBestTrainingJob": NotRequired[HyperParameterTrainingJobSummaryTypeDef],
        "WarmStartConfig": NotRequired[HyperParameterTuningJobWarmStartConfigTypeDef],
        "FailureReason": NotRequired[str],
        "Tags": NotRequired[List[TagTypeDef]],
        "TuningJobCompletionDetails": NotRequired[HyperParameterTuningJobCompletionDetailsTypeDef],
        "ConsumedResources": NotRequired[HyperParameterTuningJobConsumedResourcesTypeDef],
    },
)

ListInferenceRecommendationsJobStepsResponseTypeDef = TypedDict(
    "ListInferenceRecommendationsJobStepsResponseTypeDef",
    {
        "Steps": List[InferenceRecommendationsJobStepTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListLabelingJobsResponsePaginatorTypeDef = TypedDict(
    "ListLabelingJobsResponsePaginatorTypeDef",
    {
        "LabelingJobSummaryList": List[LabelingJobSummaryPaginatorTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ListLabelingJobsResponseTypeDef = TypedDict(
    "ListLabelingJobsResponseTypeDef",
    {
        "LabelingJobSummaryList": List[LabelingJobSummaryTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

DynamicScalingConfigurationTypeDef = TypedDict(
    "DynamicScalingConfigurationTypeDef",
    {
        "MinCapacity": NotRequired[int],
        "MaxCapacity": NotRequired[int],
        "ScaleInCooldown": NotRequired[int],
        "ScaleOutCooldown": NotRequired[int],
        "ScalingPolicies": NotRequired[List[ScalingPolicyTypeDef]],
    },
)

BatchDescribeModelPackageOutputTypeDef = TypedDict(
    "BatchDescribeModelPackageOutputTypeDef",
    {
        "ModelPackageSummaries": Dict[str, BatchDescribeModelPackageSummaryTypeDef],
        "BatchDescribeModelPackageErrorMap": Dict[str, BatchDescribeModelPackageErrorTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

MonitoringJobDefinitionPaginatorTypeDef = TypedDict(
    "MonitoringJobDefinitionPaginatorTypeDef",
    {
        "MonitoringInputs": List[MonitoringInputPaginatorTypeDef],
        "MonitoringOutputConfig": MonitoringOutputConfigPaginatorTypeDef,
        "MonitoringResources": MonitoringResourcesTypeDef,
        "MonitoringAppSpecification": MonitoringAppSpecificationPaginatorTypeDef,
        "RoleArn": str,
        "BaselineConfig": NotRequired[MonitoringBaselineConfigTypeDef],
        "StoppingCondition": NotRequired[MonitoringStoppingConditionTypeDef],
        "Environment": NotRequired[Dict[str, str]],
        "NetworkConfig": NotRequired[NetworkConfigPaginatorTypeDef],
    },
)

CreateDataQualityJobDefinitionRequestRequestTypeDef = TypedDict(
    "CreateDataQualityJobDefinitionRequestRequestTypeDef",
    {
        "JobDefinitionName": str,
        "DataQualityAppSpecification": DataQualityAppSpecificationTypeDef,
        "DataQualityJobInput": DataQualityJobInputTypeDef,
        "DataQualityJobOutputConfig": MonitoringOutputConfigTypeDef,
        "JobResources": MonitoringResourcesTypeDef,
        "RoleArn": str,
        "DataQualityBaselineConfig": NotRequired[DataQualityBaselineConfigTypeDef],
        "NetworkConfig": NotRequired[MonitoringNetworkConfigTypeDef],
        "StoppingCondition": NotRequired[MonitoringStoppingConditionTypeDef],
        "Tags": NotRequired[Sequence[TagTypeDef]],
    },
)

DescribeDataQualityJobDefinitionResponseTypeDef = TypedDict(
    "DescribeDataQualityJobDefinitionResponseTypeDef",
    {
        "JobDefinitionArn": str,
        "JobDefinitionName": str,
        "CreationTime": datetime,
        "DataQualityBaselineConfig": DataQualityBaselineConfigTypeDef,
        "DataQualityAppSpecification": DataQualityAppSpecificationTypeDef,
        "DataQualityJobInput": DataQualityJobInputTypeDef,
        "DataQualityJobOutputConfig": MonitoringOutputConfigTypeDef,
        "JobResources": MonitoringResourcesTypeDef,
        "NetworkConfig": MonitoringNetworkConfigTypeDef,
        "RoleArn": str,
        "StoppingCondition": MonitoringStoppingConditionTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateModelBiasJobDefinitionRequestRequestTypeDef = TypedDict(
    "CreateModelBiasJobDefinitionRequestRequestTypeDef",
    {
        "JobDefinitionName": str,
        "ModelBiasAppSpecification": ModelBiasAppSpecificationTypeDef,
        "ModelBiasJobInput": ModelBiasJobInputTypeDef,
        "ModelBiasJobOutputConfig": MonitoringOutputConfigTypeDef,
        "JobResources": MonitoringResourcesTypeDef,
        "RoleArn": str,
        "ModelBiasBaselineConfig": NotRequired[ModelBiasBaselineConfigTypeDef],
        "NetworkConfig": NotRequired[MonitoringNetworkConfigTypeDef],
        "StoppingCondition": NotRequired[MonitoringStoppingConditionTypeDef],
        "Tags": NotRequired[Sequence[TagTypeDef]],
    },
)

DescribeModelBiasJobDefinitionResponseTypeDef = TypedDict(
    "DescribeModelBiasJobDefinitionResponseTypeDef",
    {
        "JobDefinitionArn": str,
        "JobDefinitionName": str,
        "CreationTime": datetime,
        "ModelBiasBaselineConfig": ModelBiasBaselineConfigTypeDef,
        "ModelBiasAppSpecification": ModelBiasAppSpecificationTypeDef,
        "ModelBiasJobInput": ModelBiasJobInputTypeDef,
        "ModelBiasJobOutputConfig": MonitoringOutputConfigTypeDef,
        "JobResources": MonitoringResourcesTypeDef,
        "NetworkConfig": MonitoringNetworkConfigTypeDef,
        "RoleArn": str,
        "StoppingCondition": MonitoringStoppingConditionTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateModelExplainabilityJobDefinitionRequestRequestTypeDef = TypedDict(
    "CreateModelExplainabilityJobDefinitionRequestRequestTypeDef",
    {
        "JobDefinitionName": str,
        "ModelExplainabilityAppSpecification": ModelExplainabilityAppSpecificationTypeDef,
        "ModelExplainabilityJobInput": ModelExplainabilityJobInputTypeDef,
        "ModelExplainabilityJobOutputConfig": MonitoringOutputConfigTypeDef,
        "JobResources": MonitoringResourcesTypeDef,
        "RoleArn": str,
        "ModelExplainabilityBaselineConfig": NotRequired[ModelExplainabilityBaselineConfigTypeDef],
        "NetworkConfig": NotRequired[MonitoringNetworkConfigTypeDef],
        "StoppingCondition": NotRequired[MonitoringStoppingConditionTypeDef],
        "Tags": NotRequired[Sequence[TagTypeDef]],
    },
)

DescribeModelExplainabilityJobDefinitionResponseTypeDef = TypedDict(
    "DescribeModelExplainabilityJobDefinitionResponseTypeDef",
    {
        "JobDefinitionArn": str,
        "JobDefinitionName": str,
        "CreationTime": datetime,
        "ModelExplainabilityBaselineConfig": ModelExplainabilityBaselineConfigTypeDef,
        "ModelExplainabilityAppSpecification": ModelExplainabilityAppSpecificationTypeDef,
        "ModelExplainabilityJobInput": ModelExplainabilityJobInputTypeDef,
        "ModelExplainabilityJobOutputConfig": MonitoringOutputConfigTypeDef,
        "JobResources": MonitoringResourcesTypeDef,
        "NetworkConfig": MonitoringNetworkConfigTypeDef,
        "RoleArn": str,
        "StoppingCondition": MonitoringStoppingConditionTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateModelQualityJobDefinitionRequestRequestTypeDef = TypedDict(
    "CreateModelQualityJobDefinitionRequestRequestTypeDef",
    {
        "JobDefinitionName": str,
        "ModelQualityAppSpecification": ModelQualityAppSpecificationTypeDef,
        "ModelQualityJobInput": ModelQualityJobInputTypeDef,
        "ModelQualityJobOutputConfig": MonitoringOutputConfigTypeDef,
        "JobResources": MonitoringResourcesTypeDef,
        "RoleArn": str,
        "ModelQualityBaselineConfig": NotRequired[ModelQualityBaselineConfigTypeDef],
        "NetworkConfig": NotRequired[MonitoringNetworkConfigTypeDef],
        "StoppingCondition": NotRequired[MonitoringStoppingConditionTypeDef],
        "Tags": NotRequired[Sequence[TagTypeDef]],
    },
)

DescribeModelQualityJobDefinitionResponseTypeDef = TypedDict(
    "DescribeModelQualityJobDefinitionResponseTypeDef",
    {
        "JobDefinitionArn": str,
        "JobDefinitionName": str,
        "CreationTime": datetime,
        "ModelQualityBaselineConfig": ModelQualityBaselineConfigTypeDef,
        "ModelQualityAppSpecification": ModelQualityAppSpecificationTypeDef,
        "ModelQualityJobInput": ModelQualityJobInputTypeDef,
        "ModelQualityJobOutputConfig": MonitoringOutputConfigTypeDef,
        "JobResources": MonitoringResourcesTypeDef,
        "NetworkConfig": MonitoringNetworkConfigTypeDef,
        "RoleArn": str,
        "StoppingCondition": MonitoringStoppingConditionTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

MonitoringJobDefinitionTypeDef = TypedDict(
    "MonitoringJobDefinitionTypeDef",
    {
        "MonitoringInputs": Sequence[MonitoringInputTypeDef],
        "MonitoringOutputConfig": MonitoringOutputConfigTypeDef,
        "MonitoringResources": MonitoringResourcesTypeDef,
        "MonitoringAppSpecification": MonitoringAppSpecificationTypeDef,
        "RoleArn": str,
        "BaselineConfig": NotRequired[MonitoringBaselineConfigTypeDef],
        "StoppingCondition": NotRequired[MonitoringStoppingConditionTypeDef],
        "Environment": NotRequired[Mapping[str, str]],
        "NetworkConfig": NotRequired[NetworkConfigTypeDef],
    },
)

ModelPackageValidationProfilePaginatorTypeDef = TypedDict(
    "ModelPackageValidationProfilePaginatorTypeDef",
    {
        "ProfileName": str,
        "TransformJobDefinition": TransformJobDefinitionPaginatorTypeDef,
    },
)

AlgorithmValidationProfileTypeDef = TypedDict(
    "AlgorithmValidationProfileTypeDef",
    {
        "ProfileName": str,
        "TrainingJobDefinition": TrainingJobDefinitionTypeDef,
        "TransformJobDefinition": NotRequired[TransformJobDefinitionTypeDef],
    },
)

ModelPackageValidationProfileTypeDef = TypedDict(
    "ModelPackageValidationProfileTypeDef",
    {
        "ProfileName": str,
        "TransformJobDefinition": TransformJobDefinitionTypeDef,
    },
)

TrialComponentSourceDetailPaginatorTypeDef = TypedDict(
    "TrialComponentSourceDetailPaginatorTypeDef",
    {
        "SourceArn": NotRequired[str],
        "TrainingJob": NotRequired[TrainingJobPaginatorTypeDef],
        "ProcessingJob": NotRequired[ProcessingJobPaginatorTypeDef],
        "TransformJob": NotRequired[TransformJobTypeDef],
    },
)

TrialComponentSourceDetailTypeDef = TypedDict(
    "TrialComponentSourceDetailTypeDef",
    {
        "SourceArn": NotRequired[str],
        "TrainingJob": NotRequired[TrainingJobTypeDef],
        "ProcessingJob": NotRequired[ProcessingJobTypeDef],
        "TransformJob": NotRequired[TransformJobTypeDef],
    },
)

GetScalingConfigurationRecommendationResponseTypeDef = TypedDict(
    "GetScalingConfigurationRecommendationResponseTypeDef",
    {
        "InferenceRecommendationsJobName": str,
        "RecommendationId": str,
        "EndpointName": str,
        "TargetCpuUtilizationPerCore": int,
        "ScalingPolicyObjective": ScalingPolicyObjectiveTypeDef,
        "Metric": ScalingPolicyMetricTypeDef,
        "DynamicScalingConfiguration": DynamicScalingConfigurationTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

MonitoringScheduleConfigPaginatorTypeDef = TypedDict(
    "MonitoringScheduleConfigPaginatorTypeDef",
    {
        "ScheduleConfig": NotRequired[ScheduleConfigTypeDef],
        "MonitoringJobDefinition": NotRequired[MonitoringJobDefinitionPaginatorTypeDef],
        "MonitoringJobDefinitionName": NotRequired[str],
        "MonitoringType": NotRequired[MonitoringTypeType],
    },
)

MonitoringScheduleConfigTypeDef = TypedDict(
    "MonitoringScheduleConfigTypeDef",
    {
        "ScheduleConfig": NotRequired[ScheduleConfigTypeDef],
        "MonitoringJobDefinition": NotRequired[MonitoringJobDefinitionTypeDef],
        "MonitoringJobDefinitionName": NotRequired[str],
        "MonitoringType": NotRequired[MonitoringTypeType],
    },
)

ModelPackageValidationSpecificationPaginatorTypeDef = TypedDict(
    "ModelPackageValidationSpecificationPaginatorTypeDef",
    {
        "ValidationRole": str,
        "ValidationProfiles": List[ModelPackageValidationProfilePaginatorTypeDef],
    },
)

AlgorithmValidationSpecificationTypeDef = TypedDict(
    "AlgorithmValidationSpecificationTypeDef",
    {
        "ValidationRole": str,
        "ValidationProfiles": Sequence[AlgorithmValidationProfileTypeDef],
    },
)

ModelPackageValidationSpecificationTypeDef = TypedDict(
    "ModelPackageValidationSpecificationTypeDef",
    {
        "ValidationRole": str,
        "ValidationProfiles": Sequence[ModelPackageValidationProfileTypeDef],
    },
)

TrialComponentPaginatorTypeDef = TypedDict(
    "TrialComponentPaginatorTypeDef",
    {
        "TrialComponentName": NotRequired[str],
        "DisplayName": NotRequired[str],
        "TrialComponentArn": NotRequired[str],
        "Source": NotRequired[TrialComponentSourceTypeDef],
        "Status": NotRequired[TrialComponentStatusTypeDef],
        "StartTime": NotRequired[datetime],
        "EndTime": NotRequired[datetime],
        "CreationTime": NotRequired[datetime],
        "CreatedBy": NotRequired[UserContextTypeDef],
        "LastModifiedTime": NotRequired[datetime],
        "LastModifiedBy": NotRequired[UserContextTypeDef],
        "Parameters": NotRequired[Dict[str, TrialComponentParameterValueTypeDef]],
        "InputArtifacts": NotRequired[Dict[str, TrialComponentArtifactTypeDef]],
        "OutputArtifacts": NotRequired[Dict[str, TrialComponentArtifactTypeDef]],
        "Metrics": NotRequired[List[TrialComponentMetricSummaryTypeDef]],
        "MetadataProperties": NotRequired[MetadataPropertiesTypeDef],
        "SourceDetail": NotRequired[TrialComponentSourceDetailPaginatorTypeDef],
        "LineageGroupArn": NotRequired[str],
        "Tags": NotRequired[List[TagTypeDef]],
        "Parents": NotRequired[List[ParentTypeDef]],
        "RunName": NotRequired[str],
    },
)

TrialComponentTypeDef = TypedDict(
    "TrialComponentTypeDef",
    {
        "TrialComponentName": NotRequired[str],
        "DisplayName": NotRequired[str],
        "TrialComponentArn": NotRequired[str],
        "Source": NotRequired[TrialComponentSourceTypeDef],
        "Status": NotRequired[TrialComponentStatusTypeDef],
        "StartTime": NotRequired[datetime],
        "EndTime": NotRequired[datetime],
        "CreationTime": NotRequired[datetime],
        "CreatedBy": NotRequired[UserContextTypeDef],
        "LastModifiedTime": NotRequired[datetime],
        "LastModifiedBy": NotRequired[UserContextTypeDef],
        "Parameters": NotRequired[Dict[str, TrialComponentParameterValueTypeDef]],
        "InputArtifacts": NotRequired[Dict[str, TrialComponentArtifactTypeDef]],
        "OutputArtifacts": NotRequired[Dict[str, TrialComponentArtifactTypeDef]],
        "Metrics": NotRequired[List[TrialComponentMetricSummaryTypeDef]],
        "MetadataProperties": NotRequired[MetadataPropertiesTypeDef],
        "SourceDetail": NotRequired[TrialComponentSourceDetailTypeDef],
        "LineageGroupArn": NotRequired[str],
        "Tags": NotRequired[List[TagTypeDef]],
        "Parents": NotRequired[List[ParentTypeDef]],
        "RunName": NotRequired[str],
    },
)

ModelDashboardMonitoringSchedulePaginatorTypeDef = TypedDict(
    "ModelDashboardMonitoringSchedulePaginatorTypeDef",
    {
        "MonitoringScheduleArn": NotRequired[str],
        "MonitoringScheduleName": NotRequired[str],
        "MonitoringScheduleStatus": NotRequired[ScheduleStatusType],
        "MonitoringType": NotRequired[MonitoringTypeType],
        "FailureReason": NotRequired[str],
        "CreationTime": NotRequired[datetime],
        "LastModifiedTime": NotRequired[datetime],
        "MonitoringScheduleConfig": NotRequired[MonitoringScheduleConfigPaginatorTypeDef],
        "EndpointName": NotRequired[str],
        "MonitoringAlertSummaries": NotRequired[List[MonitoringAlertSummaryTypeDef]],
        "LastMonitoringExecutionSummary": NotRequired[MonitoringExecutionSummaryTypeDef],
    },
)

MonitoringSchedulePaginatorTypeDef = TypedDict(
    "MonitoringSchedulePaginatorTypeDef",
    {
        "MonitoringScheduleArn": NotRequired[str],
        "MonitoringScheduleName": NotRequired[str],
        "MonitoringScheduleStatus": NotRequired[ScheduleStatusType],
        "MonitoringType": NotRequired[MonitoringTypeType],
        "FailureReason": NotRequired[str],
        "CreationTime": NotRequired[datetime],
        "LastModifiedTime": NotRequired[datetime],
        "MonitoringScheduleConfig": NotRequired[MonitoringScheduleConfigPaginatorTypeDef],
        "EndpointName": NotRequired[str],
        "LastMonitoringExecutionSummary": NotRequired[MonitoringExecutionSummaryTypeDef],
        "Tags": NotRequired[List[TagTypeDef]],
    },
)

CreateMonitoringScheduleRequestRequestTypeDef = TypedDict(
    "CreateMonitoringScheduleRequestRequestTypeDef",
    {
        "MonitoringScheduleName": str,
        "MonitoringScheduleConfig": MonitoringScheduleConfigTypeDef,
        "Tags": NotRequired[Sequence[TagTypeDef]],
    },
)

DescribeMonitoringScheduleResponseTypeDef = TypedDict(
    "DescribeMonitoringScheduleResponseTypeDef",
    {
        "MonitoringScheduleArn": str,
        "MonitoringScheduleName": str,
        "MonitoringScheduleStatus": ScheduleStatusType,
        "MonitoringType": MonitoringTypeType,
        "FailureReason": str,
        "CreationTime": datetime,
        "LastModifiedTime": datetime,
        "MonitoringScheduleConfig": MonitoringScheduleConfigTypeDef,
        "EndpointName": str,
        "LastMonitoringExecutionSummary": MonitoringExecutionSummaryTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ModelDashboardMonitoringScheduleTypeDef = TypedDict(
    "ModelDashboardMonitoringScheduleTypeDef",
    {
        "MonitoringScheduleArn": NotRequired[str],
        "MonitoringScheduleName": NotRequired[str],
        "MonitoringScheduleStatus": NotRequired[ScheduleStatusType],
        "MonitoringType": NotRequired[MonitoringTypeType],
        "FailureReason": NotRequired[str],
        "CreationTime": NotRequired[datetime],
        "LastModifiedTime": NotRequired[datetime],
        "MonitoringScheduleConfig": NotRequired[MonitoringScheduleConfigTypeDef],
        "EndpointName": NotRequired[str],
        "MonitoringAlertSummaries": NotRequired[List[MonitoringAlertSummaryTypeDef]],
        "LastMonitoringExecutionSummary": NotRequired[MonitoringExecutionSummaryTypeDef],
    },
)

MonitoringScheduleTypeDef = TypedDict(
    "MonitoringScheduleTypeDef",
    {
        "MonitoringScheduleArn": NotRequired[str],
        "MonitoringScheduleName": NotRequired[str],
        "MonitoringScheduleStatus": NotRequired[ScheduleStatusType],
        "MonitoringType": NotRequired[MonitoringTypeType],
        "FailureReason": NotRequired[str],
        "CreationTime": NotRequired[datetime],
        "LastModifiedTime": NotRequired[datetime],
        "MonitoringScheduleConfig": NotRequired[MonitoringScheduleConfigTypeDef],
        "EndpointName": NotRequired[str],
        "LastMonitoringExecutionSummary": NotRequired[MonitoringExecutionSummaryTypeDef],
        "Tags": NotRequired[List[TagTypeDef]],
    },
)

UpdateMonitoringScheduleRequestRequestTypeDef = TypedDict(
    "UpdateMonitoringScheduleRequestRequestTypeDef",
    {
        "MonitoringScheduleName": str,
        "MonitoringScheduleConfig": MonitoringScheduleConfigTypeDef,
    },
)

ModelPackagePaginatorTypeDef = TypedDict(
    "ModelPackagePaginatorTypeDef",
    {
        "ModelPackageName": NotRequired[str],
        "ModelPackageGroupName": NotRequired[str],
        "ModelPackageVersion": NotRequired[int],
        "ModelPackageArn": NotRequired[str],
        "ModelPackageDescription": NotRequired[str],
        "CreationTime": NotRequired[datetime],
        "InferenceSpecification": NotRequired[InferenceSpecificationTypeDef],
        "SourceAlgorithmSpecification": NotRequired[SourceAlgorithmSpecificationPaginatorTypeDef],
        "ValidationSpecification": NotRequired[ModelPackageValidationSpecificationPaginatorTypeDef],
        "ModelPackageStatus": NotRequired[ModelPackageStatusType],
        "ModelPackageStatusDetails": NotRequired[ModelPackageStatusDetailsTypeDef],
        "CertifyForMarketplace": NotRequired[bool],
        "ModelApprovalStatus": NotRequired[ModelApprovalStatusType],
        "CreatedBy": NotRequired[UserContextTypeDef],
        "MetadataProperties": NotRequired[MetadataPropertiesTypeDef],
        "ModelMetrics": NotRequired[ModelMetricsTypeDef],
        "LastModifiedTime": NotRequired[datetime],
        "LastModifiedBy": NotRequired[UserContextTypeDef],
        "ApprovalDescription": NotRequired[str],
        "Domain": NotRequired[str],
        "Task": NotRequired[str],
        "SamplePayloadUrl": NotRequired[str],
        "AdditionalInferenceSpecifications": NotRequired[
            List[AdditionalInferenceSpecificationDefinitionPaginatorTypeDef]
        ],
        "Tags": NotRequired[List[TagTypeDef]],
        "CustomerMetadataProperties": NotRequired[Dict[str, str]],
        "DriftCheckBaselines": NotRequired[DriftCheckBaselinesTypeDef],
        "SkipModelValidation": NotRequired[SkipModelValidationType],
    },
)

CreateAlgorithmInputRequestTypeDef = TypedDict(
    "CreateAlgorithmInputRequestTypeDef",
    {
        "AlgorithmName": str,
        "TrainingSpecification": TrainingSpecificationTypeDef,
        "AlgorithmDescription": NotRequired[str],
        "InferenceSpecification": NotRequired[InferenceSpecificationTypeDef],
        "ValidationSpecification": NotRequired[AlgorithmValidationSpecificationTypeDef],
        "CertifyForMarketplace": NotRequired[bool],
        "Tags": NotRequired[Sequence[TagTypeDef]],
    },
)

DescribeAlgorithmOutputTypeDef = TypedDict(
    "DescribeAlgorithmOutputTypeDef",
    {
        "AlgorithmName": str,
        "AlgorithmArn": str,
        "AlgorithmDescription": str,
        "CreationTime": datetime,
        "TrainingSpecification": TrainingSpecificationTypeDef,
        "InferenceSpecification": InferenceSpecificationTypeDef,
        "ValidationSpecification": AlgorithmValidationSpecificationTypeDef,
        "AlgorithmStatus": AlgorithmStatusType,
        "AlgorithmStatusDetails": AlgorithmStatusDetailsTypeDef,
        "ProductId": str,
        "CertifyForMarketplace": bool,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

CreateModelPackageInputRequestTypeDef = TypedDict(
    "CreateModelPackageInputRequestTypeDef",
    {
        "ModelPackageName": NotRequired[str],
        "ModelPackageGroupName": NotRequired[str],
        "ModelPackageDescription": NotRequired[str],
        "InferenceSpecification": NotRequired[InferenceSpecificationTypeDef],
        "ValidationSpecification": NotRequired[ModelPackageValidationSpecificationTypeDef],
        "SourceAlgorithmSpecification": NotRequired[SourceAlgorithmSpecificationTypeDef],
        "CertifyForMarketplace": NotRequired[bool],
        "Tags": NotRequired[Sequence[TagTypeDef]],
        "ModelApprovalStatus": NotRequired[ModelApprovalStatusType],
        "MetadataProperties": NotRequired[MetadataPropertiesTypeDef],
        "ModelMetrics": NotRequired[ModelMetricsTypeDef],
        "ClientToken": NotRequired[str],
        "CustomerMetadataProperties": NotRequired[Mapping[str, str]],
        "DriftCheckBaselines": NotRequired[DriftCheckBaselinesTypeDef],
        "Domain": NotRequired[str],
        "Task": NotRequired[str],
        "SamplePayloadUrl": NotRequired[str],
        "AdditionalInferenceSpecifications": NotRequired[
            Sequence[AdditionalInferenceSpecificationDefinitionTypeDef]
        ],
        "SkipModelValidation": NotRequired[SkipModelValidationType],
    },
)

DescribeModelPackageOutputTypeDef = TypedDict(
    "DescribeModelPackageOutputTypeDef",
    {
        "ModelPackageName": str,
        "ModelPackageGroupName": str,
        "ModelPackageVersion": int,
        "ModelPackageArn": str,
        "ModelPackageDescription": str,
        "CreationTime": datetime,
        "InferenceSpecification": InferenceSpecificationTypeDef,
        "SourceAlgorithmSpecification": SourceAlgorithmSpecificationTypeDef,
        "ValidationSpecification": ModelPackageValidationSpecificationTypeDef,
        "ModelPackageStatus": ModelPackageStatusType,
        "ModelPackageStatusDetails": ModelPackageStatusDetailsTypeDef,
        "CertifyForMarketplace": bool,
        "ModelApprovalStatus": ModelApprovalStatusType,
        "CreatedBy": UserContextTypeDef,
        "MetadataProperties": MetadataPropertiesTypeDef,
        "ModelMetrics": ModelMetricsTypeDef,
        "LastModifiedTime": datetime,
        "LastModifiedBy": UserContextTypeDef,
        "ApprovalDescription": str,
        "CustomerMetadataProperties": Dict[str, str],
        "DriftCheckBaselines": DriftCheckBaselinesTypeDef,
        "Domain": str,
        "Task": str,
        "SamplePayloadUrl": str,
        "AdditionalInferenceSpecifications": List[
            AdditionalInferenceSpecificationDefinitionTypeDef
        ],
        "SkipModelValidation": SkipModelValidationType,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

ModelPackageTypeDef = TypedDict(
    "ModelPackageTypeDef",
    {
        "ModelPackageName": NotRequired[str],
        "ModelPackageGroupName": NotRequired[str],
        "ModelPackageVersion": NotRequired[int],
        "ModelPackageArn": NotRequired[str],
        "ModelPackageDescription": NotRequired[str],
        "CreationTime": NotRequired[datetime],
        "InferenceSpecification": NotRequired[InferenceSpecificationTypeDef],
        "SourceAlgorithmSpecification": NotRequired[SourceAlgorithmSpecificationTypeDef],
        "ValidationSpecification": NotRequired[ModelPackageValidationSpecificationTypeDef],
        "ModelPackageStatus": NotRequired[ModelPackageStatusType],
        "ModelPackageStatusDetails": NotRequired[ModelPackageStatusDetailsTypeDef],
        "CertifyForMarketplace": NotRequired[bool],
        "ModelApprovalStatus": NotRequired[ModelApprovalStatusType],
        "CreatedBy": NotRequired[UserContextTypeDef],
        "MetadataProperties": NotRequired[MetadataPropertiesTypeDef],
        "ModelMetrics": NotRequired[ModelMetricsTypeDef],
        "LastModifiedTime": NotRequired[datetime],
        "LastModifiedBy": NotRequired[UserContextTypeDef],
        "ApprovalDescription": NotRequired[str],
        "Domain": NotRequired[str],
        "Task": NotRequired[str],
        "SamplePayloadUrl": NotRequired[str],
        "AdditionalInferenceSpecifications": NotRequired[
            List[AdditionalInferenceSpecificationDefinitionTypeDef]
        ],
        "Tags": NotRequired[List[TagTypeDef]],
        "CustomerMetadataProperties": NotRequired[Dict[str, str]],
        "DriftCheckBaselines": NotRequired[DriftCheckBaselinesTypeDef],
        "SkipModelValidation": NotRequired[SkipModelValidationType],
    },
)

ModelDashboardModelPaginatorTypeDef = TypedDict(
    "ModelDashboardModelPaginatorTypeDef",
    {
        "Model": NotRequired[ModelPaginatorTypeDef],
        "Endpoints": NotRequired[List[ModelDashboardEndpointTypeDef]],
        "LastBatchTransformJob": NotRequired[TransformJobTypeDef],
        "MonitoringSchedules": NotRequired[List[ModelDashboardMonitoringSchedulePaginatorTypeDef]],
        "ModelCard": NotRequired[ModelDashboardModelCardTypeDef],
    },
)

EndpointPaginatorTypeDef = TypedDict(
    "EndpointPaginatorTypeDef",
    {
        "EndpointName": str,
        "EndpointArn": str,
        "EndpointConfigName": str,
        "EndpointStatus": EndpointStatusType,
        "CreationTime": datetime,
        "LastModifiedTime": datetime,
        "ProductionVariants": NotRequired[List[ProductionVariantSummaryTypeDef]],
        "DataCaptureConfig": NotRequired[DataCaptureConfigSummaryTypeDef],
        "FailureReason": NotRequired[str],
        "MonitoringSchedules": NotRequired[List[MonitoringSchedulePaginatorTypeDef]],
        "Tags": NotRequired[List[TagTypeDef]],
        "ShadowProductionVariants": NotRequired[List[ProductionVariantSummaryTypeDef]],
    },
)

ModelDashboardModelTypeDef = TypedDict(
    "ModelDashboardModelTypeDef",
    {
        "Model": NotRequired[ModelTypeDef],
        "Endpoints": NotRequired[List[ModelDashboardEndpointTypeDef]],
        "LastBatchTransformJob": NotRequired[TransformJobTypeDef],
        "MonitoringSchedules": NotRequired[List[ModelDashboardMonitoringScheduleTypeDef]],
        "ModelCard": NotRequired[ModelDashboardModelCardTypeDef],
    },
)

EndpointTypeDef = TypedDict(
    "EndpointTypeDef",
    {
        "EndpointName": str,
        "EndpointArn": str,
        "EndpointConfigName": str,
        "EndpointStatus": EndpointStatusType,
        "CreationTime": datetime,
        "LastModifiedTime": datetime,
        "ProductionVariants": NotRequired[List[ProductionVariantSummaryTypeDef]],
        "DataCaptureConfig": NotRequired[DataCaptureConfigSummaryTypeDef],
        "FailureReason": NotRequired[str],
        "MonitoringSchedules": NotRequired[List[MonitoringScheduleTypeDef]],
        "Tags": NotRequired[List[TagTypeDef]],
        "ShadowProductionVariants": NotRequired[List[ProductionVariantSummaryTypeDef]],
    },
)

SearchRecordPaginatorTypeDef = TypedDict(
    "SearchRecordPaginatorTypeDef",
    {
        "TrainingJob": NotRequired[TrainingJobPaginatorTypeDef],
        "Experiment": NotRequired[ExperimentTypeDef],
        "Trial": NotRequired[TrialTypeDef],
        "TrialComponent": NotRequired[TrialComponentPaginatorTypeDef],
        "Endpoint": NotRequired[EndpointPaginatorTypeDef],
        "ModelPackage": NotRequired[ModelPackagePaginatorTypeDef],
        "ModelPackageGroup": NotRequired[ModelPackageGroupTypeDef],
        "Pipeline": NotRequired[PipelineTypeDef],
        "PipelineExecution": NotRequired[PipelineExecutionTypeDef],
        "FeatureGroup": NotRequired[FeatureGroupTypeDef],
        "Project": NotRequired[ProjectPaginatorTypeDef],
        "FeatureMetadata": NotRequired[FeatureMetadataTypeDef],
        "HyperParameterTuningJob": NotRequired[HyperParameterTuningJobSearchEntityPaginatorTypeDef],
        "Model": NotRequired[ModelDashboardModelPaginatorTypeDef],
        "ModelCard": NotRequired[ModelCardTypeDef],
    },
)

SearchRecordTypeDef = TypedDict(
    "SearchRecordTypeDef",
    {
        "TrainingJob": NotRequired[TrainingJobTypeDef],
        "Experiment": NotRequired[ExperimentTypeDef],
        "Trial": NotRequired[TrialTypeDef],
        "TrialComponent": NotRequired[TrialComponentTypeDef],
        "Endpoint": NotRequired[EndpointTypeDef],
        "ModelPackage": NotRequired[ModelPackageTypeDef],
        "ModelPackageGroup": NotRequired[ModelPackageGroupTypeDef],
        "Pipeline": NotRequired[PipelineTypeDef],
        "PipelineExecution": NotRequired[PipelineExecutionTypeDef],
        "FeatureGroup": NotRequired[FeatureGroupTypeDef],
        "Project": NotRequired[ProjectTypeDef],
        "FeatureMetadata": NotRequired[FeatureMetadataTypeDef],
        "HyperParameterTuningJob": NotRequired[HyperParameterTuningJobSearchEntityTypeDef],
        "Model": NotRequired[ModelDashboardModelTypeDef],
        "ModelCard": NotRequired[ModelCardTypeDef],
    },
)

SearchResponsePaginatorTypeDef = TypedDict(
    "SearchResponsePaginatorTypeDef",
    {
        "Results": List[SearchRecordPaginatorTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)

SearchResponseTypeDef = TypedDict(
    "SearchResponseTypeDef",
    {
        "Results": List[SearchRecordTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
