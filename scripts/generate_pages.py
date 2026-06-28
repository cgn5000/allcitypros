import os

cities = ["tampa", "pittsburgh", "orlando", "fortmyers", "charlotte"]

for city in cities:
    city_dir = f"content/{city}"
    # In a real run, this would read the tracker.md
    # For now, creating a sample landing page template
    with open(f"{city_dir}/index.html", "w") as f:
        f.write(f"<html><body><h1>Welcome to {city.capitalize()} - AllCityPros</h1><p>Top rated local services coming soon.</p></body></html>")
print("Scaffolding created for: " + ", ".join(cities))
