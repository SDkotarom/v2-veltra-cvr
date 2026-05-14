/* ============================================================
   League / district pill filter
   ------------------------------------------------------------
   Markup contract:

   <div class="pill-row" data-filter-group="leagues">
     <button class="pill-btn is-active" data-filter="*">すべて</button>
     <button class="pill-btn" data-filter="premier">プレミアリーグ</button>
     ...
   </div>

   <div class="sp-grid" data-filter-target="leagues">
     <div class="sp-card" data-filter-key="premier">...</div>
     ...
   </div>

   The target's cards are shown/hidden by toggling .is-hidden.
   ============================================================ */
(function () {
  function setupGroup(pillRow) {
    var group = pillRow.getAttribute("data-filter-group");
    if (!group) return;
    var target = document.querySelector('[data-filter-target="' + group + '"]');
    if (!target) return;
    var cards = target.querySelectorAll("[data-filter-key]");
    var pills = pillRow.querySelectorAll(".pill-btn");

    function apply(value) {
      cards.forEach(function (card) {
        var keys = (card.getAttribute("data-filter-key") || "").split(/\s+/);
        var show = value === "*" || keys.indexOf(value) !== -1;
        card.classList.toggle("is-hidden", !show);
      });
      pills.forEach(function (p) {
        p.classList.toggle("is-active", p.getAttribute("data-filter") === value);
      });
      if (window.gtag) {
        window.gtag("event", "league_filter_click", { filter_value: value });
      }
      if (window.dataLayer) {
        window.dataLayer.push({ event: "league_filter_click", filter_value: value });
      }
    }

    pills.forEach(function (p) {
      p.addEventListener("click", function () {
        apply(p.getAttribute("data-filter") || "*");
      });
    });
  }

  function init() {
    document.querySelectorAll(".pill-row[data-filter-group]").forEach(setupGroup);

    // "準備中" cards: prevent navigation + GA log
    document.querySelectorAll(".is-disabled").forEach(function (el) {
      el.addEventListener("click", function (e) {
        e.preventDefault();
      });
      if (!el.getAttribute("title")) {
        el.setAttribute("title", "順次公開予定");
      }
    });

    // Generic ac click GA pass-through
    document.querySelectorAll("[data-ga-ac]").forEach(function (el) {
      el.addEventListener("click", function () {
        var ac = el.getAttribute("data-ga-ac") || "";
        var pos = el.getAttribute("data-ga-pos") || "";
        var theme = document.body.getAttribute("data-theme") || "";
        if (window.gtag) {
          window.gtag("event", "theme_to_ac_click", {
            theme_name: theme,
            ac_id: ac,
            card_position: pos
          });
        }
        if (window.dataLayer) {
          window.dataLayer.push({
            event: "theme_to_ac_click",
            theme_name: theme,
            ac_id: ac,
            card_position: pos
          });
        }
      });
    });

    // Genre card clicks on Sports TOP
    document.querySelectorAll("[data-ga-genre]").forEach(function (el) {
      el.addEventListener("click", function () {
        var name = el.getAttribute("data-ga-genre") || "";
        var pos = el.getAttribute("data-ga-pos") || "";
        if (window.gtag) {
          window.gtag("event", "genre_card_click", {
            genre_name: name,
            card_position: pos
          });
        }
        if (window.dataLayer) {
          window.dataLayer.push({
            event: "genre_card_click",
            genre_name: name,
            card_position: pos
          });
        }
      });
    });

    // theme_page_view on load
    var theme = document.body.getAttribute("data-theme");
    var pageType = document.body.getAttribute("data-page-type");
    if (theme) {
      if (window.gtag) {
        window.gtag("event", "theme_page_view", {
          theme_name: theme,
          page_type: pageType || ""
        });
      }
      if (window.dataLayer) {
        window.dataLayer.push({
          event: "theme_page_view",
          theme_name: theme,
          page_type: pageType || ""
        });
      }
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
