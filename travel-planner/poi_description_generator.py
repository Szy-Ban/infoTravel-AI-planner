from typing import Dict, List
from text_generator import TextGenerator

class POIDescriptionGenerator:
    def __init__(self, text_generator: TextGenerator):
        # Generate text for POI descriptions
        self.text_generator = text_generator

    def generate_poi_description(self, poi: Dict) -> str:
        # Prompts for description of a specific POI
        system_prompt = (
            "You are a knowledgeable travel guide providing concise, engaging descriptions "
            "of points of interest in Ireland."
        )
        user_prompt = f"""
        Create a brief, engaging description for this point of interest:
        Name: {poi.get('Name', '')}
        Location: {poi.get('AddressLocality', '')}, {poi.get('AddressRegion', '')}, Ireland
        Categories: {poi.get('Tags', '')}
        Include a practical tip for visitors.
        Keep the description concise but informative.
        """

        try:
            return self.text_generator.generate_chat_completion(system_prompt, user_prompt)
        except Exception as e:
            print(f"Error generating description for {poi['Name']}: {str(e)}")
            return f"Description unavailable for {poi['Name']}"

    def generate_day_summary(self, pois: List[Dict]) -> str:
        # Summarize a day
        system_prompt = (
            "You are a helpful travel planner creating concise day summaries for travelers in Ireland."
        )
        poi_names = [poi['Name'] for poi in pois]
        user_prompt = (
            "Create a brief summary for a day of travel visiting these locations: "
            f"{', '.join(poi_names)}. Include travel tips and suggested timing."
        )

        try:
            return self.text_generator.generate_chat_completion(system_prompt, user_prompt)
        except Exception as e:
            print(f"Error generating day summary: {str(e)}")
            return "Day summary unavailable"

    def generate_itinerary_tips(self, preferences: Dict, pois: List[Dict]) -> str:
        # Travel tips
        system_prompt = (
            "You are a knowledgeable travel advisor providing practical tips for traveling in Ireland."
        )
        poi_count = len(pois)
        regions = list(set(poi['AddressRegion'] for poi in pois))

        user_prompt = f"""
        Create travel tips for an itinerary with these details:
        - Duration: {preferences['trip_duration']} days
        - Number of locations: {poi_count}
        - Regions covered: {', '.join(regions)}
        - Transportation: {preferences['transportation']}
        - Pace: {preferences['pace']}
        - Special interests: {', '.join(preferences['interests'])}

        Include:
        1. General travel tips
        2. Logistics advice
        3. Time management suggestions
        4. Weather and packing recommendations
        """

        try:
            return self.text_generator.generate_chat_completion(system_prompt, user_prompt)
        except Exception as e:
            print(f"Error generating itinerary tips: {str(e)}")
            return "Itinerary tips unavailable"