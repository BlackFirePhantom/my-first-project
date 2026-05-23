from flask import Flask, url_for
app = Flask(__name__)

@app.route("/test/<path:url>")
def test_path(url):
    return {"url": url}

if __name__ == "__main__":
    with app.test_client() as client:
        # Test double slash url
        resp = client.get("/test/https://www.google.com")
        print("Response json:", resp.get_json())
