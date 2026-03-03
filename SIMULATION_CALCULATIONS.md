# How Calculations and Simulations Work

This document walks through the inner workings of the Multi‑Agent Human Society Policy Simulator. It explains the major algorithmic steps and economic calculations performed at each iteration.

## 1. Initialization

1. **Configuration** – default parameters are defined in `Config.py` (population size, policy ranges, economic constants, etc.).
2. **Components** – the `SimulationEngine` creates instances of:
   * `EconomyModel` – holds aggregate state and macroeconomic update rules
   * `PolicyEngine` – stores current policy parameters and applies bounds
   * A list of `Citizen` agents
3. **Population** – citizens are generated with realistic age and sector distributions. Each `Citizen` is initialized with income, savings, debt, employment status, and psychological attributes (stress, satisfaction, confidence).

## 2. Monthly Timestep Loop

The core simulation executes in `SimulationEngine.run_simulation` for a given number of months. Each timestep comprises:

1. **Agent Updates** (`Citizen.update_monthly`):
   * Employment decisions (seek job, remain unemployed) based on `job_finding_rate` and `unemployment_rate`.
   * Income collection if employed, unemployment benefits otherwise.
   * Spending decision using a simple rule that balances consumption and savings; influenced by `spending_preference`, current stress/satisfaction, and interest rate.
   * Debt repayment or borrowing depending on savings and expenses.
   * Psychological state updates (stress increases with unemployment and inflation, satisfaction with rising income, confidence with past success).
   * Learning: each citizen has a small Q‑learning agent tracked in `CitizenMemory`; rewards are derived from utility functions and guide future decisions.

2. **Protest Processing** – if a sufficient fraction of citizens are discontent, a protest event may occur. Protests temporarily lower GDP and increase unrest.

3. **Migration Processing** – citizens with persistently low satisfaction may emigrate, reducing population and altering aggregate statistics.

4. **Economy Update** (`EconomyModel.step`):
   * Aggregates consumption, savings, investment from all citizens.
   * Calculates inflation using a consumption‑driven model with inertia and cost‑push components.
   * Updates unemployment rate via a simplified Phillips curve relating it to inflation and job finding rate.
   * Computes GDP as `consumption + investment + government_spending`.
   * Evaluates wealth inequality using a Gini coefficient based on individual wealth levels.
   * Derives a social unrest index from unemployment, inequality, protest probability, and inflation.
   * Records the new state in `EconomicState`.

5. **Logging** – the simulation collects a snapshot of the economy and some citizen aggregates into `statistics_log`; protest and migration events are appended to their respective lists.

## 3. Policy Interaction

The `PolicyEngine` allows eight adjustable knobs (income tax, fuel tax multiplier, interest rate, unemployment benefits, UBI, welfare support, etc.).
Changing a policy immediately affects agent budgets in the next timestep: tax rates reduce disposable income; interest rates alter borrowing/saving; UBI and welfare add to income; fuel price changes affect cost of living.

## 4. Calibration & Accuracy

A `SimulationCalibrator` provides a mechanism to compare simulation outputs to real‑world targets (inflation 2 %, unemployment 5 %, Gini 0.35, etc.). The calibration error is a weighted relative error across these metrics. The dashboard computes an "Accuracy Score" defined as `100/(1+error)`; a perfect match yields 100.

The calibrator can also run automated tuning by adjusting economic parameters (inflation inertia, wage flexibility, etc.) to minimize error.

## 5. Data Export and Analysis

At the end of a run, `SimulationAnalyzer` computes aggregate statistics such as means, standard deviations, migration counts, protest counts, and budget balance. Results can be exported as CSV or JSON (the dashboard includes a custom JSON serializer to handle numpy types).

## 6. Visualization

The Streamlit dashboard (`Dashboard.py`) renders 12+ interactive charts: inflation, unemployment, GDP, social unrest, citizen wellbeing metrics, wealth distribution, inequality, etc. Controls allow changing policies on the fly, and a watermark indicates the prototype author.

---

This step‑by‑step description should help developers and users understand the mechanics behind the simulation and serve as a reference when modifying or extending the model.
