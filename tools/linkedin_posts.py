#!/usr/bin/env python3
"""LinkedIn posts to surface on the homepage, newest first.

WHY THIS IS A HAND-KEPT LIST
----------------------------
LinkedIn publishes no public feed for a personal profile — no RSS, no open
API. A static page cannot ask "what did Vishal post lately?"; there is
nothing to ask. What LinkedIn *does* give you is a per-post embed, and the
post has to be named. So this file is the list, and build_author.py renders
whatever is in it.

TO ADD A POST
-------------
Open the post on LinkedIn -> "..." menu -> Embed this post. Or just copy the
post's own URL out of the address bar. Paste either form below. Both work:

    https://www.linkedin.com/posts/vishal-abhinav_kubernetes-activity-7312345678901234567-Ab1c
    https://www.linkedin.com/feed/update/urn:li:activity:7312345678901234567/
    https://www.linkedin.com/embed/feed/update/urn:li:share:7312345678901234567

Only the 19-digit id matters; the builder pulls it out and drops the rest.
Newest first — the first three are the ones that render by default.

An empty list is a valid state: the column falls back to the profile card
and a follow CTA, so the page never ships a hole.
"""

# Public profile the column links to.
PROFILE = "https://www.linkedin.com/in/vishal-abhinav/"

# Post URLs, newest first. Add as you publish.
POSTS = [
    # "https://www.linkedin.com/feed/update/urn:li:activity:0000000000000000000/",
]

# How many of POSTS to embed. Each embed is an iframe, so keep it small.
SHOW = 3
