import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import json
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from model.model import NairobiModel
from model.agent import MentalHealthState
import networkx as nx

# Page configuration
st.set_page_config(
    page_title="Nairobi Youth Mental Health ABM",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)


# Load citations
@st.cache_data
def load_citations():
    with open("src/data/citations.json", "r") as f:
        return json.load(f)


citations = load_citations()

# Custom CSS for better styling
st.markdown(
    """
    <style>
    .stMetric {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 5px;
    }
    .citation {
        font-size: 0.8em;
        color: #666;
        font-style: italic;
        margin-top: 5px;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# Initialize session state
if "model" not in st.session_state:
    st.session_state.model = None
    st.session_state.history = []
    st.session_state.running = False
    st.session_state.step_count = 0

# Header
st.title("🧠 Agent-Based Model: Mental Health Transmission Among Nairobi Youth")
st.markdown("""
This interactive model simulates how mental health conditions (depression and anxiety) spread through 
social networks among youth aged 15-24 in Nairobi, Kenya. Each dot represents a young person whose 
mental health state changes based on peer interactions, environmental stressors, and protective factors. 
The model uses real data from ~880,000 youth to understand intervention impacts.

**How it works:** Adjust parameters in the sidebar, click 'Initialize Model' to create the population, 
then 'Run Simulation' to watch mental health dynamics unfold. The visualizations update in real-time 
to show the spread and intervention effects.
""")

# Sidebar with parameters
st.sidebar.header("📊 Model Parameters")


# Helper function to display parameter with citation
def param_with_citation(
    label, key, min_val, max_val, default, step, param_key, format_str=None
):
    value = st.sidebar.slider(label, min_val, max_val, default, step, format=format_str)
    if param_key in citations:
        st.sidebar.markdown(
            f"<div class='citation'>{citations[param_key]['citation']}</div>",
            unsafe_allow_html=True,
        )
        with st.sidebar.expander(f"Why this matters"):
            st.write(citations[param_key]["importance"])
    return value


st.sidebar.subheader("Population Settings")
n_agents = param_with_citation(
    "Population Size", "n_agents", 100, 5000, 1000, 100, "population_size"
)

informal_settlement_rate = (
    param_with_citation(
        "% in Informal Settlements",
        "informal_rate",
        30,
        70,
        50,
        5,
        "informal_settlement_rate",
        "%d%%",
    )
    / 100
)

out_of_school_rate = (
    param_with_citation(
        "% Out of School", "out_school", 10, 40, 25, 5, "out_of_school_rate", "%d%%"
    )
    / 100
)

st.sidebar.subheader("Mental Health Baseline")
baseline_depression = (
    param_with_citation(
        "Initial Depression Rate",
        "depression",
        15,
        35,
        26,
        1,
        "baseline_depression_rate",
        "%d%%",
    )
    / 100
)

baseline_anxiety = (
    param_with_citation(
        "Initial Anxiety Rate",
        "anxiety",
        10,
        30,
        19,
        1,
        "baseline_anxiety_rate",
        "%d%%",
    )
    / 100
)

st.sidebar.subheader("Social Network")
avg_connections = param_with_citation(
    "Avg Social Connections", "connections", 5, 20, 12, 1, "avg_social_connections"
)

social_media_hours = param_with_citation(
    "Daily Social Media Hours",
    "social_media",
    1.0,
    5.0,
    3.73,
    0.1,
    "avg_social_media_hours",
    "%.1f",
)

religious_participation = (
    param_with_citation(
        "Religious Participation Rate",
        "religious",
        40,
        90,
        70,
        5,
        "religious_participation_rate",
        "%d%%",
    )
    / 100
)

st.sidebar.subheader("Transmission Dynamics")
peer_influence = param_with_citation(
    "Peer Influence Strength",
    "peer_influence",
    0.5,
    3.0,
    2.13,
    0.1,
    "peer_influence_strength",
    "%.2f",
)

loneliness_factor = param_with_citation(
    "Loneliness Impact Factor",
    "loneliness",
    5.0,
    15.0,
    10.68,
    0.5,
    "loneliness_impact_factor",
    "%.1f",
)

stress_multiplier = param_with_citation(
    "Environmental Stress (Slums)",
    "stress",
    1.0,
    3.0,
    1.5,
    0.1,
    "environmental_stress_multiplier",
    "%.1f",
)

st.sidebar.subheader("Interventions")
st.sidebar.markdown("**Enable interventions to see their impact:**")

digital_intervention = st.sidebar.checkbox(
    "Digital Mental Health Intervention",
    help=citations["digital_intervention"]["importance"],
)

treatment_access = (
    param_with_citation(
        "Treatment Access Rate",
        "treatment",
        2,
        20,
        2,
        1,
        "treatment_access_rate",
        "%d%%",
    )
    / 100
)

peer_support_coverage = (
    param_with_citation(
        "Peer Support Program Coverage",
        "peer_support",
        0,
        50,
        0,
        5,
        "peer_support_coverage",
        "%d%%",
    )
    / 100
)

# Control buttons
col1, col2, col3, col4 = st.columns(4)
with col1:
    if st.button("🔄 Initialize Model", type="primary"):
        st.session_state.model = NairobiModel(
            n_agents=n_agents,
            informal_settlement_rate=informal_settlement_rate,
            baseline_depression_rate=baseline_depression,
            baseline_anxiety_rate=baseline_anxiety,
            out_of_school_rate=out_of_school_rate,
            avg_social_connections=avg_connections,
            avg_social_media_hours=social_media_hours,
            religious_participation_rate=religious_participation,
            peer_influence_strength=peer_influence,
            loneliness_impact_factor=loneliness_factor,
            treatment_access_rate=treatment_access,
            environmental_stress_multiplier=stress_multiplier,
            digital_intervention_enabled=digital_intervention,
            peer_support_coverage=peer_support_coverage,
        )
        st.session_state.history = []
        st.session_state.step_count = 0
        st.success("Model initialized!")

with col2:
    if st.button("▶️ Run Simulation"):
        st.session_state.running = True

with col3:
    if st.button("⏸️ Pause"):
        st.session_state.running = False

with col4:
    if st.button("🔁 Reset"):
        st.session_state.model = None
        st.session_state.history = []
        st.session_state.running = False
        st.session_state.step_count = 0

# Main visualization area
if st.session_state.model:
    # Run simulation steps if running
    if st.session_state.running:
        for _ in range(5):  # Run 5 steps per update
            st.session_state.model.step()
            st.session_state.step_count += 1
        st.rerun()

    # Create visualizations
    model = st.session_state.model

    # Collect current data
    model.datacollector.collect(model)
    model_data = model.datacollector.get_model_vars_dataframe()

    # Current metrics
    st.subheader(f"📈 Current Status (Step {st.session_state.step_count})")
    col1, col2, col3, col4, col5, col6 = st.columns(6)

    with col1:
        current_depression = model.get_depression_rate()
        delta = (current_depression - baseline_depression) * 100
        st.metric("Depression Rate", f"{current_depression:.1%}", f"{delta:+.1f}%")

    with col2:
        current_anxiety = model.get_anxiety_rate()
        delta = (current_anxiety - baseline_anxiety) * 100
        st.metric("Anxiety Rate", f"{current_anxiety:.1%}", f"{delta:+.1f}%")

    with col3:
        treatment_count = model.get_treatment_seeking_count()
        st.metric(
            "Seeking Treatment", treatment_count, f"{treatment_count / n_agents:.1%}"
        )

    with col4:
        symptomatic = model.get_symptomatic_count()
        st.metric("Symptomatic", symptomatic, f"{symptomatic / n_agents:.1%}")

    with col5:
        at_risk = model.get_at_risk_count()
        st.metric("At Risk", at_risk, f"{at_risk / n_agents:.1%}")

    with col6:
        healthy = model.get_healthy_count()
        st.metric("Healthy", healthy, f"{healthy / n_agents:.1%}")

    # Create 2x2 visualization grid
    fig = make_subplots(
        rows=2,
        cols=2,
        subplot_titles=(
            "Mental Health States Over Time",
            "Current State Distribution",
            "Network Visualization",
            "Depression vs Anxiety Correlation",
        ),
        specs=[
            [{"type": "scatter"}, {"type": "bar"}],
            [{"type": "scatter"}, {"type": "scatter"}],
        ],
    )

    # Plot 1: Time series
    if len(model_data) > 0:
        fig.add_trace(
            go.Scatter(
                x=model_data.index,
                y=model_data["Depression Rate"],
                name="Depression",
                line=dict(color="red"),
            ),
            row=1,
            col=1,
        )
        fig.add_trace(
            go.Scatter(
                x=model_data.index,
                y=model_data["Anxiety Rate"],
                name="Anxiety",
                line=dict(color="orange"),
            ),
            row=1,
            col=1,
        )

    # Plot 2: State distribution
    state_counts = {
        "Healthy": model.get_healthy_count(),
        "At Risk": model.get_at_risk_count(),
        "Symptomatic": model.get_symptomatic_count(),
        "Recovering": model.get_recovering_count(),
    }
    colors = {
        "Healthy": "green",
        "At Risk": "yellow",
        "Symptomatic": "red",
        "Recovering": "blue",
    }

    fig.add_trace(
        go.Bar(
            x=list(state_counts.keys()),
            y=list(state_counts.values()),
            marker_color=[colors[k] for k in state_counts.keys()],
        ),
        row=1,
        col=2,
    )

    # Plot 3: Network visualization (simplified)
    if n_agents <= 500:  # Only show network for small populations
        pos = nx.spring_layout(model.G, k=0.5, iterations=20)
        edge_x = []
        edge_y = []
        for edge in model.G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])

        fig.add_trace(
            go.Scatter(
                x=edge_x,
                y=edge_y,
                mode="lines",
                line=dict(width=0.5, color="#888"),
                hoverinfo="none",
            ),
            row=2,
            col=1,
        )

        node_x = []
        node_y = []
        node_colors = []
        for node in model.G.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)
            agent = model.schedule.agents[node]
            if agent.mental_state == MentalHealthState.HEALTHY:
                node_colors.append("green")
            elif agent.mental_state == MentalHealthState.AT_RISK:
                node_colors.append("yellow")
            elif agent.mental_state == MentalHealthState.SYMPTOMATIC:
                node_colors.append("red")
            else:
                node_colors.append("blue")

        fig.add_trace(
            go.Scatter(
                x=node_x,
                y=node_y,
                mode="markers",
                marker=dict(size=5, color=node_colors),
                hoverinfo="text",
            ),
            row=2,
            col=1,
        )
    else:
        # Show message for large populations
        fig.add_annotation(
            text="Network too large to display<br>(reduce population size to see network)",
            xref="x3",
            yref="y3",
            x=0.5,
            y=0.5,
            showarrow=False,
            row=2,
            col=1,
        )

    # Plot 4: Depression vs Anxiety scatter
    depression_scores = [
        a.depression_score for a in model.schedule.agents[:200]
    ]  # Sample for performance
    anxiety_scores = [a.anxiety_score for a in model.schedule.agents[:200]]

    fig.add_trace(
        go.Scatter(
            x=depression_scores,
            y=anxiety_scores,
            mode="markers",
            marker=dict(size=5, color="purple", opacity=0.5),
        ),
        row=2,
        col=2,
    )

    # Update layout
    fig.update_layout(height=700, showlegend=True)
    fig.update_xaxes(title_text="Step", row=1, col=1)
    fig.update_yaxes(title_text="Rate", row=1, col=1)
    fig.update_xaxes(title_text="State", row=1, col=2)
    fig.update_yaxes(title_text="Count", row=1, col=2)
    fig.update_xaxes(title_text="Depression Score", row=2, col=2)
    fig.update_yaxes(title_text="Anxiety Score", row=2, col=2)

    st.plotly_chart(fig, use_container_width=True)

    # Additional statistics
    st.subheader("📊 Network Statistics")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Network Clustering", f"{model.get_network_clustering():.3f}")

    with col2:
        st.metric("Avg Resilience", f"{model.get_average_resilience():.3f}")

    with col3:
        r0 = model.get_basic_reproduction_number()
        st.metric("R₀ (Reproduction Number)", f"{r0:.2f}")

    with col4:
        treatment_gap = 1 - (treatment_count / symptomatic) if symptomatic > 0 else 0
        st.metric("Treatment Gap", f"{treatment_gap:.1%}")

else:
    st.info("👈 Adjust parameters in the sidebar and click 'Initialize Model' to begin")
