"""
Macroeconomic model tracking economy-wide variables and relationships
"""
import numpy as np
from typing import Dict, List
from dataclasses import dataclass, field

@dataclass
class EconomicState:
    """Tracks macroeconomic variables"""
    inflation_rate: float = 0.02
    unemployment_rate: float = 0.05
    gdp: float = 1000000.0
    gdp_growth_rate: float = 0.02
    government_budget: float = 100000.0
    government_revenue: float = 0.0
    government_spending: float = 0.0
    average_wage: float = 2000.0
    total_consumption: float = 0.0
    total_investment: float = 0.0
    total_savings: float = 0.0
    wealth_inequality_gini: float = 0.35
    social_unrest_index: float = 0.2
    population: int = 1000
    
    # Historical tracking
    inflation_history: List[float] = field(default_factory=list)
    unemployment_history: List[float] = field(default_factory=list)
    gdp_history: List[float] = field(default_factory=list)
    unrest_history: List[float] = field(default_factory=list)


class EconomyModel:
    """
    Simulates macroeconomic dynamics based on agent behavior and policies
    """
    
    def __init__(self):
        self.state = EconomicState()
        
        # Economic parameters
        self.consumption_to_inflation_multiplier = 0.15
        self.unemployment_to_wage_multiplier = -0.5
        self.inflation_inertia = 0.6  # How much inflation persists
        self.gdp_multiplier = 0.8  # Consumption to GDP conversion
        
    def update(self, citizens: List, policies: Dict, timestep: int):
        """
        Update economic state based on aggregate citizen behavior
        
        Args:
            citizens: List of Citizen objects
            policies: Current policy dictionary
            timestep: Current time step
        """
        # Aggregate citizen behavior
        self._aggregate_citizen_data(citizens, policies)
        
        # Update inflation based on consumption and money supply
        self._update_inflation(policies)
        
        # Update unemployment
        self._update_unemployment(citizens)
        
        # Update wages
        self._update_wages(citizens, policies)
        
        # Update GDP
        self._update_gdp()
        
        # Update government budget
        self._update_government_budget(citizens, policies)
        
        # Calculate wealth inequality
        self._calculate_inequality(citizens)
        
        # Calculate social unrest
        self._calculate_social_unrest(citizens)
        
        # Store history
        self._store_history()
    
    def _aggregate_citizen_data(self, citizens: List, policies: Dict):
        """Aggregate data from all citizens"""
        self.state.total_consumption = sum(c.monthly_spending for c in citizens)
        self.state.total_savings = sum(c.savings for c in citizens)
        self.state.total_investment = self.state.total_savings * 0.3  # Portion of savings invested
        self.state.average_wage = np.mean([c.income for c in citizens])
        self.state.population = len(citizens)
        
        # Government revenue
        income_tax_rate = policies.get("income_tax_rate", 0.2)
        fuel_tax_rate = policies.get("fuel_tax_rate", 0.0)
        total_income = sum(c.income for c in citizens)
        
        self.state.government_revenue = total_income * income_tax_rate
        self.state.government_revenue += self.state.total_consumption * fuel_tax_rate * 0.3  # Fuel consumption proxy
        
        # Government spending
        ubi = policies.get("universal_basic_income", 0) * len(citizens)
        welfare = policies.get("welfare_support", 0) * len(citizens)
        unemployment_benefits = policies.get("unemployment_benefit_rate", 0.4) * total_income * \
                               sum(1 for c in citizens if c.employment_status.name == "UNEMPLOYED") / len(citizens)
        
        self.state.government_spending = ubi + welfare + unemployment_benefits
    
    def _update_inflation(self, policies: Dict):
        """Update inflation based on consumption, money supply, and supply shocks"""
        # Consumption-driven inflation
        consumption_pressure = (self.state.total_consumption - 500000) / 500000 * 0.05
        
        # Money supply shock from fuel prices (proxy for cost-push inflation)
        fuel_price_change = policies.get("fuel_price_multiplier", 1.0) - 1.0
        cost_push_inflation = fuel_price_change * 0.3
        
        # Inflation inertia (last month's inflation affects this month)
        last_inflation = self.state.inflation_history[-1] if self.state.inflation_history else 0.02
        
        new_inflation = (self.inflation_inertia * last_inflation + 
                        consumption_pressure + cost_push_inflation)
        
        self.state.inflation_rate = max(0, min(0.15, new_inflation))  # Bound between 0% and 15%
    
    def _update_unemployment(self, citizens: List):
        """Update unemployment rate"""
        employed = sum(1 for c in citizens if c.employment_status.name == "EMPLOYED")
        working_age = sum(1 for c in citizens if 18 <= c.age < 65)
        
        self.state.unemployment_rate = max(0, min(0.3, 1.0 - (employed / max(working_age, 1))))
    
    def _update_wages(self, citizens: List, policies: Dict):
        """Update average wages based on inflation and labor market"""
        unemployment_effect = (0.05 - self.state.unemployment_rate) * self.unemployment_to_wage_multiplier * 0.1
        inflation_effect = self.state.inflation_rate * 0.7  # Wages partially keep up with inflation
        
        wage_growth = unemployment_effect + inflation_effect
        self.state.average_wage *= (1 + wage_growth)
    
    def _update_gdp(self):
        """Update GDP based on consumption, investment, and government spending"""
        # Simple GDP calculation: GDP ≈ C + I + G
        self.state.gdp = (self.state.total_consumption + 
                         self.state.total_investment + 
                         self.state.government_spending) * self.gdp_multiplier
        
        # Calculate growth rate
        if len(self.state.gdp_history) > 0:
            self.state.gdp_growth_rate = (self.state.gdp - self.state.gdp_history[-1]) / self.state.gdp_history[-1]
        
        self.state.gdp_growth_rate = max(-0.1, min(0.1, self.state.gdp_growth_rate))
    
    def _update_government_budget(self, citizens: List, policies: Dict):
        """Update government budget balance"""
        deficit = self.state.government_spending - self.state.government_revenue
        self.state.government_budget -= deficit
        
        # Government debt accumulates
        if deficit > 0:
            self.state.government_budget -= deficit
    
    def _calculate_inequality(self, citizens: List):
        """Calculate Gini coefficient for wealth inequality"""
        wealth = sorted([c.savings - c.debt for c in citizens])
        n = len(wealth)
        
        if n < 2:
            self.state.wealth_inequality_gini = 0
            return
        
        # Simplified Gini calculation
        cumsum = np.cumsum(wealth)
        gini = (2 * np.sum(cumsum * np.arange(1, n + 1))) / (n * np.sum(wealth)) - (n + 1) / n
        
        self.state.wealth_inequality_gini = max(0, min(1, gini))
    
    def _calculate_social_unrest(self, citizens: List):
        """Calculate overall social unrest index"""
        avg_protest_prob = np.mean([c.protest_probability for c in citizens])
        avg_migration_prob = np.mean([c.migration_probability for c in citizens])
        
        # High inequality increases unrest
        inequality_factor = self.state.wealth_inequality_gini
        
        # High unemployment increases unrest
        unemployment_factor = self.state.unemployment_rate
        
        # High inflation decreases satisfaction
        inflation_factor = min(self.state.inflation_rate / 0.1, 1.0)
        
        self.state.social_unrest_index = (avg_protest_prob * 0.4 + 
                                         inequality_factor * 0.25 + 
                                         unemployment_factor * 0.2 + 
                                         inflation_factor * 0.15)
        
        self.state.social_unrest_index = min(1.0, self.state.social_unrest_index)
    
    def _store_history(self):
        """Store current values in history for tracking"""
        self.state.inflation_history.append(self.state.inflation_rate)
        self.state.unemployment_history.append(self.state.unemployment_rate)
        self.state.gdp_history.append(self.state.gdp)
        self.state.unrest_history.append(self.state.social_unrest_index)
        
        # Keep only last 240 months (20 years) of history
        if len(self.state.inflation_history) > 240:
            self.state.inflation_history = self.state.inflation_history[-240:]
            self.state.unemployment_history = self.state.unemployment_history[-240:]
            self.state.gdp_history = self.state.gdp_history[-240:]
            self.state.unrest_history = self.state.unrest_history[-240:]
    
    def get_state(self) -> Dict:
        """Return current economic state"""
        return {
            "inflation_rate": self.state.inflation_rate,
            "unemployment_rate": self.state.unemployment_rate,
            "gdp": self.state.gdp,
            "gdp_growth_rate": self.state.gdp_growth_rate,
            "government_budget": self.state.government_budget,
            "average_wage": self.state.average_wage,
            "total_consumption": self.state.total_consumption,
            "wealth_inequality_gini": self.state.wealth_inequality_gini,
            "social_unrest_index": self.state.social_unrest_index,
        }
