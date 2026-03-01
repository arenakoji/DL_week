"""
Learning GPS AI - Core Logic
Heuristic-based skill tracking, weakness detection, and study plan simulation.
"""

from collections import defaultdict


# ─────────────────────────────────────────────
# 1. SKILL STATE AGENT
# ─────────────────────────────────────────────

def update_skill(mastery: float, correct: bool) -> float:
    """Update mastery score based on correctness. Clamp to [0, 1]."""
    delta = 0.05 if correct else -0.07
    return max(0.0, min(1.0, mastery + delta))


def compute_skill_states(performance_data: list[dict]) -> dict[str, float]:
    """
    Process a list of performance events and return mastery per topic.
    Each event: {"topic": str, "correct": bool, "time": int}
    Starts each topic at 0.5 (neutral prior).
    """
    mastery = defaultdict(lambda: 0.5)

    for event in performance_data:
        topic = event["topic"]
        correct = event["correct"]
        mastery[topic] = update_skill(mastery[topic], correct)

    return dict(mastery)


# ─────────────────────────────────────────────
# 2. WEAKNESS DETECTION
# ─────────────────────────────────────────────

def get_weak_topics(skill_states: dict[str, float], n: int = 3) -> list[tuple[str, float]]:
    """Return the bottom n topics sorted by mastery (lowest first)."""
    sorted_topics = sorted(skill_states.items(), key=lambda x: x[1])
    return sorted_topics[:n]


# ─────────────────────────────────────────────
# 3. TIME OPTIMIZER AGENT
# ─────────────────────────────────────────────

def allocate_time(skill_states: dict[str, float], total_minutes: int) -> dict[str, int]:
    """
    Allocate study time proportionally to weakness.
    weight = (1 - mastery) for each topic.
    """
    weights = {topic: (1.0 - mastery) for topic, mastery in skill_states.items()}
    total_weight = sum(weights.values())

    if total_weight == 0:
        # All topics mastered equally — split evenly
        per = total_minutes // len(skill_states)
        return {t: per for t in skill_states}

    allocation = {}
    for topic, weight in weights.items():
        allocation[topic] = round((weight / total_weight) * total_minutes)

    # Fix rounding drift
    diff = total_minutes - sum(allocation.values())
    if diff != 0 and allocation:
        top = max(allocation, key=lambda t: weights[t])
        allocation[top] += diff

    return allocation


# ─────────────────────────────────────────────
# 4. COUNTERFACTUAL SIMULATION ENGINE
# ─────────────────────────────────────────────

def simulate_plan(
    skill_states: dict[str, float],
    weak_topics: list[tuple[str, float]],
    plan: str
) -> dict:
    """
    Simulate 3 study plans and estimate improvement.

    plan: "A" | "B" | "C"

    Plan A – Focus on weakest topic   → gain = 0.15 * (1 - mastery)
    Plan B – Balanced across weak     → gain = 0.10 * (1 - mastery)
    Plan C – Light review             → gain = 0.05 * (1 - mastery)
    """
    gain_factor = {"A": 0.15, "B": 0.10, "C": 0.05}[plan]
    descriptions = {
        "A": "🔥 Deep Focus – Attack your weakest topic hard",
        "B": "⚖️  Balanced – Spread effort across all weak areas",
        "C": "🌿 Light Review – Low effort, sustainable pace",
    }

    if plan == "A":
        # Only work on the single weakest topic
        topics_in_scope = weak_topics[:1]
    elif plan == "B":
        topics_in_scope = weak_topics
    else:  # C
        topics_in_scope = weak_topics  # same topics, lower gain

    improvements = {}
    for topic, mastery in topics_in_scope:
        gain = gain_factor * (1.0 - mastery)
        new_mastery = min(1.0, mastery + gain)
        improvements[topic] = {
            "before": round(mastery * 100, 1),
            "after": round(new_mastery * 100, 1),
            "gain": round(gain * 100, 1),
        }

    avg_gain = round(
        sum(v["gain"] for v in improvements.values()) / max(len(improvements), 1), 1
    )

    burnout_note = {
        "A": "⚠️ High intensity — risk of burnout if overused",
        "B": "✅ Sustainable — good balance of effort and gain",
        "C": "😌 Very sustainable — low burnout risk",
    }[plan]

    return {
        "plan": plan,
        "label": descriptions[plan],
        "improvements": improvements,
        "avg_gain_pct": avg_gain,
        "burnout_note": burnout_note,
    }


