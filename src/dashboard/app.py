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


# Helper function to update agent history
def update_agent_history(model, step_count):
    """Track each agent's state over time"""
    if step_count not in st.session_state.agent_history:
        st.session_state.agent_history[step_count] = {}

    for agent in model.schedule.agents:
        st.session_state.agent_history[step_count][agent.unique_id] = {
            "state": agent.mental_state.value,
            "depression": agent.depression_score,
            "anxiety": agent.anxiety_score,
            "seeking_treatment": agent.seeking_treatment,
            "in_school": agent.in_school,
            "in_informal_settlement": agent.in_informal_settlement,
            "age": agent.age,
            "gender": agent.gender,
        }


# Helper function to create agent grid visualization
def create_agent_grid_plot(model, step_count):
    """Create a grid visualization of all agents colored by their mental state"""

    # Get current agent states
    agent_data = []
    state_colors = {
        "healthy": "#2E8B57",  # Sea green
        "at_risk": "#FFD700",  # Gold
        "symptomatic": "#DC143C",  # Crimson
        "recovering": "#4169E1",  # Royal blue
    }

    # Calculate grid dimensions for square-ish layout
    n_agents = len(model.schedule.agents)
    grid_size = int(np.ceil(np.sqrt(n_agents)))

    for i, agent in enumerate(model.schedule.agents):
        row = i // grid_size
        col = i % grid_size

        agent_data.append(
            {
                "agent_id": agent.unique_id,
                "row": row,
                "col": col,
                "state": agent.mental_state.value,
                "color": state_colors[agent.mental_state.value],
                "depression": agent.depression_score,
                "anxiety": agent.anxiety_score,
                "seeking_treatment": agent.seeking_treatment,
                "age": agent.age,
                "gender": agent.gender,
                "in_school": agent.in_school,
                "in_informal_settlement": agent.in_informal_settlement,
                # Add marker size based on treatment seeking
                "size": 12 if agent.seeking_treatment else 8,
            }
        )

    df = pd.DataFrame(agent_data)

    # Create the scatter plot
    fig = px.scatter(
        df,
        x="col",
        y="row",
        color="state",
        color_discrete_map=state_colors,
        size="size",
        size_max=12,
        hover_data=[
            "agent_id",
            "depression",
            "anxiety",
            "age",
            "gender",
            "in_school",
            "seeking_treatment",
        ],
        title=f"Agent States at Tick {step_count} (Click agent to track over time)",
        labels={"col": "", "row": ""},
        height=min(600, max(400, grid_size * 15)),  # Responsive height
    )

    # Customize layout
    fig.update_layout(
        xaxis=dict(showticklabels=False, showgrid=False, zeroline=False),
        yaxis=dict(
            showticklabels=False, showgrid=False, zeroline=False, autorange="reversed"
        ),
        plot_bgcolor="white",
        showlegend=True,
        legend=dict(
            title="Mental Health State",
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
        ),
    )

    # Update traces for better visualization
    fig.update_traces(
        marker=dict(line=dict(width=1, color="DarkSlateGrey"), opacity=0.8),
        hovertemplate="<b>Agent %{customdata[0]}</b><br>"
        + "State: %{color}<br>"
        + "Depression: %{customdata[1]:.2f}<br>"
        + "Anxiety: %{customdata[2]:.2f}<br>"
        + "Age: %{customdata[3]}<br>"
        + "Gender: %{customdata[4]}<br>"
        + "In School: %{customdata[5]}<br>"
        + "Seeking Treatment: %{customdata[6]}<extra></extra>",
    )

    return fig, df


