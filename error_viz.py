from pathlib import Path
import ipywidgets as widgets
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

analog_df = pd.read_csv("analog_profiling_results_20230719.csv")
naive_df = pd.read_csv("naive_profiling_results_20230719.csv")

varnames_rb = widgets.RadioButtons(
    value="t2m", 
    options=["sst", "t2m", "msl", "z"], 
    description="Variable name"
)
search_domains_rb = widgets.RadioButtons(
    value="alaska", 
    options=["alaska", "northern_hs", "north_pacific", "panarctic"], 
    description="Search domain"
)
forecast_domains_rb = widgets.RadioButtons(
    value="alaska", 
    options=["alaska", "northern_hs", "north_pacific", "panarctic"], 
    description="Forecast domain"
)
ref_date_dd = widgets.RadioButtons(
    options=analog_df.reference_date.unique(),
    value=analog_df.reference_date.unique()[0],
    description="Reference\ndate",
    disabled=False,
)

controls = widgets.HBox([
    varnames_rb, 
    search_domains_rb, 
    forecast_domains_rb,
    ref_date_dd
])


def plot_error(varname, search_domain, forecast_domain, ref_date):
    fig, ax = plt.subplots(1, 1, figsize=(9, 5))
    query_str = (
        "forecast_domain == @forecast_domain "
        "& search_domain == @search_domain "
        "& variable == @varname "
        "& reference_date == @ref_date"
    )
    
    naive_query_str = query_str.replace("& search_domain == @search_domain", " ")
    plot_df = naive_df.query(
        # only forecast_domain in naive_df
        naive_query_str
    )[["forecast_date", "naive_2.5", "naive_50", "naive_97.5"]].set_index("forecast_date")
    
    analog_query_str = query_str + " & anomaly_search == True"
    plot_df = plot_df.join(
        analog_df.query(analog_query_str)[[
            "forecast_date", "forecast_error"
        ]].set_index("forecast_date").rename(
            columns={"forecast_error": "anom_forecast_error"}
        )
    )
    
    anom_query_str = analog_query_str.replace("anomaly_search == True", "anomaly_search == False")
    plot_df = plot_df.join(
        analog_df.query(anom_query_str)[[
            "forecast_date", "forecast_error"
        ]].set_index("forecast_date").rename(
            columns={"forecast_error": "forecast_error"}
        )
    )
    
    plot_df.plot(title=f"{varname},  search={search_domain}, forecast={forecast_domain},  Reference Date: {ref_date}", ax=ax)
    ax.set_ylabel("RMSE")
    
    return


widget = widgets.interactive(plot_error, varname=varnames_rb, search_domain=search_domains_rb, forecast_domain=forecast_domains_rb, ref_date=ref_date_dd)
output = widget.children[-1]
