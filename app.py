from flask import Flask, render_template

app = Flask(__name__)
app.config["SECRET_KEY"] = "dev-secret-change-before-submission"


@app.route("/")
def index():
    """Serve the Featherfield Preserve game page."""
    return render_template("index.html")


@app.route("/health")
def health():
    """Simple route used by tests to confirm the server is running."""
    return {"status": "ok"}


if __name__ == "__main__":
    app.run(debug=True)
