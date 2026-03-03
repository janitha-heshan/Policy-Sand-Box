"""
Calibration and validation module for tuning simulation parameters to real-world data
"""
import numpy as np
from typing import Dict, List, Tuple
from dataclasses import dataclass
import json


@dataclass
class HistoricalData:
    """Container for real-world historical economic data"""
    inflation_rates: List[float]
    unemployment_rates: List[float]
    gdp_growth_rates: List[float]
    wage_growth_rates: List[float]
    gini_coefficients: List[float]
    protest_frequency: float  # Protests per year
    migration_rate: float  # % emigration per year
    labor_force_participation: float
    median_debt_to_income: float


class RealWorldCalibration:
    """
    Contains realistic calibration parameters based on OECD, World Bank, and Central Bank data
    """
    
    # Example calibration data for a developed economy
    BASELINE_CALIBRATION = {
        "inflation_target": 0.02,
        "natural_unemployment_rate": 0.05,
        "trend_gdp_growth": 0.025,
        "wage_growth_rate": 0.025,
        "gini_coefficient": 0.35,
        "protest_frequency_per_year": 2.5,
        "annual_migration_rate": 0.005,
        "labor_force_participation": 0.65,
        "median_debt_to_income_ratio": 1.5,
    }
    
    # Shock scenarios based on historical events
    CRISIS_2008_CALIBRATION = {
        "inflation_rate": 0.035,
        "unemployment_rate": 0.09,
        "gdp_growth_rate": -0.04,
        "wage_growth_rate": -0.01,
        "gini_coefficient": 0.38,
        "protest_frequency": 5.0,
        "migration_rate": 0.008,
    }
    
    STAGFLATION_1970S = {
        "inflation_rate": 0.12,
        "unemployment_rate": 0.08,
        "gdp_growth_rate": 0.01,
        "wage_growth_rate": 0.08,
        "gini_coefficient": 0.32,
        "protest_frequency": 8.0,
    }
    
    PANDEMIC_SHOCK = {
        "inflation_rate": 0.025,
        "unemployment_rate": 0.12,
        "gdp_growth_rate": -0.03,
        "wage_growth_rate": 0.0,
        "gini_coefficient": 0.37,
        "protest_frequency": 4.0,
        "migration_rate": 0.002,
    }


class SimulationCalibrator:
    """
    Calibrates simulation parameters to match historical data patterns
    """
    
    def __init__(self):
        self.target_metrics = RealWorldCalibration.BASELINE_CALIBRATION
        self.current_error = float('inf')
        self.calibration_history = []
        
        # Parameter adjustment ranges
        self.parameter_ranges = {
            "consumption_to_inflation_multiplier": (0.05, 0.25),
            "unemployment_to_wage_multiplier": (-1.0, -0.1),
            "inflation_inertia": (0.3, 0.8),
            "job_finding_rate": (0.1, 0.5),
            "wage_flexibility": (0.3, 1.0),
        }
    
    def calculate_calibration_error(self, simulation_results: Dict, 
                                   target_data: Dict = None) -> float:
        """
        Calculate error between simulation and target metrics
        Uses mean squared error normalized by targets
        """
        if target_data is None:
            target_data = RealWorldCalibration.BASELINE_CALIBRATION
        
        metrics = [
            ("inflation_rate", simulation_results.get("inflation_rate", 0)),
            ("unemployment_rate", simulation_results.get("unemployment_rate", 0)),
            ("gini_coefficient", simulation_results.get("wealth_inequality_gini", 0)),
        ]
        
        total_error = 0
        weights = {
            "inflation_rate": 0.3,
            "unemployment_rate": 0.4,
            "gini_coefficient": 0.3,
        }
        
        for metric_name, simulated_value in metrics:
            target_value = target_data.get(metric_name, 0)
            if target_value > 0:
                relative_error = abs(simulated_value - target_value) / target_value
                weight = weights.get(metric_name, 1.0)
                total_error += relative_error * weight
        
        return total_error
    
    def automatic_calibration(self, simulation, iterations: int = 10) -> Dict:
        """
        Automatically adjust economy model parameters to match target data
        Using simple hill-climbing optimization
        """
        best_parameters = {}
        best_error = float('inf')
        
        for iteration in range(iterations):
            # Try small parameter adjustments
            for param_name, (min_val, max_val) in self.parameter_ranges.items():
                # Random adjustment
                adjustment = np.random.uniform(-0.1, 0.1)
                current_value = getattr(simulation.economy, param_name, None)
                
                if current_value is not None:
                    new_value = max(min_val, min(max_val, current_value + adjustment))
                    setattr(simulation.economy, param_name, new_value)
                    
                    # Test new parameters
                    results = simulation.get_results()
                    error = self.calculate_calibration_error({
                        "inflation_rate": simulation.economy.state.inflation_rate,
                        "unemployment_rate": simulation.economy.state.unemployment_rate,
                        "wealth_inequality_gini": simulation.economy.state.wealth_inequality_gini,
                    })
                    
                    if error < best_error:
                        best_error = error
                        best_parameters[param_name] = new_value
                    else:
                        # Revert
                        setattr(simulation.economy, param_name, current_value)
        
        return {
            "best_parameters": best_parameters,
            "calibration_error": best_error,
            "iteration": iteration
        }
    
    def validate_against_shock(self, simulation, scenario: str) -> Dict:
        """
        Validate simulation by running it through a known shock scenario
        
        Args:
            simulation: SimulationEngine instance
            scenario: Name of historical scenario
            
        Returns:
            Validation metrics
        """
        if scenario == "2008_crisis":
            shock_calibration = RealWorldCalibration.CRISIS_2008_CALIBRATION
        elif scenario == "stagflation":
            shock_calibration = RealWorldCalibration.STAGFLATION_1970S
        elif scenario == "pandemic":
            shock_calibration = RealWorldCalibration.PANDEMIC_SHOCK
        else:
            return {}
        
        # Run simulation with shock applied
        simulation.run_simulation(timesteps=60)
        
        # Compare results
        validation_results = {
            "scenario": scenario,
            "metrics_match": {},
            "overall_fit": 0
        }
        
        for metric, target_value in shock_calibration.items():
            simulated_value = getattr(simulation.economy.state, metric, None)
            if simulated_value is not None:
                error = abs(simulated_value - target_value) / target_value
                validation_results["metrics_match"][metric] = {
                    "target": target_value,
                    "simulated": simulated_value,
                    "error": error
                }
        
        return validation_results


