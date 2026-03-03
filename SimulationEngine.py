"""
Core simulation engine managing the overall simulation loop and agent interactions
"""
import numpy as np
from typing import List, Dict, Tuple
import random
from Citizen import Citizen, EmploymentStatus
from EconomyModel import EconomyModel
from PolicyEngine import PolicyEngine


class SimulationEngine:
    """
    Main simulation loop coordinating all components
    """
    
    def __init__(self, population_size: int = 1000, initial_age_distribution: str = "realistic"):
        """
        Initialize simulation
        
        Args:
            population_size: Number of citizens to simulate
            initial_age_distribution: "realistic" or "uniform"
        """
        self.timestep = 0
        self.population_size = population_size
        
        # Initialize components
        self.citizens: List[Citizen] = []
        self.economy = EconomyModel()
        self.policy_engine = PolicyEngine()
        
        # Statistics tracking
        self.statistics_log = []
        self.protest_events = []
        self.migration_events = []
        self.simulation_config = {
            "population_size": population_size,
            "start_date": "2024-01",
            "time_step_unit": "month"
        }
        
        # Initialize citizens
        self._initialize_population(population_size, initial_age_distribution)
    
    def _initialize_population(self, population_size: int, age_distribution: str):
        """Initialize citizen population"""
        random.seed(42)  # For reproducibility
        np.random.seed(42)
        
        if age_distribution == "realistic":
            # Realistic age distribution (roughly bell curve 18-75)
            ages = np.random.normal(45, 15, population_size)
            ages = np.clip(ages, 18, 75).astype(int)
        else:
            # Uniform distribution
            ages = np.random.uniform(18, 75, population_size).astype(int)
        
        # Sector distribution
        sectors = np.random.choice(["tech", "manufacturing", "service", "agriculture"], 
                                   population_size, 
                                   p=[0.2, 0.25, 0.35, 0.2])
        
        for age, sector in zip(ages, sectors):
            citizen = Citizen(age, sector)
            self.citizens.append(citizen)
    
    def run_simulation(self, timesteps: int = 120, callback=None) -> Dict:
        """
        Run simulation for specified number of timesteps
        
        Args:
            timesteps: Number of months to simulate
            callback: Optional function to call each timestep with progress info
            
        Returns:
            Dictionary with simulation results
        """
        print(f"Starting simulation with {len(self.citizens)} citizens for {timesteps} months...")
        
        for t in range(timesteps):
            self.step()
            
            if callback:
                callback(t, timesteps, self.get_current_state())
            
            if (t + 1) % 12 == 0:
                print(f"  Year {(t + 1) // 12} completed - "
                      f"Unemployment: {self.economy.state.unemployment_rate*100:.1f}%, "
                      f"Inflation: {self.economy.state.inflation_rate*100:.1f}%, "
                      f"Unrest: {self.economy.state.social_unrest_index:.2f}")
        
        print("Simulation complete!")
        return self.get_results()
    
    def step(self):
        """Execute one timestep"""
        policies = self.policy_engine.get_policies()
        macro_state = self.economy.state.__dict__
        
        # 1. Update all citizens
        for citizen in self.citizens:
            citizen.update_monthly(policies, macro_state, self.timestep)
        
        # 2. Process social events (protests, migration)
        self._process_protests()
        self._process_migration()
        
        # 3. Update economy
        self.economy.update(self.citizens, policies, self.timestep)
        
        # 4. Log statistics
        self._log_statistics()
        
        self.timestep += 1
    
    def _process_protests(self):
        """Handle protest events and their effects"""
        protesters = [c for c in self.citizens if random.random() < c.protest_probability]
        
        if protesters:
            protest_size = len(protesters)
            protest_pct = protest_size / len(self.citizens)
            
            # Large protests can trigger policy pressure
            if protest_pct > 0.1:  # More than 10% protesting
                self._apply_protest_effects(protest_size)
                self.protest_events.append({
                    "timestep": self.timestep,
                    "size": protest_size,
                    "percentage": protest_pct
                })
                
                print(f"  [Timestep {self.timestep}] {protest_size} citizens ({protest_pct*100:.1f}%) protested!")
    
    def _apply_protest_effects(self, protest_size: int):
        """Apply effects of large protests"""
        protest_influence = protest_size / len(self.citizens)
        
        # Reduce government satisfaction/trust
        for citizen in self.citizens:
            citizen.stress_level = min(1.0, citizen.stress_level + protest_influence * 0.05)
            citizen.satisfaction = max(0, citizen.satisfaction - protest_influence * 0.1)
    
    def _process_migration(self):
        """Handle migration (citizens leaving the economy)"""
        migrants = [c for c in self.citizens if random.random() < c.migration_probability]
        
        for migrant in migrants:
            self.citizens.remove(migrant)
            self.migration_events.append({
                "timestep": self.timestep,
                "age": migrant.age,
                "sector": migrant.sector,
                "wealth": migrant.savings - migrant.debt
            })
        
        if migrants:
            print(f"  [Timestep {self.timestep}] {len(migrants)} citizens migrated")
    
    def _log_statistics(self):
        """Log current simulation statistics"""
        stats = {
            "timestep": self.timestep,
            "citizen_count": len(self.citizens),
            "avg_age": np.mean([c.age for c in self.citizens]),
            "avg_income": np.mean([c.income for c in self.citizens]),
            "avg_savings": np.mean([c.savings for c in self.citizens]),
            "avg_debt": np.mean([c.debt for c in self.citizens]),
            "avg_stress": np.mean([c.stress_level for c in self.citizens]),
            "avg_satisfaction": np.mean([c.satisfaction for c in self.citizens]),
            "avg_confidence": np.mean([c.confidence for c in self.citizens]),
            "employment_rate": sum(1 for c in self.citizens if c.employment_status == EmploymentStatus.EMPLOYED) / len(self.citizens),
        }
        stats.update(self.economy.get_state())
        self.statistics_log.append(stats)
    
    def get_current_state(self) -> Dict:
        """Get current simulation state"""
        return {
            "timestep": self.timestep,
            "citizens_count": len(self.citizens),
            "economy": self.economy.get_state(),
            "policies": self.policy_engine.get_policies(),
        }
    
    def get_results(self) -> Dict:
        """Get comprehensive simulation results"""
        return {
            "config": self.simulation_config,
            "timesteps_executed": self.timestep,
            "final_population": len(self.citizens),
            "statistics_log": self.statistics_log,
            "protest_events": self.protest_events,
            "migration_events": self.migration_events,
            "policy_history": self.policy_engine.policy_history,
        }
    
    def get_citizen_data(self) -> List[Dict]:
        """Get data for all citizens"""
        return [c.get_state() for c in self.citizens]
    
    def analyze_policy_sensitivity(self, policy_name: str, values: List[float], 
                                   timesteps: int = 60) -> Dict:
        """
        Run multiple simulations with different policy values to test sensitivity
        
        Args:
            policy_name: Name of policy to vary
            values: List of values to test
            timesteps: Timesteps per simulation
            
        Returns:
            Dictionary with results for each value
        """
        results = {}
        
        for value in values:
            # Reset simulation
            original_state = self.timestep
            original_citizens = self.citizens.copy()
            
            # Set policy
            self.policy_engine.set_policy(policy_name, value)
            
            # Run simulation
            end_state = self.get_results()
            final_unrest = self.economy.state.social_unrest_index
            final_gdp = self.economy.state.gdp
            final_unemployment = self.economy.state.unemployment_rate
            
            results[value] = {
                "final_unrest": final_unrest,
                "final_gdp": final_gdp,
                "final_unemployment": final_unemployment,
                "avg_citizen_satisfaction": np.mean([c.satisfaction for c in self.citizens]),
            }
            
            # Restore state
            self.timestep = original_state
            self.citizens = original_citizens
        
        return results


