from http.server import SimpleHTTPRequestHandler, HTTPServer
from html import escape
from pathlib import Path
import csv

project_folder = Path(__file__).parent
forecast_file = project_folder / "cleaned_data" / "weekly_disruption_forecast.csv"
index_file = project_folder / "templates" / "index.html"

def make_forecast_rows():
  rows = []

  with forecast_file.open("r", newline="", encoding="utf-8-sig") as file:
      for forecast in csv.DictReader(file):
          week = escape(forecast["forecast_week"])
          risk = float(forecast["predicted_risk"])
          actual = int(forecast["actual_disruption"])

          result = "Disruption" if actual == 1 else "No disruption"

          rows.append(
              f"<tr><td>{week}</td>"
              f"<td>{risk:.1%}</td>"
              f"<td>{result}</td></tr>"
          )

  return "\n".join(rows)

class ForecastHandler(SimpleHTTPRequestHandler):
  def __init__(slef, *args, **kwargs):
    super().__init__(*args, directory=str(project_folder), **kwargs)
  
  def do_GET(self):
    if self.path == "/":
      page = index_file.read_text(encoding="utf-8")
      page = page.replace("{{ forecast_rows }}", make_forecast_rows())
      response = page.encode("utf-8")

      self.send_response(200)
      self.send_header("Content-Type", "text/html; charset=utf-8")
      self.send_header("Content-Length", str(len(response)))
      self.end_headers()
      self.wfile.write(response)
      return
      
    super().do_GET()

if __name__ == "__main__":
    print("Open http://127.0.0.1:8000 in your browser. Press Ctrl+C to stop.")
    HTTPServer(("127.0.0.1", 8000), ForecastHandler).serve_forever()