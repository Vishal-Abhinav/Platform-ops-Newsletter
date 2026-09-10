#!/usr/bin/env python3
"""Foundation content, batch B: Git, Shell & Bash, Python."""
import os, pathlib as _pl
ROOT = _pl.Path(os.environ.get("PO_ROOT") or _pl.Path(__file__).resolve().parent.parent)
TOOLS = ROOT / "tools"

from content_page import card, term, table, note, diagram, section

# ═══════════════════════════════════════════════════════════════════════════
# GIT & VERSION CONTROL
# ═══════════════════════════════════════════════════════════════════════════
GIT_DIAGRAM = diagram([
    ("Your edits", [("Working tree", "core"), ("Untracked files", "plain")]),
    ("Staging", [("Index / staging area", "warm"), ("git add", "warm"),
                 ("git restore --staged", "warm")]),
    ("Object store", [("blob = content", "go"), ("tree = directory", "go"),
                      ("commit = snapshot", "go"), ("tag = named commit", "go")]),
    ("Refs", [("HEAD", "calm"), ("refs/heads/*", "calm"),
              ("refs/remotes/*", "calm"), ("refs/tags/*", "calm")]),
    ("Safety net", [("reflog — 90 days", "hot"), ("git fsck --lost-found", "hot")]),
    ("Remote", [("origin", "plain"), ("fetch / push", "plain"), ("packfiles", "plain")]),
], "Git's four object types, the three trees, and where a lost commit still lives")

GIT_CORE = "".join([
 card(1, "The object model — Git is a content-addressed store", "Four object types and a hash. Everything else is a convention on top.",
      ["blob", "tree", "commit", "SHA"], """
<p>Git is not a diff engine. It stores <strong>snapshots</strong>, addressed by the hash of their
content, in four object types:</p>
<ul>
<li><strong>blob</strong> — the bytes of one file. No name, no permissions, just content. Two
identical files anywhere in history are one blob.</li>
<li><strong>tree</strong> — a directory listing: names, modes, and the hashes of the blobs and
trees inside it.</li>
<li><strong>commit</strong> — a pointer to one root tree, plus parent commit hashes, author,
committer and message.</li>
<li><strong>tag</strong> — an annotated pointer to a commit, with its own message and signature.</li>
</ul>
<p>Every object's name <em>is</em> the SHA of its content, which makes the whole history
tamper-evident: change one byte in one file in one old commit and every commit hash after it
changes too. That is also why rewriting published history is antisocial — everyone else's hashes
stop matching.</p>
""" + term("looking inside", [
    ("$", "git cat-file -p HEAD"),
    ("", "tree 9d4f2a1c8e7b3f0a5d6c2e1b4a8f7d3c9e0b1a2f"),
    ("", "parent 3c1e8a9f2b7d4c6e0a5f8b3d1c9e7a2f4b6d8c0e"),
    ("", "author Vishal Abhinav <...> 1789012345 +0530"),
    ("", ""),
    ("", "Fix the writeback stall under load"),
    ("$", "git cat-file -p HEAD^{tree}"),
    ("", "100644 blob a3f9...    README.md"),
    ("", "040000 tree 7b2c...    src"),
    ("#", "A commit is one tree plus metadata. That is genuinely all it is."),
])),

 card(2, "The three trees", "Working tree, index, HEAD — nearly every confusing Git command is moving something between these.",
      ["index", "HEAD", "staging"], """
<p>Git maintains three states of your project simultaneously, and almost every command is defined
by which of them it touches:</p>
<ul>
<li><strong>HEAD</strong> — the commit you're on. What <code>git log</code> starts from.</li>
<li><strong>Index</strong> (staging area) — the proposed next commit. <code>git add</code> copies
from working tree to index.</li>
<li><strong>Working tree</strong> — the files on disk you're actually editing.</li>
</ul>
<p>Once you hold that model, the reset modes stop being magic. They differ only in how far down
they push HEAD's new position:</p>
""" + table(["Command", "HEAD", "Index", "Working tree", "Use when"], [
    ["<code>git reset --soft X</code>", "→ X", "unchanged", "unchanged", "Recommit differently; keep everything staged"],
    ["<code>git reset --mixed X</code>", "→ X", "→ X", "unchanged", "Default. Unstage but keep your edits"],
    ["<code>git reset --hard X</code>", "→ X", "→ X", "→ X", "Throw the work away. Nothing else does this"],
    ["<code>git checkout X</code>", "→ X", "→ X", "→ X", "Move to another commit (detaches HEAD)"],
    ["<code>git switch B</code>", "→ B", "→ B", "→ B", "Move to a branch. The safe, modern spelling"],
    ["<code>git restore F</code>", "—", "—", "→ index", "Discard working-tree edits to one file"],
    ["<code>git restore --staged F</code>", "—", "→ HEAD", "—", "Unstage one file, keep the edit"],
], "mono") + note("tip", "switch and restore exist now", """
<p style="margin:0"><code>git checkout</code> was overloaded to do four unrelated jobs, which is
why it was so easy to lose work with it. Since 2.23 the jobs are split: <code>git switch</code>
changes branches, <code>git restore</code> changes files. Use them and a whole category of
accidents disappears.</p>""")),

 card(3, "Branches are pointers, and that is the whole trick", "17 bytes in a file. Nothing is copied, ever.",
      ["refs", "HEAD", "fast-forward"], """
<p>A branch is a file under <code>.git/refs/heads/</code> containing one 40-character hash. Making
a branch writes 41 bytes. Deleting one deletes 41 bytes. Nothing is copied, which is why Git
branching is instant while it was expensive in the tools Git replaced.</p>
<p><code>HEAD</code> is a file containing <code>ref: refs/heads/main</code> — a pointer to a
pointer. Committing updates the branch that HEAD names. <strong>Detached HEAD</strong> just means
HEAD holds a hash directly instead of a ref: commits you make there belong to no branch, and
nothing but the reflog remembers them.</p>
""" + term("branches are files", [
    ("$", "cat .git/HEAD"),
    ("", "ref: refs/heads/main"),
    ("$", "cat .git/refs/heads/main"),
    ("", "3c1e8a9f2b7d4c6e0a5f8b3d1c9e7a2f4b6d8c0e"),
    ("$", "git update-ref refs/heads/hotfix 3c1e8a9"),
    ("#", "That is exactly what 'git branch hotfix' does. No copying."),
])),

 card(4, "Merge, rebase, squash — what each actually produces", "Not a style argument. Three different histories with three different debugging properties.",
      ["merge", "rebase", "squash"], """
<p><strong>Merge</strong> creates one new commit with two parents. Nothing is rewritten, every
original hash survives, and the history records that two lines of work existed in parallel.</p>
<p><strong>Rebase</strong> replays your commits onto a new base, one at a time. Each replayed
commit is a <em>new object with a new hash</em>. The originals are orphaned (still in the reflog).
History becomes linear and the parallel work is no longer recorded.</p>
<p><strong>Squash</strong> collapses a branch into one commit on the target. Simplest log, most
information destroyed.</p>
<h3>The property that actually matters</h3>
<p>Choose on the basis of <code>git bisect</code>. Bisect needs every commit in history to build
and run. A rebased or squashed branch gives you commits that were tested as a unit — good. A merge
of a branch whose intermediate commits were broken gives you bisect runs that fail to compile, and
you spend the session marking them <code>skip</code>. That is the real argument for tidying a
branch before it lands, and it has nothing to do with the log looking pretty.</p>
""" + note("trap", "Never rebase a branch someone else has pulled", """
<p style="margin:0">Rebasing makes new commits with new hashes. Anyone who already has the old
ones will merge both copies back in on their next pull, and the branch grows a duplicate of every
commit. The rule is simple and absolute: rebase only what lives solely on your machine.</p>""")),
])

