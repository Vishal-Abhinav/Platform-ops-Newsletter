#!/usr/bin/env python3
"""Foundation content, batch A: Computer Fundamentals, Operating Systems."""
import os, pathlib as _pl
ROOT = _pl.Path(os.environ.get("PO_ROOT") or _pl.Path(__file__).resolve().parent.parent)
TOOLS = ROOT / "tools"

from content_page import card, term, table, note, diagram, section

# ═══════════════════════════════════════════════════════════════════════════
# 01 · COMPUTER FUNDAMENTALS
# ═══════════════════════════════════════════════════════════════════════════
CF_DIAGRAM = diagram([
    ("Software", [("Your process", "core"), ("Libraries / runtime", "core"),
                  ("System calls", "warm")]),
    ("Kernel", [("Scheduler", "warm"), ("Virtual memory", "warm"),
                ("Block layer", "warm"), ("Net stack", "warm")]),
    ("Translation", [("MMU + TLB", "calm"), ("Page tables", "calm"),
                     ("IOMMU / DMA", "calm")]),
    ("Cache", [("L1d / L1i ~1 ns", "go"), ("L2 ~4 ns", "go"),
               ("L3 shared ~20-40 ns", "go")]),
    ("Memory", [("DRAM ~80-100 ns", "hot"), ("NUMA remote +50%", "hot")]),
    ("Storage", [("NVMe ~20-100 µs", "plain"), ("SATA SSD ~150 µs", "plain"),
                 ("HDD ~5-10 ms", "plain")]),
    ("Network", [("Same rack ~0.1 ms", "plain"), ("Same region ~1 ms", "plain"),
                 ("Cross-continent ~100 ms", "plain")]),
], "The latency pyramid — every layer roughly an order of magnitude slower than the one above")

CF_CORE = "".join([
 card(1, "The execution model", "Fetch, decode, execute — and why the CPU is almost never doing just that.",
      ["pipeline", "IPC", "branch prediction"], """
<p>A modern core does not execute your instructions one at a time in order. It runs a
<strong>deep pipeline</strong> — typically 14–20 stages — with several instructions in flight
at once, issues them <strong>out of order</strong>, executes speculatively past branches, and
retires them back in program order so the result looks sequential.</p>
<p>That matters operationally because it decouples <em>clock speed</em> from <em>work done</em>.
The number you actually care about is <strong>IPC — instructions per cycle</strong>. A core at
3 GHz with IPC 0.4 is doing less work than one at 2 GHz with IPC 1.8. When a service gets slower
after a deploy and CPU utilisation looks identical, IPC is usually where the answer is: the code
started missing cache, and the core is spending its cycles stalled rather than retiring work.</p>
<h3>What actually stalls a core</h3>
<ul>
<li><strong>Cache misses</strong> — the biggest one. A last-level miss costs ~200–300 cycles of
doing nothing useful.</li>
<li><strong>Branch mispredictions</strong> — the pipeline is flushed and refilled, ~15–20 cycles.
Unpredictable branches in a hot loop are expensive.</li>
<li><strong>Dependency chains</strong> — instruction N+1 needs N's result, so out-of-order
execution has nothing else to run.</li>
</ul>
""" + term("measuring it rather than guessing", [
    ("$", "perf stat -e cycles,instructions,cache-misses,branch-misses ./app"),
    ("", "     41,238,551,102      cycles"),
    ("", "     18,442,190,338      instructions   #  0.45  insn per cycle"),
    ("", "        891,204,116      cache-misses"),
    ("", "         92,441,003      branch-misses"),
    ("#", "IPC 0.45 on a workload that should be compute-bound = memory-bound in disguise"),
])),

 card(2, "Memory hierarchy and the cache line", "Why 64 bytes is the most important number in performance work.",
      ["cache line", "locality", "false sharing"], """
<p>The CPU never reads one byte from RAM. It reads a <strong>cache line</strong> — 64 bytes on
every x86-64 and most ARM64 parts — and everything in that line comes along for free. This single
fact drives most of the performance difference between two implementations of the same algorithm.</p>
<p>Walking an array of structs sequentially is fast because each miss pulls in the next several
elements. Chasing pointers through a linked list is slow because every hop is a fresh miss with
nothing useful alongside it — the same O(n) traversal can differ by 10× in wall time.</p>
<h3>The two localities</h3>
<ul>
<li><strong>Temporal</strong> — you touched it recently, so it's probably still cached. Loop
counters, hot config, the top of a call stack.</li>
<li><strong>Spatial</strong> — you touched the neighbour, so it's already in the line. Arrays,
struct fields accessed together, contiguous file reads.</li>
</ul>
""" + note("trap", "False sharing", """
<p style="margin:0">Two threads on two cores writing to <em>different</em> variables that happen
to sit in the same 64-byte line will serialise on the cache-coherence protocol as if they shared
one variable. Throughput collapses and nothing in the code looks wrong. The fix is padding —
align hot per-thread counters to their own line. This shows up constantly in metrics libraries
and lock-free queues.</p>""")),

 card(3, "Virtual memory, the MMU and the TLB", "Every address your process sees is a lie the hardware maintains.",
      ["paging", "TLB", "huge pages"], """
<p>Your process sees a flat virtual address space. The <strong>MMU</strong> translates each virtual
address to a physical one by walking <strong>page tables</strong> — four levels on x86-64, so an
untranslated access could cost four extra memory reads. The <strong>TLB</strong> caches recent
translations to avoid that walk; it holds only a few thousand entries.</p>
<p>With a 4 KiB page and ~1,500 TLB entries, a core can cover roughly 6 MB of memory before it
starts missing the TLB on every access. A process with a 40 GB working set that jumps around
randomly will spend a startling fraction of its time walking page tables.</p>
<h3>Huge pages</h3>
<p>A 2 MiB page covers 512× more memory per TLB entry. For databases, JVMs with large heaps, and
anything with a big random-access working set, huge pages can be a double-digit-percent win.
Transparent Huge Pages (THP) does it automatically — and is also a classic latency culprit,
because the compaction it does to find contiguous memory stalls the process that triggered it.
Most database vendors tell you to turn THP off and use explicit hugepages instead. They are
right, for that workload.</p>
""" + term("checking translation pressure", [
    ("$", "perf stat -e dTLB-load-misses,dTLB-loads ./app"),
    ("$", "cat /sys/kernel/mm/transparent_hugepage/enabled"),
    ("", "[always] madvise never"),
    ("#", "databases usually want: madvise (or never), never always"),
    ("$", "grep -i huge /proc/meminfo"),
])),

 card(4, "The storage stack", "Six orders of magnitude between the fastest and slowest thing you'll wait on.",
      ["NVMe", "queue depth", "IOPS vs latency"], """
<p>Storage is where the latency pyramid gets steep. An NVMe read is roughly a thousand times slower
than DRAM; a spinning disk seek is a hundred thousand times slower. Any design decision that turns
a memory access into a disk access is worth a hundred micro-optimisations elsewhere.</p>
<h3>IOPS and latency are not the same problem</h3>
<p>An NVMe device advertising 800k IOPS achieves that at <strong>high queue depth</strong> — many
requests in flight at once. A single-threaded process issuing one synchronous read at a time gets
device latency, not device throughput: maybe 12k IOPS from the same hardware. If your benchmark
says the disk is fine and your application says it isn't, queue depth is usually the gap.</p>
""" + table(["Layer", "Typical latency", "What it means in practice"], [
    ["L1 cache", "~1 ns", "Effectively free. 4 cycles."],
    ["L3 cache", "~20–40 ns", "Shared across cores; contention shows here first."],
    ["DRAM (local)", "~80–100 ns", "~250 cycles of doing nothing."],
    ["DRAM (remote NUMA)", "~130–160 ns", "50%+ penalty for crossing a socket."],
    ["NVMe read", "~20–100 µs", "~1,000× DRAM. Queue depth decides throughput."],
    ["SATA SSD read", "~100–200 µs", "Fine for most things, not for a hot index."],
    ["HDD seek + read", "~5–10 ms", "~100,000× DRAM. Sequential only, or don't."],
    ["Same-rack RTT", "~0.1–0.2 ms", "Cheaper than a disk seek. Design accordingly."],
    ["Cross-region RTT", "~50–150 ms", "Physics. No amount of tuning fixes light speed."],
], "mono")),
])

