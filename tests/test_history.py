from boostcamp_mcp.history import _slim_set, _to_number, _set_volume


def test_to_number_parses_string_weight():
    assert _to_number("120", empty=False) == 120.0

def test_to_number_empty_returns_zero():
    assert _to_number("120", empty=True) == 0.0
    assert _to_number("", empty=False) == 0.0

def test_slim_set_keeps_only_meaningful_fields():
    raw = {
        "id": "abc", "from": "app", "value": "120", "amount": "10",
        "custom": False, "source": "user created", "target": 10,
        "skipped": False, "intensity": [3, 4], "time_unit": "minutes",
        "valueEmpty": False, "amountEmpty": False, "target_type": "reps",
        "target_unit": "minutes", "weight_unit": "lbs", "archived_rpe": 0,
        "archived_reps": 10, "previous_reps": 10, "intensity_unit": "RPE_range",
        "archived_weight": 120, "previous_weight": 120, "support_distance": False,
    }
    assert _slim_set(raw) == {
        "weight": 120.0, "reps": 10.0, "target": 10, "target_type": "reps",
        "rpe": [3, 4], "skipped": False, "weight_unit": "lbs",
    }

def test_slim_set_empty_rpe_becomes_none():
    raw = {"value": "100", "amount": "5", "valueEmpty": False,
           "amountEmpty": False, "intensity": [], "skipped": False,
           "weight_unit": "kg", "target": 5, "target_type": "reps"}
    assert _slim_set(raw)["rpe"] is None

def test_set_volume_multiplies_weight_by_reps():
    raw = {"value": "100", "amount": "5", "valueEmpty": False,
           "amountEmpty": False, "skipped": False}
    assert _set_volume(raw) == 500.0

def test_set_volume_skipped_is_zero():
    raw = {"value": "100", "amount": "5", "valueEmpty": False,
           "amountEmpty": False, "skipped": True}
    assert _set_volume(raw) == 0.0

def test_set_volume_empty_value_is_zero():
    raw = {"value": "", "amount": "5", "valueEmpty": True,
           "amountEmpty": False, "skipped": False}
    assert _set_volume(raw) == 0.0


from boostcamp_mcp.history import _summarize_workout, _full_workout


def _sample_workout():
    return {
        "date": "2026-06-10",
        "name": "Dave Minimum Dose",
        "title": "Week 7 · Day 1",
        "week": 6, "day": 0,
        "finished_at": "2026-06-10 21:08:23",
        "records": [
            {"name": "Squat (Barbell)", "type": "Barbell",
             "muscles_list": [{"muscle": "Quadriceps", "percent": "100%"}],
             "sets": [
                 {"value": "120", "amount": "10", "valueEmpty": False,
                  "amountEmpty": False, "skipped": False, "intensity": [3, 4],
                  "target": 10, "target_type": "reps", "weight_unit": "lbs"},
                 {"value": "120", "amount": "8", "valueEmpty": False,
                  "amountEmpty": False, "skipped": True, "intensity": [],
                  "target": 10, "target_type": "reps", "weight_unit": "lbs"},
             ]},
            {"name": "Bench Press (Barbell)", "type": "Barbell",
             "muscles_list": [], "sets": [
                 {"value": "80", "amount": "5", "valueEmpty": False,
                  "amountEmpty": False, "skipped": False, "intensity": [],
                  "target": 5, "target_type": "reps", "weight_unit": "lbs"},
             ]},
        ],
    }


def test_summarize_workout_shape():
    out = _summarize_workout(_sample_workout())
    assert out == {
        "date": "2026-06-10",
        "title": "Week 7 · Day 1",
        "program_name": "Dave Minimum Dose",
        "week": 6, "day": 0,
        "finished_at": "2026-06-10 21:08:23",
        "exercise_count": 2,
        "exercises": ["Squat (Barbell)", "Bench Press (Barbell)"],
        "total_volume": 1600.0,   # 120*10 (skipped set excluded) + 80*5
        "volume_unit": "lbs",
    }


def test_full_workout_includes_slimmed_records():
    out = _full_workout(_sample_workout())
    # carries summary fields
    assert out["program_name"] == "Dave Minimum Dose"
    assert out["total_volume"] == 1600.0
    # plus records with slimmed sets
    assert [r["name"] for r in out["records"]] == [
        "Squat (Barbell)", "Bench Press (Barbell)"]
    first_set = out["records"][0]["sets"][0]
    assert first_set == {
        "weight": 120.0, "reps": 10.0, "target": 10, "target_type": "reps",
        "rpe": [3, 4], "skipped": False, "weight_unit": "lbs",
    }
    assert out["records"][0]["muscles_list"] == [
        {"muscle": "Quadriceps", "percent": "100%"}]


