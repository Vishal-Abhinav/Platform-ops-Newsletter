#!/usr/bin/env python3
"""Build branded login, member, and administrator account surfaces."""
import os
import pathlib
import sys

ROOT = pathlib.Path(os.environ.get("PO_ROOT") or pathlib.Path(__file__).resolve().parent.parent)
TOOLS = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS))

from content_page import CSS, render, section  # noqa: E402

ASSETS = ROOT / "assets"

AUTH_CSS = CSS + r"""
.auth-shell{max-width:620px;margin:0 auto;border:1px solid var(--line-2);background:var(--card-bg);padding:28px;}
.auth-mark{width:44px;height:44px;display:grid;place-items:center;border:1px solid var(--line-2);margin-bottom:22px;
 font-family:'DM Mono',monospace;font-size:12px;color:var(--heading-fg);background:var(--panel-bg);}
.auth-shell h3{font-family:'Bebas Neue',sans-serif;font-size:32px;font-weight:400;line-height:1;margin:0 0 10px;}
.auth-shell p{margin:0;color:var(--muted);font-size:14px;line-height:1.65;}
.auth-button{display:flex;align-items:center;justify-content:center;gap:10px;width:100%;margin-top:24px;padding:13px 16px;
 border:1px solid var(--heading-fg);background:var(--heading-fg);color:var(--page-bg);text-decoration:none;
 font-family:'DM Mono',monospace;font-size:10px;letter-spacing:1.2px;text-transform:uppercase;cursor:pointer;}
.auth-button:hover{background:var(--cyan);border-color:var(--cyan);}
.auth-note{display:flex;gap:9px;margin-top:18px;padding-top:18px;border-top:1px solid var(--line-1);
 font-family:'DM Mono',monospace;font-size:9px;line-height:1.6;letter-spacing:.7px;color:var(--muted);}
.auth-note::before{content:'';width:7px;height:7px;border-radius:50%;background:var(--lime);margin-top:4px;flex:0 0 auto;}
.auth-message{display:none;margin:0 0 18px;padding:12px 14px;border-left:2px solid var(--amber);background:var(--panel-bg);
 font-size:13px;line-height:1.55;color:var(--heading-fg);}
.auth-message.show{display:block}.auth-message.error{border-color:var(--crimson)}
.account-grid{display:grid;grid-template-columns:minmax(0,1.1fr) minmax(260px,.9fr);gap:14px;}
.account-card{border:1px solid var(--line-2);background:var(--card-bg);padding:22px;min-width:0;}
.account-kicker{font-family:'DM Mono',monospace;font-size:9px;letter-spacing:1.8px;text-transform:uppercase;color:var(--muted);margin-bottom:8px;}
.account-value{font-size:17px;color:var(--heading-fg);overflow-wrap:anywhere;margin:0;}
.account-role{display:inline-flex;margin-top:14px;border:1px solid var(--line-2);padding:5px 9px;
 font-family:'DM Mono',monospace;font-size:9px;letter-spacing:1.4px;text-transform:uppercase;color:var(--cyan);}
.account-state{display:flex;align-items:center;gap:9px;font-size:13px;color:var(--muted);margin-top:14px;}
.account-state::before{content:'';width:8px;height:8px;border-radius:50%;background:var(--amber);flex:0 0 auto;}
.account-state.ready::before{background:var(--lime)}.account-state.error::before{background:var(--crimson)}
.account-actions{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:2px;background:var(--line-1);border:1px solid var(--line-1);}
.account-action{background:var(--card-bg);padding:18px;text-decoration:none;min-height:118px;display:flex;
 flex-direction:column;justify-content:space-between;transition:background .18s;}
.account-action:hover{background:var(--panel-bg)}
.account-action b{font-family:'Bebas Neue',sans-serif;font-size:22px;font-weight:400;letter-spacing:.4px;}
.account-action span{font-size:12.5px;color:var(--muted);line-height:1.5;}
.account-action i{font-style:normal;font-family:'DM Mono',monospace;font-size:9px;letter-spacing:1.2px;text-transform:uppercase;color:var(--crimson);margin-top:12px;}
.account-signout{display:inline-block;margin-top:18px;padding:0;border:0;background:none;cursor:pointer;
 font-family:'DM Mono',monospace;font-size:10px;letter-spacing:1.4px;text-transform:uppercase;color:var(--muted);}
.account-signout:hover{color:var(--crimson)}
.user-table-wrap{overflow-x:auto;border:1px solid var(--line-2);background:var(--card-bg);}
.user-table{width:100%;border-collapse:collapse;min-width:760px;font-size:12px;}
.user-table th,.user-table td{padding:13px 12px;border-bottom:1px solid var(--line-1);text-align:left;vertical-align:middle;}
.user-table th{font-family:'DM Mono',monospace;font-size:9px;letter-spacing:1.2px;text-transform:uppercase;color:var(--muted);}
.user-table strong{display:block;color:var(--heading-fg);font-weight:600}.user-table small{color:var(--muted)}
.user-table select{border:1px solid var(--line-2);background:var(--page-bg);color:var(--heading-fg);padding:7px 8px;font-size:12px;}
.user-save{border:1px solid var(--line-2);background:transparent;color:var(--cyan);padding:7px 10px;cursor:pointer;
 font-family:'DM Mono',monospace;font-size:9px;letter-spacing:1px;text-transform:uppercase;}
.user-save:hover{border-color:var(--cyan)}.user-save:disabled{opacity:.45;cursor:wait}
.user-empty{padding:24px;color:var(--muted)}
@media(max-width:700px){.account-grid,.account-actions{grid-template-columns:1fr}.auth-shell{padding:22px}}
"""

