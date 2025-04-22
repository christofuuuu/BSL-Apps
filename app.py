# -*- coding: utf-8 -*-
"""
Created on Tue Apr 22 21:23:39 2025

@author: santo
"""

from flask import Flask, request, render_template_string
import pandas as pd
import pyodbc

# --- Configuration ---
# Path to your Access .mdb file
MDB_PATH = r"C:\Users\santo\Downloads\LeagueOutput.mdb"

# Connection string for Access .mdb files
CONN_STR = (
    r"DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};"
    f"DBQ={MDB_PATH};"
)

# Initialize Flask app
app = Flask(__name__)

# Load data once at startup
def load_players():
    # Connect and read players table
    conn = pyodbc.connect(CONN_STR)
    df = pd.read_sql("SELECT ID, Name FROM Player", conn)
    conn.close()
    return df

players_df = load_players()

# HTML template
TEMPLATE = '''
<!doctype html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Player Lookup</title>
  <style>
    body { font-family: sans-serif; margin: 2rem; }
    input, button { font-size: 1rem; padding: 0.5rem; }
    .result { margin-top: 1rem; font-weight: bold; }
  </style>
</head>
<body>
  <h1>Player Lookup</h1>
  <form method="post">
    <input name="query" placeholder="Enter Player ID or Name" size="30" required>
    <button type="submit">Search</button>
  </form>
  {% if result %}
    <div class="result">{{ result }}</div>
  {% endif %}
</body>
</html>
'''

# Route
@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    if request.method == 'POST':
        q = request.form['query'].strip()
        # If numeric, treat as ID lookup
        if q.isdigit():
            pid = int(q)
            row = players_df[players_df['ID'] == pid]
            result = row['Name'].iloc[0] if not row.empty else 'Player ID not found.'
        else:
            # Otherwise, treat as name lookup (case-insensitive)
            matches = players_df[players_df['Name'].str.contains(q, case=False, na=False)]
            if not matches.empty:
                ids = matches['ID'].tolist()
                names = matches['Name'].tolist()
                pairs = [f"{n} (ID: {i})" for n, i in zip(names, ids)]
                result = '<br>'.join(pairs)
            else:
                result = 'Player name not found.'
    return render_template_string(TEMPLATE, result=result)

if __name__ == '__main__':
    # Use host='0.0.0.0' to make it accessible externally if needed
    app.run(debug=True)