def test_summarize_empty_records():
    w = {"date": "2026-01-01", "name": "P", "title": "T", "week": 0,
         "day": 0, "finished_at": "", "records": []}
    out = _summarize_workout(w)
    assert out["exercise_count"] == 0
    assert out["exercises"] == []
    assert out["total_volume"] == 0.0
    assert out["volume_unit"] is None


from boostcamp_mcp.history import _flatten, _filter_by_date


def _raw():
    return {"data": {
        "2026-06-10": [{"name": "P", "title": "newer", "records": []}],
        "2026-04-07": [{"name": "P", "title": "mid", "records": []}],
        "2023-10-24": [{"name": "P", "title": "older",
                        "finished_at": "2023-10-24 08:00:00", "records": []},
                       {"name": "P", "title": "older-2",
                        "finished_at": "2023-10-24 19:00:00", "records": []}],
    }}


def test_flatten_tags_date_and_sorts_newest_first():
    out = _flatten(_raw())
    assert [w["date"] for w in out] == [
        "2026-06-10", "2026-04-07", "2023-10-24", "2023-10-24"]
    # same-day tie-break: later finished_at first
    same_day = [w for w in out if w["date"] == "2023-10-24"]
    assert [w["title"] for w in same_day] == ["older-2", "older"]


def test_filter_by_date_inclusive_bounds():
    flat = _flatten(_raw())
    assert [w["title"] for w in _filter_by_date(flat, "2026-04-07", None)] == [
        "newer", "mid"]
    assert [w["title"] for w in _filter_by_date(flat, None, "2026-04-07")] == [
        "mid", "older-2", "older"]
    assert [w["title"] for w in
            _filter_by_date(flat, "2026-04-07", "2026-04-07")] == ["mid"]


def test_filter_by_date_none_returns_all():
    flat = _flatten(_raw())
    assert len(_filter_by_date(flat, None, None)) == 4


import pytest
from boostcamp_mcp.history import shape_history, validate_params, SUMMARY_CAP, FULL_CAP


def _raw_many(n):
    data = {}
    for i in range(n):
        # dates 2026-01-01 .. ascending; zero-padded
        date = f"2026-{(i // 28) + 1:02d}-{(i % 28) + 1:02d}"
        data.setdefault(date, []).append(
            {"name": "P", "title": f"w{i}", "records": []})
    return {"data": data}


def test_validate_rejects_bad_date():
    with pytest.raises(ValueError, match="start_date must be YYYY-MM-DD"):
        validate_params("2026/01/01", None, "summary", 1, 10)

def test_validate_rejects_bad_detail():
    with pytest.raises(ValueError, match="detail must be"):
        validate_params(None, None, "verbose", 1, 10)

def test_validate_rejects_nonpositive_paging():
    with pytest.raises(ValueError, match="page must be >= 1"):
        validate_params(None, None, "summary", 0, 10)
    with pytest.raises(ValueError, match="page_size must be >= 1"):
        validate_params(None, None, "summary", 1, 0)

def test_validate_caps_page_size_per_tier():
    # returns the (possibly capped) effective page_size
    assert validate_params(None, None, "summary", 1, 9999) == SUMMARY_CAP
    assert validate_params(None, None, "full", 1, 9999) == FULL_CAP
    # under the cap, page_size is returned unchanged
    assert validate_params(None, None, "summary", 1, 30) == 30


def test_shape_history_default_summary_paginates():
    out = shape_history(_raw_many(60), start_date=None, end_date=None,
                        detail="summary", page=1, page_size=50)
    assert out["pagination"] == {
        "page": 1, "page_size": 50, "total": 60,
        "returned": 50, "has_more": True}
    assert len(out["workouts"]) == 50
    assert out["filters"] == {
        "start_date": None, "end_date": None, "detail": "summary"}
    assert "60 workouts" in out["hint"]
    # summary workouts have no records key
    assert "records" not in out["workouts"][0]

def test_shape_history_page_two():
    out = shape_history(_raw_many(60), start_date=None, end_date=None,
                        detail="summary", page=2, page_size=50)
    assert out["pagination"]["returned"] == 10
    assert out["pagination"]["has_more"] is False

def test_shape_history_page_past_end_is_empty():
    out = shape_history(_raw_many(10), start_date=None, end_date=None,
                        detail="summary", page=5, page_size=50)
    assert out["workouts"] == []
    assert out["pagination"]["has_more"] is False
    assert "page" in out["hint"].lower()

def test_shape_history_full_caps_page_size():
    out = shape_history(_raw_many(60), start_date=None, end_date=None,
                        detail="full", page=1, page_size=9999)
    assert out["pagination"]["page_size"] == FULL_CAP
    assert len(out["workouts"]) == FULL_CAP
    assert "records" in out["workouts"][0]

