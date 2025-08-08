"""
Dash App (minimal scaffold)

This provides a simple Dash layout that will later be connected to real data
from SQLite/CSV. For now, it renders an example chart using a dummy pandas
DataFrame.

Run directly with:  python -m app.dashboards.app
"""
from __future__ import annotations

import os
import pathlib
import io
import base64
from typing import List, Dict, Any

import pandas as pd
from dash import Dash, dcc, html, Input, Output, State, dash_table
from dash.exceptions import PreventUpdate
import plotly.express as px

from app.scrapers.bank_scraper import download_pdfs
from app.processors.pdf_processor import extract_tables_to_dataframes


DATA_DIR = "/workspace/data"
PDF_DIR = os.path.join(DATA_DIR, "pdfs")
CSV_DIR = os.path.join(DATA_DIR, "csv")


def ensure_data_dirs() -> None:
    os.makedirs(PDF_DIR, exist_ok=True)
    os.makedirs(CSV_DIR, exist_ok=True)


def list_pdfs() -> List[str]:
    ensure_data_dirs()
    try:
        return sorted([
            name for name in os.listdir(PDF_DIR)
            if name.lower().endswith(".pdf") and os.path.isfile(os.path.join(PDF_DIR, name))
        ])
    except FileNotFoundError:
        return []


def unique_destination(directory: str | os.PathLike, filename: str) -> str:
    directory_path = pathlib.Path(directory)
    directory_path.mkdir(parents=True, exist_ok=True)
    destination = directory_path / filename
    if not destination.exists():
        return str(destination)
    stem = destination.stem
    suffix = destination.suffix
    for index in range(1, 1000):
        candidate = directory_path / f"{stem}_{index}{suffix}"
        if not candidate.exists():
            return str(candidate)
    raise RuntimeError("Too many conflicting filenames while saving file.")


def _serialize_tables(tables: List[pd.DataFrame]) -> List[Dict[str, Any]]:
    serialized: List[Dict[str, Any]] = []
    for df in tables:
        # Normalize column names to strings to avoid JSON issues
        df = df.copy()
        df.columns = [str(c) if c is not None else "" for c in df.columns]
        serialized.append({
            "columns": [{"name": col, "id": col} for col in df.columns],
            "data": df.to_dict(orient="records"),
        })
    return serialized


def _compute_numeric_summary(tables: List[pd.DataFrame]) -> pd.DataFrame | None:
    # Combine numeric columns from all tables and compute column sums
    numeric_frames: List[pd.DataFrame] = []
    for df in tables:
        numeric_df = df.select_dtypes(include=["number"])  # type: ignore[arg-type]
        if not numeric_df.empty:
            numeric_frames.append(numeric_df)
    if not numeric_frames:
        return None
    combined = pd.concat(numeric_frames, axis=0, ignore_index=True)
    # Drop columns with all NaNs
    combined = combined.dropna(axis=1, how="all")
    if combined.empty:
        return None
    sums = combined.sum(numeric_only=True)
    summary_df = sums.reset_index()
    summary_df.columns = ["metric", "value"]
    return summary_df


