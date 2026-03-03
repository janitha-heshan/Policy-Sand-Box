"""
QUICK START GUIDE
=================

Get started with the Multi-Agent Policy Simulator in 5 minutes!
"""

# Installation
# ============
# 1. Extract the project folder
# 2. Open terminal/PowerShell in the project directory
# 3. Install dependencies:
#    pip install -r requirements.txt

# Quick Test
# ==========
# Run a 5-minute test to verify everything works:

from SimulationEngine import SimulationEngine

print("Testing Multi-Agent Policy Simulator...")
print("Creating simulation with 100 citizens...")

sim = SimulationEngine(population_size=100)
results = sim.run_simulation(timesteps=12)

print(f"\n✓ Simulation Complete!")
print(f"  Population: {results['final_population']}")
print(f"  Unemployment: {sim.economy.state.unemployment_rate*100:.1f}%")
print(f"  Inflation: {sim.economy.state.inflation_rate*100:.1f}%")
print(f"  Social Unrest: {sim.economy.state.social_unrest_index:.2f}")

# Option A: Interactive Dashboard
# ================================
# Run in terminal:
#   streamlit run Dashboard.py
#
# Then open http://localhost:8501 in your browser
# - Adjust policies with sliders
# - See real-time impact on charts
# - Download results as CSV/JSON

# Option B: Command-line Examples
# ===============================
# Run in terminal:
#   python Main.py
#
# Choose from 7 examples:
# 1. Basic 10-year simulation
# 2. Compare 4 policy scenarios
# 3. Sensitivity analysis (tax rates)
# 4. Full scenario comparison
# 5. Individual citizen analysis
# 6. Extreme policy scenarios
# 7. Crisis simulation with policy response

# Option C: Custom Python Script
# ==============================

# Example 1: Test different UBI levels
from SimulationEngine import SimulationEngine
import pandas as pd

print("\n" + "="*50)
print("Testing UBI Policy")
print("="*50)

results = []
for ubi_amount in [0, 500, 1000, 1500]:
    sim = SimulationEngine(population_size=300)
    sim.policy_engine.set_policy("universal_basic_income", ubi_amount)
    sim.run_simulation(timesteps=60)
    
    results.append({
        "UBI ($)": ubi_amount,
        "Unemployment (%)": f"{sim.economy.state.unemployment_rate*100:.1f}",
        "Social Unrest": f"{sim.economy.state.social_unrest_index:.2f}",
        "Final Population": len(sim.citizens)
    })

df = pd.DataFrame(results)
print(df.to_string(index=False))

# Example 2: Crisis and Recovery Scenario
print("\n" + "="*50)
print("Crisis & Recovery")
print("="*50)

sim = SimulationEngine(population_size=500)

print("Phase 1: Normal Economy")
sim.policy_engine.set_policy("interest_rate", 0.05)
sim.run_simulation(timesteps=24)
normal_unemployment = sim.economy.state.unemployment_rate

print(f"  Unemployment: {normal_unemployment*100:.1f}%")

print("Phase 2: Crisis Response")
sim.policy_engine.set_policy("interest_rate", 0.0)
sim.policy_engine.set_policy("unemployment_benefit_rate", 0.8)
sim.run_simulation(timesteps=12)
crisis_unemployment = sim.economy.state.unemployment_rate

print(f"  Unemployment: {crisis_unemployment*100:.1f}%")

print("Phase 3: Recovery")
sim.policy_engine.set_policy("unemployment_benefit_rate", 0.6)
sim.run_simulation(timesteps=24)
recovery_unemployment = sim.economy.state.unemployment_rate

print(f"  Unemployment: {recovery_unemployment*100:.1f}%")

# Example 3: Compare Pre-built Scenarios
print("\n" + "="*50)
print("Scenario Comparison")
print("="*50)

from Experimentation import ExperimentBuilder

suite = ExperimentBuilder.create_scenario_suite()
suite.run_all(population=300, timesteps=60, verbose=False)
print(suite.compare_results().to_string(index=False))

# Example 4: Export Data
print("\n" + "="*50)
print("Export & Analysis")
print("="*50)

sim = SimulationEngine(population_size=200)
sim.run_simulation(timesteps=60)

from Calibration import DataExporter

# Export to files
DataExporter.export_to_csv(sim, "simulation_stats.csv")
DataExporter.export_to_json(sim, "simulation_results.json")
DataExporter.export_citizen_data(sim, "citizens.csv")

print("✓ Files exported:")
print("  - simulation_stats.csv")
print("  - simulation_results.json")
print("  - citizens.csv")

# Key Metrics to Watch
# ====================
# 
# 1. Social Unrest Index (0-1 scale)
#    - 0.0-0.3: Stable
#    - 0.3-0.6: Growing discontent
#    - 0.6+: Crisis (high migration, protests)
#
# 2. Unemployment Rate
#    - <5%: Healthy
#    - 5-8%: Normal range
#    - >8%: Recession conditions
#
# 3. Inflation Rate
#    - 1-3%: Target range
#    - >5%: Problematic
#
# 4. Wealth Inequality (Gini coefficient)
#    - <0.3: Very equal
#    - 0.3-0.4: Moderate inequality
#    - >0.4: High inequality
#
# 5. Average Citizen Stress
#    - <0.4: Content
#    - 0.4-0.7: Anxious
#    - >0.7: Crisis

# Common Questions
# ================
#
# Q: How do I run a 20-year simulation?
# A: sim.run_simulation(timesteps=240)  # 240 months = 20 years
#
# Q: How do I test multiple policies at once?
# A: Use the Experimentation module to create scenario suites
#
# Q: How do I export my results?
# A: Use DataExporter.export_to_csv() or export_to_json()
#
# Q: Why is social unrest high?
# A: Check unemployment, inequality, and inflation together
#
# Q: Can I modify agent behavior?
# A: Edit Citizen.py to customize decision-making logic

print("\n" + "="*50)
print("🎉 Ready to explore policy impacts!")
print("="*50)
print("\nNext steps:")
print("1. Run: python Main.py (for interactive menu)")
print("2. Or: streamlit run Dashboard.py (for web interface)")
print("3. Or: Create custom scripts using the examples above")
