#!/usr/bin/env python3
"""
get_recipe_info.py
Project 2 CSEN100 - Python (ASDRP Summer 2020)

Usage examples:
  python get_recipe_info.py
  python get_recipe_info.py --topics "christmas" "fruitcake" "meatloaf" "new year's" "pie"
  python get_recipe_info.py --limit 30

Before running:
  1) pip install praw requests
  2) Create a Reddit app and set the following environment variables (recommended):
       REDDIT_CLIENT_ID
       REDDIT_CLIENT_SECRET
       REDDIT_USER_AGENT
     (Do NOT hardcode credentials before submitting.)
"""

import os
import re
import argparse
import requests
from urllib.parse import urlparse
import mimetypes
import time

import praw

# -------------------------
# Helper functions
# -------------------------
def reddit_instance_from_env():
    """Create a praw.Reddit instance using environment variables."""
    client_id = os.environ.get("REDDIT_CLIENT_ID")
    client_secret = os.environ.get("REDDIT_CLIENT_SECRET")
    user_agent = os.environ.get("REDDIT_USER_AGENT", "get_recipe_info_script/0.1 by u/yourusername")

    if not client_id or not client_secret:
        raise RuntimeError("Please set REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET in your environment.")

    return praw.Reddit(client_id=client_id,
                       client_secret=client_secret,
                       user_agent=user_agent)


def sanitize_filename(name):
    """Return a filename-safe version of `name`."""
    name = name.strip().replace(" ", "_")
    # remove chars that are unsafe for filenames (basic)
    return re.sub(r'[^A-Za-z0-9_\-\.]', '', name)


def ext_from_url_or_content(url, resp):
    """Try to determine a file extension from URL or HTTP response headers."""
    # Try to get from URL path
    path = urlparse(url).path
    ext = os.path.splitext(path)[1]
    if ext and len(ext) <= 5:
        return ext
    # fallback to content-type
    ctype = resp.headers.get("Content-Type", "")
    return mimetypes.guess_extension(ctype.split(";")[0]) or ".jpg"


def download_image(url, out_path, timeout=15):
    """Download an image from url to out_path. Returns True on success."""
    try:
        resp = requests.get(url, stream=True, timeout=timeout)
        resp.raise_for_status()
    except Exception as e:
        print(f"  [!] Failed to download image from {url}: {e}")
        return False

    ext = ext_from_url_or_content(url, resp)
    if not out_path.lower().endswith(ext):
        out_path = out_path + ext

    try:
        with open(out_path, "wb") as f:
            for chunk in resp.iter_content(1024 * 8):
                if chunk:
                    f.write(chunk)
        print(f"Saved local file: {out_path}")
        return True
    except Exception as e:
        print(f"  [!] Error saving file {out_path}: {e}")
        return False


def best_top_comment(submission):
    """
    Return the most upvoted top-level comment text, ignoring removed/deleted comments.
    If comments are collapsed, call replace_more.
    """
    try:
        submission.comments.replace_more(limit=0)
    except Exception:
        # Sometimes this can fail if Reddit limits or network hiccup; we try to continue.
        pass

    best = None
    best_score = -10**9
    for c in submission.comments:
        if getattr(c, "body", None) and c.body.strip().lower() not in ("[deleted]", "[removed]"):
            # prefer higher score, and also prefer comments that are longer (likely a recipe)
            score = getattr(c, "score", 0)
            if score > best_score or (score == best_score and len(c.body) > len(best.body) if best else False):
                best = c
                best_score = score
    return best


