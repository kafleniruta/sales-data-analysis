
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import warnings
df=pd.read_csv("cleandata.csv")
df.head()

df["profit_margin"] = (df["profit"] / df["sales"]).replace([np.inf, -np.inf], np.nan)
df["is_loss"]       = df["profit"] < 0
df["revenue_band"]  = pd.cut(
    df["sales"],
    bins=[0, 100, 500, 1000, 5000, np.inf],
    labels=["<100", "100-500", "500-1K", "1K-5K", ">5K"]
)

print("\nFeature engineering complete.")
print(df[[ "profit_margin", "is_loss", "revenue_band"]].head(3))
import plotly.express as px
import pycountry

# Aggregate data by country
country_agg = df.groupby('country').agg({
    'sales': 'sum',
    'profit': 'sum',
    'order_id': 'count'
}).reset_index()
country_agg.columns = ['country', 'total_sales', 'total_profit', 'orders']
country_agg['profit_margin_pct'] = (country_agg['total_profit'] / country_agg['total_sales'] * 100).round(2)

# Add ISO-3 codes for countries
def get_iso3(country_name):
    try:
        return pycountry.countries.lookup(country_name).alpha_3
    except:
        return None

country_agg['iso3'] = country_agg['country'].apply(get_iso3)

# Remove countries with missing ISO3 codes
country_agg = country_agg.dropna(subset=['iso3'])

# Create choropleth using ISO-3
fig_map = px.choropleth(
    country_agg,
    locations="iso3",
    color="total_profit",
    hover_name="country",
    hover_data={
        "total_sales": ":,.0f",
        "orders": True,
        "profit_margin_pct": True
    },
    color_continuous_scale="Viridis",
    title="🌍  Country-Level Profit Distribution",
    locationmode="ISO-3"  # ✅ updated to prevent deprecation warning
)

fig_map.update_layout(
    height=600,
    margin=dict(l=20, r=20, t=50, b=20),
    paper_bgcolor="white",
    geo=dict(
        showframe=False,
        showcoastlines=True,
        projection_type='natural earth',
        lakecolor="LightBlue"
    ),
    coloraxis_colorbar=dict(
        title="Total Profit (USD)",
        tickprefix="$",
        lenmode="fraction",
        len=0.7
    )
)

fig_map.update_traces(
    hovertemplate=(
        "<b>%{hovertext}</b><br><br>"
        "Total Profit: $%{z:,.0f}<br>"
        "Total Sales: $%{customdata[0]:,.0f}<br>"
        "Orders: %{customdata[1]}<br>"
        "Profit Margin: %{customdata[2]:.1f}%<extra></extra>"
    )
)


fig_map.show()
