import json
from datetime import datetime
from typing import TypeVar

from pydantic import BaseModel, Field

from .common import AttributionModel, GroupBy, TypeReport, FilterCategory
from .utils import normalize_date


class ChannelItem(BaseModel):
    id: int
    title: str


class Channels(BaseModel):
    items: list[ChannelItem] = Field(alias='channels')


class Channel(BaseModel):
    id: int
    title: str
    channel_id: int


class Placement(BaseModel):
    id: int
    title: str
    channel: Channel


class Placements(BaseModel):
    items: list[Placement] = Field(alias='placements')


class Campaign(BaseModel):
    id: int
    placement_id: int
    title: str


class Campaigns(BaseModel):
    items: list[Campaign] = Field(alias='campaigns')


class Keyword(BaseModel):
    id: int
    keyword: str


class Keywords(BaseModel):
    items: list[Keyword]= Field(alias='keywords')


class CrmCustomField(BaseModel):
    id: int
    crm_account_id: int
    element_type_id: int
    custom_field_title: str
    field_type_id: int
    is_multiple: int
    group_id: int
    description: str
    status: int
    is_filter: int
    filter_param_id: int
    default_visibility: int

class CrmCustomFieldGroup(BaseModel):
    id: int
    title: str
    crm_account_id: int
    default_visibility: int
    sort: int


class CrmCustomFields(BaseModel):
    items: list[CrmCustomField] = Field(alias='crmCustomFields')

class CrmCustomFieldGroups(BaseModel):
    items: list[CrmCustomFieldGroup] = Field(alias='crmCustomFieldGroups')


class Ad(BaseModel):
    id: int
    external_id: str
    placement_id: int
    campaign_id: int | None
    external_campaign_id: str | None
    type: str
    title: str | None
    text: str | None
    text1: str | None
    text2: str | None
    preview_url: str | None
    href: str | None
    device: str | None
    created_at: str


class Ads(BaseModel):
    items: list[Ad] = Field(alias='ads')


Entity = TypeVar('Entity', ChannelItem, Placement, Campaign, Keyword, CrmCustomField, CrmCustomFieldGroup, Ad)
FieldsEntity = TypeVar('FieldsEntity', CrmCustomField, CrmCustomFieldGroup)
RootEntity = TypeVar('RootEntity', Channels, Placements, Campaigns, Keywords, CrmCustomFields, CrmCustomFieldGroups, Ads)
FieldsRootEntity = TypeVar('FieldsRootEntity', CrmCustomFields, CrmCustomFieldGroups)


class Attribution:

    def __init__(self, model_id: AttributionModel, period: int, with_direct: bool):
        self.model_id = model_id.value
        self.period = period
        self.with_direct = with_direct

    def __str__(self):
        return f"{self.model_id} {self.period} {self.with_direct}"


class Filter:
    def __init__(self, category: FilterCategory, value: int, operand: str = "="):
        self.category = category.value
        self.value = value
        self.operand = operand


class Payload:
    """Базовый класс параметров для генерации параметров к запросам"""

    def __init__(self, project: str, metrics: [str], datetime_from: datetime, datetime_to: datetime,
                 group_by: GroupBy, attribution: Attribution = None, type_report: TypeReport = TypeReport.AGGREGATED,
                 filters: list[Filter] | None = None, fields: list[str] | None = None):
        self.project = project
        self.metrics = ";".join(metrics) if metrics else ""
        self.datetime_from: str = normalize_date(datetime_from)
        self.datetime_to: str = normalize_date(datetime_to)
        self.group_by = group_by
        self.type = type_report
        self.filters = filters
        self.attribution = attribution
        self.fields = fields

    def __str__(self):
        return f"{self.datetime_from}//{self.datetime_to}"

    def to_json(self) -> str:
        payload = {"project": self.project,
                   "metrics": self.metrics,
                   "datetimeFrom": self.datetime_from,
                   "datetimeTo": self.datetime_to,
                   "groupBy": self.group_by.value,
                   "type": self.type.value}
        if self.filters:
            payload["filters"] = self.filters
        if self.attribution:
            payload["attribution"] = self.attribution.__dict__

        if self.fields:
            payload["fields"] = self.fields
        return json.dumps(payload)
