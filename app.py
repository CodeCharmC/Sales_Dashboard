import pandas as pd
from dash import Dash, dcc, html, Input, Output, dash_table, State
import plotly.express as px
from sqlalchemy import create_engine
import os

# Get DATABASE_URL from environment variable
DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
   raise ValueError("DATABASE_URL environment variable is not set!")

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL)

def load_data():
   # Query all sales data from Neon
   df = pd.read_sql("SELECT * FROM sales", engine, parse_dates=["OrderDate"])

   # Drop missing values
   if df.isnull().values.any():
      df = df.dropna()
   
   # Drop duplicates
   if df.duplicated().any():
      df = df.drop_duplicates()

   if "TotalSales" not in df.columns or df["TotalSales"].isnull().all():
      df["TotalSales"] = df["Quantity"] * df["UnitPrice"]
   df["OrderDate"] = pd.to_datetime(df["OrderDate"])
   df["Region"] = df["Region"].fillna("Unknown")

   df["ProfitMargin"] = (df["Profit"] / df["TotalSales"]) * 100
   df["ProfitMargin"] = df["ProfitMargin"].fillna(0)
   return df

df = load_data()

app = Dash(__name__)
server = app.server 

regions = sorted(df["Region"].dropna().unique())
region_options = [{"label": r, "value": r} for r in regions]

min_date = df["OrderDate"].min().date()
max_date = df["OrderDate"].max().date()

# ---------- Layout ----------

