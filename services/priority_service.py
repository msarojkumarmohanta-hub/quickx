from __future__ import annotations


def get_priority_rank(priority: str) -> int:
    mapping = {"Critical": 4, "High": 3, "Medium": 2, "Low": 1}
    return mapping.get(str(priority).title(), 2)


def recommended_priority_from_rules(category: str, description: str, location: str | None = None):
    text = f"{category or ''} {description or ''} {location or ''}".lower()
    if any(word in text for word in ["fire", "hazard", "electric", "water leak", "flood", "danger", "safety"]):
        return "Critical"
    if any(word in text for word in ["water", "road", "crack", "dark", "wifi", "light", "broken", "wet", "leak"]):
        return "High"
    if any(word in text for word in ["dirty", "noise", "furniture", "washroom", "facility", "delay"]):
        return "Medium"
    return "Low"
