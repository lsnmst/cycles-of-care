<script>
  import { onMount, onDestroy } from "svelte";
  import * as h3 from "h3-js";

  export let mode = "ingredient";
  // 'ingredient' | 'recipe'

  export let gbifIds = [];
  // in realtà ora sono taxon IDs → usati per fetch H3 JSON

  export let ingredientNames = [];

  let mapEl;
  let map;
  let layers = [];

  const EUROPE_BOUNDS = [
    [34, -25], // SW (lat, lng)
    [72, 45], // NE
  ];

  const SINGLE_COLOR = "#8099b0";
  const OVERLAP_COLOR = "#a84a4a";

  // ─────────────────────────────────────────────
  async function loadH3(taxonId) {
    const res = await fetch(
      `${import.meta.env.BASE_URL}data/h3/${taxonId}.json`,
    );

    if (!res.ok) {
      console.warn("Missing H3 file for", taxonId);
      return null;
    }

    return await res.json();
  }

  // ─────────────────────────────────────────────
  function zoomToCells(L, cells) {
    if (!cells.length) return;

    const bounds = [];

    for (const cell of cells) {
      const boundary = h3.cellToBoundary(cell, false);

      for (const [lat, lng] of boundary) {
        bounds.push([lat, lng]);
      }
    }

    if (bounds.length) {
      map.fitBounds(bounds, {
        padding: [20, 20],
        maxZoom: 8,
        animate: false,
      });
    }
  }

  // ─────────────────────────────────────────────
  function renderH3Cells(L, cells, color, opacity = 0.35) {
    for (const cell of cells) {
      try {
        const boundary = h3.cellToBoundary(cell, false);
        // false = [lat, lng] ← CORRETTO per Leaflet

        const latlngs = boundary.map(([lat, lng]) => [lat, lng]);

        const poly = L.polygon(latlngs, {
          color,
          weight: 0.8,
          opacity: 0.1,
          fillColor: color,
          fillOpacity: opacity,
        });

        poly.addTo(map);
        layers.push(poly);
      } catch (e) {
        console.warn("H3 render error:", e);
      }
    }
  }

  // ─────────────────────────────────────────────
  function intersectCellSets(sets) {
    if (!sets.length) return [];

    return [
      ...sets.reduce((acc, set) => {
        return new Set([...acc].filter((x) => set.has(x)));
      }),
    ];
  }

  // ─────────────────────────────────────────────
  function clearLayers(L) {
    for (const l of layers) {
      map.removeLayer(l);
    }
    layers = [];
  }

  // ─────────────────────────────────────────────
  async function render() {
    const L = await import("leaflet");
    clearLayers(L);

    // ─────────────────────────────
    // INGREDIENT MODE
    // ─────────────────────────────
    if (mode === "ingredient") {
      const data = await loadH3(gbifIds[0]);
      if (!data) return;

      renderH3Cells(L, data.cells, SINGLE_COLOR, 0.4);
      zoomToCells(L, data.cells);
    }

    // ─────────────────────────────
    // RECIPE MODE (INTERSECTION)
    // ─────────────────────────────
    if (mode === "recipe") {
      const datasets = [];

      for (const id of gbifIds) {
        const data = await loadH3(id);
        if (!data) continue;
        datasets.push(data.cells);
      }

      if (!datasets.length) return;

      // convert to sets
      const sets = datasets.map((cells) => new Set(cells));

      // intersection (A ∩ B ∩ C)
      const intersect = intersectCellSets(sets);

      // OPTIONAL: also show individual species faintly
      for (const cells of datasets) {
        renderH3Cells(L, cells, SINGLE_COLOR, 0.15);
      }

      // highlight intersection
      renderH3Cells(L, intersect, OVERLAP_COLOR, 0.55);
      if (intersect.length) {
        zoomToCells(L, intersect);
      } else {
        const allCells = datasets.flat();
        zoomToCells(L, allCells);
      }
    }
  }

  // ─────────────────────────────────────────────
  onMount(async () => {
    const L = await import("leaflet");

    map = L.map(mapEl, {
      center: [50, 10],
      zoom: 4,
      zoomControl: true,
      scrollWheelZoom: true,
      maxBounds: EUROPE_BOUNDS,
      maxBoundsViscosity: 1.0,
    });

    // base map (NO GBIF tiles anymore)
    L.tileLayer(
      "https://{s}.basemaps.cartocdn.com/light_nolabels/{z}/{x}/{y}{r}.png",
      {
        attribution: "© OpenStreetMap © CARTO",
        subdomains: "abcd",
        maxZoom: 12,
      },
    ).addTo(map);

    await render();
  });

  onDestroy(() => {
    map?.remove();
  });

  // ─────────────────────────────────────────────
  $: if (map) {
    render();
  }
</script>

<div class="map-container" bind:this={mapEl}></div>

<style>
  .map-container {
    flex: 1;
    min-height: 400px;
    width: 100%;
  }

  :global(.leaflet-control-attribution) {
    display: none;
  }
</style>
