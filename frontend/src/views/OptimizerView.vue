<script setup>
import { ref, onMounted, computed, nextTick, watch } from 'vue'
import { runOptimizer, runReoptimizer } from '../apiHelper';
import Papa from 'papaparse';
  
const props = defineProps({
  msg: {
    type: String,
    required: false
  }
})

const emits = defineEmits([])
const reader = new FileReader();

const constructOutputFile = (rosters) => {
  const lines = contests.value.split('\n')
  let toWrite = ''
  toWrite += lines[0] + '\n'
  for(var i = 1; i < lines.length; i += 1) {
    const line = lines[i]
    const splitLine = line.split(',')
    const p1 = splitLine[0]
    const p2 = splitLine[1]
    const p3 = splitLine[2]
    const roster = rosters[i - 1]
    const playerParts = roster.players.split(',')
    toWrite += `"${p1}","${p2}","${p3}",`
    playerParts.forEach((element) => {
      toWrite += `"${element}",`
    });
    
    toWrite += `${roster.value},`
    toWrite += `${roster.cost}\n`
  }
  
  // toWrite = toWrite.slice(0, -1);
  toWrite = toWrite.replace(/\r\n/g, '\n');
  console.log(toWrite)
  const blob = new Blob([toWrite], { type: 'text/plain' });
  const url = window.URL.createObjectURL(blob);

// Create an anchor element for the download link
  const a = document.createElement('a');
  // a.href = url;
  // a.download = 'fd_upload.csv';
  a.setAttribute('download', 'fd_upload.csv');
  a.setAttribute('href', url);

// Trigger a click event on the download link to initiate the download
  a.click();

  // Clean up by revoking the object URL
  window.URL.revokeObjectURL(url);

}

const optimize = async (sport, site, type) => {
  const result = await runOptimizer(sport, site, type, slateId.value, rosterCount.value, iterCount.value, excludedPlayers.value)
  // debugger
  // todo render this result
  console.log(result)
  constructOutputFile(result)


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
  // debugger
  // todo render this result
  console.log(result)
}

const sport = ref('NFL')
const slateId = ref('')
const contests = ref('')
const iterCount = ref(0)
const rosterCount = ref(0)
const excludedPlayers = ref('')

onMounted(() => {
  sport.value = localStorage.getItem('sport')
  slateId.value = localStorage.getItem('slateId')
  rosterCount.value = localStorage.getItem('rosterCount')
  iterCount.value = localStorage.getItem('iterCount')
  contests.value = localStorage.getItem('contests')
  excludedPlayers.value = localStorage.getItem('excludedPlayers')
})

watch(() => sport.value, (newVal, oldVal) => {
  localStorage.setItem('sport', newVal)
})

watch(() => slateId.value, (newVal, oldVal) => {
  localStorage.setItem('slateId', newVal)
})

watch(() => rosterCount.value, (newVal, oldVal) => {
  localStorage.setItem('rosterCount', newVal)
})

watch(() => iterCount.value, (newVal, oldVal) => {
  localStorage.setItem('iterCount', newVal)
})

watch(() => contests.value, (newVal, oldVal) => {
  localStorage.setItem('contests', newVal)
})

watch(() => excludedPlayers.value, (newVal, oldVal) => {
  localStorage.setItem('excludedPlayers', newVal)
})

/// show a table with every player's projcetions (source of the projection, last updated, etc.)
/// Text input for overriding projections
///Settings to modify projection source

/// Optimize button
/// Upload a slate file
// Modeled after existing optimizer site
</script>

<template>
  <main>
    <h1>Optimizer FD</h1>
    <br>
    <div class="settings">
      <p>sport:</p>
      <p>slate id:</p>
      <!-- <p>TODO: we need a dropdown of today's slates here!</p> -->

      <input type="text" placeholder="sport" v-model="sport">
      <input type="text" placeholder="slateId" v-model="slateId">
      
      <p>roster count:</p>
      <input type="text" placeholder="roster count" v-model="rosterCount">
      
      <p>iter count:</p>
      <input type="text" placeholder="iter" v-model="iterCount">
      
      

      <textarea class="exclude-text" name="" id="" cols="30" rows="2" placeholder="exclude players" v-model="excludedPlayers"></textarea>
    </div>
    <!-- <button class="button" @click="() => optimize(sport, 'fd', 'single_game')">Optimize Single Game FD</button> -->
    <br>
    <textarea name="roste
    rs" class="roster-results" rows="3" placeholder="contests" v-model="contests"></textarea>


    <div class="input-file-row">
      <input class="form-control" @change="uploadSlateFile" type="file" id="formFile">
      <button class="btn btn-outline-danger" type="button" @click="clearFile">×</button>
    </div>

    <button class="button" @click="() => optimize(sport, 'fd', '')">Optimize FD</button>
    <button class="button" @click="() => reoptimize(sport, 'fd', '')">Reoptimize</button>
  </main>
</template>

<style scoped>

.input-file-row {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
  margin: 1rem 0;
}

#formFile {
  width: 100%;
  color: white;
  font-size: 0.9em;
  padding: 0;
}

.button {
  margin: 1rem 0;
  margin-right: 2rem;
  padding: 0.5rem 1rem;
}

.settings {
  display: grid;
  grid-template-columns: 9rem 24rem;
  gap: 1rem;
}

.roster-results {
  width: 100%;
  height: 10rem;
  padding: 0;
  border-radius: 0.25rem;
  /* resize: none; */
}

.exclude-text {
  grid-column: span 2
}
</style>