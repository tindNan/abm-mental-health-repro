from mesa import Model
from mesa.time import RandomActivation
from mesa.space import NetworkGrid
from mesa.datacollection import DataCollector
import networkx as nx
import numpy as np
from .agent import YouthAgent, MentalHealthState


class NairobiModel(Model):
    def __init__(
        self,
        n_agents=1000,
        informal_settlement_rate=0.5,
        baseline_depression_rate=0.26,
        baseline_anxiety_rate=0.191,
        out_of_school_rate=0.25,
        avg_social_connections=12,
        avg_social_media_hours=3.73,
        religious_participation_rate=0.7,
        peer_influence_strength=2.13,
        loneliness_impact_factor=10.68,
        treatment_access_rate=0.02,
        intervention_active=False,
        intervention_multiplier=3.0,
        environmental_stress_multiplier=1.5,
        digital_intervention_enabled=False,
        peer_support_coverage=0.0,
    ):
        super().__init__()

        # Model parameters from research
        self.n_agents = n_agents
        self.informal_settlement_rate = informal_settlement_rate
        self.baseline_depression_rate = baseline_depression_rate
        self.baseline_anxiety_rate = baseline_anxiety_rate
        self.out_of_school_rate = out_of_school_rate
        self.avg_social_connections = avg_social_connections
        self.avg_social_media_hours = avg_social_media_hours
        self.religious_participation_rate = religious_participation_rate
        self.peer_influence_strength = peer_influence_strength
        self.loneliness_impact_factor = loneliness_impact_factor
        self.treatment_access_rate = treatment_access_rate

        # Intervention parameters
        self.intervention_active = intervention_active
        self.intervention_multiplier = intervention_multiplier
        self.environmental_stress_multiplier = environmental_stress_multiplier
        self.digital_intervention_enabled = digital_intervention_enabled
        self.peer_support_coverage = peer_support_coverage

        # Create social network
        self.G = self.create_social_network()
        self.grid = NetworkGrid(self.G)
        self.schedule = RandomActivation(self)

        # Create agents
        for i in range(self.n_agents):
            agent = YouthAgent(i, self)
            self.schedule.add(agent)
            self.grid.place_agent(agent, i)

        # Connect agents based on network
        self.connect_agents()

        # Apply peer support intervention if enabled
        if self.peer_support_coverage > 0:
            self.apply_peer_support_intervention()

        # Data collection
        self.datacollector = DataCollector(
            model_reporters={
                "Depression Rate": self.get_depression_rate,
                "Anxiety Rate": self.get_anxiety_rate,
                "Symptomatic Count": self.get_symptomatic_count,
                "At Risk Count": self.get_at_risk_count,
                "Healthy Count": self.get_healthy_count,
                "Recovering Count": self.get_recovering_count,
                "Treatment Seeking": self.get_treatment_seeking_count,
                "Average Resilience": self.get_average_resilience,
                "Network Clustering": self.get_network_clustering,
            },
            agent_reporters={
                "State": "mental_state",
                "Depression": "depression_score",
                "Anxiety": "anxiety_score",
                "Seeking Treatment": "seeking_treatment",
            },
        )

    def create_social_network(self):
        # Create a social network with properties matching Nairobi youth
        # Use small-world network to represent local clustering with some long-range connections

        # Parameters based on research
        k = int(self.avg_social_connections)  # Average connections
        p = 0.3  # Rewiring probability (higher for social media influence)

        # Create Watts-Strogatz small-world network
        G = nx.watts_strogatz_graph(self.n_agents, k, p)

        # Add some preferential attachment for popular individuals
        # This represents social media influencers and popular peers
        num_hubs = int(self.n_agents * 0.05)  # 5% are highly connected
        for i in range(num_hubs):
            hub = np.random.randint(0, self.n_agents)
            # Add extra connections to hubs
            for _ in range(k):
                target = np.random.randint(0, self.n_agents)
                if target != hub and not G.has_edge(hub, target):
                    G.add_edge(hub, target)

        return G

    def connect_agents(self):
        # Set up social connections based on network
        for agent in self.schedule.agents:
            neighbors = list(self.G.neighbors(agent.unique_id))
            agent.social_connections = neighbors

    def apply_peer_support_intervention(self):
        # Select agents to be peer supporters
        num_supporters = int(self.n_agents * self.peer_support_coverage)
        supporters = np.random.choice(
            self.schedule.agents, num_supporters, replace=False
        )

        for supporter in supporters:
            supporter.resilience_score = min(1.0, supporter.resilience_score + 0.2)
            supporter.peer_support = min(1.0, supporter.peer_support + 0.3)

    def step(self):
        # Apply digital intervention if enabled
        if self.digital_intervention_enabled:
            self.apply_digital_intervention()

        # Execute agent steps
        self.schedule.step()

        # Collect data
        self.datacollector.collect(self)

    def apply_digital_intervention(self):
        # Digital intervention through social media
        # Target agents with high social media usage
        for agent in self.schedule.agents:
            if agent.daily_social_media_hours > 3:
                # Increase awareness and reduce stigma
                if agent.mental_state in [
                    MentalHealthState.SYMPTOMATIC,
                    MentalHealthState.AT_RISK,
                ]:
                    # Higher chance of seeking treatment
                    if np.random.random() < 0.1:  # 10% chance per step
                        agent.seeking_treatment = True

                # Provide coping strategies
                agent.resilience_score = min(1.0, agent.resilience_score + 0.01)

    # Data collection methods
    def get_depression_rate(self):
        depressed = sum(1 for a in self.schedule.agents if a.depression_score > 0.6)
        return depressed / self.n_agents

    def get_anxiety_rate(self):
        anxious = sum(1 for a in self.schedule.agents if a.anxiety_score > 0.6)
        return anxious / self.n_agents

    def get_symptomatic_count(self):
        return sum(
            1
            for a in self.schedule.agents
            if a.mental_state == MentalHealthState.SYMPTOMATIC
        )

    def get_at_risk_count(self):
        return sum(
            1
            for a in self.schedule.agents
            if a.mental_state == MentalHealthState.AT_RISK
        )

    def get_healthy_count(self):
        return sum(
            1
            for a in self.schedule.agents
            if a.mental_state == MentalHealthState.HEALTHY
        )

    def get_recovering_count(self):
        return sum(
            1
            for a in self.schedule.agents
            if a.mental_state == MentalHealthState.RECOVERING
        )

    def get_treatment_seeking_count(self):
        return sum(1 for a in self.schedule.agents if a.seeking_treatment)

    def get_average_resilience(self):
        total_resilience = sum(a.resilience_score for a in self.schedule.agents)
        return total_resilience / self.n_agents

    def get_network_clustering(self):
        return nx.average_clustering(self.G)

    def get_basic_reproduction_number(self):
        # Estimate R0 for mental health transmission
        # This is a simplified calculation
        symptomatic = self.get_symptomatic_count()
        if symptomatic == 0:
            return 0

        # Average number of susceptible contacts × transmission probability
        avg_contacts = self.avg_social_connections
        transmission_prob = 0.1 * self.peer_influence_strength / 10

        return avg_contacts * transmission_prob