CF_ADV = "".join([
 card(5, "NUMA — when 'the RAM' is several different RAMs", "Two sockets means two memory controllers, and the wrong one costs you 50%.",
      ["NUMA", "numactl", "interleave"], """
<p>On a multi-socket server, each CPU package has its own memory controller and its own directly
attached DRAM. Accessing memory on the other socket goes across the interconnect and costs
roughly 1.5× the latency and less bandwidth. The kernel tries to allocate memory on the node where
the allocating thread runs — but if the scheduler later migrates that thread, every access becomes
remote.</p>
<p>This is why large single-process databases are usually pinned. It's also why a container without
CPU affinity can show 30% variance run to run on the same hardware for no visible reason.</p>
""" + term("seeing and fixing NUMA placement", [
    ("$", "lscpu | grep -i numa"),
    ("", "NUMA node(s):          2"),
    ("", "NUMA node0 CPU(s):     0-23,48-71"),
    ("", "NUMA node1 CPU(s):     24-47,72-95"),
    ("$", "numastat -p $(pgrep -f postgres | head -1)"),
    ("#", "high 'other_node' means the process is reaching across the interconnect"),
    ("$", "numactl --cpunodebind=0 --membind=0 ./latency-sensitive-thing"),
    ("#", "or interleave when the working set genuinely exceeds one node:"),
    ("$", "numactl --interleave=all ./big-heap-thing"),
])),

 card(6, "Interrupts, DMA and IRQ affinity", "How data actually gets from a NIC into your socket buffer.",
      ["IRQ", "DMA", "RSS", "softirq"], """
<p>A NIC receiving a packet does not interrupt the CPU for each byte. It <strong>DMAs</strong> the
frame straight into a ring buffer in RAM, then raises one interrupt to say "there is work". The
kernel's top half acknowledges it fast and defers the real processing to a <strong>softirq</strong>,
which is where most of the network stack actually runs.</p>
<p>Under load the kernel switches to <strong>NAPI polling</strong> — interrupts off, poll the ring
— because at a million packets per second, interrupt overhead alone would consume the machine.</p>
<h3>Where this bites in production</h3>
<p>By default all NIC interrupts may land on CPU 0. One core saturates handling softirqs while 47
others idle, and your throughput ceiling has nothing to do with your application. <strong>RSS</strong>
(receive-side scaling) spreads flows across multiple queues, and IRQ affinity pins each queue to a
core — ideally one on the same NUMA node as the NIC.</p>
""" + term("diagnosing a single-core softirq bottleneck", [
    ("$", "mpstat -P ALL 1 | head -20"),
    ("#", "one CPU at 100% %soft while the rest idle = classic IRQ pinning problem"),
    ("$", "cat /proc/interrupts | grep -E 'eth0|ens'"),
    ("$", "cat /proc/softirqs | head -3"),
    ("$", "ethtool -l ens5          # how many RX queues does the NIC have?"),
    ("$", "ethtool -L ens5 combined 16"),
    ("#", "then let irqbalance spread them, or pin by hand:"),
    ("$", "echo 2 > /proc/irq/142/smp_affinity_list"),
])),

 card(7, "Context switches and what they really cost", "The direct cost is a microsecond. The indirect cost is your cache.",
      ["context switch", "cache pollution", "scheduling"], """
<p>Saving registers and swapping page tables takes roughly <strong>1–5 µs</strong>. That number
is misleading, because the expensive part is what happens afterwards: the incoming process finds
the L1 and L2 caches full of the outgoing process's data, and the TLB partly flushed. It runs
slowly for tens of microseconds while it re-warms.</p>
<p>A machine doing 200k context switches per second is not spending 20% of its time in the switch
code — it is spending far more than that running cold. This is the real argument for CPU pinning
on latency-sensitive services, and the reason thread-per-request models fall over at high
concurrency while event loops don't.</p>
""" + term("is switching the problem?", [
    ("$", "vmstat 1 5"),
    ("", "procs -----------memory----------  ---system--- ------cpu-----"),
    ("", " r  b   swpd   free   buff  cache    in     cs   us sy id wa st"),
    ("", " 8  0      0 2104832 189232 8814720  48219 241883  62 31  6  1  0"),
    ("#", "cs 241k/s with sy 31% — the kernel is busier than the application"),
    ("$", "pidstat -w -p $(pgrep -f myapp) 1"),
    ("#", "cswch/s = voluntary (waiting on I/O or a lock)"),
    ("#", "nvcswch/s = involuntary (preempted — too many runnable threads)"),
])),

 card(8, "Numbers worth memorising", "Order-of-magnitude intuition beats a profiler you haven't run yet.",
      ["latency", "estimation", "capacity"], """
<p>You will make a hundred design decisions before you ever profile anything. Rough magnitudes are
what keep those decisions sane — and they are stable, because they are set by physics and by
hardware generations, not by your code.</p>
<ul>
<li><strong>A cache miss to DRAM is ~250 cycles.</strong> If a hot loop misses every iteration,
you have a memory problem, not a CPU problem.</li>
<li><strong>An NVMe read is ~1,000× a DRAM read.</strong> Caching a value that costs a disk read
is worth doing even if the cache hit rate is only 50%.</li>
<li><strong>A same-region network round trip is cheaper than an HDD seek.</strong> A remote cache
can genuinely be faster than local spinning disk.</li>
<li><strong>Cross-region is ~100 ms and unfixable.</strong> Any design with N sequential
cross-region calls has an N × 100 ms floor. Batch them or move the compute.</li>
<li><strong>1 Gbps is 125 MB/s.</strong> Divide bits by eight before promising anyone a transfer
window.</li>
</ul>
"""),
])

