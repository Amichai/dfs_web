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
{
  sport: 'FIBA',
  site: 'PrizePicks',
  displayName: 'PP FIBA',
  scraperName: 'PrizePicks_FIBA',
},
{
  sport: 'NBA',
  site: 'PrizePicks',
  displayName: 'PP NBA',
  scraperName: 'PrizePicks_NBA',
},
{
  sport: 'NBA',
  site: 'Caesars',
  displayName: 'Caesars NBA',
  scraperName: 'Caesars_NBA',
},
]

const scrapeSport = async (sport, site) => {
  await runScraper(sport, site)

  await selectedScraperChanged()
}

const scrape = async () => {
  const matched = scrapeOptions.find((option) => option.displayName === selectedScraper.value)
  if(!matched) {
    alert('scraper not found')
  }

  await runScraper(matched.sport, matched.site)

  await selectedScraperChanged()
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
const columns = ref(['start_time', 'line_score', 'name', 'stat', 'team', 'active'])

const parseScrapedLines = (lines) => {
  return lines.map((line) => {
    return columns.value.reduce((acc, value, index) => {
      acc[value] = line[value]
      return acc
    }, {})
  })

  // return lines
  const name_stats = Object.keys(lines)

  return name_stats.map((name_stat) => {
    return columns.value.reduce((acc, value, index) => {
      if(!lines[name_stat].current) {
        return acc
      }

      acc[value] = lines[name_stat].current[value]
      return acc
    }, {})
  })
}

onMounted(async () => {
  const lines = await getScrapedLines('Caesars_NBA')
  scrapedLines.value = parseScrapedLines(lines).filter((line) => Object.keys(line).length)
})

const selectedScraperChanged = async () => {
  const matched = scrapeOptions.find((option) => option.displayName === selectedScraper.value)
  if(!matched) {
    return
  }

  const lines = await getScrapedLines(matched.scraperName)

  scrapedLines.value = scrapedLines.value = parseScrapedLines(lines)
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

    <!-- <div class="scrapers-area">
      <ComboBox :array="scrapers" 
          v-model="selectedScraper"
          @update:modelValue="selectedScraperChanged"
          placeholder="site" />
      <button class="btn btn-primary scrape-button" @click="scrape">Scrape</button>
    </div> -->
    <button class="btn btn-primary scrape-button button-margin" @click="() => scrapeSport('NBA', 'Caesars')">Scrape Caesars NBA</button>
    <button class="btn btn-primary scrape-button button-margin" @click="() => scrapeSport('NFL', 'PrizePicks')">Scrape PP NFL</button>
    <!-- <button class="btn btn-primary scrape-button button-margin" @click="() => scrapeSport('NBA', 'PrizePicks')">PP NBA</button> -->
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

<style scoped>
.scrape-button {
  font-size: var(--fs-0);
  padding: 0.3rem 1.1rem;
  color: white;
}

.button-margin {
  margin: 0.6rem 1rem;
}

.scrapers-area {
  display: flex;
  gap: 2rem;
}
</style>