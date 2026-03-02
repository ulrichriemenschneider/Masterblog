import json
from pathlib import Path

from flask import Flask, redirect, render_template, request, url_for

app = Flask(__name__)
POSTS_FILE = Path(__file__).parent / "posts.json"


def load_posts():
    if not POSTS_FILE.exists():
        return []
    try:
        with POSTS_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)
    except (json.JSONDecodeError, OSError):
        return []
    return data if isinstance(data, list) else []


def save_posts(posts):
    with POSTS_FILE.open("w", encoding="utf-8") as file:
        json.dump(posts, file, ensure_ascii=False, indent=2)


def get_next_id(posts):
    if not posts:
        return 1
    return max(post.get("id", 0) for post in posts) + 1


def find_post(posts, post_id):
    for post in posts:
        if post.get("id") == post_id:
            return post
    return None


@app.route("/")
def index():
    posts = load_posts()
    return render_template("index.html", posts=posts)


@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        posts = load_posts()
        new_post = {
            "id": get_next_id(posts),
            "author": request.form.get("author", ""),
            "title": request.form.get("title", ""),
            "content": request.form.get("content", ""),
        }
        posts.append(new_post)
        save_posts(posts)
        return redirect(url_for("index"))
    return render_template("add.html")


@app.route("/delete/<int:post_id>")
def delete(post_id):
    posts = load_posts()
    updated_posts = [post for post in posts if post.get("id") != post_id]
    if len(updated_posts) != len(posts):
        save_posts(updated_posts)
    return redirect(url_for("index"))


@app.route("/update/<int:post_id>", methods=["GET", "POST"])
def update(post_id):
    posts = load_posts()
    post = find_post(posts, post_id)
    if post is None:
        return "Post not found", 404

    if request.method == "POST":
        post["author"] = request.form.get("author", "")
        post["title"] = request.form.get("title", "")
        post["content"] = request.form.get("content", "")
        save_posts(posts)
        return redirect(url_for("index"))

    return render_template("update.html", post=post)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=True)
