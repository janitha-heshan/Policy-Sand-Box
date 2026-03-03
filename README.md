# Multi-Agent Human Society Policy Simulator

A sophisticated simulation framework for modeling how government policies affect economic outcomes, citizen wellbeing, and social dynamics in a society of 1000+ agents.

## Overview

This simulator models a complete micro-economic society with realistic agents that have:
- **Economic attributes**: Income, savings, debt, employment status
- **Behavioral traits**: Stress, satisfaction, confidence, spending preferences
- **Learning capabilities**: Agents adapt behavior based on past experiences using reinforcement learning
- **Social dynamics**: Protests, migration, and dissatisfaction

The simulation tracks macroeconomic variables (inflation, unemployment, GDP, inequality) and allows users to adjust government policies in real-time to observe impacts.

## Project Structure

### Core Modules

1. **Citizen.py** - Individual agent model
   - `Citizen` class with realistic attributes and decision-making logic
   - `CitizenMemory` class for learning and experience tracking
   - Monthly updates including employment, income, spending, debt, and psychological state changes

2. **EconomyModel.py** - Macroeconomic dynamics
   - `EconomicState` dataclass tracking economy-wide variables
   - `EconomyModel` class managing inflation, unemployment, GDP, wealth distribution
   - Real relationships between consumption, money supply, employment, and inflation

3. **PolicyEngine.py** - Government policy management
   - `PolicySet` dataclass for all policy variables
   - `PolicyEngine` class for dynamic policy adjustment
   - Pre-built scenario functions (crisis response, UBI, green energy, etc.)

4. **SimulationEngine.py** - Core simulation loop
   - `SimulationEngine` orchestrating the monthly timestep loop
   - Agent updates, social event processing, economy updates
   - `SimulationAnalyzer` for post-simulation analysis

5. **Learning.py** - Agent learning and adaptation
   - `ReinforcementLearner` implementing Q-learning for agent behavior
   - `UtilityFunction` using economic utility theory
   - `BehavioralLearningAgent` combining learning with utility maximization

6. **Dashboard.py** - Interactive Streamlit interface
   - Real-time visualization of economic trends
   - Policy adjustment sliders
   - Charts for inflation, unemployment, GDP, social unrest
   - Event logging (protests, migration)
   - Data export functionality

7. **Calibration.py** - Parameter tuning and validation
   - `RealWorldCalibration` with historical economic data
   - `SimulationCalibrator` for automatic parameter adjustment
   - `ParameterSensitivityAnalysis` for tornado and Monte Carlo analysis

8. **Experimentation.py** - Scenario testing framework
   - `Experiment` class for individual simulations
   - `ExperimentSuite` for running multiple experiments
   - `ExperimentBuilder` with pre-built scenario suites
   - `ParameterVaryingExperiment` for grid search and sensitivity analysis

### Run Files

- **Main.py** - Command-line interface with 7 example scenarios
- **Dashboard.py** - Interactive web dashboard (requires Streamlit)

## Key Features

### 1. Agent Model
- **1000+ individual agents** with realistic demographics and economics
- **Dynamic employment status** (employed, unemployed, retired, student)
- **Behavioral feedback loops**: Stress → spending → inflation → stress
- **Learning from experience**: Agents improve decisions over time

### 2. Economic Dynamics
- **Inflation modeling**: Consumption-driven and cost-push inflation
- **Employment dynamics**: Job loss/finding based on economic conditions
- **Wage dynamics**: Inflation pass-through and labor market effects
- **GDP calculation**: Based on consumption, investment, and government spending

### 3. Policy Engine
Dynamically adjust policies:
- Income tax rate (0-70%)
- Interest rate (0-15%)
- Fuel/energy tax (0-50%)
- Unemployment benefits (0-100%)
- Universal basic income (0-$2000/month)
- Welfare support (0-$500/month)

### 4. Behavioral Layer
- **Stress system**: Affects spending, health, and protest probability
- **Satisfaction tracking**: Overall life quality metric
- **Economic confidence**: Affects savings and borrowing decisions
- **Social unrest index**: Aggregate measure combining unemployment, inequality, inflation

