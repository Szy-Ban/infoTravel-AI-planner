import json
from typing import Dict, List
from user_preferences import UserPreferences
import math


class POIManager:
    def __init__(self):
        self.pois = []

    def load_and_filter_pois(self, file_path: str, preferences: UserPreferences) -> Dict:

        # load POI from file and filtering
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                self.pois = json.load(f)
        except Exception as e:
            raise Exception(f"Error loading POI data: {str(e)}")

        filtered_pois = self._filter_pois(preferences)
        return self._organize_pois(filtered_pois)

    def _filter_pois(self, preferences: UserPreferences) -> List[Dict]:

        # Filter POIs based on user preferences
        filtered = self.pois.copy()

        # Filter by region
        if preferences.regions:
            filtered = [
                poi for poi in filtered
                if poi['AddressRegion'] in preferences.regions
            ]

        # Filter by interests
        filtered = [
            poi for poi in filtered
            if any(
                interest.lower() in poi['Tags'].lower()
                for interest in preferences.interests
            )
        ]

        # Filter based on special requirements
        if preferences.special_requirements:
            filtered = [
                poi for poi in filtered
                if any(
                    req.lower() in poi['Tags'].lower()
                    for req in preferences.special_requirements
                )
            ]

        return filtered

    def _organize_pois(self, filtered_pois: List[Dict]) -> Dict:

        # POI by region and category
        organized = {
            "total_count": len(filtered_pois),
            "by_region": {},
            "by_category": {}
        }

        for poi in filtered_pois:

            # Organize by region
            region = poi['AddressRegion']
            if region not in organized["by_region"]:
                organized["by_region"][region] = []
            organized["by_region"][region].append(poi)

            # Organize by category (using Tags)
            tags = [tag.strip() for tag in poi['Tags'].split(',')]
            for tag in tags:
                if tag not in organized["by_category"]:
                    organized["by_category"][tag] = []
                organized["by_category"][tag].append(poi)

        # Add counts
        organized["region_counts"] = {
            region: len(pois)
            for region, pois in organized["by_region"].items()
        }
        organized["category_counts"] = {
            category: len(pois)
            for category, pois in organized["by_category"].items()
        }

        return organized

    @staticmethod
    def calculate_distance(poi1: Dict, poi2: Dict) -> float:

        # calculate distance between POIs (Haversine form)
        lat1, lon1 = float(poi1['Latitude']), float(poi1['Longitude'])
        lat2, lon2 = float(poi2['Latitude']), float(poi2['Longitude'])

        R = 6371  # Earth's radius in kilometers

        # Convert coordinates to radians
        lat1, lon1 = math.radians(lat1), math.radians(lon1)
        lat2, lon2 = math.radians(lat2), math.radians(lon2)

        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
        c = 2 * math.asin(math.sqrt(a))

        return R * c  # Distance in kilometers