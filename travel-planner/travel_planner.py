from typing import Dict, List
from datetime import datetime, timedelta
from poi_description_generator import POIDescriptionGenerator
from user_preferences import UserPreferences
from text_generator import TextGenerator


class TravelPlanner:
    def __init__(self, text_generator: TextGenerator):
        self.description_generator = POIDescriptionGenerator(text_generator)

    def _calculate_interests_accuracy(self, organized_days: List[List[Dict]], interests: List[str]) -> dict:
        interest_matches = {interest: 0 for interest in interests}
        total_pois = 0

        for day in organized_days:
            for poi in day:
                total_pois += 1
                poi_tags = poi['Tags'].lower().split(',')
                poi_tags = [tag.strip() for tag in poi_tags]
                for interest in interests:
                    if any(interest.lower() in tag for tag in poi_tags):
                        interest_matches[interest] += 1

        accuracy_per_interest = {}
        for interest, matches in interest_matches.items():
            percentage = (matches / total_pois * 100) if total_pois > 0 else 0
            accuracy_per_interest[interest] = round(percentage, 2)

        total_matches = sum(interest_matches.values())
        max_possible_matches = total_pois * len(interests)
        overall_accuracy = (total_matches / max_possible_matches * 100) if max_possible_matches > 0 else 0

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
        all_pois = []
        for region_pois in poi_data["by_region"].values():
            all_pois.extend(region_pois)

        organized_days = self._organize_days(all_pois, preferences)
        interests_accuracy = self._calculate_interests_accuracy(organized_days, preferences.interests)

        plan = {
            "trip_summary": self._generate_trip_summary(organized_days, preferences),
            "days": [],
            "general_tips": self.description_generator.generate_itinerary_tips(
                preferences.to_dict(), all_pois
            ),
            "interests_accuracy": interests_accuracy
        }

        for day_number, day_pois in enumerate(organized_days, 1):
            day_plan = self._create_day_plan(day_number, day_pois, preferences)
            plan["days"].append(day_plan)

        return plan

    def _organize_days(self, pois: List[Dict], preferences: UserPreferences) -> List[List[Dict]]:
        filtered_pois = []
        for poi in pois:
            poi_tags = poi['Tags'].lower().split(',')
            poi_tags = [tag.strip() for tag in poi_tags]
            if any(interest.lower() in tag for interest in preferences.interests for tag in poi_tags):
                filtered_pois.append(poi)

        needed = preferences.trip_duration * preferences.realization_of_pois_per_day
        if len(filtered_pois) < needed:
            filtered_pois = pois

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

        user_prompt = f"""
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
        system_prompt = (
            "You are a travel planning assistant that creates precise itineraries matching user requirements exactly."
        )

        plan_text = self.description_generator.text_generator.generate_chat_completion(
            system_prompt, user_prompt
        )
        organized_days = self._parse_organized_days(plan_text, filtered_pois, preferences)
        return organized_days

    def _parse_organized_days(self, organized_text: str, pois: List[Dict], preferences: UserPreferences) -> List[
        List[Dict]]:
        organized_days = []
        current_day = []

        lines = organized_text.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
            if line.lower().startswith('day '):
                if current_day:
                    organized_days.append(current_day)
                current_day = []
            else:
                matched_poi = None
                for poi in pois:
                    if poi['Name'].lower() in line.lower():
                        matched_poi = poi
                        break
                if matched_poi:
                    current_day.append(matched_poi)

        if current_day:
            organized_days.append(current_day)

        if len(organized_days) != preferences.trip_duration:
            print("Warning: AI response didn't match required day count. Using fallback method.")
            return self._simple_day_organization(pois, preferences)

        for day_pois in organized_days:
            if len(day_pois) != preferences.realization_of_pois_per_day:
                print("Warning: AI response didn't match required activities per day. Using fallback method.")
                return self._simple_day_organization(pois, preferences)

        return organized_days

    def _simple_day_organization(self, pois: List[Dict], preferences: UserPreferences) -> List[List[Dict]]:
        def interest_score(poi):
            poi_tags = poi['Tags'].lower().split(',')
            poi_tags = [tag.strip() for tag in poi_tags]
            return sum(1 for interest in preferences.interests if any(interest.lower() in tg for tg in poi_tags))

        sorted_pois = sorted(pois, key=interest_score, reverse=True)
        total_needed = preferences.trip_duration * preferences.realization_of_pois_per_day
        selected_pois = sorted_pois[:total_needed]

        organized_days = []
        for i in range(0, len(selected_pois), preferences.realization_of_pois_per_day):
            day_pois = selected_pois[i:i + preferences.realization_of_pois_per_day]
            if day_pois:
                organized_days.append(day_pois)

        return organized_days

    def _create_day_plan(self, day_number: int, pois: List[Dict], preferences: UserPreferences) -> Dict:
        day_summary = self.description_generator.generate_day_summary(pois)
        activities = []
        start_time = datetime.strptime(preferences.preferred_start_time, "%H:%M")

        for poi in pois:
            description = self.description_generator.generate_poi_description(poi)
            visit_duration = 120
            end_time = start_time + timedelta(minutes=visit_duration)

            activity = {
                "name": poi["Name"],
                "location": f"{poi.get('AddressLocality', '')}, {poi['AddressRegion']}",
                "description": description,
                "timing": f"{start_time.strftime('%H:%M')} - {end_time.strftime('%H:%M')}"
            }
            activities.append(activity)
            start_time = end_time + timedelta(minutes=30)

        return {
            "day_number": day_number,
            "day_summary": day_summary,
            "activities": activities
        }

    def _generate_trip_summary(self, organized_days: List[List[Dict]], preferences: UserPreferences) -> str:
        total_pois = sum(len(day) for day in organized_days)
        regions = set()
        categories = set()

        for day in organized_days:
            for poi in day:
                regions.add(poi['AddressRegion'])
                if 'Tags' in poi:
                    categories.update(tag.strip() for tag in poi['Tags'].split(','))

        system_prompt = "You are a travel expert creating engaging trip summaries."
        user_prompt = f"""
        Create a brief summary of a {preferences.trip_duration}-day trip to Ireland covering:
        - {total_pois} points of interest
        - Regions: {', '.join(regions)}
        - Categories: {', '.join(categories)}
        - Transportation: {preferences.preferred_transportation}
        - Pace: {preferences.preferred_pace}

        Include highlights and what makes this itinerary special.
        """

        try:
            return self.description_generator.text_generator.generate_chat_completion(system_prompt, user_prompt)
        except Exception as e:
            print(f"Error generating trip summary: {str(e)}")
            return "Trip summary unavailable"
