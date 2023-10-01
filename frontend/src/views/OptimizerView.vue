<script setup>
import { ref, onMounted, computed, nextTick, watch } from 'vue'
import { runOptimizer } from '../apiHelper';
  
const props = defineProps({
  msg: {
    type: String,
    required: false
  }
})

const emits = defineEmits([])

const optimize = async (sport, site, type) => {
  const result = await runOptimizer(sport, site, type, slateId.value, rosterCount.value, iterCount.value)
  // debugger
  // todo render this result
  console.log(result)
}

const sport = ref('NFL')
const slateId = ref('')
const rosters = ref('')
const iterCount = ref(0)
const rosterCount = ref(0)

onMounted(() => {
  sport.value = localStorage.getItem('sport', sport.value)
  slateId.value = localStorage.getItem('slateId', slateId.value)
  rosterCount.value = localStorage.getItem('rosterCount', slateId.value)
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

/// show a table with every player's projcetions (source of the projection, last updated, etc.)
/// Text input for overriding projections
///Settings to modify projection source

/// Optimize button
/// Upload a slate file
// Modeled after existing optimizer site
</script>

<template>
  <main>
    <h1>Optimizer</h1>
    <br>
    <div class="settings">
      <p>sport:</p>
      <p>slate id:</p>

      <input type="text" placeholder="sport" v-model="sport">
      <input type="text" placeholder="slateId" v-model="slateId">
      
      <p>roster count:</p>
      <input type="text" placeholder="roster count" v-model="rosterCount">
      
      <p>iter count:</p>
      <input type="text" placeholder="iter" v-model="iterCount">
      
      <button class="button" @click="() => optimize(sport, 'fd', '')">Optimize FD</button>
      <button class="button" @click="() => optimize(sport, 'dk', '')">Optimize DK</button>
    </div>
    <button class="button" @click="() => optimize('NFL', 'fd', 'single_game')">Optimize Single Game FD</button>
    <br>
    <textarea name="rosters" class="roster-results" rows="3" placeholder="rosters" v-model="rosters" readonly></textarea>
  </main>
</template>

<style scoped>
.button {
  margin: 1rem 0;
  padding: 0.5rem 1rem;
}

.settings {
  display: grid;
  grid-template-columns: 9rem 9rem;
  gap: 1rem;
}

.roster-results {
  width: 100%;
  height: 10rem;
  padding: 0;
  border-radius: 0.25rem;
  resize: none;
}
</style>