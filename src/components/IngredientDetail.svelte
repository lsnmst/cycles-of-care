<script>
  import { activeIngredient, activeIngredientName } from '../stores/data.js'
  import MapView from './MapView.svelte'

  $: ing = $activeIngredient
  $: name = $activeIngredientName

  // botanical image: first try local pre-fetched, fall back to GBIF thumbnail
  $: localImg = ing?.GBIF_id
    ? `${import.meta.env.BASE_URL}img/botanica/${ing.GBIF_id}.jpg`
    : null

  $: gbifPageUrl = ing?.GBIF ? ing.GBIF : null

  let imgError = false
  $: if (ing) imgError = false   // reset on new ingredient
</script>

{#if ing}
<div class="ingredient-detail">
  <!-- Left: botanical card -->
  <div class="panel card-panel">
    <div class="botanical-img-wrap">
      {#if localImg && !imgError}
        <img
          src={localImg}
          alt="botanical illustration of {ing.scientific_name}"
          on:error={() => imgError = true}
        />
      {:else}
        <div class="img-placeholder">
          <span>○</span>
          <p>illustration not yet available</p>
          {#if gbifPageUrl}
            <a href={gbifPageUrl} target="_blank" rel="noopener">view on GBIF ↗</a>
          {/if}
        </div>
      {/if}
    </div>

    <div class="card-info">
      <h2>{ing.vernacular_name || name}</h2>
      <em class="scientific">{ing.scientific_name || name}</em>

      {#if ing.used_parts}
        <div class="field">
          <span class="field-label">parts used</span>
          <span>{ing.used_parts}</span>
        </div>
      {/if}

      {#if ing.harvest}
        <div class="field">
          <span class="field-label">harvest</span>
          <p>{ing.harvest}</p>
        </div>
      {/if}

      {#if ing.preservation}
        <div class="field">
          <span class="field-label">preservation</span>
          <p>{ing.preservation}</p>
        </div>
      {/if}

      {#if ing.desease}
        <div class="field">
          <span class="field-label">used for</span>
          <div class="tags">
            {#each (ing.desease || '').split(';').map(d => d.trim()).filter(Boolean) as d}
              <span class="tag">{d}</span>
            {/each}
          </div>
        </div>
      {/if}

      {#if gbifPageUrl}
        <a class="gbif-link" href={gbifPageUrl} target="_blank" rel="noopener">
          GBIF species page ↗
        </a>
      {/if}
    </div>
  </div>

  <!-- Right: map -->
  <div class="panel map-panel">
    <div class="map-label">
      <span class="dot"></span>
      distribution of <em>{ing.scientific_name || name}</em>
    </div>
    <MapView
      mode="ingredient"
      gbifIds={ing.GBIF_id ? [ing.GBIF_id] : []}
      ingredientNames={[ing.scientific_name || name]}
    />
    <div class="map-legend">
      <span><span class="swatch single"></span> species distribution</span>
    </div>
  </div>
</div>
{:else}
<p class="missing">ingredient data not found for <em>{name}</em></p>
{/if}

<style>
  .ingredient-detail {
    display: grid;
    grid-template-columns: 360px 1fr;
    gap: 0;
    min-height: calc(100vh - 200px);
    border: 1px solid var(--rose);
    margin-top: 1.5rem;
  }

  @media (max-width: 900px) {
    .ingredient-detail { grid-template-columns: 1fr; }
  }

  .panel { overflow-y: auto; }

  .card-panel {
    border-right: 0px solid var(--paper-dark);
    display: flex;
    flex-direction: column;
    max-height: calc(100vh - 120px);
  }

  .map-panel {
    display: flex;
    flex-direction: column;
    background: var(--rose-pale);
  }

  /* ── Botanical image ─── */
  .botanical-img-wrap {
    width: 100%;
    aspect-ratio: 3/4;
    max-height: 320px;
    overflow: hidden;
    background: var(--rose);
    border-bottom: 1px solid var(--paper-dark);
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .botanical-img-wrap img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    filter: sepia(0.15) contrast(1.05);
  }

  .img-placeholder {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.5rem;
    color: var(--ink-faint);
    font-family: var(--mono);
    font-size: 0.75rem;
  }
  .img-placeholder span { font-size: 2rem; }
  .img-placeholder a {
    font-size: 0.68rem;
    color: var(--rose-pale);
    text-decoration: underline;
  }

  /* ── Card info ─── */
  .card-info {
    padding: 1.25rem;
    display: flex;
    flex-direction: column;
    gap: 1rem;
    overflow-y: auto;
  }

  h2 { font-size: 1.5rem; }

  .scientific {
    font-family: var(--serif);
    font-size: 0.9rem;
    color: var(--ink-muted);
    display: block;
    margin-top: -0.5rem;
  }

  .field { display: flex; flex-direction: column; gap: 0.2rem; }

  .field-label {
    font-family: var(--mono);
    font-size: 0.62rem;
    color: var(--rose);
    letter-spacing: 0.1em;
    text-transform: uppercase;
  }

  .field span:not(.field-label), .field p {
    font-family: var(--mono);
    font-size: 0.78rem;
    color: var(--ink-muted);
    line-height: 1.55;
  }

  .tags { display: flex; flex-wrap: wrap; gap: 0.3rem; }

  .tag {
    font-family: var(--mono);
    font-size: 0.62rem;
    padding: 0.1rem 0.4rem;
    background: var(--rose);
    color: var(--paper-warm) !important;
  }

  .gbif-link {
    font-family: var(--mono);
    font-size: 0.68rem;
    color: var(--moss);
    text-decoration: underline;
    margin-top: 0.5rem;
  }

  /* ── Map panel ─── */
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
    width: 8px; height: 8px;
    border-radius: 50%;
    background: #8099b0;
    display: inline-block;
    flex-shrink: 0;
  }

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
    width: 10px; height: 10px;
    border-radius: 1px;
    margin-right: 0.3rem;
    vertical-align: middle;
  }
  .swatch.single { background: #8099b0; opacity: 0.5; }

  .missing {
    font-family: var(--mono);
    font-size: 0.8rem;
    color: var(--ink-faint);
    padding: 3rem 0;
    text-align: center;
  }
</style>
