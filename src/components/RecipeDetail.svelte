<script>
  import { onMount } from "svelte";
  import { activeRecipe, openIngredient } from "../stores/data.js";
  import MapView from "./MapView.svelte";

  $: recipe = $activeRecipe;

  onMount(() => {
    window.scrollTo({ top: 0, left: 0, behavior: "auto" });
  });
</script>

{#if recipe}
  <div class="recipe-detail">
    <!-- Left panel: recipe info -->
    <div class="panel info-panel">
      <div class="recipe-header">
        <h2>{recipe.id}</h2>
        <div class="meta-row">
          {#each recipe.diseases as d}
            <span class="tag">{d}</span>
          {/each}
          {#if recipe.type}
            <span class="tag type">{recipe.type}</span>
          {/if}
        </div>
        {#if recipe.country}
          <p class="country">↗ {recipe.country}</p>
        {/if}
      </div>

      {#if recipe.preparation}
        <div class="section">
          <h4>Preparation</h4>
          <p>{recipe.preparation}</p>
        </div>
      {/if}

      {#if recipe.use}
        <div class="section">
          <h4>Use</h4>
          <p>{recipe.use}</p>
        </div>
      {/if}

      {#if recipe.contraindications}
        <div class="section warn">
          <h4>Contraindications</h4>
          <p>{recipe.contraindications}</p>
        </div>
      {/if}

      {#if recipe.medical_recommendations}
        <div class="section">
          <h4>Medical recommendations</h4>
          <p>{recipe.medical_recommendations}</p>
        </div>
      {/if}

      {#if recipe.source}
        <div class="section source">
          <h4>Source</h4>
          <p>{recipe.source}</p>
        </div>
      {/if}

      <!-- Ingredient cards -->
      <div class="section">
        <h4>Ingredients</h4>
        <div class="ingredient-list">
          {#each recipe.ingredients as ing}
            <button
              class="ing-card"
              on:click={() => openIngredient(ing.scientific_name)}
            >
              <div class="ing-top">
                <span class="ing-vernacular">{ing.vernacular_name || "—"}</span>
                {#if ing.quantity}
                  <span class="ing-qty">{ing.quantity}</span>
                {/if}
              </div>
              <em class="ing-scientific">{ing.scientific_name}</em>
              {#if ing.parts}
                <span class="ing-parts">parts used: {ing.parts}</span>
              {/if}
              <span class="ing-link">view species →</span>
            </button>
          {/each}
        </div>
      </div>
    </div>

    <!-- Right panel: map -->
    <div class="panel map-panel">
      <div class="map-label">
        <span class="dot recipe"></span>
        coexistence = where all species of this recipe occur together
      </div>
      <MapView
        mode="recipe"
        gbifIds={recipe.ingredients.map((i) => i.gbif_id).filter(Boolean)}
        ingredientNames={recipe.ingredients.map((i) => i.scientific_name)}
      />
      <div class="map-legend">
        <!-- <span><span class="swatch overlap"></span> species overlap</span> -->
        <span><span class="swatch single"></span> single species</span>
      </div>
    </div>
  </div>
{/if}

<style>
  .recipe-detail {
    display: grid;
    grid-template-columns: 380px 1fr;
    gap: 0;
    min-height: calc(100vh - 200px);
    border: 1px solid var(--rose);
    margin-top: 1.5rem;
  }

  @media (max-width: 900px) {
    .recipe-detail {
      grid-template-columns: 1fr;
    }
  }

  .panel {
    overflow-y: auto;
  }

  .info-panel {
    border-right: 0px solid var(--rose);
    padding: 1.5rem;
    display: flex;
    flex-direction: column;
    gap: 1.25rem;
    max-height: calc(100vh - 120px);
  }

  .map-panel {
    display: flex;
    flex-direction: column;
    background: var(--rose-pale);
  }

  .map-label {
    font-family: var(--mono);
    font-size: 0.68rem;
    color: var(--ink-muted);
    padding: 0.6rem 0.8rem;
    border-bottom: 1px solid var(--paper-dark);
    display: flex;
    align-items: center;
    gap: 0.5rem;
    letter-spacing: 0.03em;
  }

  .dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    display: inline-block;
    flex-shrink: 0;
  }
  .dot.recipe {
    background: var(--rose);
  }

  /* ── Recipe header ─── */
  .recipe-header {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  h2 {
    font-size: 1.8rem;
    color: var(--ink);
  }

  .meta-row {
    display: flex;
    flex-wrap: wrap;
    gap: 0.3rem;
  }

  .tag {
    font-family: var(--mono);
    font-size: 0.65rem;
    padding: 0.15rem 0.45rem;
    background: var(--rose);
    color: var(--paper);
  }
  .tag.type {
    border: 1px solid var(--rose);
    background: none;
    color: var(--rose);
  }

  .country {
    font-family: var(--mono);
    font-size: 0.7rem;
    color: var(--ink-muted);
  }

  /* ── Sections ─── */
  .section {
    display: flex;
    flex-direction: column;
    gap: 0.35rem;
  }

  h4 {
    font-family: var(--mono);
    font-size: 0.65rem;
    color: var(--rose);
    letter-spacing: 0.1em;
    text-transform: uppercase;
    font-weight: 400;
  }

  p {
    font-family: var(--mono);
    font-size: 0.8rem;
    color: var(--ink-muted);
    line-height: 1.6;
  }

  .warn p {
    color: var(--rose);
  }

  .source p {
    font-style: italic;
    font-family: var(--serif);
    font-size: 0.78rem;
  }

  /* ── Ingredient list ─── */
  .ingredient-list {
    display: flex;
    flex-direction: column;
    gap: 1px;
    background: var(--paper-dark);
    border: 1px solid var(--rose);
  }

  .ing-card {
    background: var(--paper);
    padding: 0.85rem 1rem;
    text-align: left;
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
    cursor: pointer;
    transition: background 0.1s;
  }
  .ing-card:hover {
    background: var(--rose-pale);
  }

  .ing-top {
    display: flex;
    justify-content: space-between;
    align-items: baseline;
  }

  .ing-vernacular {
    font-family: var(--serif);
    font-size: 0.95rem;
    color: var(--ink);
  }

  .ing-qty {
    font-family: var(--mono);
    font-size: 0.68rem;
    color: var(--ink-faint);
  }

  .ing-scientific {
    font-family: var(--serif);
    font-size: 0.78rem;
    color: var(--ink-muted);
  }

  .ing-parts {
    font-family: var(--mono);
    font-size: 0.65rem;
    color: var(--ink);
  }

  .ing-link {
    font-family: var(--mono);
    font-size: 0.63rem;
    color: var(--rose);
    margin-top: 0.15rem;
  }

  /* ── Map legend ─── */
  .map-legend {
    padding: 0.5rem 0.8rem;
    font-family: var(--mono);
    font-size: 0.65rem;
    color: var(--ink-muted);
    display: flex;
    gap: 1.5rem;
    border-top: 1px solid var(--paper-dark);
  }

  .swatch {
    display: inline-block;
    width: 10px;
    height: 10px;
    border-radius: 1px;
    margin-right: 0.3rem;
    vertical-align: middle;
  }
  .swatch.overlap {
    background: var(--rose);
    opacity: 0.7;
  }
  .swatch.single {
    background: #8099b0;
    opacity: 0.5;
  }
</style>