GIT_ADV = "".join([
 card(5, "The reflog — why nothing is really lost", "Ninety days of every position HEAD has held.",
      ["reflog", "recovery", "fsck"], """
<p>Every time HEAD moves — commit, checkout, reset, rebase, merge — Git appends the old position
to the reflog. Objects stay in the store until garbage collection, and gc will not touch anything
reachable from a reflog entry. Default expiry is <strong>90 days</strong> for reachable entries
and 30 for unreachable ones.</p>
<p>This means <code>git reset --hard</code> almost never actually destroys a commit. It moves a
pointer. The commit is still there, and the reflog knows where.</p>
""" + term("recovering from a hard reset", [
    ("$", "git reset --hard HEAD~3"),
    ("", "HEAD is now at 3c1e8a9 Fix the writeback stall"),
    ("#", "...three commits of work apparently gone."),
    ("$", "git reflog"),
    ("", "3c1e8a9 HEAD@{0}: reset: moving to HEAD~3"),
    ("", "8f2b4d1 HEAD@{1}: commit: Add retry budget to the client"),
    ("", "a91c3e7 HEAD@{2}: commit: Wire up the circuit breaker"),
    ("", "5d0f8b2 HEAD@{3}: commit: Extract the transport interface"),
    ("$", "git reset --hard 8f2b4d1"),
    ("#", "All three back. The commits never went anywhere."),
    ("", ""),
    ("#", "Reflog gone too (fresh clone, or expired)? Objects may still exist:"),
    ("$", "git fsck --lost-found --no-reflogs"),
    ("", "dangling commit 8f2b4d1c9e0a7f3b2d5c8e1a4f6b9d0c3e7a2f5b"),
])),

 card(6, "git bisect — binary search over history", "Twelve builds to find the bad commit in four thousand.",
      ["bisect", "regression", "automation"], """
<p>You know it worked in the release three weeks ago and it's broken now. Between them are 4,000
commits. Bisect does binary search: <code>log₂(4000) ≈ 12</code> builds to find the exact commit
that introduced the problem.</p>
<p>The manual form is fine, but the payoff is <code>git bisect run</code> with a script that exits
0 for good and non-zero for bad. Then it's fully automatic — go and do something else while it
narrows down.</p>
""" + term("automated bisect", [
    ("$", "git bisect start"),
    ("$", "git bisect bad HEAD"),
    ("$", "git bisect good v2.14.0"),
    ("", "Bisecting: 1994 revisions left to test after this (roughly 11 steps)"),
    ("", ""),
    ("#", "exit 0 = good, 1 = bad, 125 = skip (can't build this one)"),
    ("$", "git bisect run ./scripts/reproduce.sh"),
    ("", "running ./scripts/reproduce.sh"),
    ("", "..."),
    ("", "8f2b4d1c is the first bad commit"),
    ("", "    Add retry budget to the client"),
    ("$", "git bisect reset"),
]) + note("tip", "Make the reproducer fast before you start", """
<p style="margin:0">Bisect runs your script a dozen times. A five-minute test suite is an hour;
a ten-second targeted reproducer is two minutes. Time spent narrowing the test down to the one
failing case pays for itself immediately.</p>""")),

 card(7, "Packfiles, gc, and why the clone is 4 GB", "Loose objects, delta compression, and the history you can't delete by deleting files.",
      ["packfile", "gc", "filter-repo", "LFS"], """
<p>New objects are written loose — one zlib-compressed file each. <code>git gc</code> packs them
into a <strong>packfile</strong> with delta compression, storing similar objects as diffs against
one another. A repo with 200,000 loose objects and the same repo packed can differ by an order of
magnitude on disk.</p>
<h3>The thing that catches everyone</h3>
<p>Deleting a large file in a new commit does <strong>not</strong> shrink the repository. The blob
is still reachable from every commit that contained it, so it ships with every clone forever. A
500 MB accidental binary from 2019 is still in everybody's clone today.</p>
<p>Removing it means rewriting history — <code>git filter-repo</code> (the maintained successor to
<code>filter-branch</code>) — followed by a force push and every collaborator re-cloning. Doing it
right is disruptive; the answer is to not commit large binaries in the first place, which is what
Git LFS is for.</p>
""" + term("finding what's making the repo heavy", [
    ("$", "git count-objects -vH"),
    ("", "count: 1204"),
    ("", "size-pack: 3.82 GiB"),
    ("$", "git rev-list --objects --all |"),
    ("$", "  git cat-file --batch-check='%(objecttype) %(objectname) %(objectsize) %(rest)' |"),
    ("$", "  awk '$1==\"blob\"' | sort -k3 -n -r | head -5"),
    ("", "blob 7f2a9c1 498237440 assets/demo-recording.mov"),
    ("#", "475 MB in one blob, in every clone, forever."),
])),

 card(8, "Hooks, worktrees and the bits that save real time", "Three features most people never turn on.",
      ["hooks", "worktree", "rerere"], """
<h3>Hooks</h3>
<p>Scripts in <code>.git/hooks/</code> that fire at defined points. <code>pre-commit</code> for
formatting and lint, <code>pre-push</code> for the fast test subset, <code>commit-msg</code> for
message conventions. They are local and not versioned — which is why teams use a manager like
pre-commit to install them from a config that <em>is</em> versioned. Server-side hooks are how a
platform enforces signed commits or protected paths.</p>
<h3>Worktrees</h3>
<p><code>git worktree add ../hotfix release-2.14</code> gives you a second working directory on a
different branch, sharing one object store. No stashing, no second clone, no re-downloading 4 GB
to fix one line on a release branch while your feature build is still running.</p>
<h3>rerere</h3>
<p><em>Reuse recorded resolution.</em> Turn it on and Git remembers how you resolved a given
conflict, then replays that resolution automatically when the same conflict appears again — which
it will, on every rebase of a long-running branch.</p>
""" + term("worth putting in your global config", [
    ("$", "git config --global rerere.enabled true"),
    ("$", "git config --global pull.rebase true"),
    ("$", "git config --global fetch.prune true"),
    ("$", "git config --global diff.algorithm histogram"),
    ("$", "git config --global rebase.autosquash true"),
    ("$", "git config --global init.defaultBranch main"),
    ("#", "fetch.prune alone removes a whole class of 'why is this dead branch"),
    ("#", "still in my tab completion' confusion."),
])),
])