CF_PRACTICE = """
<p>Three commands that tell you what kind of machine you are actually on, before you tune anything
on it. Run them on any box you are about to make promises about.</p>
""" + term("machine inventory in ninety seconds", [
    ("$", "lscpu"),
    ("", "Architecture:        x86_64"),
    ("", "CPU(s):              96      Thread(s) per core: 2      Core(s) per socket: 24"),
    ("", "Socket(s):           2       NUMA node(s):       2"),
    ("", "L1d cache: 32K   L1i cache: 32K   L2 cache: 1024K   L3 cache: 36864K"),
    ("#", "96 'CPUs' is 48 physical cores. Capacity plan on cores, not threads."),
    ("", ""),
    ("$", "lsblk -o NAME,ROTA,SIZE,MODEL,SCHED"),
    ("", "NAME   ROTA   SIZE MODEL              SCHED"),
    ("", "nvme0n1   0   1.8T Samsung PM9A3      none"),
    ("#", "ROTA=0 is solid state. SCHED=none is correct for NVMe — the device"),
    ("#", "reorders better than the kernel can, and mq-deadline just adds latency."),
    ("", ""),
    ("$", "ethtool ens5 | grep -E 'Speed|Duplex'"),
    ("", "Speed: 25000Mb/s"),
    ("#", "25 Gbps = 3.1 GB/s. Now you know the ceiling before you design around it."),
]) + note("tip", "The one-minute rule", """
<p style="margin:0">Before optimising anything, establish which of the four resources you are out
of: CPU cycles, memory bandwidth, I/O, or network. <code>perf stat</code> answers the first two,
<code>iostat -x 1</code> the third, <code>sar -n DEV 1</code> the fourth. Guessing wrong costs a
week; measuring costs a minute.</p>""")

