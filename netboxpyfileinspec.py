import pandas as pd

# Loads the Excel file
excel_file = "environmentfile.xlsx"
df = pd.read_excel(excel_file)

print(df.head())
