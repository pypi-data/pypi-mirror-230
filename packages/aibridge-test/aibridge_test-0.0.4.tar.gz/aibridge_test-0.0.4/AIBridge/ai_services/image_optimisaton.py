from PIL import Image
import requests
from urllib.parse import urlparse
from AIBridge.exceptions import ImageException, AIBridgeException
from io import BytesIO


class ImageOptimise:
    @classmethod
    def get_image(self, image_data):
        image_obj = []
        try:
            for index, image in enumerate(image_data):
                result = urlparse(image)
                if all([result.scheme, result.netloc]):
                    response = requests.get(image)
                    if response.status_code == 200:
                        image_data = BytesIO(response.content)
                        image = Image.open(image_data)
                else:
                    with open(image, "rb") as image_file:
                        binary_data = image_file.read()
                    image_buffer = BytesIO(binary_data)
                    image = Image.open(image_buffer)
                if image.mode != "RGBA":
                    image = image.convert("RGBA")
                print(image.mode)
                image_obj.append(image)
            return image_obj
        except AIBridgeException as e:
            raise ImageException(f"Error in reading the the image {e}")

    @classmethod
    def get_bytes_io(self, image_data):
        image_obj = []
        for image in image_data:
            buf = BytesIO()
            image.save(buf, save_all=True, format="PNG", quality=100)
            bytes_im = buf.getvalue()
            buf.close()
            image_obj.append(bytes_im)
        return image_obj

    @classmethod
    def set_dimension(self, image_data, mask_data):
        for index, image in enumerate(image_data):
            if image.size != mask_data[index].size:
                mask = mask_data[index].resize(image.size)
                print(image.size)
                mask_data[index] = mask
                print(mask_data[index].size)
        return mask_data
