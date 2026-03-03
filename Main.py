"""
Multi-Agent Human Society Policy Simulator
==========================================

A comprehensive simulation framework for modeling how government policies affect
economic outcomes, citizen wellbeing, and social dynamics.

FEATURES:
- 1000+ agents with realistic economic behavior and learning
- Real-time policy adjustment and impact analysis
- Macroeconomic modeling (inflation, unemployment, GDP, inequality)
- Behavioral economics (stress, satisfaction, confidence, protests, migration)
- Reinforcement learning for agent adaptation
- Interactive Streamlit dashboard
- Historical data calibration
- Sensitivity analysis and policy experimentation

USAGE:
1. Run this file directly for command-line experiments
2. Run: streamlit run Dashboard.py for interactive dashboard
3. Customize experiments in the examples below
"""

from SimulationEngine import SimulationEngine, SimulationAnalyzer
from PolicyEngine import PolicyEngine
from Experimentation import ExperimentBuilder, ExperimentSuite, Experiment
from Calibration import DataExporter, SimulationCalibrator
import pandas as pd
import numpy as np


def example_1_basic_simulation():
    """Example 1: Run a basic 10-year simulation"""
    print("\n" + "="*60)
    print("EXAMPLE 1: Basic 10-Year Simulation")
    print("="*60)
    
    # Create simulation with 1000 citizens
    sim = SimulationEngine(population_size=1000)
    
    # Run for 120 months (10 years)
    results = sim.run_simulation(timesteps=120)
    
    # Print summary
    print(f"\nFinal Results:")
    print(f"  Population: {results['final_population']:,}")
    print(f"  Final Unemployment: {sim.economy.state.unemployment_rate*100:.1f}%")
    print(f"  Final Inflation: {sim.economy.state.inflation_rate*100:.1f}%")
    print(f"  Final GDP: {sim.economy.state.gdp:,.0f}")
    print(f"  Social Unrest Index: {sim.economy.state.social_unrest_index:.2f}")
    print(f"  Wealth Inequality (Gini): {sim.economy.state.wealth_inequality_gini:.3f}")


def example_2_policy_scenarios():
    """Example 2: Compare different policy scenarios"""
    print("\n" + "="*60)
    print("EXAMPLE 2: Policy Scenario Comparison")
    print("="*60)
    
    scenarios = [
        ("Default Economy", {}),
        ("High Tax (50%)", {"income_tax_rate": 0.5}),
        ("Universal Basic Income", {"universal_basic_income": 1000}),
        ("Green Energy Tax", {"fuel_tax_rate": 0.3, "fuel_price_multiplier": 1.8}),
    ]
    
    results_summary = []
    
    for scenario_name, policies in scenarios:
        print(f"\nRunning: {scenario_name}...")
        
        sim = SimulationEngine(population_size=500)
        
        # Apply policies
        for policy_name, value in policies.items():
            sim.policy_engine.set_policy(policy_name, value)
        
        # Run 60 months
        sim.run_simulation(timesteps=60)
        
        results_summary.append({
            "Scenario": scenario_name,
            "Unemployment": f"{sim.economy.state.unemployment_rate*100:.1f}%",
            "Inflation": f"{sim.economy.state.inflation_rate*100:.1f}%",
            "Unrest": f"{sim.economy.state.social_unrest_index:.2f}",
            "GDP": f"{sim.economy.state.gdp:,.0f}"
        })
    
    df = pd.DataFrame(results_summary)
    print("\n" + "="*60)
    print("SCENARIO COMPARISON")
    print("="*60)
    print(df.to_string(index=False))


def example_3_policy_sensitivity():
    """Example 3: Analyze sensitivity to income tax rate"""
    print("\n" + "="*60)
    print("EXAMPLE 3: Policy Sensitivity Analysis")
    print("="*60)
    print("Testing: How does income tax rate affect outcomes?")
    
    tax_rates = [0.1, 0.2, 0.3, 0.4, 0.5]
    results = []
    
    for rate in tax_rates:
        print(f"  Testing tax rate: {rate*100:.0f}%...", end=" ")
        
        sim = SimulationEngine(population_size=300)
        sim.policy_engine.set_policy("income_tax_rate", rate)
        sim.run_simulation(timesteps=60)
        
        results.append({
            "Tax Rate": f"{rate*100:.0f}%",
            "Unemployment": f"{sim.economy.state.unemployment_rate*100:.1f}%",
            "Inflation": f"{sim.economy.state.inflation_rate*100:.1f}%",
            "Unrest": f"{sim.economy.state.social_unrest_index:.2f}",
            "Avg Income": f"{np.mean([c.income for c in sim.citizens]):.0f}"
        })
        print("✓")
    
    df = pd.DataFrame(results)
    print("\n" + "="*60)
    print("SENSITIVITY RESULTS")
    print("="*60)
    print(df.to_string(index=False))


