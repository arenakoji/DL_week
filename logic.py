from __future__ import annotations

import json
from collections import defaultdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

SAMPLE_DATA: List[Dict[str, Any]] = [
    {"topic": "integration", "correct": True, "time": 58, "ts": "2026-02-10T19:30:00"},
    {"topic": "probability", "correct": False, "time": 15, "ts": "2026-02-10T21:35:00"},
    {"topic": "trigonometry", "correct": False, "time": 18, "ts": "2026-02-10T21:50:00"},
    {"topic": "derivatives", "correct": True, "time": 42, "ts": "2026-02-11T20:10:00"},
    {"topic": "linear_algebra", "correct": False, "time": 55, "ts": "2026-02-11T20:20:00"},
    {"topic": "geometry", "correct": False, "time": 17, "ts": "2026-02-11T22:05:00"},
    {"topic": "integration", "correct": False, "time": 33, "ts": "2026-02-12T18:00:00"},
    {"topic": "probability", "correct": True, "time": 49, "ts": "2026-02-20T19:00:00"},
    {"topic": "derivatives", "correct": False, "time": 24, "ts": "2026-02-20T19:20:00"},
    {"topic": "geometry", "correct": False, "time": 16, "ts": "2026-02-20T22:15:00"},
    {"topic": "linear_algebra", "correct": True, "time": 63, "ts": "2026-02-28T18:40:00"},
    {"topic": "trigonometry", "correct": False, "time": 14, "ts": "2026-02-28T21:20:00"},
]

SCENARIO_PRESETS: Dict[str, List[Dict[str, Any]]] = {
    "Exam Week (High Gain Needed)": [
        {"topic": "integration", "correct": False, "time": 44, "ts": "2026-02-22T18:10:00"},
        {"topic": "probability", "correct": False, "time": 39, "ts": "2026-02-22T18:25:00"},
        {"topic": "derivatives", "correct": True, "time": 46, "ts": "2026-02-22T18:40:00"},
        {"topic": "linear_algebra", "correct": False, "time": 52, "ts": "2026-02-22T19:00:00"},
        {"topic": "trigonometry", "correct": False, "time": 41, "ts": "2026-02-22T19:15:00"},
        {"topic": "geometry", "correct": True, "time": 55, "ts": "2026-02-22T19:30:00"},
        {"topic": "integration", "correct": False, "time": 36, "ts": "2026-02-23T18:00:00"},
        {"topic": "probability", "correct": False, "time": 33, "ts": "2026-02-23T18:15:00"},
        {"topic": "derivatives", "correct": True, "time": 47, "ts": "2026-02-23T18:40:00"},
        {"topic": "linear_algebra", "correct": False, "time": 48, "ts": "2026-02-23T19:00:00"},
        {"topic": "trigonometry", "correct": True, "time": 43, "ts": "2026-02-23T19:15:00"},
        {"topic": "geometry", "correct": False, "time": 50, "ts": "2026-02-23T19:35:00"},
    ],
    "Burnout Risk (Fatigue Detected)": [
        {"topic": "integration", "correct": True, "time": 48, "ts": "2026-02-24T18:00:00"},
        {"topic": "probability", "correct": True, "time": 52, "ts": "2026-02-24T18:20:00"},
        {"topic": "derivatives", "correct": True, "time": 46, "ts": "2026-02-24T18:40:00"},
        {"topic": "geometry", "correct": False, "time": 32, "ts": "2026-02-24T19:00:00"},
        {"topic": "trigonometry", "correct": True, "time": 44, "ts": "2026-02-24T19:20:00"},
        {"topic": "linear_algebra", "correct": True, "time": 49, "ts": "2026-02-24T19:40:00"},
        {"topic": "integration", "correct": False, "time": 18, "ts": "2026-02-24T21:15:00"},
        {"topic": "probability", "correct": False, "time": 14, "ts": "2026-02-24T21:30:00"},
        {"topic": "derivatives", "correct": False, "time": 16, "ts": "2026-02-24T21:45:00"},
        {"topic": "geometry", "correct": False, "time": 13, "ts": "2026-02-24T22:05:00"},
        {"topic": "trigonometry", "correct": False, "time": 15, "ts": "2026-02-24T22:20:00"},
        {"topic": "linear_algebra", "correct": False, "time": 12, "ts": "2026-02-24T22:35:00"},
    ],
    "Long Gap Return (Inactivity)": [
        {"topic": "integration", "correct": True, "time": 56, "ts": "2026-01-28T18:00:00"},
        {"topic": "probability", "correct": False, "time": 45, "ts": "2026-01-28T18:20:00"},
        {"topic": "derivatives", "correct": True, "time": 54, "ts": "2026-01-28T18:40:00"},
        {"topic": "geometry", "correct": False, "time": 38, "ts": "2026-01-28T19:00:00"},
        {"topic": "trigonometry", "correct": True, "time": 51, "ts": "2026-01-28T19:20:00"},
        {"topic": "linear_algebra", "correct": False, "time": 47, "ts": "2026-01-28T19:40:00"},
        {"topic": "integration", "correct": False, "time": 36, "ts": "2026-02-09T18:00:00"},
        {"topic": "probability", "correct": False, "time": 34, "ts": "2026-02-09T18:15:00"},
        {"topic": "derivatives", "correct": True, "time": 50, "ts": "2026-02-09T18:35:00"},
        {"topic": "geometry", "correct": False, "time": 30, "ts": "2026-02-09T18:55:00"},
        {"topic": "trigonometry", "correct": False, "time": 32, "ts": "2026-02-09T19:15:00"},
        {"topic": "linear_algebra", "correct": True, "time": 53, "ts": "2026-02-09T19:35:00"},
    ],
}

