#!/usr/bin/env python3
"""Build terminal/index.html — a Unix practice terminal that runs in the page.

WHAT THIS IS, PRECISELY
-----------------------
A shell implemented in JavaScript over an in-memory filesystem. Commands are
really parsed and really executed against that filesystem: pipes move data,
redirection writes files, chmod changes modes, and the next command sees the
result. What it is NOT is a kernel — there is no process model, no real disk,
no network. The page says so, out loud, because a practice tool that lets you
believe you are on a real box is teaching you the wrong thing.

WHY NOT A REAL ONE
------------------
A WebAssembly Linux is tens of megabytes off a CDN, which the colophon page
correctly says this site never uses. A remote shell needs containers, auth and
abuse handling — a product, not a page. A simulation is the only option that
fits a static site, and for learning `grep | sort | uniq` it is not a
compromise: the commands behave correctly, which is the part that teaches.

The filesystem and the exercises live in terminal_fs.py — content, editable
without reading a line of the shell below.
"""
import json
import os
import pathlib
import sys

ROOT = pathlib.Path(os.environ.get("PO_ROOT") or pathlib.Path(__file__).resolve().parent.parent)
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))

from content_page import CSS, render, section, note, esc      # noqa: E402
from terminal_fs import FS, HOME, USER, HOST, EXERCISES       # noqa: E402

OUT = ROOT / "terminal"


# ── the filesystem, flattened into something JS can walk ────────────────────
def to_js(node):
    """Python tree -> JS tree. {"d": {...}} becomes a dir, tuples become files."""
    if isinstance(node, dict) and "d" in node:
        return {"t": "d", "mode": "0755",
                "c": {k: to_js(v) for k, v in node["d"].items()}}
    if isinstance(node, tuple):
        mode, content = node
        return {"t": "f", "mode": mode, "c": content}
    raise TypeError(f"unexpected node: {node!r}")


FS_JS = {"t": "d", "mode": "0755", "c": {k: to_js(v) for k, v in FS.items()}}

EX_JS = [{"title": t, "task": task, "hint": hint, "check": chk}
         for t, task, hint, chk in EXERCISES]


TERMINAL_CSS = """
/* ─── PRACTICE TERMINAL ─── */
.tm-wrap{display:grid;grid-template-columns:minmax(0,1fr) 300px;gap:18px;margin:8px 0 6px;}
@media(max-width:900px){.tm-wrap{grid-template-columns:minmax(0,1fr);}}

.tm{background:#0d0f14;border:1px solid rgba(255,255,255,.1);border-radius:8px;
  overflow:hidden;display:flex;flex-direction:column;min-width:0;}
.tm-bar{display:flex;align-items:center;gap:7px;padding:10px 13px;
  background:rgba(255,255,255,.04);border-bottom:1px solid rgba(255,255,255,.07);}
.tm-bar i{width:11px;height:11px;border-radius:50%;display:block;}
.tm-bar i.r{background:#ff5f57;} .tm-bar i.y{background:#febc2e;} .tm-bar i.g{background:#28c840;}
.tm-bar b{margin-left:8px;font-family:'DM Mono',monospace;font-size:10.5px;letter-spacing:1.5px;
  color:rgba(255,255,255,.38);font-weight:400;}
.tm-bar .tm-reset{margin-left:auto;background:none;border:1px solid rgba(255,255,255,.14);
  color:rgba(255,255,255,.5);font-family:'DM Mono',monospace;font-size:9.5px;letter-spacing:1.2px;
  text-transform:uppercase;padding:4px 9px;border-radius:3px;cursor:pointer;}
.tm-bar .tm-reset:hover{color:#fff;border-color:rgba(255,255,255,.4);}

.tm-screen{height:430px;overflow-y:auto;padding:14px 15px;font-family:'DM Mono',monospace;
  font-size:12.5px;line-height:1.65;color:#cfd3dc;-webkit-overflow-scrolling:touch;}
@media(max-width:600px){.tm-screen{height:340px;font-size:11.5px;}}
.tm-screen::-webkit-scrollbar{width:9px;}
.tm-screen::-webkit-scrollbar-track{background:rgba(255,255,255,.05);}
.tm-screen::-webkit-scrollbar-thumb{background:rgba(255,255,255,.2);border-radius:5px;}
.tm-line{white-space:pre-wrap;word-break:break-word;}
.tm-ps{color:#84cc16;} .tm-path{color:#00c2d4;} .tm-err{color:#f07570;}
.tm-dim{color:rgba(255,255,255,.34);}
.tm-dir{color:#6ea8ff;} .tm-exe{color:#a7e137;}

.tm-input{display:flex;align-items:center;gap:8px;border-top:1px solid rgba(255,255,255,.07);
  padding:11px 15px;background:rgba(255,255,255,.02);}
.tm-input label{font-family:'DM Mono',monospace;font-size:12.5px;color:#84cc16;flex-shrink:0;}
.tm-input input{flex:1;min-width:0;background:none;border:0;outline:none;color:#e7e5df;
  font-family:'DM Mono',monospace;font-size:12.5px;caret-color:#84cc16;}
@media(max-width:600px){.tm-input input,.tm-input label{font-size:11.5px;}}

.tm-side{display:flex;flex-direction:column;gap:2px;min-width:0;}
.tm-side h3{font-family:'DM Mono',monospace;font-size:9.5px;letter-spacing:2px;
  text-transform:uppercase;color:var(--muted);margin:0 0 9px;}
.tm-ex{background:var(--card-bg);border:1px solid var(--line-1);padding:11px 13px;
  cursor:pointer;display:flex;gap:10px;align-items:flex-start;text-align:left;width:100%;
  font:inherit;color:inherit;transition:background .2s,border-color .2s;}
.tm-ex:hover{background:var(--panel-bg);}
.tm-ex.on{border-color:var(--crimson);}
.tm-ex-n{font-family:'DM Mono',monospace;font-size:10px;color:var(--ash);flex-shrink:0;
  width:17px;padding-top:2px;}
.tm-ex-t{flex:1;min-width:0;font-size:13px;line-height:1.45;color:var(--heading-fg);}
.tm-ex.done .tm-ex-t{color:var(--muted);text-decoration:line-through;}
.tm-ex-c{flex-shrink:0;font-size:12px;color:var(--ash);}
.tm-ex.done .tm-ex-c{color:#5a9c1a;}
html[data-theme="dark"] .tm-ex.done .tm-ex-c{color:var(--lime);}
.tm-task{background:var(--panel-bg);border:1px solid var(--line-2);border-left:2px solid var(--crimson);
  padding:13px 15px;margin-top:10px;font-size:13.5px;line-height:1.6;}
.tm-task b{display:block;font-family:'DM Mono',monospace;font-size:9.5px;letter-spacing:1.6px;
  text-transform:uppercase;color:var(--muted);margin-bottom:6px;}
.tm-hint{margin-top:9px;font-size:12.5px;color:var(--muted);font-style:italic;display:none;}
.tm-hint.show{display:block;}
.tm-hintbtn{margin-top:9px;background:none;border:0;padding:0;font-family:'DM Mono',monospace;
  font-size:9.5px;letter-spacing:1.4px;text-transform:uppercase;color:var(--crimson);cursor:pointer;}
.tm-progress{font-family:'DM Mono',monospace;font-size:9.5px;letter-spacing:1.4px;
  text-transform:uppercase;color:var(--muted);margin-bottom:9px;}
.tm-progress b{color:var(--crimson);font-weight:400;}
"""