CF_CHEAT = table(["Command", "What it tells you"], [
    ["<code>lscpu</code>", "Cores, sockets, NUMA nodes, cache sizes, flags"],
    ["<code>lstopo --of txt</code>", "Full topology map — which core shares which cache"],
    ["<code>numactl --hardware</code>", "NUMA nodes, memory per node, inter-node distances"],
    ["<code>numastat -p PID</code>", "Local vs remote memory hits for one process"],
    ["<code>perf stat -e cycles,instructions CMD</code>", "IPC — cycles actually spent retiring work"],
    ["<code>perf stat -e cache-misses,LLC-load-misses CMD</code>", "Whether you are memory-bound"],
    ["<code>perf top</code>", "Live symbol-level view of where cycles go"],
    ["<code>vmstat 1</code>", "Context switches, interrupts, run queue, swap activity"],
    ["<code>pidstat -w -p PID 1</code>", "Voluntary vs involuntary switches for one process"],
    ["<code>mpstat -P ALL 1</code>", "Per-CPU breakdown — finds the one saturated core"],
    ["<code>cat /proc/interrupts</code>", "Which CPU is servicing which device"],
    ["<code>iostat -x 1</code>", "Per-device await, queue depth, utilisation"],
    ["<code>lsblk -o NAME,ROTA,SCHED</code>", "Rotational or not, and the I/O scheduler in use"],
    ["<code>dmidecode -t memory</code>", "DIMM population, speed, channel layout"],
    ["<code>getconf LEVEL1_DCACHE_LINESIZE</code>", "Cache line size — 64 on anything you'll meet"],
], "mono")

COMPUTER_FUNDAMENTALS = dict(
    slug="computer-fundamentals",
    title="Computer Fundamentals",
    tagline=("What the hardware is actually doing underneath your process — caches, translation, "
             "interrupts and the six orders of magnitude between L1 and a disk seek."),
    eyebrow="Foundation · Core",
    meta=["<b>22 min</b> read", "Level: <b>core → advanced</b>", "Foundation <b>01 / 10</b>"],
    sections=(
        section("The model", "THE LATENCY PYRAMID",
                "Every layer below is roughly an order of magnitude slower than the one above it. "
                "Most performance work is moving an access up this diagram.",
                f'<div class="dg-scroll">{CF_DIAGRAM}</div>'
                '<p class="dg-cap">The numbers are for a current x86-64 server. They move slowly — '
                'the ratios between layers have been stable for two decades, which is what makes '
                'them worth memorising.</p>')
        + section("Core", "CORE CONCEPTS",
                  "The four things that explain most of what you'll see on a production box.", CF_CORE)
        + section("Advanced", "ADVANCED",
                  "Where the simple model stops predicting what you measure.", CF_ADV)
        + section("In practice", "ON A REAL BOX", None, CF_PRACTICE)
        + section("Reference", "CHEATSHEET", None, CF_CHEAT)
    ),
)


# ═══════════════════════════════════════════════════════════════════════════
# 02 · OPERATING SYSTEMS
# ═══════════════════════════════════════════════════════════════════════════
OS_DIAGRAM = diagram([
    ("User space", [("Your process", "core"), ("libc / runtime", "core"),
                    ("Shared libs", "core"), ("vDSO", "go")]),
    ("The boundary", [("syscall instruction", "hot"), ("Trap → ring 0", "hot"),
                      ("seccomp filter", "warm")]),
    ("Kernel: process", [("Scheduler (EEVDF)", "warm"), ("task_struct", "warm"),
                         ("Signals", "warm"), ("cgroups", "calm"), ("namespaces", "calm")]),
    ("Kernel: memory", [("Virtual memory", "warm"), ("Page cache", "warm"),
                        ("Writeback", "warm"), ("OOM killer", "hot")]),
    ("Kernel: I/O", [("VFS", "warm"), ("Filesystem", "warm"),
                     ("Block layer", "warm"), ("Net stack", "warm")]),
    ("Drivers", [("Device drivers", "plain"), ("IRQ handlers", "plain")]),
    ("Hardware", [("CPU / MMU", "plain"), ("RAM", "plain"),
                  ("Disk", "plain"), ("NIC", "plain")]),
], "From a process call to hardware, and the kernel subsystems in between")

