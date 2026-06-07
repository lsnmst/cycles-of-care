import { writable, derived, get } from 'svelte/store'
import Papa from 'papaparse'

// ─── Raw stores ───────────────────────────────────────────
export const ingredientsRaw = writable([])
export const recipesRaw = writable([])
export const loading = writable(true)
export const loadError = writable(null)

// ─── UI state ─────────────────────────────────────────────
export const activeView = writable('archive')   // 'archive' | 'recipe' | 'ingredient'
export const activeRecipeId = writable(null)
export const activeIngredientName = writable(null)     // scientific_name
export const filters = writable({ disease: '', type: '', country: '', ingredient: "" })

// ─── Helpers ──────────────────────────────────────────────
function parseCSV(url) {
  return new Promise((resolve, reject) => {
    Papa.parse(url, {
      download: true,
      header: true,
      skipEmptyLines: true,
      transformHeader: h => h.trim(),
      transform: v => v.trim(),
      complete: r => resolve(r.data),
      error: reject,
    })
  })
}

// ─── InfoPanel ────────────────────────────────────────────
export const showInfoPanel = writable(true);

// ─── Loader ───────────────────────────────────────────────
export async function loadData(base = '') {
  try {
    loading.set(true)
    const [ing, rec] = await Promise.all([
      parseCSV(`${base}/data/ingredients.csv`),
      parseCSV(`${base}/data/recipes.csv`),
    ])
    ingredientsRaw.set(ing)
    recipesRaw.set(rec)
  } catch (e) {
    loadError.set(e.message ?? 'Failed to load data')
  } finally {
    loading.set(false)
  }
}

// ─── Derived: ingredients indexed by scientific_name ──────
export const ingredientsByName = derived(ingredientsRaw, $ing => {
  const map = {}
  for (const row of $ing) {
    if (row.scientific_name) map[row.scientific_name] = row
  }
  return map
})

// ─── Derived: recipes grouped by name (id) ────────────────
// Each recipe = { id, disease[], type, country, source, preparation, use,
//                 contraindications, medical_recommendations,
//                 ingredients: [{ ...recipeRow, ...ingredientDetail }] }
export const recipes = derived(
  [recipesRaw, ingredientsByName],
  ([$rows, $byName]) => {
    const map = {}
    for (const row of $rows) {
      const id = row.name
      if (!id) continue
      if (!map[id]) {
        map[id] = {
          id,
          diseases: [],
          type: row.type ?? '',
          country: row.country ?? '',
          source: row.source ?? '',
          preparation: row.preparation ?? '',
          use: row.use ?? '',
          contraindications: row.contraindications ?? '',
          medical_recommendations: row.medical_recommendations ?? '',
          ingredients: [],
        }
      }
      const recipe = map[id]

      // collect unique diseases
      const diseases = (row.disease ?? '').split(';').map(d => d.trim()).filter(Boolean)
      for (const d of diseases) {
        if (!recipe.diseases.includes(d)) recipe.diseases.push(d)
      }

      // attach ingredient detail
      const detail = $byName[row.scientific_name] ?? {}
      recipe.ingredients.push({
        scientific_name: row.scientific_name ?? '',
        vernacular_name: row.vernacular_name ?? detail.vernacular_name ?? '',
        parts: row.parts ?? detail.used_parts ?? '',
        quantity: row.quantity ?? '',
        harvest: detail.harvest ?? '',
        preservation: detail.preservation ?? '',
        gbif_url: detail.GBIF ?? '',
        gbif_id: detail.GBIF_id ?? '',
      })
    }
    return Object.values(map)
  }
)

// ─── Derived: all unique filter options ───────────────────
export const filterOptions = derived(recipes, ($recipes) => {
  const diseases = new Set();
  const types = new Set();
  const countries = new Set();
  const ingredients = new Set();

  for (const r of $recipes) {
    r.diseases.forEach((d) => diseases.add(d));

    if (r.type) types.add(r.type);
    if (r.country) countries.add(r.country);

    for (const ing of r.ingredients) {
      if (ing.scientific_name) {
        ingredients.add(ing.scientific_name);
      }
    }
  }

  return {
    diseases: [...diseases].sort(),
    types: [...types].sort(),
    countries: [...countries].sort(),
    ingredients: [...ingredients].sort(), // NEW
  };
});


// ─── Derived: filtered recipes ────────────────────────────
export const filteredRecipes = derived([recipes, filters], ([$recipes, $f]) => {
  return $recipes.filter(r => {
    if ($f.disease && !r.diseases.some(d => d.toLowerCase().includes($f.disease.toLowerCase()))) return false
    if ($f.type && r.type.toLowerCase() !== $f.type.toLowerCase()) return false
    if ($f.country && r.country.toLowerCase() !== $f.country.toLowerCase()) return false
    if ($f.ingredient) {
      const query = $f.ingredient.toLowerCase();

      const match = r.ingredients.some((ing) => {
        return (
          ing.scientific_name?.toLowerCase().includes(query) ||
          ing.vernacular_name?.toLowerCase().includes(query)
        );
      });

      if (!match) return false;
    }
    return true
  })
})

// ─── Derived: active recipe object ────────────────────────
export const activeRecipe = derived([recipes, activeRecipeId], ([$r, $id]) => {
  return $r.find(r => r.id === $id) ?? null
})

// ─── Derived: active ingredient detail (from ingredientsRaw) ─
export const activeIngredient = derived(
  [ingredientsByName, activeIngredientName],
  ([$map, $name]) => $map[$name] ?? null
)

// ─── Navigation helpers ────────────────────────────────────
export function openRecipe(id) {
  activeRecipeId.set(id)
  activeView.set('recipe')
}

export function openIngredient(scientificName) {
  activeIngredientName.set(scientificName)
  activeView.set('ingredient')
}

export function goBack() {
  const view = get(activeView)
  if (view === 'ingredient') {
    // go back to the recipe if one is open, else archive
    const rid = get(activeRecipeId)
    activeView.set(rid ? 'recipe' : 'archive')
  } else {
    activeView.set('archive')
  }
}
