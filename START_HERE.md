# Multi-Agent Human Society Policy Simulator

**A complete, production-ready simulation framework for modeling government policy impacts on economic outcomes, citizen wellbeing, and social dynamics.**

## 🚀 Quick Start (Choose One)

### Option 1: Interactive Dashboard (Recommended)
```bash
pip install -r requirements.txt
streamlit run Dashboard.py
```
Then open http://localhost:8501 in your browser to adjust policies and see real-time effects.

### Option 2: Command-line Examples
```bash
pip install -r requirements.txt
python Main.py
```
Choose from 7 pre-built example scenarios with detailed output.

### Option 3: Custom Python Script
```python
from SimulationEngine import SimulationEngine
sim = SimulationEngine(population_size=1000)
sim.run_simulation(timesteps=120)
print(f"Unemployment: {sim.economy.state.unemployment_rate*100:.1f}%")
```

## 📋 What's Included

✅ **1,000+ realistic agent simulation** with income, savings, employment, stress, learning  
✅ **Dynamic economy model** tracking inflation, unemployment, GDP, wealth inequality  
✅ **8 adjustable policies** including taxes, welfare, UBI, interest rates  
✅ **Behavioral economics** with stress, satisfaction, confidence affecting decisions  
✅ **Reinforcement learning** agents that adapt behavior based on experiences  
✅ **Interactive dashboard** with real-time charts and policy controls  
✅ **Crisis simulation** to test policy responses to economic shocks  
✅ **Comprehensive analysis tools** for sensitivity analysis and scenario comparison  
✅ **Real-world calibration** based on OECD, World Bank, and Central Bank data  
✅ **Complete documentation** with 7 example scenarios  

## 📁 Project Structure

**Core Modules (8 files):**
- `Citizen.py` - Individual agent behavior and decisions
- `EconomyModel.py` - Macroeconomic dynamics and relationships
- `PolicyEngine.py` - Government policy management and scenarios
- `SimulationEngine.py` - Main simulation loop and orchestration
- `Learning.py` - Q-learning and behavioral adaptation
- `Dashboard.py` - Interactive Streamlit web interface
- `Calibration.py` - Real-world data validation and sensitivity analysis
- `Experimentation.py` - Scenario testing and parameter exploration

**Entry Points (3 ways to use):**
- `Main.py` - Command-line with 7 executable examples
- `Dashboard.py` - Web-based interactive interface
- Your own Python scripts using the modules

**Documentation:**
- `README.md` - Comprehensive feature documentation
- `PROJECT_GUIDE.txt` - Visual overview and navigation
- `QUICKSTART.py` - Code examples and quick reference
- `INDEX.md` - Complete file index and navigation

## 🎯 Try These First

1. **See it working** (2 minutes)
   ```bash
   python QUICKSTART.py
   ```

2. **Run an example** (5 minutes)
   ```bash
   python Main.py
   # Choose option 1
   ```

3. **Use the dashboard** (10 minutes)
   ```bash
   streamlit run Dashboard.py
   ```

4. **Compare policies** (10 minutes)
   ```bash
   python Main.py
   # Choose option 2 or 4
   ```

## 📊 Key Features Explained

### Agents
- 1,000 citizens with realistic demographics and economics
- Track income, savings, debt, employment, and psychological state
- Make monthly decisions about spending, saving, borrowing
- Learn from experiences and adapt behavior

### Economy
- Inflation driven by consumption and supply shocks
- Unemployment from job loss/finding dynamics
- GDP calculated from consumption, investment, government spending
- Wealth inequality (Gini coefficient) and social unrest tracking

### Policies (Adjustable)
- Income tax rate (0-70%)
- Interest rate (0-15%)
- Fuel/energy tax (0-50%)
- Unemployment benefits (0-100%)
- Universal basic income (0-$2000/month)
- Welfare support (0-$500/month)

### Behavioral System
- **Stress** increases with unemployment, debt, high inflation
- **Satisfaction** affected by wealth status and employment
- **Confidence** influences savings and borrowing decisions
- Thresholds trigger protests, migration, health effects

### Learning System
- Agents use Q-learning to improve decisions
- Remember past outcomes of actions
- Adjust behavior when certain actions prove beneficial

## 💡 What Can You Do?

### Analyze Policy Impacts
```python
# Test how UBI affects outcomes
for ubi in [0, 500, 1000, 1500]:
    sim = SimulationEngine(1000)
    sim.policy_engine.set_policy("universal_basic_income", ubi)
    sim.run_simulation(120)
    print(f"UBI ${ubi}: Unrest = {sim.economy.state.social_unrest_index:.2f}")
```

### Simulate Economic Crises
```python
# Model crisis and policy response
sim = SimulationEngine(1000)
sim.run_simulation(24)  # Normal economy

sim.policy_engine.set_policy("interest_rate", 0.0)  # Emergency rate cut
sim.policy_engine.set_policy("unemployment_benefit_rate", 0.8)  # Enhanced benefits
sim.run_simulation(12)  # Crisis phase

sim.policy_engine.set_policy("unemployment_benefit_rate", 0.6)  # Taper benefits
sim.run_simulation(24)  # Recovery phase
```