# -------------------------
# Core logic
# -------------------------
def find_recipe_for_topic(reddit, topic, subreddit_name="recipes", search_limit=25):
    """
    Search r/recipes for posts related to topic and return a dict with:
      - title
      - image_url (or None)
      - top_recipe_text (or None)
      - author (poster username)
      - post_url
    The function prioritizes posts with link flair 'Recipes' (case-insensitive).
    """
    sr = reddit.subreddit(subreddit_name)

    # Build a search query. We search title & selftext for the topic.
    # Use quotes for multiword topics.
    q = f'title:"{topic}" OR selftext:"{topic}" OR "{topic}"'
    # We will loop over search results and pick the best submission that has flair 'Recipes'.
    candidates = sr.search(q, sort="relevance", limit=search_limit)

    chosen = None
    for submission in candidates:
        # check link flair text if present
        flair = getattr(submission, "link_flair_text", "") or ""
        # normalize
        flair_norm = flair.lower().strip()
        # some posts use 'Recipe' or 'Recipes' or 'recipes' etc.
        if "recipe" not in flair_norm:
            # skip non-recipe flairs
            continue

        # Accept this submission; pick the one with highest score among recipe-flair results
        if chosen is None or submission.score > chosen.score:
            chosen = submission

    if not chosen:
        # fallback: accept top search result even without flair, but warn
        candidates = sr.search(q, sort="relevance", limit=search_limit)
        for submission in candidates:
            if chosen is None or submission.score > chosen.score:
                chosen = submission

    if not chosen:
        return None

    # Get image URL: many posts have submission.url pointing to image (imgur, i.redd.it, reddit preview)
    image_url = None
    url = getattr(chosen, "url", "")
    # common image hosts
    if url and re.search(r'\.(jpe?g|png|gif|bmp|webp)(?:$|\?)', url, re.IGNORECASE):
        image_url = url
    else:
        # try preview
        preview = getattr(chosen, "preview", None)
        if preview and isinstance(preview, dict):
            images = preview.get("images")
            if images and len(images) > 0:
                # use the source url
                image_url = images[0].get("source", {}).get("url")

    # try to get top recipe comment
    top_comment = best_top_comment(chosen)
    recipe_text = top_comment.body if top_comment else None

    return {
        "title": chosen.title,
        "image_url": image_url,
        "recipe_text": recipe_text,
        "author": str(chosen.author) if chosen.author else "[deleted]",
        "post_url": f"https://www.reddit.com{chosen.permalink}"
    }


def main(topics, subreddit="recipes", out_dir=".", limit=25):
    reddit = reddit_instance_from_env()

    for topic in topics:
        print("#" * 56)
        print(f"Topic : {topic}")
        try:
            result = find_recipe_for_topic(reddit, topic, subreddit_name=subreddit, search_limit=limit)
        except Exception as e:
            print(f"  [!] Error searching for topic '{topic}': {e}")
            continue

        if not result:
            print(f"  No results found for topic '{topic}'.\n")
            continue

        # Print recipe title
        print(result["title"])
        print()

        # Print recipe (from top comment) or indicate missing
        if result["recipe_text"]:
            # For readability, print a shortened first N lines if extremely long
            print(result["recipe_text"])
            print()
        else:
            print("  [!] No top comment recipe found for this post.")
            print()

        # Username
        print("Source :", result["author"])
        print("Post URL:", result["post_url"])

        # Save image if available
        if result["image_url"]:
            base_name = sanitize_filename(topic)
            out_path = os.path.join(out_dir, base_name)  # extension appended by downloader
            download_image(result["image_url"], out_path)
        else:
            print("  [!] No image URL found for this post.")

        # be polite with Reddit
        time.sleep(1.0)


# -------------------------
# Command line handling
# -------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Find recipes on r/recipes and save images.")
    parser.add_argument("--topics", nargs="+",
                        default=["christmas", "fruitcake", "meatloaf", "new year's", "pie"],
                        help="List of topics to search for.")
    parser.add_argument("--subreddit", default="recipes", help="Subreddit to search (default: recipes).")
    parser.add_argument("--outdir", default=".", help="Directory to save images.")
    parser.add_argument("--limit", type=int, default=25, help="Search limit per topic (result pool size).")

    args = parser.parse_args()
    main(args.topics, subreddit=args.subreddit, out_dir=args.outdir, limit=args.limit)