PLAN_CONFIGS: Dict[str, Dict[str, Any]] = {
    "A": {
        "name": "Deep Focus",
        "gain_factor": 0.15,
        "base_burnout_cost": 0.35,
        "intensity_factor": 1.0,
        "burnout_note": "High intensity; best for urgent catch-up.",
    },
    "B": {
        "name": "Balanced",
        "gain_factor": 0.10,
        "base_burnout_cost": 0.18,
        "intensity_factor": 0.7,
        "burnout_note": "Balanced growth with moderate effort.",
    },
    "C": {
        "name": "Light Review",
        "gain_factor": 0.05,
        "base_burnout_cost": 0.08,
        "intensity_factor": 0.4,
        "burnout_note": "Lowest burnout risk; gradual improvement.",
    },
}


def _clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def _rate(part: int, whole: int) -> float:
    if whole <= 0:
        return 0.0
    return part / whole


def _parse_timestamp(ts_value: Any) -> Optional[datetime]:
    if not isinstance(ts_value, str) or not ts_value.strip():
        return None
    candidate = ts_value.strip().replace("Z", "+00:00")
    try:
        dt = datetime.fromisoformat(candidate)
        if dt.tzinfo is not None:
            dt = dt.astimezone(timezone.utc).replace(tzinfo=None)
        return dt
    except ValueError:
        return None


def to_json_text(events: List[Dict[str, Any]]) -> str:
    return json.dumps(events, indent=2)


