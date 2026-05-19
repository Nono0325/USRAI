from datetime import timedelta

from django.db.models import Avg
from django.utils import timezone

from inn_app.models import ContactInfo, Course, Event, Story, TechProject, USRAchievement
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


def search_site(query: str) -> dict:
    query = (query or "").strip()
    if not query:
        return {"error": "請提供搜尋關鍵字。"}

    return {
        "courses": [
            {"title": item.title, "instructor": item.instructor, "start_time": item.start_time.isoformat()}
            for item in Course.objects.filter(title__icontains=query, is_active=True).order_by("-start_time")[:5]
        ],
        "events": [
            {"title": item.title, "date": item.date.isoformat(), "description": item.description[:120]}
            for item in Event.objects.filter(title__icontains=query).order_by("-date")[:5]
        ],
        "stories": [
            {"title": item.title, "category": item.category}
            for item in Story.objects.filter(title__icontains=query).order_by("-created_at")[:5]
        ],
        "achievements": [
            {"title": item.title, "date": item.date.isoformat(), "summary": item.summary[:120]}
            for item in USRAchievement.objects.filter(title__icontains=query).order_by("-date")[:5]
        ],
        "tech_projects": [
            {"name": item.name}
            for item in TechProject.objects.filter(name__icontains=query, is_active=True).order_by("order")[:5]
        ],
    }


def get_upcoming_courses(limit: int = 5) -> dict:
    limit = min(max(int(limit or 5), 1), 10)
    courses = Course.objects.filter(
        is_active=True,
        start_time__gte=timezone.now(),
    ).order_by("start_time")[:limit]
    return {
        "courses": [
            {
                "title": item.title,
                "instructor": item.instructor,
                "start_time": item.start_time.isoformat(),
                "capacity": item.capacity,
            }
            for item in courses
        ]
    }


def get_contact_info() -> dict:
    info = ContactInfo.objects.filter(is_active=True).first()
    if not info:
        return {"error": "目前尚未設定聯絡資訊。"}
    return {
        "title": info.title,
        "address": info.address,
        "phone": info.phone,
        "email": info.email,
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
    {
        "type": "function",
        "function": {
            "name": "search_site",
            "description": "搜尋網站內容，包含課程、活動、故事、USR 成果與科技專案。",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "搜尋關鍵字"}
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_upcoming_courses",
            "description": "查詢近期可參加的課程與活動報名資訊。",
            "parameters": {
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "description": "回傳筆數，預設 5"}
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_contact_info",
            "description": "查詢水井村風雲客棧的地址、電話與 Email。",
            "parameters": {"type": "object", "properties": {}},
        },
    },
]

_TOOL_REGISTRY = {
    "list_ponds": list_ponds,
    "get_latest_water_quality": get_latest_water_quality,
    "get_average_do": get_average_do,
    "get_water_quality_history": get_water_quality_history,
    "check_thresholds": check_thresholds,
    "search_site": search_site,
    "get_upcoming_courses": get_upcoming_courses,
    "get_contact_info": get_contact_info,
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
