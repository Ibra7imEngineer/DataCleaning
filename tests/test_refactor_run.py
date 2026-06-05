import pandas as pd
import app

print('session_state keys before:', list(app.st.session_state.keys())[:10])
# Build sample df
df = pd.DataFrame({
    'cust_name': ['Ali','Ali','Ail','Mona','Mona','Mona'],
    'amount': [100.0, None, 120.0, None, 200.0, 150.0],
    'notes': [None, 'ok', 'ok', '', None, 'fine']
})
print('Original df:\n', df)
# standardize
std = app._standardize_majority_words(df)
print('standardized cells:', std)
# impute
df2, imputed, text_missing = app._fill_missing(df.copy())
print('median imputed coords:', imputed)
print('text missing coords:', text_missing)
app.st.session_state['median_imputed_cells'] = imputed
app.st.session_state['red_coordinates'] = text_missing
# style preview
sty = app.style_preview(
    df2,
    preview_only=True,
    preview_rows=10,
    median_coords=imputed,
    missing_coords=text_missing,
)
print('styler type:', type(sty))
# export excel bytes
b = app.export_excel(df2)
print('excel bytes length:', len(b))
