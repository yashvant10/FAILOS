import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'failos_project.settings')
django.setup()

from failures.models import Country, State, City, EcosystemStats, IndustryPerformance

def populate():
    # Countries
    india, _ = Country.objects.get_or_create(name="India", code="IN")
    usa, _ = Country.objects.get_or_create(name="United States", code="US")

    # States India
    ka, _ = State.objects.get_or_create(name="Karnataka", country=india)
    mh, _ = State.objects.get_or_create(name="Maharashtra", country=india)
    dl, _ = State.objects.get_or_create(name="Delhi", country=india)

    # States USA
    ca, _ = State.objects.get_or_create(name="California", country=usa)
    ny, _ = State.objects.get_or_create(name="New York", country=usa)

    # Cities
    blr, _ = City.objects.get_or_create(name="Bangalore", state=ka)
    mys, _ = City.objects.get_or_create(name="Mysore", state=ka)
    mum, _ = City.objects.get_or_create(name="Mumbai", state=mh)
    sf, _ = City.objects.get_or_create(name="San Francisco", state=ca)
    la, _ = City.objects.get_or_create(name="Los Angeles", state=ca)

    # Stats - Bangalore
    stats_blr, _ = EcosystemStats.objects.get_or_create(city=blr)
    stats_blr.total_startups = 1200
    stats_blr.successful_startups = 430
    stats_blr.failed_startups = 770
    stats_blr.growth_rate = 12.5
    stats_blr.save()

    # Industries - Bangalore
    for ind, succ in [("AI Startups", True), ("SaaS", True), ("Fintech", True), ("Health Tech", True)]:
        IndustryPerformance.objects.get_or_create(city=blr, industry_name=ind, is_successful=True, count=100)
    for ind, succ in [("Generic E-commerce", False), ("Food Delivery Clones", False), ("Local Marketplaces", False)]:
        IndustryPerformance.objects.get_or_create(city=blr, industry_name=ind, is_successful=False, count=80)

    # Stats - San Francisco
    stats_sf, _ = EcosystemStats.objects.get_or_create(city=sf)
    stats_sf.total_startups = 5000
    stats_sf.successful_startups = 2000
    stats_sf.failed_startups = 3000
    stats_sf.growth_rate = 8.2
    stats_sf.save()

    print("Data population complete!")

if __name__ == "__main__":
    populate()
