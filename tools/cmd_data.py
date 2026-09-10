#!/usr/bin/env python3
"""Command reference data. Each row: (command, what it does, typical use)."""

# ═══════════════════════════════════════════════════════════════════════════
LINUX = dict(
    slug="linux-commands", icon="🐧", title="Linux Commands",
    tagline=("The sysadmin set, grouped by what you are trying to do rather than "
             "alphabetically — with the flags that actually get used."),
    groups=[
 ("nav", "Files & navigation", "Moving around and seeing what is there. <code>ls -lh</code> and "
  "<code>find</code> do most of the work; the rest is knowing which flag saves the second command.", [
  ("<b>ls</b> -lhtr", "Long listing, human sizes, oldest last — newest at the bottom where the cursor is", "ls -lhtr /var/log"),
  ("<b>ls</b> -lda", "Show a directory's own entry rather than its contents", "ls -lda /etc/ssl"),
  ("<b>cd</b> -", "Jump back to the previous directory", "cd -"),
  ("<b>pwd</b> -P", "Physical path, resolving symlinks", "pwd -P"),
  ("<b>tree</b> -L 2 -d", "Directory tree, two levels, directories only", "tree -L 2 -d /opt"),
  ("<b>stat</b>", "Inode, size, permissions and all three timestamps", "stat /etc/passwd"),
  ("<b>file</b>", "What a file actually is, by content not extension", "file /bin/ls"),
  ("<b>readlink</b> -f", "Resolve a symlink chain to its final target", "readlink -f $(which python3)"),
  ("<b>basename</b> / <b>dirname</b>", "Split a path — useful in scripts", "dirname /a/b/c.txt"),
  ("<b>cp</b> -a", "Archive copy: preserves mode, owner, timestamps, links", "cp -a /etc/nginx /backup/"),
  ("<b>mv</b> -n", "Move without overwriting an existing target", "mv -n a.log archive/"),
  ("<b>rsync</b> -avh --progress", "Copy only what changed, with a progress bar", "rsync -avh src/ dst/"),
  ("<b>rsync</b> -avh --delete", "Mirror — removes files gone from the source. Dry-run first", "rsync -avhn --delete a/ b/"),
  ("<b>ln</b> -s", "Symbolic link", "ln -s /opt/app/current /usr/local/bin/app"),
  ("<b>shred</b> -u", "Overwrite then remove — for keys on spinning disks", "shred -u secret.key"),
 ]),

 ("perm", "Permissions & ownership", "Numeric mode is three digits of read(4) write(2) execute(1). "
  "The fourth digit is setuid(4), setgid(2), sticky(1) — and the sticky bit on a shared directory is "
  "what stops users deleting each other's files.", [
  ("<b>chmod</b> 640", "Owner read/write, group read, others nothing", "chmod 640 /etc/app/secrets.conf"),
  ("<b>chmod</b> u+x,g-w", "Symbolic form — change only what you name", "chmod u+x deploy.sh"),
  ("<b>chmod</b> -R g+rX", "Recursive; capital X adds execute only to directories", "chmod -R g+rX /srv/www"),
  ("<b>chmod</b> 1777", "Sticky bit — only the owner can delete their own files", "chmod 1777 /tmp"),
  ("<b>chmod</b> 2775", "setgid on a directory — new files inherit the group", "chmod 2775 /srv/shared"),
  ("<b>chown</b> -R user:group", "Change owner and group recursively", "chown -R www-data:www-data /srv/www"),
  ("<b>umask</b> 027", "Default mask for new files in this shell", "umask 027"),
  ("<b>getfacl</b> / <b>setfacl</b>", "Per-user ACLs beyond the owner/group/other model", "setfacl -m u:deploy:rx /srv/app"),
  ("<b>lsattr</b> / <b>chattr</b> +i", "Immutable flag — even root cannot modify until cleared", "chattr +i /etc/resolv.conf"),
  ("<b>sudo</b> -l", "What can this user actually run as root?", "sudo -l -U deploy"),
  ("<b>id</b>", "UID, GID and every supplementary group", "id deploy"),
  ("<b>namei</b> -l", "Permissions of every component in a path — finds the one bad directory", "namei -l /srv/app/data/f"),
 ]),

 ("text", "Text processing", "The pipeline tools. Worth knowing well: most log investigation is "
  "<code>grep</code> to narrow, <code>awk</code> to extract, <code>sort | uniq -c</code> to count.", [
  ("<b>grep</b> -rn --include='*.py'", "Recursive search with line numbers, one file type", "grep -rn --include='*.py' TODO ."),
  ("<b>grep</b> -c / -l / -v", "Count matches / list files only / invert the match", "grep -c ERROR app.log"),
  ("<b>grep</b> -A3 -B3", "Show context lines after and before each hit", "grep -A3 -B3 Traceback app.log"),
  ("<b>grep</b> -P '\\d{3}'", "Perl regex — the only way to get \\d and lookarounds", "grep -oP 'status=\\K\\d+' access.log"),
  ("<b>awk</b> '{print $7}'", "Print a field. The default separator is any run of whitespace", "awk '{print $7}' access.log"),
  ("<b>awk</b> -F: '$3>=1000{print $1}'", "Filter on a field with a custom separator", "awk -F: '$3>=1000{print $1}' /etc/passwd"),
  ("<b>awk</b> '{s+=$1} END{print s}'", "Sum a column", "du -s * | awk '{s+=$1} END{print s}'"),
  ("<b>sed</b> -i.bak 's/a/b/g'", "In-place replace, keeping a .bak. Always keep the backup", "sed -i.bak 's/8080/9090/g' app.conf"),
  ("<b>sed</b> -n '100,120p'", "Print a line range without printing everything else", "sed -n '100,120p' huge.log"),
  ("<b>sort</b> -k2 -n -r", "Sort by field 2, numeric, descending", "sort -k2 -n -r sizes.txt"),
  ("<b>sort</b> | <b>uniq</b> -c | <b>sort</b> -rn", "The counting idiom — top offenders in any log", "awk '{print $1}' a.log | sort | uniq -c | sort -rn | head"),
  ("<b>cut</b> -d, -f1,3", "Fields from delimited text, when awk is overkill", "cut -d, -f1,3 data.csv"),
  ("<b>tr</b> -d '\\r'", "Strip characters — this one fixes CRLF files", "tr -d '\\r' < win.txt > unix.txt"),
  ("<b>tail</b> -f / -F", "Follow a file; -F survives log rotation", "tail -F /var/log/app.log"),
  ("<b>head</b> -n -5", "Everything except the last 5 lines", "head -n -5 file.txt"),
  ("<b>wc</b> -l", "Line count", "wc -l access.log"),
  ("<b>jq</b> -r '.items[].name'", "Query JSON. -r drops the quotes", "kubectl get po -o json | jq -r '.items[].metadata.name'"),
  ("<b>column</b> -t", "Align whitespace-separated output into columns", "mount | column -t"),
  ("<b>diff</b> -u / <b>vimdiff</b>", "Unified diff between two files", "diff -u old.conf new.conf"),
 ]),

 ("proc", "Processes & signals", "A process is doing one of: running, waiting on I/O (D), sleeping (S), "
  "or already dead (Z). Which one it is decides where you look next.", [
  ("<b>ps</b> aux --sort=-%mem", "Every process, biggest memory first", "ps aux --sort=-%mem | head"),
  ("<b>ps</b> -eo pid,ppid,stat,wchan:20,cmd", "State and the kernel function it is blocked in", "ps -eo pid,stat,wchan:20,cmd"),
  ("<b>pgrep</b> -af", "Find PIDs by pattern, showing the full command line", "pgrep -af nginx"),
  ("<b>pkill</b> -f -TERM", "Signal by full-command-line match. Check with pgrep first", "pkill -f -TERM 'python worker.py'"),
  ("<b>kill</b> -TERM / -KILL", "15 asks politely, 9 cannot be caught or cleaned up after", "kill -TERM 4412"),
  ("<b>kill</b> -HUP", "Reload config without a restart, for daemons that support it", "kill -HUP $(pidof nginx)"),
  ("<b>kill</b> -l", "List signal names and numbers", "kill -l"),
  ("<b>nice</b> / <b>renice</b>", "Scheduling priority, -20 (highest) to 19", "renice 10 -p 4412"),
  ("<b>ionice</b> -c3", "Idle I/O class — for backups that must not disturb production", "ionice -c3 rsync -a src/ dst/"),
  ("<b>nohup</b> … &amp;", "Survive the terminal closing", "nohup ./long-job.sh &amp;"),
  ("<b>timeout</b> 30s", "Kill a command that runs too long. Use it in every cron job", "timeout 30s curl https://api/health"),
  ("<b>lsof</b> -p PID", "Every file, socket and pipe a process holds open", "lsof -p 4412"),
  ("<b>lsof</b> -i :8080", "Which process owns a port", "lsof -i :8080"),
  ("<b>fuser</b> -vm /mnt", "Who is using a mount point — before you unmount", "fuser -vm /mnt/data"),
  ("<b>strace</b> -c -p PID", "Syscall summary of a running process", "strace -c -p 4412"),
  ("<b>pstree</b> -p", "Process tree with PIDs — shows who forked whom", "pstree -p 1"),
 ]),

 ("user", "Users, groups & sessions", "Account state lives in /etc/passwd, /etc/shadow and "
  "/etc/group. Everything below just edits those safely.", [
  ("<b>useradd</b> -m -s /bin/bash", "Create a user with a home directory and a real shell", "useradd -m -s /bin/bash deploy"),
  ("<b>useradd</b> -r -s /usr/sbin/nologin", "System account that cannot log in — for services", "useradd -r -s /usr/sbin/nologin appsvc"),
  ("<b>usermod</b> -aG", "Add to a group. Forget the -a and you replace every other group", "usermod -aG docker deploy"),
  ("<b>userdel</b> -r", "Delete the user and their home directory", "userdel -r olduser"),
  ("<b>passwd</b> -l / -S", "Lock an account / show its password status", "passwd -S deploy"),
  ("<b>chage</b> -l", "Password ageing and expiry for an account", "chage -l deploy"),
  ("<b>groupadd</b> / <b>gpasswd</b> -a", "Create a group, add a member", "gpasswd -a deploy sudo"),
  ("<b>getent</b> passwd", "Query users through NSS — sees LDAP/SSSD, unlike grepping the file", "getent passwd deploy"),
  ("<b>w</b> / <b>who</b>", "Who is logged in and what they are running", "w"),
  ("<b>last</b> -a", "Login history from wtmp", "last -a | head"),
  ("<b>lastb</b>", "Failed login attempts", "lastb | head"),
  ("<b>loginctl</b> list-sessions", "systemd's view of active sessions", "loginctl list-sessions"),
 ]),

 ("pkg", "Packages", "Three families. Know which one you are on before you type — "
  "<code>/etc/os-release</code> tells you.", [
  ("<b>apt</b> update &amp;&amp; apt upgrade", "Refresh the index, then upgrade (Debian/Ubuntu)", "apt update &amp;&amp; apt upgrade -y"),
  ("<b>apt</b> list --installed", "What is installed", "apt list --installed | grep nginx"),
  ("<b>apt-cache</b> policy", "Installed version, candidate version, and which repo", "apt-cache policy nginx"),
  ("<b>dpkg</b> -l / -L / -S", "List packages / files in a package / which package owns a file", "dpkg -S /usr/sbin/nginx"),
  ("<b>dnf</b> install / update", "RHEL 8+, Fedora, Rocky, Alma", "dnf install -y nginx"),
  ("<b>dnf</b> history / history undo", "Transaction log, and rolling one back", "dnf history undo last"),
  ("<b>rpm</b> -qa / -ql / -qf", "Query all / files in a package / owner of a file", "rpm -qf /usr/sbin/nginx"),
  ("<b>rpm</b> -q --changelog", "Why a version exists — includes the CVE it fixed", "rpm -q --changelog openssl | head"),
  ("<b>yum</b> / <b>zypper</b> / <b>apk</b>", "RHEL 7 / SUSE / Alpine equivalents", "apk add --no-cache curl"),
  ("<b>needs-restarting</b> -r", "Does this box need a reboot after patching? (RHEL)", "needs-restarting -r"),
  ("<b>ls</b> /var/run/reboot-required", "Same question on Debian/Ubuntu", "cat /var/run/reboot-required"),
 ]),

 ("disk", "Disk & filesystem", "Two different 'full' conditions: out of blocks (<code>df -h</code>) "
  "and out of inodes (<code>df -i</code>). Check both — millions of tiny files exhaust inodes first.", [
  ("<b>df</b> -h / -i", "Free space by blocks / by inodes", "df -h; df -i"),
  ("<b>du</b> -sh * | sort -h", "What is taking the space in this directory", "du -sh * | sort -h | tail"),
  ("<b>du</b> -xh --max-depth=1 /", "Top-level usage without crossing into other filesystems", "du -xh --max-depth=1 / | sort -h"),
  ("<b>lsblk</b> -o NAME,SIZE,ROTA,MOUNTPOINT", "Block devices, and whether they are rotational", "lsblk -o NAME,SIZE,ROTA,MOUNTPOINT"),
  ("<b>blkid</b>", "UUIDs and filesystem types — what to put in /etc/fstab", "blkid /dev/sdb1"),
  ("<b>mount</b> -o remount,rw /", "Remount read-write, e.g. in rescue mode", "mount -o remount,rw /"),
  ("<b>findmnt</b>", "Mounts as a tree, with the options actually in effect", "findmnt /var"),
  ("<b>mkfs.ext4</b> / <b>mkfs.xfs</b>", "Create a filesystem", "mkfs.xfs -L data /dev/sdb1"),
  ("<b>xfs_growfs</b> / <b>resize2fs</b>", "Grow a filesystem after growing the volume", "xfs_growfs /data"),
  ("<b>fsck</b> -n", "Check without repairing. Never fsck a mounted filesystem", "fsck -n /dev/sdb1"),
  ("<b>pvs</b> / <b>vgs</b> / <b>lvs</b>", "LVM at a glance — physical, group, logical", "vgs; lvs"),
  ("<b>lvextend</b> -r -L +50G", "Grow a logical volume and its filesystem in one step", "lvextend -r -L +50G /dev/vg0/data"),
  ("<b>iostat</b> -x 1", "Per-device await and utilisation — is the disk the bottleneck?", "iostat -x 1"),
  ("<b>lsof</b> +L1", "Deleted files still held open — why df and du disagree", "lsof +L1"),
 ]),

 ("find", "Search & locate", "<code>find</code> is a query language. The order of predicates matters: "
  "it evaluates left to right and stops early, so put the cheap tests first.", [
  ("<b>find</b> . -name '*.log' -mtime +30", "Files matching a name, older than 30 days", "find /var/log -name '*.log' -mtime +30"),
  ("<b>find</b> . -size +100M", "Files over a size", "find / -xdev -size +100M 2>/dev/null"),
  ("<b>find</b> . -type f -newer ref", "Changed more recently than a reference file", "find /etc -type f -newer /tmp/mark"),
  ("<b>find</b> … -delete", "Delete matches. Run it without -delete first, every time", "find /tmp -name 'core.*' -mtime +7 -delete"),
  ("<b>find</b> … -print0 | xargs -0", "Safe with spaces and newlines in filenames", "find . -name '*.gz' -print0 | xargs -0 rm"),
  ("<b>find</b> … -exec … +", "One invocation for many files, not one per file", "find . -name '*.c' -exec grep -l TODO {} +"),
  ("<b>find</b> / -xdev", "Stay on one filesystem — stops it wandering into /proc and NFS", "find / -xdev -name core"),
  ("<b>find</b> . -perm -4000", "setuid binaries — a standard audit sweep", "find / -xdev -perm -4000 -ls"),
  ("<b>locate</b> / <b>updatedb</b>", "Instant filename search from a prebuilt index", "locate nginx.conf"),
  ("<b>which</b> / <b>type</b> -a", "Where a command comes from; type -a shows aliases too", "type -a ls"),
 ]),

 ("cron", "Scheduling & boot", "cron for wall-clock jobs, systemd timers for anything that needs "
  "dependencies, logging or a missed-run catch-up.", [
  ("<b>crontab</b> -l / -e / -u", "List, edit, or act on another user's crontab", "crontab -l -u deploy"),
  ("<b>systemctl</b> list-timers --all", "Every timer, when it last ran and when it runs next", "systemctl list-timers --all"),
  ("<b>systemd-analyze</b> blame", "Which units made the boot slow", "systemd-analyze blame | head"),
  ("<b>systemd-analyze</b> critical-chain", "The dependency path that determined boot time", "systemd-analyze critical-chain"),
  ("<b>at</b> now + 1 hour", "One-off scheduled command", "echo 'systemctl restart app' | at now + 1 hour"),
  ("<b>run-parts</b> --test", "What would /etc/cron.daily actually run?", "run-parts --test /etc/cron.daily"),
  ("<b>uptime</b> / <b>who</b> -b", "How long since boot, and when it booted", "who -b"),
  ("<b>last</b> reboot", "Reboot history", "last reboot | head"),
 ]),

 ("net", "Networking", "<code>ifconfig</code>, <code>netstat</code> and <code>route</code> are "
  "deprecated and missing on modern minimal images. The <code>ip</code> and <code>ss</code> "
  "equivalents are below.", [
  ("<b>ip</b> a", "Interfaces and addresses (replaces ifconfig)", "ip -br a"),
  ("<b>ip</b> r", "Routing table (replaces route -n)", "ip r get 8.8.8.8"),
  ("<b>ip</b> -s link", "Per-interface counters, including errors and drops", "ip -s link show eth0"),
  ("<b>ss</b> -tulpn", "Listening TCP/UDP sockets with the owning process (replaces netstat)", "ss -tulpn"),
  ("<b>ss</b> -s", "Socket summary — how many in each state", "ss -s"),
  ("<b>ss</b> -tan state time-wait | wc -l", "Count sockets in one state", "ss -tan state time-wait | wc -l"),
  ("<b>dig</b> +short / +trace", "DNS answer only / the full delegation path", "dig +trace api.example.com"),
  ("<b>dig</b> @1.1.1.1", "Ask a specific resolver — proves whether it is your resolver", "dig @1.1.1.1 example.com"),
  ("<b>curl</b> -sS -o /dev/null -w '%{http_code} %{time_total}\\n'", "Status and timing without the body", "curl -sS -o /dev/null -w '%{http_code} %{time_total}\\n' https://api/health"),
  ("<b>curl</b> -v --resolve host:443:IP", "Test one backend directly, bypassing DNS", "curl -v --resolve api:443:10.0.1.5 https://api/"),
  ("<b>tcpdump</b> -nni any port 443 -w f.pcap", "Capture to a file for Wireshark", "tcpdump -nni any port 443 -c 100"),
  ("<b>mtr</b> -rw", "traceroute and ping combined, in a report", "mtr -rw 8.8.8.8"),
  ("<b>nc</b> -zv", "Is the port open? The quickest connectivity test there is", "nc -zv db.internal 5432"),
  ("<b>ethtool</b> -S", "NIC statistics — drops, errors, ring exhaustion", "ethtool -S eth0 | grep -i drop"),
  ("<b>nft</b> list ruleset", "Firewall rules (nftables; iptables-save on older systems)", "nft list ruleset"),
 ]),
])