GIT_PRACTICE = """
<p>Two situations that come up constantly, and the shortest correct path through each.</p>
<h3>You committed to the wrong branch</h3>
""" + term("move the last commit to where it belongs", [
    ("$", "git log --oneline -1"),
    ("", "8f2b4d1 Add retry budget to the client"),
    ("#", "This should have been on feature/retries, not main."),
    ("$", "git branch feature/retries          # point a new branch here"),
    ("$", "git reset --hard HEAD~1             # rewind main"),
    ("$", "git switch feature/retries          # the commit is safely over here"),
]) + """
<h3>You need one commit from another branch</h3>
""" + term("cherry-pick, and what to watch for", [
    ("$", "git cherry-pick 8f2b4d1"),
    ("#", "Makes a NEW commit with a new hash and the same change."),
    ("#", "Both branches now carry the change under different hashes, so the"),
    ("#", "eventual merge may conflict. -x records the origin in the message:"),
    ("$", "git cherry-pick -x 8f2b4d1"),
    ("", "    (cherry picked from commit 8f2b4d1c9e0a7f3b2d5c8e1a4f6b9d0c3e7a2f5b)"),
]) + note("warn", "The one habit worth building", """
<p style="margin:0">Before any command that rewrites history — <code>reset --hard</code>,
<code>rebase</code>, <code>filter-repo</code> — run <code>git reflog</code> once and note the
current hash. It takes two seconds and turns every subsequent mistake into a one-line
recovery.</p>""")

GIT_CHEAT = table(["Command", "What it does"], [
    ["<code>git reflog</code>", "Every position HEAD has held. Your undo button"],
    ["<code>git log --oneline --graph --all</code>", "The actual shape of your branches"],
    ["<code>git log -S'string'</code>", "Commits that added or removed that string — pickaxe search"],
    ["<code>git log -p -- path/to/file</code>", "Full history of one file, with diffs"],
    ["<code>git blame -w -C file</code>", "Blame ignoring whitespace and following moved code"],
    ["<code>git bisect run ./test.sh</code>", "Automatic binary search for the breaking commit"],
    ["<code>git switch -c branch</code>", "Create and move to a branch (safe <code>checkout -b</code>)"],
    ["<code>git restore --staged file</code>", "Unstage without touching your edits"],
    ["<code>git worktree add ../dir branch</code>", "Second working directory, one object store"],
    ["<code>git stash push -m 'msg' -- path</code>", "Stash only specific paths, with a label"],
    ["<code>git rebase -i --autosquash HEAD~5</code>", "Tidy a branch before it lands"],
    ["<code>git commit --fixup HASH</code>", "Mark a fix for autosquash to fold in later"],
    ["<code>git diff --staged</code>", "Review exactly what you are about to commit"],
    ["<code>git fsck --lost-found</code>", "Find dangling objects when the reflog can't help"],
    ["<code>git count-objects -vH</code>", "Repo size, packed and loose"],
    ["<code>git push --force-with-lease</code>", "Force push that refuses if someone else pushed first"],
], "mono")

GIT = dict(
    slug="git-version-control",
    title="Git & Version Control",
    tagline=("Git as a content-addressed object store — the four object types, the three trees, "
             "and the recovery paths that mean you have almost certainly not lost that work."),
    eyebrow="Foundation · Core",
    meta=["<b>24 min</b> read", "Level: <b>core → advanced</b>", "Foundation <b>10 / 10</b>"],
    sections=(
        section("The model", "WHAT GIT ACTUALLY STORES",
                "Four object types, three trees, and a reflog that keeps 90 days of everything "
                "you thought you deleted.",
                f'<div class="dg-scroll">{GIT_DIAGRAM}</div>'
                '<p class="dg-cap">Nothing in the object store is ever modified — objects are '
                'immutable and named by their own hash. Every operation that looks destructive '
                'is really just moving a pointer.</p>')
        + section("Core", "CORE CONCEPTS", "The model that makes every confusing command obvious.", GIT_CORE)
        + section("Advanced", "ADVANCED", "Recovery, bisection, repository weight, and the features worth turning on.", GIT_ADV)
        + section("In practice", "TWO COMMON MESSES", None, GIT_PRACTICE)
        + section("Reference", "CHEATSHEET", None, GIT_CHEAT)
    ),
)


# ═══════════════════════════════════════════════════════════════════════════
# SHELL & BASH
# ═══════════════════════════════════════════════════════════════════════════
SH_DIAGRAM = diagram([
    ("1 · Read", [("Read a line", "core"), ("Tokenise", "core"), ("Parse into commands", "core")]),
    ("2 · Expand", [("Brace {a,b}", "warm"), ("Tilde ~", "warm"), ("Parameter $VAR", "warm"),
                    ("Command $(…)", "warm"), ("Arithmetic $((…))", "warm")]),
    ("3 · Split", [("Word splitting on $IFS", "hot"), ("Pathname glob *", "hot"),
                   ("Quote removal", "hot")]),
    ("4 · Redirect", [("< > >> 2>&1", "calm"), ("Pipes |", "calm"),
                      ("Here-docs <<EOF", "calm")]),
    ("5 · Execute", [("Builtin?", "go"), ("Function?", "go"),
                     ("fork + execve", "go"), ("wait / $?", "go")]),
], "The order the shell does things — and why quoting bugs are always a step-3 problem")

