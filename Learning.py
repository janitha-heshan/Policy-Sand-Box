"""
Learning and adaptation mechanisms for agents using reinforcement learning principles
"""
import numpy as np
from typing import Dict, List, Tuple
from enum import Enum


class Decision(Enum):
    """Agent decision types"""
    SAVE = 1
    SPEND = 2
    BORROW = 3
    CHANGE_JOB = 4
    PROTEST = 5
    MIGRATE = 6


class ReinforcementLearner:
    """
    Implements Q-learning style behavior adaptation for citizens
    Agents learn which actions lead to better outcomes
    """
    
    def __init__(self, learning_rate: float = 0.1, discount_factor: float = 0.95):
        """
        Initialize Q-learner
        
        Args:
            learning_rate: How quickly to update Q-values (0-1)
            discount_factor: How much to weight future rewards (0-1)
        """
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        
        # Q-table: maps (state, action) -> expected value
        # State representation: (employment, wealth_level, stress_level) -> discrete buckets
        self.q_table = {}
        self.action_history = []
        self.reward_history = []
    
    def get_state_key(self, citizen) -> Tuple:
        """
        Discretize citizen state into buckets for Q-learning
        """
        # Employment state (0=unemployed, 1=employed, 2=retired)
        employment = 0 if citizen.employment_status.name == "UNEMPLOYED" else (
            2 if citizen.employment_status.name == "RETIRED" else 1)
        
        # Wealth level (negative=in_debt, 0=poor, 1=middle, 2=rich)
        wealth = citizen.savings - citizen.debt
        if wealth < 0:
            wealth_level = -1
        elif wealth < citizen.income * 3:
            wealth_level = 0
        elif wealth < citizen.income * 12:
            wealth_level = 1
        else:
            wealth_level = 2
        
        # Stress level (0=low, 1=medium, 2=high)
        stress_level = int(citizen.stress_level * 3)
        stress_level = min(2, stress_level)
        
        return (employment, wealth_level, stress_level)
    
    def get_action_value(self, state: Tuple, action: Decision) -> float:
        """Get Q-value for state-action pair"""
        key = (state, action)
        return self.q_table.get(key, 0.0)
    
    def select_action(self, citizen, state: Tuple, exploration_rate: float = 0.1) -> Decision:
        """
        Select action using epsilon-greedy strategy
        
        Args:
            citizen: Citizen object
            state: Current state tuple
            exploration_rate: Probability of random exploration (epsilon)
            
        Returns:
            Selected Decision action
        """
        # Epsilon-greedy: explore with probability epsilon, exploit best known action
        if np.random.random() < exploration_rate:
            # Explore: random action
            valid_actions = self._get_valid_actions(citizen)
            return np.random.choice(valid_actions)
        else:
            # Exploit: best known action
            valid_actions = self._get_valid_actions(citizen)
            best_action = max(valid_actions, 
                            key=lambda a: self.get_action_value(state, a))
            return best_action
    
    def _get_valid_actions(self, citizen) -> List[Decision]:
        """Get valid actions for citizen based on current state"""
        valid_actions = [Decision.SAVE, Decision.SPEND]
        
        # Can only borrow if not already heavily indebted
        if citizen.debt < citizen.income * 5:
            valid_actions.append(Decision.BORROW)
        
        # Can change job if employed or have been unemployed
        if citizen.employment_status.name in ["EMPLOYED", "UNEMPLOYED"]:
            valid_actions.append(Decision.CHANGE_JOB)
        
        # Can protest if stressed enough
        if citizen.stress_level > 0.5:
            valid_actions.append(Decision.PROTEST)
        
        # Can migrate if unhappy enough
        if citizen.satisfaction < 0.4:
            valid_actions.append(Decision.MIGRATE)
        
        return valid_actions
    
    def calculate_reward(self, citizen, action: Decision, previous_state: Dict) -> float:
        """
        Calculate reward for taking an action
        Rewards learning that improves citizen wellbeing
        """
        reward = 0.0
        
        # Base reward: improved satisfaction
        satisfaction_improvement = citizen.satisfaction - previous_state.get("satisfaction", citizen.satisfaction)
        reward += satisfaction_improvement * 2.0
        
        # Penalize stress increase
        stress_increase = citizen.stress_level - previous_state.get("stress_level", citizen.stress_level)
        reward -= stress_increase * 1.5
        
        # Action-specific rewards
        if action == Decision.SAVE:
            # Reward saving if it improves wealth
            wealth_change = (citizen.savings - citizen.debt) - (
                previous_state.get("savings", citizen.savings) - previous_state.get("debt", citizen.debt))
            if wealth_change > 0:
                reward += 1.0
            else:
                reward -= 0.5
        
        elif action == Decision.SPEND:
            # Reward spending that increases satisfaction (within limits)
            if citizen.satisfaction > 0.7:
                reward += 0.5
            elif citizen.satisfaction < 0.4:
                reward -= 0.5
        
        elif action == Decision.BORROW:
            # Reward borrowing only if it improves situations
            if citizen.confidence > 0.6 and citizen.debt < citizen.income * 5:
                reward += 0.5
            else:
                reward -= 1.0  # Penalize over-borrowing
        
        elif action == Decision.CHANGE_JOB:
            # Reward job changes that increase income/satisfaction
            if citizen.employment_status.name == "EMPLOYED":
                reward += 0.5
            else:
                reward -= 0.3
        
        elif action == Decision.PROTEST:
            # Complex: short-term stress relief but long-term effects vary
            reward -= 0.2  # Slight penalty (protest is disruptive)
        
        return reward
    
    def update_q_value(self, state: Tuple, action: Decision, reward: float, 
                       next_state: Tuple, done: bool = False):
        """
        Update Q-value using Q-learning update rule
        Q(s,a) = Q(s,a) + α[r + γ*max(Q(s',a')) - Q(s,a)]
        """
        key = (state, action)
        current_q = self.q_table.get(key, 0.0)
        
        # Find max Q-value for next state
        next_actions = [a for a in Decision]
        max_next_q = max([self.q_table.get((next_state, a), 0.0) for a in next_actions], default=0.0)
        
        # Q-learning update
        if done:
            new_q = current_q + self.learning_rate * (reward - current_q)
        else:
            new_q = current_q + self.learning_rate * (reward + self.discount_factor * max_next_q - current_q)
        
        self.q_table[key] = new_q
    
    def get_learning_stats(self) -> Dict:
        """Get statistics about learning progress"""
        if not self.q_table:
            return {"total_state_actions": 0, "avg_q_value": 0}
        
        q_values = list(self.q_table.values())
        return {
            "total_state_actions": len(self.q_table),
            "avg_q_value": np.mean(q_values),
            "max_q_value": np.max(q_values),
            "min_q_value": np.min(q_values),
        }