### Run Experiment Suites
```python
from Experimentation import ExperimentBuilder

suite = ExperimentBuilder.create_scenario_suite()
suite.run_all(population=500, timesteps=60)
print(suite.compare_results())
```

### Export & Analyze Data
```python
from Calibration import DataExporter

sim.run_simulation(120)
DataExporter.export_to_csv(sim, "results.csv")
DataExporter.export_to_json(sim, "results.json")
```

## 📈 Understanding Results

### Social Unrest Index (0-1 scale)
- **0.0-0.3:** Stable society
- **0.3-0.6:** Growing discontent, protests emerging
- **0.6+:** Crisis conditions, high migration

### Unemployment Rate
- **<5%:** Healthy labor market
- **5-8%:** Normal range
- **>8%:** Recession conditions

### Inflation Rate
- **1-3%:** Target range (healthy)
- **>5%:** Problematic price growth

## 📚 Documentation

**Start here:**
1. `PROJECT_GUIDE.txt` - Visual project overview
2. `QUICKSTART.py` - Code examples to try
3. `Main.py` - 7 executable scenarios

**Deep dive:**
1. `README.md` - Complete feature documentation
2. `INDEX.md` - File index and navigation guide
3. Code docstrings - Technical implementation details

## ⚙️ Installation

```bash
# Clone/extract the project
cd "Policy Sand Box"

# Install dependencies
pip install -r requirements.txt

# Verify installation
python -c "import numpy, pandas, streamlit, plotly; print('✓ Ready!')"
```

## 🔧 Customization

### Change Default Parameters
Edit `Config.py`:
```python
SIMULATION_CONFIG = {
    "default_population": 1000,
    "default_timesteps": 120,
}
```

### Modify Agent Behavior
Edit `Citizen.py`:
```python
def _make_consumption_decision(self, disposable_income, policies, macro_state):
    # Customize spending/saving logic here
    ...
```

### Add New Policies
Edit `PolicyEngine.py` and `Config.py`:
```python
# In PolicySet class
new_policy: float = 0.5

# In POLICY_CONSTRAINTS
"new_policy": (0, 1)
```

## 🤝 How It Works

1. **Initialization:** Create 1,000 citizens with random attributes
2. **Monthly Loop:**
   - Update each citizen (employment, income, spending, debt, psychology)
   - Process social events (protests, migration)
   - Update economy (inflation, unemployment, GDP, etc.)
   - Log statistics for analysis
3. **Policy Adjustment:** User can change policies anytime
4. **Analysis:** View results in dashboard or export for analysis

## 📊 Example Scenarios

**Example 1: Basic 10-year simulation**
Run a baseline economy and observe natural dynamics.

**Example 2: Policy comparison**
Test 4 different tax policies side-by-side.

**Example 3: Sensitivity analysis**
See how income tax rate affects unemployment and unrest.

**Example 4: Complete scenario suite**
Run 6 different policy scenarios and compare results.

**Example 5: Individual citizen analysis**
Deep dive into agent demographics and psychology.

**Example 6: Extreme scenarios**
Test 70% tax, massive fuel prices, and libertarian policies.

**Example 7: Crisis & recovery**
Model pre-crisis, crisis response, and recovery phases.

## ⚡ Performance

- 1,000 agents × 120 months: ~10-30 seconds
- 5,000 agents × 120 months: ~60-120 seconds

Tip: Use smaller populations for quick testing, larger populations for detailed analysis.

## 🧠 Learning System

Agents use Q-learning to improve decisions:
- State: (employment, wealth, stress)
- Actions: (save, spend, borrow, change job, protest)
- Reward: Improved satisfaction and stress reduction
- Learning: Update Q-values based on outcomes

Over time, agents learn which behaviors improve their situation.

## 🎓 Real-World Calibration

Parameters based on:
- OECD Economic Indicators
- World Bank Development Data
- Central Bank policy rates
- Historical crisis scenarios (2008, stagflation, pandemic)

## 🔬 Experimentation Tools

- **Sensitivity Analysis:** Tornado diagrams showing parameter impacts
- **Grid Search:** Test all combinations of multiple parameters
- **Scenario Comparison:** Side-by-side analysis of different policies
- **Crisis Validation:** Test against historical economic shocks

## 🚨 Troubleshooting

**Dashboard won't load?**
```bash
streamlit run Dashboard.py
```
Make sure you're in the correct directory.

**Import errors?**
```bash
pip install -r requirements.txt
```

**Simulation too slow?**
Reduce population size or number of timesteps:
```python
sim = SimulationEngine(population_size=300)
sim.run_simulation(timesteps=60)
```

## 📞 Support

Check these files for help:
- `PROJECT_GUIDE.txt` - Common questions
- `README.md` - Comprehensive documentation
- `QUICKSTART.py` - Code examples
- `Main.py` - 7 working examples

## 📜 License

Educational and research use. See specific module docstrings for implementation details and references.

---

**Ready to start?** Run:
```bash
python Main.py
```

Or open the dashboard:
```bash
streamlit run Dashboard.py
```

Happy exploring! 🎉
