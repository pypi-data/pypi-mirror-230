
# Video Images Creator

This package creates a video with animation for a set of Images urls(feature screens) along with there titles.




## Steps to generate your first video

#### Step 1:

Install the package using pip: 

pip install video_images_creator


#### Step 2

Create a python file Myfile.py with below code 

```
from video_images_creator import video_creator

feature_names = ["Splash Screen", "Search"] 
image_urls = ["https://buildernowassets.azureedge.net/builder-now-beta/uploads/staging/feature_figma/image/485/b478c7bd-84f8-48f2-81c7-3b9a5dbe7960.png", "https://buildernowassets.azureedge.net/builder-now-beta/uploads/staging/feature_figma/image/485/b478c7bd-84f8-48f2-81c7-3b9a5dbe7960.png"]

video_creator.build(image_urls, feature_names)
```

#You can customize the images and feature names

#### Step 3

Run your Python script to create the video inside the 'outputs' folder