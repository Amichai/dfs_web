<script setup>
import { ref, onMounted, computed, nextTick, watch } from 'vue'
import { runOptimizer, runReoptimizer, getRosterExposures } from '../apiHelper';
import Papa from 'papaparse';
  
const props = defineProps({
  // slateSettings: {
  //   type: Object,
  //   required: true
  // },
  id: {
    type: Number,
    required: true
  }
})

const emits = defineEmits(['delete'])
const reader = new FileReader();

const sport = ref('NBA')
const site = ref('fd')
const slateId = ref('')
const contests = ref('')
const iterCount = ref('11')
const rosterCount = ref(0)
const excludedPlayers = ref('')
const slateName = ref('')
const startTime = ref('7')
const gameType = ref('')

const slatePlayers = ref([])
const playerExposures = ref({})
const startTimeExposures = ref({})

const resetVals = () => {
  console.log('Resetting', props.id)
  sport.value = 'NBA'
  site.value = 'fd'
  slateId.value = ''
  contests.value = ''
  iterCount.value = 0
  rosterCount.value = 0
  excludedPlayers.value = ''
  slateName.value = ''
  startTime.value = 0
  gameType.value = ''
}

onMounted(() => {
  console.log('Mounted', props.id)
  sport.value = localStorage.getItem(`sport_${props.id}`)
  slateId.value = localStorage.getItem(`slateId_${props.id}`)
  rosterCount.value = localStorage.getItem(`rosterCount_${props.id}`)
  iterCount.value = localStorage.getItem(`iterCount_${props.id}`)
  contests.value = localStorage.getItem(`contests_${props.id}`)
  excludedPlayers.value = localStorage.getItem(`excludedPlayers_${props.id}`)
  slateName.value = localStorage.getItem(`slateName_${props.id}`)
  startTime.value = localStorage.getItem(`startTime_${props.id}`)
  site.value = localStorage.getItem(`site_${props.id}`)
  gameType.value = localStorage.getItem(`gameType_${props.id}`)
})

watch(() => sport.value, (newVal) => {
  localStorage.setItem(`sport_${props.id}`, newVal)
})

watch(() => slateId.value, (newVal) => {
  localStorage.setItem(`slateId_${props.id}`, newVal)
})

watch(() => rosterCount.value, (newVal) => {
  localStorage.setItem(`rosterCount_${props.id}`, newVal)
})

watch(() => iterCount.value, (newVal) => {
  localStorage.setItem(`iterCount_${props.id}`, newVal)
})

watch(() => contests.value, (newVal) => {
  localStorage.setItem(`contests_${props.id}`, newVal)
})

watch(() => excludedPlayers.value, (newVal) => {
  localStorage.setItem(`excludedPlayers_${props.id}`, newVal)
})

watch(() => slateName.value, (newVal) => {
  localStorage.setItem(`slateName_${props.id}`, newVal)
})

watch(() => startTime.value, (newVal) => {
  localStorage.setItem(`startTime_${props.id}`, newVal)
})

watch(() => site.value, (newVal) => {
  localStorage.setItem(`site_${props.id}`, newVal)
})

watch(() => gameType.value, (newVal) => {
  localStorage.setItem(`gameType_${props.id}`, newVal)
})

const constructOutputFile = (rosters, filename) => {
  const lines = contests.value.split('\n')
  let toWrite = ''
  toWrite += lines[0] + '\n'
  for(var i = 1; i < lines.length; i += 1) {
    const line = lines[i]
    const splitLine = line.split(',')
    const p1 = splitLine[0]
    const p2 = splitLine[1]
    const p3 = splitLine[2]
    const p4 = splitLine[3]
    const roster = rosters[i - 1]
    const playerParts = roster.players.split(',')
    if(site.value === 'fd') {
      toWrite += `"${p1}","${p2}","${p3}",`
    } else {
      toWrite += `"${p1}","${p2}","${p3}","${p4}",`
    }
    playerParts.forEach((element) => {
      toWrite += `"${element}",`
    });
    
    toWrite += `${roster.value},`
    toWrite += `${roster.cost}\n`
  }
  
  toWrite = toWrite.replace(/\r\n/g, '\n');
  console.log(toWrite)
  const blob = new Blob([toWrite], { type: 'text/plain' });
  const url = window.URL.createObjectURL(blob);

  const a = document.createElement('a');
  a.setAttribute('download', filename);
  a.setAttribute('href', url);

  a.click();
  window.URL.revokeObjectURL(url);
}

const getCurrentTimeDecimal = () => {
  var now = new Date();
  var current_time = (now.getHours() - 12) + (now.getMinutes() / 60);
  current_time = Math.round(current_time * 100) / 100; // rounding to 2 decimal places
  return current_time;
}

const showExposures = async () => {
  const exposures = await getRosterExposures(slateId.value, contests.value, sport.value, site.value)
  
  slatePlayers.value = JSON.parse(exposures.name_to_player)
  playerExposures.value = Object.keys(exposures.player_exposures).map((player) => {
    return [player, exposures.player_exposures[player]]
  }).sort((a, b) => b[1] - a[1])

  startTimeExposures.value = exposures.start_times

  console.log(playerExposures.value)
  console.log(startTimeExposures.value)
}