TERMINAL_HTML = """<div class="tm-wrap">
  <div class="tm">
    <div class="tm-bar"><i class="r"></i><i class="y"></i><i class="g"></i>
      <b>__USER__@__HOST__ — simulated</b>
      <button class="tm-reset" type="button" id="tmReset">Reset box</button></div>
    <div class="tm-screen" id="tmScreen" role="log" aria-live="polite" aria-label="Terminal output"></div>
    <form class="tm-input" id="tmForm" autocomplete="off">
      <label for="tmInput" id="tmPrompt">$</label>
      <input id="tmInput" name="cmd" type="text" autocapitalize="off" autocorrect="off"
             spellcheck="false" aria-label="Type a shell command">
    </form>
  </div>
  <div class="tm-side">
    <h3>Exercises</h3>
    <div class="tm-progress"><b id="tmDone">0</b> of <span id="tmTotal">0</span> done</div>
    <div id="tmList"></div>
    <div class="tm-task" id="tmTask" hidden>
      <b id="tmTaskN">Task</b>
      <span id="tmTaskT"></span>
      <button class="tm-hintbtn" type="button" id="tmHintBtn">Show hint</button>
      <div class="tm-hint" id="tmHint"></div>
    </div>
  </div>
</div>"""


# ── the shell ───────────────────────────────────────────────────────────────
# Written as one plain string rather than an f-string: it is dense with braces
# and doubling every one of them would make it unreadable.
TERMINAL_JS = r"""
(function(){
'use strict';
var FS0 = __FS__, EX = __EX__, HOME = "__HOME__", USER = "__USER__", HOST = "__HOST__";

var fs, cwd, history_ = [], hpos = -1, done = {}, current = 0;
var screen = document.getElementById('tmScreen');
var input  = document.getElementById('tmInput');
var form   = document.getElementById('tmForm');

function clone(o){ return JSON.parse(JSON.stringify(o)); }

/* ── paths ───────────────────────────────────────────────────────────── */
function norm(p){
  var abs = p.charAt(0) === '/';
  var out = [];
  p.split('/').forEach(function(s){
    if (!s || s === '.') return;
    if (s === '..') { if (out.length) out.pop(); return; }
    out.push(s);
  });
  return (abs ? '/' : '') + out.join('/');
}
function resolve(p){
  if (p === undefined || p === '') return cwd;
  if (p === '~') return HOME;
  if (p.indexOf('~/') === 0) p = HOME + '/' + p.slice(2);
  if (p.charAt(0) !== '/') p = cwd + '/' + p;
  var n = norm(p);
  return n === '' ? '/' : n;
}
function node(abs){
  if (abs === '/') return fs;
  var cur = fs;
  var parts = abs.split('/').filter(Boolean);
  for (var i = 0; i < parts.length; i++){
    if (!cur || cur.t !== 'd' || !cur.c[parts[i]]) return null;
    cur = cur.c[parts[i]];
  }
  return cur;
}
function parent(abs){
  var i = abs.lastIndexOf('/');
  return { dir: node(i <= 0 ? '/' : abs.slice(0, i)), name: abs.slice(i + 1) };
}
function shortCwd(){ return cwd === HOME ? '~' : (cwd.indexOf(HOME + '/') === 0 ? '~' + cwd.slice(HOME.length) : cwd); }

/* ── glob ────────────────────────────────────────────────────────────── */
function globRe(pat){
  var re = '';
  for (var i = 0; i < pat.length; i++){
    var ch = pat[i];
    if (ch === '*') re += '[^/]*';
    else if (ch === '?') re += '[^/]';
    else re += ch.replace(/[.+^${}()|[\]\\]/g, '\\$&');
  }
  return new RegExp('^' + re + '$');
}
function expand(tok){
  if (!/[*?]/.test(tok)) return [tok];
  var slash = tok.lastIndexOf('/');
  var dirPart = slash === -1 ? '' : tok.slice(0, slash + 1);
  var pat = slash === -1 ? tok : tok.slice(slash + 1);
  var d = node(resolve(dirPart || '.'));
  if (!d || d.t !== 'd') return [tok];
  var re = globRe(pat);
  var hits = Object.keys(d.c).filter(function(n){ return re.test(n) && (pat[0] === '.' || n[0] !== '.'); }).sort();
  return hits.length ? hits.map(function(n){ return dirPart + n; }) : [tok];
}

/* ── tokenizer ───────────────────────────────────────────────────────── */
function tokenize(line){
  var out = [], cur = '', q = null, had = false;
  for (var i = 0; i < line.length; i++){
    var ch = line[i];
    if (q){ if (ch === q) q = null; else cur += ch; continue; }
    if (ch === '"' || ch === "'"){ q = ch; had = true; continue; }
    if (/\s/.test(ch)){ if (cur || had){ out.push({v: cur, q: had}); cur = ''; had = false; } continue; }
    cur += ch;
  }
  if (cur || had) out.push({v: cur, q: had});
  return out;
}

/* ── commands ────────────────────────────────────────────────────────── */
function lines(s){ return s.length ? s.replace(/\n$/, '').split('\n') : []; }
function flags(args){
  var f = {}, rest = [];
  args.forEach(function(a){
    if (a.length > 1 && a[0] === '-' && !/^-\d/.test(a) && isNaN(Number(a))) {
      a.slice(1).split('').forEach(function(c){ f[c] = true; });
    } else rest.push(a);
  });
  return { f: f, rest: rest };
}
function numFlag(args, letter){
  for (var i = 0; i < args.length; i++){
    if (args[i] === '-' + letter && args[i+1] !== undefined) return parseInt(args[i+1], 10);
    if (/^-\d+$/.test(args[i])) return parseInt(args[i].slice(1), 10);
  }
  return null;
}
function err(m){ return { out: '', err: m }; }
function ok(o){ return { out: o === undefined ? '' : o, err: '' }; }

function modeStr(n){
  var m = n.mode.slice(-3), map = ['---','--x','-w-','-wx','r--','r-x','rw-','rwx'];
  return (n.t === 'd' ? 'd' : '-') + m.split('').map(function(d){ return map[parseInt(d, 8)]; }).join('');
}
function sizeOf(n){ return n.t === 'd' ? 4096 : n.c.length; }

var CMD = {};

CMD.pwd = function(){ return ok(cwd); };
CMD.whoami = function(){ return ok(USER); };
CMD.hostname = function(){ return ok(HOST); };
CMD.id = function(){ return ok('uid=1000(' + USER + ') gid=1000(' + USER + ') groups=1000(' + USER + '),27(sudo)'); };
CMD.date = function(){ return ok('Tue Sep  1 12:00:00 UTC 2026'); };
CMD.uname = function(a){ return ok(a.indexOf('-a') >= 0
  ? 'Linux ' + HOST + ' 6.8.0-lab #1 SMP x86_64 GNU/Linux' : 'Linux'); };
CMD.echo = function(a){ return ok(a.join(' ')); };
CMD.clear = function(){ screen.innerHTML = ''; return ok(); };

CMD.cd = function(a){
  var t = resolve(a[0] === undefined ? HOME : a[0]);
  var n = node(t);
  if (!n) return err('cd: ' + a[0] + ': No such file or directory');
  if (n.t !== 'd') return err('cd: ' + a[0] + ': Not a directory');
  cwd = t; return ok();
};

CMD.ls = function(a){
  var p = flags(a), all = p.f.a, long = p.f.l;
  var targets = p.rest.length ? p.rest : ['.'];
  var chunks = [];
  targets.forEach(function(t){
    var abs = resolve(t), n = node(abs);
    if (!n) { chunks.push({ e: 'ls: cannot access \'' + t + '\': No such file or directory' }); return; }
    var names, base;
    if (n.t === 'f'){ names = [t]; base = null; }
    else { base = n; names = Object.keys(n.c).sort(); if (!all) names = names.filter(function(x){ return x[0] !== '.'; }); }
    var rows = names.map(function(name){
      var child = base ? base.c[name] : n;
      if (!long) return { name: name, n: child };
      return { name: name, n: child, line:
        modeStr(child) + ' ' + (child.t === 'd' ? '2' : '1') + ' ' + USER + ' ' + USER +
        ' ' + String(sizeOf(child)).padStart(6) + ' Sep  1 12:00 ' + name };
    });
    if (long) chunks.push({ o: rows.map(function(r){ return r.line; }).join('\n') });
    else chunks.push({ o: rows.map(function(r){ return r.name + (r.n.t === 'd' ? '/' : ''); }).join('  ') });
  });
  var e = chunks.filter(function(c){ return c.e; }).map(function(c){ return c.e; }).join('\n');
  var o = chunks.filter(function(c){ return c.o !== undefined; }).map(function(c){ return c.o; }).join('\n');
  return { out: o, err: e };
};

CMD.cat = function(a, stdin){
  if (!a.length) return ok(stdin);
  var o = '', e = '';
  a.forEach(function(t){
    var n = node(resolve(t));
    if (!n) e += (e ? '\n' : '') + 'cat: ' + t + ': No such file or directory';
    else if (n.t === 'd') e += (e ? '\n' : '') + 'cat: ' + t + ': Is a directory';
    else o += n.c;
  });
  return { out: o.replace(/\n$/, ''), err: e };
};

function headTail(which){
  return function(a, stdin){
    var n = numFlag(a, 'n'); if (n === null) n = 10;
    var files = a.filter(function(x, i){
      if (/^-\d+$/.test(x)) return false;
      if (x === '-n') return false;
      if (i > 0 && a[i-1] === '-n') return false;
      return x[0] !== '-';
    });
    var text = files.length ? (node(resolve(files[0])) || {c:''}).c : stdin;
    if (files.length && !node(resolve(files[0])))
      return err(which + ': cannot open \'' + files[0] + '\' for reading: No such file or directory');
    var L = lines(text);
    return ok((which === 'head' ? L.slice(0, n) : L.slice(-n)).join('\n'));
  };
}
CMD.head = headTail('head');
CMD.tail = headTail('tail');

CMD.wc = function(a, stdin){
  var p = flags(a);
  var text = p.rest.length ? (node(resolve(p.rest[0])) || {c:''}).c : stdin;
  if (p.rest.length && !node(resolve(p.rest[0])))
    return err('wc: ' + p.rest[0] + ': No such file or directory');
  var l = lines(text).length, w = text.split(/\s+/).filter(Boolean).length, c = text.length;
  var tag = p.rest.length ? ' ' + p.rest[0] : '';
  if (p.f.l) return ok(String(l) + tag);
  if (p.f.w) return ok(String(w) + tag);
  if (p.f.c) return ok(String(c) + tag);
  return ok(l + ' ' + w + ' ' + c + tag);
};

CMD.grep = function(a, stdin){
  var p = flags(a), pat = p.rest.shift();
  if (pat === undefined) return err('usage: grep [-invc] PATTERN [FILE]');
  var text = p.rest.length ? (node(resolve(p.rest[0])) || {c: null}).c : stdin;
  if (p.rest.length && text === null) return err('grep: ' + p.rest[0] + ': No such file or directory');
  var re;
  try { re = new RegExp(pat, p.f.i ? 'i' : ''); } catch (ex) { return err('grep: invalid pattern'); }
  var hit = lines(text).filter(function(l){ var m = re.test(l); return p.f.v ? !m : m; });
  if (p.f.c) return ok(String(hit.length));
  if (p.f.n){
    var all = lines(text), outn = [];
    all.forEach(function(l, i){ var m = re.test(l); if (p.f.v ? !m : m) outn.push((i+1) + ':' + l); });
    return ok(outn.join('\n'));
  }
  return ok(hit.join('\n'));
};

CMD.sort = function(a, stdin){
  var p = flags(a);
  var text = p.rest.length ? (node(resolve(p.rest[0])) || {c:''}).c : stdin;
  var L = lines(text).slice();
  L.sort(p.f.n ? function(x, y){ return parseFloat(x) - parseFloat(y); }
               : function(x, y){ return x < y ? -1 : x > y ? 1 : 0; });
  if (p.f.r) L.reverse();
  return ok(L.join('\n'));
};

CMD.uniq = function(a, stdin){
  var p = flags(a);
  var text = p.rest.length ? (node(resolve(p.rest[0])) || {c:''}).c : stdin;
  var L = lines(text), out = [], counts = [];
  L.forEach(function(l){
    if (out.length && out[out.length-1] === l) counts[counts.length-1]++;
    else { out.push(l); counts.push(1); }
  });
  if (p.f.c) return ok(out.map(function(l, i){ return String(counts[i]).padStart(7) + ' ' + l; }).join('\n'));
  return ok(out.join('\n'));
};

CMD.cut = function(a, stdin){
  var d = ' ', fspec = null, rest = [];
  for (var i = 0; i < a.length; i++){
    if (a[i] === '-d'){ d = a[++i]; }
    else if (a[i].indexOf('-d') === 0){ d = a[i].slice(2); }
    else if (a[i] === '-f'){ fspec = a[++i]; }
    else if (a[i].indexOf('-f') === 0){ fspec = a[i].slice(2); }
    else rest.push(a[i]);
  }
  if (!fspec) return err('cut: you must specify a list of fields');
  var text = rest.length ? (node(resolve(rest[0])) || {c:''}).c : stdin;
  var want = fspec.split(',').map(Number);
  return ok(lines(text).map(function(l){
    var parts = d === ' ' ? l.split(/ +/) : l.split(d);
    return want.map(function(n){ return parts[n-1] === undefined ? '' : parts[n-1]; }).join(d === ' ' ? ' ' : d);
  }).join('\n'));
};

CMD.tr = function(a, stdin){
  if (a.length < 2) return err('usage: tr SET1 SET2');
  var from = a[0], to = a[1];
  return ok(stdin.split('').map(function(ch){
    var i = from.indexOf(ch);
    return i >= 0 ? (to[i] || to[to.length-1]) : ch;
  }).join(''));
};

CMD.mkdir = function(a){
  var p = flags(a);
  if (!p.rest.length) return err('mkdir: missing operand');
  var e = '';
  p.rest.forEach(function(t){
    var abs = resolve(t);
    if (p.f.p){
      var parts = abs.split('/').filter(Boolean), cur = fs, acc = '';
      parts.forEach(function(seg){ acc += '/' + seg;
        if (!cur.c[seg]) cur.c[seg] = { t:'d', mode:'0755', c:{} };
        cur = cur.c[seg]; });
      return;
    }
    var pr = parent(abs);
    if (!pr.dir || pr.dir.t !== 'd') e += 'mkdir: cannot create directory \'' + t + '\': No such file or directory';
    else if (pr.dir.c[pr.name]) e += 'mkdir: cannot create directory \'' + t + '\': File exists';
    else pr.dir.c[pr.name] = { t:'d', mode:'0755', c:{} };
  });
  return { out:'', err:e };
};

CMD.touch = function(a){
  if (!a.length) return err('touch: missing file operand');
  a.forEach(function(t){
    var abs = resolve(t), pr = parent(abs);
    if (pr.dir && pr.dir.t === 'd' && !pr.dir.c[pr.name])
      pr.dir.c[pr.name] = { t:'f', mode:'0644', c:'' };
  });
  return ok();
};

CMD.rm = function(a){
  var p = flags(a);
  if (!p.rest.length) return err('rm: missing operand');
  var e = '';
  p.rest.forEach(function(t){
    var abs = resolve(t), n = node(abs), pr = parent(abs);
    if (!n){ if (!p.f.f) e += 'rm: cannot remove \'' + t + '\': No such file or directory'; return; }
    if (n.t === 'd' && !p.f.r){ e += 'rm: cannot remove \'' + t + '\': Is a directory'; return; }
    delete pr.dir.c[pr.name];
  });
  return { out:'', err:e };
};

function copyMove(move){
  return function(a){
    var p = flags(a);
    if (p.rest.length < 2) return err((move ? 'mv' : 'cp') + ': missing destination file operand');
    var src = resolve(p.rest[0]), dstRaw = p.rest[1], dst = resolve(dstRaw);
    var sn = node(src);
    if (!sn) return err((move ? 'mv' : 'cp') + ': cannot stat \'' + p.rest[0] + '\': No such file or directory');
    if (sn.t === 'd' && !move && !p.f.r) return err('cp: -r not specified; omitting directory \'' + p.rest[0] + '\'');
    var dn = node(dst);
    if (dn && dn.t === 'd'){ dst = dst + '/' + src.split('/').pop(); }
    var dp = parent(dst);
    if (!dp.dir || dp.dir.t !== 'd') return err((move ? 'mv' : 'cp') + ': cannot create \'' + dstRaw + '\': No such file or directory');
    dp.dir.c[dp.name] = clone(sn);
    if (move){ var sp = parent(src); delete sp.dir.c[sp.name]; }
    return ok();
  };
}
CMD.cp = copyMove(false);
CMD.mv = copyMove(true);

CMD.find = function(a){
  var start = (a[0] && a[0][0] !== '-') ? a[0] : '.';
  var name = null, type = null;
  for (var i = 0; i < a.length; i++){
    if (a[i] === '-name') name = a[i+1];
    if (a[i] === '-type') type = a[i+1];
  }
  var base = resolve(start), root = node(base);
  if (!root) return err('find: \'' + start + '\': No such file or directory');
  var re = name ? globRe(name) : null, out = [];
  (function walk(n, path){
    var isDir = n.t === 'd';
    var okType = !type || (type === 'd' ? isDir : !isDir);
    var okName = !re || re.test(path.split('/').pop() || '/');
    if (okType && okName) out.push(path);
    if (isDir) Object.keys(n.c).sort().forEach(function(k){
      walk(n.c[k], (path === '/' ? '' : path) + '/' + k);
    });
  })(root, start === '.' ? '.' : base);
  return ok(out.join('\n'));
};

CMD.chmod = function(a){
  var p = flags([]);
  var rest = a.slice();
  var spec = rest.shift();
  if (!spec || !rest.length) return err('chmod: missing operand');
  var e = '';
  rest.forEach(function(t){
    var n = node(resolve(t));
    if (!n){ e += 'chmod: cannot access \'' + t + '\': No such file or directory'; return; }
    if (/^[0-7]{3,4}$/.test(spec)){
      n.mode = (spec.length === 3 ? '0' : '') + spec;
      return;
    }
    var m = /^([ugoa]*)([-+=])([rwx]+)$/.exec(spec);
    if (!m){ e += 'chmod: invalid mode: \'' + spec + '\''; return; }
    var who = m[1] || 'a', op = m[2], bitsTxt = m[3];
    var bits = (bitsTxt.indexOf('r') >= 0 ? 4 : 0) + (bitsTxt.indexOf('w') >= 0 ? 2 : 0) + (bitsTxt.indexOf('x') >= 0 ? 1 : 0);
    var cur = n.mode.slice(-3).split('').map(Number);
    var idx = { u:[0], g:[1], o:[2], a:[0,1,2] };
    (who.split('').reduce(function(acc, w){ return acc.concat(idx[w]); }, [])).forEach(function(i){
      if (op === '+') cur[i] |= bits;
      else if (op === '-') cur[i] &= ~bits;
      else cur[i] = bits;
    });
    n.mode = '0' + cur.join('');
  });
  return { out:'', err:e };
};

CMD.stat = function(a){
  if (!a.length) return err('stat: missing operand');
  var abs = resolve(a[0]), n = node(abs);
  if (!n) return err('stat: cannot stat \'' + a[0] + '\': No such file or directory');
  return ok('  File: ' + abs + '\n  Size: ' + sizeOf(n) +
            '\nAccess: (' + n.mode.slice(-4).padStart(4,'0') + '/' + modeStr(n) + ')  Uid: ( 1000/' + USER + ')');
};

CMD.df = function(){ return ok(
  'Filesystem      Size  Used Avail Use% Mounted on\n' +
  '/dev/vda1        20G  6.2G   13G  33% /\n' +
  'tmpfs           2.0G     0  2.0G   0% /dev/shm'); };
CMD.ps = function(){ return ok(
  '  PID TTY          TIME CMD\n' +
  '  811 ?        00:00:00 systemd\n' +
  ' 1422 ?        00:00:12 api\n' +
  ' 2041 pts/0    00:00:00 bash\n' +
  ' 2077 pts/0    00:00:00 ps'); };
CMD.env = function(){ return ok('USER=' + USER + '\nHOME=' + HOME + '\nSHELL=/bin/bash\nPWD=' + cwd); };
CMD.history = function(){ return ok(history_.map(function(h, i){ return String(i+1).padStart(4) + '  ' + h; }).join('\n')); };

CMD.help = function(){
  return ok('Available: ' + Object.keys(CMD).sort().join(' ') +
            '\nPipes |  redirection > >>  chaining &&  globs *  and ~ all work.\n' +
            'Up/Down walks history, Tab completes paths.');
};
CMD.man = function(a){
  var d = {
    ls:'list directory contents  (-l long, -a all)',
    grep:'print lines matching a pattern  (-i ignore case, -v invert, -n number, -c count)',
    wc:'count lines, words and bytes  (-l, -w, -c)',
    chmod:'change file mode  (755 or +x)',
    find:'search a directory tree  (-name PATTERN, -type f|d)',
    cut:'select fields from each line  (-d DELIM -f N)',
    sort:'sort lines  (-r reverse, -n numeric)',
    uniq:'collapse repeated neighbouring lines  (-c count)'
  };
  if (!a.length) return err('What manual page do you want?');
  return d[a[0]] ? ok(a[0] + ' — ' + d[a[0]]) : err('No manual entry for ' + a[0]);
};

/* ── run one pipeline ────────────────────────────────────────────────── */
function runSimple(tokens, stdin){
  var argv = [];
  tokens.forEach(function(t){
    if (t.q) argv.push(t.v);
    else expand(t.v).forEach(function(x){ argv.push(x); });
  });
  var name = argv.shift();
  if (!name) return ok();
  if (!CMD[name]) return err(name + ': command not found');
  return CMD[name](argv, stdin === undefined ? '' : stdin);
}

function runLine(line){
  var outAll = '', errAll = '';
  line.split('&&').forEach(function(seg, si, segs){
    if (errAll && si) return;                       /* && stops on failure */
    var redir = null, target = null;
    var m = /(>>?)\s*([^\s>]+)\s*$/.exec(seg);
    if (m){ redir = m[1]; target = m[2]; seg = seg.slice(0, m.index); }
    var stdin = '', out = '', e = '';
    var stages = seg.split('|');
    for (var i = 0; i < stages.length; i++){
      var r = runSimple(tokenize(stages[i]), stdin);
      if (r.err) { e += (e ? '\n' : '') + r.err; out = r.out; break; }
      out = r.out; stdin = out;
    }
    if (redir && !e){
      var abs = resolve(target), pr = parent(abs);
      if (!pr.dir || pr.dir.t !== 'd') e = 'bash: ' + target + ': No such file or directory';
      else {
        var body = out + (out.length ? '\n' : '');
        var prev = (redir === '>>' && pr.dir.c[pr.name]) ? pr.dir.c[pr.name].c : '';
        pr.dir.c[pr.name] = { t:'f', mode:'0644', c: prev + body };
        out = '';
      }
    }
    if (out) outAll += (outAll ? '\n' : '') + out;
    if (e) errAll += (errAll ? '\n' : '') + e;
  });
  return { out: outAll, err: errAll };
}

/* ── screen ──────────────────────────────────────────────────────────── */
function esc(s){ return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); }
function print(html, cls){
  var d = document.createElement('div');
  d.className = 'tm-line' + (cls ? ' ' + cls : '');
  d.innerHTML = html;
  screen.appendChild(d);
  screen.scrollTop = screen.scrollHeight;
}
function promptHTML(){
  return '<span class="tm-ps">' + USER + '@' + HOST + '</span>:<span class="tm-path">' +
         esc(shortCwd()) + '</span>$ ';
}
function syncPrompt(){ document.getElementById('tmPrompt').textContent = shortCwd() + ' $'; }

/* ── exercises ───────────────────────────────────────────────────────── */
var ctxFor = function(out, cmd){
  return {
    out: out.replace(/\s+$/, ''), cmd: cmd.trim(), cwd: cwd,
    read: function(p){ var n = node(resolve(p)); return n && n.t === 'f' ? n.c : null; },
    mode: function(p){ var n = node(resolve(p)); return n ? n.mode : null; },
    exists: function(p){ return !!node(resolve(p)); }
  };
};
var checks = EX.map(function(e){
  try { return new Function('c', 'return (' + e.check + ');'); }
  catch (ex) { return function(){ return false; }; }
});
function renderList(){
  var list = document.getElementById('tmList');
  list.innerHTML = '';
  EX.forEach(function(e, i){
    var b = document.createElement('button');
    b.type = 'button';
    b.className = 'tm-ex' + (done[i] ? ' done' : '') + (i === current ? ' on' : '');
    b.innerHTML = '<span class="tm-ex-n">' + String(i+1).padStart(2,'0') + '</span>' +
                  '<span class="tm-ex-t">' + esc(e.title) + '</span>' +
                  '<span class="tm-ex-c">' + (done[i] ? '✓' : '') + '</span>';
    b.addEventListener('click', function(){ current = i; showTask(); renderList(); });
    list.appendChild(b);
  });
  document.getElementById('tmDone').textContent = Object.keys(done).length;
  document.getElementById('tmTotal').textContent = EX.length;
}
function showTask(){
  var e = EX[current], box = document.getElementById('tmTask');
  box.hidden = false;
  document.getElementById('tmTaskN').textContent = 'Task ' + (current+1);
  document.getElementById('tmTaskT').textContent = e.task;
  var h = document.getElementById('tmHint');
  h.textContent = e.hint; h.classList.remove('show');
}
function grade(out, cmd){
  var c = ctxFor(out, cmd), hit = -1;
  checks.forEach(function(fn, i){
    if (done[i]) return;
    var pass = false;
    try { pass = !!fn(c); } catch (ex) { pass = false; }
    if (pass){ done[i] = true; if (hit === -1) hit = i; }
  });
  if (hit !== -1){
    print('<span class="tm-dim">✓ exercise ' + (hit+1) + ' complete — ' + esc(EX[hit].title) + '</span>');
    save();
    var next = EX.findIndex(function(_, i){ return !done[i]; });
    if (next !== -1) current = next;
    renderList(); showTask();
    if (Object.keys(done).length === EX.length)
      print('<span class="tm-dim">all ' + EX.length + ' exercises done.</span>');
  }
}

/* ── persistence (per tab, best effort) ──────────────────────────────── */
function save(){ try { sessionStorage.setItem('po-term', JSON.stringify(done)); } catch (e) {} }
function load(){ try { var d = sessionStorage.getItem('po-term'); if (d) done = JSON.parse(d) || {}; } catch (e) { done = {}; } }

/* ── completion ──────────────────────────────────────────────────────── */
function complete(){
  var v = input.value, m = /(\S*)$/.exec(v), frag = m[1];
  var pool;
  if (v.trim() === frag) pool = Object.keys(CMD).sort();
  else {
    var slash = frag.lastIndexOf('/');
    var dirPart = slash === -1 ? '' : frag.slice(0, slash + 1);
    var base = frag.slice(slash + 1);
    var d = node(resolve(dirPart || '.'));
    if (!d || d.t !== 'd') return;
    pool = Object.keys(d.c).sort().map(function(n){ return dirPart + n + (d.c[n].t === 'd' ? '/' : ''); });
    frag = frag;
  }
  var hits = pool.filter(function(x){ return x.indexOf(frag) === 0; });
  if (hits.length === 1) input.value = v.slice(0, v.length - frag.length) + hits[0];
  else if (hits.length > 1){
    print(promptHTML() + esc(v));
    print('<span class="tm-dim">' + esc(hits.join('  ')) + '</span>');
  }
}

/* ── boot ────────────────────────────────────────────────────────────── */
function reset(quiet){
  fs = clone(FS0); cwd = HOME;
  if (!quiet) screen.innerHTML = '';
  print('<span class="tm-dim">Platform Ops practice terminal — a simulation, in your browser.</span>');
  print('<span class="tm-dim">Nothing you type leaves this page. Type <b>help</b> for the command list.</span>');
  print(' ');
  syncPrompt();
}

form.addEventListener('submit', function(ev){
  ev.preventDefault();
  var line = input.value;
  input.value = '';
  print(promptHTML() + esc(line));
  if (line.trim()){
    history_.push(line); hpos = history_.length;
    var r = runLine(line);
    if (r.out) print(esc(r.out));
    if (r.err) print(esc(r.err), 'tm-err');
    syncPrompt();
    grade(r.out, line);
  }
  screen.scrollTop = screen.scrollHeight;
});

input.addEventListener('keydown', function(ev){
  if (ev.key === 'ArrowUp'){ ev.preventDefault();
    if (hpos > 0){ hpos--; input.value = history_[hpos]; } }
  else if (ev.key === 'ArrowDown'){ ev.preventDefault();
    if (hpos < history_.length - 1){ hpos++; input.value = history_[hpos]; }
    else { hpos = history_.length; input.value = ''; } }
  else if (ev.key === 'Tab'){ ev.preventDefault(); complete(); }
  else if (ev.key === 'l' && ev.ctrlKey){ ev.preventDefault(); screen.innerHTML = ''; }
});

document.getElementById('tmReset').addEventListener('click', function(){ reset(false); input.focus(); });
document.getElementById('tmHintBtn').addEventListener('click', function(){
  document.getElementById('tmHint').classList.toggle('show'); });
screen.addEventListener('click', function(){ if (!window.getSelection().toString()) input.focus(); });

load(); reset(false); renderList(); showTask();
window.__poTerm = { run: function(l){ return runLine(l); }, state: function(){ return { cwd: cwd, done: done }; } };
})();
"""


