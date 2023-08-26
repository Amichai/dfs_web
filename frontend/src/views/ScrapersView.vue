<script setup>
import { ref, onMounted, computed, nextTick, watch } from 'vue'
import ComboBox from '../components/ComboBox.vue'
import { runScraper, getScrapedLines } from '../apiHelper';
import TableComponent from '../components/TableComponent.vue'

const scrape = () => {
  if(selectedScraper.value === 'PP NFL') {
    runScraper('NFL', 'PrizePicks')
  } else {
    alert('scraper not found')
  }
}

const timeAgo = (secondsFromEpoch) => {
  // Convert to milliseconds for Date object and comparison
  const pastDate = new Date(secondsFromEpoch * 1000);
  const now = new Date();
  
  const seconds = Math.floor((now - pastDate) / 1000);
  const minutes = Math.floor(seconds / 60);
  const hours = Math.floor(minutes / 60);
  const days = Math.floor(hours / 24);
  const weeks = Math.floor(days / 7);
  const months = Math.floor(days / 30);
  const years = Math.floor(days / 365);
  
  if (years > 0) {
    return years + ' year' + (years === 1 ? '' : 's') + ' ago';
  } else if (months > 0) {
    return months + ' month' + (months === 1 ? '' : 's') + ' ago';
  } else if (weeks > 0) {
    return weeks + ' week' + (weeks === 1 ? '' : 's') + ' ago';
  } else if (days > 0) {
    return days + ' day' + (days === 1 ? '' : 's') + ' ago';
  } else if (hours > 0) {
    return hours + ' hour' + (hours === 1 ? '' : 's') + ' ago';
  } else if (minutes > 0) {
    return minutes + ' minute' + (minutes === 1 ? '' : 's') + ' ago';
  } else {
    return 'just now';
  }
}

const selectedScraper = ref('')

const scrapers = ref(['PP NFL', 'Caesars', 'Underdog', 'DraftKings', 'Stokastic', 'DFS Crunch', 'NFL', 'NBA', 'MLB'])

const scrapedLines = ref([])
const columns = ref(['time', 'line_score', 'name', 'stat', 'team', 'updated_at'])

onMounted(async () => {
  const lines = await getScrapedLines('NFL')

  scrapedLines.value = lines.map((row) => {
    return columns.value.reduce((acc, value, index) => {
      acc[value] = row[value]
      return acc
    }, {})
  })
})

const toEpochSeconds = (dateString) => {
  const date = new Date(dateString);
  return Math.floor(date.getTime() / 1000);
}
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

    <TableComponent 
      :columns="columns ?? []"
      :mappedVals="scrapedLines ?? []"
      :columnMapper="{
        'time': timeAgo,
        'updated_at': (val) => timeAgo(toEpochSeconds(val))
      }"
    />

  </main>
</template>

<style>
.scrape-button {
  font-size: var(--fs-0);
  padding: 0.3rem 1.1rem;
  color: white;
}
</style>