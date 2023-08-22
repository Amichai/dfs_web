<script setup>
import { ref, onMounted, computed, nextTick, watch } from 'vue'


const emits = defineEmits([])

const scrape = () => {

}
</script>

<template>
  <main>
    <h1>Scrapers</h1>
    <br>
    <button class="btn btn-primary scrape-button" @click="scrape">Scrape</button>
    <div>

    </div>
  </main>
</template>

<style>
.scrape-button {
  font-size: var(--fs-0);
  padding: 0.3rem 1.1rem;
  color: white;
}
</style>