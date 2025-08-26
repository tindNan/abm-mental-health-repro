# 🧠 Nairobi Youth Mental Health Agent-Based Model

An interactive simulation dashboard for understanding mental health transmission among youth (ages 15-24) in Nairobi, Kenya. This agent-based model (ABM) uses real research data to simulate how depression and anxiety spread through social networks, test intervention strategies, and track individual agent journeys over time.

## 🎯 Purpose

This model helps researchers, policymakers, and public health officials:
- Understand how mental health conditions spread through youth social networks
- Test intervention strategies before real-world implementation
- Identify key factors that influence mental health transmission
- Visualize the impact of improving treatment access and peer support programs

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- `uv` package manager (recommended) or `pip`

### Installation with uv (Recommended)

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv pip install -r requirements.txt

# Run the dashboard
uv run python main.py
```

### Installation with pip

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the dashboard
python main.py
```

The dashboard will open automatically in your browser at `http://localhost:8501`

## 📊 How to Use the Dashboard

### 1. **Set Parameters** (Left Sidebar)
Each parameter includes:
- A slider to adjust the value
- Citation from research data
- "Why this matters" explanation

Key parameters include:
- **Population Size**: Number of agents (100-5000)
- **Informal Settlement Rate**: % living in slums (default: 50%)
- **Depression/Anxiety Baseline**: Initial prevalence rates
- **Social Connections**: Average network size
- **Peer Influence Strength**: How much peers affect mental health

### 2. **Set Simulation Length** (NetLogo-style)
Choose how many ticks (simulation steps) to run:
- **Tick Options**: 10, 25, 50, 100, 250, 500, 1000, 2000
- **Auto-stop**: Automatically pause when reaching target ticks
- **Progress Bar**: Visual progress tracking

### 3. **Initialize the Model**
Click "🔄 Initialize Model" to create the population with your selected parameters.

### 4. **Run the Simulation**
Multiple control options available:
- **▶️ Run Simulation**: Start real-time simulation with visual updates
- **⏸️ Pause**: Stop and examine current state  
- **⏭️ Step Once**: Advance by exactly one tick
- **⚡ Run to Target**: Execute all remaining ticks instantly (fast)
- **🔁 Reset**: Start over with new parameters

The current tick counter shows progress like NetLogo's interface.

### 5. **Interpret the Results**
The dashboard shows multiple synchronized visualizations:

**Population-Level Analysis:**
1. **Time Series**: Depression and anxiety rates over time
2. **State Distribution**: Current count of healthy, at-risk, symptomatic, and recovering agents
3. **Network View**: Social connections colored by mental health state (for small populations)
4. **Correlation Plot**: Relationship between depression and anxiety scores

**Individual Agent Analysis (NEW!):**
5. **Agent Grid**: Every agent as a colored dot showing their mental health state
   - 🟢 Healthy, 🟡 At Risk, 🔴 Symptomatic, 🔵 Recovering
   - Larger dots = seeking treatment
   - Hover for detailed agent information
   - Available for populations ≤2000 (performance optimized)
6. **Individual Timelines**: Track selected agents over time
   - **Agent Selection**: Choose specific agents or pick random ones
   - **State History**: See how agents transition between mental health states
   - **Score Evolution**: Depression/anxiety levels over time
   - **Treatment Tracking**: Purple crosses show when seeking treatment
   - **Current Status**: Real-time metrics for selected agent

Metrics display:
- Current vs baseline rates
- Number seeking treatment
- Network clustering coefficient
- R₀ (reproduction number) for mental health transmission
- Treatment gap percentage

## 🎮 Testing Interventions

### Digital Mental Health Intervention
- Enable to reach youth through social media
- Targets the 3.73 hours daily they spend on platforms
- Increases treatment-seeking behavior

### Improve Treatment Access
- Slide from baseline 2% up to 20%
- Models impact of adding mental health services
- Shows how reducing barriers affects outcomes

### Peer Support Programs
- Coverage from 0-50% of population
- Leverages natural social networks
- Based on strongest protective factor (β = 2.13)

## 📈 Understanding the Model

### Agent States
Each youth agent can be in one of four states:
- 🟢 **Healthy**: No significant mental health issues
- 🟡 **At Risk**: Elevated symptoms, vulnerable to progression
- 🔴 **Symptomatic**: Clinical levels of depression/anxiety
- 🔵 **Recovering**: In treatment and improving

### Transmission Mechanisms
Mental health spreads through:
1. **Peer Influence**: Friends affect each other's mental health
2. **Environmental Stress**: Living conditions impact vulnerability
3. **Social Media**: Digital connections create additional pathways
4. **Loneliness**: Strongest individual risk factor (OR = 10.68)

### Protective Factors
- Religious participation (70% attend weekly)
- Family support
- Peer support networks
- Access to treatment

## 📚 Research Foundation

This model is based on comprehensive research data from Nairobi youth:
- Population: ~880,000 youth aged 15-24
- Mental Health: 26% depression, 19.1% anxiety prevalence
- Treatment Gap: 98% receive no formal mental health services
- Living Conditions: 50% in informal settlements
- Digital Usage: Highest global social media use (3h 43min daily)

See `research.md` for detailed data and citations.

## 🏗️ Project Structure

```
├── src/
│   ├── model/           # Core ABM components
│   │   ├── agent.py     # Youth agent behaviors
│   │   └── model.py     # Main simulation logic
│   ├── dashboard/       # Streamlit interface
│   │   └── app.py       # Interactive dashboard
│   └── data/           
│       └── citations.json # Parameter documentation
├── main.py              # Entry point
├── requirements.txt     # Dependencies
├── research.md          # Detailed research data
├── brief.md            # ABM methodology overview
└── CLAUDE.md           # Development guide
```

## 🔧 Customization

### Adjusting Model Parameters
Edit default values in `src/model/model.py`:
```python
baseline_depression_rate=0.26  # 26% from research
peer_influence_strength=2.13   # β coefficient from study
```

### Adding New Interventions
Extend `src/model/model.py`:
```python
def apply_custom_intervention(self):
    # Your intervention logic here
    pass
```

## 📖 Citation

If you use this model in your research, please cite:
```
Agent-Based Model of Mental Health Transmission Among Nairobi Youth
https://github.com/[your-repo]
Based on research data from Nairobi, Kenya (2024)
```

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- Additional intervention strategies
- Performance optimization for larger populations
- More detailed agent behaviors
- Validation against longitudinal data

## 📝 License

MIT License - See LICENSE file for details

## 🙏 Acknowledgments

This model uses real data from mental health research conducted among Nairobi youth. Special thanks to the researchers who collected and analyzed this critical data to understand youth mental health in urban African contexts.

---

**Need Help?** Open an issue or consult the `CLAUDE.md` file for development guidance.