SH_CORE = "".join([
 card(1, "Expansion order — the root of most shell bugs", "The shell does eight things to your line, in a fixed order, before anything runs.",
      ["expansion", "word splitting", "globbing"], """
<p>Almost every surprising shell behaviour comes from not knowing this order. The shell performs,
strictly in sequence:</p>
<ol>
<li>Brace expansion — <code>{a,b}</code></li>
<li>Tilde expansion — <code>~</code></li>
<li>Parameter and variable expansion — <code>$VAR</code></li>
<li>Command substitution — <code>$(…)</code></li>
<li>Arithmetic expansion — <code>$((…))</code></li>
<li><strong>Word splitting</strong> on <code>$IFS</code></li>
<li><strong>Pathname expansion</strong> (globbing)</li>
<li>Quote removal</li>
</ol>
<p>Steps 6 and 7 happen <em>after</em> your variable has been substituted. That is the entire
explanation for the filename-with-spaces bug: the shell substitutes
<code>my report.pdf</code>, then splits it into two words, then hands <code>rm</code> two
arguments that don't exist.</p>
<p><strong>Double quotes suppress steps 6 and 7.</strong> That is what they are for. Quote every
expansion unless you have a specific reason not to.</p>
""" + term("the same command, quoted and not", [
    ("$", "f='my report.pdf'"),
    ("$", "rm $f"),
    ("", "rm: cannot remove 'my': No such file or directory"),
    ("", "rm: cannot remove 'report.pdf': No such file or directory"),
    ("$", 'rm "$f"'),
    ("#", "One argument. This is the whole lesson."),
    ("", ""),
    ("#", "Arrays need the same care — \"${a[@]}\" keeps elements intact:"),
    ("$", 'files=("my report.pdf" "notes 2.txt")'),
    ("$", 'printf "%s\\n" "${files[@]}"'),
    ("", "my report.pdf"),
    ("", "notes 2.txt"),
])),

 card(2, "Exit codes, pipelines and where failures hide", "A pipeline's exit status is the last command's, which is almost never what you want.",
      ["exit code", "pipefail", "PIPESTATUS"], """
<p><code>$?</code> holds the exit status of the last command: 0 for success, 1–255 otherwise.
By convention 1 is a general error, 2 is a usage error, 126 means found but not executable, 127
means not found, and 128+N means killed by signal N — so 137 is SIGKILL (128+9), which is what an
OOM kill looks like from the outside.</p>
<h3>The pipeline trap</h3>
<p>In <code>a | b | c</code>, <code>$?</code> is <strong>c's</strong> exit status. If
<code>a</code> fails and <code>c</code> succeeds, the pipeline reports success. A backup script
of the form <code>pg_dump … | gzip &gt; backup.gz</code> will happily report success while writing
a perfectly valid gzip of an error message.</p>
<p><code>set -o pipefail</code> makes the pipeline return the rightmost non-zero status.
<code>${PIPESTATUS[@]}</code> gives you every stage's status individually.</p>
""" + term("the backup that silently wasn't", [
    ("$", "pg_dump missing_db | gzip > backup.sql.gz; echo $?"),
    ("", "pg_dump: error: connection to database \"missing_db\" failed"),
    ("", "0"),
    ("#", "Exit 0. The cron job is 'green'. The backup is 20 bytes of nothing."),
    ("", ""),
    ("$", "set -o pipefail"),
    ("$", "pg_dump missing_db | gzip > backup.sql.gz; echo $?"),
    ("", "1"),
    ("$", 'echo "${PIPESTATUS[@]}"'),
    ("", "1 0"),
    ("#", "Stage 1 failed, stage 2 succeeded. Now you know which."),
])),

 card(3, "Redirection and file descriptors", "0, 1, 2 — and why 2>&1 has to come after > file.",
      ["stdin", "stdout", "stderr", "fd"], """
<p>Every process starts with three descriptors: <strong>0 stdin</strong>, <strong>1 stdout</strong>,
<strong>2 stderr</strong>. Redirection rewires them before the command runs.</p>
<p>Order matters, and it is the reverse of how people read it. <code>&gt;file 2&gt;&amp;1</code>
first points 1 at the file, then points 2 at wherever 1 is now — the file. Both go to the file.
<code>2&gt;&amp;1 &gt;file</code> first points 2 at wherever 1 currently is — the terminal — and
then moves 1 to the file. stdout goes to the file, stderr still goes to the terminal. This is the
single most common shell redirection bug.</p>
""" + table(["Form", "Effect"], [
    ["<code>&gt; f</code>", "stdout to f, truncating"],
    ["<code>&gt;&gt; f</code>", "stdout to f, appending"],
    ["<code>2&gt; f</code>", "stderr to f"],
    ["<code>&amp;&gt; f</code> / <code>&gt; f 2&gt;&amp;1</code>", "both to f (bash)"],
    ["<code>2&gt;&amp;1 &gt; f</code>", "<strong>stdout to f, stderr to terminal</strong> — usually a bug"],
    ["<code>&gt; /dev/null 2&gt;&amp;1</code>", "discard everything"],
    ["<code>&lt; f</code>", "stdin from f"],
    ["<code>&lt;&lt;&lt; 'str'</code>", "here-string — feed a literal to stdin"],
    ["<code>&lt;(cmd)</code>", "process substitution — a command's output as a filename"],
    ["<code>exec 3&gt; f</code>", "open fd 3 for the rest of the script"],
], "mono")),

 card(4, "Test constructs: [ vs [[ vs ((", "Three of them, and only one is a real shell keyword.",
      ["test", "conditionals", "bash"], """
<p><code>[</code> is a <em>command</em> — historically <code>/usr/bin/[</code>. Its arguments go
through word splitting and globbing like any other command's, which is why an unquoted empty
variable turns <code>[ $x = y ]</code> into <code>[ = y ]</code> and a syntax error.</p>
<p><code>[[ ]]</code> is a bash <strong>keyword</strong>. The shell parses it specially: no word
splitting, no globbing on the left side, and it adds <code>=~</code> for regex and
<code>&amp;&amp;</code>/<code>||</code> inside. Use it in bash, always.</p>
<p><code>(( ))</code> is arithmetic evaluation: bare variable names, C-style operators, and an
exit status that is 0 when the expression is non-zero — the opposite of every other exit code
convention, which trips people up exactly once.</p>
""" + term("why [[ ]] is worth the non-portability", [
    ("$", "x="),
    ("$", "[ $x = foo ] && echo yes"),
    ("", "bash: [: =: unary operator expected"),
    ("$", "[[ $x = foo ]] && echo yes"),
    ("#", "No error. No output. Correct."),
    ("", ""),
    ("$", '[[ $version =~ ^v([0-9]+)\\.([0-9]+) ]] && echo "major ${BASH_REMATCH[1]}"'),
    ("", "major 2"),
    ("", ""),
    ("$", "(( count > 10 )) && echo busy"),
    ("#", "No $ needed, and it reads like arithmetic because it is."),
])),
])