const optimize = async () => {
  const currentTime = getCurrentTimeDecimal()
  if (currentTime > startTime.value) {
    // alert('Slate has already started')
    // return


    const result = await runReoptimizer(sport.value, site.value, 
    gameType.value, slateId.value, rosterCount.value, iterCount.value, contests.value, excludedPlayers.value)
    constructOutputFile(result, `${site.value}_${slateName.value}_${slateId.value}_reopto.csv`)
  } else {

    const result = await runOptimizer(sport.value, site.value, 
    gameType.value, slateId.value, rosterCount.value, iterCount.value, excludedPlayers.value)
    constructOutputFile(result, `${site.value}_${slateName.value}_${slateId.value}.csv`)
  }
}

const uploadSlateFile = (evt) => {
  const files = evt.target.files; // FileList object
  const f = files[0];
  const name = f.name;

  reader.onload = (() => {
    return function (e) {
      const content = e.target.result
      const result = Papa.parse(content)
      const filteredRows = result.data.filter(row => row[0] !== '').map(row => row.slice(0, 13))
      
      contests.value = Papa.unparse(filteredRows)
      rosterCount.value = filteredRows.length - 1
    };
  })();

  reader.readAsText(f);
}

const reoptimize = async  (sport, site, type) => {
  const result = await runReoptimizer(sport, site, type, slateId.value, rosterCount.value, iterCount.value, contests.value, excludedPlayers.value)
  console.log(result)
  constructOutputFile(result, `${site}_reoptimize.csv`)
}

const deleteSlate = () => {
  resetVals()
  nextTick(() => {
    emits('delete')
  })
}

</script>

<template>
  <div class="root">
    <div class="header">
      <button class="button" @click="deleteSlate">delete</button>
    </div>
    <div class="input-grid">
      <div>Sport:</div>
      <input type="text" placeholder="sport" v-model="sport">
      <div>Site:</div>
      <input type="text" placeholder="site" v-model="site">
      <div>Slate:</div>
      <input type="text" placeholder="slateId" v-model="slateId">
      <div>Type:</div>
      <input type="text" placeholder="type" v-model="gameType">

      <div>Name:</div>
      <input type="text" placeholder="name" v-model="slateName">
      <div>Iter:</div>
      <input type="text" placeholder="iter" v-model="iterCount">
      <div>Roster ct:</div>
      <input type="text" placeholder="roster count" v-model="rosterCount">
      <div>Start time:</div>
      <input type="text" placeholder="start time" v-model="startTime">
      <div>Exclude:</div>
      <textarea class="exclude-text span-3" name="" id="" cols="30" rows="2" placeholder="exclude players" v-model="excludedPlayers"></textarea>
      <div>Contests:</div>
      <textarea name="rosters" class="roster-results span-3" rows="3" placeholder="contests" v-model="contests"></textarea>
      <div class="input-file-row">
        <input class="form-control" @change="uploadSlateFile" type="file" id="formFile">
        <button class="btn btn-outline-danger" type="button" @click="clearFile">×</button>
      </div>
    </div>
    <button class="button" @click="optimize">Optimize</button>
    <button class="button" @click="showExposures">Show/Hide Exposures</button>
    <div class="exposure-grid">
      <div>
      <div class="player-exposure-grid grid-header">
        <div>idx</div>
        <div>name</div>
        <div>ct</div>
      </div>
      <div v-for="(player, index) in playerExposures" :key="index" class="player-exposure-grid">
        <div>{{ index + 1}}</div>
        <div>{{ player[0] }}</div>
        <div>{{ player[1] }} / {{ rosterCount }}</div>
      </div>
    </div>
      <!-- <div>test2</div> -->
    </div>
    
  </div>
</template>

<style>
.input-grid {
  display: grid;
  grid-template-columns: 6rem 1fr 6rem 1fr;
  gap: 0.5rem
}

.player-exposure-grid {
  font-size: 0.8rem;
  display: grid;
  grid-template-columns: 1fr 9rem 5rem 1fr 1fr 1fr 1fr;
}

.span-3 {
  grid-column: span 3;
}

.input-file-row {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
  margin: 1rem 0;
  grid-column: span 4;
}

#formFile {
  width: 100%;
  color: white;
  font-size: 0.9em;
  padding: 0;
}

.button {
  margin: 0.1rem 0;
  margin-right: 2rem;
  padding: 0.5rem 1rem;
}

.root {
  border: 1px solid white;
  padding: 1rem;
}

.header {
  display: flex;
  flex-direction: row-reverse;
}

.game-type {
  display: flex;
  gap: 0.5rem;
}

.exposure-grid {
  border-radius: 0.5rem;
  margin: 0.5rem;
  padding: 0.5rem;
  background-color: lightgray;
  color: black;
  display: grid;
  grid-template-columns: 1fr 1fr;
}

.grid-header {
  font-weight: bold;
}
</style>