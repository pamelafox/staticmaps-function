import time

from locust import HttpUser, task


class HelloWorldUser(HttpUser):
    @task
    def hello_world(self):
        for lat in range(5):
            for lng in range(5):
                for zoom in range(5, 10):
                    self.client.get(
                        f"/generate_map?center=40.{lat}%2C-73.{lng}&zoom={zoom}&width=400&height=400&tile_provider=osm"
                    )
                    time.sleep(0.1)
