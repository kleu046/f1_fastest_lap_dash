# f1_fastest_lap_dash
Dashboard for fastest laps in F1 eveents

The dashboard is created using data retrieved using the fastf1 package: https://theoehrly.github.io/Fast-F1/

The package provides an ease way to retrieve data that originate from:

The official f1 data stream -> https://www.formula1.com/en/f1-live.html
Ergast web api -> ergast.com

f1.py: Functions were created to download specific session and driver data for laps and telemetry. The data are manipulated to a useful format and stored in pandas dataframes

f1_dash.py: The Plotly Dash package https://dash.plotly.com/ was used to create a dashboard.

The Dash board screenshot shows 2022 F1 Suzuka event.  The speed of the fastest lap from multiple drivers can be shown and the respective plots for speed vs position on trackare colour coded.

<img width="1306" alt="Screen Shot 2022-10-21 at 8 23 02 PM" src="https://user-images.githubusercontent.com/89670261/197137268-2f0a0219-9ed0-4e7f-bc16-dfc15c7f50b9.png">
