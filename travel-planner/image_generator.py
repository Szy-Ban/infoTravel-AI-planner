import os
import requests

class ImageGenerator:
    def __init__(self, api_key: str):
        self.api_key = api_key

    def generate_trip_image(self, trip_summary: str, interests: list) -> str:
        # interests into a comma-separated string
        interests_text = ", ".join(interests)

        original_prompt = (
            f"Create a thumbnail for a trip to Ireland, based on user preferences and a trip summary. "
            f"Do not generate any text in the image. You don't need to visualize all points of interest; "
            f"instead pick a general theme. The image is supposed to advertise the trip to the user, "
            f"convincing them it's tailored to their preferences.\n\n"
            f"User preferences: {interests_text}\n"
            f"The trip summary is: {trip_summary}."
        )

        # 1000-char limit for prompts
        MAX_PROMPT_LENGTH = 1000
        if len(original_prompt) > MAX_PROMPT_LENGTH:
            truncated_prompt = original_prompt[:MAX_PROMPT_LENGTH]
        else:
            truncated_prompt = original_prompt

        endpoint = "https://api.openai.com/v1/images/generations"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "prompt": truncated_prompt,
            "n": 1,
            "size": "1024x1024",
            "model": "dall-e-3",
        }

        try:
            response = requests.post(endpoint, headers=headers, json=data, timeout=60)
            response.raise_for_status()
            response_json = response.json()
            return response_json["data"][0]["url"]
        except requests.HTTPError as http_err:
            print(f"Error generating image: {http_err}")
            print("Response content:", response.text)
            return None
        except Exception as e:
            print(f"Error generating image: {str(e)}")
            return None

    def save_image_from_url(self, image_url: str, filename: str = "travel_poster.png") -> None:
        output_directory = "./output"
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)

        file_path = os.path.join(output_directory, filename)

        try:
            print(f"Downloading image from {image_url}...")
            response = requests.get(image_url, timeout=60)
            if response.status_code == 200:
                with open(file_path, 'wb') as f:
                    f.write(response.content)
                print(f"Image saved as {file_path}")
            else:
                print(f"Failed to download image. HTTP status code: {response.status_code}")
        except Exception as e:
            print(f"Error saving image: {str(e)}")