import pandas as pd
import streamlit as st
import folium as fm
import pandas as pd
import geopandas as gpd
from streamlit_folium import folium_static
import json

MWmap = fm.Map(location=[39.9137, -85.27474], tiles="CartoDB positron",
               name="Light Map", zoom_start=5.7, attr="My Data attribution")


healthscore = f"data/sample_data.csv"  # Healthscore  data data with zipcodes
usincome = f"data/usincome_filt.csv"
merged_geo = f"data/midwest.geojson"
towns = f"data/town_names.xlsx"


# Concatenate the GeoDataFrames
# merged_gdf = gpd.GeoDataFrame(pd.concat([gdf1, gdf2, gdf3], ignore_index=True))

# merged_gdf.to_file('midwest.geojson', driver='GeoJSON')

# merged_geo = json.loads(merged_gdf.to_json())


health_df = pd.read_csv(healthscore)
incomedata_df = pd.read_csv(usincome)  # reading in income data.
towns_df = pd.read_excel(towns)


incomedata_df = incomedata_df[["ZIP", "Households Median Income (Dollars)"]]
towns_df = towns_df[["Zip Code", "Official USPS city name"]]


# incomedata_df["household_median_income"] = incomedata_df["household_median_income"].apply(pd.to_numeric, errors='coerce')  # converting income column into numeric.


# turn population numbers into integers.
# popdata_df["Pop2020"] = popdata_df["Pop2020"].astype("int")


# group by zipcode, summing up Pop2020, keeping ZipName, Tract and TractGeoID
# convert Pop2020 to integer from string

incomedata_df = incomedata_df.rename(
    columns={'Households Median Income (Dollars)': 'Median Income'})

towns_df = towns_df.rename(
    columns={'Official USPS city name': 'Town Name'})

health_df = health_df.merge(
    incomedata_df, left_on="zip_code", right_on="ZIP", how="inner")

health_df = health_df.merge(
    towns_df, left_on="zip_code", right_on="Zip Code", how="inner")

healthscore_df = health_df.groupby("zip_code").agg(
    {'health_score': 'mean', 'Median Income': 'first', 'Town Name': 'first'}).reset_index()

healthscore_df = healthscore_df.rename(
    columns={'health_score': 'Health Score'})

# print(healthscore_df)

# healthscore_df = healthscore_df['Median Income'].apply(lambda x: "{:,}".format(x))

# healthscore_df = healthscore_df.merge(incomedata_df, left_on="zip_code", right_on="ZIP", how="inner")


# print(type(healthscore_df["Health Score"][0]))

# healthscore_df["Households Median Income (Dollars)"] = healthscore_df["Households Median Income (Dollars)"].astype(float)


choice = ["Health Score"]  # drop down selections.
choice_selected = st.selectbox("Choose", choice)

mp = fm.Choropleth(
    geo_data=merged_geo,
    name="choropleth",
    data=healthscore_df,
    columns=["zip_code", choice_selected],
    # understand how to get the loop down to the string
    key_on="feature.properties.ZCTA5CE10",
    fill_color="YlOrRd",
    fill_opacity=0.7,
    line_opacity=0.1,
    legend_name=choice_selected,
    nan_fill_color='lightgrey'

)
mp.add_to(MWmap)

healthscore_df_indexed = healthscore_df.set_index('zip_code')

for s in mp.geojson.data['features']:
    try:
        s['properties']['Health Score'] = healthscore_df_indexed.loc[int(
            s['properties']['ZCTA5CE10']), 'Health Score']
        s['properties']['Median Income'] = healthscore_df_indexed.loc[int(
            s['properties']['ZCTA5CE10']), 'Median Income']
        s['properties']['Town'] = healthscore_df_indexed.loc[int(
            s['properties']['ZCTA5CE10']), 'Town Name']

    except KeyError:
        continue


fm.GeoJsonTooltip(['Town', 'Health Score', 'Median Income']).add_to(mp.geojson)

# fm.LayerControl().add_to(mp)


folium_static(MWmap, width=900, height=550)


st.markdown("""
### Food Desert Project
The map above visualizes a food "health score" for Kentucky, Indiana, and Ohio based on data from Kroger-branded stores operating in a zipcode. 
            The health score ranges from 0-100 is based on nutritional value based on data obtained from Open Food Facts & the factors below:
- **Inventory**: Volume of products a particular Kroger-branded store is carrying.
- **Price**: Cost of a product relative to its average price.

""")