SH_ADV = "".join([
 card(5, "set -euo pipefail — and where it lies to you", "The standard safety preamble, plus the three cases it doesn't cover.",
      ["strict mode", "errexit", "traps"], """
<p><code>set -e</code> exits on an unhandled non-zero status. <code>set -u</code> errors on an
unset variable. <code>set -o pipefail</code> propagates pipeline failures. Together they turn a
script that limps on after an error into one that stops. Every ops script should start with them.</p>
<h3>Three places -e does not fire</h3>
<ul>
<li><strong>Inside a condition.</strong> <code>if cmd; then</code>, <code>cmd &amp;&amp; …</code>,
<code>! cmd</code> — the failure is being tested, so it is not an error. Correct, but it means a
function called from an <code>if</code> loses errexit <em>throughout its body</em>.</li>
<li><strong>Command substitution in an assignment.</strong> <code>local x=$(failing)</code>
succeeds, because <code>local</code> succeeded. Split the declaration from the assignment.</li>
<li><strong>Anything but the last command in a pipeline</strong> — unless pipefail is set.</li>
</ul>
""" + term("the one that gets everyone", [
    ("$", "set -euo pipefail"),
    ("$", "get_version() { cat /nonexistent; }"),
    ("$", "main() { local v=$(get_version); echo \"got [$v]\"; }"),
    ("$", "main"),
    ("", "cat: /nonexistent: No such file or directory"),
    ("", "got []"),
    ("#", "Still running, with an empty value. 'local' returned 0."),
    ("", ""),
    ("#", "Split it, and -e does its job:"),
    ("$", "main() { local v; v=$(get_version); echo \"got [$v]\"; }"),
])),

 card(6, "Traps, cleanup and signal handling", "The difference between a script that leaves a mess and one that doesn't.",
      ["trap", "EXIT", "mktemp"], """
<p><code>trap 'handler' EXIT</code> runs the handler however the script ends — normal exit, error
under <code>set -e</code>, or a caught signal. It is the shell's <code>finally</code>, and it is
the right place for every temp file, lock and mount you created.</p>
<p>Trapping <code>INT TERM</code> as well lets you clean up when someone hits Ctrl-C or the
orchestrator sends SIGTERM. In a container, a script that traps TERM and forwards it to its child
is the difference between a two-second shutdown and the full 30-second grace period.</p>
""" + term("a cleanup that actually runs", [
    ("$", "#!/usr/bin/env bash"),
    ("$", "set -euo pipefail"),
    ("", ""),
    ("$", 'tmp=$(mktemp -d)'),
    ("$", 'cleanup() { rm -rf "$tmp"; [[ -n ${child:-} ]] && kill "$child" 2>/dev/null || true; }'),
    ("$", "trap cleanup EXIT INT TERM"),
    ("", ""),
    ("$", 'long_running_thing > "$tmp/out" &'),
    ("$", "child=$!"),
    ("$", 'wait "$child"'),
    ("#", "Ctrl-C, SIGTERM, an error, or success — the temp dir goes away and"),
    ("#", "the child gets signalled. One trap line covers all four paths."),
])),

 card(7, "Process substitution and doing without a temp file", "<(cmd) gives you a command's output where a filename is expected.",
      ["process substitution", "fifo", "diff"], """
<p><code>&lt;(cmd)</code> runs <code>cmd</code> and substitutes the path of a file descriptor
(<code>/dev/fd/63</code>) that reads its output. Anything expecting a filename now accepts a
command. No temp file, no cleanup, no race.</p>
<p>The classic use is comparing two things that aren't files — the output of a command on two
hosts, a sorted list against another sorted list, a config as deployed versus as intended.</p>
""" + term("comparing two live states", [
    ("$", "diff <(ssh web-1 'rpm -qa | sort') <(ssh web-2 'rpm -qa | sort')"),
    ("", "> nginx-1.24.0-1.el9.x86_64"),
    ("#", "web-2 has a package web-1 doesn't. No temp files were involved."),
    ("", ""),
    ("#", "Also solves the classic subshell-loses-variables problem:"),
    ("$", "count=0; find . -name '*.log' | while read -r f; do ((count++)); done; echo $count"),
    ("", "0"),
    ("#", "The pipeline put the loop in a subshell — the increment was lost."),
    ("$", "count=0; while read -r f; do ((count++)); done < <(find . -name '*.log'); echo $count"),
    ("", "1842"),
])),

 card(8, "Parallelism without a job scheduler", "xargs -P turns a serial loop into a bounded worker pool.",
      ["xargs", "parallel", "GNU parallel"], """
<p>A <code>for</code> loop over 400 hosts running one SSH command each, serially at two seconds
apiece, is thirteen minutes. <code>xargs -P 20</code> makes it forty seconds, with a bounded
concurrency you control.</p>
<p><code>-P N</code> sets parallelism, <code>-n 1</code> passes one argument per invocation, and
<code>-0</code> with <code>find -print0</code> handles filenames with spaces and newlines safely.
For anything more complex, GNU <code>parallel</code> adds per-job output grouping — which matters,
because interleaved output from 20 concurrent jobs is unreadable.</p>
""" + term("bounded parallel work", [
    ("$", "cat hosts.txt | xargs -P 20 -n 1 -I{} ssh {} 'uptime' "),
    ("", ""),
    ("#", "Filenames done safely — NUL-separated, never split on whitespace:"),
    ("$", "find . -name '*.log' -print0 | xargs -0 -P 8 -n 50 gzip"),
    ("", ""),
    ("#", "GNU parallel keeps each job's output together instead of interleaved:"),
    ("$", "parallel -j 20 --tag ssh {} uptime :::: hosts.txt"),
]) + note("warn", "Bound it, always", """
<p style="margin:0"><code>-P 0</code> means unlimited. Point that at 4,000 hosts and you will
exhaust file descriptors, fork bomb the box, or get rate-limited by whatever you're talking to.
Pick a number, and pick it based on what the <em>far</em> side can take.</p>""")),
])

SH_PRACTICE = """
<p>The skeleton below is worth keeping as a template. Every line in it exists because of a specific
class of production failure.</p>
""" + term("a script that fails properly", [
    ("$", "#!/usr/bin/env bash"),
    ("#", "env bash, not /bin/bash — macOS and BSD put it elsewhere"),
    ("$", "set -euo pipefail"),
    ("$", "IFS=$'\\n\\t'"),
    ("#", "drop space from IFS: filenames with spaces stop splitting"),
    ("", ""),
    ("$", 'readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"'),
    ("$", 'readonly LOG_TAG="${0##*/}"'),
    ("", ""),
    ("$", 'log() { printf "%s [%s] %s\\n" "$(date -Is)" "$LOG_TAG" "$*" >&2; }'),
    ("$", 'die() { log "FATAL: $*"; exit 1; }'),
    ("#", "log to stderr so stdout stays clean and pipeable"),
    ("", ""),
    ("$", 'tmp="$(mktemp -d)"'),
    ("$", 'trap \'rm -rf "$tmp"\' EXIT INT TERM'),
    ("", ""),
    ("$", '[[ $# -ge 1 ]] || die "usage: $LOG_TAG <target>"'),
    ("$", 'command -v jq >/dev/null || die "jq is required"'),
    ("", ""),
    ("$", 'main() {'),
    ("$", '  local target="$1"'),
    ("$", '  log "starting on $target"'),
    ("$", '  ...'),
    ("$", '}'),
    ("$", 'main "$@"'),
]) + note("tip", "Run shellcheck in CI", """
<p style="margin:0">ShellCheck catches unquoted expansions, the <code>2&gt;&amp;1</code> ordering
bug, useless <code>cat</code>, subshell variable loss, and about two hundred other things — all
statically, in under a second. There is no reason for a shell script in a repo not to be passing
it.</p>""")

SH_CHEAT = table(["Idiom", "What it does"], [
    ["<code>set -euo pipefail</code>", "Stop on error, on unset var, and on any pipeline stage failing"],
    ["<code>\"${var:-default}\"</code>", "Value, or a default if unset or empty"],
    ["<code>\"${var:?message}\"</code>", "Value, or exit with that message if unset"],
    ["<code>\"${var%%.*}\"</code>", "Strip the longest trailing match — <code>a.b.c</code> → <code>a</code>"],
    ["<code>\"${var##*/}\"</code>", "Strip the longest leading match — basename, without forking"],
    ["<code>\"${var//old/new}\"</code>", "Replace all occurrences, no sed needed"],
    ["<code>\"${#var}\"</code>", "String length"],
    ["<code>\"${arr[@]}\"</code>", "All array elements, each kept as one word"],
    ["<code>${PIPESTATUS[@]}</code>", "Exit status of every stage in the last pipeline"],
    ["<code>trap 'cleanup' EXIT INT TERM</code>", "Run cleanup however the script ends"],
    ["<code>mktemp -d</code>", "Race-free temp directory"],
    ["<code>&lt;(cmd)</code>", "Command output where a filename is expected"],
    ["<code>while read -r l; do …; done &lt; &lt;(cmd)</code>", "Loop without losing variables to a subshell"],
    ["<code>find … -print0 | xargs -0 -P N</code>", "Parallel, safe with any filename"],
    ["<code>command -v tool &gt;/dev/null</code>", "Portable 'is this installed'"],
    ["<code>exec 200&gt;/var/lock/f; flock -n 200</code>", "Don't let two copies run at once"],
    ["<code>shellcheck script.sh</code>", "Static analysis. Run it in CI"],
], "mono")