# Helper function to create individual agent timeline
def create_agent_timeline(agent_id, agent_history):
    """Create a timeline showing an individual agent's state changes over time"""

    if not agent_history or agent_id is None:
        return None

    # Extract agent data over time
    timeline_data = []
    state_colors = {
        "healthy": "#2E8B57",  # Sea green
        "at_risk": "#FFD700",  # Gold
        "symptomatic": "#DC143C",  # Crimson
        "recovering": "#4169E1",  # Royal blue
    }

    state_numeric = {"healthy": 0, "at_risk": 1, "symptomatic": 2, "recovering": 1.5}

    for tick in sorted(agent_history.keys()):
        if agent_id in agent_history[tick]:
            agent_data = agent_history[tick][agent_id]
            timeline_data.append(
                {
                    "tick": tick,
                    "state": agent_data["state"],
                    "state_numeric": state_numeric[agent_data["state"]],
                    "depression": agent_data["depression"],
                    "anxiety": agent_data["anxiety"],
                    "seeking_treatment": agent_data["seeking_treatment"],
                }
            )

    if not timeline_data:
        return None

    df = pd.DataFrame(timeline_data)

    # Create the timeline plot
    fig = make_subplots(
        rows=2,
        cols=1,
        subplot_titles=(
            f"Agent {agent_id} Mental Health State Over Time",
            f"Agent {agent_id} Depression & Anxiety Scores",
        ),
        vertical_spacing=0.15,
    )

    # State timeline (top plot)
    for state in ["healthy", "at_risk", "symptomatic", "recovering"]:
        state_data = df[df["state"] == state]
        if len(state_data) > 0:
            fig.add_trace(
                go.Scatter(
                    x=state_data["tick"],
                    y=state_data["state_numeric"],
                    mode="markers+lines",
                    name=state.title(),
                    marker=dict(color=state_colors[state], size=8),
                    line=dict(color=state_colors[state], width=2),
                    connectgaps=False,
                ),
                row=1,
                col=1,
            )

    # Depression and anxiety scores (bottom plot)
    fig.add_trace(
        go.Scatter(
            x=df["tick"],
            y=df["depression"],
            mode="lines+markers",
            name="Depression",
            line=dict(color="red", width=2),
            marker=dict(color="red", size=4),
        ),
        row=2,
        col=1,
    )

    fig.add_trace(
        go.Scatter(
            x=df["tick"],
            y=df["anxiety"],
            mode="lines+markers",
            name="Anxiety",
            line=dict(color="orange", width=2),
            marker=dict(color="orange", size=4),
        ),
        row=2,
        col=1,
    )

    # Add treatment seeking indicators
    treatment_ticks = df[df["seeking_treatment"] == True]["tick"]
    if len(treatment_ticks) > 0:
        fig.add_trace(
            go.Scatter(
                x=treatment_ticks,
                y=[2.5] * len(treatment_ticks),  # Above state plot
                mode="markers",
                name="Seeking Treatment",
                marker=dict(
                    symbol="cross", color="purple", size=12, line=dict(width=2)
                ),
                showlegend=True,
            ),
            row=1,
            col=1,
        )

    # Update layout
    fig.update_layout(
        height=500, title=f"Individual Agent {agent_id} Analysis", showlegend=True
    )

    # Update y-axes
    fig.update_yaxes(
        title_text="Mental Health State",
        ticktext=["Healthy", "At Risk/Recovering", "Symptomatic"],
        tickvals=[0, 1, 2],
        row=1,
        col=1,
    )

    fig.update_yaxes(title_text="Score (0-1)", range=[0, 1], row=2, col=1)

    fig.update_xaxes(title_text="Tick", row=2, col=1)

    return fig


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
    st.session_state.target_ticks = 100
    st.session_state.auto_stop = False
    st.session_state.agent_history = {}  # Track each agent's state over time
    st.session_state.selected_agent = None  # Currently selected agent for detailed view

