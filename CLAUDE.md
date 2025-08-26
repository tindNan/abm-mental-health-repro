# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Interactive agent-based model (ABM) dashboard for simulating mental health transmission among Nairobi youth (ages 15-24). Uses Mesa for ABM, Streamlit for the interactive dashboard, and real research data from research.md.

## Development Commands

All commands use `uv` for package management:

```bash
# Install dependencies
uv pip install -r requirements.txt

# Run the dashboard
uv run python main.py

# Run specific modules
uv run python src/model/model.py
uv run python src/dashboard/app.py

# Install new packages
uv pip install package_name

# Run tests
uv run pytest tests/ -v

# Run with custom parameters
uv run python main.py --config configs/custom_params.yaml
```

## Key Technologies

- **Mesa**: Agent-based modeling framework
- **Streamlit**: Interactive web dashboard
- **Plotly**: Dynamic visualizations
- **NetworkX**: Social network modeling
- **Pandas/NumPy**: Data processing
- **Pydantic**: Parameter validation

## Project Structure

```
/src/
  /model/          # Core ABM components
    agent.py       # YouthAgent class
    model.py       # NairobiModel main simulation
    networks.py    # Network generation
    transmission.py # Mental health transmission logic
    interventions.py # Intervention strategies
  /dashboard/      # Streamlit interface
    app.py         # Main dashboard
    components.py  # UI components
    visualizations.py # Charts and plots
    documentation.py # Parameter docs
  /data/
    parameters.py  # Default values from research
    citations.json # Source citations
/configs/          # Configuration files
/tests/           # Test suite

## Model Parameters (from research.md)

Critical values to maintain:
- Population: 50% in informal settlements
- Mental health: 26% depression, 19.1% anxiety baseline
- Social media: 3.73 hours daily usage
- Treatment access: 2% baseline
- Peer influence: β = 2.13 (strongest factor)
- Loneliness impact: OR = 10.68

## Dashboard Requirements

1. **NetLogo-style controls**: Sliders for all parameters with live updates
2. **Documentation**: Each parameter must show source citation
3. **Visualization**: Spatial grid, network view, time series, statistics
4. **Performance**: Smooth interaction with 1000-5000 agents

## Testing Priorities

1. Validate baseline prevalence matches research (26% depression)
2. Test transmission mechanisms produce realistic spread
3. Verify intervention effects are measurable
4. Ensure dashboard updates smoothly

## Common Issues

- If dashboard is slow, reduce agent count or update frequency
- Network visualization may lag with >2000 agents
- Use batch updates for better performance

## Data Sources

All parameters and ranges come from:
- research.md: Comprehensive Nairobi youth mental health data
- brief.md: ABM methodology overview