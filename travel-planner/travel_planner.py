from typing import Dict, List
from openai import OpenAI
from datetime import datetime, timedelta
from poi_description_generator import POIDescriptionGenerator
from user_preferences import UserPreferences
from config import GPT_MODEL, MAX_TOKENS, TEMPERATURE


class TravelPlanner:
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
        self.description_generator = POIDescriptionGenerator(api_key)

    def _calculate_interests_accuracy(self, organized_days: List[List[Dict]], interests: List[str]) -> dict:

        # Calculate how well the planned activities match user interests
        # Initialize counters
        interest_matches = {interest: 0 for interest in interests}
        total_pois = 0

        # Count matches for each interest
        for day in organized_days:
            for poi in day:
                total_pois += 1
                poi_tags = poi['Tags'].lower().split(',')
                poi_tags = [tag.strip() for tag in poi_tags]

                for interest in interests:
                    if any(interest.lower() in tag for tag in poi_tags):
                        interest_matches[interest] += 1

        # Calculate percentages
        accuracy_per_interest = {}
        for interest, matches in interest_matches.items():
            percentage = (matches / total_pois * 100) if total_pois > 0 else 0
            accuracy_per_interest[interest] = round(percentage, 2)

        # Calculate overall accuracy
        total_matches = sum(interest_matches.values())
        max_possible_matches = total_pois * len(interests)
        overall_accuracy = (total_matches / max_possible_matches * 100) if max_possible_matches > 0 else 0

        # Calculate interests usage
        interests_used = sum(1 for matches in interest_matches.values() if matches > 0)
        interests_usage_percentage = (interests_used / len(interests) * 100) if interests else 0

        return {
            "overall_accuracy": round(overall_accuracy, 2),
            "accuracy_per_interest": accuracy_per_interest,
            "total_pois": total_pois,
            "matches_found": total_matches,
            "interest_matches": interest_matches,
            "interests_usage": {
                "used": interests_used,
                "total": len(interests),
                "percentage": round(interests_usage_percentage, 2)
            }
        }

    def generate_travel_plan(self, poi_data: Dict, preferences: UserPreferences) -> Dict:

        # Generate a complete travel plan based on POI data and user preferences
        # Extract POIs from organized data
        all_pois = []
        for region_pois in poi_data["by_region"].values():
            all_pois.extend(region_pois)

        # AI organize POIs into optimal days
        organized_days = self._organize_days(all_pois, preferences)

        # Calculate accuracy of interests matching
        interests_accuracy = self._calculate_interests_accuracy(organized_days, preferences.interests)

        # Complete plan
        plan = {
            "trip_summary": self._generate_trip_summary(organized_days, preferences),
            "days": [],
            "general_tips": self.description_generator.generate_itinerary_tips(
                preferences.to_dict(), all_pois
            ),
            "interests_accuracy": interests_accuracy
        }

        # Detailed day plans
        for day_number, day_pois in enumerate(organized_days, 1):
            day_plan = self._create_day_plan(day_number, day_pois, preferences)
            plan["days"].append(day_plan)

        return plan

    def _organize_days(self, pois: List[Dict], preferences: UserPreferences) -> List[List[Dict]]:
        # Organize POIs into days using OpenAI for optimization"

        filtered_pois = []
        for poi in pois:
            poi_tags = poi['Tags'].lower().split(',')
            poi_tags = [tag.strip() for tag in poi_tags]

            # Check if POI matches any user interest
            if any(interest.lower() in tag for interest in preferences.interests
                   for tag in poi_tags):
                filtered_pois.append(poi)

        # If we don't have enough POIs, use original list
        if len(filtered_pois) < preferences.trip_duration * preferences.realization_of_pois_per_day:
            filtered_pois = pois

        # Prepare POI information for the prompt
        poi_info = []
        for poi in filtered_pois:
            tags = poi['Tags'].split(',')
            matching_interests = [
                interest for interest in preferences.interests
                if any(interest.lower() in tag.lower() for tag in tags)
            ]
            info = f"- {poi['Name']} ({poi['AddressRegion']})"
            if matching_interests:
                info += f" [Matches interests: {', '.join(matching_interests)}]"
            poi_info.append(info)

        prompt = f"""
        Create a {preferences.trip_duration}-day travel plan with EXACTLY {preferences.realization_of_pois_per_day} activities per day.

        User interests: {', '.join(preferences.interests)}
        Transportation: {preferences.preferred_transportation}
        Pace: {preferences.preferred_pace}

        Requirements:
        1. MUST include EXACTLY {preferences.realization_of_pois_per_day} activities per day
        2. MUST be organized into EXACTLY {preferences.trip_duration} days
        3. Prioritize POIs that match user interests
        4. Consider geographical proximity for efficient travel
        5. Each day should be logistically feasible given the transportation method

        Available Points of Interest:
        {chr(10).join(poi_info)}

        Format your response as:
        Day 1:
        - [POI name exactly as provided]
        - [POI name exactly as provided]
        (etc. for each day)
        """

        try:
            response = self.client.chat.completions.create(
                model=GPT_MODEL,
                messages=[
                    {"role": "system",
                     "content": "You are a travel planning assistant that creates precise itineraries matching user requirements exactly."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=MAX_TOKENS,
                temperature=TEMPERATURE
            )

            # Process the response to extract organized days
            organized_text = response.choices[0].message.content
            organized_days = self._parse_organized_days(organized_text, filtered_pois)

            # Validate the organization
            if len(organized_days) != preferences.trip_duration:
                print("Warning: AI response didn't match required days, using fallback method")
                return self._simple_day_organization(filtered_pois, preferences)

            for day_pois in organized_days:
                if len(day_pois) != preferences.realization_of_pois_per_day:
                    print("Warning: AI response didn't match required activities per day, using fallback method")
                    return self._simple_day_organization(filtered_pois, preferences)

            return organized_days

        except Exception as e:
            print(f"Error organizing days: {str(e)}")
            return self._simple_day_organization(filtered_pois, preferences)

    def _simple_day_organization(self, pois: List[Dict], preferences: UserPreferences) -> List[List[Dict]]:

        # Sort POIs by how well they match user interests
        def interest_score(poi):
            poi_tags = poi['Tags'].lower().split(',')
            poi_tags = [tag.strip() for tag in poi_tags]
            return sum(1 for interest in preferences.interests
                       if any(interest.lower() in tag for tag in poi_tags))

        sorted_pois = sorted(pois, key=interest_score, reverse=True)

        # Calculate total needed POIs
        total_needed = preferences.trip_duration * preferences.realization_of_pois_per_day

        # Take only needed number of POIs
        selected_pois = sorted_pois[:total_needed]

        # Organize into days
        organized_days = []
        for i in range(0, total_needed, preferences.realization_of_pois_per_day):
            day_pois = selected_pois[i:i + preferences.realization_of_pois_per_day]
            if day_pois:  # Only add non-empty days
                organized_days.append(day_pois)

        return organized_days

    def _parse_organized_days(self, organized_text: str, pois: List[Dict]) -> List[List[Dict]]:

        # Parse AI response into organized days
        organized_days = []
        current_day = []

        # Parsing based on "Day X" markers
        for line in organized_text.split('\n'):
            line = line.strip()
            if not line:
                continue

            if line.lower().startswith('day '):
                if current_day:
                    organized_days.append(current_day)
                current_day = []
            else:
                # Match POI names from the line to our POI list
                for poi in pois:
                    if poi['Name'].lower() in line.lower():
                        current_day.append(poi)
                        break

        if current_day:
            organized_days.append(current_day)

        return organized_days

    def _simple_day_organization(self, pois: List[Dict], num_days: int) -> List[List[Dict]]:

        # Organize POIs into days
        organized_days = []
        pois_per_day = len(pois) // num_days + (1 if len(pois) % num_days else 0)

        for i in range(0, len(pois), pois_per_day):
            day_pois = pois[i:i + pois_per_day]
            organized_days.append(day_pois)

        return organized_days

    def _create_day_plan(self, day_number: int, pois: List[Dict], preferences: UserPreferences) -> Dict:

        # Create a detailed plan for a single day
        day_summary = self.description_generator.generate_day_summary(pois)

        activities = []
        start_time = datetime.strptime(preferences.preferred_start_time, "%H:%M")

        for poi in pois:

            # Generate description
            description = self.description_generator.generate_poi_description(poi)

            # Calculate timing
            visit_duration = 120  # default 2 hours in minutes
            end_time = start_time + timedelta(minutes=visit_duration)

            activity = {
                "name": poi["Name"],
                "location": f"{poi.get('AddressLocality', '')}, {poi['AddressRegion']}",
                "description": description,
                "timing": f"{start_time.strftime('%H:%M')} - {end_time.strftime('%H:%M')}"
            }
            activities.append(activity)

            # Update start time for next activity
            start_time = end_time + timedelta(minutes=30)  # 30 min break between activities

        return {
            "day_number": day_number,
            "day_summary": day_summary,
            "activities": activities
        }

    def _generate_trip_summary(self, organized_days: List[List[Dict]], preferences: UserPreferences) -> str:

        # Overall summary of the trip using AI
        total_pois = sum(len(day) for day in organized_days)
        regions = set()
        categories = set()

        for day in organized_days:
            for poi in day:
                regions.add(poi['AddressRegion'])
                if 'Tags' in poi:
                    categories.update(tag.strip() for tag in poi['Tags'].split(','))

        prompt = f"""
        Create a brief summary of a {preferences.trip_duration}-day trip to Ireland covering:
        - {total_pois} points of interest
        - Regions: {', '.join(regions)}
        - Categories: {', '.join(categories)}
        - Transportation: {preferences.preferred_transportation}
        - Pace: {preferences.preferred_pace}

        Include highlights and what makes this itinerary special.
        """

        try:
            response = self.client.chat.completions.create(
                model=GPT_MODEL,
                messages=[
                    {"role": "system", "content": "You are a travel expert creating engaging trip summaries."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=MAX_TOKENS,
                temperature=TEMPERATURE
            )

            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error generating trip summary: {str(e)}")
            return "Trip summary unavailable"

