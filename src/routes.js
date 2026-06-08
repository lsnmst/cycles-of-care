import Archive from "./pages/Archive.svelte";
import Recipe from "./pages/Recipe.svelte";
import Ingredient from "./pages/Ingredient.svelte";

export default {
    "/": Archive,
    "/recipe/:id": Recipe,
    "/ingredient/:id": Ingredient,
};