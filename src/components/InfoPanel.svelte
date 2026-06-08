<script>
    import { showInfoPanel } from "../stores/data.js";
</script>

{#if $showInfoPanel}
    <aside class="panel">
        <button class="close" on:click={() => showInfoPanel.set(false)}>
            ×
        </button>

        <div class="content">
            <p>
                <i>Cycles of Care</i> is an archive of traditional herbal
                recipes used to treat menstrual conditions collected from
                ethnobotanical sources across Italy and beyond.<br /><br />
                <i>Cycles of Care</i> is a map of a knowledge that was
                systematically destroyed. For centuries, women held an intimate
                understanding of plants, cycles, and bodies. They knew which
                roots to boil, which flowers to dry in shade, which leaves to
                hold against the skin. This knowledge moved through hands and
                voices, from mother to daughter, from healer to neighbour. It
                was local, embodied, and deeply tied to specific landscapes. The
                criminalization of female healing was inseparable from the
                enclosure of land and the dispossession of communal resources.
                To lose the plants was to lose the territory. To lose the
                territory was to lose the body.<br /> <br />
                This archive makes that spatial dimension visible. For each recipe,
                you can see where all its species coexists, where the ecology that
                made the knowledge possible still exists, or once existed. For each
                ingredient, you can trace its distribution. <br />
                <br />What you find here is not medical advice. It is an
                invitation to reconnect body to plant, plant to territory,
                territory to the communities that still carry this knowledge
                forward.<br /><br />

                To contribute or get in touch, 
                <a style="color: var(--paper);" href="https://www.instagram.com/alessandromusetta/" target="_blank" rel="noopener">DM ⸙͎۪۫</a>
            </p>
            <div class="method">
                <br />DATA<br />
                Species distribution data were obtained from the Global Biodiversity
                Information Facility (GBIF) Occurrence Records. Only records containing
                valid geographic coordinates (latitude/longitude) and no reported
                geospatial issues were included. Records lacking coordinates or containing
                obvious spatial errors were excluded. All species names were harmonized
                using GBIF taxonomic identifiers (taxon keys) to ensure consistency
                across datasets.
                <br /><br /><br />SPATIAL PROCESSING<br />
                Instead of using raw point distributions or fixed-degree latitude/longitude
                grids, species occurrences were transformed into a discrete hierarchical
                spatial index using the H3 geospatial indexing system. Each occurrence
                point was mapped to an H3 cell at resolution 6 (approx. ~10–15 km
                scale depending on latitude). To account for ecological uncertainty
                and sampling sparsity, a k-ring expansion (buffering) was optionally
                applied, extending each occupied cell to its neighboring cells. This
                produces a presence–absence representation of each species as a set
                of H3 cells: <br /><br /><i
                    >Presence = H3 cells containing at least one occurrence
                    record<br />Buffered presence = expanded neighborhood of
                    ecological influence</i
                >
                <br /><br />All spatial data are stored in WGS84 / EPSG:4326 for
                web compatibility.
                <br /><br /><br />CO-OCCURRENCE AND RECIPE-LEVEL ANALYSIS<br />
                For each herbal recipe, species are aggregated into a multi-species
                set. Spatial co-occurrence is computed as:<br /><br /><i
                    >Coexistence = intersection of H3 cells shared by ≥2 species</i
                ><br /><br />This allows identification of: shared ecological
                niches between medicinal plants; potential biocultural
                assemblages reflected in traditional recipes; spatial overlap of
                pharmacologically relevant species.<br />In recipe mode, both:
                individual species distributions (light overlay); intersection
                zones (coexistence hotspots), are visualized.
                <br /><br /><br />LIMITATIONS & BIASES<br />
                The GBIF occurrence data used in this project is inherently uneven
                in spatial and taxonomic coverage. Data quality depends on contributions
                from museums, herbaria, universities, and citizen-science initiatives.
                As a result:<br />
                some species are overrepresented in well-studied regions; others
                are underrepresented due to lack of sampling or digitization; occurrence
                points may reflect collection bias rather than true ecological distribution;
                absence of records does not imply true absence in nature.<br />
                Additional limitations arise from:<br />use of a fixed H3
                resolution, which simplifies continuous ecological gradients
                into discrete cells; buffering operations, which introduce
                modeled rather than observed presence; reliance on occurrence
                data rather than full species distribution models (SDMs).<br />
                <br /><br /><br />CRITICAL NOTE<br />
                This system does not attempt to reconstruct “true” botanical ranges,
                but rather models a computational ecology of presence, shaped by:<br
                />
                institutional data collection practices; historical herbarium biases;
                uneven geopolitical sampling infrastructures.<br />As such, the
                resulting spatial patterns should be interpreted as
                data-mediated ecologies, not neutral representations of nature.

                <br /><br /><br />BIBLIOGRAPHY FOR RECIPES<br />
                Mazzei R, Genovese C, Magariello A, Patitucci A, Russo G, Tagarelli
                G. Plants in Menstrual Diseases: A Systematic Study from Italian
                Folk Medicine on Current Approaches. Plants (Basel). 2024 Feb 22;13(5):589.
                doi: 10.3390/plants13050589. PMID: 38475436; PMCID: PMC10935160.<br
                />
                Motti, R., Bonanomi, G., Emrick, S. et al. Traditional Herbal Remedies
                Used in women’s Health Care in Italy: a Review. Hum Ecol 47, 941–972
                (2019).<br />
            </div>
        </div>
    </aside>
{/if}

<style>
    .panel {
        position: fixed;
        top: 0.5vh; /* (100 - 75) / 2 */
        right: 0.5rem;

        width: 50vw;
        max-width: 420px;
        height: 90vh;

        background: var(--rose);
        border: 1px solid var(--rose-pale);

        display: flex;
        flex-direction: column;

        z-index: 1000;
    }

    .content {
        padding: 1.25rem;
        overflow-y: auto;

        font-family: var(--serif);
        font-size: 0.95rem;
        font-weight: 400;
        line-height: 1.32;
        color: var(--paper);
    }

    .method {
        font-size: 0.8rem;
        padding: 1.25rem;
        border: 1px solid var(--rose-pale);
        margin-top: 3em;
    }

    .close {
        align-self: flex-end;
        font-family: var(--mono);
        font-size: 1.8rem;
        padding: 0.4rem 0.6rem;
        color: var(--paper);
    }

    .close:hover {
        background: none;
    }

    @media (max-width: 600px) {
        .panel {
            bottom: 0;
            right: 0;
            left: 0;
            top: auto;

            width: 100vw;
            max-width: none;
            height: 50vh;

            border-top: 1px solid var(--rose-pale);
            border-right: none;
        }
    }
</style>