OS_CORE = "".join([
 card(1, "The user / kernel boundary", "One instruction, one privilege change, and the only door between the two worlds.",
      ["syscall", "ring 0", "vDSO"], """
<p>Your process runs in <strong>user mode</strong> and cannot touch hardware, other processes'
memory, or the page tables. Everything it needs from the outside world goes through a
<strong>system call</strong>: it puts a number in <code>rax</code>, arguments in registers, and
executes the <code>syscall</code> instruction. The CPU switches to <strong>ring 0</strong>, jumps
to a fixed kernel entry point, and the kernel does the work on the process's behalf.</p>
<p>The base cost is roughly 50–100 ns, meaningfully more since Spectre/Meltdown mitigations added
page-table isolation. That is cheap once and ruinous a million times a second — which is the entire
reason <code>io_uring</code>, batched writes and buffered I/O exist.</p>
<h3>The vDSO shortcut</h3>
<p>Some calls don't need the kernel at all. <code>gettimeofday()</code> and
<code>clock_gettime()</code> are served from the <strong>vDSO</strong> — a small shared page the
kernel maps into every process, containing data the kernel keeps updated. The call becomes an
ordinary function call at a few nanoseconds instead of a trap. If you ever wonder why timestamping
every log line is affordable, this is why.</p>
""" + term("watching the boundary", [
    ("$", "strace -c -p 4412"),
    ("", "% time     seconds  usecs/call     calls    errors syscall"),
    ("", "------ ----------- ----------- --------- --------- ----------------"),
    ("", " 61.28    2.914021           3    971340           futex"),
    ("", " 22.10    1.050882           2    525441           epoll_wait"),
    ("", "  9.44    0.448911           4    112228           write"),
    ("#", "971k futex calls means lock contention, not I/O. Look at the locking,"),
    ("#", "not the disk — strace -c is the fastest way to find that out."),
])),

 card(2, "Processes, threads and what the scheduler sees", "The kernel does not really distinguish them. That explains a lot.",
      ["task_struct", "clone", "EEVDF"], """
<p>Linux schedules <strong>tasks</strong>. A process and a thread are both a
<code>task_struct</code>; the only difference is how much they share. <code>fork()</code> creates a
task with a copy of the address space, <code>clone()</code> with <code>CLONE_VM</code> creates one
that shares it. "Thread" is a userspace word for a task that shares memory with its siblings.</p>
<h3>Copy-on-write fork</h3>
<p><code>fork()</code> does not copy your 8 GB heap. It marks every page read-only in both parent
and child and copies a page only when one of them writes to it. This is why forking a large process
is fast — and why a forked child can still trigger an out-of-memory kill minutes later, when the
writes finally arrive. Redis's background save is the canonical example.</p>
<h3>The scheduler</h3>
<p>Since kernel 6.6 the default is <strong>EEVDF</strong> (Earliest Eligible Virtual Deadline
First), replacing CFS. Both are fair-share designs: each runnable task accrues virtual runtime,
and the one that has had least gets the CPU. EEVDF adds an explicit deadline so latency-sensitive
tasks can be served ahead of throughput-hungry ones rather than merely fairly.</p>
<p>What matters operationally is unchanged: <strong>fair-share means nobody is starved and nobody
is guaranteed</strong>. If you need a guarantee, you need <code>SCHED_FIFO</code>, cgroup CPU
bandwidth, or pinning — not a nice value.</p>
""" + table(["State", "In <code>ps</code>", "What it means"], [
    ["Running / runnable", "R", "On a CPU, or in the run queue waiting for one"],
    ["Interruptible sleep", "S", "Waiting on I/O or an event; signals wake it"],
    ["Uninterruptible sleep", "D", "In a kernel path that cannot be interrupted — usually disk or NFS. Persistent D state is a storage problem"],
    ["Stopped", "T", "SIGSTOP, or under a debugger"],
    ["Zombie", "Z", "Exited, but the parent hasn't called <code>wait()</code>. Harmless singly, a PID leak in bulk"],
], "mono")),

 card(3, "Virtual memory, the page cache and writeback", "Why 'free' memory is the least interesting number on the box.",
      ["page cache", "dirty pages", "RSS vs VSZ"], """
<p>The kernel uses every spare byte of RAM as <strong>page cache</strong> — a cache of file
contents. A box showing 200 MB free and 60 GB cached is not short of memory; it is doing exactly
what it should. Cache is reclaimable on demand. The number to watch is <code>available</code> in
<code>/proc/meminfo</code>, which accounts for that.</p>
<h3>Reading the memory columns</h3>
<ul>
<li><strong>VSZ</strong> — everything mapped, including memory never touched and files mapped but
not read. Nearly meaningless for capacity.</li>
<li><strong>RSS</strong> — resident pages, but shared pages are counted in full against every
process sharing them. Sum the RSS of 20 workers and you'll double-count libc twenty times.</li>
<li><strong>PSS</strong> — proportional set size; shared pages divided among sharers. This is the
number you want when asking "how much is this process really costing me".</li>
</ul>
<h3>Writeback</h3>
<p>A buffered write returns as soon as the page is marked dirty. Flushing happens later, governed
by <code>vm.dirty_ratio</code> and <code>vm.dirty_background_ratio</code>. When dirty pages exceed
<code>dirty_ratio</code>, writers are <strong>throttled synchronously</strong> — the application
stalls in the kernel until writeback catches up. On a box with lots of RAM and a slow disk, the
defaults let gigabytes accumulate and then stall everything at once. Lowering the ratios trades a
little throughput for far less latency variance.</p>
""" + term("reading memory honestly", [
    ("$", "free -h"),
    ("", "               total        used        free      shared  buff/cache   available"),
    ("", "Mem:            125Gi        48Gi       1.2Gi       892Mi        76Gi        75Gi"),
    ("#", "free 1.2Gi looks alarming; available 75Gi is the truth."),
    ("$", "grep -E 'Dirty|Writeback' /proc/meminfo"),
    ("", "Dirty:           4194304 kB"),
    ("#", "4 GB of dirty pages waiting on a disk that does 200 MB/s = a 20s stall"),
    ("$", "sysctl vm.dirty_ratio vm.dirty_background_ratio"),
    ("$", "grep Pss /proc/4412/smaps_rollup"),
])),

 card(4, "File descriptors, VFS and everything-is-a-file", "One integer, one abstraction, and the reason ulimits page you at 3am.",
      ["fd", "VFS", "ulimit", "epoll"], """
<p>A file descriptor is a small integer indexing a per-process table. Behind it the
<strong>VFS</strong> presents one interface — read, write, seek, close — over regular files,
sockets, pipes, devices, epoll instances, timers, even other processes' memory. That uniformity is
why <code>strace</code> is so useful: almost everything a process does is a read or a write to
some fd.</p>
<p>Descriptors are a hard-limited resource, and the limit is per-process, inherited at exec, and
usually far lower than people expect. A service that leaks one fd per request will run for hours
and then fail all at once with <code>EMFILE</code> — accept() starts failing while the process
looks perfectly healthy.</p>
""" + term("fd accounting", [
    ("$", "ls /proc/4412/fd | wc -l"),
    ("", "1021"),
    ("$", "cat /proc/4412/limits | grep 'open files'"),
    ("", "Max open files            1024                 1048576              files"),
    ("#", "soft limit 1024 and 1021 in use — this fails within the minute"),
    ("$", "ls -l /proc/4412/fd | awk '{print $NF}' | sort | uniq -c | sort -rn | head"),
    ("", "    847 socket:[8823191]"),
    ("#", "847 sockets: connections not being closed. Raising the limit buys"),
    ("#", "time; it does not fix a leak."),
])),
])

