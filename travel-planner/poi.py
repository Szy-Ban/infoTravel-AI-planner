from dataclasses import dataclass
from typing import Optional, List

@dataclass
class POI:
    name: str
    location: str
    short_description: str
    full_description: str
    image: str
    realization_of_interest_per_day: int = 2
    category: Optional[str] = None
    visit_duration: Optional[int] = 120  # default 2 hours in minutes
    tags: Optional[List[str]] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    address_region: Optional[str] = None
    address_locality: Optional[str] = None
    telephone: Optional[str] = None
    url: Optional[str] = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = []

    @classmethod
    def from_json(cls, data: dict) -> 'POI':
        return cls(
            name=data['Name'],
            location=f"{data.get('AddressLocality', '')}, {data.get('AddressRegion', '')}",
            short_description="",  # AI
            full_description="",   # AI
            image="",              # Placeholder
            category=next(iter(data.get('Tags', '').split(',')), None),
            tags=data.get('Tags', '').split(','),
            latitude=float(data.get('Latitude', 0)),
            longitude=float(data.get('Longitude', 0)),
            address_region=data.get('AddressRegion'),
            address_locality=data.get('AddressLocality'),
            telephone=data.get('Telephone'),
            url=data.get('Url')
        )

    def to_dict(self) -> dict:
        return {
            'name': self.name,
            'location': self.location,
            'short_description': self.short_description,
            'full_description': self.full_description,
            'image': self.image,
            'category': self.category,
            'visit_duration': self.visit_duration,
            'tags': self.tags,
            'coordinates': {
                'latitude': self.latitude,
                'longitude': self.longitude
            },
            'contact': {
                'telephone': self.telephone,
                'url': self.url
            },
            'address': {
                'region': self.address_region,
                'locality': self.address_locality
            }
        }

    def estimate_visit_duration(self) -> int:
        category_durations = {
            'Museum': 180,
            'Castle': 120,
            'Park': 90,
            'Church': 45,
            'Gallery': 60,
            'Garden': 60,
            'Historic': 90,
            'Walking': 120,
        }
        if self.category:
            for cat, duration in category_durations.items():
                if cat.lower() in self.category.lower():
                    return duration
        return self.visit_duration

    def is_compatible_with_interests(self, interests: List[str]) -> bool:
        if not interests:
            return True
        return any(
            interest.lower() in tag.lower()
            for interest in interests
            for tag in self.tags
        )