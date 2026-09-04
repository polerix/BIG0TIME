(function () {
  const FEATURED_SLUGS = [
    "butterpass",
    "security-adventure",
    "vax-console-sim",
    "kraemeverse-wiki",
    "tornado-cones",
    "satans-spreadsheet",
    "sandrine-portfolio",
    "mobius-farm-ii",
    "aetherstones-council-of-green-point",
    "touski",
    "neutral-zero",
    "pixel-duel-ii",
    "pixel-duel"
  ];

  const PRIVATE_REPO_URLS = new Set([
    "https://github.com/polerix/security-adventure",
    "https://github.com/polerix/purgeclock"
  ]);

  const DELIST_REPO_URLS = new Set([
    "https://github.com/polerix/pixelmonitor",
    "https://github.com/polerix/smrt",
    "https://github.com/ghostwright/phantom",
    "https://github.com/arthur-ficial/apfel",
    "https://github.com/bachili/diffvg",
    "https://github.com/polerix/drone-swarm-sim",
    "https://github.com/polerix/funhaus",
    "https://github.com/polerix/gargoyle",
    "https://github.com/polerix/hailmary",
    "https://github.com/polerix/ports-back-panel-brawl",
    "https://github.com/polerix/perambulators",
    "https://github.com/polerix/roomsim",
    "https://github.com/polerix/voigt-kampff_empathy-test",
    "https://github.com/polerix/eyephone",
    "https://github.com/polerix/m314-tracker",
    "https://github.com/polerix/petscii_game",
    "https://github.com/polerix/poop-boy",
    "https://github.com/polerix/scripts",
    "https://github.com/polerix/streamliner",
    "https://github.com/polerix/valkyr",
    "https://github.com/polerix/vk_console",
    "https://github.com/polerix/ytdl-gui"
  ]);

  const REUSE_SOURCES = {
    "roomsim": "room-stimulator",
    "moovers": "MooVers",
    "voigt-kampff-empathy-test": "voigt-kampff-empathy-test"
  };

  const BROKEN_EXECUTES = new Set([
    "hackers-team",
    "pixelmonitor",
    "m314-tracker",
    "phantom",
    "lucid-reader",
    "bus-broadcaster-swift",
    "apfel",
    "recordmonitor",
    "eyephone",
    "streamliner",
    "obs-projects",
    "drone-swarm-sim",
    "ports-back-panel-brawl",
    "cosmic-brawler",
    "moovers",
    "moof-patrol",
    "bubalina",
    "bpm-vending-pigs",
    "poop-boy",
    "petscii-game",
    "roomsim",
    "aqua-sleeve",
    "hailmary",
    "perambulators",
    "payload-emulator-loop",
    "labyrinth-explorer-1",
    "kung-fu",
    "tmp-nz",
    "moo-shroom",
    "diffvg",
    "c64-os",
    "voigt-kampff-empathy-test",
    "raspberry-pi-fallout",
    "raspberry-pi-2b-commodore-1701-screen",
    "blinkwell-observer",
    "funhaus",
    "gargoyle",
    "valkyr",
    "scripts",
    "last-dance-in-dry-gulcg",
    "maudlin-modellers",
    "glitcher-app",
    "ascii-lab",
    "move-blaster",
    "vk-console",
    "ytdl-gui"
  ]);

  const LINK_OVERRIDES = {
    "maticspirits": {
      execute: "https://polerix.github.io/MaticSpirits/",
      repo: "https://github.com/polerix/MaticSpirits"
    },
    "obstricloner": {
      execute: "https://polerix.github.io/OBSTriCloner/",
      repo: "https://github.com/polerix/OBSTriCloner"
    },
    "hal9000": {
      execute: "https://polerix.github.io/HAL9000/",
      repo: "https://github.com/polerix/HAL9000"
    },
    "voigt-kampff-empathy-test": {
      execute: "",
      repo: "https://github.com/polerix/voigt-kampff-empathy-test"
    },
    "roomsim": {
      execute: "",
      repo: "https://github.com/polerix/room-stimulator"
    },
    "moovers": {
      execute: "",
      repo: "https://github.com/polerix/MooVers"
    }
  };

  const CHANGED_ITEMS = [
    {
      name: "MaticSpirits",
      slug: "maticspirits",
      repo: "https://github.com/polerix/MaticSpirits",
      execute: "https://polerix.github.io/MaticSpirits/",
      description: "Server-backed Matic Spirit generator portal with one-of-one serials, faction skins, duel rites, and a searchable turnaround vault.",
      pushedAt: "2026-09-04T14:18:39Z"
    },
    {
      name: "defrag-tool",
      slug: "defrag-tool",
      repo: "https://github.com/polerix/defrag-tool",
      pushedAt: "2026-09-02T23:24:05Z"
    },
    {
      name: "voigt-kampff-empathy-test",
      slug: "voigt-kampff-empathy-test",
      reuseSlug: "voigt-kampff-empathy-test",
      repo: "https://github.com/polerix/voigt-kampff-empathy-test",
      description: "The Voigt-Kampff Empathy Test as a Python application designed for a normal 80x24 terminal.",
      pushedAt: "2026-09-02T20:48:20Z"
    },
    {
      name: "hackers-team",
      slug: "hackers-team",
      repo: "https://github.com/polerix/hackers-team",
      description: "Hack the Gibson: a Spaceteam-style co-op hacking game set in the world of the 1995 movie Hackers.",
      pushedAt: "2026-09-02T20:48:18Z"
    },
    {
      name: "OBSTriCloner",
      slug: "obstricloner",
      repo: "https://github.com/polerix/OBSTriCloner",
      execute: "https://polerix.github.io/OBSTriCloner/",
      pushedAt: "2026-09-02T20:48:17Z"
    },
    {
      name: "HAL9000",
      slug: "hal9000",
      repo: "https://github.com/polerix/HAL9000",
      execute: "https://polerix.github.io/HAL9000/",
      description: "HAL9000 terminal interface for Raspberry Pi.",
      pushedAt: "2026-09-02T20:32:17Z"
    },
    {
      name: "tony_toni_tone",
      slug: "tony_toni_tone",
      repo: "https://github.com/polerix/tony_toni_tone",
      execute: "https://polerix.github.io/tony_toni_tone/",
      pushedAt: "2026-09-01T22:32:32Z"
    },
    {
      name: "swarm-system-lab",
      slug: "swarm-system-lab",
      repo: "https://github.com/polerix/swarm-system-lab",
      execute: "https://polerix.github.io/swarm-system-lab/",
      description: "Autonomous hive warfare sandbox tuned for GitHub Pages.",
      pushedAt: "2026-09-01T16:57:25Z"
    },
    {
      name: "TornadoConesVR",
      slug: "tornadoconesvr",
      repo: "https://github.com/polerix/TornadoConesVR",
      pushedAt: "2026-08-29T03:03:15Z"
    },
    {
      name: "CosmicWebVR",
      slug: "cosmicwebvr",
      repo: "https://github.com/polerix/CosmicWebVR",
      pushedAt: "2026-08-28T22:01:25Z"
    },
    {
      name: "aqua-sleeve",
      slug: "aqua-sleeve",
      repo: "https://github.com/polerix/aqua-sleeve",
      description: "Sleeve-based personality and memory management for an AI agent.",
      pushedAt: "2026-08-21T10:38:38Z"
    },
    {
      name: "ServoSkull",
      slug: "servoskull",
      repo: "https://github.com/polerix/ServoSkull",
      execute: "https://polerix.github.io/ServoSkull/",
      description: "Working online and offline on the ServoSkull project.",
      pushedAt: "2026-08-17T17:08:19Z"
    }
  ];

  const MISSING_ITEMS = [
    { name: "room-stimulator", slug: "room-stimulator", reuseSlug: "roomsim", repo: "https://github.com/polerix/room-stimulator", description: "Its a room.", pushedAt: "2026-08-15T18:31:30Z" },
    { name: "MooVers", slug: "moovers", reuseSlug: "moovers", repo: "https://github.com/polerix/MooVers", description: "Games in the MooVerse.", pushedAt: "2026-08-14T00:50:25Z" },
    { name: "DisplayGuardDog", slug: "displayguarddog", repo: "https://github.com/polerix/DisplayGuardDog", description: "Keeps your screens from moving around over KVM switching.", pushedAt: "2026-07-09T18:57:32Z" },
    { name: "skills-github-pages", slug: "skills-github-pages", repo: "https://github.com/polerix/skills-github-pages", description: "My clone repository for pages.", pushedAt: "2026-07-01T22:16:16Z" },
    { name: "pilbo", slug: "pilbo", repo: "https://github.com/polerix/pilbo", description: "Help the Magus Aurelius feed the homunculus Pilbo to see what the newly made magic pills do.", pushedAt: "2026-06-27T19:55:04Z" },
    { name: "fishbone", slug: "fishbone", repo: "https://github.com/polerix/fishbone", description: "Fishbone diagram.", pushedAt: "2026-06-12T14:56:00Z" },
    { name: "comedia", slug: "comedia", repo: "https://github.com/polerix/comedia", description: "Fun surveys.", pushedAt: "2026-05-16T22:44:00Z" },
    { name: "Arr-Type", slug: "arr-type", repo: "https://github.com/polerix/Arr-Type", description: "R-Type clone with pirate theme.", pushedAt: "2026-04-05T01:13:07Z" },
    { name: "Egg_Rush", slug: "egg-rush", repo: "https://github.com/polerix/Egg_Rush", description: "Get eggs before the goat does.", pushedAt: "2026-04-01T21:41:38Z" },
    { name: "voight-kampff-model", slug: "voight-kampff-model", repo: "https://github.com/polerix/voight-kampff-model", pushedAt: "2026-03-27T17:13:42Z" },
    { name: "cosmo", slug: "cosmo", repo: "https://github.com/polerix/cosmo", pushedAt: "2026-03-17T11:18:03Z" },
    { name: "c64upgrade", slug: "c64upgrade", repo: "https://github.com/polerix/c64upgrade", description: "Tracking work with c64 upgrade.", pushedAt: "2026-02-02T11:39:26Z" },
    { name: "MaudlinModellers", slug: "maudlinmodellers", repo: "https://github.com/polerix/MaudlinModellers", description: "Tracking electronics and hardware in Maudlin Modellers.", pushedAt: "2026-02-01T13:39:54Z" },
    { name: "stronkbot", slug: "stronkbot", repo: "https://github.com/polerix/stronkbot", description: "A side scroller mech game.", pushedAt: "2026-01-31T23:27:07Z" },
    { name: "MooShoother", slug: "mooshoother", repo: "https://github.com/polerix/MooShoother", pushedAt: "2026-01-30T19:08:09Z" },
    { name: "skills-introduction-to-github", slug: "skills-introduction-to-github", repo: "https://github.com/polerix/skills-introduction-to-github", description: "My clone repository for GitHub intro.", pushedAt: "2025-12-18T18:22:57Z" },
    { name: "moo", slug: "moo", repo: "https://github.com/polerix/moo", description: "Games in development.", pushedAt: "2024-07-22T13:44:20Z" },
    { name: "GitBag", slug: "gitbag", repo: "https://github.com/polerix/GitBag", description: "Pithon and Node-red dev.", pushedAt: "2024-05-17T22:03:18Z" },
    { name: "soundboard", slug: "soundboard", repo: "https://github.com/polerix/soundboard", description: "Soundboard for dungeons and dragons.", pushedAt: "2024-05-17T22:03:04Z" },
    { name: "Octoprint_Setup", slug: "octoprint-setup", repo: "https://github.com/polerix/Octoprint_Setup", description: "Where I keep my Octoprint instance setup.", pushedAt: "2024-05-17T22:02:09Z" },
    { name: "Telepod-Teleprompter", slug: "telepod-teleprompter", repo: "https://github.com/polerix/Telepod-Teleprompter", description: "A multi-layer teleprompter with variable web page backgrounds.", pushedAt: "2024-05-17T22:02:03Z" },
    { name: "Millenium-Falcon-Control", slug: "millenium-falcon-control", repo: "https://github.com/polerix/Millenium-Falcon-Control", description: "To control a Raspberry Pi in a Millenium Falcon.", pushedAt: "2024-05-17T22:01:48Z" },
    { name: "dirtygenerator", slug: "dirtygenerator", repo: "https://github.com/polerix/dirtygenerator", description: "Small web page that generates memes.", pushedAt: "2024-05-17T22:01:36Z" },
    { name: "demo", slug: "demo", repo: "https://github.com/polerix/demo", description: "Testing stuff.", pushedAt: "2024-03-27T16:58:20Z" },
    { name: "sarlacc", slug: "sarlacc", repo: "https://github.com/polerix/sarlacc", description: "The sarlacc pit of the git.", pushedAt: "2022-06-01T14:24:00Z" },
    { name: "JouetLeMarchand", slug: "jouetlemarchand", repo: "https://github.com/polerix/JouetLeMarchand", description: "Lemarchand Puzzle Box.", pushedAt: "2012-10-22T13:49:53Z" }
  ];

  function normalizeSlug(value) {
    return String(value || "")
      .trim()
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, "-")
      .replace(/^-+|-+$/g, "");
  }

  function normalizeUrl(value) {
    return String(value || "").trim().replace(/\/+$/, "").toLowerCase();
  }

  function escapeHtml(value) {
    return String(value || "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function formatDate(iso) {
    const date = new Date(iso);
    return date.toLocaleDateString("en-US", {
      year: "numeric",
      month: "long",
      day: "numeric",
      timeZone: "UTC"
    });
  }

  function describe(meta) {
    if (meta.description && meta.description.trim()) {
      return meta.description.trim();
    }
    return "Updated " + formatDate(meta.pushedAt) + ".";
  }

  function setButtons(card, meta, category) {
    const actions = card.querySelector(".actions");
    if (!actions) return;

    const repoUrl = normalizeUrl(meta.repo);
    const executeUrl = meta.execute || "";
    const isPrivateRepo = PRIVATE_REPO_URLS.has(repoUrl);
    const bits = [];

    if (executeUrl) {
      bits.push(
        '<a href="' + escapeHtml(executeUrl) + '" target="_blank" rel="noopener noreferrer"><button class="lcars-btn open-btn">EXECUTE</button></a>'
      );
    }

    if (!isPrivateRepo && meta.repo) {
      bits.push(
        '<a href="' + escapeHtml(meta.repo) + '" target="_blank" rel="noopener noreferrer"><button class="lcars-btn repo-btn">REPOS</button></a>'
      );
    }

    if (!bits.length && meta.repo) {
      bits.push(
        '<a href="' + escapeHtml(meta.repo) + '" target="_blank" rel="noopener noreferrer"><button class="lcars-btn repo-btn">REPOS</button></a>'
      );
    }

    actions.innerHTML = bits.join("");

    const badgeWrap = card.querySelector(".card-badges");
    if (!badgeWrap) return;

    if (category === "pinned") {
      badgeWrap.innerHTML = '<span class="lcars-tag tag-pinned">🥇 FEATURED</span>' + (executeUrl ? ' <span class="lcars-tag tag-static">🌐 LIVE</span>' : "");
      return;
    }

    if (category === "changed") {
      badgeWrap.innerHTML = '<span class="lcars-tag tag-recent">🆕 ' + escapeHtml(formatDate(meta.pushedAt)) + "</span>" +
        (executeUrl ? ' <span class="lcars-tag tag-static">🌐 PAGES</span>' : ' <span class="lcars-tag tag-muted">📦 REPO</span>');
      return;
    }

    badgeWrap.innerHTML = executeUrl
      ? '<span class="lcars-tag tag-static">🌐 PAGES</span>'
      : '<span class="lcars-tag tag-muted">📦 REPO</span>';
  }

  function updateCard(card, meta, category, sysId) {
    card.dataset.name = meta.slug || normalizeSlug(meta.name);
    card.dataset.category = category;
    card.dataset.search = (meta.name + " " + describe(meta)).toLowerCase();
    card.classList.remove("pinned");
    card.classList.toggle("muted", !meta.execute);
    if (category === "pinned") {
      card.classList.add("pinned");
    }

    const idNode = card.querySelector(".sys-id");
    if (idNode && sysId) idNode.textContent = sysId;
    const nameNode = card.querySelector(".name");
    if (nameNode) nameNode.textContent = meta.name;
    const descNode = card.querySelector(".desc");
    if (descNode) descNode.textContent = describe(meta);
    setButtons(card, meta, category);
    return card;
  }

  function createCard(meta, category, sysId) {
    const card = document.createElement("div");
    card.className = meta.execute ? "bubble" : "bubble muted";
    card.innerHTML =
      '<div class="card-header">' +
        '<span class="sys-id"></span>' +
        '<div class="card-badges"></div>' +
      "</div>" +
      '<div class="name"></div>' +
      '<div class="desc"></div>' +
      '<div class="actions"></div>';
    return updateCard(card, meta, category, sysId);
  }

  function extractMeta(card) {
    const nameText = card.querySelector(".name") ? card.querySelector(".name").textContent.trim() : "";
    const slug = normalizeSlug(card.dataset.name || nameText);
    const repoAnchor = card.querySelector(".repo-btn") ? card.querySelector(".repo-btn").closest("a") : null;
    const openAnchor = card.querySelector(".open-btn") ? card.querySelector(".open-btn").closest("a") : null;
    const override = LINK_OVERRIDES[slug] || {};
    const repo = override.repo || (repoAnchor ? repoAnchor.href : "");
    const execute = override.execute !== undefined ? override.execute : (openAnchor ? openAnchor.href : "");
    return {
      name: nameText || slug,
      slug: slug,
      repo: repo,
      execute: BROKEN_EXECUTES.has(slug) && override.execute === undefined ? "" : execute,
      description: card.querySelector(".desc") ? card.querySelector(".desc").textContent.trim() : "",
      pushedAt: "2026-09-04T00:00:00Z"
    };
  }

  window.applyBig0Catalog = function applyBig0Catalog() {
    const pinnedGrid = document.getElementById("grid-pinned");
    const changedGrid = document.getElementById("grid-business");
    const whateverGrid = document.getElementById("grid-games");
    const toyGrid = document.getElementById("grid-toys");
    const toySection = document.getElementById("sec-toys");
    const pinnedHeader = pinnedGrid && pinnedGrid.previousElementSibling;
    const changedHeader = document.getElementById("sec-business");
    const whateverHeader = document.getElementById("sec-games");

    if (!pinnedGrid || !changedGrid || !whateverGrid) return;

    const allCards = Array.from(document.querySelectorAll(".bubble"));
    const bySlug = new Map();

    allCards.forEach(function (card) {
      const meta = extractMeta(card);
      card.dataset.slug = meta.slug;
      if (!bySlug.has(meta.slug)) bySlug.set(meta.slug, []);
      bySlug.get(meta.slug).push(card);
    });

    const used = new Set();

    function shouldDelist(card) {
      const meta = extractMeta(card);
      const repoUrl = normalizeUrl(meta.repo);
      return DELIST_REPO_URLS.has(repoUrl) && !REUSE_SOURCES[meta.slug];
    }

    function pickExisting(slug) {
      const list = bySlug.get(slug) || [];
      for (let i = 0; i < list.length; i += 1) {
        const card = list[i];
        if (!used.has(card) && !shouldDelist(card)) {
          used.add(card);
          return card;
        }
      }
      return null;
    }

    allCards.forEach(function (card) {
      if (shouldDelist(card)) {
        card.remove();
      }
    });

    pinnedGrid.innerHTML = "";
    changedGrid.innerHTML = "";
    whateverGrid.innerHTML = "";
    if (toyGrid) toyGrid.innerHTML = "";
    if (toySection) toySection.style.display = "none";
    if (toyGrid) toyGrid.style.display = "none";

    FEATURED_SLUGS.forEach(function (slug, index) {
      const card = pickExisting(slug);
      if (!card) return;
      const meta = extractMeta(card);
      meta.execute = LINK_OVERRIDES[slug] && LINK_OVERRIDES[slug].execute !== undefined ? LINK_OVERRIDES[slug].execute : meta.execute;
      if (!meta.execute) return;
      updateCard(card, meta, "pinned", "LCARS-PRIORITY-" + String(index + 1).padStart(2, "0"));
      pinnedGrid.appendChild(card);
    });

    CHANGED_ITEMS.forEach(function (item, index) {
      const sourceSlug = item.reuseSlug || item.slug;
      const card = pickExisting(sourceSlug) || createCard(item, "changed", "");
      const meta = Object.assign({}, extractMeta(card), item);
      updateCard(card, meta, "changed", "LCARS-NEW-" + String(index + 1).padStart(3, "0"));
      changedGrid.appendChild(card);
    });

    const extraCards = [];
    allCards.forEach(function (card) {
      if (used.has(card) || shouldDelist(card)) return;
      const meta = extractMeta(card);
      if (FEATURED_SLUGS.indexOf(meta.slug) !== -1) return;
      if (CHANGED_ITEMS.some(function (item) { return (item.reuseSlug || item.slug) === meta.slug; })) return;
      meta.execute = LINK_OVERRIDES[meta.slug] && LINK_OVERRIDES[meta.slug].execute !== undefined ? LINK_OVERRIDES[meta.slug].execute : meta.execute;
      if (BROKEN_EXECUTES.has(meta.slug) && !(LINK_OVERRIDES[meta.slug] && LINK_OVERRIDES[meta.slug].execute)) {
        meta.execute = "";
      }
      extraCards.push(updateCard(card, meta, "whatever", card.querySelector(".sys-id") ? card.querySelector(".sys-id").textContent : ""));
    });

    MISSING_ITEMS.forEach(function (item, index) {
      const inChanged = CHANGED_ITEMS.some(function (changed) { return changed.slug === item.slug; });
      if (inChanged) return;
      const card = pickExisting(item.reuseSlug || item.slug) || createCard(item, "whatever", "");
      const meta = Object.assign({}, extractMeta(card), item, { execute: item.execute || "" });
      extraCards.push(updateCard(card, meta, "whatever", "LCARS-ARC-" + String(index + 1).padStart(3, "0")));
    });

    extraCards
      .sort(function (a, b) {
        const left = (a.querySelector(".name") ? a.querySelector(".name").textContent : "").toLowerCase();
        const right = (b.querySelector(".name") ? b.querySelector(".name").textContent : "").toLowerCase();
        return left.localeCompare(right);
      })
      .forEach(function (card) {
        whateverGrid.appendChild(card);
      });

    if (pinnedHeader) {
      const text = pinnedHeader.querySelector(".lcars-header-text");
      if (text) text.textContent = "01 // PINNED SITES (" + pinnedGrid.children.length + " NODES)";
    }
    if (changedHeader) {
      const text = changedHeader.querySelector(".lcars-header-text");
      if (text) text.textContent = "02 // NEWLY CHANGED (" + changedGrid.children.length + " NODES)";
    }
    if (whateverHeader) {
      const text = whateverHeader.querySelector(".lcars-header-text");
      if (text) text.textContent = "03 // WHATEVER (" + whateverGrid.children.length + " NODES)";
    }
  };
})();
