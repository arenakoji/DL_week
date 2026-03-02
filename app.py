from typing import Any, Dict, List, Tuple

import pandas as pd
import streamlit as st

from logic import (
    SAMPLE_DATA,
    SCENARIO_PRESETS,
    parse_events_json,
    preview_rows,
    run_learning_gps,
    sanitize_events,
    to_json_text,
)

st.set_page_config(page_title="Learning GPS AI", layout="wide")

st.markdown(
    """
    <style>
    .block-container {
        padding-top: 1.2rem;
        padding-bottom: 2rem;
    }
    .plan-card {
        border: 1px solid #d0dae8;
        border-radius: 12px;
        padding: 12px;
        background: linear-gradient(180deg, #f9fbff 0%, #f4f8ff 100%);
        min-height: 160px;
    }
    .plan-card.recommended {
        border: 2px solid #0f766e;
        background: linear-gradient(180deg, #ecfeff 0%, #e6fffa 100%);
        box-shadow: 0 0 0 2px rgba(15, 118, 110, 0.12);
    }
    .plan-title {
        font-size: 1.1rem;
        font-weight: 700;
        margin-bottom: 0.2rem;
    }
    .muted {
        color: #475569;
        font-size: 0.88rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

if "analysis_result" not in st.session_state:
    st.session_state["analysis_result"] = None
if "json_input" not in st.session_state:
    st.session_state["json_input"] = to_json_text(SAMPLE_DATA)

st.title("Learning GPS AI")
st.caption(
    "AI learning copilot with mastery tracking, behavior signals, and counterfactual forecasting of study strategies."
)

st.sidebar.header("Controls")
study_time = st.sidebar.slider("Total study time (minutes)", min_value=30, max_value=180, value=90, step=5)
weak_topics_n = st.sidebar.slider("Number of weak topics", min_value=2, max_value=5, value=3, step=1)
use_sample_data = st.sidebar.checkbox("Use sample data", value=True)
scenario_options = ["Custom JSON"] + list(SCENARIO_PRESETS.keys())
scenario_choice = st.sidebar.selectbox("Demo scenario preset", options=scenario_options, index=0)

if st.sidebar.button("Load preset into JSON"):
    if scenario_choice == "Custom JSON":
        st.sidebar.info("Pick one of the 3 demo scenarios first.")
    else:
        st.session_state["json_input"] = to_json_text(SCENARIO_PRESETS[scenario_choice])

json_text = st.sidebar.text_area("Paste events JSON", key="json_input", height=320)

openai_key = st.sidebar.text_input("OpenAI API key (optional)", type="password")
model_choice = st.sidebar.selectbox(
    "OpenAI model",
    options=["gpt-4o-mini", "gpt-4.1-mini", "gpt-4o"],
    index=0,
)

generate_clicked = st.sidebar.button("Generate Plan", type="primary")


def resolve_input_data(
    use_sample: bool,
    scenario: str,
    raw_json_text: str,
) -> Tuple[List[Dict[str, Any]], List[str], str]:
    if use_sample:
        events, messages = sanitize_events(SAMPLE_DATA)
        return events, messages, "Sample data"

    if scenario != "Custom JSON":
        events, messages = sanitize_events(SCENARIO_PRESETS[scenario])
        return events, messages, scenario

    events, messages = parse_events_json(raw_json_text)
    return events, messages, "Custom JSON"


preview_events, preview_messages, source_label = resolve_input_data(
    use_sample=use_sample_data,
    scenario=scenario_choice,
    raw_json_text=json_text,
)

st.subheader("Input Preview")
st.caption(f"Active source: {source_label}")

if preview_messages:
    st.warning("Validation notes:\n- " + "\n- ".join(preview_messages[:8]))

if preview_events:
    preview_df = pd.DataFrame(preview_rows(preview_events))
    st.dataframe(preview_df, use_container_width=True, hide_index=True)
else:
    st.info("No valid events to preview yet. Add valid JSON or enable sample data.")

if generate_clicked:
    raw_events = preview_rows(preview_events)
    result = run_learning_gps(
        events=raw_events,
        study_minutes=study_time,
        weak_topics_n=weak_topics_n,
        openai_api_key=openai_key.strip() or None,
        model=model_choice,
    )
    st.session_state["analysis_result"] = result

result = st.session_state.get("analysis_result")

if result is None:
    st.info("Click Generate Plan to run mastery modeling, forecasting, and recommendations.")
    st.stop()

if result.get("errors"):
    st.error("\n".join(result["errors"]))

if result.get("validation_messages"):
    with st.expander("Validation details"):
        st.markdown("- " + "\n- ".join(result["validation_messages"]))

skill_states = result.get("skill_states", {})
weak_topics = result.get("weak_topics", [])
time_allocation = result.get("time_allocation", {})
behavior = result.get("behavior", {})
drift = result.get("drift", {})
simulations = result.get("simulations", {})
recommended_plan = result.get("recommended_plan")

st.subheader("1) Skill Map")
if skill_states:
    skill_df = pd.DataFrame(
        [{"topic": topic, "mastery": mastery} for topic, mastery in skill_states.items()]
    ).sort_values("mastery", ascending=True)
    st.bar_chart(skill_df.set_index("topic"))
else:
    st.info("Skill map unavailable. Add valid events and generate again.")

st.subheader("2) Weak Topics")
if weak_topics:
    weak_df = pd.DataFrame(
        [
            {"topic": topic, "mastery": round(mastery, 3), "mastery_pct": f"{mastery * 100:.1f}%"}
            for topic, mastery in weak_topics
        ]
    )
    st.dataframe(weak_df, use_container_width=True, hide_index=True)
else:
    st.info("No weak topic list available.")

st.subheader("3) Time Allocation")
if time_allocation:
    alloc_df = pd.DataFrame(
        [{"topic": topic, "minutes": minutes} for topic, minutes in time_allocation.items()]
    )
    st.dataframe(alloc_df, use_container_width=True, hide_index=True)
else:
    st.info("No allocation generated.")

st.subheader("4) Behavior Insights")
metric_cols = st.columns(3)
metric_cols[0].metric("Fast guess rate", f"{behavior.get('fast_guess_rate', 0) * 100:.1f}%")
metric_cols[1].metric(
    "Late-night error rate",
    f"{behavior.get('late_night_error_rate', 0) * 100:.1f}%",
)
metric_cols[2].metric("Fatigue slope", f"{behavior.get('fatigue_slope', 0):+.2f}")

behavior_notes = behavior.get("notes", ["No behavior notes available."])
st.markdown("- " + "\n- ".join(behavior_notes))
st.info("Tip: " + behavior.get("tip", "No behavior tip available."))

st.subheader("5) Drift / Inactivity")
inactivity_days = drift.get("inactivity_days")
if inactivity_days is None:
    st.metric("Inactivity days", "N/A")
else:
    st.metric("Inactivity days", str(inactivity_days))

if drift.get("inactivity_flag"):
    st.warning("Inactivity flag triggered (>= 7 days between the latest two sessions).")

regression_topics = drift.get("regression_topics", [])
if regression_topics:
    st.markdown("Regression topics: " + ", ".join(regression_topics))
else:
    st.markdown("Regression topics: none")

st.markdown("- " + "\n- ".join(drift.get("notes", ["No drift notes available."])))

st.subheader("6) Predicted Outcomes: Plan A vs B vs C")
st.caption("Counterfactual simulation shows expected mastery gains under each strategy.")

plan_cols = st.columns(3)
for idx, plan_id in enumerate(["A", "B", "C"]):
    plan = simulations.get(plan_id)
    with plan_cols[idx]:
        if not plan:
            st.info(f"Plan {plan_id} unavailable.")
            continue

        card_class = "plan-card recommended" if plan_id == recommended_plan else "plan-card"
        st.markdown(
            (
                f"<div class='{card_class}'>"
                f"<div class='plan-title'>Plan {plan_id}: {plan['name']}</div>"
                f"<div class='muted'>{plan['burnout_note']}</div>"
                f"<div class='muted'>Focus: {', '.join(plan['focus_topics'])}</div>"
                "</div>"
            ),
            unsafe_allow_html=True,
        )

        if plan_id == recommended_plan:
            st.success("Recommended")

        st.metric("Avg gain (focused)", f"{plan['avg_gain_pct']:.2f}%")
        st.metric("Utility", f"{plan.get('utility', 0):.2f}")
        st.caption(
            f"Burnout cost: {plan.get('adjusted_burnout_cost', plan.get('base_burnout_cost', 0)):.3f}"
        )

        breakdown = plan.get("breakdown", [])
        if breakdown:
            breakdown_df = pd.DataFrame(breakdown).rename(
                columns={
                    "topic": "Topic",
                    "before": "Before",
                    "after": "After",
                    "gain_pct": "Gain %",
                }
            )
            st.dataframe(breakdown_df, use_container_width=True, hide_index=True)

st.subheader("7) Explanation")
st.write(result.get("explanation", "No explanation generated."))

st.caption(
    "Forecasting advantage: compare expected gains and burnout-adjusted utility before committing to a study strategy."
)
