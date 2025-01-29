import os
import json
from config import OPENAI_API_KEY, POI_DATA_FILE
from travel_planner import TravelPlanner
from poi_manager import POIManager
from user_preferences import UserPreferences
from image_generator import ImageGenerator
from text_generator import TextGenerator

def get_openai_api_key():
    api_key = OPENAI_API_KEY
    if not api_key:
        print("\nOpenAI API key not found in environment variables.")
        api_key = input("Please enter your OpenAI API key: ").strip()
        os.environ["OPENAI_API_KEY"] = api_key
    return api_key

def get_user_input():
    print("\n=== Ireland Travel Planner ===\n")

    AVAILABLE_TAGS = [
        "Walking", "Forest Park", "Park and Forest Walk", "National Park",
        "National and Forest Park", "Public Park", "Nature and Wildlife",
        "Natural Landscape", "Castle", "Historic Houses and Castle",
        "Ruins", "Museums and Attraction", "Learning", "Movies",
        "Cinema", "Venue", "Activity Operator", "Art Gallery",
        "Music", "Literary Ireland", "Church Abbey", "Monastery",
        "Churches", "Abbeys and Monastery", "Public Sculpture",
        "Bird Watching", "Photography", "Transport", "Coach",
        "Road", "Food and Drink", "Restaurant", "Food Shops",
        "Shopping", "Gardens", "Garden", "Craft", "Tracing Your Ancestors",
        "Embarkation Point", "Island", "Offshore Island", "Boat",
        "Tour", "Gaa", "Stadium", "Sports Venue", "Sports Venues",
        "Zoos and Aquarium", "Swimming", "Swimming Pools and Water Park",
        "Beach", "Fishing", "Angling", "Horse Riding", "Equestrian",
        "Kayaking", "Cruising", "Visitor Farm", "Agriculture",
        "Traditionally Irish", "Discovery Point", "River"
    ]

    print("Available interests (enter numbers separated by commas):")
    for i, tag in enumerate(AVAILABLE_TAGS, 1):
        print(f"{i:2d}. {tag}")
        if i % 3 == 0:
            print()

    # interests by index or range
    while True:
        try:
            interests_input = input("\nEnter numbers of your interests (e.g., 1,5,10 or 1-5): ").strip()
            selected_indices = set()

            for part in interests_input.split(','):
                part = part.strip()
                if '-' in part:
                    start, end = map(int, part.split('-'))
                    if 1 <= start <= len(AVAILABLE_TAGS) and 1 <= end <= len(AVAILABLE_TAGS):
                        selected_indices.update(range(start - 1, end))
                    else:
                        raise ValueError("Numbers out of range")
                else:
                    index = int(part) - 1
                    if 0 <= index < len(AVAILABLE_TAGS):
                        selected_indices.add(index)
                    else:
                        raise ValueError("Number out of range")

            selected_interests = [AVAILABLE_TAGS[i] for i in selected_indices]

            if not selected_interests:
                print("Please select at least one interest")
                continue

            print("\nSelected interests:")
            for interest in selected_interests:
                print(f"- {interest}")

            confirm = input("\nConfirm these selections? (y/n): ").lower()
            if confirm == 'y':
                break

        except (ValueError, IndexError):
            print("Please enter valid numbers separated by commas or ranges (e.g., 1,5,10 or 1-5)")

    # trip duration
    while True:
        try:
            duration = int(input("\nEnter trip duration (days, 1-14): "))
            if 1 <= duration <= 14:
                break
            print("Please enter a number between 1 and 14.")
        except ValueError:
            print("Please enter a valid number.")

    # activities per day
    while True:
        try:
            activities = int(input("Enter preferred number of activities per day (1-5): "))
            if 1 <= activities <= 5:
                break
            print("Please enter a number between 1 and 5.")
        except ValueError:
            print("Please enter a valid number.")

    # user-chosen regions (optional)
    print("\nAvailable regions in Ireland:")
    print("Dublin, Kerry, Galway, Cork, Clare, Donegal, Wicklow")
    regions = input("Enter preferred regions (comma-separated, or press Enter for all): ")
    regions = [r.strip() for r in regions.split(',')] if regions else []

    # pace
    while True:
        pace = input("\nPreferred pace (slow/moderate/fast): ").lower()
        if pace in ['slow', 'moderate', 'fast']:
            break
        print("Please enter 'slow', 'moderate', or 'fast'.")

    # transportation method
    while True:
        transport = input("Preferred transportation (car/public/walking): ").lower()
        if transport in ['car', 'public', 'walking']:
            break
        print("Please enter 'car', 'public', or 'walking'.")

    # budget
    while True:
        budget = input("Budget level (low/moderate/high): ").lower()
        if budget in ['low', 'moderate', 'high']:
            break
        print("Please enter 'low', 'moderate', or 'high'.")

    # UserPreferences object with all user inputs
    return UserPreferences(
        interests=selected_interests,
        trip_duration=duration,
        realization_of_pois_per_day=activities,
        preferred_pace=pace,
        regions=regions,
        preferred_transportation=transport,
        budget_level=budget
    )