class UtilityFunction:
    """
    Models citizen utility/preference functions using economic principles
    """
    
    @staticmethod
    def cobb_douglas_utility(consumption: float, leisure: float, alpha: float = 0.7) -> float:
        """
        Cobb-Douglas utility: U = C^α * L^(1-α)
        
        Args:
            consumption: Consumption level
            leisure: Leisure/free time (1 - work fraction)
            alpha: Consumption preference parameter (0-1)
        """
        if consumption <= 0 or leisure <= 0:
            return 0.0
        return (consumption ** alpha) * (leisure ** (1 - alpha))
    
    @staticmethod
    def risk_adjusted_utility(expected_return: float, variance: float, 
                             risk_aversion: float = 2.0) -> float:
        """
        Risk-adjusted utility considering both return and risk
        U = E[R] - (risk_aversion/2) * Var[R]
        
        Args:
            expected_return: Expected return
            variance: Return variance
            risk_aversion: Coefficient of risk aversion
        """
        return expected_return - (risk_aversion / 2) * variance
    
    @staticmethod
    def consumption_utility(consumption: float, habit: float, 
                           satiation_rate: float = 0.8) -> float:
        """
        Consumption utility with habit formation
        Higher consumption above habit level = diminishing returns
        """
        excess_consumption = max(0, consumption - habit)
        return habit * np.log(max(1, consumption)) + excess_consumption * satiation_rate
    
    @staticmethod
    def portfolio_choice(current_savings: float, risk_tolerance: float,
                        expected_interest: float, inflation: float) -> Tuple[float, float]:
        """
        Determine optimal consumption vs savings split
        
        Returns:
            (consumption_share, savings_share)
        """
        # Risk-tolerant agents save less when interest rates are low
        real_interest = expected_interest - inflation
        
        # Base consumption share (propensity to consume)
        base_mpc = 0.8  # Marginal propensity to consume
        
        # Adjust for interest rates and risk tolerance
        interest_sensitivity = max(-0.3, min(0.3, real_interest * 5))
        risk_adjustment = (risk_tolerance - 0.5) * 0.2
        
        consumption_share = base_mpc + interest_sensitivity + risk_adjustment
        consumption_share = max(0.4, min(0.95, consumption_share))
        
        savings_share = 1.0 - consumption_share
        
        return consumption_share, savings_share


class BehavioralLearningAgent:
    """
    Combines Q-learning and utility functions for adaptive agent behavior
    """
    
    def __init__(self, citizen):
        self.citizen = citizen
        self.q_learner = ReinforcementLearner(learning_rate=citizen.learning_rate)
        self.previous_state = {}
    
    def decide_action(self, macro_state: Dict, exploration_rate: float = 0.1) -> Decision:
        """
        Make decision based on learned Q-values and utility maximization
        """
        state = self.q_learner.get_state_key(self.citizen)
        action = self.q_learner.select_action(self.citizen, state, exploration_rate)
        return action
    
    def learn_from_outcome(self, action: Decision, next_macro_state: Dict):
        """
        Update learning based on outcome of previous action
        """
        state = self.q_learner.get_state_key(self.citizen)
        reward = self.q_learner.calculate_reward(self.citizen, action, self.previous_state)
        next_state = self.q_learner.get_state_key(self.citizen)
        
        self.q_learner.update_q_value(state, action, reward, next_state)
        
        # Store current state for next update
        self.previous_state = {
            "satisfaction": self.citizen.satisfaction,
            "stress_level": self.citizen.stress_level,
            "savings": self.citizen.savings,
            "debt": self.citizen.debt,
        }
