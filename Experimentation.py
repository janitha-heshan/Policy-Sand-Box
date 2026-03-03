"""
Experimentation framework for running multiple scenarios and analyzing results
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Callable
import json
from SimulationEngine import SimulationEngine, SimulationAnalyzer
from Calibration import DataExporter


class Experiment:
    """Represents a single simulation experiment with configuration and results"""
    
    def __init__(self, name: str, description: str, policy_config: Dict):
        self.name = name
        self.description = description
        self.policy_config = policy_config
        self.results = None
        self.simulation = None
        self.metadata = {
            "created_at": pd.Timestamp.now(),
            "status": "pending"
        }
    
    def run(self, population: int = 1000, timesteps: int = 120):
        """Execute the experiment"""
        self.metadata["status"] = "running"
        
        self.simulation = SimulationEngine(population_size=population)
        
        # Apply policy configuration
        for policy_name, value in self.policy_config.items():
            self.simulation.policy_engine.set_policy(policy_name, value)
        
        # Run simulation
        self.results = self.simulation.run_simulation(timesteps=timesteps)
        self.metadata["status"] = "completed"
        
        return self.results
    
    def get_summary(self) -> Dict:
        """Get experiment summary"""
        if not self.results:
            return {}
        
        analyzer = SimulationAnalyzer()
        stats = analyzer.calculate_aggregate_metrics(self.results['statistics_log'])
        
        return {
            "name": self.name,
            "description": self.description,
            "status": self.metadata["status"],
            "final_metrics": {
                "population": self.results['final_population'],
                "unemployment_rate": self.simulation.economy.state.unemployment_rate,
                "inflation_rate": self.simulation.economy.state.inflation_rate,
                "gdp": self.simulation.economy.state.gdp,
                "social_unrest": self.simulation.economy.state.social_unrest_index,
            },
            "aggregate_stats": stats
        }


class ExperimentSuite:
    """Container for running multiple related experiments"""
    
    def __init__(self, name: str):
        self.name = name
        self.experiments: List[Experiment] = []
        self.results = []
    
    def add_experiment(self, experiment: Experiment):
        """Add experiment to suite"""
        self.experiments.append(experiment)
    
    def run_all(self, population: int = 1000, timesteps: int = 120, 
                verbose: bool = True):
        """Run all experiments in suite"""
        for i, experiment in enumerate(self.experiments, 1):
            if verbose:
                print(f"[{i}/{len(self.experiments)}] Running: {experiment.name}")
            
            experiment.run(population, timesteps)
            self.results.append(experiment.get_summary())
            
            if verbose:
                summary = experiment.get_summary()
                print(f"  ✓ Unrest: {summary['final_metrics']['social_unrest']:.2f}")
    
    def compare_results(self) -> pd.DataFrame:
        """Compare results across all experiments"""
        comparison_data = []
        
        for result in self.results:
            comparison_data.append({
                "Experiment": result["name"],
                "Population": result["final_metrics"]["population"],
                "Unemployment": f"{result['final_metrics']['unemployment_rate']*100:.1f}%",
                "Inflation": f"{result['final_metrics']['inflation_rate']*100:.1f}%",
                "GDP": f"{result['final_metrics']['gdp']:.0f}",
                "Social Unrest": f"{result['final_metrics']['social_unrest']:.2f}"
            })
        
        return pd.DataFrame(comparison_data)
    
    def export_results(self, filename: str):
        """Export results to JSON"""
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)


class ExperimentBuilder:
    """Helper class to create standard experiment suites"""
    
    @staticmethod
    def create_policy_sensitivity_suite(policy_name: str, 
                                       values: List[float]) -> ExperimentSuite:
        """Create suite testing different values of a single policy"""
        suite = ExperimentSuite(f"Policy Sensitivity: {policy_name}")
        
        for value in values:
            config = {policy_name: value}
            exp = Experiment(
                name=f"{policy_name} = {value}",
                description=f"Testing {policy_name} at {value}",
                policy_config=config
            )
            suite.add_experiment(exp)
        
        return suite
    
    @staticmethod
    def create_scenario_suite() -> ExperimentSuite:
        """Create suite with realistic policy scenarios"""
        suite = ExperimentSuite("Policy Scenarios")
        
        # Scenario 1: Conservative Economy (Low Spending)
        suite.add_experiment(Experiment(
            name="Conservative Economy",
            description="Low taxes, minimal welfare",
            policy_config={
                "income_tax_rate": 0.15,
                "universal_basic_income": 0,
                "welfare_support": 0,
                "interest_rate": 0.04
            }
        ))
        
        # Scenario 2: Social Market Economy
        suite.add_experiment(Experiment(
            name="Social Market Economy",
            description="Balanced tax and welfare",
            policy_config={
                "income_tax_rate": 0.30,
                "universal_basic_income": 300,
                "welfare_support": 100,
                "interest_rate": 0.03,
                "unemployment_benefit_rate": 0.60
            }
        ))
        
        # Scenario 3: Universal Basic Income
        suite.add_experiment(Experiment(
            name="Universal Basic Income",
            description="Strong UBI with higher taxes",
            policy_config={
                "income_tax_rate": 0.35,
                "universal_basic_income": 1500,
                "welfare_support": 0,
                "interest_rate": 0.02
            }
        ))
        
        # Scenario 4: Green Economy Transition
        suite.add_experiment(Experiment(
            name="Green Energy Transition",
            description="High fuel taxes, green investment",
            policy_config={
                "fuel_tax_rate": 0.40,
                "fuel_price_multiplier": 2.0,
                "income_tax_rate": 0.25,
                "universal_basic_income": 400,
                "welfare_support": 150
            }
        ))
        
        # Scenario 5: Crisis Response
        suite.add_experiment(Experiment(
            name="Financial Crisis Response",
            description="Low rates, high benefits",
            policy_config={
                "interest_rate": 0.00,
                "income_tax_rate": 0.20,
                "unemployment_benefit_rate": 0.80,
                "welfare_support": 300,
                "universal_basic_income": 200
            }
        ))
        
        # Scenario 6: Austerity
        suite.add_experiment(Experiment(
            name="Austerity Program",
            description="High taxes, low spending",
            policy_config={
                "income_tax_rate": 0.40,
                "universal_basic_income": 0,
                "welfare_support": 50,
                "unemployment_benefit_rate": 0.30,
                "interest_rate": 0.05
            }
        ))
        
        return suite
    
    @staticmethod
    def create_inequality_analysis_suite() -> ExperimentSuite:
        """Create suite analyzing impact on wealth inequality"""
        suite = ExperimentSuite("Inequality Analysis")
        
        configs = [
            ("No Redistribution", {
                "income_tax_rate": 0.10,
                "universal_basic_income": 0,
                "welfare_support": 0
            }),
            ("Moderate Redistribution", {
                "income_tax_rate": 0.25,
                "universal_basic_income": 500,
                "welfare_support": 100
            }),
            ("Strong Redistribution", {
                "income_tax_rate": 0.40,
                "universal_basic_income": 1000,
                "welfare_support": 200
            }),
            ("Extreme Redistribution", {
                "income_tax_rate": 0.60,
                "universal_basic_income": 1500,
                "welfare_support": 300
            })
        ]
        
        for name, config in configs:
            suite.add_experiment(Experiment(
                name=name,
                description=f"Wealth redistribution test: {name}",
                policy_config=config
            ))
        
        return suite


class ParameterVaryingExperiment:
    """Run experiment while varying multiple parameters systematically"""
    
    def __init__(self, base_config: Dict, varying_params: Dict):
        """
        Args:
            base_config: Base policy configuration
            varying_params: Dict mapping parameter names to lists of values
        """
        self.base_config = base_config
        self.varying_params = varying_params
        self.results = []
    
    def run_grid_search(self, population: int = 1000, timesteps: int = 60):
        """Run all combinations (full factorial design)"""
        import itertools
        
        # Generate all combinations
        param_names = list(self.varying_params.keys())
        param_values = [self.varying_params[name] for name in param_names]
        
        combinations = list(itertools.product(*param_values))
        
        print(f"Running {len(combinations)} experiments (grid search)...")
        
        for i, combo in enumerate(combinations, 1):
            config = self.base_config.copy()
            
            for param_name, value in zip(param_names, combo):
                config[param_name] = value
            
            exp = Experiment(
                name=f"Config {i}",
                description=str(config),
                policy_config=config
            )
            
            exp.run(population, timesteps)
            summary = exp.get_summary()
            summary['parameter_values'] = dict(zip(param_names, combo))
            self.results.append(summary)
            
            if i % 5 == 0:
                print(f"  {i}/{len(combinations)} completed")
        
        return pd.DataFrame([
            {
                "params": r['parameter_values'],
                "unrest": r['final_metrics']['social_unrest'],
                "unemployment": r['final_metrics']['unemployment_rate'],
                "inequality": r.get('aggregate_stats', {}).get('wealth_inequality_gini_mean', 0)
            }
            for r in self.results
        ])


class SensitivityAnalyzer:
    """Analyze sensitivity of outcomes to parameter changes"""
    
    @staticmethod
    def tornado_analysis(suite: ExperimentSuite, metric: str = "social_unrest"):
        """Create tornado diagram data"""
        impacts = {}
        
        for result in suite.results:
            exp_name = result['name']
            value = result['final_metrics'].get(metric, 0)
            impacts[exp_name] = value
        
        # Sort by magnitude of difference
        sorted_impacts = sorted(
            impacts.items(),
            key=lambda x: abs(x[1]),
            reverse=True
        )
        
        return dict(sorted_impacts)
    
    @staticmethod
    def interaction_analysis(grid_results: pd.DataFrame) -> Dict:
        """Analyze interactions between parameters"""
        interactions = {}
        
        # For each pair of parameters, check if their effects combine linearly
        # or if there's an interaction
        
        return interactions