def display_travel_plan(plan, image_url=None):
    print("\n" + "=" * 50)
    print("YOUR IRELAND TRAVEL PLAN")
    print("=" * 50 + "\n")

    print("Trip Summary:")
    print("-" * 20)
    print(plan['trip_summary'])

    if image_url:
        print("\nGenerated Travel Poster:")
        print(image_url)

    print("\n" + "=" * 50 + "\n")
    print("Interests Analysis:")
    print("-" * 20)
    print(f"Overall accuracy: {plan['interests_accuracy']['overall_accuracy']}%")

    usage = plan['interests_accuracy']['interests_usage']
    print(
        f"\nInterests usage: {usage['used']}/{usage['total']} "
        f"({usage['percentage']}%)"
    )

    print("\nAccuracy per interest:")
    for interest, accuracy in plan['interests_accuracy']['accuracy_per_interest'].items():
        print(f"- {interest}: {accuracy}%")
    print(f"\nTotal POIs in plan: {plan['interests_accuracy']['total_pois']}")
    print(f"Total interest matches found: {plan['interests_accuracy']['matches_found']}")
    print("\n" + "=" * 50 + "\n")

    for day in plan['days']:
        print(f"Day {day['day_number']}:")
        print("-" * 20)
        print(f"Summary: {day['day_summary']}\n")

        for idx, activity in enumerate(day['activities'], 1):
            print(f"{idx}. {activity['name']}")
            print(f"   Location: {activity['location']}")
            print(f"   Description: {activity['description']}")
            if 'timing' in activity:
                print(f"   Suggested timing: {activity['timing']}")
            print()
        print("-" * 50)

    print("\nGeneral Tips for Your Trip:")
    print("-" * 20)
    print(plan['general_tips'])
    print("\n" + "=" * 50)

def save_plan_to_file(plan, filename="travel_plan.json"):
    directory = "./output"
    if not os.path.exists(directory):
        os.makedirs(directory)

    file_path = os.path.join(directory, filename)
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(plan, f, indent=2, ensure_ascii=False)
    print(f"\nPlan saved to {file_path}")

def main():
    try:
        api_key = get_openai_api_key()
        if not api_key:
            print("Warning: no OpenAI API key provided. Might fail with image generation.")

        # text generator
        text_generator = TextGenerator()
        # Create TravelPlanner
        planner = TravelPlanner(text_generator)
        # Create POIManager
        poi_manager = POIManager()
        # Create ImageGenerator
        image_generator = ImageGenerator(api_key)

        # Gather user preferences
        preferences = get_user_input()

        print("\nLoading and filtering points of interest...")
        poi_dict = poi_manager.load_and_filter_pois(POI_DATA_FILE, preferences)

        print("Generating your travel plan...")
        plan = planner.generate_travel_plan(poi_dict, preferences)

        # print("Generating thumbnail...")
        # image_url = image_generator.generate_trip_image(plan['trip_summary'], preferences.interests)
        # if image_url:
        #     print(f"Generated image URL: {image_url}")
        #     save_image = input("Do you want to save this image? (y/n): ").lower()
        #     if save_image == 'y':
        #         filename = "travel_poster.png"
        #         image_generator.save_image_from_url(image_url, filename)
        # else:
        #     print("Failed to generate trip image.")

        # display_travel_plan(plan, image_url)
        display_travel_plan(plan)
        save_plan_to_file(plan)

    except Exception as e:
        print(f"\nError: {str(e)}")

if __name__ == "__main__":
    main()
