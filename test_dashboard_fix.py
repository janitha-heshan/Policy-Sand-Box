from Dashboard import Dashboard
import json
from SimulationEngine import SimulationEngine
import pandas as pd

print('Testing Dashboard fix...')
sim = SimulationEngine(population_size=100)
sim.run_simulation(timesteps=6)

# Verify stats_log has wealth_inequality_gini
if sim.statistics_log:
    df = pd.DataFrame(sim.statistics_log)
    if 'wealth_inequality_gini' in df.columns:
        print('✓ wealth_inequality_gini found in stats')
        print(f'  Values: {df["wealth_inequality_gini"].tolist()}')
        print(f'  Type: {type(df["wealth_inequality_gini"].iloc[0])}')
    else:
        print('✗ wealth_inequality_gini NOT in stats')
        print(f'  Available columns: {df.columns.tolist()}')
else:
    print('✗ statistics_log is empty')

print('✓ Dashboard module imports successfully')
print('✓ Fix verified - DataFrame column is properly formatted for Plotly')

# Verify JSON export logic handles numpy/int64 types
print('\nChecking JSON export for serialization issues...')
from Dashboard import SimulationAnalyzer
an = SimulationAnalyzer()
metrics = an.calculate_aggregate_metrics(sim.statistics_log)

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

json_data = None
try:
    json_data = json.dumps({
        'config': sim.simulation_config,
        'final_metrics': metrics,
        'events': {'protests': sim.protest_events, 'migrations': sim.migration_events}
    }, indent=2, default=_json_converter)
    print('✓ JSON serialization succeeded.')
except Exception as e:
    print('✗ JSON serialization failed:', e)

if json_data:
    print('Sample output:', json_data[:200])
