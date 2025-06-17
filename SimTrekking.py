import streamlit as st
import random
from collections import Counter
import pandas as pd
import altair as alt

st.set_page_config(layout="wide")
st.title("Simulatie: blauw → eruit, goud → reset")

# SIDEBAR: Businessregels en invoer
with st.sidebar:
    st.header("Businessregels")
    st.markdown("""
- Een zak bevat 1 gouden bal en 𝑛 blauwe ballen, waarbij 𝑛 wordt opgegeven door de gebruiker.
- Per beurt (trekking) wordt één bal getrokken.
- Wordt een blauwe bal getrokken, dan verdwijnt deze uit de zak (geen teruglegging).
- Wordt een gouden bal getrokken, dan worden alle ballen terug in de zak gedaan, zodat de samenstelling weer 1 gouden en 𝑛 blauwe ballen is.
- Dit proces wordt herhaald voor het aantal trekkingen dat door de gebruiker is opgegeven.
""")

    st.header("Simulatie-invoer")
    aantal_blauwe_start = st.number_input("Aantal blauwe ballen (𝑛) bij start", min_value=1, value=3)
    aantal_trekkingen = st.number_input("Aantal trekkingen", min_value=1, value=100)
    toon_log = st.checkbox("Toon simulatielog", value=True)
    simulatie_starten = st.button("Start simulatie")

    # Formule voor gemiddelde kans
    st.markdown("---")
    st.markdown(f"### Gemiddelde theoretische kans op goud bij {aantal_blauwe_start} blauwe ballen:")
    with st.container():
        # st.markdown(
            # """
            # <div style='border: 1px solid #ddd; border-radius: 10px; padding: 10px; background-color: #f0f0f0;'>
            # <strong>Formule:</strong><br><br>
            # """,
            # unsafe_allow_html=True
        # )
        formule = rf"P_{{gem}} = \frac{{2}}{{n + 2}} = \frac{{2}}{{{aantal_blauwe_start} + 2}} = {2 / (aantal_blauwe_start + 2):.3f}"
        st.latex(formule)
        st.markdown("</div>", unsafe_allow_html=True)

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

    p_gem_simulatie = totaal_goud / aantal_trekkingen
    
    st.subheader("Resultaten")
    st.write(f"Totaal trekkingen: **{aantal_trekkingen}**")
    st.write(f"Aantal keer goud getrokken: **{totaal_goud}**")
    st.write(f"Aantal keer blauw getrokken: **{totaal_blauw}**")    
    st.markdown(
    rf"**Gemiddelde kans op goud uit simulatie:** $P_{{gem}} = \frac{{{totaal_goud}}}{{{aantal_trekkingen}}} = {totaal_goud / aantal_trekkingen:.3f}$"
)

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

    # ➕ GRAFIEK: Aantal blauwe ballen per trekking
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

    if toon_log:
        st.subheader("Simulatielog")
        for regel in log:
            st.text(regel)
