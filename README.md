# 🧭 Learning GPS AI

> AI-powered student performance analyzer & personalized study plan generator

---

## 🚀 Quick Start

```bash
# 1. Clone / unzip the project
cd learning_gps

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run
streamlit run app.py
```

Open your browser to: **http://localhost:8501**

---

## 📁 Project Structure

```
learning_gps/
├── app.py              # Streamlit UI (frontend)
├── logic.py            # Core AI logic (backend)
├── requirements.txt    # Python dependencies
└── README.md
```

---

## ✨ Features

| Feature | How it works |
|---|---|
| **Skill State Tracking** | Mastery starts at 0.5. Correct → +0.05, Wrong → -0.07 |
| **Weakness Detection** | Bottom 3 topics by mastery score |
| **Time Allocation** | Proportional to `(1 - mastery)` weight |
| **Plan Simulation** | Plans A/B/C with different gain factors (0.15 / 0.10 / 0.05) |
| **AI Explanation** | OpenAI GPT or built-in heuristic fallback |

---

## 📥 Input Format

```json
[
  {"topic": "integration", "correct": false, "time": 45},
  {"topic": "recursion",   "correct": true,  "time": 30}
]
```

---

## ⚙️ Configuration

- **OpenAI API Key** — Optional. Leave blank for heuristic explanation.
- **Study Time** — Slider: 30–180 minutes
- **Recommended Plan** — Which plan (A/B/C) to explain

---

## 📊 Output Sections

1. **Skill Map** — Visual mastery bars per topic
2. **Weak Topics** — Bottom 3 ranked
3. **Time Allocation** — Minutes per topic
4. **Predicted Outcomes** — Plans A, B, C with % gain
5. **AI Explanation** — Why the chosen plan was recommended
