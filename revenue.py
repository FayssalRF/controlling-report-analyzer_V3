import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

def revenue_tab():
    st.header("💸 ÅTD Revenue Sammenligning 2025 vs. 2024")
    
    uploaded_file = st.file_uploader("Upload revenue-rapport (Excel)", type=["xlsx"])
    if not uploaded_file:
        st.info("Upload en Excel-fil for at starte analysen.")
        return
    
    # Læs Excel og det relevante ark
    try:
        xls = pd.ExcelFile(uploaded_file)
        df = xls.parse("Revenue", skiprows=4)
    except Exception as e:
        st.error(f"Fejl ved indlæsning af Excel-fil: {e}")
        return

    # Fjern rækker uden 'Company Name'
    df = df.dropna(subset=["Company Name"])
    
    # Udtræk de kolonner, der indeholder datoer
    date_cols = [col for col in df.columns if isinstance(col, str) and '-' in col]
    df_dates = df[['Company Name', 'Name', 'ID'] + date_cols].copy()
    
    # Konverter de dato-relaterede kolonner til datetime-objekter
    try:
        new_date_cols = pd.to_datetime(df_dates.columns[3:], format='%b-%y', errors='coerce')
    except Exception as e:
        st.error(f"Fejl ved konvertering af datoer: {e}")
        return
    df_dates.columns = df_dates.columns[:3].tolist() + new_date_cols.tolist()
    
    # Filtrer kun de kolonner, der svarer til 2024 og 2025
    datetime_cols = [col for col in df_dates.columns[3:] if isinstance(col, pd.Timestamp) and col.year in [2024, 2025]]
    df_dates = df_dates[['Company Name', 'Name', 'ID'] + datetime_cols]
    
    # Opdel dato-kolonnerne efter år
    cols_2024 = [col for col in datetime_cols if col.year == 2024]
    cols_2025 = [col for col in datetime_cols if col.year == 2025]
    
    # Find de fælles måneder (samme periode) for begge år
    common_months = set(col.month for col in cols_2024) & set(col.month for col in cols_2025)
    cols_2024_common = sorted([col for col in cols_2024 if col.month in common_months])
    cols_2025_common = sorted([col for col in cols_2025 if col.month in common_months])
    
    # Beregn ÅTD revenue for de fælles måneder
    df_dates['ÅTD 2024'] = df_dates[cols_2024_common].sum(axis=1)
    df_dates['ÅTD 2025'] = df_dates[cols_2025_common].sum(axis=1)
    
    # Filtrer kun de virksomheder, der har revenue i begge år (dvs. hvor sum ikke er 0)
    df_filtered = df_dates[(df_dates['ÅTD 2024'] != 0) & (df_dates['ÅTD 2025'] != 0)].copy()
    
    # Beregn procentvis ændring
    df_filtered['YTD Change %'] = ((df_filtered['ÅTD 2025'] - df_filtered['ÅTD 2024']) / df_filtered['ÅTD 2024']) * 100
    
    st.subheader("ÅTD Revenue Sammenligning")
    st.dataframe(
        df_filtered[['Company Name', 'ÅTD 2024', 'ÅTD 2025', 'YTD Change %']]
        .sort_values('YTD Change %', ascending=False)
    )
    
    st.subheader("Top 10 virksomheder - YTD Change %")
    top_10 = df_filtered.sort_values('YTD Change %', ascending=False).head(10)
    # Fast bredde (300px ~ 3 inches ved standard dpi) forbliver uafhængig af browserens zoom
    fig, ax = plt.subplots(figsize=(3, 1.5))
    ax.barh(top_10['Company Name'], top_10['YTD Change %'])
    ax.set_xlabel("YTD Change %")
    ax.set_title("Top 10 - YTD Change 2025 vs. 2024")
    st.pyplot(fig, use_container_width=False)
    
    st.metric("Antal virksomheder analyseret", f"{len(df_filtered)}")