# Header
st.title("🧠 Agent-Based Model: Mental Health Transmission Among Nairobi Youth")
st.markdown("""
This interactive model simulates how mental health conditions (depression and anxiety) spread through 
social networks among youth aged 15-24 in Nairobi, Kenya. Each dot represents a young person whose 
mental health state changes based on peer interactions, environmental stressors, and protective factors. 
The model uses real data from ~880,000 youth to understand intervention impacts.

**How it works:** Adjust parameters in the sidebar, set your target number of ticks (like NetLogo), 
then click 'Initialize Model' to create the population. Use 'Run Simulation' for real-time visualization, 
'Step Once' for manual control, or 'Run to Target' for fast execution. The tick counter and progress bar 
show simulation progress just like NetLogo's interface.
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

# Simulation Controls
st.subheader("🎮 Simulation Controls")

# Time interval controls
col1, col2, col3 = st.columns([2, 1, 1])
with col1:
    target_ticks = st.selectbox(
        "🕒 Run for how many ticks?",
        [10, 25, 50, 100, 250, 500, 1000, 2000],
        index=3,  # Default to 100
        help="Similar to NetLogo's tick counter - choose how many simulation steps to run",
    )
    st.session_state.target_ticks = target_ticks

with col2:
    auto_stop = st.checkbox(
        "Auto-stop at target",
        value=True,
        help="Automatically pause when reaching the target number of ticks",
    )
    st.session_state.auto_stop = auto_stop

with col3:
    st.metric("Current Tick", st.session_state.step_count, f"/ {target_ticks}")

# Progress bar
if st.session_state.auto_stop and st.session_state.model:
    progress = min(st.session_state.step_count / target_ticks, 1.0)
    st.progress(
        progress,
        text=f"Progress: {st.session_state.step_count}/{target_ticks} ticks ({progress:.1%})",
    )

# Control buttons
col1, col2, col3, col4, col5, col6 = st.columns(6)
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
        st.session_state.agent_history = {}
        st.session_state.selected_agent = None
        # Initialize agent history with tick 0
        update_agent_history(st.session_state.model, 0)
        st.success("Model initialized!")

with col2:
    if st.button("▶️ Run Simulation"):
        if st.session_state.model:
            st.session_state.running = True
        else:
            st.warning("Please initialize model first!")

with col3:
    if st.button("⏸️ Pause"):
        st.session_state.running = False

with col4:
    if st.button("⏭️ Step Once"):
        if st.session_state.model:
            st.session_state.model.step()
            st.session_state.step_count += 1
            update_agent_history(st.session_state.model, st.session_state.step_count)
            st.rerun()
        else:
            st.warning("Please initialize model first!")

with col5:
    if st.button("🔁 Reset"):
        st.session_state.model = None
        st.session_state.history = []
        st.session_state.running = False
        st.session_state.step_count = 0
        st.session_state.agent_history = {}
        st.session_state.selected_agent = None

with col6:
    if st.button("⚡ Run to Target"):
        if st.session_state.model:
            # Run all remaining steps at once (faster)
            remaining = st.session_state.target_ticks - st.session_state.step_count
            if remaining > 0:
                with st.spinner(f"Running {remaining} ticks..."):
                    for _ in range(remaining):
                        st.session_state.model.step()
                        st.session_state.step_count += 1
                        update_agent_history(
                            st.session_state.model, st.session_state.step_count
                        )
                st.success(f"🎯 Completed {remaining} ticks instantly!")
                st.rerun()
            else:
                st.info("Already at target ticks!")
        else:
            st.warning("Please initialize model first!")

# Main visualization area
if st.session_state.model:
    # Run simulation steps if running
    if st.session_state.running:
        # Check if we should auto-stop
        if (
            st.session_state.auto_stop
            and st.session_state.step_count >= st.session_state.target_ticks
        ):
            st.session_state.running = False
            st.success(
                f"🎯 Simulation completed! Reached {st.session_state.target_ticks} ticks."
            )
        else:
            # Run steps (fewer steps if we're close to target)
            remaining_steps = (
                st.session_state.target_ticks - st.session_state.step_count
                if st.session_state.auto_stop
                else 5
            )
            steps_to_run = min(5, remaining_steps) if st.session_state.auto_stop else 5

            if steps_to_run > 0:
                for _ in range(steps_to_run):
                    st.session_state.model.step()
                    st.session_state.step_count += 1
                    # Update agent history after each step
                    update_agent_history(
                        st.session_state.model, st.session_state.step_count
                    )

                    # Check if we've reached the target mid-loop
                    if (
                        st.session_state.auto_stop
                        and st.session_state.step_count >= st.session_state.target_ticks
                    ):
                        st.session_state.running = False
                        st.success(
                            f"🎯 Simulation completed! Reached {st.session_state.target_ticks} ticks."
                        )
                        break

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

    # Agent State Visualization Section
    st.subheader("👥 Individual Agent Visualization")

    # Only show agent grid for reasonable population sizes
    if n_agents <= 2000:
        col1, col2 = st.columns([2, 1])

        with col1:
            # Create and display agent grid
            agent_fig, agent_df = create_agent_grid_plot(
                model, st.session_state.step_count
            )

            # Handle agent selection via click (simulated with selectbox for now)
            with st.expander("🔍 Agent Selection", expanded=False):
                st.markdown(
                    "**Select an agent to track its mental health journey over time:**"
                )

                # Agent selection controls
                col_a, col_b = st.columns(2)
                with col_a:
                    selected_agent_id = st.selectbox(
                        "Choose Agent ID:",
                        options=sorted([a.unique_id for a in model.schedule.agents]),
                        index=0
                        if st.session_state.selected_agent is None
                        else sorted([a.unique_id for a in model.schedule.agents]).index(
                            st.session_state.selected_agent
                        )
                        if st.session_state.selected_agent
                        in [a.unique_id for a in model.schedule.agents]
                        else 0,
                        help="Select an agent to see their individual timeline",
                    )

                with col_b:
                    if st.button("🎯 Track This Agent"):
                        st.session_state.selected_agent = selected_agent_id
                        st.success(f"Now tracking Agent {selected_agent_id}")

                # Random agent selection
                if st.button("🎲 Pick Random Agent"):
                    import random

                    random_agent = random.choice(
                        [a.unique_id for a in model.schedule.agents]
                    )
                    st.session_state.selected_agent = random_agent
                    st.success(f"Now tracking Agent {random_agent}")

            st.plotly_chart(agent_fig, use_container_width=True)

        with col2:
            # Agent state legend and info
            st.markdown("**🎨 State Colors:**")
            st.markdown("""
            - 🟢 **Healthy**: No significant mental health issues
            - 🟡 **At Risk**: Elevated symptoms, vulnerable
            - 🔴 **Symptomatic**: Clinical depression/anxiety levels  
            - 🔵 **Recovering**: In treatment and improving
            """)

            st.markdown("**ℹ️ Visual Guide:**")
            st.markdown("""
            - **Dot Size**: Larger dots = seeking treatment
            - **Hover**: Shows agent details (depression, anxiety, age, etc.)
            - **Layout**: Agents arranged in grid for easy viewing
            """)

            # Performance info
            st.info(
                f"💡 Showing {n_agents} agents. For populations >2000, use smaller sizes for better performance."
            )

    else:
        st.info(
            f"👥 Agent grid visualization disabled for {n_agents} agents (>2000). Reduce population size to see individual agent dots."
        )

    # Individual Agent Timeline
    if st.session_state.selected_agent is not None and st.session_state.agent_history:
        st.subheader(f"📈 Individual Timeline: Agent {st.session_state.selected_agent}")

        # Create timeline plot
        timeline_fig = create_agent_timeline(
            st.session_state.selected_agent, st.session_state.agent_history
        )

        if timeline_fig:
            st.plotly_chart(timeline_fig, use_container_width=True)

            # Agent details
            if st.session_state.selected_agent < len(model.schedule.agents):
                agent = next(
                    (
                        a
                        for a in model.schedule.agents
                        if a.unique_id == st.session_state.selected_agent
                    ),
                    None,
                )
                if agent:
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Current State", agent.mental_state.value.title())
                    with col2:
                        st.metric("Depression", f"{agent.depression_score:.2f}")
                    with col3:
                        st.metric("Anxiety", f"{agent.anxiety_score:.2f}")
                    with col4:
                        st.metric(
                            "In Treatment", "Yes" if agent.seeking_treatment else "No"
                        )
        else:
            st.warning(
                "No timeline data available yet. Run some simulation steps first."
            )

    elif st.session_state.selected_agent is None:
        st.info(
            "👆 Select an agent above to see their individual mental health timeline"
        )

else:
    st.info("👈 Adjust parameters in the sidebar and click 'Initialize Model' to begin")
