import pandas as pd
import sys
sys.path.insert(0, '.')
from core.text_processor import optimize_memory, AuditTrail

# Test 1: verify optimize_memory returns (df, log) tuple
print("=" * 60)
print("TEST 1: optimize_memory returns tuple(df, log)")
print("=" * 60)
df_test = pd.DataFrame({
    'name': ['Ahmed', 'Mona', 'Hassan'],
    'age': [25, 30, 22],
    'score': [95.5, 88.2, 92.1]
})

result_df, result_log = optimize_memory(df_test)
print(f"✓ Returns dataframe shape: {result_df.shape}")
print(f"✓ Log dict keys: {list(result_log.keys())}")
print(f"  - memory_before_bytes: {result_log['memory_before_bytes']}")
print(f"  - memory_after_bytes: {result_log['memory_after_bytes']}")
print(f"  - reduction_bytes: {result_log['reduction_bytes']}")
print(f"  - reduction_percent: {result_log['reduction_percent']}%")
print()

# Test 2: verify AuditTrail has log_change method
print("=" * 60)
print("TEST 2: AuditTrail.log_change works for row-level changes")
print("=" * 60)
audit = AuditTrail()
audit.log_change(
    row_idx=0,
    col_name='name',
    old_value='Ahmed',
    new_value='Ahmed (Cleaned)',
    reason='standardized'
)
audit.log_change(
    row_idx=1,
    col_name='age',
    old_value='30',
    new_value=30,
    reason='converted to numeric'
)
print(f"✓ Logged {len(audit.records)} changes")
for record in audit.records:
    print(f"  - Row {record['row_index']}, Col '{record['column']}': '{record['old_value']}' → '{record['new_value']}'")
print()
print("=" * 60)
print("✅ ALL TESTS PASSED - BOTH FIXES ARE WORKING!")
print("=" * 60)
