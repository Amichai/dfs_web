<script setup>
import { ref, onMounted, computed, nextTick, watch } from 'vue'
import ComboBox from '../components/ComboBox.vue'
import { getSlates, getSlatePlayers } from '../apiHelper';
import { getDateString } from '../utils';
  
const props = defineProps({

})

const slates = ref(['test1'])


onMounted(async () => {
  // await getSlates(getDateString())
  const result = await getSlates('2023-09-18')
  slates.value = result
})

const selectedSlate = ref('')

const selectedSlateChanged = async (newVal, oldVal) => {
  console.log(newVal)
  // TODO: we should be getting the slateid from the selected slate
  // TODO: uploading a slate file, should write to the slates database
  const slateId = '94032'
  await getSlatePlayers(slateId, 'FD', 'nfl')
  // get the slate info!
}

const emits = defineEmits([])
</script>

<template>
  <main>
    <h1>Optimizer</h1>
    <p>[x] pick the slate from a dropdown</p>
    <p>[ ] show the players available for the slate</p>
    <p>[ ] show the projections</p>
    <p>[ ] show the projection sources</p>
    <p>[ ] start times</p>
    <p>[ ] Optimizer</p>
    <p>[ ] Show player exposures</p>

    <ComboBox :array="slates" 
      v-model="selectedSlate"
      :renderer="slate => `${slate.sport} ${slate.date}`"
      @update:model-value="selectedSlateChanged"
      placeholder="site" />

  </main>
</template>

<style>
</style>