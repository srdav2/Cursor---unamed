"""
Dash App (QC-enabled)

Renders a DataTable of extracted items with a Validated checkbox and a screenshot
preview. Expects a SQLite database at data/qc.db with table extracted_items.

Run: python -m app.dashboards.app
"""
from __future__ import annotations

import os
import sqlite3
from typing import List, Dict, Any

import pandas as pd
from dash import Dash, dcc, html, Input, Output, State, dash_table, ctx
import dash

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DB_PATH = os.path.join(PROJECT_ROOT, "data", "qc.db")
SCREENSHOT_ROOT = os.path.join(PROJECT_ROOT, "data", "screenshots")


def ensure_db() -> None:
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS extracted_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                document_path TEXT NOT NULL,
                page_index INTEGER NOT NULL,
                value TEXT,
                row_index INTEGER,
                col_index INTEGER,
                bbox_x0 REAL,
                bbox_top REAL,
                bbox_x1 REAL,
                bbox_bottom REAL,
                screenshot_path TEXT,
                section_hint TEXT,
                validated INTEGER DEFAULT 0,
                validated_by TEXT,
                validated_at TEXT
            )
            """
        )


essential_columns = [
    "id",
    "document_path",
    "page_index",
    "value",
    "row_index",
    "col_index",
    "bbox_x0",
    "bbox_top",
    "bbox_x1",
    "bbox_bottom",
    "screenshot_path",
    "section_hint",
    "validated",
    "validated_by",
    "validated_at",
]


def load_items_df() -> pd.DataFrame:
    with sqlite3.connect(DB_PATH) as conn:
        df = pd.read_sql_query("SELECT * FROM extracted_items ORDER BY validated ASC, id ASC", conn)
    return df


def create_app() -> Dash:
    ensure_db()

    app = Dash(__name__)

    # Serve screenshots from data/screenshots via Flask route
    server = app.server

    @server.route("/screenshots/<path:path>")
    def serve_screenshot(path):
        from flask import send_from_directory
        return send_from_directory(SCREENSHOT_ROOT, path)

    df = load_items_df()

    app.layout = html.Div([
        html.H2("Quality Check - Extracted Financial Data"),
        html.Div([
            html.Button("Refresh", id="refresh-btn", n_clicks=0),
            dcc.Dropdown(
                id="filter-validated",
                options=[
                    {"label": "All", "value": "all"},
                    {"label": "Unvalidated", "value": "unvalidated"},
                    {"label": "Validated", "value": "validated"},
                ],
                value="all",
                clearable=False,
                style={"width": "200px", "marginLeft": "12px"},
            ),
        ], style={"display": "flex", "alignItems": "center", "gap": "8px"}),
        dash_table.DataTable(
            id="items-table",
            columns=[
                {"name": "ID", "id": "id"},
                {"name": "Value", "id": "value"},
                {"name": "Doc", "id": "document_path"},
                {"name": "Page", "id": "page_index"},
                {"name": "Row", "id": "row_index"},
                {"name": "Col", "id": "col_index"},
                {"name": "Screenshot", "id": "screenshot_path", "presentation": "markdown"},
                {"name": "Validated", "id": "validated", "presentation": "dropdown"},
                {"name": "By", "id": "validated_by"},
                {"name": "At", "id": "validated_at"},
            ],
            data=df.to_dict("records"),
            page_size=15,
            style_table={"overflowX": "auto"},
            style_cell={"maxWidth": 240, "textOverflow": "ellipsis", "overflow": "hidden"},
            dropdown={
                "validated": {
                    "options": [
                        {"label": "No", "value": 0},
                        {"label": "Yes", "value": 1},
                    ]
                }
            },
            editable=True,
            row_selectable="single",
        ),
        dcc.Store(id="store-filtered"),
    ])

    @app.callback(
        Output("items-table", "data"),
        Input("refresh-btn", "n_clicks"),
        Input("filter-validated", "value"),
        prevent_initial_call=False,
    )
    def refresh_table(_n, filter_value):
        df = load_items_df()
        if filter_value == "validated":
            df = df[df["validated"] == 1]
        elif filter_value == "unvalidated":
            df = df[df["validated"] == 0]
        # Render screenshot column as markdown clickable link
        def render_cell(path: str | None) -> str:
            if not path or not os.path.exists(path):
                return ""
            # Map absolute file path to web route
            try:
                rel = os.path.relpath(path, SCREENSHOT_ROOT)
                url = f"/screenshots/{rel}"
            except Exception:
                url = ""
            return f"[Open]({url})"
        if not df.empty:
            df = df.copy()
            df["screenshot_path"] = df["screenshot_path"].apply(render_cell)
        return df.to_dict("records")

    @app.callback(
        Output("items-table", "data", allow_duplicate=True),
        Input("items-table", "data_timestamp"),
        State("items-table", "data"),
        prevent_initial_call=True,
    )
    def save_edits(_timestamp, rows):
        # Persist validated edits
        with sqlite3.connect(DB_PATH) as conn:
            for row in rows:
                conn.execute(
                    """
                    UPDATE extracted_items
                    SET validated = ?,
                        validated_by = COALESCE(?, validated_by),
                        validated_at = CASE WHEN ? = 1 THEN datetime('now') ELSE validated_at END
                    WHERE id = ?
                    """,
                    (
                        int(row.get("validated") or 0),
                        row.get("validated_by"),
                        int(row.get("validated") or 0),
                        int(row["id"]),
                    ),
                )
            conn.commit()
        return rows

    return app


def main() -> None:
    app = create_app()
    app.run_server(debug=True)


if __name__ == "__main__":
    main()