def sanitize_events(raw_events: Any) -> Tuple[List[Dict[str, Any]], List[str]]:
    issues: List[str] = []
    clean_events: List[Dict[str, Any]] = []

    if not isinstance(raw_events, list):
        return [], ["Input must be a JSON array of events."]

    for idx, event in enumerate(raw_events):
        event_idx = idx + 1
        if not isinstance(event, dict):
            issues.append(f"Event {event_idx}: expected an object; skipped.")
            continue

        topic = str(event.get("topic", "")).strip()
        if not topic:
            issues.append(f"Event {event_idx}: missing topic; skipped.")
            continue

        correct_raw = event.get("correct")
        if isinstance(correct_raw, bool):
            correct = correct_raw
        elif isinstance(correct_raw, int) and correct_raw in (0, 1):
            correct = bool(correct_raw)
            issues.append(f"Event {event_idx}: coerced numeric correct value to boolean.")
        elif isinstance(correct_raw, str) and correct_raw.lower() in {"true", "false"}:
            correct = correct_raw.lower() == "true"
            issues.append(f"Event {event_idx}: coerced string correct value to boolean.")
        else:
            issues.append(f"Event {event_idx}: invalid correct value; skipped.")
            continue

        time_raw = event.get("time")
        time_seconds: Optional[float] = None
        if time_raw is None:
            time_seconds = None
        elif isinstance(time_raw, (int, float)) and float(time_raw) > 0:
            time_seconds = float(time_raw)
        else:
            issues.append(f"Event {event_idx}: invalid time value ignored.")

        ts_raw = event.get("ts")
        parsed_ts = _parse_timestamp(ts_raw)
        ts_clean: Optional[str] = None
        if ts_raw is None:
            ts_clean = None
        elif parsed_ts is None:
            issues.append(f"Event {event_idx}: invalid timestamp ignored.")
            ts_clean = None
        else:
            ts_clean = parsed_ts.isoformat(timespec="seconds")

        clean_events.append(
            {
                "topic": topic,
                "correct": correct,
                "time": time_seconds,
                "ts": ts_clean,
                "dt": parsed_ts,
            }
        )

    return clean_events, issues


def parse_events_json(json_text: str) -> Tuple[List[Dict[str, Any]], List[str]]:
    if not json_text or not json_text.strip():
        return [], ["Input JSON is empty."]

    try:
        parsed = json.loads(json_text)
    except json.JSONDecodeError as exc:
        return [], [f"Invalid JSON: {exc.msg} (line {exc.lineno}, col {exc.colno})."]

    return sanitize_events(parsed)