def build_js():
    js = TERMINAL_JS
    js = js.replace("__FS__", json.dumps(FS_JS))
    js = js.replace("__EX__", json.dumps(EX_JS))
    js = js.replace("__HOME__", HOME).replace("__USER__", USER).replace("__HOST__", HOST)
    assert "__FS__" not in js and "__EX__" not in js, "a placeholder survived"
    return js


BODY = TERMINAL_HTML.replace("__USER__", USER).replace("__HOST__", HOST)

SECTIONS = "".join([
    section("Practice", "A Unix terminal that actually runs",
            "Type real commands. They are parsed and executed against a filesystem held in "
            "this page — pipes move data, redirection writes files, and the next command "
            "sees what the last one changed.",
            BODY
            + note("warn", "This is a simulation, not a machine",
                   "<p>There is no kernel, no processes and no network behind it — a shell "
                   "implemented in JavaScript over an in-memory tree. It is honest about "
                   "that because a practice box you mistake for a real one teaches the "
                   "wrong lesson. Nothing you type leaves the page, and "
                   "<b>Reset box</b> puts the filesystem back exactly as it started.</p>")),

    section("What works", "The parts of a shell worth practising",
            "Not every flag of every tool — the ones you reach for daily, behaving correctly.",
            "<div class='tw'><table class='tbl'><thead><tr><th>Area</th><th>Commands</th>"
            "</tr></thead><tbody>"
            "<tr><td>Moving around</td><td><code>pwd</code> <code>cd</code> <code>ls -l -a</code></td></tr>"
            "<tr><td>Reading</td><td><code>cat</code> <code>head -n</code> <code>tail -n</code> "
            "<code>wc -l -w -c</code> <code>stat</code></td></tr>"
            "<tr><td>Searching</td><td><code>grep -i -v -n -c</code> <code>find -name -type</code></td></tr>"
            "<tr><td>Shaping text</td><td><code>sort -r -n</code> <code>uniq -c</code> "
            "<code>cut -d -f</code> <code>tr</code> <code>echo</code></td></tr>"
            "<tr><td>Changing things</td><td><code>mkdir -p</code> <code>touch</code> "
            "<code>rm -r</code> <code>cp</code> <code>mv</code> <code>chmod</code></td></tr>"
            "<tr><td>Looking around</td><td><code>whoami</code> <code>id</code> <code>ps</code> "
            "<code>df</code> <code>env</code> <code>uname -a</code> <code>history</code></td></tr>"
            "<tr><td>Shell itself</td><td>pipes <code>|</code>, redirection <code>&gt;</code> "
            "<code>&gt;&gt;</code>, chaining <code>&amp;&amp;</code>, globs <code>*</code>, "
            "<code>~</code>, quoting, Tab completion, Up/Down history</td></tr>"
            "</tbody></table></div>"),
])

