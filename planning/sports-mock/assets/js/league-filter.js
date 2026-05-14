/* ============================================================
   League / division filter + GA4 event wiring
   ------------------------------------------------------------
   Markup contract (matches Claude Design HTML):

     <div class="filter-row" role="tablist">
       <button class="filter-chip is-active" data-filter="all">…</button>
       <button class="filter-chip" data-filter="al">…</button>
       …
     </div>

     Cards within the same .sec that carry data-league="<key>" are
     shown/hidden based on the active chip. data-filter="all" shows all.

   Events fired (gtag + dataLayer):
     - theme_page_view       on load (body[data-theme], data-page-type)
     - theme_to_ac_click     on [data-ga-ac] click
     - genre_card_click      on [data-ga-genre] click
     - league_filter_click   on filter-chip click
   ============================================================ */
(function () {
  function fireEvent(name, params) {
    if (window.gtag) window.gtag("event", name, params);
    if (window.dataLayer) window.dataLayer.push(Object.assign({ event: name }, params));
  }

  function setupFilters() {
    document.querySelectorAll('.filter-row[role="tablist"]').forEach(function (row) {
      var chips = row.querySelectorAll(".filter-chip[data-filter]");
      var scope = row.closest(".sec") || document;
      var cards = scope.querySelectorAll("[data-league]");
      if (!chips.length || !cards.length) return;

      chips.forEach(function (chip) {
        chip.addEventListener("click", function () {
          var key = chip.getAttribute("data-filter") || "all";
          chips.forEach(function (c) { c.classList.remove("is-active"); });
          chip.classList.add("is-active");
          cards.forEach(function (card) {
            var match = key === "all" || card.getAttribute("data-league") === key;
            card.style.display = match ? "" : "none";
          });
          fireEvent("league_filter_click", { filter_value: key });
        });
      });
    });
  }

  function setupDisabled() {
    document.querySelectorAll(".is-soon, [aria-disabled='true']").forEach(function (el) {
      if (el.tagName !== "A") return;
      el.addEventListener("click", function (e) { e.preventDefault(); });
      if (!el.getAttribute("title")) el.setAttribute("title", "順次公開予定");
    });
  }

  function setupGAClicks() {
    var theme = document.body.getAttribute("data-theme") || "";

    document.querySelectorAll("[data-ga-ac]").forEach(function (el) {
      el.addEventListener("click", function () {
        fireEvent("theme_to_ac_click", {
          theme_name: theme,
          ac_id: el.getAttribute("data-ga-ac") || "",
          card_position: el.getAttribute("data-ga-pos") || ""
        });
      });
    });

    document.querySelectorAll("[data-ga-genre]").forEach(function (el) {
      el.addEventListener("click", function () {
        fireEvent("genre_card_click", {
          genre_name: el.getAttribute("data-ga-genre") || "",
          card_position: el.getAttribute("data-ga-pos") || ""
        });
      });
    });
  }

  function firePageView() {
    var theme = document.body.getAttribute("data-theme");
    if (!theme) return;
    fireEvent("theme_page_view", {
      theme_name: theme,
      page_type: document.body.getAttribute("data-page-type") || ""
    });
  }

  function setupAnchorNav() {
    var anchorBar = document.getElementById("page-anchor");
    if (!anchorBar) return;
    var links = anchorBar.querySelectorAll("a");
    var sections = [];
    links.forEach(function (a) {
      var s = document.querySelector(a.getAttribute("href"));
      if (s) sections.push(s);
    });
    if (!sections.length) return;
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) {
          var id = "#" + e.target.id;
          links.forEach(function (l) {
            l.classList.toggle("is-current", l.getAttribute("href") === id);
          });
        }
      });
    }, { rootMargin: "-50% 0px -40% 0px" });
    sections.forEach(function (s) { io.observe(s); });
  }

  function init() {
    setupFilters();
    setupDisabled();
    setupGAClicks();
    setupAnchorNav();
    firePageView();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
