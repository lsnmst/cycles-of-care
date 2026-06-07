<script>
  import {
    filteredRecipes,
    filterOptions,
    filters,
    openRecipe,
  } from "../stores/data.js";
  import InfoPanel from "./InfoPanel.svelte";

  const typeSymbols = {
    bath: "☽",
    boil: "▲",
    decoction: "△",
    infusion: "◎",
    "not specified": "·",
    salad: "✧",
    soup: "◒",
    "topical administration": "□",
    washing: "◌",
  };
  function symbol(type) {
    return typeSymbols[type?.toLowerCase()] ?? "·";
  }

  function resetFilters() {
    filters.set({ disease: "", type: "", ingredient: "", country: "" });
  }

  $: hasFilters =
    $filters.disease ||
    $filters.type ||
    $filters.ingredient ||
    $filters.country;
</script>

<section class="archive">
  <!-- Filter bar -->
  <div class="filter-bar">
    <span class="filter-label">filter by</span>

    <select bind:value={$filters.disease}>
      <option value="">all conditions</option>
      {#each $filterOptions.diseases as d}
        <option value={d}>{d}</option>
      {/each}
    </select>

    <select bind:value={$filters.type}>
      <option value="">all types</option>
      {#each $filterOptions.types as t}
        <option value={t}>{symbol(t)} {t}</option>
      {/each}
    </select>

    <select bind:value={$filters.ingredient}>
      <option value="">all ingredients</option>
      {#each $filterOptions.ingredients as i}
        <option value={i}>{i}</option>
      {/each}
    </select>

    <select bind:value={$filters.country}>
      <option value="">all countries</option>
      {#each $filterOptions.countries as c}
        <option value={c}>{c}</option>
      {/each}
    </select>

    {#if hasFilters}
      <button class="reset" on:click={resetFilters}>× clear</button>
    {/if}

    <span class="count">{$filteredRecipes.length} recipes</span>
  </div>

  <!-- Legend -->
  <div class="legend">
    {#each Object.entries(typeSymbols) as [type, sym]}
      <span><span class="sym">{sym}</span> {type}</span>
    {/each}
  </div>

  <!-- Grid -->
  {#if $filteredRecipes.length === 0}
    <p class="empty">no recipes match the current filters.</p>
  {:else}
    <div class="grid">
      {#each $filteredRecipes as recipe (recipe.id)}
        <button class="card" on:click={() => openRecipe(recipe.id)}>
          <div class="card-top">
            <span class="card-symbol">{symbol(recipe.type)}</span>
            <!-- <span class="card-id">{recipe.id}</span> -->
          </div>
          <div class="card-diseases">
            {#each recipe.diseases as d}
              <span class="tag">{d}</span>
            {/each}
          </div>
          <!--             
            {#each recipe.ingredients.slice(0, 4) as ing}
              <li>{ing.vernacular_name || ing.scientific_name}</li>
            {/each}
            {#if recipe.ingredients.length > 4}
              <li class="more">+{recipe.ingredients.length - 4} more</li>
            {/if} -->
          <h1 class="card-id">{recipe.id}</h1>

          <div class="card-ingredients">
            <div class="hover">
              {#each recipe.ingredients.slice(0, 4) as ing}
                <div class="ing">
                  {ing.vernacular_name || ing.scientific_name}
                </div>
              {/each}

              {#if recipe.ingredients.length > 4}
                <div class="more">
                  +{recipe.ingredients.length - 4} more
                </div>
              {/if}
            </div>
          </div>

          <div class="card-footer">
            <span class="card-country">{recipe.country}</span>
            <span class="card-type">{recipe.type}</span>
          </div>
        </button>
      {/each}
    </div>
  {/if}

  <InfoPanel />
</section>

<style>
  .archive {
    padding-top: 1.5rem;
  }

  /* ── Filter bar ─────────────────────────────────────────── */
  .filter-bar {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    flex-wrap: wrap;
    margin-bottom: 0.75rem;
    padding-bottom: 0.75rem;
    border-bottom: 1px solid var(--paper-dark);
  }

  .filter-label {
    font-family: var(--mono);
    font-size: 0.7rem;
    color: var(--ink-faint);
    letter-spacing: 0.08em;
    text-transform: uppercase;
  }

  select {
    font-family: var(--mono);
    font-size: 0.75rem;
    color: var(--ink);
    background: var(--rose-pale);
    border: 1px solid var(--rose);
    padding: 0.3rem 0.6rem;
    border-radius: var(--radius);
    appearance: none;
    cursor: pointer;
  }
  select:focus {
    outline: 1px solid var(--rose);
  }

  .reset {
    font-size: 0.7rem;
    color: var(--rose);
    border: 1px solid var(--rose-pale);
    padding: 0.25rem 0.5rem;
  }
  .reset:hover {
    background: var(--rose-pale);
  }

  .count {
    font-family: var(--mono);
    font-size: 0.7rem;
    color: var(--ink);
    margin-left: auto;
  }

  .card-ingredients .hover {
    display: none;
  }

  .card:hover .hover {
    display: block;
  }

  .card:hover .default {
    display: none;
  }

  .ing {
    color: var(--paper);
  }

  /* ── Legend ─────────────────────────────────────────────── */
  .legend {
    display: flex;
    gap: 1.5rem;
    flex-wrap: wrap;
    font-family: var(--mono);
    font-size: 0.68rem;
    color: var(--ink-muted);
    margin-bottom: 1.5rem;
    letter-spacing: 0.03em;
  }
  .sym {
    color: var(--rose);
    margin-right: 0.2rem;
  }

  /* ── Grid ───────────────────────────────────────────────── */
  .grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
    gap: 1px;
    background: var(--rose);
    border: 1px solid var(--rose-pale);
  }

  .card {
    background: var(--paper);
    padding: 1.25rem;
    text-align: left;
    display: flex;
    flex-direction: column;
    gap: 0.6rem;
    transition: background 0.12s;
    cursor: pointer;
  }
  .card:hover {
    background: var(--rose);
  }

  .card-top {
    display: flex;
    justify-content: space-between;
    align-items: baseline;
  }

  .card-symbol {
    font-size: 1.2rem;
    color: var(--rose);
    line-height: 1;
  }

  .card-id {
    font-family: var(--mono);
    font-size: clamp(1.4rem, 3vw, 2.5rem);
    letter-spacing: -0.01em;
    color: var(--ink);
    letter-spacing: 0.06em;
  }

  .card-diseases {
    display: flex;
    flex-wrap: wrap;
    gap: 0.3rem;
  }

  .tag {
    font-family: var(--mono);
    font-size: 0.62rem;
    background: var(--rose);
    color: var(--paper);
    padding: 0.1rem 0.4rem;
    letter-spacing: 0.03em;
  }

  .card-ingredients {
    list-style: none;
    font-family: var(--serif);
    font-size: 0.85rem;
    font-style: italic;
    color: var(--ink-muted);
    line-height: 1.4;
  }

  .card-ingredients .more {
    font-family: var(--mono);
    font-style: normal;
    font-size: 0.65rem;
    color: var(--ink-faint);
  }

  .card-footer {
    display: flex;
    justify-content: space-between;
    font-family: var(--mono);
    font-size: 0.65rem;
    color: var(--ink-faint);
    margin-top: auto;
    padding-top: 0.5rem;
    border-top: 1px solid var(--paper-dark);
    letter-spacing: 0.04em;
  }

  .empty {
    font-family: var(--mono);
    font-size: 0.8rem;
    color: var(--ink);
    padding: 3rem 0;
    text-align: center;
  }

  @media (max-width: 600px) {
    .legend {
      display: none;
    }

    .filter-bar {
      flex-direction: column;
      gap: 0.25rem;
    }

    .filter-label {
      font-size: 0.65rem;
    }

    .filter-label select {
      font-size: 0.65rem;
      text-align: center;
      text-align: -webkit-center;
    }
  }
</style>
