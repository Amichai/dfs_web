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
  // const result = await getSlates('2023-09-18')
  // slates.value = result
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


    <p>scrape button</p>
    <p>Optimize all slates</p>

    <p>add slate</p>
    <ul>
      <li>sport</li>
      <li>slate id</li>
      <li>site</li>
      <li>roster count</li>
      <li>iter count</li>
      <li>optimize</li>
      <li>reoptimize</li>
      <li>exclude</li>
      <li>existing rosters</li>
      <li>remove this slate</li>
    </ul>
    <p>Show player exposure</p>
    <p>Show lock-time exposure</p>

    <ComboBox :array="slates" 
      v-model="selectedSlate"
      :renderer="slate => `${slate.sport} ${slate.date}`"
      @update:model-value="selectedSlateChanged"
      placeholder="site" />

  </main>
</template>

<style>
</style>