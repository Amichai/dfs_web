<script setup>
import { computed } from 'vue'

const path = computed(() => {
  return window.location.pathname.split('/')[1]
})

</script>

<template>
  <nav class="nav-bar">
    <a href="/upload" :class="['nav-item', path === 'upload' && 'selected']">Upload</a>
    <!-- <a href="/slates" :class="['nav-item', path === 'slates' && 'selected']">Slates</a> -->
    <a href="/scrapers" :class="['nav-item', path === 'scrapers' && 'selected']">Scrapers</a>
    <a href="/optimizer" :class="['nav-item', path === 'optimizer' && 'selected']">Optimizer</a>
    <a href="/optimizerdk" :class="['nav-item', path === 'optimizerdk' && 'selected']">Optimizer DK</a>
    <a href="/optimizernew" :class="['nav-item', path === 'optimizernew' && 'selected']">Optimizer New</a>
    <a href="/results" :class="['nav-item', path === 'results' && 'selected']">Results</a>
    <a href="/backtester" :class="['nav-item', path === 'backtester' && 'selected']">Backtester</a>
    <a href="/arbitrage" :class="['nav-item', path === 'arbitrage' && 'selected']">Arbitrage</a>
  </nav>
  <hr>
</template>

<style scoped>
.nav-bar {
  background-color: var(--clr-background);
  overflow: hidden;
}

.nav-item {
  float: left;
  display: block;
  color: #f2f2f2;
  text-align: center;
  padding: 14px 16px;
  text-decoration: none;
}

.nav-item:hover {
  background-color: #ddd;
  color: black;
}

.selected {
  background-color: #ddd;
  color: black;
}
</style>