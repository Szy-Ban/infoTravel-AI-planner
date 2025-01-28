from dataclasses import dataclass
from typing import List, Optional
from config import (
    DEFAULT_DAILY_ACTIVITIES,
    DEFAULT_TRIP_DURATION,
    DEFAULT_START_TIME,
    DEFAULT_END_TIME
)


@dataclass
class UserPreferences:
    interests: List[str]
    trip_duration: int = DEFAULT_TRIP_DURATION
    realization_of_pois_per_day: int = DEFAULT_DAILY_ACTIVITIES
    preferred_pace: str = "moderate"
    regions: List[str] = None
    preferred_start_time: str = DEFAULT_START_TIME
    preferred_end_time: str = DEFAULT_END_TIME
    require_breaks: bool = True
    preferred_transportation: str = "car"
    budget_level: str = "moderate"
    special_requirements: Optional[List[str]] = None

    def __post_init__(self):
        if self.regions is None:
            self.regions = []
        if self.special_requirements is None:
            self.special_requirements = []

    def validate(self):
        if not self.interests:
            raise ValueError("At least one interest must be specified")

        if self.trip_duration < 1 or self.trip_duration > 14:
            raise ValueError("Trip duration must be between 1 and 14 days")

        if self.realization_of_pois_per_day < 1 or self.realization_of_pois_per_day > 5:
            raise ValueError("Number of POIs per day must be between 1 and 5")

        if self.preferred_pace not in ["slow", "moderate", "fast"]:
            raise ValueError("Preferred pace must be slow, moderate, or fast")

        if self.budget_level not in ["low", "moderate", "high"]:
            raise ValueError("Budget level must be low, moderate, or high")

        return True

    def to_dict(self):
        return {
            "interests": self.interests,
            "trip_duration": self.trip_duration,
            "daily_activities": self.realization_of_pois_per_day,
            "pace": self.preferred_pace,
            "regions": self.regions,
            "start_time": self.preferred_start_time,
            "end_time": self.preferred_end_time,
            "breaks": self.require_breaks,
            "transportation": self.preferred_transportation,
            "budget": self.budget_level,
            "special_requirements": self.special_requirements
        }