LOGIN_SCRIPT = r"""<script>
(function(){
  var params=new URLSearchParams(location.search);
  var message=document.querySelector('[data-auth-message]');
  var messages={
    pending:'Your identity is verified. An administrator must approve the account before private pages open.',
    'signed-out':'You have been signed out safely.'
  };
  var errors={
    configuration:'Sign-in is being configured. Please return shortly.',
    state:'The sign-in request expired. Start again from this page.',
    github:'GitHub could not verify this account. Confirm that your GitHub email is verified, then try again.',
    suspended:'This account is not currently permitted to sign in.',
    session:'Your session expired. Sign in again to continue.'
  };
  var text=errors[params.get('error')] || messages[params.get('status')];
  if(text){message.textContent=text;message.classList.add('show');if(params.get('error'))message.classList.add('error');}
  var next=params.get('next');
  if(next && next.charAt(0)==='/' && next.indexOf('//')!==0){
    document.querySelector('[data-github-login]').href='/auth/github?next='+encodeURIComponent(next);
  }
})();
</script>"""

SESSION_SCRIPT = r"""<script>
(function(){
  var root=document.querySelector('[data-account]');
  if(!root)return;
  fetch('/auth/session',{headers:{Accept:'application/json'},credentials:'same-origin'})
    .then(function(response){if(!response.ok)throw new Error('session');return response.json();})
    .then(function(session){
      var user=session.user;
      root.querySelector('[data-account-name]').textContent=user.name || user.githubLogin;
      root.querySelector('[data-account-email]').textContent=user.email;
      root.querySelector('[data-account-role]').textContent=user.role;
      var state=root.querySelector('[data-account-state]');
      state.textContent='Verified with GitHub';state.className='account-state ready';
    }).catch(function(){location.assign('/login/?error=session');});
})();
</script>"""

ADMIN_SCRIPT = r"""<script>
(function(){
  var body=document.querySelector('[data-user-list]');
  if(!body)return;
  function option(value,current){var o=document.createElement('option');o.value=value;o.textContent=value;o.selected=value===current;return o;}
  function load(){
    fetch('/admin/api/users',{headers:{Accept:'application/json'},credentials:'same-origin'})
      .then(function(r){if(!r.ok)throw new Error('load');return r.json();})
      .then(function(data){
        body.textContent='';
        if(!data.users.length){var row=body.insertRow();var cell=row.insertCell();cell.colSpan=5;cell.className='user-empty';cell.textContent='No accounts yet.';return;}
        data.users.forEach(function(user){
          var row=body.insertRow();
          var identity=row.insertCell();var name=document.createElement('strong');name.textContent=user.name || user.github_login;
          var detail=document.createElement('small');detail.textContent='@'+user.github_login+' / '+user.email;identity.append(name,detail);
          var role=row.insertCell();var roleSelect=document.createElement('select');['user','admin'].forEach(function(v){roleSelect.append(option(v,user.role));});role.append(roleSelect);
          var status=row.insertCell();var statusSelect=document.createElement('select');['pending','approved','suspended'].forEach(function(v){statusSelect.append(option(v,user.status));});status.append(statusSelect);
          var seen=row.insertCell();seen.textContent=user.last_login_at ? new Date(user.last_login_at).toLocaleDateString() : 'Never';
          var action=row.insertCell();var save=document.createElement('button');save.type='button';save.className='user-save';save.textContent='Save';action.append(save);
          save.addEventListener('click',function(){
            save.disabled=true;save.textContent='Saving';
            fetch('/admin/api/users/'+user.id,{method:'PATCH',credentials:'same-origin',headers:{'Content-Type':'application/json'},body:JSON.stringify({role:roleSelect.value,status:statusSelect.value})})
              .then(function(r){return r.json().then(function(data){if(!r.ok)throw new Error(data.error || 'Update failed');});})
              .then(load).catch(function(error){alert(error.message);save.disabled=false;save.textContent='Save';});
          });
        });
      }).catch(function(){body.textContent='';var row=body.insertRow();var cell=row.insertCell();cell.colSpan=5;cell.className='user-empty';cell.textContent='Account list could not be loaded.';});
  }
  load();
})();
</script>"""


