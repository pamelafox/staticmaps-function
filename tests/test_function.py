# Test the API functions in the function module
import io
import math

import fastapi
import fastapi.testclient
import PIL

from function import fastapi_app


def assert_image_equal(image1, image2):
    assert image1.size == image2.size
    assert image1.mode == image2.mode
    # Based on https://stackoverflow.com/a/55251080/1347623
    diff = PIL.ImageChops.difference(image1, image2).histogram()
    sq = (value * (i % 256) ** 2 for i, value in enumerate(diff))
    rms = math.sqrt(sum(sq) / float(image1.size[0] * image1.size[1]))
    assert rms < 90


def test_generate_map():
    client = fastapi.testclient.TestClient(fastapi_app)
    response = client.get("/generate_map?center=40.714728,-73.998672&zoom=12&width=400&height=400&tile_provider=osm")
    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"
    assert response.content is not None
    generated_image = PIL.Image.open(io.BytesIO(response.content))
    baseline_image = PIL.Image.open("tests/staticmap_example.png")
    assert_image_equal(generated_image, baseline_image)
