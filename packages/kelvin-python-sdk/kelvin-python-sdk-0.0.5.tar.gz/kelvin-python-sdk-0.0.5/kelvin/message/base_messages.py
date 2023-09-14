from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field, validator

from kelvin.message.krn import KRN
from kelvin.message.message import Message
from kelvin.message.msg_type import (
    KMessageTypeControl,
    KMessageTypeControlStatus,
    KMessageTypeData,
    KMessageTypeRecommendation,
)
from kelvin.message.utils import from_rfc3339_timestamp, to_rfc3339_timestamp


class ControlChangeModel(BaseModel):
    timeout: Optional[int] = Field(description="Timeout for retries")
    retries: Optional[int] = Field(description="Max retries")
    expiration_date: datetime = Field(decription="Absolutc expiration Date in UTC")
    payload: Any = Field(None, description="Control Change payload")

    class Config:
        json_encoders = {datetime: to_rfc3339_timestamp}

    @validator("expiration_date", pre=True, always=True)
    def parse_expiration_date(cls, v: Union[str, datetime]) -> datetime:
        if isinstance(v, str):
            return from_rfc3339_timestamp(v)
        return v


class ControlChange(Message):
    """Generic Control Change Message"""

    _TYPE = KMessageTypeControl(icd="kelvin.control_change")

    payload: ControlChangeModel


class StateEnum(str, Enum):
    ready = "ready"
    sent = "sent"
    failed = "failed"
    processed = "processed"
    applied = "applied"


class ControlChangeStatusModel(BaseModel):
    state: StateEnum
    message: Optional[str] = Field(decription="")
    payload: Any = Field(None, description="Metric value at status time")


class ControlChangeStatus(Message):
    """Generic Control Change Message"""

    _TYPE = KMessageTypeControlStatus(icd="kelvin.control_change_status")

    payload: ControlChangeStatusModel


class SensorDataModel(BaseModel):
    data: List[float] = Field(..., description="Array of sensor measurements.", min_items=1)
    sample_rate: float = Field(..., description="Sensor sample-rate in Hertz.", gt=0.0)


class SensorData(Message):
    """Sensor data."""

    _TYPE = KMessageTypeData("object", "kelvin.sensor_data")

    payload: SensorDataModel


class AlarmModel(BaseModel):
    alarm_type_name: str
    description: str
    payload: Dict
    severity: Optional[int] = Field(ge=1, le=5)
    solution: Optional[str]
    tags: Optional[List[str]]
    target_asset_name: str
    custom_identifier: Optional[str]
    title: str


class DataLabelMetricModel(BaseModel):
    asset_name: str
    name: str


class DataLabelModel(BaseModel):
    confidence: int
    description: str
    info: Dict
    label_name: str
    metrics: List[DataLabelMetricModel]
    start_date: datetime
    end_date: datetime
    validation: bool

    class Config:
        json_encoders = {datetime: to_rfc3339_timestamp}

    @validator("start_date", "end_date", pre=True, always=True)
    def parse_datetime(cls, v: Union[str, datetime]) -> datetime:
        if isinstance(v, str):
            return from_rfc3339_timestamp(v)
        return v


class RecommendationControlChangeModel(ControlChangeModel):
    # asset and metric name optional, to be removed later
    retries: Optional[int] = Field(description="Max retries", alias="retry")
    asset_name: Optional[str]
    metric_name: Optional[str]


class RecommendationActionsModel(BaseModel):
    # alarms and datalabels deprecated, to be removed later
    alarms: Optional[List[AlarmModel]] = None
    control_changes: List[RecommendationControlChangeModel] = []
    datalabels: Optional[List[DataLabelModel]] = None


class RecommendationModel(BaseModel):
    source: Optional[KRN]
    resource: KRN
    type: str
    description: Optional[str]
    confidence: Optional[int] = Field(ge=1, le=4)
    expiration_date: Optional[datetime]
    actions: RecommendationActionsModel = RecommendationActionsModel()
    metadata: Dict[str, Any] = {}

    class Config:
        json_encoders = {datetime: to_rfc3339_timestamp}

    @validator("expiration_date", pre=True, always=True)
    def parse_expiration_date(cls, v: Union[str, datetime]) -> datetime:
        if isinstance(v, str):
            return from_rfc3339_timestamp(v)
        return v


class Recommendation(Message):
    _TYPE = KMessageTypeRecommendation()

    payload: RecommendationModel
