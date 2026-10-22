from datetime import date

import pandas as pd
import streamlit as st

from ..repositories import loans, stats

DUE_SOON_DAYS = 7


def _active_frame() -> pd.DataFrame:
    """Active loans as a DataFrame, with a 'days_late' column when due_on exists."""
    rows = [dict(row) for row in loans.active()]
    df = pd.DataFrame(rows)
    if df.empty:
        return df

    if "due_on" in df.columns:
        due = pd.to_datetime(df["due_on"], errors="coerce")
        days_left = (due - pd.Timestamp(date.today())).dt.days
        df["days_late"] = (-days_left).clip(lower=0).where(df["status"] == "Overdue", 0)
        df["_days_left"] = days_left
    return df


def _count_due_soon(df: pd.DataFrame) -> str:
    if df.empty or "_days_left" not in df.columns:
        return "–"
    soon = df[(df["status"] != "Overdue") & df["_days_left"].between(0, DUE_SOON_DAYS)]
    return str(len(soon))


def _visible(df: pd.DataFrame) -> pd.DataFrame:
    """Hide helper columns from tables."""
    return df.drop(
        columns=[c for c in df.columns if c.startswith("_")], errors="ignore"
    )


def _column_config(df: pd.DataFrame) -> dict:
    config = {}
    if "days_late" in df.columns:
        config["days_late"] = st.column_config.NumberColumn("Days late", format="%d")
    return config


def render() -> None:
    st.header("Dashboard")
    st.caption(f"Overview as of {date.today():%d %B %Y}")

    data = stats.summary()
    df = _active_frame()

    # ---------- Metric cards ----------
    cards = [
        ("📖 Titles", data["titles"], "Distinct book titles in the catalogue"),
        ("👥 Members", data["members"], "Registered library members"),
        ("🔄 Issued", data["issued"], "Books currently out on loan"),
        ("⚠️ Overdue", data["overdue"], "Loans past their due date"),
        ("⏳ Due soon", _count_due_soon(df), f"Due within {DUE_SOON_DAYS} days"),
    ]
    for col, (label, value, hint) in zip(st.columns(len(cards)), cards):
        col.metric(label, value, help=hint)

    st.write("")

    # ---------- Charts ----------
    if not df.empty:
        left, right = st.columns(2)

        with left:
            st.subheader("Loan status")
            status_counts = (
                df["status"].value_counts().rename_axis("Status").to_frame("Loans")
            )
            st.bar_chart(status_counts, use_container_width=True)

        with right:
            st.subheader("Returns due by date")
            if "due_on" in df.columns:
                by_due = (
                    df.assign(due_on=pd.to_datetime(df["due_on"], errors="coerce"))
                    .dropna(subset=["due_on"])
                    .groupby(df["due_on"].astype(str))
                    .size()
                    .rename("Loans")
                    .to_frame()
                    .sort_index()
                )
                st.bar_chart(by_due, use_container_width=True)
            else:
                st.info("Due dates are not available.")

    # ---------- Tables ----------
    tab_overdue, tab_active = st.tabs(["⚠️ Overdue books", "📚 All active loans"])

    with tab_overdue:
        overdue = df[df["status"] == "Overdue"] if not df.empty else df
        if overdue.empty:
            st.success("Nothing overdue. 🎉")
        else:
            if "days_late" in overdue.columns:
                overdue = overdue.sort_values("days_late", ascending=False)
            shown = _visible(overdue)
            st.dataframe(
                shown,
                use_container_width=True,
                hide_index=True,
                column_config=_column_config(shown),
            )

    with tab_active:
        if df.empty:
            st.info("No active loans right now.")
        else:
            query = st.text_input(
                "Search active loans",
                placeholder="Type a book, member or status…",
                label_visibility="collapsed",
            ).strip()
            shown = _visible(df)
            if query:
                mask = (
                    shown.astype(str)
                    .apply(lambda col: col.str.contains(query, case=False, na=False))
                    .any(axis=1)
                )
                shown = shown[mask]
            st.caption(f"{len(shown)} loan(s)")
            st.dataframe(
                shown,
                use_container_width=True,
                hide_index=True,
                column_config=_column_config(shown),
            )
