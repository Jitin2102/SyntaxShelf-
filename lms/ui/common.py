import sqlite3
from collections.abc import Callable

import streamlit as st


def attempt(action: Callable[[], object], success: str) -> None:
    try:
        result = action()
    except sqlite3.Error as err:
        st.error(f"Database error: {err}")
        return
    except ValueError as err:
        st.error(str(err))
        return
    st.session_state["flash"] = success.format(result)
    st.rerun()


def show_flash() -> None:
    message = st.session_state.pop("flash", None)
    if message:
        st.success(message)
