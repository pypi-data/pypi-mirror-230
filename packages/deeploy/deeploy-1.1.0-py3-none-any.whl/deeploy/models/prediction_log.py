from typing import Dict, Optional

from pydantic import BaseModel


class RequestLog(BaseModel):
    id: str
    deploymentId: str
    commit: str
    requestContentType: str
    responseTimeMS: int
    statusCode: int
    personalKeysId: Optional[str]
    tokenId: Optional[str]
    createdAt: str
    predictionLogs: Optional[Dict]


class PredictionLog(BaseModel):
    id: str
    requestBody: Optional[Dict]
    requestBodyBlobLink: Optional[str]
    responseBody: Dict
    requestLog: Dict
    evaluation: Optional[Dict]
    actual: Optional[Dict]
    createdAt: str
    tags: Dict