PAGER = ('<div class="pager">'
         '<a href="../categories/foundation/index.html">← Foundation<b>Category hub</b></a>'
         '<a class="next" href="../Commands/LINUX-COMMANDS/linux-commands.html">'
         'Linux commands →<b>Full reference</b></a>'
         '</div>')

OUT.mkdir(parents=True, exist_ok=True)
(OUT / "topic.css").write_text(CSS.strip() + "\n" + TERMINAL_CSS, encoding="utf-8")

html_out = render(
    slug="terminal",
    title="Practice Terminal",
    tagline=("A Unix shell simulated in your browser: real command behaviour over an "
             "in-memory filesystem, with exercises that check your work."),
    eyebrow="Practice",
    crumbs=[("Home", "../index.html"), ("Practice Terminal", None)],
    meta=[f"{len(EXERCISES)} exercises", "30+ commands", "no backend", "runs offline"],
    sections=SECTIONS,
    pager=PAGER,
    up="../",
    css="topic.css",
    canon="terminal/")

html_out = html_out.replace("</body>", f"<script>{build_js()}</script>\n</body>", 1)
(OUT / "index.html").write_text(html_out, encoding="utf-8")
print(f"  {len(html_out) // 1024:3d} KB  terminal/index.html  "
      f"({len(EXERCISES)} exercises, {len(FS_JS['c'])} top-level dirs)")
