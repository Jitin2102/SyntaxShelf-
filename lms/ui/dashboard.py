import streamlit as st

from ..repositories import loans, stats


def render() -> None:
    st.header("Dashboard")
    data = stats.summary()
    cols = st.columns(4)
    for col, (label, key) in zip(
        cols,
        [("Titles", "titles"), ("Members", "members"), ("Issued", "issued"), ("Overdue", "overdue")],
    ):
        col.metric(label, data[key])

    st.subheader("Overdue books")
    overdue = [row for row in loans.active() if row["status"] == "Overdue"]
    if overdue:
        st.dataframe(overdue, use_container_width=True, hide_index=True)
    else:
        st.info("Nothing overdue.")
