import json
from typing import Dict, List
from user_preferences import UserPreferences
import math


class POIManager:
    def __init__(self):
        self.pois = []

    def load_and_filter_pois(self, file_path: str, preferences: UserPreferences) -> Dict:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                self.pois = json.load(f)
        except Exception as e:
            raise Exception(f"Error loading POI data: {str(e)}")

        filtered_pois = self._filter_pois(preferences)
        return self._organize_pois(filtered_pois)

    def _filter_pois(self, preferences: UserPreferences) -> List[Dict]:
        filtered = self.pois.copy()

        if preferences.regions:
            filtered = [
                poi for poi in filtered
                if poi['AddressRegion'] in preferences.regions
            ]

        filtered = [
            poi for poi in filtered
            if any(
                interest.lower() in poi['Tags'].lower()
                for interest in preferences.interests
            )
        ]

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
        organized = {
            "total_count": len(filtered_pois),
            "by_region": {},
            "by_category": {}
        }

        for poi in filtered_pois:
            region = poi['AddressRegion']
            if region not in organized["by_region"]:
                organized["by_region"][region] = []
            organized["by_region"][region].append(poi)

            tags = [tag.strip() for tag in poi['Tags'].split(',')]
            for tag in tags:
                if tag not in organized["by_category"]:
                    organized["by_category"][tag] = []
                organized["by_category"][tag].append(poi)

        organized["region_counts"] = {
            region: len(pois_list)
            for region, pois_list in organized["by_region"].items()
        }
        organized["category_counts"] = {
            category: len(pois_list)
            for category, pois_list in organized["by_category"].items()
        }
        return organized

    @staticmethod
    def calculate_distance(poi1: Dict, poi2: Dict) -> float:
        lat1, lon1 = float(poi1['Latitude']), float(poi1['Longitude'])
        lat2, lon2 = float(poi2['Latitude']), float(poi2['Longitude'])

        R = 6371  # Earth's radius in kilometers
        lat1, lon1 = math.radians(lat1), math.radians(lon1)
        lat2, lon2 = math.radians(lat2), math.radians(lon2)

        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
        c = 2 * math.asin(math.sqrt(a))
        return R * c
