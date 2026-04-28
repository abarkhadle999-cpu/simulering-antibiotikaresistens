# -*- coding: utf-8 -*-
"""
Created on Fri Apr 24 10:32:27 2026

@author: abdirahmaan.barkhad
"""

import streamlit as st
import pandas as pd
import random

st.title("Antibiotic Resistance Simulator")

st.write("""
This simulation shows how antibiotic resistance can evolve in a bacterial population.
Students can change parameters like antibiotic usage, mutation rate, bacterial growth
and horizontal gene transfer.
""")

# =====================================================
# INPUT PARAMETERS
# =====================================================

st.header("Simulation Settings")

col1, col2 = st.columns(2)

with col1:
    generations = st.number_input("Time Steps", 10, 500, 100)
    initial_sensitive = st.number_input("Initial Sensitive Bacteria", 100, 100000, 1000)
    initial_resistant = st.number_input("Initial Resistant Bacteria", 0, 10000, 10)

with col2:
    mutation_rate = st.slider("Mutation Rate", 0.0, 0.1, 0.01)
    transfer_rate = st.slider("Horizontal Gene Transfer Rate", 0.0, 0.5, 0.01)
    growth_rate = st.slider("Bacterial Growth Rate", 1.0, 3.0, 1.5)

antibiotic_level = st.selectbox(
    "Antibiotic Usage Level",
    ["1 - Low", "2 - Medium", "3 - High", "4 - Very High"]
)

# convert level to numeric strength
antibiotic_strength = int(antibiotic_level[0]) * 0.15

# =====================================================
# SIMULATION MODEL
# =====================================================

def simulate_step(sensitive, resistant):

    total = sensitive + resistant
    if total == 0:
        return 0, 0

    # =====================================================
    # 1. TILLVÄXT
    # =====================================================
    sensitive *= growth_rate
    resistant *= growth_rate

    # =====================================================
    # 2. MUTATION (S -> R)
    # =====================================================
    mutations = sensitive * mutation_rate
    sensitive -= mutations
    resistant += mutations

    # =====================================================
    # 3. HORIZONTAL GENE TRANSFER
    # =====================================================
    transfer = sensitive * transfer_rate * (resistant / (sensitive + resistant))
    sensitive -= transfer
    resistant += transfer

    # =====================================================
    # 4. ANTIBIOTIKA (SELEKTION)
    # =====================================================
    # Känsliga dör mycket
    sensitive *= (1 - antibiotic_strength * 0.7)

    # Resistenta dör lite (kostnad finns)
    resistant *= (1 - antibiotic_strength * 0.1)

    # =====================================================
    # 5. SELEKTIONSFÖRDEL FÖR RESISTENTA
    # =====================================================
    resistant *= (1 + antibiotic_strength * 0.3)

    # =====================================================
    # 6. HÅLL POPULATIONEN STABIL (undvik explosion/kollaps)
    # =====================================================
    total = sensitive + resistant
    max_pop = 100000

    if total > max_pop:
        scale = max_pop / total
        sensitive *= scale
        resistant *= scale

    return sensitive, resistant
# =====================================================
# RUN SIMULATION
# =====================================================

if st.button("Run Simulation"):

    sensitive = initial_sensitive
    resistant = initial_resistant

    results = []

    for t in range(generations):

        sensitive, resistant = simulate_step(sensitive, resistant)

        results.append([t, sensitive, resistant])

    df = pd.DataFrame(results, columns=[
        "Time Step",
        "Sensitive Bacteria",
        "Resistant Bacteria"
    ])

    st.success("Simulation completed")

    # graph
    st.line_chart(df.set_index("Time Step"))

    # table
    st.subheader("Simulation Data")
    st.dataframe(df)

    # =====================================================
    # DOWNLOAD DATA
    # =====================================================

    csv = df.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="Download Results (CSV)",
        data=csv,
        file_name="antibiotic_resistance_simulation.csv",
        mime="text/csv"
    )