def test_shape_history_empty_history():
    out = shape_history({"data": {}}, start_date=None, end_date=None,
                        detail="summary", page=1, page_size=50)
    assert out["workouts"] == []
    assert out["pagination"]["total"] == 0
    assert out["pagination"]["has_more"] is False


from boostcamp_mcp.history import _normalize_records


def _superset_workout():
    """A workout mixing a normal lift, a Superset wrapper (no name/sets of its
    own, children in `supersets`), and a skipped bodyweight lift — mirrors the
    real /programs/history shape."""
    return {
        "date": "2026-05-31",
        "name": "P", "title": "Day 1", "week": 1, "day": 0,
        "finished_at": "2026-05-31 10:00:00",
        "records": [
            {"name": "Squat (Barbell)", "type": "Barbell", "muscles_list": [],
             "sets": [{"value": "100", "amount": "5", "valueEmpty": False,
                       "amountEmpty": False, "skipped": False, "intensity": [],
                       "target": 5, "target_type": "reps", "weight_unit": "lbs"}]},
            {"type": "Superset", "uniq": "ss-1", "supersets": [
                {"name": "Incline Bench (Dumbbell)", "type": "Dumbbell",
                 "muscles_list": [{"muscle": "Chest", "percent": "100%"}],
                 "sets": [{"value": "60", "amount": "10", "valueEmpty": False,
                           "amountEmpty": False, "skipped": False, "intensity": [],
                           "target": 10, "target_type": "reps", "weight_unit": "lbs"}]},
                {"name": "Push Up", "type": "Bodyweight", "muscles_list": [],
                 "sets": [{"value": "", "amount": "12", "valueEmpty": False,
                           "amountEmpty": False, "skipped": False, "intensity": [],
                           "target": 12, "target_type": "reps", "weight_unit": "lbs"}]},
            ]},
            {"name": "Pull-Up (Bodyweight)", "type": "Bodyweight", "muscles_list": [],
             "sets": [{"value": "", "amount": "", "valueEmpty": True,
                       "amountEmpty": True, "skipped": True, "intensity": [],
                       "target": 8, "target_type": "reps", "weight_unit": "lbs"}]},
        ],
    }


def test_normalize_records_expands_supersets():
    norm = _normalize_records(_superset_workout()["records"])
    assert [r.get("name") for r in norm] == [
        "Squat (Barbell)", "Incline Bench (Dumbbell)", "Push Up",
        "Pull-Up (Bodyweight)"]
    tagged = {r["name"]: r.get("superset") for r in norm}
    assert tagged["Incline Bench (Dumbbell)"] == "ss-1"
    assert tagged["Push Up"] == "ss-1"
    assert tagged["Squat (Barbell)"] is None
    assert tagged["Pull-Up (Bodyweight)"] is None


def test_normalize_records_passes_through_plain_records():
    plain = [{"name": "Deadlift", "type": "Barbell", "sets": []}]
    assert _normalize_records(plain) == plain


def test_summarize_flattens_supersets_no_null_exercise():
    out = _summarize_workout(_superset_workout())
    assert None not in out["exercises"]
    assert out["exercises"] == [
        "Squat (Barbell)", "Incline Bench (Dumbbell)", "Push Up",
        "Pull-Up (Bodyweight)"]
    assert out["exercise_count"] == 4
    # volume now includes superset children: 100*5 + 60*10; bodyweight/skipped = 0
    assert out["total_volume"] == 1100.0
    # unit resolves even though the only non-superset weighted lift here is the
    # skipped pull-up — sets carry a weight_unit, so it is no longer null
    assert out["volume_unit"] == "lbs"


def test_full_workout_preserves_superset_grouping():
    out = _full_workout(_superset_workout())
    by_name = {r["name"]: r for r in out["records"]}
    assert by_name["Incline Bench (Dumbbell)"]["superset"] == "ss-1"
    assert "superset" not in by_name["Squat (Barbell)"]
    assert by_name["Incline Bench (Dumbbell)"]["sets"][0]["weight"] == 60.0


def test_summarize_unitless_workout_stays_null():
    # genuinely no weight_unit anywhere -> volume_unit stays None
    w = {"date": "2026-01-01", "name": "P", "title": "T", "week": 0, "day": 0,
         "finished_at": "", "records": [
            {"name": "Plank", "type": "Bodyweight", "muscles_list": [],
             "sets": [{"value": "", "amount": "60", "valueEmpty": True,
                       "amountEmpty": False, "skipped": False, "intensity": [],
                       "target": 60, "target_type": "seconds", "weight_unit": ""}]}]}
    out = _summarize_workout(w)
    assert out["total_volume"] == 0.0
    assert out["volume_unit"] is None
