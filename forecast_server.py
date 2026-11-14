from http.server import SimpleHTTPRequestHandler, HTTPServer
from pathlib import Path
import csv
import json


project_folder = Path(__file__).parent
forecast_file = project_folder / "cleaned_data" / "weekly_disruption_forecast.csv"


class ForecastHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(project_folder), **kwargs)

    def do_GET(self):
        if self.path == "/data":
            if not forecast_file.exists():
                self.send_error(404, "Run model_analysis.py to create the forecast CSV.")
                return

            with forecast_file.open("r", newline="", encoding="utf-8-sig") as file:
                forecast_rows = list(csv.DictReader(file))

            response = json.dumps(forecast_rows).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(response)))
            self.end_headers()
            self.wfile.write(response)
            return

        if self.path == "/":
            self.path = "/forecast_dashboard.html"

        super().do_GET()


if __name__ == "__main__":
    print("Open http://127.0.0.1:8000 in your browser. Press Ctrl+C to stop.")
    HTTPServer(("127.0.0.1", 8000), ForecastHandler).serve_forever()
