from __future__ import annotations

import re

CATEGORY_KEYWORDS = {
    "Water Leakage": ["water", "leak", "pipe", "drain", "flood", "sewer", "wet", "plumbing"],
    "Lighting": ["light", "bulb", "lamp", "dark", "power", "lighting", "glow", "switch"],
    "Electrical": ["electrical", "short", "circuit", "power", "socket", "sparks", "wire", "voltage"],
    "Cleanliness": ["garbage", "trash", "dust", "dirty", "clean", "sanitation", "litter", "toilet"],
    "Network/Wi-Fi": ["wifi", "wi-fi", "network", "internet", "signal", "router", "connectivity", "broadband"],
    "Furniture": ["chair", "table", "bench", "desk", "cabinet", "furniture", "broken"],
    "Road/Pathway": ["road", "path", "pavement", "crack", "sidewalk", "walkway", "lane"],
    "Washroom": ["washroom", "restroom", "toilet", "bathroom", "sanitizer", "wc"],
    "Safety": ["safety", "hazard", "unsafe", "danger", "accident", "injury", "gate", "fence"],
    "Infrastructure": ["wall", "roof", "ceiling", "door", "window", "building", "structure", "infrastructure"],
}

SEVERITY_KEYWORDS = {
    "Critical": ["urgent", "danger", "hazard", "safety", "fire", "electrical", "leak", "water", "critical"],
    "High": ["severe", "leak", "broken", "dark", "power", "network", "flood", "wet"],
    "Medium": ["damaged", "faulty", "issue", "problem", "maintenance"],
    "Low": ["small", "minor", "cosmetic", "slightly", "light"],
}


def extract_keywords(text: str):
    text = (text or "").lower()
    tokens = re.findall(r"[a-zA-Z0-9]+", text)
    return list(dict.fromkeys(tokens))[:12]


def classify_category(title: str, description: str, category_hint: str | None = None):
    if category_hint:
        return category_hint
    combined = f"{title or ''} {description or ''}".lower()
    scores = {}
    for category, keywords in CATEGORY_KEYWORDS.items():
        score = sum(1 for keyword in keywords if keyword in combined)
        scores[category] = score
    best_category, best_score = max(scores.items(), key=lambda item: item[1], default=("Other", 0))
    if best_score == 0:
        return "Other"
    return best_category


def classify_severity(title: str, description: str):
    combined = f"{title or ''} {description or ''}".lower()
    for severity in ["Critical", "High", "Medium", "Low"]:
        if any(keyword in combined for keyword in SEVERITY_KEYWORDS.get(severity, [])):
            return severity
    return "Medium"


def recommend_priority(category: str, severity: str):
    category = category or "Other"
    severity = severity or "Medium"
    if category in {"Safety", "Electrical"} or severity == "Critical":
        return "Critical"
    if category in {"Water Leakage", "Road/Pathway"} or severity == "High":
        return "High"
    if category in {"Lighting", "Network/Wi-Fi", "Cleanliness"} or severity == "Medium":
        return "Medium"
    return "Low"


def analyze_issue(title: str, description: str, category_hint: str | None = None):
    category = classify_category(title, description, category_hint)
    severity = classify_severity(title, description)
    priority = recommend_priority(category, severity)
    keywords = extract_keywords(f"{title or ''} {description or ''}")
    recommendation = (
        f"Potential {category.lower()} impact detected. "
        f"Severity is {severity.lower()} and recommended priority is {priority}."
    )
    return {
        "category": category,
        "severity": severity,
        "priority": priority,
        "keywords": keywords,
        "recommendation": recommendation,
    }
