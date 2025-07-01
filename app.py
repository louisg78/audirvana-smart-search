from flask import Flask, request, render_template
from search_engine import search

app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():
    q = request.args.get("q", "")
    results = search(q) if q else []
    return render_template("search.html", results=results, query=q)

if __name__ == "__main__":
    app.run(debug=True)

