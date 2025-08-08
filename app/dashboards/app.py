"""
Dash App (minimal scaffold)

This provides a simple Dash layout that will later be connected to real data
from SQLite/CSV. For now, it renders an example chart using a dummy pandas
DataFrame.

Run directly with:  python -m app.dashboards.app
"""
from __future__ import annotations

import pandas as pd
from dash import Dash, dcc, html
import plotly.express as px


def create_app() -> Dash:
    app = Dash(__name__)

        # Load data from SQLite
    from app.storage.db import connect, fetch_metrics_dataframe
    conn = connect()
    df = fetch_metrics_dataframe(conn)
    if df.empty:
        df = pd.DataFrame({"category": [], "amount": []})

    fig = px.bar(df, x="category", y="amount", title="Financial Metrics (SQLite)")

    app.layout = html.Div([
        html.H2("Financial Analysis Dashboard"),
        dcc.Graph(figure=fig),
    ])

    return app


def main() -> None:
    app = create_app()
    app.run_server(debug=True)


if __name__ == "__main__":
    main()
