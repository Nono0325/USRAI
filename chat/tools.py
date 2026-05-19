from datetime import timedelta

from django.db.models import Avg
from django.utils import timezone

from water.models import Pond


def list_ponds() -> dict:
    ponds = list(Pond.objects.values("name", "species", "description"))
    return {"ponds": ponds}


def get_latest_water_quality(pond_name: str) -> dict:
    try:
        pond = Pond.objects.get(name=pond_name)
    except Pond.DoesNotExist:
        return {
            "error": f"找不到魚塭 `{pond_name}`。",
            "available_ponds": list(Pond.objects.values_list("name", flat=True)),
        }

    latest = pond.readings.first()
    if not latest:
        return {"error": f"`{pond_name}` 目前沒有水質讀數。"}

    return {
        "pond": pond.name,
        "species": pond.species,
        "measured_at": latest.measured_at.isoformat(),
        "temperature_c": latest.temperature,
        "ph": latest.ph,
        "dissolved_oxygen_mg_l": latest.dissolved_oxygen,
        "salinity_ppt": latest.salinity,
    }


def get_average_do(pond_name: str, days: int = 7) -> dict:
    try:
        pond = Pond.objects.get(name=pond_name)
    except Pond.DoesNotExist:
        return {"error": f"找不到魚塭 `{pond_name}`。"}

    since = timezone.now() - timedelta(days=days)
    avg = pond.readings.filter(measured_at__gte=since).aggregate(
        avg_do=Avg("dissolved_oxygen")
    )
    return {
        "pond": pond.name,
        "days": days,
        "average_dissolved_oxygen_mg_l": round(avg["avg_do"] or 0, 2),
    }


def get_water_quality_history(pond_name: str, days: int = 3) -> dict:
    try:
        pond = Pond.objects.get(name=pond_name)
    except Pond.DoesNotExist:
        return {"error": f"找不到魚塭 `{pond_name}`。"}

    since = timezone.now() - timedelta(days=days)
    readings = pond.readings.filter(measured_at__gte=since).order_by("-measured_at")[:30]
    return {
        "pond": pond.name,
        "days": days,
        "readings": [
            {
                "measured_at": item.measured_at.isoformat(),
                "temperature_c": item.temperature,
                "ph": item.ph,
                "dissolved_oxygen_mg_l": item.dissolved_oxygen,
                "salinity_ppt": item.salinity,
            }
            for item in readings
        ],
    }


def check_thresholds(pond_name: str) -> dict:
    latest = get_latest_water_quality(pond_name)
    if "error" in latest:
        return latest

    alerts = []
    if latest["dissolved_oxygen_mg_l"] < 4:
        alerts.append("溶氧低於 4 mg/L，建議立即增氧並觀察魚群活動。")
    if latest["ph"] < 6.5 or latest["ph"] > 9:
        alerts.append("pH 超出建議範圍 6.5-9，建議複測並檢查水源。")
    if latest["temperature_c"] > 32:
        alerts.append("水溫偏高，建議加強遮蔭與換水評估。")

    return {
        "pond": latest["pond"],
        "latest": latest,
        "status": "warning" if alerts else "normal",
        "alerts": alerts,
    }


TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "list_ponds",
            "description": "列出目前可查詢的魚塭名稱、養殖物種與描述。",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_latest_water_quality",
            "description": "查詢指定魚塭最新水質資料。",
            "parameters": {
                "type": "object",
                "properties": {
                    "pond_name": {"type": "string", "description": "魚塭名稱，例如 1 號池"}
                },
                "required": ["pond_name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_average_do",
            "description": "查詢指定魚塭最近 N 天平均溶氧。",
            "parameters": {
                "type": "object",
                "properties": {
                    "pond_name": {"type": "string", "description": "魚塭名稱，例如 1 號池"},
                    "days": {"type": "integer", "description": "天數，預設 7"},
                },
                "required": ["pond_name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_water_quality_history",
            "description": "查詢指定魚塭最近 N 天的水質歷史。",
            "parameters": {
                "type": "object",
                "properties": {
                    "pond_name": {"type": "string", "description": "魚塭名稱，例如 1 號池"},
                    "days": {"type": "integer", "description": "天數，預設 3"},
                },
                "required": ["pond_name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "check_thresholds",
            "description": "檢查指定魚塭最新水質是否有異常。",
            "parameters": {
                "type": "object",
                "properties": {
                    "pond_name": {"type": "string", "description": "魚塭名稱，例如 1 號池"}
                },
                "required": ["pond_name"],
            },
        },
    },
]

_TOOL_REGISTRY = {
    "list_ponds": list_ponds,
    "get_latest_water_quality": get_latest_water_quality,
    "get_average_do": get_average_do,
    "get_water_quality_history": get_water_quality_history,
    "check_thresholds": check_thresholds,
}


def dispatch(name: str, arguments: dict) -> dict:
    fn = _TOOL_REGISTRY.get(name)
    if fn is None:
        return {"error": f"unknown tool: {name}"}
    try:
        return fn(**arguments)
    except TypeError as exc:
        return {"error": f"參數錯誤：{exc}"}
    except Exception as exc:  # noqa: BLE001
        return {"error": f"工具執行失敗：{type(exc).__name__}: {exc}"}
