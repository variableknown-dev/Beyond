import os

from ollama import chat


VISION_MODEL = "gemma3:4b"


def analyze_image(image_path, prompt="Describe this image in detail."):
    """
    Sends an image to the vision model and returns its response.
    """

    image_path = os.path.expanduser(image_path.strip())

    if not os.path.isfile(image_path):
        return False, f"I couldn't find the image:\n{image_path}"

    try:

        response = chat(
            model=VISION_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                    "images": [image_path],
                }
            ],
        )

        result = response["message"]["content"].strip()

        return True, result

    except Exception as e:

        return False, f"Vision error: {e}"
