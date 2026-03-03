"""
Configuration and constants for the Policy Simulator
"""

# Simulation Parameters
SIMULATION_CONFIG = {
    "default_population": 1000,
    "min_population": 100,
    "max_population": 5000,
    "default_timesteps": 120,  # 10 years
    "time_unit": "month",
    "random_seed": 42,
}

# Agent Parameters
AGENT_CONFIG = {
    "age_range": (18, 75),
    "initial_income_range": (500, 5000),
    "initial_savings_multiplier": (0.5, 2.0),  # Relative to income
    "initial_debt_range": (0, 3),  # Relative to income
    "stress_level_range": (0.2, 0.8),
    "risk_tolerance_range": (0.2, 0.9),
    "learning_rate_range": (0.05, 0.15),
}

# Policy Constraints
POLICY_CONSTRAINTS = {
    "income_tax_rate": (0.0, 0.7),
    "fuel_tax_rate": (0.0, 0.5),
    "fuel_price_multiplier": (0.5, 3.0),
    "interest_rate": (0.0, 0.15),
    "unemployment_benefit_rate": (0.0, 1.0),
    "pension_replacement_rate": (0.0, 1.0),
    "universal_basic_income": (0.0, 2000),
    "welfare_support": (0.0, 500),
}

# Economic Parameters
ECONOMY_CONFIG = {
    "consumption_to_inflation_multiplier": 0.15,
    "unemployment_to_wage_multiplier": -0.5,
    "inflation_inertia": 0.6,
    "inflation_target": 0.02,
    "unemployment_natural_rate": 0.05,
    "gdp_multiplier": 0.8,
    "initial_gdp": 1000000,
    "initial_inflation": 0.02,
    "initial_unemployment": 0.05,
}

# Behavioral Thresholds
BEHAVIORAL_CONFIG = {
    "high_stress_threshold": 0.7,
    "low_stress_threshold": 0.4,
    "high_unrest_threshold": 0.6,
    "critical_unrest_threshold": 0.8,
    "low_satisfaction_threshold": 0.4,
    "protest_stress_minimum": 0.5,
    "migration_satisfaction_maximum": 0.4,
}

# Sector Configuration
SECTORS = {
    "tech": {"multiplier": 1.4, "volatility": "medium"},
    "manufacturing": {"multiplier": 0.9, "volatility": "high"},
    "service": {"multiplier": 0.7, "volatility": "low"},
    "agriculture": {"multiplier": 0.6, "volatility": "high"},
}

# Learning Parameters
LEARNING_CONFIG = {
    "learning_rate": 0.1,
    "discount_factor": 0.95,
    "exploration_rate": 0.1,
    "q_learning_enabled": True,
    "utility_function": "cobb_douglas",
}

# Visualization Configuration
DASHBOARD_CONFIG = {
    "refresh_rate": 1,  # seconds
    "history_window": 240,  # months (20 years)
    "chart_height": 400,
    "chart_width": None,  # Full width
    "show_gridlines": True,
    "color_scheme": "plotly",
}

# Output Configuration
OUTPUT_CONFIG = {
    "export_format": ["csv", "json"],
    "save_citizen_data": True,
    "save_statistics": True,
    "save_events": True,
    "log_level": "INFO",
}

# Calibration Targets (OECD averages)
CALIBRATION_TARGETS = {
    "inflation_rate": 0.02,
    "unemployment_rate": 0.05,
    "gdp_growth_rate": 0.025,
    "gini_coefficient": 0.35,
    "wage_growth_rate": 0.025,
    "protest_frequency": 2.5,  # per year
    "migration_rate": 0.005,  # per year
}

# Scenario Definitions
PREDEFINED_SCENARIOS = {
    "default": {
        "description": "Default economy",
        "policies": {}
    },
    "conservative": {
        "description": "Low taxes, minimal welfare",
        "policies": {
            "income_tax_rate": 0.15,
            "universal_basic_income": 0,
            "welfare_support": 0,
        }
    },
    "social_market": {
        "description": "Balanced tax and welfare",
        "policies": {
            "income_tax_rate": 0.30,
            "universal_basic_income": 300,
            "welfare_support": 100,
        }
    },
    "ubi": {
        "description": "Universal Basic Income",
        "policies": {
            "income_tax_rate": 0.35,
            "universal_basic_income": 1500,
            "welfare_support": 0,
        }
    },
    "green_energy": {
        "description": "Green energy transition",
        "policies": {
            "fuel_tax_rate": 0.40,
            "fuel_price_multiplier": 2.0,
            "income_tax_rate": 0.25,
        }
    },
    "crisis": {
        "description": "Financial crisis response",
        "policies": {
            "interest_rate": 0.00,
            "unemployment_benefit_rate": 0.80,
            "welfare_support": 300,
        }
    }
}

# Messages and Labels
LABELS = {
    "unemployment": "Unemployment Rate",
    "inflation": "Inflation Rate",
    "gdp": "Gross Domestic Product",
    "unrest": "Social Unrest Index",
    "gini": "Wealth Inequality (Gini)",
    "stress": "Average Stress Level",
    "satisfaction": "Average Satisfaction",
    "confidence": "Economic Confidence",
}

def get_policy_info(policy_name: str) -> dict:
    """Get information about a policy"""
    descriptions = {
        "income_tax_rate": "Percentage of income collected as taxes",
        "fuel_tax_rate": "Tax on fuel/energy consumption",
        "fuel_price_multiplier": "Multiplier on base fuel prices",
        "interest_rate": "Central bank interest rate",
        "unemployment_benefit_rate": "% of income for unemployed citizens",
        "pension_replacement_rate": "% of income replacement for retirees",
        "universal_basic_income": "Monthly stipend for all citizens",
        "welfare_support": "Monthly welfare payments",
    }
    
    constraints = POLICY_CONSTRAINTS.get(policy_name, (0, 1))
    
    return {
        "name": policy_name,
        "description": descriptions.get(policy_name, ""),
        "min": constraints[0],
        "max": constraints[1],
    }