OS_ADV = "".join([
 card(5, "cgroups and namespaces — containers, demystified", "There is no such thing as a container. There are two kernel features.",
      ["cgroup v2", "namespaces", "containers"], """
<p>A container is a normal Linux process with two things done to it. <strong>Namespaces</strong>
change what it can see; <strong>cgroups</strong> limit what it can use. There is no container
object in the kernel, which is exactly why containers start in milliseconds and why a container
escape is a kernel bug rather than a hypervisor bug.</p>
<h3>The namespaces</h3>
<ul>
<li><strong>pid</strong> — its own PID 1 and process tree. Your process is 1 inside, 48122 outside.</li>
<li><strong>net</strong> — its own interfaces, routes, iptables rules, port space.</li>
<li><strong>mnt</strong> — its own mount table; the root filesystem it sees.</li>
<li><strong>uts</strong> — its own hostname.</li>
<li><strong>ipc</strong> — its own shared memory and semaphores.</li>
<li><strong>user</strong> — UID mapping; root inside, unprivileged outside. The one that makes
rootless containers possible.</li>
<li><strong>cgroup</strong> — hides the host's cgroup hierarchy from the process.</li>
</ul>
<h3>Why PID 1 matters inside</h3>
<p>PID 1 has special duties: it reaps orphaned children and it does not get default signal
handlers. Run an application as PID 1 without thinking about it and you get two classic bugs —
zombie processes accumulating because nothing reaps them, and <code>SIGTERM</code> being ignored
so every deploy waits the full termination grace period and then gets SIGKILLed. That is what
<code>--init</code> and tini exist to fix.</p>
""" + term("a container is just a process", [
    ("$", "docker run -d --name web --memory=512m nginx"),
    ("$", "docker inspect -f '{{.State.Pid}}' web"),
    ("", "48122"),
    ("$", "ls -l /proc/48122/ns/"),
    ("", "lrwxrwxrwx ... net -> 'net:[4026532281]'"),
    ("", "lrwxrwxrwx ... pid -> 'pid:[4026532283]'"),
    ("$", "cat /sys/fs/cgroup/system.slice/docker-*.scope/memory.max"),
    ("", "536870912"),
    ("#", "It's PID 48122 on the host, with different namespace inodes and a"),
    ("#", "cgroup memory ceiling. That is the entire trick."),
])),

 card(6, "The OOM killer and cgroup memory accounting", "Why your pod died and the node's memory graph looks fine.",
      ["OOM", "memory.max", "oom_score_adj"], """
<p>Two different OOM paths exist and they behave differently. <strong>Global OOM</strong> fires
when the whole machine is out and the kernel picks a victim by <code>oom_score</code> — roughly,
whoever is using the most, adjusted by <code>oom_score_adj</code>. <strong>cgroup OOM</strong>
fires when a single cgroup hits its <code>memory.max</code>, and kills something inside that cgroup
only. The host has plenty of free memory; the container still dies.</p>
<p>This is the entire explanation for the most confusing Kubernetes failure mode: a pod is OOMKilled
while the node's memory graph shows 40% used. The node was never the constraint. The container's
limit was.</p>
<h3>What counts against the limit</h3>
<p>Under cgroup v2, the charge includes anonymous memory <em>and</em> page cache the cgroup caused.
A process that reads a lot of files can be OOMKilled for cache it does not need and would happily
give back — the kernel does try to reclaim first, but a fast enough reader can outrun reclaim.
This is why a batch job that streams large files needs a limit well above its apparent working set.</p>
""" + term("post-mortem on a kill", [
    ("$", "dmesg -T | grep -i -A3 'killed process'"),
    ("", "[Wed Sep 10 04:12:08] Memory cgroup out of memory: Killed process 48901 (java)"),
    ("", "  total-vm:9812344kB, anon-rss:4103288kB, file-rss:18244kB"),
    ("#", "'Memory cgroup out of memory' — a limit, not the node."),
    ("$", "cat /sys/fs/cgroup/.../memory.events"),
    ("", "low 0"),
    ("", "high 2841"),
    ("", "max 19"),
    ("", "oom 3"),
    ("", "oom_kill 1"),
    ("#", "high 2841 = it was throttled under reclaim pressure 2841 times before"),
    ("#", "it died. That pressure was visible for a long time first."),
])),

 card(7, "Signals, and why your container ignores SIGTERM", "The default disposition changes for PID 1, and nobody tells you.",
      ["SIGTERM", "PID 1", "graceful shutdown"], """
<p>Signals are the kernel's interrupt mechanism for processes. Most have a default disposition:
<code>SIGTERM</code> terminates, <code>SIGKILL</code> terminates and cannot be caught,
<code>SIGSEGV</code> dumps core. A process can install a handler for anything except
<code>SIGKILL</code> and <code>SIGSTOP</code>.</p>
<p><strong>PID 1 is the exception.</strong> The kernel does not apply default dispositions to it.
A process running as PID 1 with no explicit <code>SIGTERM</code> handler simply ignores the signal.
Kubernetes sends SIGTERM, waits <code>terminationGracePeriodSeconds</code> (30 by default), then
SIGKILLs. If your entrypoint is the application itself and it has no handler, every single pod
deletion takes the full 30 seconds and ends in a hard kill — connections dropped, in-flight
requests lost, and a rolling deploy that takes half an hour.</p>
""" + note("trap", "Shell-form entrypoints swallow signals", """
<p style="margin:0"><code>ENTRYPOINT ./app</code> in shell form becomes <code>/bin/sh -c ./app</code>.
The shell is PID 1, your app is a child, and <code>sh</code> does not forward signals to it. Use
exec form — <code>ENTRYPOINT ["./app"]</code> — or <code>exec ./app</code> in your wrapper script.
This one line is behind a remarkable proportion of "why are deploys so slow" investigations.</p>""")
 + term("proving it", [
     ("$", "kubectl exec -it web -- ps -o pid,comm"),
     ("", "  PID COMMAND"),
     ("", "    1 sh"),
     ("", "    7 node"),
     ("#", "node is PID 7. SIGTERM goes to sh, which does nothing with it."),
     ("$", "time kubectl delete pod web"),
     ("", "pod \"web\" deleted"),
     ("", "real    0m30.4s"),
     ("#", "30 seconds every time = the grace period expiring, then SIGKILL"),
 ])),

 card(8, "I/O paths: buffered, direct, and io_uring", "Three ways to get bytes off a disk, with very different syscall bills.",
      ["io_uring", "O_DIRECT", "page cache"], """
<p><strong>Buffered I/O</strong> is the default: reads are served from page cache when possible,
writes return once dirty. Great throughput, unpredictable latency, and a copy between kernel and
user buffers on every call.</p>
<p><strong>Direct I/O</strong> (<code>O_DIRECT</code>) bypasses the page cache entirely and DMAs
straight into your buffer. Databases use it because they maintain a better cache than the kernel
can — they know which pages matter. It demands aligned buffers and aligned offsets, and it is
slower for anything that would have hit cache.</p>
<p><strong>io_uring</strong> replaces the syscall-per-operation model with two shared ring buffers
between userspace and kernel. You write submission entries into a ring, the kernel writes
completions into another, and with polling mode you can do sustained I/O with <em>zero</em>
syscalls. For anything issuing hundreds of thousands of operations a second, this is the
difference between spending 40% of your CPU in kernel entry overhead and spending almost none.</p>
""" + table(["Path", "Syscalls per op", "Page cache", "Use when"], [
    ["Buffered read/write", "1+", "Yes", "Almost everything. Default for a reason."],
    ["<code>mmap</code>", "0 after map", "Yes", "Random access to a file that fits in RAM; beware page-fault stalls"],
    ["<code>O_DIRECT</code>", "1+", "Bypassed", "You maintain your own cache — databases, mostly"],
    ["<code>io_uring</code>", "~0 (batched)", "Optional", "Very high IOPS, or many concurrent ops from few threads"],
])),
])

