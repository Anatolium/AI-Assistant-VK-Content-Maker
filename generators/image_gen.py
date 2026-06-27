from openai import OpenAI

class ImageGenerator:
    def __init__(self, openai_key, base_url):
        self.client = OpenAI(api_key=openai_key, base_url=base_url)

    def generate_image(self, prompt):
        response = self.client.images.generate(
          model="dall-e-3",
          prompt=prompt,
          size="1024x1024",
          quality="standard",
          n=1,
        )

        image_url = response.data[0].url
        return image_url
