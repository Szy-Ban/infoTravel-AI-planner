from typing import Dict, List
from openai import OpenAI
from config import GPT_MODEL, MAX_TOKENS, TEMPERATURE


class POIDescriptionGenerator:
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)

    def generate_poi_description(self, poi: Dict) -> str:

        # LLM description for POI
        prompt = self._create_poi_prompt(poi)

        try:
            response = self.client.chat.completions.create(
                model=GPT_MODEL,
                messages=[
                    {"role": "system",
                     "content": "You are a knowledgeable travel guide providing concise, engaging descriptions of points of interest in Ireland."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=MAX_TOKENS,
                temperature=TEMPERATURE
            )

            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error generating description for {poi['Name']}: {str(e)}")
            return f"Description unavailable for {poi['Name']}"

    def generate_day_summary(self, pois: List[Dict]) -> str:

        # summary for activity
        poi_names = [poi['Name'] for poi in pois]
        prompt = f"Create a brief summary for a day of travel visiting these locations: {', '.join(poi_names)}. Include travel tips and suggested timing."

        try:
            response = self.client.chat.completions.create(
                model=GPT_MODEL,
                messages=[
                    {"role": "system",
                     "content": "You are a helpful travel planner creating concise day summaries for travelers in Ireland."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=MAX_TOKENS,
                temperature=TEMPERATURE
            )

            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error generating day summary: {str(e)}")
            return "Day summary unavailable"

    def _create_poi_prompt(self, poi: Dict) -> str:

        # prompt for POI gen
        return f"""
        Create a brief, engaging description for this point of interest:
        Name: {poi['Name']}
        Location: {poi['AddressLocality']}, {poi['AddressRegion']}, Ireland
        Categories: {poi['Tags']}

        Include:
        1. What makes this place special
        2. What visitors can see or do
        3. Any relevant historical or cultural significance
        4. A practical tip for visitors

        Keep the description concise but informative.
        """

    def generate_itinerary_tips(self, preferences: Dict, pois: List[Dict]) -> str:

        # generate tips
        poi_count = len(pois)
        regions = list(set(poi['AddressRegion'] for poi in pois))

        prompt = f"""
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
            response = self.client.chat.completions.create(
                model=GPT_MODEL,
                messages=[
                    {"role": "system",
                     "content": "You are a knowledgeable travel advisor providing practical tips for traveling in Ireland."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=MAX_TOKENS,
                temperature=TEMPERATURE
            )

            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error generating itinerary tips: {str(e)}")
            return "Itinerary tips unavailable"