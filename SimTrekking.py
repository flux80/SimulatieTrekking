import streamlit as st
import random
from collections import Counter
import pandas as pd
import altair as alt

st.set_page_config(layout="wide")
st.title("Simulatie: blauw = verwijderen, goud = reset")

# SIDEBAR: Businessregels en invoer
with st.sidebar:
    st.header("Businessregels")
    st.markdown("""
- De zak bevat 1 gouden en een door de gebruiker opgegeven aantal blauwe ballen.  
- Per beurt wordt **één bal getrokken**.  
- Als er een **blauwe bal** wordt getrokken:  
  - Die bal **verdwijnt uit de zak** (geen teruglegging).  
- Als er een **gouden bal** wordt getrokken:  
  - **Alle ballen worden teruggelegd** (dus opnieuw: 1 gouden + X blauwe).
""")

    st.header("Simulatie-invoer")
    aantal_blauwe_start = st.number_input("Aantal blauwe ballen bij start", min_value=1, value=3)
    aantal_trekkingen = st.number_input("Aantal trekkingen", min_value=1, value=100)    
    simulatie_starten = st.button("Start simulatie")

# HOOFDGEDEELTE: Resultaten en log
if simulatie_starten:
    start_zak = ["goud"] + ["blauw"] * aantal_blauwe_start
    zak = start_zak.copy()
    totaal_goud = 0
    totaal_blauw = 0
    log = []
    state_counter = Counter()
    blauw_per_trekking = []

    for i in range(1, aantal_trekkingen + 1):
        huidige_state = tuple(sorted(zak))
        state_counter[huidige_state] += 1

        # ➕ Aantal blauwe vóór trekking
        blauw_per_trekking.append(zak.count("blauw"))

        if not zak:
            zak = start_zak.copy()
            log.append(f"⛔️ Trekking {i}: zak was leeg, automatische reset naar {zak}")
            huidige_state = tuple(sorted(zak))
            state_counter[huidige_state] += 1
            blauw_per_trekking[-1] = zak.count("blauw")  # correctie na reset

        getrokken = random.choice(zak)

        if getrokken == "goud":
            totaal_goud += 1
            zak = start_zak.copy()
            log.append(f"🎯 Trekking {i}: goud getrokken → reset zak naar {zak}")
        else:
            totaal_blauw += 1
            zak.remove("blauw")
            log.append(f"🔵 Trekking {i}: blauw getrokken → zak = {zak}")

    st.subheader("Resultaten")
    st.write(f"Totaal trekkingen: **{aantal_trekkingen}**")
    st.write(f"Aantal keer goud getrokken: **{totaal_goud}**")
    st.write(f"Aantal keer blauw getrokken: **{totaal_blauw}**")

    df_states = pd.DataFrame([
        {
            'State': f"{state.count('blauw')} blauwe, 1 gouden",
            'Aantal keer': count,
            'Aantal blauwe': state.count("blauw")
        }
        for state, count in state_counter.items()
    ])
    df_states = df_states.sort_values("Aantal blauwe", ascending=False)

    st.subheader("Verdeling van zak-samenstellingen (states)")
    st.dataframe(df_states[["State", "Aantal keer"]])

    chart = alt.Chart(df_states).mark_bar().encode(
        x=alt.X('State:N', sort=list(df_states["State"])),
        y='Aantal keer:Q',
        tooltip=['State', 'Aantal keer']
    ).properties(
        width=600,
        height=400
    )
    st.altair_chart(chart, use_container_width=True)

    # ➕ NIEUWE GRAFIEK: Aantal blauwe ballen per trekking
    df_blauw = pd.DataFrame({
        "Trekking": list(range(1, aantal_trekkingen + 1)),
        "Aantal blauwe": blauw_per_trekking
    })

    st.subheader("Aantal blauwe ballen per trekking")
    chart_blauw = alt.Chart(df_blauw).mark_line(point=True).encode(
        x=alt.X('Trekking:Q', title="Trekking nummer"),
        y=alt.Y('Aantal blauwe:Q', title="Aantal blauwe ballen"),
        tooltip=['Trekking', 'Aantal blauwe']
    ).properties(
        width=700,
        height=300
    )
    st.altair_chart(chart_blauw, use_container_width=True)
    
    st.subheader("Simulatielog")
    for regel in log:
        st.text(regel)