def run_all_simulations(
    skill_states: dict[str, float],
    weak_topics: list[tuple[str, float]]
) -> list[dict]:
    """Run Plans A, B, C and return all results."""
    return [simulate_plan(skill_states, weak_topics, p) for p in ["A", "B", "C"]]


# ─────────────────────────────────────────────
# 5. EXPLANATION AGENT (LLM)
# ─────────────────────────────────────────────

def generate_explanation(
    skill_states: dict[str, float],
    weak_topics: list[tuple[str, float]],
    recommended_plan: str,
    api_key: str,
) -> str:
    """
    Call OpenAI to generate a short explanation of the recommended plan.
    Falls back to a heuristic explanation if no API key is provided.
    """
    if not api_key or api_key.strip() == "":
        return _fallback_explanation(skill_states, weak_topics, recommended_plan)

    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)

        weak_str = ", ".join(
            f"{t} (mastery {round(m*100)}%)" for t, m in weak_topics
        )
        skill_str = ", ".join(
            f"{t}: {round(m*100)}%" for t, m in skill_states.items()
        )

        prompt = f"""You are a student learning coach AI.

Student skill levels: {skill_str}
Weakest topics: {weak_str}
Recommended plan: Plan {recommended_plan}

In 2–3 sentences, explain why this study plan was chosen and how it will help the student improve. Be specific, encouraging, and concise."""

        response = client.chat.completions.create(
            model="claude-sonnet-4-20250514",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150,
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        return _fallback_explanation(skill_states, weak_topics, recommended_plan) + f"\n\n_(LLM unavailable: {e})_"


def _fallback_explanation(
    skill_states: dict[str, float],
    weak_topics: list[tuple[str, float]],
    plan: str,
) -> str:
    """Heuristic explanation when no LLM is available."""
    weakest = weak_topics[0][0] if weak_topics else "unknown"
    weakest_pct = round(weak_topics[0][1] * 100) if weak_topics else 0

    explanations = {
        "A": (
            f"Plan A was selected because **{weakest}** has a critically low mastery of {weakest_pct}%. "
            f"Concentrated focus on a single weak point produces the highest marginal gain. "
            f"Once {weakest} improves, the overall performance ceiling rises significantly."
        ),
        "B": (
            f"Plan B was selected to address all weak areas simultaneously. "
            f"With {weakest} at {weakest_pct}% mastery, a balanced approach prevents skill gaps from widening "
            f"while making steady progress across all topics — ideal for well-rounded improvement."
        ),
        "C": (
            f"Plan C was selected for a sustainable, low-intensity review session. "
            f"Rather than risking burnout, light reinforcement of {weakest} and other weak topics "
            f"maintains progress and keeps motivation high for future sessions."
        ),
    }
    return explanations.get(plan, "A study plan was generated based on your current skill levels.")


# ─────────────────────────────────────────────
# SAMPLE DATA
# ─────────────────────────────────────────────

SAMPLE_DATA = [
    {"topic": "integration", "correct": False, "time": 45},
    {"topic": "integration", "correct": False, "time": 50},
    {"topic": "recursion",   "correct": True,  "time": 30},
    {"topic": "recursion",   "correct": True,  "time": 25},
    {"topic": "sorting",     "correct": False, "time": 40},
    {"topic": "sorting",     "correct": True,  "time": 35},
    {"topic": "graphs",      "correct": False, "time": 60},
    {"topic": "graphs",      "correct": False, "time": 55},
    {"topic": "probability", "correct": True,  "time": 20},
    {"topic": "probability", "correct": False, "time": 30},
    {"topic": "linked lists","correct": True,  "time": 15},
    {"topic": "linked lists","correct": True,  "time": 20},
]