def preview_rows(events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for event in events:
        rows.append(
            {
                "topic": event.get("topic"),
                "correct": event.get("correct"),
                "time": event.get("time"),
                "ts": event.get("ts"),
            }
        )
    return rows


def _ordered_events(events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    if not any(event.get("dt") for event in events):
        return list(events)
    return sorted(events, key=lambda e: (e.get("dt") is None, e.get("dt") or datetime.max))


def compute_skill_states(events: List[Dict[str, Any]]) -> Dict[str, float]:
    if not events:
        return {}

    mastery: Dict[str, float] = {}
    ordered = _ordered_events(events)

    for event in ordered:
        for topic in list(mastery.keys()):
            mastery[topic] = _clamp(mastery[topic] * 0.99)

        topic = event["topic"]
        if topic not in mastery:
            mastery[topic] = 0.5

        delta = 0.05 if event["correct"] else -0.07
        mastery[topic] = _clamp(mastery[topic] + delta)

    return dict(sorted(mastery.items(), key=lambda item: item[0]))


def detect_weak_topics(skill_states: Dict[str, float], n: int = 3) -> List[Tuple[str, float]]:
    if not skill_states:
        return []
    n = max(1, int(n))
    sorted_topics = sorted(skill_states.items(), key=lambda item: (item[1], item[0]))
    return sorted_topics[:n]


def allocate_study_time(
    skill_states: Dict[str, float],
    weak_topics: List[Tuple[str, float]],
    total_minutes: int,
) -> Dict[str, int]:
    total_minutes = max(0, int(total_minutes))
    if total_minutes == 0 or not skill_states:
        return {}

    focus_topics = [topic for topic, _ in weak_topics] or list(skill_states.keys())
    weights = {topic: max(0.01, 1.0 - skill_states.get(topic, 0.5)) for topic in focus_topics}
    weight_sum = sum(weights.values())

    if weight_sum <= 0:
        equal = total_minutes // len(focus_topics)
        allocation = {topic: equal for topic in focus_topics}
        remainder = total_minutes - sum(allocation.values())
        for topic in focus_topics[:remainder]:
            allocation[topic] += 1
        return allocation

    raw_alloc = {topic: total_minutes * (weight / weight_sum) for topic, weight in weights.items()}
    allocation = {topic: int(value) for topic, value in raw_alloc.items()}
    remainder = total_minutes - sum(allocation.values())

    if remainder > 0:
        ranked = sorted(
            focus_topics,
            key=lambda topic: (raw_alloc[topic] - allocation[topic], weights[topic]),
            reverse=True,
        )
        for i in range(remainder):
            allocation[ranked[i % len(ranked)]] += 1

    return dict(sorted(allocation.items(), key=lambda item: item[1], reverse=True))


def behavior_agent(events: List[Dict[str, Any]]) -> Dict[str, Any]:
    if not events:
        return {
            "fast_guess_rate": 0.0,
            "late_night_error_rate": 0.0,
            "fatigue_slope": 0.0,
            "first_half_accuracy": 0.0,
            "second_half_accuracy": 0.0,
            "notes": ["No events available to infer behavior patterns."],
            "tip": "Add at least 6 events with time and timestamp fields for richer behavior signals.",
        }

    timed_events = [event for event in events if event.get("time") is not None]
    fast_guess_count = sum(
        1
        for event in timed_events
        if event.get("time") is not None and event["time"] < 20 and not event["correct"]
    )
    fast_guess_rate = _rate(fast_guess_count, len(timed_events))

    timestamped_errors = [
        event for event in events if (event.get("dt") is not None and not event["correct"])
    ]
    late_night_errors = sum(1 for event in timestamped_errors if event["dt"].hour >= 21)
    late_night_error_rate = _rate(late_night_errors, len(timestamped_errors))

    split_idx = len(events) // 2
    first_half = events[:split_idx] if split_idx > 0 else events
    second_half = events[split_idx:] if split_idx > 0 else events

    first_half_accuracy = _rate(sum(1 for event in first_half if event["correct"]), len(first_half))
    second_half_accuracy = _rate(sum(1 for event in second_half if event["correct"]), len(second_half))
    fatigue_slope = second_half_accuracy - first_half_accuracy

    notes: List[str] = []
    if fast_guess_rate >= 0.25:
        notes.append(
            f"Fast guessing risk: {fast_guess_rate * 100:.1f}% of timed attempts were quick incorrect responses."
        )
    if late_night_error_rate >= 0.35:
        notes.append(
            f"Late-night risk: {late_night_error_rate * 100:.1f}% of timestamped errors happened after 21:00."
        )
    if fatigue_slope <= -0.15:
        notes.append(
            f"Fatigue signal: accuracy dropped from {first_half_accuracy * 100:.1f}% to {second_half_accuracy * 100:.1f}% later in the sequence."
        )
    if not notes:
        notes.append("Behavior looks stable: no major fast-guessing, late-night, or fatigue red flags.")

    if fatigue_slope <= -0.15:
        tip = "Use 25-minute focus blocks and a 5-minute reset before switching topics."
    elif fast_guess_rate >= 0.25:
        tip = "Add a 10-second pause before submitting answers to reduce impulsive errors."
    elif late_night_error_rate >= 0.35:
        tip = "Move difficult topics to earlier sessions and keep late-night work to light review only."
    else:
        tip = "Keep your current pace and add one short mixed-topic quiz every session."

    return {
        "fast_guess_rate": round(fast_guess_rate, 3),
        "late_night_error_rate": round(late_night_error_rate, 3),
        "fatigue_slope": round(fatigue_slope, 3),
        "first_half_accuracy": round(first_half_accuracy, 3),
        "second_half_accuracy": round(second_half_accuracy, 3),
        "notes": notes[:3],
        "tip": tip,
    }


def drift_inactivity_detector(events: List[Dict[str, Any]]) -> Dict[str, Any]:
    inactivity_days: Optional[int] = None
    session_dates = sorted({event["dt"].date() for event in events if event.get("dt") is not None})

    if len(session_dates) >= 2:
        inactivity_days = (session_dates[-1] - session_dates[-2]).days

    topic_groups: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for event in _ordered_events(events):
        topic_groups[event["topic"]].append(event)

    regression_topics: List[str] = []
    for topic, topic_events in topic_groups.items():
        if len(topic_events) < 6:
            continue
        baseline = topic_events[:-4]
        recent = topic_events[-4:]
        if len(baseline) < 2:
            continue

        baseline_acc = _rate(sum(1 for event in baseline if event["correct"]), len(baseline))
        recent_acc = _rate(sum(1 for event in recent if event["correct"]), len(recent))

        if baseline_acc - recent_acc >= 0.15:
            regression_topics.append(topic)

    notes: List[str] = []
    inactivity_flag = inactivity_days is not None and inactivity_days >= 7

    if inactivity_days is None:
        notes.append("Not enough timestamped sessions to compute inactivity gap.")
    elif inactivity_flag:
        notes.append(f"Inactivity detected: {inactivity_days} days between the two most recent sessions.")
        notes.append("Warm-up advice: start with 10 minutes of mixed recall before deep practice.")
    else:
        notes.append(f"Recent inactivity gap is {inactivity_days} day(s), within a normal range.")

    if regression_topics:
        notes.append("Regression signal in: " + ", ".join(sorted(regression_topics)) + ".")
    else:
        notes.append("No strong topic-level regression in recent attempts.")

    return {
        "inactivity_days": inactivity_days,
        "inactivity_flag": inactivity_flag,
        "regression_topics": sorted(regression_topics),
        "notes": notes,
    }


def _simulate_single_plan(
    plan_id: str,
    skill_states: Dict[str, float],
    focus_topics: List[str],
    gain_factor: float,
) -> Dict[str, Any]:
    improvements: Dict[str, Dict[str, float]] = {}
    focus_set = set(focus_topics)
    focused_gains: List[float] = []

    for topic, before in skill_states.items():
        gain = gain_factor * (1.0 - before) * 0.9 if topic in focus_set else 0.0
        after = _clamp(before + gain)
        gain_pct = (after - before) * 100
        improvements[topic] = {
            "before": round(before, 3),
            "after": round(after, 3),
            "gain_pct": round(gain_pct, 2),
        }
        if topic in focus_set:
            focused_gains.append(gain_pct)

    avg_gain_pct = round(sum(focused_gains) / len(focused_gains), 2) if focused_gains else 0.0
    overall_gain_pct = round(
        sum(item["gain_pct"] for item in improvements.values()) / max(len(improvements), 1),
        2,
    )

    breakdown = [
        {
            "topic": topic,
            "before": values["before"],
            "after": values["after"],
            "gain_pct": values["gain_pct"],
        }
        for topic, values in improvements.items()
        if topic in focus_set
    ]
    breakdown.sort(key=lambda row: row["gain_pct"], reverse=True)

    config = PLAN_CONFIGS[plan_id]
    return {
        "plan_id": plan_id,
        "name": config["name"],
        "focus_topics": focus_topics,
        "gain_factor": gain_factor,
        "avg_gain_pct": avg_gain_pct,
        "overall_gain_pct": overall_gain_pct,
        "burnout_note": config["burnout_note"],
        "base_burnout_cost": config["base_burnout_cost"],
        "breakdown": breakdown,
        "improvements": improvements,
    }


def simulate_study_plans(
    skill_states: Dict[str, float],
    weak_topics: List[Tuple[str, float]],
) -> Dict[str, Dict[str, Any]]:
    if not skill_states:
        return {}

    weak_names = [topic for topic, _ in weak_topics if topic in skill_states]
    if not weak_names:
        weak_names = list(skill_states.keys())[:3]

    plan_focus: Dict[str, List[str]] = {
        "A": weak_names[:1],
        "B": list(weak_names),
        "C": list(weak_names),
    }

    simulations: Dict[str, Dict[str, Any]] = {}
    for plan_id in ("A", "B", "C"):
        config = PLAN_CONFIGS[plan_id]
        focus_topics = plan_focus[plan_id]
        if not focus_topics:
            focus_topics = list(skill_states.keys())
        simulations[plan_id] = _simulate_single_plan(
            plan_id=plan_id,
            skill_states=skill_states,
            focus_topics=focus_topics,
            gain_factor=float(config["gain_factor"]),
        )

    return simulations


def choose_recommended_plan(
    simulations: Dict[str, Dict[str, Any]],
    behavior: Dict[str, Any],
    burnout_weight: float = 25.0,
) -> Tuple[Optional[str], Dict[str, float]]:
    if not simulations:
        return None, {}

    fast_guess_rate = float(behavior.get("fast_guess_rate", 0.0))
    late_night_error_rate = float(behavior.get("late_night_error_rate", 0.0))
    fatigue_penalty = max(0.0, -float(behavior.get("fatigue_slope", 0.0)))

    risk_add = 0.0
    risk_add += min(0.22, fast_guess_rate * 0.60)
    risk_add += min(0.18, late_night_error_rate * 0.45)
    risk_add += min(0.25, fatigue_penalty * 0.90)

    utilities: Dict[str, float] = {}
    for plan_id, plan in simulations.items():
        intensity = float(PLAN_CONFIGS[plan_id]["intensity_factor"])
        adjusted_cost = plan["base_burnout_cost"] + (risk_add * intensity)
        utility = plan["avg_gain_pct"] - burnout_weight * adjusted_cost

        plan["adjusted_burnout_cost"] = round(adjusted_cost, 3)
        plan["utility"] = round(utility, 2)
        utilities[plan_id] = plan["utility"]

    ranked = sorted(
        utilities.keys(),
        key=lambda pid: (utilities[pid], simulations[pid]["avg_gain_pct"]),
        reverse=True,
    )
    return ranked[0], utilities


def deterministic_explanation(
    weak_topics: List[Tuple[str, float]],
    behavior: Dict[str, Any],
    drift: Dict[str, Any],
    recommended_plan: Optional[str],
    simulations: Dict[str, Dict[str, Any]],
    time_allocation: Dict[str, int],
) -> str:
    if not weak_topics:
        return "Not enough valid data to recommend a plan. Add events with topic and correct fields, then generate again."

    weakest_summary = ", ".join(
        f"{topic} ({mastery:.2f})" for topic, mastery in weak_topics[:3]
    )

    plan_text = "No plan available."
    if recommended_plan and recommended_plan in simulations:
        sim = simulations[recommended_plan]
        plan_text = (
            f"Plan {recommended_plan} ({sim['name']}) is selected because it offers "
            f"{sim['avg_gain_pct']:.2f}% focused gain with utility {sim['utility']:.2f}."
        )

    tip = behavior.get("tip", "Keep sessions focused and review weak topics first.")
    if drift.get("inactivity_flag"):
        tip = "After a long gap, start with a 10-minute mixed recall warm-up before deep practice."

    allocation_text = ", ".join(f"{topic}: {mins}m" for topic, mins in time_allocation.items())
    if not allocation_text:
        allocation_text = "no allocation available"

    return (
        f"Weakest topics are {weakest_summary}, so marginal gains are highest there. "
        f"{plan_text} "
        f"Tip: {tip} "
        f"Next action: run today's study block using this split -> {allocation_text}."
    )


def generate_explanation(
    weak_topics: List[Tuple[str, float]],
    behavior: Dict[str, Any],
    drift: Dict[str, Any],
    recommended_plan: Optional[str],
    simulations: Dict[str, Dict[str, Any]],
    time_allocation: Dict[str, int],
    openai_api_key: Optional[str] = None,
    model: str = "gpt-4o-mini",
) -> str:
    fallback = deterministic_explanation(
        weak_topics=weak_topics,
        behavior=behavior,
        drift=drift,
        recommended_plan=recommended_plan,
        simulations=simulations,
        time_allocation=time_allocation,
    )

    if not openai_api_key:
        return fallback

    try:
        from openai import OpenAI

        weak_text = ", ".join(f"{topic}:{mastery:.2f}" for topic, mastery in weak_topics[:3])
        sim = simulations.get(recommended_plan or "", {})

        prompt = (
            "Write 2-4 concise sentences for a student dashboard. "
            "Must include weakest topics with reason, one behavior or drift tip, "
            "and end with a clear next action line.\n"
            f"Weak topics: {weak_text}.\n"
            f"Behavior metrics: fast_guess_rate={behavior.get('fast_guess_rate')}, "
            f"late_night_error_rate={behavior.get('late_night_error_rate')}, "
            f"fatigue_slope={behavior.get('fatigue_slope')}.\n"
            f"Drift: inactivity_days={drift.get('inactivity_days')}, "
            f"regression_topics={drift.get('regression_topics')}.\n"
            f"Recommended plan: {recommended_plan}, avg_gain={sim.get('avg_gain_pct')}, utility={sim.get('utility')}.\n"
            f"Time allocation: {time_allocation}."
        )

        client = OpenAI(api_key=openai_api_key)
        response = client.chat.completions.create(
            model=model,
            temperature=0.3,
            max_tokens=180,
            messages=[
                {
                    "role": "system",
                    "content": "You are a concise learning analytics copilot.",
                },
                {"role": "user", "content": prompt},
            ],
        )

        content = (response.choices[0].message.content or "").strip()
        if content:
            return content
        return fallback + "\n\n(LLM unavailable: empty response)"

    except Exception as exc:
        short_error = str(exc).splitlines()[0][:140]
        return fallback + f"\n\n(LLM unavailable: {short_error})"


def run_learning_gps(
    events: Any,
    study_minutes: int = 90,
    weak_topics_n: int = 3,
    openai_api_key: Optional[str] = None,
    model: str = "gpt-4o-mini",
) -> Dict[str, Any]:
    clean_events, validation_messages = sanitize_events(events)

    result: Dict[str, Any] = {
        "events": clean_events,
        "preview_rows": preview_rows(clean_events),
        "validation_messages": validation_messages,
        "errors": [],
        "skill_states": {},
        "weak_topics": [],
        "time_allocation": {},
        "behavior": behavior_agent(clean_events),
        "drift": drift_inactivity_detector(clean_events),
        "simulations": {},
        "recommended_plan": None,
        "utilities": {},
        "explanation": "",
    }

    if not clean_events:
        result["errors"].append("No valid events available after validation.")
        result["explanation"] = (
            "No recommendation generated. Provide at least one valid event with topic and correct fields."
        )
        return result

    skill_states = compute_skill_states(clean_events)
    weak_topics = detect_weak_topics(skill_states, n=weak_topics_n)
    time_allocation = allocate_study_time(skill_states, weak_topics, total_minutes=study_minutes)

    behavior = behavior_agent(clean_events)
    drift = drift_inactivity_detector(clean_events)

    simulations = simulate_study_plans(skill_states, weak_topics)
    recommended_plan, utilities = choose_recommended_plan(simulations, behavior)

    explanation = generate_explanation(
        weak_topics=weak_topics,
        behavior=behavior,
        drift=drift,
        recommended_plan=recommended_plan,
        simulations=simulations,
        time_allocation=time_allocation,
        openai_api_key=openai_api_key,
        model=model,
    )

    result.update(
        {
            "skill_states": skill_states,
            "weak_topics": weak_topics,
            "time_allocation": time_allocation,
            "behavior": behavior,
            "drift": drift,
            "simulations": simulations,
            "recommended_plan": recommended_plan,
            "utilities": utilities,
            "explanation": explanation,
        }
    )

    return result
