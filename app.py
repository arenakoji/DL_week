"""
Learning GPS AI — Streamlit App
"""

import json
import streamlit as st
from logic import (
    compute_skill_states,
    get_weak_topics,
    allocate_time,
    run_all_simulations,
    generate_explanation,
    SAMPLE_DATA,
)

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Learning GPS AI",
    page_icon="🧭",
    layout="wide",
)

# ─────────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

/* Background */
.stApp {
    background: #0d0f1a;
    color: #e8eaf0;
}

/* Hero Header */
.hero {
    background: linear-gradient(135deg, #1a1d2e 0%, #0d1117 50%, #0f1a2e 100%);
    border: 1px solid #2a2d3e;
    border-radius: 16px;
    padding: 2.5rem 3rem;
    margin-bottom: 2rem;
    position: relative;
    overflow: hidden;
}
.hero::before {
    content: '';
    position: absolute;
    top: -50%;
    right: -20%;
    width: 400px;
    height: 400px;
    background: radial-gradient(circle, rgba(99,179,237,0.08) 0%, transparent 70%);
    pointer-events: none;
}
.hero h1 {
    font-family: 'Space Mono', monospace;
    font-size: 2.4rem;
    font-weight: 700;
    color: #63b3ed;
    margin: 0 0 0.4rem 0;
    letter-spacing: -1px;
}
.hero p {
    color: #8892a4;
    font-size: 1.05rem;
    margin: 0;
}
.hero .badge {
    display: inline-block;
    background: rgba(99,179,237,0.12);
    border: 1px solid rgba(99,179,237,0.3);
    color: #63b3ed;
    padding: 2px 10px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-family: 'Space Mono', monospace;
    margin-bottom: 0.8rem;
}

/* Cards */
.card {
    background: #13162a;
    border: 1px solid #2a2d3e;
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 1rem;
}
.card-title {
    font-family: 'Space Mono', monospace;
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 2px;
    color: #63b3ed;
    margin-bottom: 1rem;
}

/* Weakness items */
.weak-item {
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: #1a1d2e;
    border-left: 3px solid #fc8181;
    border-radius: 0 8px 8px 0;
    padding: 0.7rem 1rem;
    margin-bottom: 0.5rem;
}
.weak-label { font-weight: 600; font-size: 0.95rem; color: #e8eaf0; }
.weak-score { font-family: 'Space Mono', monospace; font-size: 0.85rem; color: #fc8181; }

/* Progress bar */
.prog-wrap { margin-bottom: 0.8rem; }
.prog-label { display: flex; justify-content: space-between; font-size: 0.85rem; margin-bottom: 4px; color: #8892a4; }
.prog-bar-bg { background: #1e2235; border-radius: 99px; height: 8px; }
.prog-bar-fill { height: 8px; border-radius: 99px; transition: width 0.5s ease; }

/* Plan cards */
.plan-card {
    background: #13162a;
    border: 1px solid #2a2d3e;
    border-radius: 12px;
    padding: 1.2rem 1.4rem;
    height: 100%;
}
.plan-card.best {
    border-color: #63b3ed;
    background: linear-gradient(135deg, #13162a, #0f1a2e);
}
.plan-gain {
    font-family: 'Space Mono', monospace;
    font-size: 2rem;
    font-weight: 700;
    margin: 0.5rem 0 0.2rem;
}
.plan-gain.high { color: #68d391; }
.plan-gain.mid  { color: #63b3ed; }
.plan-gain.low  { color: #fbb6ce; }

/* Explanation box */
.explain-box {
    background: linear-gradient(135deg, #0f1a2e, #1a1d2e);
    border: 1px solid rgba(99,179,237,0.3);
    border-radius: 12px;
    padding: 1.5rem;
    color: #c7d2e0;
    line-height: 1.7;
    font-size: 0.97rem;
}

/* Section headers */
h2.section-head {
    font-family: 'Space Mono', monospace;
    font-size: 1rem;
    color: #63b3ed;
    border-bottom: 1px solid #2a2d3e;
    padding-bottom: 0.5rem;
    margin: 1.5rem 0 1rem;
}

/* Streamlit overrides */
.stButton > button {
    background: linear-gradient(135deg, #2563eb, #1d4ed8);
    color: white;
    border: none;
    border-radius: 8px;
    padding: 0.6rem 2rem;
    font-family: 'Space Mono', monospace;
    font-size: 0.85rem;
    letter-spacing: 1px;
    width: 100%;
    cursor: pointer;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #3b82f6, #2563eb);
}
.stTextArea textarea {
    background: #1a1d2e !important;
    color: #e8eaf0 !important;
    border: 1px solid #2a2d3e !important;
    border-radius: 8px !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 0.82rem !important;
}
.stSlider [data-baseweb="slider"] { padding: 0; }
label { color: #8892a4 !important; font-size: 0.85rem !important; }
.stSelectbox div[data-baseweb="select"] {
    background: #1a1d2e !important;
    border-color: #2a2d3e !important;
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# HERO HEADER
# ─────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <div class="badge">🧭 AI-POWERED</div>
  <h1>Learning GPS AI</h1>
  <p>Detect skill gaps → Build your optimal study plan → Predict your improvement</p>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# SIDEBAR — INPUTS
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Configuration")
    
    openai_key = st.text_input(
        "OpenAI API Key (optional)",
        type="password",
        help="Leave blank to use built-in heuristic explanation",
    )
    
    study_time = st.slider(
        "Available study time (minutes)",
        min_value=30,
        max_value=180,
        value=90,
        step=15,
    )

    recommended_plan_choice = st.selectbox(
        "Plan to explain",
        options=["A — Deep Focus", "B — Balanced", "C — Light Review"],
        index=0,
    )
    plan_letter = recommended_plan_choice[0]

    st.markdown("---")
    st.markdown("### 📥 Performance Data")
    
    use_sample = st.checkbox("Use sample data", value=True)

    default_json = json.dumps(SAMPLE_DATA, indent=2)
    raw_input = st.text_area(
        "Or paste JSON below:",
        value=default_json if use_sample else "[]",
        height=300,
    )

    generate_btn = st.button("🚀 GENERATE PLAN")


# ─────────────────────────────────────────────
# MAIN OUTPUT
# ─────────────────────────────────────────────
if generate_btn:
    # Parse input
    try:
        performance_data = json.loads(raw_input)
        if not isinstance(performance_data, list) or len(performance_data) == 0:
            st.error("Please provide a non-empty JSON array of performance events.")
            st.stop()
    except json.JSONDecodeError as e:
        st.error(f"Invalid JSON: {e}")
        st.stop()

    # Run logic
    skill_states = compute_skill_states(performance_data)
    weak_topics  = get_weak_topics(skill_states, n=3)
    time_plan    = allocate_time(skill_states, study_time)
    simulations  = run_all_simulations(skill_states, weak_topics)
    explanation  = generate_explanation(skill_states, weak_topics, plan_letter, openai_key)

    # ── SECTION 1: All Skills + Weak Topics ──────────────────────────────
    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        st.markdown('<h2 class="section-head">📊 Section 1 — Skill Map</h2>', unsafe_allow_html=True)
        
        sorted_skills = sorted(skill_states.items(), key=lambda x: x[1])
        for topic, mastery in sorted_skills:
            pct = round(mastery * 100)
            if pct < 45:
                color, icon = "#fc8181", "🔴"
            elif pct < 65:
                color, icon = "#f6ad55", "🟡"
            else:
                color, icon = "#68d391", "🟢"

            st.markdown(f"""
            <div class="prog-wrap">
                <div class="prog-label">
                    <span>{icon} {topic.title()}</span>
                    <span style="font-family:'Space Mono',monospace;color:{color}">{pct}%</span>
                </div>
                <div class="prog-bar-bg">
                    <div class="prog-bar-fill" style="width:{pct}%;background:{color}"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    with col2:
        st.markdown('<h2 class="section-head">🎯 Section 1 — Weak Topics</h2>', unsafe_allow_html=True)
        
        for i, (topic, mastery) in enumerate(weak_topics):
            rank = ["🥇", "🥈", "🥉"][i] if i < 3 else f"#{i+1}"
            st.markdown(f"""
            <div class="weak-item">
                <span class="weak-label">{rank} {topic.title()}</span>
                <span class="weak-score">{round(mastery*100)}% mastery</span>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<h2 class="section-head">⏱️ Section 2 — Time Allocation</h2>', unsafe_allow_html=True)

        for topic, mins in sorted(time_plan.items(), key=lambda x: -x[1]):
            pct_bar = round((mins / study_time) * 100)
            mastery = skill_states.get(topic, 0.5)
            pct_m   = round(mastery * 100)
            st.markdown(f"""
            <div class="prog-wrap">
                <div class="prog-label">
                    <span>{topic.title()}</span>
                    <span style="font-family:'Space Mono',monospace">{mins} min</span>
                </div>
                <div class="prog-bar-bg">
                    <div class="prog-bar-fill" style="width:{pct_bar}%;background:#63b3ed"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    # ── SECTION 3: Simulated Plans ────────────────────────────────────────
    st.markdown('<h2 class="section-head">🔮 Section 3 — Predicted Outcomes</h2>', unsafe_allow_html=True)

    plan_cols = st.columns(3, gap="medium")
    gain_colors = ["high", "mid", "low"]
    
    for i, (sim, col) in enumerate(zip(simulations, plan_cols)):
        is_best = sim["plan"] == plan_letter
        card_class = "plan-card best" if is_best else "plan-card"
        badge = "⭐ RECOMMENDED" if is_best else ""
        gain_class = gain_colors[i]

        # Build topic breakdown HTML
        breakdown_html = ""
        for topic, data in sim["improvements"].items():
            breakdown_html += f"""
            <div style="display:flex;justify-content:space-between;font-size:0.8rem;padding:4px 0;border-bottom:1px solid #2a2d3e;">
                <span style="color:#8892a4">{topic.title()}</span>
                <span style="font-family:'Space Mono',monospace;color:#68d391">+{data['gain']}%</span>
            </div>"""

        col.markdown(f"""
        <div class="{card_class}">
            <div style="font-size:0.65rem;font-family:'Space Mono',monospace;letter-spacing:2px;color:#63b3ed;margin-bottom:0.3rem">PLAN {sim['plan']} {badge}</div>
            <div style="font-size:0.9rem;font-weight:600;color:#e8eaf0;margin-bottom:0.5rem">{sim['label']}</div>
            <div class="plan-gain {gain_class}">+{sim['avg_gain_pct']}%</div>
            <div style="font-size:0.75rem;color:#8892a4;margin-bottom:1rem">avg. expected gain</div>
            {breakdown_html}
            <div style="margin-top:0.8rem;font-size:0.75rem;color:#8892a4">{sim['burnout_note']}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # ── SECTION 4: Explanation ─────────────────────────────────────────────
    st.markdown('<h2 class="section-head">🤖 Section 4 — AI Explanation</h2>', unsafe_allow_html=True)

    st.markdown(f"""
    <div class="explain-box">
        <div style="font-size:0.7rem;font-family:'Space Mono',monospace;letter-spacing:2px;color:#63b3ed;margin-bottom:0.8rem">
            WHY PLAN {plan_letter}?
        </div>
        {explanation.replace(chr(10), '<br>')}
    </div>
    """, unsafe_allow_html=True)

    # ── Summary stats ──────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    m1, m2, m3, m4 = st.columns(4)
    avg_mastery = round(sum(skill_states.values()) / len(skill_states) * 100, 1)
    best_gain   = max(s["avg_gain_pct"] for s in simulations)
    weakest_pct = round(weak_topics[0][1] * 100) if weak_topics else 0
    
    for metric_col, label, value, color in [
        (m1, "Topics Tracked",    len(skill_states), "#63b3ed"),
        (m2, "Avg Mastery",       f"{avg_mastery}%",   "#f6ad55"),
        (m3, "Weakest Topic",     f"{weakest_pct}%",   "#fc8181"),
        (m4, "Best Plan Gain",    f"+{best_gain}%",    "#68d391"),
    ]:
        metric_col.markdown(f"""
        <div class="card" style="text-align:center">
            <div style="font-size:1.8rem;font-weight:700;color:{color};font-family:'Space Mono',monospace">{value}</div>
            <div style="font-size:0.75rem;color:#8892a4;margin-top:4px">{label}</div>
        </div>
        """, unsafe_allow_html=True)

else:
    # Landing state
    st.markdown("""
    <div style="text-align:center;padding:4rem 2rem;color:#4a5568">
        <div style="font-size:4rem;margin-bottom:1rem">🧭</div>
        <div style="font-family:'Space Mono',monospace;font-size:1rem;color:#63b3ed;margin-bottom:0.5rem">READY TO NAVIGATE</div>
        <div style="color:#8892a4;font-size:0.9rem">Configure your settings in the sidebar, then click <strong style="color:#63b3ed">Generate Plan</strong></div>
    </div>
    """, unsafe_allow_html=True)

    # Show sample data preview
    with st.expander("📋 View Sample Data Format", expanded=False):
        st.code(json.dumps(SAMPLE_DATA[:4], indent=2), language="json")
        st.caption("Full sample includes 12 events across 6 topics.")