def example_4_experiment_suite():
    """Example 4: Run full experiment suite"""
    print("\n" + "="*60)
    print("EXAMPLE 4: Complete Policy Scenario Suite")
    print("="*60)
    
    # Create scenario suite
    suite = ExperimentBuilder.create_scenario_suite()
    
    # Run all experiments
    suite.run_all(population=500, timesteps=60, verbose=True)
    
    # Compare results
    print("\n" + "="*60)
    print("EXPERIMENT RESULTS COMPARISON")
    print("="*60)
    comparison = suite.compare_results()
    print(comparison.to_string(index=False))
    
    # Export results
    DataExporter.export_results(suite, "experiment_results.json")
    print("\n✓ Results exported to experiment_results.json")


def example_5_citizen_analysis():
    """Example 5: Deep dive into individual citizen behavior"""
    print("\n" + "="*60)
    print("EXAMPLE 5: Individual Citizen Analysis")
    print("="*60)
    
    sim = SimulationEngine(population_size=100)
    sim.run_simulation(timesteps=60)
    
    # Get citizen data
    citizen_data = sim.get_citizen_data()
    df_citizens = pd.DataFrame(citizen_data)
    
    print("\nCitizen Demographics:")
    print(f"  Average age: {df_citizens['age'].mean():.1f} years")
    print(f"  Age range: {df_citizens['age'].min()}-{df_citizens['age'].max()}")
    
    print("\nCitizen Economics:")
    print(f"  Average income: ${df_citizens['income'].mean():.0f}")
    print(f"  Average savings: ${df_citizens['savings'].mean():.0f}")
    print(f"  Average debt: ${df_citizens['debt'].mean():.0f}")
    print(f"  Average wealth: ${(df_citizens['savings'] - df_citizens['debt']).mean():.0f}")
    
    print("\nCitizen Wellbeing:")
    print(f"  Average stress: {df_citizens['stress_level'].mean():.2f}/1.0")
    print(f"  Average satisfaction: {df_citizens['satisfaction'].mean():.2f}/1.0")
    print(f"  Average confidence: {df_citizens['confidence'].mean():.2f}/1.0")
    
    print("\nEmployment:")
    employment_counts = df_citizens['employment_status'].value_counts()
    for status, count in employment_counts.items():
        print(f"  {status}: {count} ({count/len(df_citizens)*100:.1f}%)")


def example_6_extreme_scenarios():
    """Example 6: Test extreme/hypothetical policies"""
    print("\n" + "="*60)
    print("EXAMPLE 6: Extreme Policy Scenarios")
    print("="*60)
    
    extreme_scenarios = [
        ("70% Tax + Strong UBI", {
            "income_tax_rate": 0.70,
            "universal_basic_income": 2000,
            "welfare_support": 300
        }),
        ("Massive Fuel Price Increase", {
            "fuel_price_multiplier": 3.0,
            "fuel_tax_rate": 0.5
        }),
        ("Zero Interest Rate + High Welfare", {
            "interest_rate": 0.0,
            "unemployment_benefit_rate": 0.9,
            "welfare_support": 500
        }),
        ("Ultra-Libertarian (Min Gov)", {
            "income_tax_rate": 0.05,
            "interest_rate": 0.02,
            "universal_basic_income": 0,
            "welfare_support": 0
        })
    ]
    
    results = []
    
    for scenario_name, policies in extreme_scenarios:
        print(f"\nTesting: {scenario_name}...")
        
        sim = SimulationEngine(population_size=500)
        
        for policy_name, value in policies.items():
            sim.policy_engine.set_policy(policy_name, value)
        
        sim.run_simulation(timesteps=60)
        
        # Check for instability
        unrest_trend = sim.economy.state.unrest_history[-10:] if sim.economy.state.unrest_history else []
        avg_unrest = np.mean(unrest_trend) if unrest_trend else 0
        
        results.append({
            "Scenario": scenario_name,
            "Final Unrest": f"{sim.economy.state.social_unrest_index:.2f}",
            "Avg Unrest (last 10m)": f"{avg_unrest:.2f}",
            "Population": sim.population_size - len(sim.citizens),
            "Unemployment": f"{sim.economy.state.unemployment_rate*100:.1f}%"
        })
    
    df = pd.DataFrame(results)
    print("\n" + "="*60)
    print("EXTREME SCENARIO RESULTS")
    print("="*60)
    print(df.to_string(index=False))