def create_app() -> Dash:
    ensure_data_dirs()

    app = Dash(__name__)

    app.layout = html.Div([
        html.H2("Financial Analysis Dashboard"),
        dcc.Tabs(id="tabs", value="tab-scrape", children=[
            dcc.Tab(label="Scrape PDFs", value="tab-scrape", children=[
                html.Div([
                    html.Label("Start URL"),
                    dcc.Input(id="start-url", type="url", placeholder="https://example.com/investors", style={"width": "70%"}),
                    html.Button("Scrape", id="scrape-btn", n_clicks=0, style={"marginLeft": "12px"}),
                ], style={"marginBottom": "12px"}),
                html.Div(id="scrape-status", style={"marginBottom": "8px"}),
                dash_table.DataTable(
                    id="scrape-table",
                    columns=[
                        {"name": "url", "id": "url"},
                        {"name": "output_path", "id": "output_path"},
                        {"name": "ok", "id": "ok"},
                        {"name": "status_code", "id": "status_code"},
                        {"name": "error", "id": "error"},
                    ],
                    data=[],
                    page_size=10,
                    style_cell={"whiteSpace": "nowrap", "textOverflow": "ellipsis", "maxWidth": 0},
                    style_table={"overflowX": "auto"},
                ),
            ]),
            dcc.Tab(label="Parse PDF", value="tab-parse", children=[
                html.Div([
                    html.Div([
                        html.Label("Upload PDF"),
                        dcc.Upload(
                            id="upload-pdf",
                            children=html.Div([
                                "Drag and Drop or ", html.A("Select PDF")
                            ]),
                            multiple=False,
                            style={
                                "width": "100%",
                                "height": "60px",
                                "lineHeight": "60px",
                                "borderWidth": "1px",
                                "borderStyle": "dashed",
                                "borderRadius": "5px",
                                "textAlign": "center",
                                "marginBottom": "12px",
                            },
                        ),
                    ]),
                    html.Div([
                        html.Label("Or choose an existing PDF"),
                        dcc.Dropdown(id="pdf-dropdown", options=[{"label": name, "value": name} for name in list_pdfs()], placeholder="Select a PDF from /data/pdfs"),
                    ], style={"marginBottom": "12px"}),
                    html.Button("Parse PDF", id="parse-btn", n_clicks=0),
                ], style={"marginBottom": "12px"}),
                html.Div(id="parse-summary", style={"marginBottom": "8px"}),
                html.Div(id="tables-container"),
            ]),
            dcc.Tab(label="Visualize", value="tab-visualize", children=[
                html.Div(id="visualize-content", children=[
                    html.Div("Load or parse a PDF to see charts."),
                    dcc.Graph(id="summary-figure"),
                ])
            ]),
        ]),
        dcc.Store(id="scrape-results"),
        dcc.Store(id="parsed-tables"),
    ], style={"padding": "12px"})

    # Callbacks

    @app.callback(
        Output("scrape-status", "children"),
        Output("scrape-table", "data"),
        Output("scrape-results", "data"),
        Output("pdf-dropdown", "options"),
        Input("scrape-btn", "n_clicks"),
        State("start-url", "value"),
        prevent_initial_call=True,
    )
    def handle_scrape(n_clicks: int, start_url: str | None):  # type: ignore[unused-ignore]
        if not start_url:
            return (
                html.Span("Please provide a start URL.", style={"color": "#a00"}),
                [],
                None,
                [{"label": name, "value": name} for name in list_pdfs()],
            )
        results = download_pdfs(start_url=start_url, output_dir=PDF_DIR)
        # Convert dataclass list to list of dicts for table
        rows = [
            {
                "url": r.url,
                "output_path": r.output_path,
                "ok": r.ok,
                "status_code": r.status_code,
                "error": r.error,
            }
            for r in results
        ]
        ok_count = sum(1 for r in results if r.ok)
        status = html.Span(
            f"Downloaded {ok_count} of {len(results)} PDF(s).",
            style={"color": "#080" if ok_count else "#a00"},
        )
        return status, rows, rows, [{"label": name, "value": name} for name in list_pdfs()]

    @app.callback(
        Output("pdf-dropdown", "options"),
        Output("pdf-dropdown", "value"),
        Input("upload-pdf", "contents"),
        State("upload-pdf", "filename"),
        prevent_initial_call=True,
    )
    def handle_upload(contents: str | None, filename: str | None):
        if not contents or not filename:
            raise PreventUpdate
        # Save uploaded PDF into PDF_DIR
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        destination = unique_destination(PDF_DIR, filename)
        with open(destination, 'wb') as f:
            f.write(decoded)
        options = [{"label": name, "value": name} for name in list_pdfs()]
        return options, pathlib.Path(destination).name

    @app.callback(
        Output("parsed-tables", "data"),
        Output("parse-summary", "children"),
        Output("tables-container", "children"),
        Input("parse-btn", "n_clicks"),
        State("pdf-dropdown", "value"),
        prevent_initial_call=True,
    )
    def handle_parse(n_clicks: int, selected_pdf: str | None):  # type: ignore[unused-ignore]
        if not selected_pdf:
            return None, html.Span("Please select a PDF first.", style={"color": "#a00"}), []
        pdf_path = os.path.join(PDF_DIR, selected_pdf)
        if not os.path.exists(pdf_path):
            return None, html.Span("Selected PDF not found on disk.", style={"color": "#a00"}), []
        try:
            tables = extract_tables_to_dataframes(pdf_path)
        except Exception as exc:
            return None, html.Span(f"Failed to parse PDF: {exc}", style={"color": "#a00"}), []

        if not tables:
            return None, html.Span("No tables detected in the PDF.", style={"color": "#a00"}), []

        serialized = _serialize_tables(tables)

        # Render tables
        table_components: List[Any] = []
        for idx, tbl in enumerate(serialized):
            table_components.append(html.H4(f"Table {idx + 1}"))
            table_components.append(dash_table.DataTable(
                columns=tbl["columns"],
                data=tbl["data"],
                page_size=10,
                style_table={"overflowX": "auto", "marginBottom": "16px"},
                style_cell={"whiteSpace": "nowrap", "textOverflow": "ellipsis", "maxWidth": 0},
            ))

        summary_text = html.Span(f"Parsed {len(serialized)} table(s) from {selected_pdf}.")
        return serialized, summary_text, table_components

    @app.callback(
        Output("summary-figure", "figure"),
        Input("parsed-tables", "data"),
    )
    def update_summary_chart(serialized_tables: List[Dict[str, Any]] | None):
        if not serialized_tables:
            return px.scatter(title="No numeric data available yet")
        # Rehydrate DataFrames
        tables: List[pd.DataFrame] = []
        for item in serialized_tables:
            cols = [c["id"] for c in item["columns"]]
            df = pd.DataFrame(item["data"], columns=cols)
            # Attempt to coerce numeric columns
            for col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="ignore")
            tables.append(df)
        summary_df = _compute_numeric_summary(tables)
        if summary_df is None or summary_df.empty:
            return px.scatter(title="No numeric columns detected to summarize")
        fig = px.bar(summary_df, x="metric", y="value", title="Numeric Column Sums")
        fig.update_layout(margin=dict(l=20, r=20, t=50, b=20))
        return fig

    return app


def main() -> None:
    app = create_app()
    app.run_server(debug=True)


if __name__ == "__main__":
    main()
