#README.tsx
___ Dashboard for Sales Analysis ___

📌This project provides an interactive sales dashboard built with Python, Dash, and Plotly.

▶ Steps to Run
1. Make sure you have Python 3.8+ installed.
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   or use `pip install dash pandas plotly` on your terminal 
   
3. Place the sales.csv file inside the same directory as app.py.
4. Run the app:
   ```bash
   python app.py
   ```
5. Open your browser and go to:
   http://127.0.0.1:8050
The dashboard will open in a new tab.

📊 Features & Graphs
- KPI Cards → Show Total Sales, Orders, and Profit
- Revenue by Region → Bar chart summarizing sales across regions
- Revenue Trend → Line chart of monthly sales trends
- Top Products → Horizontal bar chart of the top 10 products
- Profit margins → Shows bar chart for profit margins by categoris
- Recent Orders Table → Interactive table with pagination

📦 requirements.txt
# for running app.py locally
- Here are the dependencies you should list in requirements.txt:
   ```bash
   dash
   pandas
   plotly
   ```
- If you use a specific version for compatibility, you can pin them, e.g.:
   ```bash
   pandas==2.2.2
   dash==2.17.0
   plotly==5.24.0
   ```
# for uploading on vercel
   ```bash
   psycopg2-binary
   pandas
   dash
   plotly
   werkzeug
   ```

📝 README.txt
- This file provides an overview of the dashboard and its features.

📝 Notes
- Date range and region filters are available in the sidebar (expand/collapse with 🔎 Filters button).
- Missing regions are categorized as "Unknown".
- If TotalSales is missing in the dataset, it is auto-calculated as:
  ```bash
   TotalSales = Quantity × UnitPrice
   ```


⚠️ Caution
- The app runs in debug mode by default. For production, set:
  ```bash
   app.run(debug=False)
   ```
- Ensure sales.csv is pre-cleaned (duplicates removed, missing values handled).
- If dataset is very large, rendering might slow down (consider sampling data).
- Do not expose sensitive data (e.g., profit margins) if sharing this dashboard publicly.

Live Dashboard: https://sales-dashboard-five-gamma.vercel.app/