SHELL = dict(
    slug="shell-and-bash",
    title="Shell & Bash",
    tagline=("How the shell reads, expands and executes a line — and why nearly every shell bug "
             "is really a quoting bug at the word-splitting stage."),
    eyebrow="Foundation · Core",
    meta=["<b>23 min</b> read", "Level: <b>core → advanced</b>", "Foundation <b>06 / 10</b>"],
    sections=(
        section("The model", "WHAT HAPPENS TO A LINE",
                "Five stages, in a fixed order, before your command ever runs.",
                f'<div class="dg-scroll">{SH_DIAGRAM}</div>'
                '<p class="dg-cap">Word splitting and globbing happen <em>after</em> variable '
                'expansion. Double quotes suppress exactly those two steps — which is the whole '
                'reason to use them.</p>')
        + section("Core", "CORE CONCEPTS", "Expansion, exit codes, redirection, conditionals.", SH_CORE)
        + section("Advanced", "ADVANCED", "Strict mode's blind spots, traps, process substitution, parallelism.", SH_ADV)
        + section("In practice", "A SCRIPT SKELETON", None, SH_PRACTICE)
        + section("Reference", "CHEATSHEET", None, SH_CHEAT)
    ),
)


# ═══════════════════════════════════════════════════════════════════════════
# PYTHON
# ═══════════════════════════════════════════════════════════════════════════
PY_DIAGRAM = diagram([
    ("Source", [("your.py", "core"), ("__pycache__/*.pyc", "core")]),
    ("Compile", [("AST", "warm"), ("Bytecode", "warm")]),
    ("Runtime", [("Eval loop (ceval)", "hot"), ("The GIL", "hot"),
                 ("Reference counting", "warm"), ("Cycle GC", "warm")]),
    ("Concurrency", [("threading — I/O only", "calm"), ("multiprocessing — real cores", "go"),
                     ("asyncio — one thread", "calm")]),
    ("Escape hatches", [("C extensions release GIL", "go"), ("numpy / lxml", "go"),
                        ("subprocess", "plain")]),
    ("Environment", [("venv", "plain"), ("pip / uv", "plain"),
                     ("lockfile", "plain"), ("wheels", "plain")]),
], "CPython from source to running code, and where each concurrency model actually helps")

PY_CORE = "".join([
 card(1, "The GIL — what it does and doesn't block", "One lock on the interpreter. It does not make Python single-threaded.",
      ["GIL", "threads", "CPU-bound"], """
<p>CPython's <strong>Global Interpreter Lock</strong> means only one thread executes Python
bytecode at a time. Two threads doing arithmetic will not use two cores; they will take turns, and
the switching overhead can make the threaded version <em>slower</em> than the serial one.</p>
<p>But the GIL is <strong>released around blocking calls</strong>. Every socket read, file read,
<code>time.sleep()</code> and database round trip drops the lock so other threads run. Threads are
genuinely effective for I/O-bound work — which, for ops tooling, is most work. Polling 300
endpoints with 30 threads is a real 30× speedup.</p>
<p>Well-written C extensions do the same. NumPy releases the GIL for the duration of a large array
operation, so numeric code can use multiple cores despite it.</p>
<p>CPython 3.13 shipped an experimental <strong>free-threaded build</strong> (PEP 703) that removes
the GIL entirely. It is opt-in, carries a single-thread performance cost, and much of the C
ecosystem is still catching up — worth watching, not yet worth depending on.</p>
""" + table(["Workload", "Right tool", "Why"], [
    ["HTTP calls, DB queries, file I/O", "<code>threading</code> or <code>asyncio</code>", "GIL is released while blocked"],
    ["Thousands of concurrent connections", "<code>asyncio</code>", "No thread stack per connection"],
    ["Parsing, crunching, compression in pure Python", "<code>multiprocessing</code>", "Only way to get real cores"],
    ["Numeric arrays", "NumPy / Polars", "C code releases the GIL for you"],
    ["Shelling out to other tools", "<code>subprocess</code> + threads", "The work isn't in Python at all"],
])),

 card(2, "Threads, processes, asyncio — picking one", "Three concurrency models, three completely different failure modes.",
      ["asyncio", "multiprocessing", "concurrency"], """
<p><strong>Threads</strong> share memory, cost ~8 MB of stack each, and are preemptive — you can
be interrupted between any two bytecodes, so shared mutable state needs locks. Good to a few
hundred.</p>
<p><strong>Processes</strong> get their own interpreter and their own GIL, so they use real cores.
They cost tens of MB each and communication means pickling across a pipe. Use for CPU-bound work,
and beware: passing large objects can cost more than the computation saves.</p>
<p><strong>asyncio</strong> runs one thread with an event loop; tasks yield at every
<code>await</code>. Tens of thousands of concurrent connections on one core, and no locks needed
because switches only happen at points you can see. The catch is total: <strong>one blocking call
freezes everything</strong>. A single synchronous <code>requests.get()</code> inside an async
handler stops the entire loop.</p>
""" + term("the mistake that makes async slower than sync", [
    ("$", "# WRONG — requests is synchronous; the whole loop stops here"),
    ("$", "async def fetch(url):"),
    ("$", "    return requests.get(url).text"),
    ("", ""),
    ("$", "# Right — an async client all the way down"),
    ("$", "async def fetch(client, url):"),
    ("$", "    r = await client.get(url)"),
    ("$", "    return r.text"),
    ("", ""),
    ("$", "# Or, when the library has no async version, push it off the loop:"),
    ("$", "loop = asyncio.get_running_loop()"),
    ("$", "text = await loop.run_in_executor(None, lambda: requests.get(url).text)"),
])),

 card(3, "Environments and dependency resolution", "The reason 'it works on my machine' is usually literally true.",
      ["venv", "pip", "lockfile", "uv"], """
<p>A virtual environment is a directory with its own <code>site-packages</code> and a
<code>python</code> symlink. Activating it puts that <code>bin/</code> first on
<code>PATH</code>. There is no magic — which is why you can also just call
<code>.venv/bin/python</code> directly and skip activation entirely, and why that is the right
thing to do in a cron job or a systemd unit.</p>
<h3>requirements.txt is not a lockfile</h3>
<p><code>requests&gt;=2.28</code> resolves to whatever is newest at install time. Two installs a
month apart give two different dependency trees, and a transitive dependency you have never heard
of can break your build on a Tuesday. Pin transitively — <code>pip-compile</code>, Poetry,
<code>uv lock</code> — and commit the lock. In a container, install from the lockfile and never
from a range.</p>
<p><code>uv</code> is worth knowing about: a Rust-implemented resolver and installer that is
typically 10–100× faster than pip and speaks the same interfaces. For CI, that difference is real
minutes per build.</p>
""" + term("reproducible, and fast", [
    ("$", "python -m venv .venv && .venv/bin/pip install -r requirements.lock"),
    ("", ""),
    ("#", "or, with uv:"),
    ("$", "uv venv && uv pip sync requirements.lock"),
    ("", ""),
    ("#", "In a Dockerfile — no activation, no ambiguity about which python:"),
    ("$", "RUN python -m venv /opt/venv"),
    ("$", "ENV PATH=/opt/venv/bin:$PATH"),
    ("$", "COPY requirements.lock ."),
    ("$", "RUN pip install --no-cache-dir -r requirements.lock"),
    ("#", "requirements.lock copied before the source = the layer caches"),
])),

 card(4, "Generators and not loading the 40 GB file", "Lazy iteration is the difference between a script that runs and one that gets OOMKilled.",
      ["generator", "yield", "memory"], """
<p><code>f.readlines()</code> reads the whole file into a list. On a 40 GB log that is 40 GB of
RSS and an OOM kill. Iterating the file object directly reads a buffer at a time and holds one
line — constant memory regardless of file size.</p>
<p>Generators extend that to your own code. A function with <code>yield</code> produces values on
demand; chain several and you have a streaming pipeline where nothing is ever fully materialised.
This is the single highest-value Python idiom for ops work, where the input is usually bigger than
the box.</p>
""" + term("streaming, not loading", [
    ("$", "# 40 GB in memory. Killed."),
    ("$", "lines = open('app.log').readlines()"),
    ("$", "errors = [l for l in lines if 'ERROR' in l]"),
    ("", ""),
    ("$", "# Constant memory, any file size"),
    ("$", "def read_lines(path):"),
    ("$", "    with open(path) as f:"),
    ("$", "        yield from f"),
    ("", ""),
    ("$", "def only(lines, needle):"),
    ("$", "    for l in lines:"),
    ("$", "        if needle in l:"),
    ("$", "            yield l"),
    ("", ""),
    ("$", "for line in only(read_lines('app.log'), 'ERROR'):"),
    ("$", "    handle(line)"),
    ("#", "Nothing is materialised. One line is in memory at a time."),
])),
])

