import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ga4 import GA4_SNIPPET  # noqa: E402

cities = ["tampa", "pittsburgh", "orlando", "fortmyers", "charlotte"]

for city in cities:
    city_dir = f"content/{city}"
    # In a real run, this would read the tracker.md
    # For now, creating a sample landing page template
    with open(f"{city_dir}/index.html", "w") as f:
        f.write(
            f"<html><head>\n{GA4_SNIPPET}</head><body><h1>Welcome to {city.capitalize()} - AllCityPros</h1>"
            f"<p>Top rated local services coming soon.</p></body></html>"
        )
print("Scaffolding created for: " + ", ".join(cities))
