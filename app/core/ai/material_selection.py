import datetime
from typing import List, Dict, Any, Optional

def select_personalized_materials(
    student: Dict[str, Any],
    candidate_content: List[Dict[str, Any]],
    *,
    context: Optional[Dict[str, Any]] = None,
    max_items: int = 10
) -> Dict[str, Any]:
    """
    Protocol-compliant material selection engine.
    See /docs/architecture/material_selection_protocol.md
    """
    student_id = student.get("id")
    completed = set(student.get("completed_content", []))
    learning_style = student.get("learning_style")
    performance = student.get("performance", {})
    selection_context = {}

    context = context or {}
    required_style = context.get("required_style")
    exclude_ids = set(context.get("exclude_ids", []))
    prioritize_tags = set(context.get("prioritize_tags", []))
    presentation_mode = context.get("presentation_mode")
    selection_context.update({k: v for k, v in context.items() if v})
    # --- Filtering ---
    filtered = []
    for item in candidate_content:
        cid = item.get("id")
        if cid in completed or cid in exclude_ids:
            continue
        tags = set(item.get("tags", []))
        fmt = item.get("format", None)
        # Required style - must intersect tags/format or skip
        if required_style:
            if (fmt and required_style == fmt) or (required_style in tags):
                pass
            else:
                continue
        filtered.append(item)

    # --- Ranking/Scoring ---
    results = []
    for item in filtered:
        score = 1.0  # baseline; boost if prioritized or matches style/format
        tags = set(item.get("tags", []))
        fmt = item.get("format")
        reason_parts = []
        # Boost for matching learning style
        if learning_style and ((fmt and fmt == learning_style) or (learning_style in tags)):
            score += 0.5
            reason_parts.append(f"Matches preferred learning style '{learning_style}'")
        if prioritize_tags and tags.intersection(prioritize_tags):
            score += 0.5
            reason_parts.append(f"Priority tag(s): {', '.join(prioritize_tags & tags)}")
        # Performance or difficulty could influence score for real adaptation
        difficulty = item.get("difficulty")
        if difficulty == "hard" and performance and item["id"] not in performance:
            score -= 0.2
            reason_parts.append("Reduced score: not previously attempted hard material")
        # Always explain non-completion
        reason_parts.append("Not completed yet")
        results.append((score, item, " and ".join(reason_parts)))

    # Order by score, then by original input order for stability
    results = sorted(results, key=lambda t: (-t[0], candidate_content.index(t[1])))
    selected = results[:max_items]

    # Build output per protocol
    selected_materials = []
    for idx, (score, item, reason) in enumerate(selected, 1):
        selected_materials.append({
            "order": idx,
            "content_id": item["id"],
            "content_type": item["type"],
            "format": item.get("format"),
            "reason": reason,
            "score": round(score, 2)
        })

    now = datetime.datetime.now(datetime.UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")

    return {
        "student_id": student_id,
        "selected_materials": selected_materials,
        "generated_at": now,
        "selection_context": selection_context
    }