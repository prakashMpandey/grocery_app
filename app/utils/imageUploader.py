import cloudinary
import cloudinary.uploader
import cloudinary.api
from cloudinary import CloudinaryImage
from cloudinary import CloudinaryVideo
from dotenv import load_dotenv
import os
load_dotenv()


cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD"),
    api_key=os.getenv("CLOUDINARY_API_SECRET"),
    api_secret=os.getenv("CLOUDINARY_API_KEY")
)


def image_uploader(file):
    try:
        upload_result=cloudinary.uploader.upload(file,folder="grocery",resource_type="image")
        print(f"uplaod : {upload_result}")
        return {
            "url":upload_result["secure_url"]
        }
    
    except Exception as e:
        raise Exception(f"upload faiked :{e}")
