#!/usr/bin/env python3
"""LinkedIn posts to surface on the homepage, newest first.

WHY THIS IS A HAND-KEPT LIST
----------------------------
LinkedIn publishes no public feed for a personal profile. Reading a person's
posts needs the r_member_social permission, which LinkedIn documents as
"restricted and available to approved users only" — partner approval — and
even then it is an OAuth flow needing a server to hold the token. This site is
static HTML on GitHub Pages out of a public repo, so neither half is possible.
The per-post embed is public and needs nothing, so that is what this list is.

TO ADD A POST
-------------
On the post: the "…" menu -> Embed this post -> copy the whole snippet and
paste it below as a string. PASTE THE WHOLE IFRAME, not just the link — it
carries two things a bare URL does not:

  * the URN TYPE. A post is urn:li:ugcPost:, urn:li:share: or
    urn:li:activity: depending on how it was created, and guessing wrong
    renders an empty box.
  * the HEIGHT LinkedIn measured for that specific post. The embed does not
    resize itself, so this is the only way to know how tall it should be.

A bare URL still works — the parser falls back to urn:li:share: and a default
height — but the embed snippet is the reliable form.

Newest first. SHOW caps how many render.
An empty list is a valid state: the column falls back to the profile card and
a follow CTA, so the page never ships a hole.
"""

# Public profile the column links to.
PROFILE = "https://www.linkedin.com/in/vishal-abhinav/"

# Whole embed snippets, newest first.
POSTS = [
    '<iframe src="https://www.linkedin.com/embed/feed/update/urn:li:ugcPost:7503042341247750144?collapsed=1" height="567" width="504" frameborder="0" allowfullscreen="" title="Embedded post"></iframe>',
    '<iframe src="https://www.linkedin.com/embed/feed/update/urn:li:ugcPost:7464815680668786688" height="1743" width="504" frameborder="0" allowfullscreen="" title="Embedded post"></iframe>',
    '<iframe src="https://www.linkedin.com/embed/feed/update/urn:li:ugcPost:7439191723156856832" height="1260" width="504" frameborder="0" allowfullscreen="" title="Embedded post"></iframe>',
]

# How many of POSTS to embed. Each one is an iframe that loads from LinkedIn.
SHOW = 3