# ═══════════════════════════════════════════════════════════════════════════
KUBECTL = dict(
    slug="kubernetes-commands", icon="☸️", title="Kubernetes Commands",
    tagline=("kubectl grouped by task — inspect, change, debug, and the output flags that make it "
             "scriptable instead of something you read."),
    groups=[
 ("look", "Inspecting", "<code>get</code> tells you what exists, <code>describe</code> tells you why "
  "it is unhappy. Events at the bottom of describe answer most questions on their own.", [
  ("<b>kubectl get</b> po -o wide", "Pods with node, IP and nominated node", "kubectl get po -o wide"),
  ("<b>kubectl get</b> po -A", "Across every namespace", "kubectl get po -A | grep -v Running"),
  ("<b>kubectl get</b> po --field-selector status.phase!=Running", "Only what is not healthy", "kubectl get po -A --field-selector status.phase!=Running"),
  ("<b>kubectl get</b> po -l app=api", "By label — the way controllers select", "kubectl get po -l 'app in (api,web)'"),
  ("<b>kubectl get</b> po --sort-by=.status.containerStatuses[0].restartCount", "Worst restart offenders first", "kubectl get po --sort-by=.status.containerStatuses[0].restartCount"),
  ("<b>kubectl get</b> ev --sort-by=.lastTimestamp", "Events in time order, not the default jumble", "kubectl get ev -A --sort-by=.lastTimestamp | tail -30"),
  ("<b>kubectl describe</b> po NAME", "Full state plus the events for that object", "kubectl describe po api-7d4f-x9k2"),
  ("<b>kubectl get</b> all -n NS", "The common workload kinds in one namespace", "kubectl get all -n payments"),
  ("<b>kubectl api-resources</b>", "Every kind the cluster knows, with short names", "kubectl api-resources --namespaced=true"),
  ("<b>kubectl explain</b> po.spec.containers", "Field documentation straight from the API server", "kubectl explain deploy.spec.strategy --recursive"),
  ("<b>kubectl top</b> po --sort-by=memory", "Live usage — needs metrics-server", "kubectl top po -A --sort-by=memory"),
 ]),

 ("change", "Applying & deleting", "<code>apply</code> is declarative and records intent in an "
  "annotation; <code>create</code> is imperative and fails if the object exists. Use apply.", [
  ("<b>kubectl apply</b> -f dir/ -R", "Apply a directory tree", "kubectl apply -f k8s/ -R"),
  ("<b>kubectl apply</b> --dry-run=server", "Ask the API server what would happen, admission and all", "kubectl apply -f d.yaml --dry-run=server"),
  ("<b>kubectl diff</b> -f", "Diff your manifest against the live object before applying", "kubectl diff -f deploy.yaml"),
  ("<b>kubectl create</b> … --dry-run=client -o yaml", "Generate a manifest skeleton to edit", "kubectl create deploy api --image=nginx --dry-run=client -o yaml"),
  ("<b>kubectl patch</b> -p", "Change one field without sending the whole object", "kubectl patch deploy api -p '{\"spec\":{\"replicas\":5}}'"),
  ("<b>kubectl set image</b>", "Change an image and trigger a rollout", "kubectl set image deploy/api api=repo/api:v2"),
  ("<b>kubectl edit</b>", "Open the live object in $EDITOR. Fine for triage, bad as a habit", "kubectl edit deploy api"),
  ("<b>kubectl delete</b> --grace-period=0 --force", "Last resort for a stuck pod; it can orphan resources", "kubectl delete po stuck --grace-period=0 --force"),
  ("<b>kubectl replace</b> --force", "Delete and recreate — for immutable field changes", "kubectl replace --force -f job.yaml"),
  ("<b>kubectl label</b> / <b>annotate</b> --overwrite", "Add or change metadata in place", "kubectl label no worker-3 tier=spot --overwrite"),
 ]),

 ("debug", "Logs, exec & debugging", "The order that finds it fastest: logs, then previous logs, "
  "then events, then exec. If the container will not start, exec is not available — use "
  "<code>debug</code>.", [
  ("<b>kubectl logs</b> -f --tail=100", "Follow the last 100 lines", "kubectl logs -f --tail=100 api-7d4f"),
  ("<b>kubectl logs</b> --previous", "Logs from the container that just crashed. The important one", "kubectl logs api-7d4f --previous"),
  ("<b>kubectl logs</b> -l app=api --max-log-requests=10", "Aggregate logs across pods by label", "kubectl logs -l app=api --tail=50 --prefix"),
  ("<b>kubectl logs</b> --since=15m --timestamps", "Time-bounded, with timestamps", "kubectl logs api-7d4f --since=15m --timestamps"),
  ("<b>kubectl exec</b> -it -- sh", "Shell in a running container", "kubectl exec -it api-7d4f -c api -- sh"),
  ("<b>kubectl debug</b> -it --image=nicolaka/netshoot", "Attach an ephemeral container with real tools", "kubectl debug -it api-7d4f --image=nicolaka/netshoot --target=api"),
  ("<b>kubectl debug</b> node/NAME -it --image=ubuntu", "A privileged pod on a node, with its root at /host", "kubectl debug node/worker-3 -it --image=ubuntu"),
  ("<b>kubectl run</b> tmp --rm -it --image=busybox -- sh", "Throwaway pod for a quick test", "kubectl run tmp --rm -it --image=busybox --restart=Never -- sh"),
  ("<b>kubectl port-forward</b>", "Reach a pod or service from your laptop", "kubectl port-forward svc/api 8080:80"),
  ("<b>kubectl cp</b>", "Copy files in or out of a container", "kubectl cp api-7d4f:/tmp/heap.hprof ./heap.hprof"),
  ("<b>kubectl attach</b> -it", "Attach to PID 1's stdio, rather than starting a new process", "kubectl attach -it api-7d4f"),
 ]),

 ("roll", "Rollouts & scaling", "A rollout is a new ReplicaSet gradually taking over from the old "
  "one. <code>rollout status</code> blocks until it settles, which makes it usable in CI.", [
  ("<b>kubectl rollout status</b> --timeout=5m", "Wait for a rollout, fail the pipeline if it stalls", "kubectl rollout status deploy/api --timeout=5m"),
  ("<b>kubectl rollout history</b>", "Revisions, with the change-cause annotation", "kubectl rollout history deploy/api"),
  ("<b>kubectl rollout undo</b> --to-revision=3", "Roll back to a specific revision", "kubectl rollout undo deploy/api --to-revision=3"),
  ("<b>kubectl rollout restart</b>", "Restart every pod without changing the spec — picks up new secrets", "kubectl rollout restart deploy/api"),
  ("<b>kubectl rollout pause</b> / <b>resume</b>", "Hold a rollout mid-flight to inspect it", "kubectl rollout pause deploy/api"),
  ("<b>kubectl scale</b> --replicas=0", "Scale to zero and back — the crudest restart", "kubectl scale deploy/api --replicas=0"),
  ("<b>kubectl autoscale</b> --min --max --cpu-percent", "Create an HPA imperatively", "kubectl autoscale deploy/api --min=2 --max=10 --cpu-percent=70"),
  ("<b>kubectl wait</b> --for=condition=Ready", "Block until a condition holds — for scripts", "kubectl wait --for=condition=Ready po -l app=api --timeout=120s"),
 ]),

 ("node", "Nodes & scheduling", "Draining is two steps: cordon stops new pods, drain evicts the "
  "existing ones respecting PodDisruptionBudgets.", [
  ("<b>kubectl get no</b> -o wide", "Nodes with version, OS image and kernel", "kubectl get no -o wide"),
  ("<b>kubectl describe no</b> NAME", "Conditions, allocatable, and what is already on it", "kubectl describe no worker-3"),
  ("<b>kubectl cordon</b> / <b>uncordon</b>", "Stop / resume scheduling onto a node", "kubectl cordon worker-3"),
  ("<b>kubectl drain</b> --ignore-daemonsets --delete-emptydir-data", "Evict everything before maintenance", "kubectl drain worker-3 --ignore-daemonsets --delete-emptydir-data"),
  ("<b>kubectl taint no</b> key=value:NoSchedule", "Repel pods that lack the matching toleration", "kubectl taint no worker-3 gpu=true:NoSchedule"),
  ("<b>kubectl get po</b> --field-selector spec.nodeName=X", "What is running on one node", "kubectl get po -A --field-selector spec.nodeName=worker-3"),
  ("<b>kubectl describe no</b> | grep -A5 Allocated", "How much of the node is already requested", "kubectl describe no worker-3 | grep -A6 'Allocated resources'"),
 ]),

 ("ctx", "Contexts, config & access", "<code>kubectl config</code> edits your kubeconfig; "
  "<code>auth can-i</code> answers RBAC questions without trial and error.", [
  ("<b>kubectl config get-contexts</b>", "Every cluster you can reach, and which is current", "kubectl config get-contexts"),
  ("<b>kubectl config use-context</b>", "Switch cluster", "kubectl config use-context prod-eu"),
  ("<b>kubectl config set-context --current --namespace=</b>", "Stop typing -n on every command", "kubectl config set-context --current --namespace=payments"),
  ("<b>kubectl auth can-i</b> --list", "Everything the current identity may do here", "kubectl auth can-i --list -n payments"),
  ("<b>kubectl auth can-i</b> delete po --as=", "Check another user's or service account's rights", "kubectl auth can-i delete po --as=system:serviceaccount:ci:deployer"),
  ("<b>kubectl auth whoami</b>", "Which identity the API server sees", "kubectl auth whoami"),
  ("<b>kubectl get</b> secret NAME -o jsonpath='{.data.k}' | base64 -d", "Read one key out of a secret", "kubectl get secret db -o jsonpath='{.data.password}' | base64 -d"),
 ]),

 ("out", "Output & scripting", "Everything above becomes automatable with the right -o. "
  "<code>jsonpath</code> for one value, <code>-o json | jq</code> for anything complex.", [
  ("<b>-o jsonpath</b>='{.items[*].metadata.name}'", "Pull specific fields", "kubectl get po -o jsonpath='{.items[*].spec.nodeName}'"),
  ("<b>-o custom-columns</b>=", "Build your own table", "kubectl get po -o custom-columns=NAME:.metadata.name,NODE:.spec.nodeName"),
  ("<b>-o yaml</b> / <b>-o json</b>", "The full object as the API server holds it", "kubectl get deploy api -o yaml"),
  ("<b>--no-headers</b>", "Machine-readable output for a pipeline", "kubectl get po --no-headers | wc -l"),
  ("<b>-w</b> / <b>--watch</b>", "Stream changes as they happen", "kubectl get po -w"),
  ("<b>kubectl get</b> --raw /metrics", "Hit an API server endpoint directly", "kubectl get --raw /readyz?verbose"),
  ("<b>kubectl kustomize</b> dir/", "Render a kustomization without applying it", "kubectl kustomize overlays/prod | less"),
  ("<b>kubectl</b> … <b>--v=8</b>", "Log every HTTP request kubectl makes — the debugging escape hatch", "kubectl get po --v=8"),
 ]),
])


