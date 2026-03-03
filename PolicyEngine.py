"""
Policy engine for managing government policies and their effects
"""
from typing import Dict, List
from dataclasses import dataclass, field
import json

@dataclass
class PolicySet:
    """Container for all policies"""
    income_tax_rate: float = 0.2  # 0-1
    fuel_tax_rate: float = 0.0  # Tax on fuel/energy
    fuel_price_multiplier: float = 1.0  # Base fuel price multiplier
    interest_rate: float = 0.05  # Central bank rate
    unemployment_benefit_rate: float = 0.4  # % of income while unemployed
    pension_replacement_rate: float = 0.6  # % of income in retirement
    universal_basic_income: float = 0.0  # Monthly UBI per citizen
    welfare_support: float = 0.0  # General welfare per citizen
    
    def to_dict(self) -> Dict:
        return {
            "income_tax_rate": self.income_tax_rate,
            "fuel_tax_rate": self.fuel_tax_rate,
            "fuel_price_multiplier": self.fuel_price_multiplier,
            "interest_rate": self.interest_rate,
            "unemployment_benefit_rate": self.unemployment_benefit_rate,
            "pension_replacement_rate": self.pension_replacement_rate,
            "universal_basic_income": self.universal_basic_income,
            "welfare_support": self.welfare_support,
        }


class PolicyEngine:
    """
    Manages policy adjustments and their impacts on the simulation
    """
    
    def __init__(self):
        self.policies = PolicySet()
        self.policy_history = []
        self.policy_effects_log = []
        
        # Policy constraints
        self.constraints = {
            "income_tax_rate": (0.0, 0.7),
            "fuel_tax_rate": (0.0, 0.5),
            "fuel_price_multiplier": (0.5, 3.0),
            "interest_rate": (0.0, 0.15),
            "unemployment_benefit_rate": (0.0, 1.0),
            "pension_replacement_rate": (0.0, 1.0),
            "universal_basic_income": (0.0, 2000),
            "welfare_support": (0.0, 500),
        }
    
    def set_policy(self, policy_name: str, value: float) -> bool:
        """
        Set a policy to a new value with constraint checking
        
        Returns True if successful, False otherwise
        """
        if policy_name not in self.constraints:
            return False
        
        min_val, max_val = self.constraints[policy_name]
        clamped_value = max(min_val, min(max_val, value))
        
        # Record old value
        old_value = getattr(self.policies, policy_name)
        
        # Set new value
        setattr(self.policies, policy_name, clamped_value)
        
        # Log change
        if old_value != clamped_value:
            self.policy_history.append({
                "policy": policy_name,
                "old_value": old_value,
                "new_value": clamped_value,
                "timestep": len(self.policy_history)
            })
        
        return True
    
    def set_policies_from_dict(self, policy_dict: Dict) -> List[str]:
        """
        Set multiple policies at once
        
        Returns list of successfully updated policies
        """
        successful = []
        for policy_name, value in policy_dict.items():
            if self.set_policy(policy_name, value):
                successful.append(policy_name)
        return successful
    
    def get_policies(self) -> Dict:
        """Return current policies as dictionary"""
        return self.policies.to_dict()
    
    def calculate_policy_impacts(self, citizens: List, macro_state: Dict) -> Dict:
        """
        Calculate aggregate impacts of current policies
        
        Returns dictionary of impacts
        """
        impacts = {
            "total_tax_burden": 0,
            "avg_disposable_income": 0,
            "govt_revenue": 0,
            "govt_spending": 0,
            "welfare_coverage": 0,
            "avg_fuel_cost_impact": 0,
        }
        
        total_income = sum(c.income for c in citizens)
        avg_income = total_income / len(citizens) if citizens else 0
        
        # Tax burden
        impacts["total_tax_burden"] = avg_income * self.policies.income_tax_rate
        
        # Disposable income
        ubi = self.policies.universal_basic_income
        welfare = self.policies.welfare_support
        impacts["avg_disposable_income"] = avg_income * (1 - self.policies.income_tax_rate) + ubi + welfare
        
        # Government finances
        impacts["govt_revenue"] = total_income * self.policies.income_tax_rate
        unemployed_count = sum(1 for c in citizens if c.employment_status.name == "UNEMPLOYED")
        impacts["govt_spending"] = (ubi * len(citizens) + 
                                   welfare * len(citizens) +
                                   unemployed_count * avg_income * self.policies.unemployment_benefit_rate)
        
        # Welfare coverage (% of population receiving welfare)
        impacts["welfare_coverage"] = ((ubi > 0) + (welfare > 0)) * 0.5
        
        # Fuel cost impact
        impacts["avg_fuel_cost_impact"] = (self.policies.fuel_price_multiplier - 1.0) * 100  # % change
        
        return impacts
    
    def scenario_extreme_tax(self):
        """Extreme high-tax scenario (70% income tax)"""
        self.set_policy("income_tax_rate", 0.7)
        self.set_policy("universal_basic_income", 1000)
        self.set_policy("welfare_support", 200)
    
    def scenario_libertarian(self):
        """Low-tax, minimal welfare scenario"""
        self.set_policy("income_tax_rate", 0.1)
        self.set_policy("universal_basic_income", 0)
        self.set_policy("welfare_support", 0)
        self.set_policy("interest_rate", 0.02)
    
    def scenario_ubi(self):
        """Universal Basic Income experiment"""
        self.set_policy("income_tax_rate", 0.3)
        self.set_policy("universal_basic_income", 1500)
        self.set_policy("welfare_support", 0)
    
    def scenario_green_energy(self):
        """High fuel price to incentivize renewable energy"""
        self.set_policy("fuel_tax_rate", 0.3)
        self.set_policy("fuel_price_multiplier", 1.8)
        self.set_policy("universal_basic_income", 200)  # Offset regressive tax
    
    def scenario_financial_crisis(self):
        """Simulate post-financial crisis response"""
        self.set_policy("interest_rate", 0.0)  # Zero rates
        self.set_policy("unemployment_benefit_rate", 0.8)  # Enhanced benefits
        self.set_policy("income_tax_rate", 0.15)  # Lower taxes to stimulate
        self.set_policy("welfare_support", 300)
    
    def reset_to_default(self):
        """Reset all policies to defaults"""
        self.policies = PolicySet()
