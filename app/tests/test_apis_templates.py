import json

import pytest


def describe_list():
    def describe_GET():
        @pytest.mark.slow
        def it_returns_all_templates(expect, client):
            request, response = client.get("/templates")
            expect(response.status) == 200


def describe_detail():
    def describe_GET():
        def it_includes_metadata(expect, client):
            request, response = client.get("/templates/iw")
            expect(response.status) == 200
            expect(response.json) == {
                "name": "Insanity Wolf",
                "key": "iw",
                "lines": 2,
                "styles": [],
                "blank": "http://localhost:5000/images/iw.png",
                "example": "http://localhost:5000/images/iw/does_testing/in_production.png",
                "source": "http://knowyourmeme.com/memes/insanity-wolf",
                "_self": "http://localhost:5000/templates/iw",
            }

        def it_shortens_example_when_no_text(expect, client):
            request, response = client.get("/templates/mmm")
            expect(response.status) == 200
            expect(response.json["example"]) == "http://localhost:5000/images/mmm.png"

        def it_returns_404_when_missing(expect, client):
            request, response = client.get("/templates/foobar")
            expect(response.status) == 404

    def describe_POST():
        @pytest.mark.parametrize("as_json", [True, False])
        def it_returns_an_image_url(expect, client, as_json):
            data = {"text_lines[]": ["foo", "bar"], "extension": "jpg"}
            request, response = client.post(
                "/templates/iw", data=json.dumps(data) if as_json else data
            )
            expect(response.status) == 201
            expect(response.json) == {
                "url": "http://localhost:5000/images/iw/foo/bar.jpg"
            }

        @pytest.mark.parametrize("as_json", [True, False])
        def it_supports_custom_backgrounds(expect, client, as_json):
            data = {
                "image_url": "https://www.gstatic.com/webp/gallery/3.png",
                "text_lines[]": ["foo", "bar"],
                "extension": "jpg",
            }
            request, response = client.post(
                "/templates/custom", data=json.dumps(data) if as_json else data
            )
            expect(response.status) == 201
            expect(response.json) == {
                "url": "http://localhost:5000/images/custom/foo/bar.jpg"
                "?background=https://www.gstatic.com/webp/gallery/3.png"
            }

        @pytest.mark.parametrize("key", ["fry", "custom"])
        def it_redirects_if_requested(expect, client, key):
            data = {"text_lines": ["abc"], "redirect": True}
            request, response = client.post(
                f"/templates/{key}", data=data, allow_redirects=False
            )
            redirect = f"http://localhost:5000/images/{key}/abc.png"
            expect(response.status) == 302
            expect(response.headers["Location"]) == redirect