app.layout = html.Div([
   # Sidebar
   html.Div([
      html.Button("🔎 Filters", id="toggle-btn", n_clicks=0, style={"width": "100%", "border": "1px solid #ddd", "borderRadius": "12px"}),
      # Expanded filter panel (hidden by default)
      html.Div([
         html.Label("Date range"),
         dcc.DatePickerRange(
            id="date-picker",
            start_date=min_date,
            end_date=max_date,
            display_format="YYYY-MM-DD"
         ),
         html.Br(), html.Br(),

         html.Label("Region (multiple)"),
         dcc.Dropdown(
            id="region-dropdown",
            options=region_options,
            value=regions,
            multi=True,
            placeholder="Select region(s)"
         ),
      ], id="filter-panel", style={"display": "none"})  # start hidden
   ], className="sidebar"),
    
   # Main Content Area
   html.Div([
      html.H2("📊 Sales Dashboard", style={"textAlign": "center", "marginBottom": "25px", "color": "#333", "fontWeight": "700", "fontSize": "32px"}),
      # KPI Cards
      html.Div([
         html.Div([
            html.H4(id="total-sales", style={"fontSize": "26px", "fontWeight": "bold", "color": "#2c3e50"}),
            html.P("Total Revenue", style={"color": "#555"})
         ], className="kpi-card", style={
            "flex": "1", 
            "minWidth": "0",
            "backgroundColor": "#ffffff",
            "border": "1px solid #ddd",
            "borderRadius": "12px",
            "padding": "20px",
            "boxShadow": "0 4px 12px rgba(0,0,0,0.08)",
            "textAlign": "center"
         }),

         html.Div([
            html.H4(id="total-orders", style={"fontSize": "26px", "fontWeight": "bold", "color": "#2c3e50"}),
            html.P("Total Orders", style={"color": "#555"})
         ], className="kpi-card", style={
            "flex": "1",
            "minWidth": "0",
            "backgroundColor": "#ffffff",
            "border": "1px solid #ddd",
            "borderRadius": "12px",
            "padding": "20px",
            "boxShadow": "0 4px 12px rgba(0,0,0,0.08)",
            "textAlign": "center"
         }),

         html.Div([
            html.H4(id="total-profit", style={"fontSize": "26px", "fontWeight": "bold", "color": "#2c3e50"}),
            html.P("Total Profit", style={"color": "#555"})
         ], className="kpi-card", style={
            "flex": "1",
            "minWidth": "0",
            "backgroundColor": "#ffffff", 
            "border": "1px solid #ddd",
            "borderRadius": "12px",
            "padding": "20px",
            "boxShadow": "0 4px 12px rgba(0,0,0,0.08)",
            "textAlign": "center"
         }),

         html.Div([
            html.H4(id="profit-margin", style={
               "fontSize": "26px", "fontWeight": "bold", "color": "#2c3e50"}),
            html.P("Average Profit Margin", style={"color": "#555"})
         ], className="kpi-card", style={
            "flex": "1",
            "minWidth": "0",
            "backgroundColor": "#ffffff",
            "border": "1px solid #ddd",
            "borderRadius": "12px",
            "padding": "20px",
            "boxShadow": "0 4px 12px rgba(0,0,0,0.08)",
            "textAlign": "center"
         }),
      ], style={"display": "flex", "gap": "15px", "marginBottom": "20px", "width": "100%"}),

      # Middle Row: Revenue by Region + Trend
      html.Div([
         html.Div(dcc.Graph(id="revenue-by-region"), style={
            "flex": "1",
            "minWidth": "0",
            "backgroundColor": "#fff",
            "border": "1px solid #ddd",
            "borderRadius": "12px", 
            "padding": "10px",
            "boxShadow": "0 4px 12px rgba(0,0,0,0.08)"
         }),
         html.Div(dcc.Graph(id="trend-over-time"), style={
            "flex": "1",
            "minWidth": "0",
            "backgroundColor": "#fff",
            "border": "1px solid #ddd",
            "borderRadius": "12px",
            "padding": "10px",
            "boxShadow": "0 4px 12px rgba(0,0,0,0.08)"
         })
      ], style={"display": "flex", "gap": "15px", "marginBottom": "20px"}),

      # Top Products Graph
      html.Div([
         dcc.Graph(id="top-products")
      ], style={
         "marginTop": "20px",
         "border": "1px solid #ddd",
         "borderRadius": "12px",
         "padding": "15px",
         "backgroundColor": "#fff",
         "boxShadow": "0 4px 12px rgba(0,0,0,0.06)"
      }),

      html.Div([
         dcc.Graph(id="profit-margin-category")
      ], style={
         "marginTop": "20px",
         "border": "1px solid #ddd",
         "borderRadius": "12px",
         "padding": "15px",
         "backgroundColor": "#fff",
         "boxShadow": "0 4px 12px rgba(0,0,0,0.06)"
      }),


      # Bottom Row: Recent Orders Table
      html.Div([
         html.Div([
            html.H4("Recent Orders", style={"marginBottom": "20px", "color": "#333"}),
            dash_table.DataTable(
               id="table",
               columns=[{"name": c, "id": c} for c in ["OrderID", "OrderDate", "Region", "Product", "Category", "Quantity", "UnitPrice", "TotalSales", "Profit"]],
               page_size=8,
               style_table={"overflowX": "auto"},
               style_cell={
                  "fontSize": "12px",
                  "padding": "8px",
                  "color": "#555",
                  "textAlign": "left"
               },
               style_header={
                  "backgroundColor": "#f2f2f2",
                  "fontWeight": "bold",
                  "color": "#333"
               },
               style_data_conditional=[
                  {"if": {"row_index": "odd"}, "backgroundColor": "#fafafa"}
               ]
            )
         ], style={
            "flex": "1",
            "minWidth": "0",
            "border": "1px solid #ddd",
            "borderRadius": "12px",
            "padding": "15px",
            "backgroundColor": "#fff",
            "boxShadow": "0 4px 12px rgba(0,0,0,0.08)"
         }),
      ], style={"display": "flex", "gap": "15px", "marginTop": "20px"})
   ], style={"width": "100%", "margin": "0 auto", "padding": "20px", "boxSizing": "border-box",  "overflowX": "hidden",})

], style={"fontFamily": "Arial, sans-serif", "padding": "20px", "backgroundColor": "#f7f7f7"})


# ---------- Callbacks ----------

@app.callback(
   Output("filter-panel", "style"),
   Input("toggle-btn", "n_clicks"),
   State("filter-panel", "style")
)
def toggle_sidebar(n_clicks, current_style):
   if n_clicks % 2 == 1:
      return {"display": "block"}  # expand
   return {"display": "none"}      # collapse

