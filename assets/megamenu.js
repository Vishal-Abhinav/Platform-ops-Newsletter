var PO_NAV = {"pillars":[{"name":"Foundation","cats":[{"name":"Foundation","icon":"🧱","href":"categories/foundation/index.html","live":7,"pipe":0,"plan":3}],"live":7,"pipe":0},{"name":"Infrastructure","cats":[{"name":"IT Infrastructure","icon":"🏗️","href":"categories/it-infrastructure/index.html","live":0,"pipe":5,"plan":7},{"name":"Storage","icon":"💽","href":"categories/storage/index.html","live":1,"pipe":2,"plan":12},{"name":"Virtualization","icon":"🖥️","href":"categories/virtualization/index.html","live":0,"pipe":1,"plan":10}],"live":1,"pipe":8},{"name":"Networking","cats":[{"name":"Networking","icon":"🌐","href":"categories/networking/index.html","live":1,"pipe":4,"plan":26}],"live":1,"pipe":4},{"name":"Cloud","cats":[{"name":"Cloud","icon":"☁️","href":"categories/cloud/index.html","live":0,"pipe":4,"plan":13}],"live":0,"pipe":4},{"name":"Delivery","cats":[{"name":"DevOps","icon":"⚙️","href":"categories/devops/index.html","live":9,"pipe":5,"plan":7},{"name":"Containers","icon":"📦","href":"categories/containers/index.html","live":0,"pipe":6,"plan":6},{"name":"Infrastructure as Code","icon":"📐","href":"categories/infrastructure-as-code/index.html","live":0,"pipe":3,"plan":8},{"name":"Configuration Management","icon":"🔧","href":"categories/configuration-management/index.html","live":0,"pipe":3,"plan":9},{"name":"GitOps","icon":"🔀","href":"categories/gitops/index.html","live":3,"pipe":2,"plan":3},{"name":"Platform Engineering","icon":"🛠️","href":"categories/platform-engineering/index.html","live":0,"pipe":3,"plan":9}],"live":12,"pipe":22},{"name":"Kubernetes","cats":[{"name":"Kubernetes","icon":"☸️","href":"categories/kubernetes/index.html","live":16,"pipe":13,"plan":6},{"name":"OpenShift","icon":"🔴","href":"categories/openshift/index.html","live":2,"pipe":2,"plan":9},{"name":"Service Mesh","icon":"🕸️","href":"categories/service-mesh/index.html","live":0,"pipe":2,"plan":8}],"live":18,"pipe":17},{"name":"Reliability","cats":[{"name":"SRE","icon":"📡","href":"categories/sre/index.html","live":4,"pipe":8,"plan":13},{"name":"Observability","icon":"📊","href":"categories/observability/index.html","live":11,"pipe":4,"plan":7},{"name":"Logging","icon":"📜","href":"categories/logging/index.html","live":2,"pipe":3,"plan":9},{"name":"Performance Engineering","icon":"⚡","href":"categories/performance-engineering/index.html","live":4,"pipe":2,"plan":6},{"name":"Troubleshooting","icon":"🔍","href":"categories/troubleshooting/index.html","live":5,"pipe":2,"plan":5},{"name":"Backup & DR","icon":"🗄️","href":"categories/backup-dr/index.html","live":0,"pipe":4,"plan":12},{"name":"ITSM & Operations","icon":"🎫","href":"categories/itsm-operations/index.html","live":1,"pipe":2,"plan":12}],"live":27,"pipe":25},{"name":"Security","cats":[{"name":"Security","icon":"🛡️","href":"categories/security/index.html","live":0,"pipe":11,"plan":20},{"name":"Supply Chain Security","icon":"🔗","href":"categories/supply-chain-security/index.html","live":0,"pipe":7,"plan":8}],"live":0,"pipe":18},{"name":"Data & Applications","cats":[{"name":"Database","icon":"🗃️","href":"categories/database/index.html","live":0,"pipe":3,"plan":13},{"name":"Middleware","icon":"🧩","href":"categories/middleware/index.html","live":0,"pipe":3,"plan":11},{"name":"API & Microservices","icon":"🔌","href":"categories/api-microservices/index.html","live":0,"pipe":4,"plan":12},{"name":"Distributed Systems","icon":"🕮","href":"categories/distributed-systems/index.html","live":1,"pipe":2,"plan":11}],"live":1,"pipe":12},{"name":"Modern Ops","cats":[{"name":"AI Infrastructure","icon":"🤖","href":"categories/ai-infrastructure/index.html","live":0,"pipe":6,"plan":14},{"name":"AIOps","icon":"🧠","href":"categories/aiops/index.html","live":0,"pipe":4,"plan":10},{"name":"FinOps","icon":"💰","href":"categories/finops/index.html","live":0,"pipe":5,"plan":6},{"name":"Automation","icon":"🔁","href":"categories/automation/index.html","live":3,"pipe":3,"plan":6},{"name":"Architecture","icon":"🏛️","href":"categories/architecture/index.html","live":0,"pipe":3,"plan":9}],"live":3,"pipe":21}],"quick":[{"label":"All Categories","href":"categories/index.html"},{"label":"Reference Library","href":"index.html#library"},{"label":"Knowledge Map","href":"index.html#topics"},{"label":"Latest Issues","href":"index.html#issues"},{"label":"Subscribe","href":"index.html#subscribe"}]};
/* Site-wide mega-menu. Injected into whatever <nav> the page already has,
   so no page needs its own markup. Depth comes from data-root on this tag. */