OS_PRACTICE = """
<p>A process is slow and you have sixty seconds. This is the order that finds the answer fastest,
because each step rules out an entire class of cause.</p>
""" + term("triage in four commands", [
    ("#", "1. Is it even running, or is it blocked?"),
    ("$", "ps -o pid,stat,wchan:20,comm -p 4412"),
    ("", "  PID STAT WCHAN                COMMAND"),
    ("", " 4412 D    io_schedule          postgres"),
    ("#", "D + io_schedule = blocked on disk. Stop looking at the CPU."),
    ("", ""),
    ("#", "2. What is it asking the kernel for?"),
    ("$", "strace -c -f -p 4412 -- sleep 10"),
    ("", ""),
    ("#", "3. Is the machine or the cgroup the constraint?"),
    ("$", "cat /sys/fs/cgroup/$(cut -d: -f3 /proc/4412/cgroup | tail -1)/memory.events"),
    ("$", "cat /sys/fs/cgroup/.../cpu.stat | grep throttled"),
    ("", "nr_throttled 88213"),
    ("", "throttled_usec 41028339"),
    ("#", "CPU throttling: the limit is the problem, not the code."),
    ("", ""),
    ("#", "4. Where is the time actually going?"),
    ("$", "perf record -F 99 -g -p 4412 -- sleep 20 && perf report --stdio | head -30"),
]) + note("tip", "cpu.stat before anything else, in a container", """
<p style="margin:0">In Kubernetes, <code>nr_throttled</code> climbing is the single most common
cause of "the app is slow and the CPU graph looks fine". CFS bandwidth control gives the cgroup a
quota per 100 ms period; burn it in 20 ms and the process is frozen for the remaining 80 ms. The
average utilisation looks like 20%. The p99 latency looks like a disaster. Both are true.</p>""")

