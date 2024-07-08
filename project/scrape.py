import pandas as pd

# URL of the page to scrape
url = "https://fbref.com/en/squads/18bb7c10/2022-2023/Arsenal-Stats"

# Reading the table with the specified attributes
df_list = pd.read_html(url, attrs={"id": "stats_standard_9"}, flavor='lxml')
players = []
# Check if the table is found
if df_list:
    df = df_list[0]

    # Drop rows where 'Rk' column has NaN values (if needed)
    # df = df.dropna(subset=['Rk'])

    # Rename columns to combine multi-index columns into single level (if applicable)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = ['_'.join(col).strip() for col in df.columns.values]
    else:
        df.columns = df.columns.get_level_values(0)  # If it's a single level, just get the column names

    # Print the column names to inspect them
    print("Column names in the DataFrame:")
    print(df.columns)

    # Set pandas display options to show more columns
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)

    # Specify the columns to display
    columns_to_display = [
        'Unnamed: 0_level_0_Player',
        'Unnamed: 1_level_0_Nation',
        'Unnamed: 2_level_0_Pos',
        'Unnamed: 3_level_0_Age',
        'Unnamed: 4_level_0_MP',
        'Playing Time_90s',
        'Performance_Gls', 
        'Performance_Ast',
        'Performance_CrdY', 
        'Performance_CrdR',
    ]

    # Select those columns from the DataFrame
    selected_df = df[columns_to_display]

    # Modify the 'Nation' column to keep only the value after the space
    selected_df['Unnamed: 1_level_0_Nation'] = selected_df['Unnamed: 1_level_0_Nation'].str.split().str[-1]

    # Modify the 'Nation' column to keep only the value after the space
    selected_df['Unnamed: 2_level_0_Pos'] = selected_df['Unnamed: 2_level_0_Pos'].str.split(',').str[-1].str.strip()

    # Loop through all the rows and print each one where '90s' is 5 or higher
    counter = 0
    for index, row in selected_df[:-2].iterrows():
        if row['Playing Time_90s'] < 5 or pd.isna(row['Playing Time_90s']):
            continue
        combinedEntry = {
            'teamId': 2,
            'playerId': counter,
            'name': row['Unnamed: 0_level_0_Player'],
            'nation': row['Unnamed: 1_level_0_Nation'],
            'mainPos': row['Unnamed: 2_level_0_Pos'],
            'age': row['Unnamed: 3_level_0_Age'],
            'apps': row['Unnamed: 4_level_0_MP'],
            'fullGames': row['Playing Time_90s'],
            'goals': row['Performance_Gls'], 
            'assists': row['Performance_Ast'],
            'yellow': row['Performance_CrdY'], 
            'red': row['Performance_CrdR']
        }
        print(combinedEntry)
        print('\n')
        counter += 1
else:
    print("Table not found.")
