#!/usr/bin/env python3
"""The starting filesystem and the exercises for the practice terminal.

Kept apart from build_terminal.py for the same reason the deep-dive prose is
kept apart from its renderer: this is content, and it should be editable
without reading a line of the shell implementation.

The tree is deliberately small but realistic — a log file with a genuine mix
of levels, a config with comments, a script that is not executable yet. Every
exercise below is solvable with what is actually in here.
"""

# node types: {"d": {...children}} for a directory, or a (mode, content) tuple
# for a file. Modes are octal strings exactly as chmod would print them.
FS = {
    "etc": {"d": {
        "hostname": ("0644", "platform-ops-lab\n"),
        "hosts": ("0644",
                  "127.0.0.1\tlocalhost\n"
                  "::1\t\tlocalhost ip6-localhost\n"
                  "10.0.1.10\tapi-01\n"
                  "10.0.1.11\tapi-02\n"
                  "10.0.1.20\tdb-primary\n"),
        "passwd": ("0644",
                   "root:x:0:0:root:/root:/bin/bash\n"
                   "daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin\n"
                   "www-data:x:33:33:www-data:/var/www:/usr/sbin/nologin\n"
                   "vishal:x:1000:1000:Vishal:/home/vishal:/bin/bash\n"),
        "os-release": ("0644",
                       'NAME="Platform Ops Lab"\nVERSION="1.0"\nID=polab\n'),
    }},
    "home": {"d": {
        "vishal": {"d": {
            ".bashrc": ("0644", "export PS1='\\u@\\h:\\w$ '\nalias ll='ls -l'\n"),
            ".profile": ("0644", "# sourced at login\numask 022\n"),
            "README.txt": ("0644",
                           "Practice box for the Platform Ops terminal.\n"
                           "Everything here is simulated in your browser.\n"
                           "Nothing you type leaves this page.\n"),
            "notes": {"d": {
                "linux.md": ("0644",
                             "# Linux\n"
                             "- everything is a file\n"
                             "- pipes join small tools\n"
                             "- permissions are user/group/other\n"),
                "kubernetes.md": ("0644",
                                  "# Kubernetes\n"
                                  "- a Pod is the unit of scheduling\n"
                                  "- a Service gives Pods a stable address\n"),
                "system-design.md": ("0644",
                                     "# System design\n"
                                     "- cache what is read often\n"
                                     "- shard what is written often\n"),
            }},
            "logs": {"d": {
                "app.log": ("0644",
                            "2026-09-01 08:14:02 INFO  starting api server\n"
                            "2026-09-01 08:14:03 INFO  connected to db-primary\n"
                            "2026-09-01 08:19:44 WARN  slow query 1420ms\n"
                            "2026-09-01 08:22:10 ERROR connection refused db-primary\n"
                            "2026-09-01 08:22:11 INFO  retrying in 5s\n"
                            "2026-09-01 08:22:16 INFO  connected to db-primary\n"
                            "2026-09-01 09:02:55 WARN  memory usage 87%\n"
                            "2026-09-01 09:31:07 ERROR upstream timeout api-02\n"
                            "2026-09-01 09:31:09 INFO  removed api-02 from pool\n"
                            "2026-09-01 10:05:33 ERROR disk pressure on node-3\n"
                            "2026-09-01 10:06:00 INFO  evicted 2 pods\n"
                            "2026-09-01 11:40:21 INFO  shutdown signal received\n"),
                "access.log": ("0644",
                               "10.0.1.10 GET /healthz 200\n"
                               "10.0.1.11 GET /healthz 200\n"
                               "10.0.1.10 GET /api/users 200\n"
                               "10.0.1.11 POST /api/users 201\n"
                               "10.0.1.10 GET /api/users 500\n"
                               "10.0.1.11 GET /api/orders 200\n"
                               "10.0.1.10 GET /api/orders 500\n"),
            }},
            "scripts": {"d": {
                # 0644 on purpose: one of the exercises is to fix this.
                "deploy.sh": ("0644",
                              "#!/bin/bash\n"
                              "set -euo pipefail\n"
                              'echo "deploying..."\n'),
            }},
        }},
    }},
    "var": {"d": {
        "log": {"d": {
            "syslog": ("0644",
                       "Sep  1 08:00:01 platform-ops-lab cron[811]: job started\n"
                       "Sep  1 08:05:17 platform-ops-lab kernel: eth0 link up\n"
                       "Sep  1 08:22:10 platform-ops-lab api[1422]: db unreachable\n"),
        }},
        "www": {"d": {}},
    }},
    "tmp": {"d": {}},
    "usr": {"d": {"bin": {"d": {}}, "share": {"d": {}}}},
}

