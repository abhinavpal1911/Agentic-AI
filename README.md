# Agentic Campaign Optimization Engine

Interactive Streamlit app demonstrating an AI "agent" that analyzes marketing data, finds underperforming segments, rewrites ad copy, and reallocates budget.

Getting started

1. Create a virtual environment and install dependencies:

```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

2. Run the app:

```bash
streamlit run app.py
```
The app automatically generates dummy marketing data and exports it to `data/marketing_data.xlsx` when first run.
Project layout

- `app.py` - Streamlit application entrypoint
- `data/generator.py` - Dummy marketing data generator (exports Excel)
- `utils/metrics.py` - Metric helpers
- `requirements.txt` - Python dependencies

This is an initial scaffold. Continue iterating to add more visuals and polish for the workshop.