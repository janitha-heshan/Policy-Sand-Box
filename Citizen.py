import numpy as np
from typing import Dict, List
from enum import Enum
from dataclasses import dataclass, field
import random

class EmploymentStatus(Enum):
    EMPLOYED = 1
    UNEMPLOYED = 2
    RETIRED = 3
    STUDENT = 4

@dataclass
class CitizenMemory:
    """Learning memory for citizens tracking past experiences"""
    past_savings_return: List[float] = field(default_factory=list)
    past_debt_cost: List[float] = field(default_factory=list)
    past_job_satisfaction: List[float] = field(default_factory=list)
    past_protest_effectiveness: List[float] = field(default_factory=list)
    job_change_attempts: int = 0
    times_protested: int = 0
    times_migrated: int = 0
    
    def get_avg_savings_return(self) -> float:
        return np.mean(self.past_savings_return) if self.past_savings_return else 0.02
    
    def get_avg_debt_cost(self) -> float:
        return np.mean(self.past_debt_cost) if self.past_debt_cost else 0.05

class Citizen:
    """
    Represents a citizen agent in the society simulator with behavioral and economic attributes.
    """
    _id_counter = 0
    
    def __init__(self, age: int, sector: str = "general", risk_tolerance: float = None):
        Citizen._id_counter += 1
        self.id = Citizen._id_counter
        
        # Demographic attributes
        self.age = age
        self.sector = sector  # "manufacturing", "service", "tech", "agriculture"
        
        # Economic attributes
        self.income = self._init_income(age, sector)
        self.savings = self.income * random.uniform(0.5, 2.0)  # Initial savings relative to monthly income
        self.debt = random.uniform(0, self.income * 3)  # Credit/personal debt
        self.employment_status = self._init_employment_status(age)
        self.job_security = random.uniform(0.5, 1.0)  # How stable the current job is
        
        # Behavioral attributes
        self.stress_level = random.uniform(0.2, 0.8)  # 0-1 scale
        self.satisfaction = random.uniform(0.3, 0.9)  # Overall life satisfaction
        self.confidence = random.uniform(0.3, 0.9)  # Economic confidence
        self.risk_tolerance = risk_tolerance if risk_tolerance else random.uniform(0.2, 0.9)
        
        # Spending & consumption patterns
        self.spending_preference = random.uniform(0.3, 0.8)  # Propensity to consume
        self.monthly_spending = self.income * self.spending_preference
        self.essential_spending = self.income * random.uniform(0.4, 0.7)  # Food, rent, utilities
        
        # Migration and protest likelihood
        self.migration_probability = 0.0
        self.protest_probability = 0.0
        self.willingness_to_protest = random.uniform(0.2, 0.9)
        
        # Learning and adaptation
        self.memory = CitizenMemory()
        self.learning_rate = random.uniform(0.05, 0.15)  # How quickly they adapt
        self.policy_preference = {}  # Learned policy preferences
        
        # Health and well-being
        self.health = random.uniform(0.6, 1.0)
        
    def _init_income(self, age: int, sector: str) -> float:
        """Initialize income based on age and sector"""
        base_age_factor = min(age / 40, 1.0) * 0.7 + 0.3  # Peak earnings around age 50
        sector_multiplier = {
            "tech": 1.4,
            "manufacturing": 0.9,
            "service": 0.7,
            "agriculture": 0.6
        }.get(sector, 1.0)
        
        # Monthly income in arbitrary units
        base_income = 2000 * base_age_factor * sector_multiplier
        variance = base_income * random.uniform(0.8, 1.3)
        return variance
    
    def _init_employment_status(self, age: int) -> EmploymentStatus:
        """Initialize employment status based on age"""
        if age < 18:
            return EmploymentStatus.STUDENT
        elif age >= 65:
            return EmploymentStatus.RETIRED
        else:
            # 90% employment rate for working-age
            return EmploymentStatus.EMPLOYED if random.random() < 0.9 else EmploymentStatus.UNEMPLOYED
    
    def update_monthly(self, policies: Dict, macro_state: Dict, timestep: int):
        """
        Update citizen state for one month (timestep)
        """
        # Update employment
        self._update_employment(policies, macro_state)
        
        # Update income based on employment and inflation
        self._update_income(policies, macro_state)
        
        # Calculate disposable income after taxes
        disposable_income = self._calculate_disposable_income(policies)
        
        # Make spending/saving decisions
        self._make_consumption_decision(disposable_income, policies, macro_state)
        
        # Update debt
        self._update_debt(policies, macro_state)
        
        # Update psychological state
        self._update_psychological_state(policies, macro_state, timestep)
        
        # Determine protest and migration probability
        self._update_social_behavior(policies, macro_state)
    
    def _update_employment(self, policies: Dict, macro_state: Dict):
        """Update employment status based on economic conditions"""
        if self.employment_status == EmploymentStatus.EMPLOYED:
            # Job loss probability increases with unemployment and decreases with job security
            unemployment_factor = macro_state.get("unemployment_rate", 0.05) * 2
            loss_probability = unemployment_factor * (1 - self.job_security)
            
            if random.random() < loss_probability:
                self.employment_status = EmploymentStatus.UNEMPLOYED
                self.stress_level = min(1.0, self.stress_level + 0.15)
                self.confidence = max(0, self.confidence - 0.2)
        
        elif self.employment_status == EmploymentStatus.UNEMPLOYED:
            # Job finding probability increases with job market health
            job_finding_rate = (1 - macro_state.get("unemployment_rate", 0.05)) * 0.3
            if random.random() < job_finding_rate:
                self.employment_status = EmploymentStatus.EMPLOYED
                self.job_security = random.uniform(0.4, 0.8)
                self.stress_level = max(0, self.stress_level - 0.1)
    
    def _update_income(self, policies: Dict, macro_state: Dict):
        """Update income based on employment and economic conditions"""
        if self.employment_status == EmploymentStatus.EMPLOYED:
            # Wage growth/decline based on inflation and productivity
            inflation = macro_state.get("inflation_rate", 0.02)
            wage_growth = inflation * 0.7  # Wages lag inflation
            self.income *= (1 + wage_growth)
        elif self.employment_status == EmploymentStatus.UNEMPLOYED:
            # Unemployment benefits (if policy exists)
            unemployment_benefit = policies.get("unemployment_benefit_rate", 0.4)
            self.income = self.income * unemployment_benefit
        elif self.employment_status == EmploymentStatus.RETIRED:
            # Pension (if policy exists)
            pension_rate = policies.get("pension_replacement_rate", 0.6)
            self.income = self.income * pension_rate
    
    def _calculate_disposable_income(self, policies: Dict) -> float:
        """Calculate disposable income after taxes and welfare"""
        income_tax_rate = policies.get("income_tax_rate", 0.2)
        taxes = self.income * income_tax_rate
        
        # Welfare/UBI benefits
        ubi = policies.get("universal_basic_income", 0)
        welfare = policies.get("welfare_support", 0)
        
        return self.income - taxes + ubi + welfare
    
    def _make_consumption_decision(self, disposable_income: float, policies: Dict, macro_state: Dict):
        """Decide how much to spend vs save based on psychological state and learning"""
        # Base spending tendency (spending_preference is always a float)
        spending_rate = self.spending_preference
        
        # Stress and confidence modulate spending
        stress_impact = self.stress_level * 0.2  # High stress increases spending (coping)
        confidence_boost = self.confidence * 0.15  # Confidence increases spending
        
        # Learned behavior from memory
        avg_savings_return = self.memory.get_avg_savings_return()
        if avg_savings_return > 0.05:
            spending_rate = spending_rate * 0.8  # Save more if savings are paying off
        
        adjusted_spending_rate = min(1.0, max(0.3, spending_rate + stress_impact + confidence_boost))
        
        # Actual spending decision
        discretionary_income = max(0, disposable_income - self.essential_spending)
        discretionary_spending = discretionary_income * adjusted_spending_rate
        self.monthly_spending = self.essential_spending + discretionary_spending
        
        # Save the remainder
        saved_amount = disposable_income - self.monthly_spending
        self.savings += saved_amount
        
        # Update memory
        if saved_amount > 0:
            inflation = macro_state.get("inflation_rate", 0.02)
            real_return = -inflation  # Savings lose to inflation
            self.memory.past_savings_return.append(real_return)
    
    def _update_debt(self, policies: Dict, macro_state: Dict):
        """Update debt levels based on interest rates and repayment behavior"""
        interest_rate = policies.get("interest_rate", 0.05)
        interest_cost = self.debt * interest_rate / 12  # Monthly interest
        
        # Debt repayment from income if employed
        if self.employment_status == EmploymentStatus.EMPLOYED:
            repayment_rate = max(0.1, self.confidence * 0.3)
            disposable = self._calculate_disposable_income(policies)
            repayment = disposable * repayment_rate
            self.debt = max(0, self.debt + interest_cost - repayment)
            self.memory.past_debt_cost.append(interest_cost)
    
    def _update_psychological_state(self, policies: Dict, macro_state: Dict, timestep: int):
        """Update stress, satisfaction, and confidence based on economic conditions"""
        # Income stability affects stress
        if self.employment_status == EmploymentStatus.UNEMPLOYED:
            stress_change = 0.05
        else:
            stress_change = -0.02
        
        # Debt burden affects stress
        debt_ratio = self.debt / max(self.income, 1) if self.income > 0 else 0
        stress_change += debt_ratio * 0.1
        
        # Inflation affects stress and satisfaction
        inflation = macro_state.get("inflation_rate", 0.02)
        if inflation > 0.05:
            stress_change += 0.03
        
        # Wealth status affects confidence and satisfaction
        wealth_level = self.savings - self.debt
        if wealth_level < 0:
            satisfaction_change = -0.1
            confidence_change = -0.15
        else:
            satisfaction_change = 0.02
            confidence_change = 0.05
        
        # Apply changes with bounds
        self.stress_level = max(0, min(1.0, self.stress_level + stress_change))
        self.satisfaction = max(0, min(1.0, self.satisfaction + satisfaction_change))
        self.confidence = max(0, min(1.0, self.confidence + confidence_change))
        
        # Health deteriorates with high stress
        if self.stress_level > 0.7:
            self.health = max(0.4, self.health - 0.01)
        elif self.stress_level < 0.4:
            self.health = min(1.0, self.health + 0.01)
    
    def _update_social_behavior(self, policies: Dict, macro_state: Dict):
        """Update likelihood of protesting and migrating"""
        # Protest probability based on dissatisfaction and stress
        dissatisfaction = 1.0 - self.satisfaction
        economic_hardship = (1.0 - self.confidence) * 0.3 + self.stress_level * 0.3
        
        self.protest_probability = dissatisfaction * self.willingness_to_protest * economic_hardship
        self.protest_probability = min(1.0, self.protest_probability)
        
        # Migration probability based on job prospects and satisfaction
        unemployment_rate = macro_state.get("unemployment_rate", 0.05)
        job_prospects = 1 - unemployment_rate
        
        self.migration_probability = (1.0 - self.satisfaction) * job_prospects * 0.05
        self.migration_probability = min(0.1, self.migration_probability)  # Cap at 10% per month
    
    def get_state(self) -> Dict:
        """Return current state as dictionary"""
        return {
            "id": self.id,
            "age": self.age,
            "sector": self.sector,
            "income": self.income,
            "savings": self.savings,
            "debt": self.debt,
            "employment_status": self.employment_status.name,
            "stress_level": self.stress_level,
            "satisfaction": self.satisfaction,
            "confidence": self.confidence,
            "monthly_spending": self.monthly_spending,
            "wealth": self.savings - self.debt,
            "protest_probability": self.protest_probability,
            "migration_probability": self.migration_probability,
        }