OS_CHEAT = table(["Command", "What it answers"], [
    ["<code>ps -o pid,stat,wchan:25,comm -p PID</code>", "Running, sleeping, or stuck — and in which kernel function"],
    ["<code>strace -c -f -p PID</code>", "Which syscalls dominate, and which are erroring"],
    ["<code>ltrace -p PID</code>", "Library calls, when the syscalls look innocent"],
    ["<code>cat /proc/PID/status</code>", "Threads, signal masks, VmRSS, context switch counts"],
    ["<code>cat /proc/PID/limits</code>", "Every rlimit, soft and hard"],
    ["<code>cat /proc/PID/stack</code>", "Kernel stack of a D-state process — what it's blocked in"],
    ["<code>grep Pss /proc/PID/smaps_rollup</code>", "Honest per-process memory, shared pages apportioned"],
    ["<code>ls -l /proc/PID/ns/</code>", "Which namespaces it's in — is it actually containerised?"],
    ["<code>cat /proc/PID/cgroup</code>", "Which cgroup, so you can find its limits"],
    ["<code>cat &lt;cgroup&gt;/cpu.stat</code>", "<code>nr_throttled</code> — CPU-limit throttling"],
    ["<code>cat &lt;cgroup&gt;/memory.events</code>", "<code>high</code>, <code>max</code>, <code>oom_kill</code> counts"],
    ["<code>dmesg -T | grep -i oom</code>", "Who got killed, by which OOM path, and how big they were"],
    ["<code>vmstat 1</code>", "Run queue, context switches, swap, io wait, at a glance"],
    ["<code>pidstat -d -p PID 1</code>", "Per-process read/write throughput"],
    ["<code>sysctl -a | grep dirty</code>", "Writeback thresholds — the stall-under-load knobs"],
    ["<code>perf record -F 99 -g -p PID</code>", "Sampled stacks; the only honest answer to 'where is the time'"],
], "mono")

OPERATING_SYSTEMS = dict(
    slug="operating-systems",
    title="Operating Systems",
    tagline=("The kernel as an operator sees it — the syscall boundary, the scheduler, the page "
             "cache, cgroups, and the failure modes each one produces in production."),
    eyebrow="Foundation · Core",
    meta=["<b>26 min</b> read", "Level: <b>core → advanced</b>", "Foundation <b>02 / 10</b>"],
    sections=(
        section("The model", "WHAT SITS BETWEEN YOU AND THE HARDWARE",
                "Everything a process does that it cannot do itself crosses this boundary exactly once.",
                f'<div class="dg-scroll">{OS_DIAGRAM}</div>'
                '<p class="dg-cap">Containers do not add a layer to this diagram. They are the '
                'cgroups and namespaces boxes applied to an ordinary process — which is why a '
                'container problem is always a Linux problem underneath.</p>')
        + section("Core", "CORE CONCEPTS",
                  "The four abstractions that every production incident eventually comes back to.", OS_CORE)
        + section("Advanced", "ADVANCED",
                  "Container behaviour, memory accounting, signals and the modern I/O paths.", OS_ADV)
        + section("In practice", "TRIAGING A SLOW PROCESS", None, OS_PRACTICE)
        + section("Reference", "CHEATSHEET", None, OS_CHEAT)
    ),
)

TOPICS = [COMPUTER_FUNDAMENTALS, OPERATING_SYSTEMS]
