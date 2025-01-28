from openai import OpenAI

class ImageGenerator:
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)

    def generate_trip_image(self, trip_summary: str) -> str:

        # generate image prompt
        prompt = f"Create a stunning and vibrant thumbnail for a trip to Ireland, based on a trip summary. You don't need to visualize all points of interest, instead try to pick up a general theme. \n The trip summary is: {trip_summary}."

        try:
            response = self.client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size="1024x1024",
                quality="standard",
                n=1
            )

            # return URL for gen. image
            return response.data[0].url
        except Exception as e:
            print(f"Error generating image: {str(e)}")
            return None

    def save_image_from_url(self, image_url: str, filename: str = "travel_poster.png") -> None:

        # Download and save the image
        import requests
        try:
            print(f"Downloading image from {image_url}...")
            response = requests.get(image_url)
            if response.status_code == 200:
                with open(filename, 'wb') as f:
                    f.write(response.content)
                print(f"Image saved as {filename}")
            else:
                print(f"Failed to download image. HTTP status code: {response.status_code}")
        except Exception as e:
            print(f"Error saving image: {str(e)}")