### 5. Learning & Adaptation
- **Q-learning**: Agents learn which actions improve their situation
- **State discretization**: Agents track (employment, wealth, stress) states
- **Utility maximization**: Economic preferences influence consumption/saving
- **Habit formation**: Consumption preferences adapt over time

### 6. Scenarios Included

Pre-built policy scenarios:
- **Conservative Economy**: Low taxes, minimal welfare
- **Social Market Economy**: Balanced tax and welfare
- **Universal Basic Income**: Strong UBI with higher taxes
- **Green Energy Transition**: High fuel taxes for renewable incentives
- **Financial Crisis Response**: Zero rates and enhanced benefits
- **Austerity Program**: High taxes, low spending

### 7. Analysis Tools

- **Sensitivity analysis**: Tornado diagrams showing parameter impacts
- **Scenario comparison**: Side-by-side policy outcome analysis
- **Historical calibration**: Match simulation to real-world data patterns
- **Crisis simulation**: Model pre/during/post crisis scenarios
- **Inequality analysis**: Deep dive into wealth distribution effects

## Getting Started

### Installation

```bash
# Clone or extract the project
cd "Policy Sand Box"

# Install dependencies
pip install numpy pandas streamlit plotly
```

### Quick Start

**Option 1: Command-line examples**
```bash
python Main.py
```
Choose from 7 different example scenarios to run.

**Option 2: Interactive Dashboard**
```bash
streamlit run Dashboard.py
```
Opens a web interface for real-time policy adjustment and visualization.

## Usage Examples

### Example 1: Basic Simulation
```python
from SimulationEngine import SimulationEngine

sim = SimulationEngine(population_size=1000)
results = sim.run_simulation(timesteps=120)  # 10 years
```

### Example 2: Policy Comparison
```python
sim = SimulationEngine(population_size=1000)

# Set policy
sim.policy_engine.set_policy("universal_basic_income", 1000)
sim.policy_engine.set_policy("income_tax_rate", 0.35)

# Run simulation
sim.run_simulation(timesteps=120)

# Check results
print(f"Unrest: {sim.economy.state.social_unrest_index:.2f}")
print(f"Unemployment: {sim.economy.state.unemployment_rate*100:.1f}%")
```

### Example 3: Sensitivity Analysis
```python
from Experimentation import ExperimentBuilder

# Test different UBI levels
suite = ExperimentBuilder.create_policy_sensitivity_suite(
    "universal_basic_income",
    [0, 500, 1000, 1500, 2000]
)

suite.run_all(population=500, timesteps=60)
comparison = suite.compare_results()
print(comparison)
```

### Example 4: Crisis Scenario
```python
sim = SimulationEngine(population_size=500)

# Normal economy
sim.policy_engine.set_policy("interest_rate", 0.05)
sim.run_simulation(timesteps=24)

# Crisis hits - policy response
sim.policy_engine.set_policy("interest_rate", 0.0)
sim.policy_engine.set_policy("unemployment_benefit_rate", 0.8)
sim.run_simulation(timesteps=12)

# Recovery
sim.policy_engine.set_policy("unemployment_benefit_rate", 0.6)
sim.run_simulation(timesteps=24)
```

## Understanding the Simulation

### Time Scale
- Each timestep = 1 month
- 120 timesteps = 10 years
- Citizens age in real-time

### Key Economic Relationships

1. **Inflation**: Driven by consumption relative to production
   - Higher consumption → Higher inflation
   - Inflation lags (inertia effect)
   - Supply shocks (fuel prices) cause immediate inflation spikes

2. **Unemployment**: Determined by job loss/finding rates
   - Employment decreases with high unemployment (discouraged workers)
   - Job finding increases with economic growth
   - Wage effects: High unemployment suppresses wage growth

3. **Citizen Behavior**: Based on psychological and economic factors
   - High stress → Increased spending (coping behavior)
   - High debt → Reduced consumption and increased stress
   - Job loss → Immediate stress increase, confidence drop

