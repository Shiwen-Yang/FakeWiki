from flask import Flask, redirect, render_template, request, url_for

from Engine import Engine

app = Flask(__name__)
engine = Engine()


@app.route("/")
def index():
    return render_template("index.html", topics=engine.get_homepage_topics())


@app.route("/search")
def search():
    query = (request.args.get("query") or "").strip()
    if not query:
        return render_template(
            "index.html",
            topics=engine.get_homepage_topics(),
            error="Enter a term to generate a page.",
        )

    page = engine.get_or_create_page(query)
    return redirect(url_for("view_page", slug=page.slug))


@app.route("/page/<slug>")
def view_page(slug: str):
    page = engine.get_page(slug)
    if page is None:
        page = engine.get_or_create_page(slug.replace("-", " "))

    link_targets = [
        {"title": term, "slug": engine.resolve_link(term)} for term in page.links
    ]
    return render_template("page.html", page=page, link_targets=link_targets)


if __name__ == "__main__":
    app.run(debug=True)
