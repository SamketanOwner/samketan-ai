"""Customer-specific Business DNA profiles for Samketan AI.

Profiles define *where to research*, not claims that any buyer has a current need.
No scraping, network calls, AI inference or external dependencies.
"""
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class BusinessProfile:
    industry: str
    offering: str
    target_regions: tuple[str, ...]
    buyer_types: tuple[str, ...]
    demand_signals: tuple[str, ...]
    exclusion_terms: tuple[str, ...] = ()

    def __post_init__(self):
        if not self.industry.strip() or not self.offering.strip():
            raise ValueError("Industry and offering are required")
        if not self.target_regions or not all(x.strip() for x in self.target_regions):
            raise ValueError("At least one target region is required")
        if not self.buyer_types or not all(x.strip() for x in self.buyer_types):
            raise ValueError("At least one buyer type is required")
        if not self.demand_signals:
            raise ValueError("At least one demand signal is required")

    def research_queries(self, max_queries: int = 12) -> list[str]:
        if not 1 <= max_queries <= 50:
            raise ValueError("max_queries must be between 1 and 50")
        queries = []
        for region in self.target_regions:
            for signal in self.demand_signals:
                queries.append(f"{self.industry} {signal} {region}")
                if len(queries) >= max_queries:
                    return queries
        return queries


def warehouse_leasing(regions: tuple[str, ...] = ("Kalaburagi",)) -> BusinessProfile:
    return BusinessProfile(
        industry="warehouse leasing",
        offering="industrial warehouse space for lease",
        target_regions=regions,
        buyer_types=("logistics manager", "supply chain head", "distribution head", "3PL procurement"),
        demand_signals=(
            "new distribution centre expansion",
            "warehouse space requirement tender",
            "regional stock point opening",
            "logistics network expansion",
        ),
        exclusion_terms=("residential rental", "self storage"),
    )


def pulses_manufacturing(regions: tuple[str, ...] = ("Karnataka",)) -> BusinessProfile:
    return BusinessProfile(
        industry="pulses manufacturing",
        offering="bulk processed tur dal and pulses",
        target_regions=regions,
        buyer_types=("commodity buyer", "purchase manager", "food procurement head", "distributor"),
        demand_signals=(
            "tur dal bulk procurement tender",
            "pulses distributor appointment",
            "food processing raw material sourcing",
            "institutional pulses supply requirement",
        ),
        exclusion_terms=("retail recipe", "home cooking"),
    )


PROFILES = {
    "warehouse_leasing": warehouse_leasing,
    "pulses_manufacturing": pulses_manufacturing,
}


def make_profile(key: str, regions: Optional[tuple[str, ...]] = None) -> BusinessProfile:
    try:
        factory = PROFILES[key]
    except KeyError as exc:
        raise ValueError("Unknown business profile") from exc
    return factory() if regions is None else factory(regions)