(function () {
  var me = document.currentScript ||
           document.querySelector('script[src$="megamenu.js"]');
  var ROOT = (me && me.getAttribute('data-root')) || '';

  function el(tag, cls, html) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (html != null) e.innerHTML = html;
    return e;
  }

  try { build(PO_NAV); } catch (e) { /* nav is an enhancement, not load-bearing */ }

  function build(data) {
    var nav = document.querySelector('nav');
    if (!nav) return;

    var btn = el('button', 'mm-btn');
    btn.type = 'button';
    btn.setAttribute('aria-expanded', 'false');
    btn.setAttribute('aria-haspopup', 'true');
    btn.innerHTML = '<i><span></span></i>Browse';

    var scrim = el('div', 'mm-scrim');
    var panel = el('div', 'mm');
    panel.setAttribute('role', 'dialog');
    panel.setAttribute('aria-label', 'Browse all categories');

    var left = el('div', 'mm-l');
    var right = el('div', 'mm-r');
    var foot = el('div', 'mm-foot');

    data.pillars.forEach(function (p, i) {
      var b = el('button', 'mm-p');
      b.type = 'button';
      b.setAttribute('role', 'tab');
      b.setAttribute('aria-selected', i === 0 ? 'true' : 'false');
      b.innerHTML = '<span class="n">' + String(i + 1).padStart(2, '0') + '</span>' +
                    '<span class="t">' + p.name + '</span>' +
                    (p.live ? '<span class="c">' + p.live + '</span>' : '') +
                    '<span class="a">›</span>';
      var show = function () {
        left.querySelectorAll('.mm-p').forEach(function (x) {
          x.setAttribute('aria-selected', 'false');
        });
        b.setAttribute('aria-selected', 'true');
        paint(p);
      };
      b.addEventListener('mouseenter', show);
      b.addEventListener('focus', show);
      b.addEventListener('click', show);
      left.appendChild(b);
    });

    function paint(p) {
      right.innerHTML = '';
      right.appendChild(el('div', 'mm-head',
        p.name + ' — ' + p.cats.length + ' categor' + (p.cats.length === 1 ? 'y' : 'ies') +
        ' · ' + p.live + ' live · ' + p.pipe + ' in pipeline'));
      var grid = el('div', 'mm-grid');
      p.cats.forEach(function (c) {
        var a = el('a', 'mm-c');
        a.href = ROOT + c.href;
        a.innerHTML = '<span class="ico">' + c.icon + '</span><span>' +
          '<span class="nm">' + c.name + '</span>' +
          '<span class="sub">' + (c.live ? '<b>' + c.live + ' live</b> · ' : '') +
          c.pipe + ' pipe · ' + c.plan + ' planned</span></span>';
        grid.appendChild(a);
      });
      right.appendChild(grid);
    }
    paint(data.pillars[0]);

    data.quick.forEach(function (q) {
      var a = el('a', null, q.label);
      a.href = ROOT + q.href;
      foot.appendChild(a);
    });

    panel.appendChild(left);
    panel.appendChild(right);
    panel.appendChild(foot);
    document.body.appendChild(scrim);
    document.body.appendChild(panel);

    /* Anchor under the nav, clamped to the viewport. Fixed positioning, so it
       is measured from the button rather than nested inside a nav that may be
       backdrop-filtered — a filter creates a containing block and would trap
       an absolutely positioned panel inside it. */
    function place() {
      var r = btn.getBoundingClientRect();
      var w = Math.min(900, window.innerWidth - 24);
      panel.style.width = w + 'px';
      panel.style.top = Math.round(r.bottom + 8) + 'px';
      panel.style.left = Math.round(
        Math.max(12, Math.min(r.left, window.innerWidth - w - 12))) + 'px';
    }

    function open(on) {
      btn.setAttribute('aria-expanded', on ? 'true' : 'false');
      panel.classList.toggle('on', on);
      scrim.classList.toggle('on', on);
      if (on) place();
    }

    btn.addEventListener('click', function (e) {
      e.stopPropagation();
      open(btn.getAttribute('aria-expanded') !== 'true');
    });
    scrim.addEventListener('click', function () { open(false); });
    panel.addEventListener('click', function (e) { e.stopPropagation(); });
    document.addEventListener('click', function () { open(false); });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') { open(false); btn.focus(); }
    });
    window.addEventListener('resize', function () {
      if (panel.classList.contains('on')) place();
    });
    window.addEventListener('scroll', function () {
      if (panel.classList.contains('on')) place();
    }, { passive: true });

    /* Put it next to the logo where there's room, else at the end of the nav. */
    var logo = nav.querySelector('.nav-logo');
    if (logo && logo.parentNode === nav) logo.insertAdjacentElement('afterend', btn);
    else nav.appendChild(btn);
  }
})();
