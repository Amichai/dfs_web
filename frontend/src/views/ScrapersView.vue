<script setup>
import { ref, onMounted, computed, nextTick, watch } from 'vue'
import ComboBox from '../components/ComboBox.vue'
import { runScraper, getScrapedLines } from '../apiHelper';
import TableComponent from '../components/TableComponent.vue'


const scrapeOptions = [{
  sport: 'NFL',
  site: 'PrizePicks',
  displayName: 'PP NFL',
  scraperName: 'PrizePicks_NFL',
},
{
  sport: 'WNBA',
  site: 'PrizePicks',
  displayName: 'PP WNBA',
  scraperName: 'PrizePicks_WNBA',
},
{
  sport: 'WNBA',
  site: 'Caesars',
  displayName: 'Caesars WNBA',
  scraperName: 'Caesars_WNBA',
},
]

const scrape = () => {
  const matched = scrapeOptions.find((option) => option.displayName === selectedScraper.value)
  if(!matched) {
    alert('scraper not found')
  }

  runScraper(matched.sport, matched.site)
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

const scrapers = ref(scrapeOptions.map((option) => option.displayName))

const scrapedLines = ref([])
const columns = ref(['time', 'line_score', 'name', 'stat', 'team', 'updated_at'])

onMounted(async () => {
  const lines = await getScrapedLines('PrizePicks_NFL')

  scrapedLines.value = lines.map((row) => {
    return columns.value.reduce((acc, value, index) => {
      acc[value] = row[value]
      return acc
    }, {})
  })
})

const selectedScraperChanged = async () => {
  const matched = scrapeOptions.find((option) => option.displayName === selectedScraper.value)
  if(!matched) {
    return
  }

  const lines = await getScrapedLines(matched.scraperName)

  scrapedLines.value = lines.map((row) => {
    return columns.value.reduce((acc, value, index) => {
      acc[value] = row[value]
      return acc
    }, {})
  })
}

const toEpochSeconds = (dateString) => {
  const date = new Date(dateString);
  return Math.floor(date.getTime() / 1000);
}

///TODO: add an input box for filtering rows
</script>

<template>
  <main>
    <h1>Scrapers</h1>
    <br>

    <div class="scrapers-area">
      <ComboBox :array="scrapers" 
          v-model="selectedScraper"
          @update:modelValue="selectedScraperChanged"
          placeholder="site" />
      <button class="btn btn-primary scrape-button" @click="scrape">Scrape</button>
    </div>
    <br>
    <hr>
    <br>
    
    <TableComponent 
      :columns="columns ?? []"
      :mappedVals="scrapedLines ?? []"
      :columnMapper="{
        'time': timeAgo,
        'updated_at': (val) => timeAgo(toEpochSeconds(val))
      }"
    />

    <br><br><br>
  </main>
</template>

<style>
.scrape-button {
  font-size: var(--fs-0);
  padding: 0.3rem 1.1rem;
  color: white;
}

.scrapers-area {
  display: flex;
  gap: 2rem;
}
</style>