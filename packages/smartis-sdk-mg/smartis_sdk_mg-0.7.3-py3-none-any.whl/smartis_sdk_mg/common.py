"""Словари используемые в модуле main."""
from collections import namedtuple
from enum import Enum


class Filter(Enum):
    SmartisID = 7071
    Channel = 1222
    Placement = 1223


MethodFields = namedtuple("MethodFields", "method location id")


class Method(Enum):
    GET_PROJECTS = MethodFields("projects/get", "projects", "project")
    GET_METRICS = MethodFields("metrics/get", "metrics", "code")
    GET_GROUPINGS = MethodFields("reports/getGroupings", "groupings", "code")
    GET_ATTRIBUTIONS = MethodFields("reports/getModelAttributions", "modelAttributions", "id")
    GET_CHANNELS = MethodFields("reports/getChannels", "", "")
    GET_PLACEMENTS = MethodFields("reports/getPlacements", "", "")
    GET_CAMPAIGNS = MethodFields("reports/getCampaigns", "", "")
    GET_ADS = MethodFields("reports/getAds", "", "")
    GET_KEYWORDS = MethodFields("reports/getKeywords", "", "")
    GET_CRM_CUSTOM_FIELDS = MethodFields("crm/crmCustomField/get", "crmCustomFields", "")
    GET_CRM_CUSTOM_FIELD_GROUPS = MethodFields("crm/crmCustomFieldGroup/get", "crmCustomFieldGroups", "")


class GroupBy(Enum):
    ADS = "ad_id"
    DAY = "day"
    PLACEMENT = "placement_id"
    CAMPAIGN = "campaigns"
    OBJECTS = "smartis_object"


class FilterCategory(Enum):
    SMARTIS_ID = 7071
    CHANNEL = 1222
    PLACEMENT = 1223


class AttributionModel(Enum):
    LAST_CLICK = 1  # Последнее касание
    FIRST_CLICK = 2  # Первое касание
    LINEAR = 3  # Линейное распределение
    BY_POSITION = 4  # На основе позиции
    FIRST_COMMUNICATION = 5  # Первое обращение
    LINEAR_BY_COMMUNICATION = 6  # Линейное распределение на обращениях
    LINEAR_WITH_POSTVIEW = 10  # Линейное распределение с учетом post-view
    LAST_CLICK_WITH_POSTVIEW = 15  # Последнее касание с учетом post-view
    FIRST_CLICK_WITH_POSTVIEW = 16  # Первое касание с учетом post-view
    NOT_FIRST_NOT_LAST_CLICK = 17  # Не первое и не последнее
    LAST_COMMUNICATION = 22  # Последнее обращение
    BY_POSITION_WITH_POSTVIEW = 23  # На основе позиции с учетом post-view


class TypeReport(Enum):
    RAW = "raw"
    AGGREGATED = "aggregated"