PY_ADV = "".join([
 card(5, "Memory: refcounting, cycles, and why RSS never drops", "Python frees objects eagerly and gives memory back to the OS reluctantly.",
      ["refcount", "gc", "arena", "RSS"], """
<p>CPython frees an object the moment its reference count hits zero — deterministic, no pause. A
cycle detector runs periodically to catch objects that reference each other and would otherwise
never reach zero.</p>
<p>But freeing an object does not return memory to the OS. CPython manages memory in
<strong>arenas</strong> of 1 MB (256 KB in older versions), and an arena is only released when
<em>every</em> block in it is free. One long-lived object in an arena pins the whole megabyte.
After processing a large batch, RSS stays high even though Python considers the memory free — it
will be reused by Python, just not returned.</p>
<p>Operationally: a worker whose RSS grows and plateaus is normal. One that grows without bound is
a leak — usually an unbounded cache, a list that's appended to forever, or a logging handler
holding references. For long-running workers, the pragmatic answer is what gunicorn's
<code>--max-requests</code> does: recycle the process periodically and stop worrying about it.</p>
""" + term("finding a leak", [
    ("$", "python -X tracemalloc=5 app.py"),
    ("", ""),
    ("$", "import tracemalloc; tracemalloc.start()"),
    ("$", "snap1 = tracemalloc.take_snapshot()"),
    ("$", "...do the work..."),
    ("$", "snap2 = tracemalloc.take_snapshot()"),
    ("$", "for s in snap2.compare_to(snap1, 'lineno')[:10]: print(s)"),
    ("", "app/cache.py:42: size=812 MiB (+812 MiB), count=2104881 (+2104881)"),
    ("#", "An unbounded dict in cache.py. functools.lru_cache(maxsize=N) exists"),
    ("#", "precisely so you don't hand-roll this."),
])),

 card(6, "subprocess, done correctly", "Where ops scripts go wrong, in four specific ways.",
      ["subprocess", "shell=True", "timeout"], """
<p>Four rules cover almost every subprocess bug:</p>
<ul>
<li><strong>Pass a list, never a string.</strong> <code>shell=True</code> hands your string to
<code>/bin/sh</code>, and any interpolated value becomes shell syntax. It is command injection in
a script you wrote yourself.</li>
<li><strong>Always set a timeout.</strong> Without one, a hung child hangs your script forever —
and in a CI job or a cron, forever means until someone notices.</li>
<li><strong>Check the return code.</strong> <code>run()</code> does not raise by default. Use
<code>check=True</code>, or check <code>.returncode</code> yourself.</li>
<li><strong>Don't use <code>stdout=PIPE</code> with <code>wait()</code>.</strong> If the child
fills the pipe buffer (~64 KB) it blocks writing while you block waiting. Classic deadlock.
<code>run()</code> and <code>communicate()</code> handle this; <code>Popen.wait()</code>
doesn't.</li>
</ul>
""" + term("the safe form", [
    ("$", "# WRONG — injection, no timeout, no error check"),
    ("$", "os.system(f'kubectl delete pod {name}')"),
    ("", ""),
    ("$", "# Right"),
    ("$", "import subprocess"),
    ("$", "try:"),
    ("$", "    r = subprocess.run("),
    ("$", "        ['kubectl', 'delete', 'pod', name],"),
    ("$", "        capture_output=True, text=True, timeout=30, check=True)"),
    ("$", "except subprocess.TimeoutExpired:"),
    ("$", "    log.error('kubectl timed out after 30s')"),
    ("$", "except subprocess.CalledProcessError as e:"),
    ("$", "    log.error('kubectl failed rc=%s: %s', e.returncode, e.stderr.strip())"),
    ("#", "name is one argv element. It cannot become shell syntax."),
])),

 card(7, "Logging that survives contact with production", "print() has no level, no timestamp, and no way to be turned down at 3am.",
      ["logging", "structlog", "JSON"], """
<p>Use the <code>logging</code> module, get the logger with <code>logging.getLogger(__name__)</code>
so every message carries its module, and configure handlers once in <code>main()</code> — never at
import time, which breaks anything importing your module.</p>
<p>Use <strong>lazy formatting</strong>: <code>log.debug("got %s", expensive())</code> evaluates
the argument only if DEBUG is enabled. An f-string is evaluated always, even when the message is
discarded — in a hot loop that is real cost for output nobody sees.</p>
<p>In containers, log <strong>JSON to stdout</strong>. Every log pipeline — Loki, ELK, CloudWatch
— parses structured lines natively, and one exception spanning twelve lines of traceback becomes
one searchable event rather than twelve unrelated ones.</p>
""" + term("a logging setup worth copying", [
    ("$", "import logging, sys, json"),
    ("", ""),
    ("$", "class JsonFormatter(logging.Formatter):"),
    ("$", "    def format(self, r):"),
    ("$", "        d = {'ts': self.formatTime(r), 'level': r.levelname,"),
    ("$", "             'logger': r.name, 'msg': r.getMessage()}"),
    ("$", "        if r.exc_info: d['exc'] = self.formatException(r.exc_info)"),
    ("$", "        return json.dumps(d)"),
    ("", ""),
    ("$", "def setup(level='INFO'):"),
    ("$", "    h = logging.StreamHandler(sys.stdout)"),
    ("$", "    h.setFormatter(JsonFormatter())"),
    ("$", "    logging.basicConfig(level=level, handlers=[h], force=True)"),
    ("", ""),
    ("$", "log = logging.getLogger(__name__)"),
    ("$", "log.info('processed %d records in %.2fs', n, elapsed)"),
])),

 card(8, "Making Python fast enough", "Usually the answer is 'stop writing loops', not 'rewrite it in Go'.",
      ["performance", "profiling", "vectorise"], """
<p>Each bytecode dispatch costs tens of nanoseconds. A Python-level loop over ten million items is
seconds; the same work inside a C-implemented builtin is milliseconds. The optimisation is almost
always to push the loop down into C.</p>
<ul>
<li><code>sum(x)</code>, <code>any()</code>, <code>max()</code>, <code>''.join()</code>,
<code>sorted()</code> — all C loops. Prefer them to hand-written equivalents.</li>
<li>A comprehension beats <code>append</code> in a loop; the append lookup happens once.</li>
<li><code>set</code> membership is O(1); <code>list</code> membership is O(n). Getting this wrong
inside a loop is the most common accidental O(n²) in ops scripts.</li>
<li>NumPy/Polars for numeric work — one operation over a million elements, in C, GIL released.</li>
<li><code>functools.lru_cache</code> for pure functions called repeatedly with the same arguments.</li>
</ul>
<p>And profile before any of it. <code>cProfile</code> for call counts,
<code>py-spy</code> for a live process you cannot restart — which, on a production box, is usually
the only option you have.</p>
""" + term("profiling without touching the process", [
    ("$", "pip install py-spy"),
    ("$", "py-spy top --pid 4412"),
    ("", "Total Samples 4100"),
    ("", "%Own   %Total  OwnTime  TotalTime  Function (filename:line)"),
    ("", "68.00%  71.00%    28.4s     29.7s   _match (app/rules.py:88)"),
    ("", " 9.00%  92.00%     3.8s     38.4s   process (app/worker.py:41)"),
    ("#", "68% in one function. No restart, no code change, no instrumentation."),
    ("", ""),
    ("$", "py-spy record -o profile.svg --pid 4412 --duration 30"),
    ("#", "flame graph of a live production process"),
])),
])

