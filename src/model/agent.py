from enum import Enum
import random
from mesa import Agent
import numpy as np


class MentalHealthState(Enum):
    HEALTHY = "healthy"
    AT_RISK = "at_risk"
    SYMPTOMATIC = "symptomatic"
    RECOVERING = "recovering"


class YouthAgent(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

        # Demographics
        self.age = random.randint(15, 24)
        self.gender = random.choice(["male", "female"])
        self.in_school = random.random() > model.out_of_school_rate
        self.in_informal_settlement = random.random() < model.informal_settlement_rate

        # Mental health
        self.mental_state = MentalHealthState.HEALTHY
        self.depression_score = 0.0
        self.anxiety_score = 0.0
        self.resilience_score = random.uniform(0.3, 0.8)
        self.loneliness_level = random.uniform(0, 0.5)

        # Social factors
        self.social_connections = []
        self.family_support = random.uniform(0.2, 0.9)
        self.peer_support = random.uniform(0.1, 0.8)
        self.religious_participation = (
            random.random() < model.religious_participation_rate
        )
        self.daily_social_media_hours = np.random.normal(
            model.avg_social_media_hours, 1.0
        )
        self.daily_social_media_hours = max(0, min(8, self.daily_social_media_hours))

        # Risk and protective factors
        self.stress_exposure = self.calculate_stress_exposure()
        self.seeking_treatment = False
        self.treatment_duration = 0

        # Initialize mental health based on baseline prevalence
        self.initialize_mental_health()

    def initialize_mental_health(self):
        # Set initial mental health based on research prevalence
        depression_prob = self.model.baseline_depression_rate
        anxiety_prob = self.model.baseline_anxiety_rate

        # Adjust for risk factors
        if not self.in_school:
            depression_prob *= 1.5  # Out-of-school youth have higher rates
            anxiety_prob *= 1.45

        if self.in_informal_settlement:
            depression_prob *= 1.3
            anxiety_prob *= 1.25

        # Set initial states
        if random.random() < depression_prob:
            self.depression_score = random.uniform(0.6, 1.0)
            self.mental_state = MentalHealthState.SYMPTOMATIC

        if random.random() < anxiety_prob:
            self.anxiety_score = random.uniform(0.6, 1.0)
            if self.mental_state == MentalHealthState.HEALTHY:
                self.mental_state = MentalHealthState.AT_RISK

    def calculate_stress_exposure(self):
        base_stress = 0.3

        # Environmental stressors
        if self.in_informal_settlement:
            base_stress += 0.3

        if not self.in_school:
            base_stress += 0.2

        # Gender-specific stressors
        if self.gender == "female":
            base_stress += 0.1

        return min(1.0, base_stress + random.uniform(-0.1, 0.1))

    def step(self):
        # Update mental health based on interactions
        self.update_mental_health()

        # Consider seeking treatment
        self.evaluate_treatment_seeking()

        # Update treatment progress if in treatment
        if self.seeking_treatment:
            self.treatment_duration += 1
            self.apply_treatment_effects()

    def update_mental_health(self):
        # Calculate peer influence
        peer_influence = self.calculate_peer_influence()

        # Apply loneliness impact (OR = 10.68 from research)
        loneliness_impact = self.loneliness_level * self.model.loneliness_impact_factor

        # Calculate protective factors
        protection = (
            self.resilience_score * 0.3
            + self.family_support * 0.3
            + self.peer_support * 0.2
            + (0.2 if self.religious_participation else 0)
        )

        # Update depression and anxiety scores
        depression_change = (
            peer_influence * 0.4
            + self.stress_exposure * 0.3
            + loneliness_impact * 0.3
            - protection * 0.5
        )

        anxiety_change = (
            peer_influence * 0.35
            + self.stress_exposure * 0.35
            + loneliness_impact * 0.2
            - protection * 0.4
        )

        # Apply changes with bounds
        self.depression_score = max(
            0, min(1, self.depression_score + depression_change * 0.05)
        )
        self.anxiety_score = max(0, min(1, self.anxiety_score + anxiety_change * 0.05))

        # Update mental state based on scores
        self.update_mental_state()

    def calculate_peer_influence(self):
        if not self.social_connections:
            return 0

        # Calculate average mental health of connections
        total_influence = 0
        for neighbor_id in self.social_connections:
            neighbor = self.model.schedule.agents[neighbor_id]
            if neighbor.mental_state in [
                MentalHealthState.SYMPTOMATIC,
                MentalHealthState.AT_RISK,
            ]:
                total_influence += (
                    0.5 if neighbor.mental_state == MentalHealthState.AT_RISK else 1.0
                )

        avg_influence = (
            total_influence / len(self.social_connections)
            if self.social_connections
            else 0
        )

        # Apply peer influence strength from research (β = 2.13)
        return avg_influence * self.model.peer_influence_strength

    def update_mental_state(self):
        # Determine state based on scores
        if self.depression_score > 0.6 or self.anxiety_score > 0.6:
            if self.mental_state == MentalHealthState.RECOVERING:
                self.mental_state = MentalHealthState.AT_RISK
            else:
                self.mental_state = MentalHealthState.SYMPTOMATIC
        elif self.depression_score > 0.4 or self.anxiety_score > 0.4:
            self.mental_state = MentalHealthState.AT_RISK
        elif self.mental_state == MentalHealthState.RECOVERING:
            if self.depression_score < 0.3 and self.anxiety_score < 0.3:
                self.mental_state = MentalHealthState.HEALTHY
        else:
            self.mental_state = MentalHealthState.HEALTHY

    def evaluate_treatment_seeking(self):
        # Only 2% baseline access from research
        if self.seeking_treatment:
            return

        # More likely to seek if symptomatic
        if self.mental_state == MentalHealthState.SYMPTOMATIC:
            seek_probability = self.model.treatment_access_rate

            # Increase probability if intervention is active
            if self.model.intervention_active:
                seek_probability *= self.model.intervention_multiplier

            if random.random() < seek_probability:
                self.seeking_treatment = True
                self.treatment_duration = 0

    def apply_treatment_effects(self):
        # Treatment gradually reduces symptoms
        if self.treatment_duration > 4:  # Minimum treatment duration
            reduction_rate = 0.1
            self.depression_score = max(0, self.depression_score - reduction_rate)
            self.anxiety_score = max(0, self.anxiety_score - reduction_rate)

            if self.treatment_duration > 12:
                self.mental_state = MentalHealthState.RECOVERING

            if (
                self.treatment_duration > 20
                and self.depression_score < 0.3
                and self.anxiety_score < 0.3
            ):
                self.seeking_treatment = False
                self.mental_state = MentalHealthState.HEALTHY