HOME = "/home/vishal"
USER = "vishal"
HOST = "platform-ops-lab"

# ── exercises ───────────────────────────────────────────────────────────────
# check is a JS expression evaluated with `c` in scope:
#   c.out   stdout of the last command, trimmed
#   c.cmd   the last command line, trimmed
#   c.cwd   current directory
#   c.read(path)   file contents or null
#   c.mode(path)   octal mode string or null
#   c.exists(path) boolean
#
# Checking state beats checking the command string wherever possible — there
# is more than one right way to type most of these, and an exercise that only
# accepts one of them teaches typing, not Linux.
EXERCISES = [
    ("Where am I?",
     "Print the full path of the directory you are standing in.",
     "The command is three letters.",
     "c.cmd === 'pwd' && c.out === c.cwd"),

    ("Show the hidden files",
     "List everything in your home directory, including the dotfiles.",
     "ls has a flag for 'all'.",
     "/^ls(\\s|$)/.test(c.cmd) && c.out.includes('.bashrc') && c.out.includes('README.txt')"),

    ("Go to the logs",
     "Change into the logs directory inside your home.",
     "cd logs — or cd ~/logs from anywhere.",
     "c.cwd === '/home/vishal/logs'"),

    ("Read the top of a file",
     "Show only the first 5 lines of app.log.",
     "head takes -n, and -5 is shorthand for it.",
     "c.out.split('\\n').length === 5 && c.out.includes('starting api server') "
     "&& !c.out.includes('memory usage')"),

    ("Count the lines",
     "How many lines are in app.log? Print just the number.",
     "wc counts; -l restricts it to lines.",
     "/\\b12\\b/.test(c.out) && /wc/.test(c.cmd)"),

    ("Find the errors",
     "Show every line of app.log that contains ERROR.",
     "grep PATTERN FILE.",
     "c.out.split('\\n').filter(Boolean).length === 3 && "
     "c.out.split('\\n').every(l => !l || l.includes('ERROR'))"),

    ("Count the errors",
     "Print how many ERROR lines app.log has — the number alone.",
     "grep can count for you, or you can pipe into wc -l.",
     "c.out.trim() === '3' && /grep/.test(c.cmd)"),

    ("Which log levels appear?",
     "List the distinct log levels in app.log — INFO, WARN, ERROR — one per line, no duplicates.",
     "Cut the level out of each line, sort it, then remove neighbouring duplicates.",
     "(function(){var l=c.out.split('\\n').map(s=>s.trim()).filter(Boolean);"
     "return /uniq/.test(c.cmd) && l.length===3 && l.includes('INFO') "
     "&& l.includes('WARN') && l.includes('ERROR');})()"),

    ("Save the errors to a file",
     "Write just the ERROR lines of app.log into a new file called errors.txt in the same directory.",
     "Redirect grep's output with >.",
     "(function(){var f=c.read('/home/vishal/logs/errors.txt');"
     "return !!f && f.split('\\n').filter(Boolean).length===3 "
     "&& f.split('\\n').filter(Boolean).every(l=>l.includes('ERROR'));})()"),

    ("Make the script runnable",
     "deploy.sh in ~/scripts is not executable. Fix that.",
     "chmod +x, or the numeric form 755.",
     "(function(){var m=c.mode('/home/vishal/scripts/deploy.sh');"
     "return !!m && m[1] && (parseInt(m[1],8) & 1) === 1;})()"),

    ("Find every note",
     "Find all files ending in .md anywhere under your home directory.",
     "find TAKES A PATH then -name with a quoted pattern.",
     "/find/.test(c.cmd) && c.out.includes('linux.md') && c.out.includes('kubernetes.md') "
     "&& c.out.includes('system-design.md')"),

    ("Who am I?",
     "Print your username.",
     "One word, and it is a question.",
     "c.out.trim() === 'vishal' && /whoami/.test(c.cmd)"),
]
