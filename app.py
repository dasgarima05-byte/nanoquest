"""NanoQuest: Engineer the Cure. Run with:  streamlit run app.py"""
import base64

import streamlit as st

from levels import LEVELS
from sandbox import run_in_sandbox

st.set_page_config(page_title="NanoQuest", page_icon="🧲", layout="wide")

ss = st.session_state
ss.setdefault("done", {})      # level id -> XP earned
ss.setdefault("hints", {})     # level id -> number of hints used
ss.setdefault("results", {})   # level id -> last sandbox result
ss.setdefault("resets", {})    # level id -> counter, to reset the editor

labels = [lv.short for lv in LEVELS]
unlocked = labels[: len(ss["done"]) + 1]
ss.setdefault("nav", labels[0])
if ss["nav"] not in unlocked:
    ss["nav"] = unlocked[-1]


def go_next(label):
    ss["nav"] = label


# ------------------------------------------------------------------ sidebar
st.sidebar.title("🧲 NanoQuest")
st.sidebar.caption("Engineer the Cure")
st.sidebar.radio("Mission", unlocked, key="nav")
st.sidebar.progress(len(ss["done"]) / len(LEVELS),
                    text=f"{len(ss['done'])} of {len(LEVELS)} missions complete")
st.sidebar.metric("XP", sum(ss["done"].values()))
st.sidebar.caption("Hints cost 10 XP each. Science constants are simplified for "
                   "learning; check the literature before relying on them.")

idx = labels.index(ss["nav"])
level = LEVELS[idx]

# ------------------------------------------------------------------ level
st.title(level.title)
st.caption(level.skill)
st.markdown(level.story)

with st.expander("🔬 The science behind it", expanded=True):
    st.markdown(level.science)
    if level.formula:
        st.latex(level.formula)

left, right = st.columns([3, 2])

with left:
    editor_key = f"code_{level.id}_{ss['resets'].get(level.id, 0)}"
    code = st.text_area("Your code", value=level.starter, height=420, key=editor_key)
    c1, c2, c3 = st.columns(3)
    run = c1.button("▶ Run code", type="primary", use_container_width=True)
    if c2.button("↺ Reset code", use_container_width=True):
        ss["resets"][level.id] = ss["resets"].get(level.id, 0) + 1
        ss["results"].pop(level.id, None)
        st.rerun()
    used = ss["hints"].get(level.id, 0)
    hint_label = f"💡 Hint ({used}/{len(level.hints)})" if used < len(level.hints) \
        else "🔓 Show solution"
    hint = c3.button(hint_label, use_container_width=True)

    if hint:
        ss["hints"][level.id] = min(used + 1, len(level.hints) + 1)
    used = ss["hints"].get(level.id, 0)
    for i in range(min(used, len(level.hints))):
        st.info(f"Hint {i + 1}: {level.hints[i]}")
    if used > len(level.hints):
        st.warning("Reference solution:")
        st.code(level.solution, language="python")

    if run:
        with st.spinner("Running simulation..."):
            res = run_in_sandbox(level.id, code)
        ss["results"][level.id] = res
        if res["passed"] and level.id not in ss["done"]:
            penalty = 10 * min(ss["hints"].get(level.id, 0), len(level.hints) + 1)
            ss["done"][level.id] = max(10, level.xp - penalty)
            st.rerun()

with right:
    st.subheader("Output")
    res = ss["results"].get(level.id)
    if res is None:
        st.write("Run your code to see results here.")
    else:
        if res["error"]:
            st.error(res["error"])
        if res["stdout"]:
            st.code(res["stdout"], language="text")
        if res["figure"]:
            st.image(base64.b64decode(res["figure"]))
        for m in res["messages"]:
            (st.success if res["passed"] else st.warning)(m)

if level.id in ss["done"]:
    st.success(f"Mission complete! +{ss['done'][level.id]} XP")
    if idx + 1 < len(LEVELS):
        st.button("Next mission ➜", on_click=go_next, args=(labels[idx + 1],))
    else:
        st.balloons()
        st.header("🎉 Patient cured!")
        st.write(f"You engineered the nanofluid, kept it stable, dosed it safely, "
                 f"plotted the release, and debugged the delivery. "
                 f"Final score: **{sum(ss['done'].values())} XP**.")