def example_7_crisis_simulation():
    """Example 7: Simulate a financial crisis and recovery"""
    print("\n" + "="*60)
    print("EXAMPLE 7: Financial Crisis Simulation")
    print("="*60)
    
    sim = SimulationEngine(population_size=500)
    
    print("\nPhase 1: Normal Economy (Months 1-24)")
    sim.policy_engine.set_policy("interest_rate", 0.05)
    sim.run_simulation(timesteps=24)
    
    normal_state = {
        "unemployment": sim.economy.state.unemployment_rate,
        "inflation": sim.economy.state.inflation_rate,
        "gdp": sim.economy.state.gdp
    }
    
    print(f"  Unemployment: {normal_state['unemployment']*100:.1f}%")
    print(f"  Inflation: {normal_state['inflation']*100:.1f}%")
    print(f"  GDP: {normal_state['gdp']:,.0f}")
    
    print("\nPhase 2: Crisis Hits (Months 25-36)")
    print("  Policy response: Interest rate → 0%, Enhanced benefits")
    sim.policy_engine.set_policy("interest_rate", 0.0)
    sim.policy_engine.set_policy("unemployment_benefit_rate", 0.8)
    sim.policy_engine.set_policy("welfare_support", 300)
    sim.run_simulation(timesteps=12)
    
    crisis_state = {
        "unemployment": sim.economy.state.unemployment_rate,
        "inflation": sim.economy.state.inflation_rate,
        "gdp": sim.economy.state.gdp
    }
    
    print(f"  Unemployment: {crisis_state['unemployment']*100:.1f}%")
    print(f"  Inflation: {crisis_state['inflation']*100:.1f}%")
    print(f"  GDP: {crisis_state['gdp']:,.0f}")
    
    print("\nPhase 3: Recovery (Months 37-60)")
    print("  Stimulus gradually wound down")
    sim.policy_engine.set_policy("unemployment_benefit_rate", 0.6)
    sim.policy_engine.set_policy("welfare_support", 150)
    sim.run_simulation(timesteps=24)
    
    recovery_state = {
        "unemployment": sim.economy.state.unemployment_rate,
        "inflation": sim.economy.state.inflation_rate,
        "gdp": sim.economy.state.gdp
    }
    
    print(f"  Unemployment: {recovery_state['unemployment']*100:.1f}%")
    print(f"  Inflation: {recovery_state['inflation']*100:.1f}%")
    print(f"  GDP: {recovery_state['gdp']:,.0f}")
    
    print("\nCRISIS IMPACT ANALYSIS")
    print(f"  Unemployment increase: {(crisis_state['unemployment'] - normal_state['unemployment'])*100:.1f}pp")
    print(f"  GDP change: {(recovery_state['gdp'] - normal_state['gdp'])/normal_state['gdp']*100:.1f}%")


def main():
    """Run all examples"""
    print("\n" + "█"*60)
    print("█ MULTI-AGENT POLICY SIMULATOR - EXAMPLES")
    print("█"*60)
    
    examples = [
        ("1", "Basic Simulation", example_1_basic_simulation),
        ("2", "Policy Scenario Comparison", example_2_policy_scenarios),
        ("3", "Sensitivity Analysis", example_3_policy_sensitivity),
        ("4", "Experiment Suite", example_4_experiment_suite),
        ("5", "Citizen Analysis", example_5_citizen_analysis),
        ("6", "Extreme Scenarios", example_6_extreme_scenarios),
        ("7", "Crisis Simulation", example_7_crisis_simulation),
    ]
    
    print("\nAvailable Examples:")
    for num, title, _ in examples:
        print(f"  {num}. {title}")
    print("  0. Run All Examples")
    print("  D. Interactive Dashboard (requires Streamlit)")
    
    choice = input("\nSelect example to run (0-7, D, or Q to quit): ").strip().upper()
    
    if choice == "Q":
        print("Exiting...")
        return
    
    elif choice == "D":
        print("\nLaunching interactive dashboard...")
        print("Run: streamlit run Dashboard.py")
        return
    
    elif choice == "0":
        for num, title, func in examples:
            try:
                func()
            except Exception as e:
                print(f"\n⚠ Error in Example {num}: {e}")
    
    else:
        for num, title, func in examples:
            if num == choice:
                try:
                    func()
                except Exception as e:
                    print(f"\n⚠ Error: {e}")
                    import traceback
                    traceback.print_exc()
                return
        
        print("Invalid selection")


if __name__ == "__main__":
    main()