def identity_panel(area):
    return (
        f'<div class="account-grid" data-account="{area}">'
        '<div class="account-card"><div class="account-kicker">Signed in as</div>'
        '<p class="account-value" data-account-name>Checking session...</p>'
        '<p class="account-value" data-account-email></p>'
        '<span class="account-role" data-account-role>verifying</span>'
        '<div class="account-state" data-account-state>Validating secure session</div></div>'
        '<div class="account-card"><div class="account-kicker">Session security</div>'
        '<p>GitHub verifies your identity. Platform Ops stores only the account profile, role, and a hashed session token.</p>'
        '<form method="post" action="/auth/logout"><button class="account-signout" type="submit">Sign out</button></form>'
        '</div></div>')


def action(href, title, text, label, external=False):
    attrs = ' target="_blank" rel="noopener noreferrer"' if external else ''
    return (f'<a class="account-action" href="{href}"{attrs}><b>{title}</b>'
            f'<span>{text}</span><i>{label}</i></a>')


def build_page(area, title, tagline, lede, actions, extra_sections="", scripts=""):
    page = render(
        slug=area,
        title=title,
        tagline=tagline,
        eyebrow="Private workspace",
        crumbs=[("Home", "../index.html"), (title, None)],
        meta=["GitHub identity", "Role checked", "No search indexing"],
        sections=section("Identity", "Your secure session", lede, identity_panel(area))
        + extra_sections
        + section("Workspace", "Choose a destination", "Only destinations appropriate to this account are shown here.",
                  '<div class="account-actions">' + ''.join(actions) + '</div>'),
        pager="",
        up="../",
        css="../assets/auth.css",
        canon=f"{area}/",
        robots="noindex,nofollow",
    )
    page = page.replace("</body>", SESSION_SCRIPT + scripts + "\n</body>")
    out = ROOT / area
    out.mkdir(parents=True, exist_ok=True)
    (out / "index.html").write_text(page, encoding="utf-8")


ASSETS.mkdir(parents=True, exist_ok=True)
(ASSETS / "auth.css").write_text(AUTH_CSS, encoding="utf-8")

login_body = (
    '<div class="auth-shell"><div class="auth-mark" aria-hidden="true">GH</div>'
    '<div class="auth-message" role="status" data-auth-message></div>'
    '<h3>Continue securely</h3><p>Use a verified GitHub account. Platform Ops never receives or stores your GitHub password.</p>'
    '<a class="auth-button" href="/auth/github" data-github-login>Continue with GitHub</a>'
    '<div class="auth-note">New accounts enter a pending state. An administrator approves access before private tools become available.</div></div>')
login = render(
    slug="login", title="Member Sign In",
    tagline="One identity, a short-lived session, and no password database.",
    eyebrow="Platform Ops account",
    crumbs=[("Home", "../index.html"), ("Sign in", None)],
    meta=["GitHub OAuth", "Admin approval", "No password stored"],
    sections=section("Sign in", "Access your workspace", "Public knowledge remains open. Sign-in is only for private account tools.", login_body),
    pager="", up="../", css="../assets/auth.css", canon="login/", robots="noindex,nofollow",
)
(ROOT / "login").mkdir(parents=True, exist_ok=True)
(ROOT / "login" / "index.html").write_text(login.replace("</body>", LOGIN_SCRIPT + "\n</body>"), encoding="utf-8")

user_table = (
    '<div class="user-table-wrap"><table class="user-table"><thead><tr>'
    '<th>Account</th><th>Role</th><th>Status</th><th>Last sign-in</th><th>Action</th>'
    '</tr></thead><tbody data-user-list><tr><td colspan="5" class="user-empty">Loading accounts...</td></tr></tbody></table></div>')

build_page(
    "admin", "Admin Console", "Manage access without leaving the Platform Ops site.",
    "This page is available only to approved administrator accounts.",
    [
        action("https://dash.cloudflare.com/", "Cloudflare", "Review Worker deployments, D1 usage, logs, and runtime settings.", "Open dashboard", True),
        action("https://github.com/Vishal-Abhinav/Platform-ops-Newsletter/actions", "Deployments", "Inspect build, browser tests, and production deployment.", "Open GitHub Actions", True),
        action("https://search.google.com/search-console", "Search Console", "Review indexing, sitemap discovery, and search performance.", "Open Search Console", True),
        action("../colophon/index.html", "Build System", "Read the generated architecture and build-stage inventory.", "View colophon"),
    ],
    extra_sections=section("Access", "Approve and manage accounts", "New GitHub identities remain pending until an administrator approves them.", user_table),
    scripts=ADMIN_SCRIPT,
)

build_page(
    "user", "Member Workspace", "A signed-in starting point for approved Platform Ops readers.",
    "This page is available to approved readers and administrators.",
    [
        action("../issues/index.html", "Latest Issues", "Continue with the newest deep dives and production field notes.", "Browse issues"),
        action("../categories/index.html", "Knowledge Map", "Move through the complete topic and category map.", "Explore topics"),
        action("../terminal/index.html", "Practice Terminal", "Work through command exercises in the browser-based lab.", "Open terminal"),
        action("../index.html", "Ops Assistant", "Return to the public site and open the troubleshooting assistant.", "Open assistant"),
    ],
)

print("  auth -> login/index.html, admin/index.html, user/index.html, assets/auth.css")
