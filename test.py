from generators.text_gen import PostGenerator
from generators.image_gen import ImageGenerator
from social_publishers.vk_publisher import VKPublisher
from config import OPENAI_API_KEY, VK_API_KEY, VK_GROUP_ID

post_gen = PostGenerator(OPENAI_API_KEY, tone="позитивный и весёлый",
                         topic="Наш новый гарнитур для гостиной: уютный уголок,"
                               " где каждый вечер оживает теплом семейных историй.")
content = post_gen.generate_post()
img_desc = post_gen.generate_post_image_description()

img_gen = ImageGenerator(OPENAI_API_KEY)
image_url = img_gen.generate_image(img_desc)

vk_pub = VKPublisher(VK_API_KEY, VK_GROUP_ID, debug=True)
vk_pub.publish_post(content, image_url)

print(content)
print(image_url)
