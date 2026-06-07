<script>
  import { onMount } from 'svelte'
  import { loadData, activeView, loading, loadError } from './stores/data.js'
  import Archive     from './components/Archive.svelte'
  import RecipeDetail    from './components/RecipeDetail.svelte'
  import IngredientDetail from './components/IngredientDetail.svelte'
  import Header      from './components/Header.svelte'

  onMount(() => {
    // In dev: /data/... lives in /public/data/
    // In prod (gh-pages): base is /cycles-of-care/
    loadData(import.meta.env.BASE_URL.replace(/\/$/, ''))
  })
</script>

<div class="app-shell">
  <Header />

  <main>
    {#if $loading}
      <div class="status">
        <span class="blink">○</span> loading archive…
      </div>
    {:else if $loadError}
      <div class="status error">error: {$loadError}</div>
    {:else if $activeView === 'archive'}
      <Archive />
    {:else if $activeView === 'recipe'}
      <RecipeDetail />
    {:else if $activeView === 'ingredient'}
      <IngredientDetail />
    {/if}
  </main>
</div>

<style>
  .app-shell {
    display: flex;
    flex-direction: column;
    min-height: 100vh;
  }

  main {
    flex: 1;
    padding: 0 var(--gap) var(--gap);
    max-width: 1400px;
    margin: 0 auto;
    width: 100%;
  }

  .status {
    font-family: var(--mono);
    font-size: 0.8rem;
    color: var(--ink-muted);
    padding: 4rem 0;
    text-align: center;
    letter-spacing: 0.05em;
  }

  .status.error { color: var(--rose); }

  .blink {
    display: inline-block;
    animation: blink 1.2s step-end infinite;
  }
  @keyframes blink { 0%,100%{opacity:1} 50%{opacity:0} }
</style>