class ParameterSensitivityAnalysis:
    """
    Analyzes how sensitive simulation outcomes are to parameter changes
    """
    
    @staticmethod
    def tornado_analysis(base_simulation, parameters: Dict, 
                        output_metric: str = "social_unrest_index") -> Dict:
        """
        Tornado diagram: shows impact of each parameter on output metric
        
        Args:
            base_simulation: Baseline simulation
            parameters: Dict of parameter ranges to test
            output_metric: Output metric to measure
            
        Returns:
            Dict mapping parameters to (low_value, high_value) impacts
        """
        impacts = {}
        
        baseline_value = getattr(base_simulation.economy.state, output_metric, 0)
        
        for param_name, (min_val, max_val) in parameters.items():
            # Test at low value
            setattr(base_simulation.economy, param_name, min_val)
            base_simulation.step()
            low_value = getattr(base_simulation.economy.state, output_metric, 0)
            
            # Test at high value
            setattr(base_simulation.economy, param_name, max_val)
            base_simulation.step()
            high_value = getattr(base_simulation.economy.state, output_metric, 0)
            
            impact_range = abs(high_value - low_value)
            impacts[param_name] = {
                "low": low_value,
                "high": high_value,
                "impact_range": impact_range
            }
        
        # Sort by impact
        sorted_impacts = sorted(impacts.items(), 
                               key=lambda x: x[1]["impact_range"], 
                               reverse=True)
        
        return dict(sorted_impacts)
    
    @staticmethod
    def monte_carlo_sensitivity(simulation, parameters: Dict, 
                               iterations: int = 100) -> Dict:
        """
        Monte Carlo sensitivity: random parameter sampling
        
        Args:
            simulation: SimulationEngine instance
            parameters: Dict of parameter distributions
            iterations: Number of samples
            
        Returns:
            Statistical summary of impacts
        """
        results = {
            "iterations": iterations,
            "parameter_stats": {},
            "output_distribution": []
        }
        
        for i in range(iterations):
            # Random parameter assignment
            for param_name, (min_val, max_val) in parameters.items():
                random_value = np.random.uniform(min_val, max_val)
                setattr(simulation.economy, param_name, random_value)
            
            # Run simulation
            simulation.step()
            
            # Record output
            unrest = simulation.economy.state.social_unrest_index
            results["output_distribution"].append(unrest)
        
        # Calculate statistics
        results["output_mean"] = np.mean(results["output_distribution"])
        results["output_std"] = np.std(results["output_distribution"])
        results["output_min"] = np.min(results["output_distribution"])
        results["output_max"] = np.max(results["output_distribution"])
        
        return results


class DataExporter:
    """
    Export simulation data for external analysis
    """
    
    @staticmethod
    def export_to_csv(simulation, filename: str):
        """Export simulation statistics to CSV"""
        import csv
        
        with open(filename, 'w', newline='') as f:
            if not simulation.statistics_log:
                return
            
            fieldnames = list(simulation.statistics_log[0].keys())
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(simulation.statistics_log)
    
    @staticmethod
    def export_to_json(simulation, filename: str):
        """Export simulation results to JSON"""
        results = simulation.get_results()
        
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2, default=str)
    
    @staticmethod
    def export_citizen_data(simulation, filename: str):
        """Export individual citizen data to CSV"""
        import csv
        
        citizen_data = simulation.get_citizen_data()
        
        with open(filename, 'w', newline='') as f:
            if not citizen_data:
                return
            
            fieldnames = list(citizen_data[0].keys())
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(citizen_data)
