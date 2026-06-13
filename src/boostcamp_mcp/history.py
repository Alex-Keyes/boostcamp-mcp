"""Pure transforms for shaping Boostcamp training history.

The upstream /programs/history endpoint returns the entire history grouped by
date with no server-side filtering or pagination, so all shaping happens here.
No network or I/O — every function in this module is pure and unit-tested.
"""
import re
from collections import Counter
from typing import Any, Optional

VALID_DETAIL = ("summary", "full")
SUMMARY_CAP = 100
FULL_CAP = 25
_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def _to_number(raw: Any, empty: bool) -> float:
    """Coerce a stringy numeric field to float; empty/blank -> 0.0."""
    if empty:
        return 0.0
    try:
        return float(raw)
    except (TypeError, ValueError):
        return 0.0


def _slim_set(s: dict) -> dict:
    """Keep only the analytically meaningful fields of a raw set."""
    intensity = s.get("intensity") or None
    return {
        "weight": _to_number(s.get("value"), s.get("valueEmpty", False)),
        "reps": _to_number(s.get("amount"), s.get("amountEmpty", False)),
        "target": s.get("target"),
        "target_type": s.get("target_type"),
        "rpe": intensity,
        "skipped": s.get("skipped", False),
        "weight_unit": s.get("weight_unit"),
    }


def _set_volume(s: dict) -> float:
    """weight * reps for a non-skipped set, else 0.0."""
    if s.get("skipped", False):
        return 0.0
    weight = _to_number(s.get("value"), s.get("valueEmpty", False))
    reps = _to_number(s.get("amount"), s.get("amountEmpty", False))
    return weight * reps


def _normalize_records(records: list) -> list:
    """Expand Superset wrapper records into their child exercises.

    A Superset record carries no name or sets of its own — its exercises live in
    a `supersets` list, each shaped like a normal record. Left as-is they surface
    as a `null` exercise and, worse, their sets (often real weighted work) are
    skipped when computing volume. We expand the children to top-level records,
    tagging each with the wrapper's id so full detail can still show the grouping.
    Non-superset records pass through unchanged.
    """
    out = []
    for r in records:
        if r.get("type") == "Superset":
            group = r.get("uniq") or r.get("id")
            for child in r.get("supersets", []):
                tagged = dict(child)
                tagged["superset"] = group
                out.append(tagged)
        else:
            out.append(r)
    return out


def _workout_volume_and_unit(records: list) -> tuple[float, Optional[str]]:
    """Total volume across non-skipped sets, and the dominant weight unit.

    Volume excludes skipped sets, but the unit is read from any set that
    declares a weight_unit (skipped or not) so bodyweight/skipped-only days
    still report the unit their weights would be in rather than null.
    """
    total = 0.0
    units: Counter = Counter()
    for rec in records:
        for s in rec.get("sets", []):
            total += _set_volume(s)
            if s.get("weight_unit"):
                units[s["weight_unit"]] += 1
    unit = units.most_common(1)[0][0] if units else None
    return total, unit


def _summarize_workout(w: dict) -> dict:
    records = _normalize_records(w.get("records", []))
    total, unit = _workout_volume_and_unit(records)
    named = [r for r in records if r.get("name")]
    return {
        "date": w.get("date"),
        "title": w.get("title"),
        "program_name": w.get("name"),
        "week": w.get("week"),
        "day": w.get("day"),
        "finished_at": w.get("finished_at"),
        "exercise_count": len(named),
        "exercises": [r["name"] for r in named],
        "total_volume": total,
        "volume_unit": unit,
    }


def _full_workout(w: dict) -> dict:
    out = _summarize_workout(w)
    records = []
    for r in _normalize_records(w.get("records", [])):
        rec = {
            "name": r.get("name"),
            "type": r.get("type"),
            "muscles_list": r.get("muscles_list", []),
            "sets": [_slim_set(s) for s in r.get("sets", [])],
        }
        if r.get("superset"):
            rec["superset"] = r["superset"]
        records.append(rec)
    out["records"] = records
    return out


def _flatten(raw: dict) -> list:
    """Flatten {date: [workout,...]} into a flat list tagged with date,
    sorted newest-first (tie-break: later finished_at first)."""
    flat = []
    for date, workouts in raw.get("data", {}).items():
        for w in workouts:
            tagged = dict(w)
            tagged["date"] = date
            flat.append(tagged)
    flat.sort(key=lambda w: (w["date"], w.get("finished_at") or ""),
              reverse=True)
    return flat


def _filter_by_date(flat: list, start_date: Optional[str],
                    end_date: Optional[str]) -> list:
    """Inclusive date-range filter on the YYYY-MM-DD date tag."""
    out = flat
    if start_date:
        out = [w for w in out if w["date"] >= start_date]
    if end_date:
        out = [w for w in out if w["date"] <= end_date]
    return out


def _check_date(label: str, value: Optional[str]) -> None:
    if value is not None and not _DATE_RE.match(value):
        raise ValueError(f"{label} must be YYYY-MM-DD (got {value!r}).")


def validate_params(start_date, end_date, detail, page, page_size) -> int:
    """Validate inputs; return the effective (capped) page_size.

    Raises ValueError with a user-facing message on bad input.
    """
    _check_date("start_date", start_date)
    _check_date("end_date", end_date)
    if detail not in VALID_DETAIL:
        raise ValueError(
            f"detail must be one of {VALID_DETAIL} (got {detail!r}).")
    if page < 1:
        raise ValueError(f"page must be >= 1 (got {page}).")
    if page_size < 1:
        raise ValueError(f"page_size must be >= 1 (got {page_size}).")
    cap = SUMMARY_CAP if detail == "summary" else FULL_CAP
    return min(page_size, cap)


def _build_hint(total, page, page_size, returned, has_more, detail) -> str:
    if total == 0:
        return ("No workouts match. Remove or widen start_date/end_date, "
                "or omit them to see your full history.")
    parts = [f"{total} workouts match."]
    if returned == 0:
        last_page = (total + page_size - 1) // page_size
        parts.append(f"Page {page} is past the end; last page is {last_page}.")
        return " ".join(parts)
    parts.append(f"Showing {returned} (page {page}, {detail}).")
    if has_more:
        parts.append(f"Use page={page + 1} for older workouts, or "
                     "start_date/end_date (YYYY-MM-DD) to narrow.")
    if detail == "summary":
        parts.append("Use detail='full' for sets and reps.")
    return " ".join(parts)


def shape_history(raw, *, start_date, end_date, detail, page, page_size) -> dict:
    """Public entrypoint: validate, filter, shape, paginate, build envelope."""
    effective_size = validate_params(
        start_date, end_date, detail, page, page_size)

    flat = _filter_by_date(_flatten(raw), start_date, end_date)
    total = len(flat)

    start = (page - 1) * effective_size
    end = start + effective_size
    page_items = flat[start:end]

    shaper = _summarize_workout if detail == "summary" else _full_workout
    workouts = [shaper(w) for w in page_items]

    returned = len(workouts)
    has_more = end < total
    return {
        "workouts": workouts,
        "pagination": {
            "page": page,
            "page_size": effective_size,
            "total": total,
            "returned": returned,
            "has_more": has_more,
        },
        "filters": {
            "start_date": start_date,
            "end_date": end_date,
            "detail": detail,
        },
        "hint": _build_hint(
            total, page, effective_size, returned, has_more, detail),
    }
