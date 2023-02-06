# Test the API functions in the function module
import io

import fastapi
import fastapi.testclient
import PIL
import numpy

from function import app

client = fastapi.testclient.TestClient(app)

def assert_image_equal(image1, image2):
    assert image1.size == image2.size
    assert image1.mode == image2.mode
    assert image1.tobytes() == image2.tobytes()

def test_generate_map():
    response = client.get("/generate_map?center=40.714728,-73.998672&zoom=12&width=400&height=400&tile_provider=osm")
    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"
    assert response.content != None
    generated_image = PIL.Image.open(io.BytesIO(response.content))
    baseline_image = PIL.Image.open('tests/staticmap_example.png')
    assert_image_equal(generated_image, baseline_image)