# ═══════════════════════════════════════════════════════════════════════════
DOCKER = dict(
    slug="docker-commands", icon="🐳", title="Docker Commands",
    tagline=("Running, building, inspecting and cleaning up — plus the flags that keep a laptop "
             "from filling with dead layers."),
    groups=[
 ("run", "Running containers", "<code>run</code> is <code>create</code> plus <code>start</code>. "
  "<code>--rm</code> on anything interactive, or you accumulate stopped containers forever.", [
  ("<b>docker run</b> --rm -it", "Interactive, removed on exit", "docker run --rm -it ubuntu bash"),
  ("<b>docker run</b> -d --name", "Detached, with a name you can refer to", "docker run -d --name web nginx"),
  ("<b>docker run</b> -p 8080:80", "Publish host:container. Add 127.0.0.1: to avoid exposing it", "docker run -p 127.0.0.1:8080:80 nginx"),
  ("<b>docker run</b> -v $PWD:/app:ro", "Bind-mount, read-only", "docker run -v $PWD:/app:ro node npm test"),
  ("<b>docker run</b> -e / --env-file", "Environment variables", "docker run --env-file .env api"),
  ("<b>docker run</b> --memory=512m --cpus=1.5", "Resource limits — the cgroup settings", "docker run --memory=512m --cpus=1.5 api"),
  ("<b>docker run</b> --init", "Real init as PID 1 — reaps zombies, forwards signals", "docker run --init api"),
  ("<b>docker run</b> -u $(id -u):$(id -g)", "Run as your UID so bind-mounted files aren't root-owned", "docker run -u $(id -u):$(id -g) -v $PWD:/w node"),
  ("<b>docker run</b> --read-only --tmpfs /tmp", "Immutable root filesystem with writable /tmp", "docker run --read-only --tmpfs /tmp api"),
  ("<b>docker run</b> --restart=unless-stopped", "Restart on failure and on boot, but honour a manual stop", "docker run -d --restart=unless-stopped api"),
  ("<b>docker start</b> / <b>stop</b> / <b>restart</b>", "Lifecycle of an existing container", "docker stop -t 30 web"),
 ]),

 ("build", "Images & building", "Layers are cached in order, so the least-changing steps go first. "
  "Copying source before installing dependencies invalidates the cache on every edit.", [
  ("<b>docker build</b> -t name:tag .", "Build and tag", "docker build -t api:v2 ."),
  ("<b>docker build</b> --target", "Stop at a named stage of a multi-stage build", "docker build --target test -t api:test ."),
  ("<b>docker build</b> --no-cache", "Ignore the layer cache", "docker build --no-cache -t api:v2 ."),
  ("<b>docker build</b> --build-arg", "Pass a build-time variable", "docker build --build-arg VERSION=2.1 -t api ."),
  ("<b>docker build</b> --platform linux/amd64", "Cross-build — routine on Apple silicon", "docker build --platform linux/amd64 -t api ."),
  ("<b>docker buildx build</b> --push --platform a,b", "Multi-arch image, built and pushed in one step", "docker buildx build --platform linux/amd64,linux/arm64 -t repo/api:v2 --push ."),
  ("<b>docker images</b> --filter dangling=true", "Untagged layers left by rebuilds", "docker images --filter dangling=true"),
  ("<b>docker history</b>", "Every layer and what it cost — finds the fat one", "docker history api:v2"),
  ("<b>docker tag</b> / <b>docker push</b>", "Retag for a registry and upload", "docker tag api:v2 repo/api:v2 &amp;&amp; docker push repo/api:v2"),
  ("<b>docker save</b> / <b>load</b>", "Move an image without a registry", "docker save api:v2 | gzip &gt; api.tgz"),
 ]),

 ("look", "Inspecting & logs", "<code>inspect</code> returns the full JSON; the <code>-f</code> "
  "Go template pulls out one value without piping through jq.", [
  ("<b>docker ps</b> -a", "All containers, including stopped ones", "docker ps -a"),
  ("<b>docker ps</b> --filter status=exited", "Filter by state, name, label or ancestor", "docker ps --filter 'status=exited'"),
  ("<b>docker ps</b> --format 'table {{.Names}}\\t{{.Status}}'", "Only the columns you want", "docker ps --format 'table {{.Names}}\\t{{.Status}}'"),
  ("<b>docker logs</b> -f --tail 100", "Follow the last 100 lines", "docker logs -f --tail 100 web"),
  ("<b>docker logs</b> --since 10m -t", "Time-bounded with timestamps", "docker logs --since 10m -t web"),
  ("<b>docker inspect</b> -f '{{.State.Pid}}'", "One field out of the JSON", "docker inspect -f '{{.State.Pid}}' web"),
  ("<b>docker inspect</b> -f '{{.State.OOMKilled}}'", "Was it killed for memory?", "docker inspect -f '{{.State.OOMKilled}}' api"),
  ("<b>docker stats</b> --no-stream", "CPU, memory and I/O per container, once", "docker stats --no-stream"),
  ("<b>docker exec</b> -it", "Shell in a running container", "docker exec -it web sh"),
  ("<b>docker top</b>", "Processes inside a container, from the host's view", "docker top web"),
  ("<b>docker diff</b>", "What changed in the container's filesystem since it started", "docker diff web"),
  ("<b>docker cp</b>", "Copy files in or out — works on stopped containers too", "docker cp web:/etc/nginx/nginx.conf ."),
 ]),

 ("net", "Networking & volumes", "The default bridge has no DNS between containers. A user-defined "
  "network does, which is why compose creates one.", [
  ("<b>docker network ls</b>", "Networks that exist", "docker network ls"),
  ("<b>docker network create</b>", "A user-defined bridge — gives you container-name DNS", "docker network create appnet"),
  ("<b>docker network connect</b>", "Attach a running container to another network", "docker network connect appnet web"),
  ("<b>docker network inspect</b>", "Subnet, gateway and which containers are attached", "docker network inspect appnet"),
  ("<b>docker run</b> --network=host", "Share the host's network namespace. Linux only", "docker run --network=host api"),
  ("<b>docker volume create</b> / <b>ls</b>", "Named volumes — managed, unlike bind mounts", "docker volume create pgdata"),
  ("<b>docker volume inspect</b>", "Where a volume actually lives on the host", "docker volume inspect pgdata"),
  ("<b>docker run</b> -v pgdata:/var/lib/postgresql/data", "Mount a named volume", "docker run -v pgdata:/var/lib/postgresql/data postgres"),
  ("<b>docker run</b> --mount type=bind,src=,dst=,ro", "Explicit form; fails loudly if the source is missing", "docker run --mount type=bind,src=$PWD,dst=/app,ro node"),
 ]),

 ("compose", "Compose", "Compose v2 is <code>docker compose</code> — a subcommand, not the old "
  "<code>docker-compose</code> binary.", [
  ("<b>docker compose up</b> -d", "Start the stack detached", "docker compose up -d"),
  ("<b>docker compose up</b> --build --force-recreate", "Rebuild images and recreate containers", "docker compose up -d --build"),
  ("<b>docker compose down</b> -v", "Stop and remove, including named volumes. Destroys data", "docker compose down -v"),
  ("<b>docker compose logs</b> -f svc", "Follow one service", "docker compose logs -f api"),
  ("<b>docker compose ps</b>", "Status of the stack's containers", "docker compose ps"),
  ("<b>docker compose exec</b>", "Shell into a service by its compose name", "docker compose exec db psql -U app"),
  ("<b>docker compose config</b>", "Render the final merged config — resolves every override and var", "docker compose config"),
  ("<b>docker compose -f a.yml -f b.yml</b>", "Layer an override file over a base", "docker compose -f compose.yml -f compose.prod.yml up -d"),
  ("<b>docker compose run</b> --rm svc cmd", "One-off command in a service's environment", "docker compose run --rm api pytest"),
 ]),

 ("clean", "Cleanup", "Docker never reclaims anything on its own. On a build host this is the "
  "difference between a working disk and a 3am page.", [
  ("<b>docker system df</b>", "What is using the space, by category", "docker system df -v"),
  ("<b>docker system prune</b>", "Stopped containers, unused networks, dangling images, build cache", "docker system prune"),
  ("<b>docker system prune</b> -a --volumes", "Everything not currently in use. Read that twice", "docker system prune -a --volumes"),
  ("<b>docker image prune</b> -a --filter 'until=168h'", "Images unused for a week — a safe cron job", "docker image prune -a --filter 'until=168h' -f"),
  ("<b>docker builder prune</b>", "Build cache only, leaving images alone", "docker builder prune --keep-storage 10GB"),
  ("<b>docker volume prune</b>", "Volumes no container references. Check before running", "docker volume ls -f dangling=true"),
  ("<b>docker container prune</b>", "Stopped containers only", "docker container prune -f"),
  ("<b>docker rm</b> -f $(docker ps -aq)", "Remove every container, running or not", "docker rm -f $(docker ps -aq)"),
 ]),
])

ALL = [LINUX, KUBECTL, DOCKER]
