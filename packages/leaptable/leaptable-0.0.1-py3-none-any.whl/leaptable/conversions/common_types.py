from typing import Union, List

from leaptable.client.http import models as rest
from leaptable.client import grpc

Filter = Union[rest.Filter, grpc.Filter]
SearchParams = Union[rest.SearchParams, grpc.SearchParams]
PayloadSelector = Union[rest.PayloadSelector, grpc.WithPayloadSelector]
Distance = Union[rest.Distance, grpc.Distance]
HnswConfigDiff = Union[rest.HnswConfigDiff, grpc.HnswConfigDiff]
OptimizersConfigDiff = Union[rest.OptimizersConfigDiff, grpc.OptimizersConfigDiff]
WalConfigDiff = Union[rest.WalConfigDiff, grpc.WalConfigDiff]
PointId = Union[int, str, grpc.PointId]
PayloadSchemaType = Union[rest.PayloadSchemaType, grpc.PayloadSchemaType]
Points = Union[rest.Batch, List[Union[rest.PointStruct, grpc.PointStruct]]]
PointsSelector = Union[rest.PointsSelector, grpc.PointsSelector]
AliasOperations = Union[
    rest.CreateAliasOperation,
    rest.RenameAliasOperation,
    rest.DeleteAliasOperation,
    grpc.AliasOperations
]
Payload = rest.Payload

ScoredPoint = rest.ScoredPoint
UpdateResult = rest.UpdateResult
Record = rest.Record
CollectionsResponse = rest.CollectionsResponse
CollectionInfo = rest.CollectionInfo
CountResult = rest.CountResult
SnapshotDescription = rest.SnapshotDescription
