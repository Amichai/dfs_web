<script setup>
import { ref, onMounted, computed, nextTick, watch } from 'vue'
import ComboBox from '../components/ComboBox.vue'
import { runScraper } from '../apiHelper';

const scrape = () => {
  runScraper(selectedScraper.value)
}

const selectedScraper = ref('')

const scrapers = ref(['PP', 'Caesars', 'Underdog', 'DraftKings', 'Stokastic', 'DFS Crunch', 'NFL', 'NBA', 'MLB'])

</script>

<template>
  <main>
    <h1>Scrapers</h1>
    <br>

    <ComboBox :array="scrapers" 
        v-model="selectedScraper"
        placeholder="site" />
    <br>
    <button class="btn btn-primary scrape-button" @click="scrape">Scrape</button>
    <br>
  </main>
</template>

<style>
.scrape-button {
  font-size: var(--fs-0);
  padding: 0.3rem 1.1rem;
  color: white;
}
</style>