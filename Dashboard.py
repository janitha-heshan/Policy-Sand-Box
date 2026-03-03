"""
Interactive dashboard and visualization for the policy simulator
Uses Streamlit for web-based interface
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, List
import json
from datetime import datetime, timedelta

from SimulationEngine import SimulationEngine, SimulationAnalyzer
from Calibration import SimulationCalibrator
from PolicyEngine import PolicyEngine


class Dashboard:
    """
    Streamlit-based interactive dashboard for policy simulation
    """
    
    def __init__(self):
        st.set_page_config(page_title="Policy Simulator", layout="wide")
        self.simulation = None
        self.history = []
    
    def run(self):
        """Run the dashboard"""
        st.title("🏛️ Multi-Agent Human Society Policy Simulator")
        st.markdown("""
        Simulate the effects of different government policies on a society of 1000+ citizens.
        Adjust policies and observe real-time impacts on economic indicators, citizen wellbeing, and social stability.
        """)

        # watermark/footer
        st.markdown(
            "<style>body::after{content:'Developed by Janitha Heshan as a POC';"
            "position:fixed;bottom:8px;right:8px;opacity:0.25;font-size:12px;}",
            unsafe_allow_html=True)
        
        # Sidebar for controls
        with st.sidebar:
            st.header("⚙️ Simulation Controls")
            
            # Simulation settings
            st.subheader("Simulation Setup")
            population = st.slider(
                "Population Size", 100, 5000, 1000, step=100,
                help="Number of citizens in the model. Larger populations give smoother aggregate results but increase computation time."
            )
            timesteps = st.slider(
                "Simulation Length (months)", 12, 240, 120, step=12,
                help="Total number of months to advance the simulation. Longer runs reveal long-term trends."
            )
            
            # Preset scenarios
            st.subheader("Policy Scenarios")
            scenario = st.selectbox("Choose Scenario", [
                "Custom",
                "Default (Current)",
                "Extreme Tax (70%)",
                "Libertarian (Low Tax)",
                "Universal Basic Income",
                "Green Energy Transition",
                "Financial Crisis Response"
            ], help="Select a pre‑configured policy bundle. Choose 'Custom' to manually adjust the sliders below.")
            
            # Policy controls
            st.subheader("Policy Adjustments")
            col1, col2 = st.columns(2)
            
            with col1:
                income_tax = st.slider(
                    "Income Tax (%)", 0, 70, 20,
                    help="Personal income tax rate. Higher values reduce disposable income and consumption."
                )
                interest_rate = st.slider("Interest Rate (%)", 0, 15, 5,
                                                                                     help="Policy interest rate applied to loans and savings. Affects spending and investment decisions.")
                fuel_price = st.slider("Fuel Price Multiplier", 0.5, 3.0, 1.0,
                                         step=0.1,
                                                                                 help="Multiplier on default fuel cost. Influences transportation expenses and inflation pressure.")
            
            with col2:
                unemployment_benefit = st.slider(
                    "Unemployment Benefits (%)", 0, 100, 40,
                    help="Portion of lost wages paid to unemployed citizens.")
                ubi = st.slider("Universal Basic Income ($)", 0, 2000, 0, step=100,
                                 help="Fixed cash transfer to every citizen regardless of employment.")
                welfare = st.slider("Welfare Support ($)", 0, 500, 0, step=50,
                                     help="Additional means‑tested support for low‑income households.")
            
            # Run controls
            st.subheader("Execution")
            col1, col2 = st.columns(2)
            run_simulation = col1.button("▶️ Run Simulation", use_container_width=True)
            reset_button = col2.button("🔄 Reset", use_container_width=True)
        
        # Main content area
        if run_simulation:
            self._run_scenario(scenario, population, timesteps, 
                             income_tax, interest_rate, fuel_price,
                             unemployment_benefit, ubi, welfare)
        
        elif reset_button:
            st.session_state.clear()
            st.rerun()
        
        # Display previous results if available
        elif 'simulation' in st.session_state:
            self._display_results(st.session_state['simulation'])
        
        else:
            st.info("👈 Configure simulation settings and click 'Run Simulation' to begin")
    
    def _run_scenario(self, scenario: str, population: int, timesteps: int,
                     income_tax: float, interest_rate: float, fuel_price: float,
                     unemployment_benefit: float, ubi: float, welfare: float):
        """Run simulation with selected scenario"""
        
        # Create simulation
        sim = SimulationEngine(population_size=population)
        
        # Apply scenario
        if scenario == "Extreme Tax (70%)":
            sim.policy_engine.scenario_extreme_tax()
        elif scenario == "Libertarian (Low Tax)":
            sim.policy_engine.scenario_libertarian()
        elif scenario == "Universal Basic Income":
            sim.policy_engine.scenario_ubi()
        elif scenario == "Green Energy Transition":
            sim.policy_engine.scenario_green_energy()
        elif scenario == "Financial Crisis Response":
            sim.policy_engine.scenario_financial_crisis()
        else:
            # Custom settings
            sim.policy_engine.set_policy("income_tax_rate", income_tax / 100)
            sim.policy_engine.set_policy("interest_rate", interest_rate / 100)
            sim.policy_engine.set_policy("fuel_price_multiplier", fuel_price)
            sim.policy_engine.set_policy("unemployment_benefit_rate", unemployment_benefit / 100)
            sim.policy_engine.set_policy("universal_basic_income", ubi)
            sim.policy_engine.set_policy("welfare_support", welfare)
        
        # Progress bar
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        def update_progress(timestep, total, state):
            progress = timestep / total
            progress_bar.progress(progress)
            status_text.text(f"Progress: Month {timestep + 1}/{total}")
        
        # Run simulation
        with st.spinner("🔄 Running simulation..."):
            results = sim.run_simulation(timesteps=timesteps, callback=update_progress)
        
        st.session_state['simulation'] = sim
        st.session_state['results'] = results
        
        # Display results
        self._display_results(sim)
    
    def _display_results(self, simulation: SimulationEngine):
        """Display simulation results"""
        
        stats_log = simulation.statistics_log
        economy_state = simulation.economy.state
        
        if not stats_log:
            st.warning("No simulation results to display")
            return
        
        # Convert to DataFrame
        df = pd.DataFrame(stats_log)
        
        # Key metrics section
        st.header("📊 Key Outcomes")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Final Population", len(simulation.citizens),
                     delta=len(simulation.citizens) - simulation.population_size)
        
        with col2:
            final_unemployment = df['unemployment_rate'].iloc[-1] * 100
            st.metric("Final Unemployment", f"{final_unemployment:.1f}%",
                     delta=f"{(final_unemployment - df['unemployment_rate'].iloc[0] * 100):.1f}%")
        
        with col3:
            final_inflation = df['inflation_rate'].iloc[-1] * 100
            st.metric("Final Inflation", f"{final_inflation:.1f}%")
        
        with col4:
            final_unrest = df['social_unrest_index'].iloc[-1]
            st.metric("Social Unrest", f"{final_unrest:.2f}", delta=f"{(final_unrest - df['social_unrest_index'].iloc[0]):.2f}")

        # calibration accuracy score
        try:
            calibrator = SimulationCalibrator()
            final_stats = df.iloc[-1].to_dict()
            error = calibrator.calculate_calibration_error(final_stats)
            accuracy_score = 100 / (1 + error)  # 100 = perfect
            st.metric("Calibration Accuracy", f"{accuracy_score:.1f}",
                      help="Score based on deviation from baseline real-world targets (higher is better).")
        except Exception:
            # if something goes wrong, skip gracefully
            pass
        
        # Charts
        st.header("📈 Economic Trends")
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig_inflation = go.Figure()
            fig_inflation.add_trace(go.Scatter(y=df['inflation_rate']*100, mode='lines',
                                              name='Inflation Rate',
                                              line=dict(color='red', width=2)))
            fig_inflation.update_layout(title="Inflation Rate Over Time",
                                       xaxis_title="Month", yaxis_title="Inflation (%)",
                                       hovermode='x unified', height=400)
            st.plotly_chart(fig_inflation, use_container_width=True)
        
        with col2:
            fig_unemployment = go.Figure()
            fig_unemployment.add_trace(go.Scatter(y=df['unemployment_rate']*100, mode='lines',
                                                 name='Unemployment',
                                                 line=dict(color='orange', width=2)))
            fig_unemployment.update_layout(title="Unemployment Rate Over Time",
                                          xaxis_title="Month", yaxis_title="Unemployment (%)",
                                          hovermode='x unified', height=400)
            st.plotly_chart(fig_unemployment, use_container_width=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig_gdp = go.Figure()
            fig_gdp.add_trace(go.Scatter(y=df['gdp'], mode='lines',
                                        name='GDP',
                                        line=dict(color='green', width=2)))
            fig_gdp.update_layout(title="GDP Over Time",
                                 xaxis_title="Month", yaxis_title="GDP",
                                 hovermode='x unified', height=400)
            st.plotly_chart(fig_gdp, use_container_width=True)
        
        with col2:
            fig_unrest = go.Figure()
            fig_unrest.add_trace(go.Scatter(y=df['social_unrest_index'], mode='lines',
                                           name='Social Unrest',
                                           line=dict(color='purple', width=2)))
            fig_unrest.add_hline(y=0.6, line_dash="dash", line_color="red",
                                annotation_text="High Unrest Threshold")
            fig_unrest.update_layout(title="Social Unrest Index",
                                    xaxis_title="Month", yaxis_title="Unrest Level",
                                    hovermode='x unified', height=400)
            st.plotly_chart(fig_unrest, use_container_width=True)
        
        # Citizen wellbeing
        st.header("👥 Citizen Wellbeing")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            fig_stress = go.Figure()
            fig_stress.add_trace(go.Scatter(y=df['avg_stress'], mode='lines',
                                           name='Average Stress',
                                           line=dict(color='red', width=2)))
            fig_stress.update_layout(title="Average Stress Level",
                                    xaxis_title="Month", yaxis_title="Stress",
                                    hovermode='x unified', height=350)
            st.plotly_chart(fig_stress, use_container_width=True)
        
        with col2:
            fig_satisfaction = go.Figure()
            fig_satisfaction.add_trace(go.Scatter(y=df['avg_satisfaction'], mode='lines',
                                                 name='Satisfaction',
                                                 line=dict(color='blue', width=2)))
            fig_satisfaction.update_layout(title="Average Satisfaction",
                                          xaxis_title="Month", yaxis_title="Satisfaction",
                                          hovermode='x unified', height=350)
            st.plotly_chart(fig_satisfaction, use_container_width=True)
        
        with col3:
            fig_confidence = go.Figure()
            fig_confidence.add_trace(go.Scatter(y=df['avg_confidence'], mode='lines',
                                               name='Confidence',
                                               line=dict(color='green', width=2)))
            fig_confidence.update_layout(title="Average Economic Confidence",
                                        xaxis_title="Month", yaxis_title="Confidence",
                                        hovermode='x unified', height=350)
            st.plotly_chart(fig_confidence, use_container_width=True)
        
        # Wealth distribution
        st.header("💰 Wealth Metrics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig_wealth = go.Figure()
            fig_wealth.add_trace(go.Scatter(y=df['avg_income'], name='Avg Income',
                                           line=dict(color='green')))
            fig_wealth.add_trace(go.Scatter(y=df['avg_savings'], name='Avg Savings',
                                           line=dict(color='blue')))
            fig_wealth.update_layout(title="Income & Savings Trends",
                                    xaxis_title="Month", hovermode='x unified', height=400)
            st.plotly_chart(fig_wealth, use_container_width=True)
        
        with col2:
            fig_inequality = go.Figure()
            fig_inequality.add_trace(go.Scatter(y=df['wealth_inequality_gini'], mode='lines',
                                               name='Gini Coefficient',
                                               line=dict(color='red', width=2)))
            fig_inequality.update_layout(title="Wealth Inequality (Gini Index)",
                                        xaxis_title="Month", yaxis_title="Gini",
                                        hovermode='x unified', height=400)
            st.plotly_chart(fig_inequality, use_container_width=True)
        
        # Events section
        st.header("⚡ Major Events")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Protests")
            if simulation.protest_events:
                for event in simulation.protest_events[-10:]:  # Last 10 events
                    st.write(f"Month {event['timestep']}: {event['size']} citizens ({event['percentage']*100:.1f}%)")
            else:
                st.info("No major protests occurred")
        
        with col2:
            st.subheader("Migration Events")
            if simulation.migration_events:
                total_migrated = len(simulation.migration_events)
                st.write(f"Total citizens migrated: {total_migrated}")
                st.write(f"Final population: {len(simulation.citizens)}")
            else:
                st.info("No citizens migrated")
        
        # Analysis
        st.header("📋 Analysis")
        
        analyzer = SimulationAnalyzer()
        metrics = analyzer.calculate_aggregate_metrics(stats_log)
        
        metric_df = pd.DataFrame({
            'Metric': list(metrics.keys()),
            'Value': list(metrics.values())
        })
        
        st.dataframe(metric_df, use_container_width=True)
        
        # Export data
        st.subheader("💾 Export Results")
        
        col1, col2 = st.columns(2)
        
        with col1:
            csv = df.to_csv(index=False)
            st.download_button("📥 Download Statistics CSV", csv, "simulation_stats.csv")
        
        with col2:
            # Prepare JSON export. The config/metrics/events dictionaries may
            # contain numpy types (int64, float64) or dataclasses which aren't
            # serializable by default. Use a converter that casts numpy
            # scalars/arrays to native Python types and falls back to str().
            def _json_converter(obj):
                try:
                    import numpy as _np
                    if isinstance(obj, _np.generic):
                        return obj.item()
                    if isinstance(obj, _np.ndarray):
                        return obj.tolist()
                except ImportError:
                    pass
                try:
                    from dataclasses import is_dataclass, asdict
                    if is_dataclass(obj):
                        return asdict(obj)
                except Exception:
                    pass
                return str(obj)

            json_data = json.dumps({
                'config': simulation.simulation_config,
                'final_metrics': metrics,
                'events': {
                    'protests': simulation.protest_events,
                    'migrations': simulation.migration_events
                }
            }, indent=2, default=_json_converter)
            st.download_button("📥 Download Results JSON", json_data, "simulation_results.json")


def run_dashboard():
    """Entry point for dashboard"""
    dashboard = Dashboard()
    dashboard.run()


if __name__ == "__main__":
    run_dashboard()
