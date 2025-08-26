import pytest
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.model.model import NairobiModel
from src.model.agent import YouthAgent, MentalHealthState


def test_model_initialization():
    """Test that the model initializes with correct parameters."""
    model = NairobiModel(n_agents=100)

    assert model.n_agents == 100
    assert len(model.schedule.agents) == 100
    assert model.baseline_depression_rate == 0.26
    assert model.baseline_anxiety_rate == 0.191
    assert model.peer_influence_strength == 2.13


def test_baseline_prevalence():
    """Test that initial mental health prevalence matches research data."""
    # Run multiple times for statistical validity
    depression_rates = []
    anxiety_rates = []

    for _ in range(10):
        model = NairobiModel(n_agents=1000)
        depression_rate = model.get_depression_rate()
        anxiety_rate = model.get_anxiety_rate()
        depression_rates.append(depression_rate)
        anxiety_rates.append(anxiety_rate)

    avg_depression = sum(depression_rates) / len(depression_rates)
    avg_anxiety = sum(anxiety_rates) / len(anxiety_rates)

    # Check within reasonable range of baseline (allowing for randomness)
    assert 0.20 <= avg_depression <= 0.32, (
        f"Depression rate {avg_depression} outside expected range"
    )
    assert 0.14 <= avg_anxiety <= 0.24, (
        f"Anxiety rate {avg_anxiety} outside expected range"
    )


def test_agent_initialization():
    """Test that agents are initialized with correct properties."""
    model = NairobiModel(n_agents=100)
    agent = model.schedule.agents[0]

    assert 15 <= agent.age <= 24
    assert agent.gender in ["male", "female"]
    assert 0 <= agent.resilience_score <= 1
    assert 0 <= agent.depression_score <= 1
    assert 0 <= agent.anxiety_score <= 1
    assert agent.mental_state in MentalHealthState


def test_social_network_creation():
    """Test that social network has expected properties."""
    model = NairobiModel(n_agents=100, avg_social_connections=10)

    # Check network exists
    assert model.G is not None
    assert model.G.number_of_nodes() == 100

    # Check average degree is close to target
    avg_degree = sum(dict(model.G.degree()).values()) / model.G.number_of_nodes()
    assert 8 <= avg_degree <= 12, f"Average degree {avg_degree} outside expected range"


def test_intervention_effects():
    """Test that interventions have measurable effects."""
    # Model without intervention
    model1 = NairobiModel(
        n_agents=500, treatment_access_rate=0.02, digital_intervention_enabled=False
    )

    # Model with intervention
    model2 = NairobiModel(
        n_agents=500,
        treatment_access_rate=0.10,  # Increased access
        digital_intervention_enabled=True,
    )

    # Run simulations
    for _ in range(20):
        model1.step()
        model2.step()

    # Check that intervention model has more treatment seekers
    seekers1 = model1.get_treatment_seeking_count()
    seekers2 = model2.get_treatment_seeking_count()

    assert seekers2 >= seekers1, "Intervention should increase treatment seeking"


def test_peer_influence():
    """Test that peer influence affects agent mental health."""
    model = NairobiModel(n_agents=100, peer_influence_strength=2.13)

    # Get an agent and make all their connections symptomatic
    agent = model.schedule.agents[0]
    initial_depression = agent.depression_score

    for neighbor_id in agent.social_connections[:5]:
        neighbor = model.schedule.agents[neighbor_id]
        neighbor.mental_state = MentalHealthState.SYMPTOMATIC
        neighbor.depression_score = 0.8

    # Run a few steps
    for _ in range(5):
        agent.step()

    # Check that agent's mental health was influenced
    # (May not always increase due to protective factors, but should change)
    assert agent.depression_score != initial_depression, (
        "Peer influence should affect mental health"
    )


def test_treatment_reduces_symptoms():
    """Test that treatment reduces depression and anxiety scores."""
    model = NairobiModel(n_agents=100)

    # Create a symptomatic agent in treatment
    agent = model.schedule.agents[0]
    agent.mental_state = MentalHealthState.SYMPTOMATIC
    agent.depression_score = 0.8
    agent.anxiety_score = 0.7
    agent.seeking_treatment = True

    initial_depression = agent.depression_score
    initial_anxiety = agent.anxiety_score

    # Simulate treatment duration
    for _ in range(15):
        agent.apply_treatment_effects()
        agent.treatment_duration += 1

    # Check that symptoms reduced
    assert agent.depression_score < initial_depression, (
        "Treatment should reduce depression"
    )
    assert agent.anxiety_score < initial_anxiety, "Treatment should reduce anxiety"


def test_model_data_collection():
    """Test that data collection works correctly."""
    model = NairobiModel(n_agents=100)

    # Run simulation
    for _ in range(10):
        model.step()

    # Check data was collected
    model_data = model.datacollector.get_model_vars_dataframe()
    assert len(model_data) == 10
    assert "Depression Rate" in model_data.columns
    assert "Anxiety Rate" in model_data.columns
    assert "Treatment Seeking" in model_data.columns


if __name__ == "__main__":
    # Run basic tests
    test_model_initialization()
    print("✓ Model initialization test passed")

    test_baseline_prevalence()
    print("✓ Baseline prevalence test passed")

    test_agent_initialization()
    print("✓ Agent initialization test passed")

    test_social_network_creation()
    print("✓ Social network test passed")

    test_intervention_effects()
    print("✓ Intervention effects test passed")

    test_peer_influence()
    print("✓ Peer influence test passed")

    test_treatment_reduces_symptoms()
    print("✓ Treatment effectiveness test passed")

    test_model_data_collection()
    print("✓ Data collection test passed")

    print("\n✅ All tests passed!")
