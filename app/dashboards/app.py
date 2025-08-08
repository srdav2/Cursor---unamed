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

    # Dummy data for scaffold
    df = pd.DataFrame({
        "category": ["Revenue", "Expenses", "Profit"],
        "amount": [100, 70, 30],
    })

    fig = px.bar(df, x="category", y="amount", title="Example Financial Summary")

    app.layout = html.Div([
        html.H2("Financial Analysis Dashboard (Scaffold)"),
        dcc.Graph(figure=fig),
    ])

    return app


def main() -> None:
    app = create_app()
    app.run_server(debug=True)


if __name__ == "__main__":
    main()