@app.callback(
   Output("revenue-by-region", "figure"),
   Output("trend-over-time", "figure"),
   Output("top-products", "figure"),
   Output("profit-margin-category", "figure"),
   Output("table", "data"),
   Output("total-sales", "children"),
   Output("total-orders", "children"),
   Output("total-profit", "children"),
   Output("profit-margin", "children"),  
   Input("date-picker", "start_date"),
   Input("date-picker", "end_date"),
   Input("region-dropdown", "value"),
)

def update_charts(start_date, end_date, selected_regions):
   dff = df.copy()
   if start_date:
      dff = dff[dff["OrderDate"] >= pd.to_datetime(start_date)]
   if end_date:
      dff = dff[dff["OrderDate"] < pd.to_datetime(end_date) + pd.Timedelta(days=1)]
   if selected_regions:
      dff = dff[dff["Region"].isin(selected_regions)]

   if dff.empty:
      return (
         px.bar(title="No data"),          
         px.line(title="No data"), 
         px.bar(title="No data"),
         px.bar(title="No data"),
         [],  
         "$0.00", 
         "0",  
         "$0.00",  
         "0%"  
      )
   
   df_category = (
      dff.groupby("Category")
      .agg({"TotalSales": "sum", "Profit": "sum"})
      .reset_index()
   )
   df_category["ProfitMargin"] = (df_category["Profit"] / df_category["TotalSales"]) * 100
   df_category["ProfitMargin"] = df_category["ProfitMargin"].fillna(0)

   # Charts
   df_reg = dff.groupby("Region", as_index=False)["TotalSales"].sum()
   fig_region = px.bar(df_reg, x="Region", y="TotalSales", title="Revenue by Region")

   df_time = dff.groupby(pd.Grouper(key="OrderDate", freq="MS"))["TotalSales"].sum().reset_index()
   fig_trend = px.line(df_time, x="OrderDate", y="TotalSales", markers=True, title="Revenue Trend by Month")
   fig_trend.update_layout(xaxis=dict(tickformat="%b", dtick="M1", title="Month"), yaxis=dict(title="Revenue"))

   df_prod = dff.groupby("Product", as_index=False)["TotalSales"].sum().nlargest(10, "TotalSales")
   fig_top = px.bar(df_prod, x="TotalSales", y="Product", orientation="h", title="Top 10 Products")
   fig_top.update_layout(yaxis={"categoryorder": "total ascending"}, xaxis={"title": "Revenue"})

   fig_category = px.bar(
      df_category,
      x="Category",
      y="ProfitMargin",
      color="ProfitMargin",
      color_continuous_scale="RdYlGn",
      title="Profit Margin by Product Category",
      text=df_category["ProfitMargin"].round(1).astype(str) + "%",
   )

   fig_category.update_traces(textposition="outside")
   fig_category.update_layout(yaxis_title="Profit Margin (%)", xaxis_title="Product Category")


   # KPIs
   total_sales_value = dff['TotalSales'].sum()
   total_profit_value = dff['Profit'].sum()

   total_sales = human_format(total_sales_value, "$")
   total_orders = f"{dff['OrderID'].nunique():,}"
   total_profit = human_format(total_profit_value, "$")

   if total_sales_value > 0:
      profit_margin = f"{(total_profit_value / total_sales_value) * 100:.2f}%"
   else:
      profit_margin = "0%"

   table_data = dff.sort_values("OrderDate", ascending=False).head(100).to_dict("records")
   return fig_region, fig_trend, fig_top, fig_category, table_data, total_sales, total_orders, total_profit, profit_margin


def human_format(num, currency="$"):
   """
   Converts a number into a human-readable format like 1.2K, 3.4M
   """
   if num >= 1_000_000:
      return f"{currency}{num/1_000_000:.1f}M"
   elif num >= 1_000:
      return f"{currency}{num/1_000:.1f}K"
   else:
      return f"{currency}{num:.0f}"


# if __name__ == "__main__":
#    app.run(debug=True, port=8050)

from werkzeug.middleware.proxy_fix import ProxyFix
app.server.wsgi_app = ProxyFix(app.server.wsgi_app)