PY_PRACTICE = """
<p>Most ops Python is a script that reads something, does something, and has to be safe to run from
cron at 3am. This skeleton covers the parts that matter when nobody is watching.</p>
""" + term("an ops script that behaves", [
    ("$", "#!/usr/bin/env python3"),
    ("$", '"""Reconcile pod counts against the expected inventory."""'),
    ("$", "import argparse, logging, sys, signal"),
    ("", ""),
    ("$", "log = logging.getLogger('reconcile')"),
    ("", ""),
    ("$", "def parse_args(argv=None):"),
    ("$", "    p = argparse.ArgumentParser(description=__doc__)"),
    ("$", "    p.add_argument('--namespace', required=True)"),
    ("$", "    p.add_argument('--dry-run', action='store_true')"),
    ("$", "    p.add_argument('--log-level', default='INFO')"),
    ("$", "    return p.parse_args(argv)"),
    ("", ""),
    ("$", "def main(argv=None) -> int:"),
    ("$", "    args = parse_args(argv)"),
    ("$", "    setup_logging(args.log_level)"),
    ("$", "    signal.signal(signal.SIGTERM, lambda *_: sys.exit(143))"),
    ("#", "    exit 143 = 128+15, the same code the shell reports for SIGTERM"),
    ("$", "    try:"),
    ("$", "        n = reconcile(args.namespace, dry_run=args.dry_run)"),
    ("$", "    except Exception:"),
    ("$", "        log.exception('reconcile failed')"),
    ("$", "        return 1"),
    ("$", "    log.info('reconciled %d pods', n)"),
    ("$", "    return 0"),
    ("", ""),
    ("$", "if __name__ == '__main__':"),
    ("$", "    sys.exit(main())"),
]) + note("tip", "Return an int from main, and sys.exit it", """
<p style="margin:0">It makes the script testable — <code>assert main(['--namespace','x']) == 0</code>
runs the whole thing in-process — and it gives cron, systemd and Kubernetes a real exit code to act
on. <code>log.exception()</code> inside the handler logs the traceback at ERROR without re-raising,
so the failure is recorded rather than printed to a stderr nobody captured.</p>""")

PY_CHEAT = table(["Tool / idiom", "What it's for"], [
    ["<code>py-spy top --pid N</code>", "Profile a running process without restarting it"],
    ["<code>py-spy dump --pid N</code>", "Stack trace of every thread — for a hung process"],
    ["<code>python -X tracemalloc=5</code>", "Allocation tracking with 5 frames of context"],
    ["<code>python -m cProfile -s cumtime s.py</code>", "Where the time goes, by cumulative cost"],
    ["<code>python -m venv .venv</code>", "Isolated environment — no activation needed to use it"],
    ["<code>uv pip sync requirements.lock</code>", "Fast, exact, reproducible install"],
    ["<code>pip-compile requirements.in</code>", "Turn ranges into a transitively pinned lockfile"],
    ["<code>subprocess.run([...], check=True, timeout=N)</code>", "The only correct default form"],
    ["<code>logging.getLogger(__name__)</code>", "Per-module logger, configurable from one place"],
    ["<code>log.debug('x=%s', v)</code>", "Lazy formatting — not evaluated if DEBUG is off"],
    ["<code>functools.lru_cache(maxsize=N)</code>", "Memoise a pure function, bounded"],
    ["<code>concurrent.futures.ThreadPoolExecutor</code>", "I/O parallelism without touching threads directly"],
    ["<code>concurrent.futures.ProcessPoolExecutor</code>", "CPU parallelism across real cores"],
    ["<code>yield from f</code>", "Stream a file instead of loading it"],
    ["<code>pathlib.Path</code>", "Path handling that doesn't break on separators"],
    ["<code>ruff check . &amp;&amp; ruff format .</code>", "Lint and format, fast enough for a pre-commit hook"],
    ["<code>mypy --strict</code>", "Catch the type errors that only show up in the 3am code path"],
], "mono")

PYTHON = dict(
    slug="python",
    title="Python",
    tagline=("Python for people who run things — the GIL, choosing a concurrency model, streaming "
             "instead of loading, and the subprocess and logging patterns that survive production."),
    eyebrow="Foundation · Core",
    meta=["<b>25 min</b> read", "Level: <b>core → advanced</b>", "Foundation <b>07 / 10</b>"],
    sections=(
        section("The model", "CPYTHON, END TO END",
                "Source to bytecode to the eval loop — and the three ways around the one lock in "
                "the middle.",
                f'<div class="dg-scroll">{PY_DIAGRAM}</div>'
                '<p class="dg-cap">The GIL only guards the eval loop. Everything below it — '
                'blocking I/O, C extensions, subprocesses — runs with the lock released, which '
                'is why threads still help for the work ops code actually does.</p>')
        + section("Core", "CORE CONCEPTS", "Concurrency, environments, and lazy iteration.", PY_CORE)
        + section("Advanced", "ADVANCED", "Memory behaviour, subprocess, logging, and making it fast.", PY_ADV)
        + section("In practice", "AN OPS SCRIPT SKELETON", None, PY_PRACTICE)
        + section("Reference", "CHEATSHEET", None, PY_CHEAT)
    ),
)

TOPICS = [GIT, SHELL, PYTHON]
