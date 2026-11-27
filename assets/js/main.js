(() => {
  // Sticky header hairline once the page has scrolled (IntersectionObserver, no scroll listener).
  const header = document.querySelector(".site-header");
  const sentinel = document.createElement("div");
  sentinel.style.cssText = "position:absolute;top:0;height:1px;width:1px";
  document.body.prepend(sentinel);
  new IntersectionObserver(([e]) => header.classList.toggle("scrolled", !e.isIntersecting)).observe(sentinel);

  // Mobile nav
  const toggle = document.querySelector(".nav-toggle");
  const links = document.querySelector(".nav-links");
  toggle?.addEventListener("click", () => {
    const open = links.classList.toggle("open");
    toggle.setAttribute("aria-expanded", String(open));
  });

  links?.addEventListener("click", (event) => {
    if (!event.target.closest("a")) return;
    links.classList.remove("open");
    toggle?.setAttribute("aria-expanded", "false");
  });
  document.addEventListener("keydown", (event) => {
    if (event.key !== "Escape" || !links?.classList.contains("open")) return;
    links.classList.remove("open");
    toggle?.setAttribute("aria-expanded", "false");
    toggle?.focus();
  });

  // Reveal on scroll
  const io = new IntersectionObserver((entries) => {
    for (const e of entries) {
      if (e.isIntersecting) { e.target.classList.add("in"); io.unobserve(e.target); }
    }
  }, { threshold: 0.15, rootMargin: "0px 0px -40px 0px" });
  const revealables = document.querySelectorAll(".reveal, .mask-in, .track");
  revealables.forEach((el) => io.observe(el));
  // Failsafe: anything already on screen is shown even if the observer never reports it.
  const showVisible = () => revealables.forEach((el) => {
    const r = el.getBoundingClientRect();
    if (r.top < innerHeight && r.bottom > 0) el.classList.add("in");
  });
  requestAnimationFrame(() => requestAnimationFrame(showVisible));
  setTimeout(showVisible, 1500);

  const calm = matchMedia("(prefers-reduced-motion: reduce)").matches;

  document.querySelectorAll("[data-ambient-video]").forEach((video) => {
    const button = document.querySelector(`[data-film-toggle][aria-controls="${video.id}"]`);
    const label = video.id === "hero-film" ? "hero" : "workplace";
    const sync = () => {
      if (!button) return;
      button.textContent = video.paused ? "Play video" : "Pause video";
      button.setAttribute("aria-label", `${video.paused ? "Play" : "Pause"} ${label} video`);
    };
    video.muted = true;
    video.addEventListener("play", sync);
    video.addEventListener("pause", sync);
    button?.addEventListener("click", () => {
      if (video.paused) video.play().catch(sync);
      else video.pause();
    });
    if (calm) { video.autoplay = false; video.pause(); }
    else video.play().catch(sync);
    sync();
  });

  // Hero: rotating word in the headline
  const rot = document.querySelector(".rot");
  if (rot && !calm) {
    const words = [...rot.children];
    let i = 0;
    words[0].classList.add("on");
    setInterval(() => {
      const cur = words[i];
      cur.classList.remove("on"); cur.classList.add("off");
      setTimeout(() => cur.classList.remove("off"), 600);
      i = (i + 1) % words.length;
      words[i].classList.add("on");
    }, 2600);
  }

  // Hero: greeting bubble types a new hello every few seconds
  const say = document.querySelector(".bubble .say");
  const typing = document.querySelector(".bubble .typing");
  if (say && typing && !calm) {
    const hellos = JSON.parse(say.dataset.words || "[]");
    let k = 0;
    setInterval(() => {
      say.hidden = true; typing.hidden = false;
      setTimeout(() => {
        k = (k + 1) % hellos.length;
        say.textContent = hellos[k];
        typing.hidden = true; say.hidden = false;
      }, 900);
    }, 3200);
  }

  // Pointer effects (fine pointers only): card spotlight, button fill origin
  if (matchMedia("(pointer: fine)").matches && !calm) {
    document.querySelectorAll(".card").forEach((c) => c.addEventListener("pointermove", (ev) => {
      const r = c.getBoundingClientRect();
      c.style.setProperty("--sx", `${ev.clientX - r.left}px`);
      c.style.setProperty("--sy", `${ev.clientY - r.top}px`);
    }));
    document.querySelectorAll(".btn-primary").forEach((b) => b.addEventListener("pointerenter", (ev) => {
      const r = b.getBoundingClientRect();
      b.style.setProperty("--mx", `${ev.clientX - r.left}px`);
      b.style.setProperty("--my", `${ev.clientY - r.top}px`);
    }));
  }

  // Tabs (Our values / Working here)
  const tabs = [...document.querySelectorAll('[role="tab"]')];
  const select = (t) => {
    tabs.forEach((x) => {
      const on = x === t;
      x.setAttribute("aria-selected", String(on));
      x.tabIndex = on ? 0 : -1;
      document.getElementById(x.getAttribute("aria-controls")).hidden = !on;
    });
  };
  tabs.forEach((t, i) => {
    t.addEventListener("click", () => select(t));
    t.addEventListener("keydown", (ev) => {
      if (ev.key !== "ArrowRight" && ev.key !== "ArrowLeft") return;
      const n = tabs[(i + (ev.key === "ArrowRight" ? 1 : tabs.length - 1)) % tabs.length];
      select(n); n.focus();
    });
  });

  // Careers: filter openings by office
  const chips = document.querySelectorAll("[data-filter]");
  chips.forEach((chip) => chip.addEventListener("click", () => {
    const f = chip.dataset.filter;
    chips.forEach((c) => c.setAttribute("aria-pressed", String(c === chip)));
    let shown = 0;
    document.querySelectorAll(".job").forEach((j) => {
      const ok = f === "all" || j.dataset.office === f;
      j.hidden = !ok;
      if (ok) shown++;
    });
    const none = document.getElementById("no-match");
    if (none) none.hidden = shown !== 0;
  }));

  // Enquiry form
  const form = document.getElementById("enquiry");
  if (!form) return;
  const status = form.querySelector(".form-status");
  const show = (cls, msg) => { status.className = "form-status show " + cls; status.textContent = msg; };
  form.addEventListener("submit", async (ev) => {
    ev.preventDefault();
    let valid = true;
    form.querySelectorAll(".field").forEach((f) => {
      const input = f.querySelector("input, select, textarea");
      const ok = input.checkValidity();
      f.classList.toggle("invalid", !ok);
      if (!ok && valid) { input.focus(); valid = false; }
    });
    if (!valid) return;

    const endpoint = form.dataset.endpoint;
    const email = form.dataset.email;
    const data = new FormData(form);
    if (endpoint) {
      const btn = form.querySelector("button[type=submit]");
      btn.disabled = true; btn.textContent = "Sending...";
      try {
        const res = await fetch(endpoint, { method: "POST", body: data, headers: { Accept: "application/json" } });
        if (!res.ok) throw new Error(String(res.status));
        form.reset();
        show("ok", "Thanks, we have your message. Someone from our team will call you back within one working day.");
      } catch {
        show("warn", "That did not go through. Please try again, or call the office nearest to you.");
      } finally {
        btn.disabled = false; btn.textContent = "Send message";
      }
    } else if (email) {
      const body = [...data.entries()].map(([k, v]) => `${k}: ${v}`).join("\n");
      location.href = `mailto:${email}?subject=${encodeURIComponent("Website enquiry: " + data.get("userSelect"))}&body=${encodeURIComponent(body)}`;
    } else {
      show("warn", "Online enquiries are not switched on yet. Please call one of our offices listed on this page.");
    }
  });
  form.querySelectorAll("input, select, textarea").forEach((el) =>
    el.addEventListener("input", () => el.closest(".field").classList.remove("invalid")));
})();
