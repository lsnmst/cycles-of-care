<script>
  import {
    activeView,
    activeRecipeId,
    activeIngredientName,
    goBack,
  } from "../stores/data.js";

  $: showBack = $activeView !== "archive";
</script>

<header>
  <div class="title-block">
    <h1>Cycles of Care</h1>
    <p class="subtitle">a menstrual rematriation archive</p>
  </div>

  {#if showBack}
    <button class="back" on:click={goBack}> ← back </button>
  {/if}

  {#if $activeView !== "archive"}
    <nav class="breadcrumb">
      <span
        on:click={() => activeView.set("archive")}
        role="button"
        tabindex="0"
        on:keydown={(e) => e.key === "Enter" && activeView.set("archive")}
      >
        archive
      </span>

      {#if $activeView === "recipe" || $activeView === "ingredient"}
        <span class="sep">/</span>
        <span
          class:active={$activeView === "recipe"}
          on:click={() => {
            if ($activeRecipeId) activeView.set("recipe");
          }}
          role="button"
          tabindex="0"
          on:keydown={(e) => e.key === "Enter" && activeView.set("recipe")}
        >
          {$activeRecipeId}
        </span>
      {/if}

      {#if $activeView === "ingredient"}
        <span class="sep">/</span>
        <span class="active">
          <em>{$activeIngredientName}</em>
        </span>
      {/if}
    </nav>
  {/if}
</header>

<style>
  header {
    display: flex;
    align-items: baseline;
    gap: 2rem;
    padding: 1.5rem var(--gap) 1rem;
    border-bottom: 3px double var(--rose-pale);
    flex-wrap: wrap;
    max-width: 1400px;
    margin: 0 auto;
    width: 100%;
  }

  .title-block {
    flex: 1;
    min-width: 200px;
  }

  h1 {
    font-family: var(--mono);
    font-size: clamp(1.6rem, 4vw, 2.8rem);
    letter-spacing: -0.01em;
    color: var(--ink);
  }

  .title-block h1 {
    font-style: italic;
    letter-spacing: 0em;
    color: var(--rose);
  }

  .subtitle {
    font-family: var(--mono);
    font-size: 0.7rem;
    color: var(--ink);
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin-top: 0.15rem;
  }

  .back {
    font-size: 0.75rem;
    color: var(--rose);
    letter-spacing: 0.05em;
    padding: 0.25rem 0.5rem;
    border: 1px solid var(--rose-pale);
    transition: background 0.15s;
  }
  .back:hover {
    background: var(--rose-pale);
  }

  .breadcrumb {
    font-family: var(--mono);
    font-size: 0.7rem;
    color: var(--ink-faint);
    display: flex;
    align-items: center;
    gap: 0.4rem;
    flex-wrap: wrap;
  }

  .breadcrumb span {
    cursor: pointer;
  }
  .breadcrumb span:hover {
    color: var(--ink-muted);
  }
  .breadcrumb span.active {
    color: var(--ink);
    cursor: default;
  }
  .breadcrumb .sep {
    cursor: default;
  }
</style>