class SimulationAnalyzer:
    """
    Post-simulation analysis and visualization support
    """
    
    @staticmethod
    def calculate_aggregate_metrics(stats_log: List[Dict]) -> Dict:
        """Calculate aggregate metrics from simulation"""
        if not stats_log:
            return {}
        
        keys = ["avg_income", "avg_stress", "avg_satisfaction", "unemployment_rate", 
                "inflation_rate", "social_unrest_index"]
        
        metrics = {}
        for key in keys:
            values = [s[key] for s in stats_log if key in s]
            if values:
                metrics[f"{key}_mean"] = np.mean(values)
                metrics[f"{key}_std"] = np.std(values)
                metrics[f"{key}_min"] = np.min(values)
                metrics[f"{key}_max"] = np.max(values)
        
        return metrics
    
    @staticmethod
    def identify_key_periods(stats_log: List[Dict]) -> List[Dict]:
        """Identify significant periods in simulation"""
        periods = []
        
        unrest_threshold = 0.6
        unemployment_threshold = 0.1
        
        for i, stat in enumerate(stats_log):
            if stat.get("social_unrest_index", 0) > unrest_threshold:
                periods.append({
                    "type": "high_unrest",
                    "timestep": i,
                    "value": stat["social_unrest_index"]
                })
            
            if stat.get("unemployment_rate", 0) > unemployment_threshold:
                periods.append({
                    "type": "high_unemployment",
                    "timestep": i,
                    "value": stat["unemployment_rate"]
                })
        
        return periods