4. **Social Unrest**: Aggregate of individual grievances
   - Unemployment + Inequality + Inflation drive unrest
   - High unrest leads to protests and migration
   - Can reach critical threshold (>0.6) indicating system instability

### Calibration to Reality

The simulation is calibrated to match real-world patterns:
- **Baseline unemployment**: ~5% natural rate
- **Target inflation**: ~2% (standard central bank target)
- **Wage growth**: Partially follows inflation (wage-price spiral)
- **Inequality**: Gini coefficient tracking wealth concentration
- **Employment sensitivity**: Job loss increases with economic downturn

## Advanced Features

### Parameter Sensitivity Analysis

Test how sensitive outcomes are to parameter changes:
```python
from Calibration import ParameterSensitivityAnalysis

sensitivity = ParameterSensitivityAnalysis.tornado_analysis(
    sim,
    {"consumption_to_inflation_multiplier": (0.05, 0.25)},
    output_metric="social_unrest_index"
)
```

### Scenario Analysis with Grid Search

Test all combinations of multiple parameters:
```python
from Experimentation import ParameterVaryingExperiment

exp = ParameterVaryingExperiment(
    base_config={"interest_rate": 0.05},
    varying_params={
        "income_tax_rate": [0.2, 0.3, 0.4],
        "universal_basic_income": [0, 500, 1000]
    }
)

results = exp.run_grid_search(population=300, timesteps=60)
```

### Data Export

Export simulation results for external analysis:
```python
from Calibration import DataExporter

DataExporter.export_to_csv(sim, "simulation_data.csv")
DataExporter.export_to_json(sim, "results.json")
DataExporter.export_citizen_data(sim, "citizens.csv")
```

## Interpretation Guide

### Social Unrest Index
- **0.0-0.3**: Stable society, no major issues
- **0.3-0.6**: Moderate discontent, growing protests
- **0.6-1.0**: Crisis conditions, high migration, system instability

### Economic Health
- **Unemployment <5%**: Strong labor market
- **Unemployment 5-8%**: Normal range
- **Unemployment >8%**: Recession conditions
- **Inflation 1-3%**: Target range
- **Inflation >5%**: Problematic price growth

### Citizen Wellbeing
- **Stress <0.4**: Content population
- **Stress 0.4-0.7**: Moderate anxiety
- **Stress >0.7**: Crisis conditions
- **Satisfaction >0.7**: Most citizens happy
- **Satisfaction <0.4**: Widespread unhappiness

## Limitations & Assumptions

1. **Simplified model**: Real economies have much greater complexity
2. **Homogeneous agents**: All citizens follow same decision logic (real behavior is heterogeneous)
3. **No international trade**: Closed economy model
4. **Limited sectoral detail**: Generic "manufacturing, service, tech, agriculture"
5. **Discrete age progression**: Doesn't include births/deaths
6. **Linear policy effects**: Complex policies have non-linear real-world effects

## Future Enhancements

Possible extensions:
- **Multi-region modeling**: Different regions with trade
- **Sectoral shocks**: Industry-specific disruptions
- **Heterogeneous agents**: Agents with different utility functions
- **Political dynamics**: Elections and policy constraints
- **Supply-side economics**: Production capacity constraints
- **Financial markets**: Stock/bond market dynamics
- **Real asset modeling**: Housing, capital investment

## References

### Economic Theory
- Keynesian consumption function and multiplier effect
- Phillips curve (unemployment-inflation relationship)
- Supply and demand dynamics
- Behavioral economics (Kahneman, Tversky)

### Agent-Based Modeling
- Reinforcement learning (Sutton & Barto)
- Q-learning for agent adaptation
- Utility maximization (consumer choice theory)
- Cobb-Douglas production/utility functions

### Real-World Data
- OECD Economic Indicators
- World Bank Development Indicators
- IMF World Economic Outlook
- Federal Reserve Economic Data (FRED)

## License

This project is provided as an educational tool for understanding economic policy impacts through agent-based simulation.

## Support

For questions or issues:
1. Check the examples in Main.py
2. Review docstrings in each module
3. Experiment with Dashboard.py for interactive exploration
4. Analyze sensitivity results to understand which parameters matter most
