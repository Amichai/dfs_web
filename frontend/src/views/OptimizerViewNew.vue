<script setup>
import { ref, onMounted, computed, nextTick, watch } from 'vue'
import ComboBox from '../components/ComboBox.vue'
import SlateSetup from '../components/SlateSetup.vue'
import { getSlates, getSlatePlayers } from '../apiHelper';
import { getDateString } from '../utils';
  
const props = defineProps({

})

const slateIds = ref([])

const addSlate = () => {
  slateIds.value.push(lowestAvailableId())
  localStorage.setItem(`slateIds`, slateIds.value.join(','))
}

const removeSlate = (index) => {
  slateIds.value.splice(index, 1)
  console.log("Remove slate slateIds", slateIds.value)
  localStorage.setItem(`slateIds`, slateIds.value.join(','))
}

onMounted(async () => {
  const slateIdsString = localStorage.getItem(`slateIds`)
  slateIds.value = slateIdsString === '' ? [] :
    slateIdsString?.split(',')?.map(s => parseInt(s)) ?? []

  console.log("slateIds", slateIds.value)
})

const lowestAvailableId = () => {
  let id = 0
  while (slateIds.value.filter(slateId => slateId === id).length) {
    id += 1
  }

  console.log("lowestAvailableId", id)
  return id
}

const emits = defineEmits([])


</script>

<template>
  <main>
    <h1>Optimizer</h1>
    <div v-for="(slateId, index) in slateIds" :key="slateId">
      <SlateSetup
        :id="slateId"
        @delete="() => removeSlate(index)"
        />
    </div>

    <button class="button" @click="addSlate">Add Slate</button>
<!-- 

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
    <p>Show lock-time exposure</p> -->

    <!-- <ComboBox :array="slates" 
      v-model="selectedSlate"
      :renderer="slate => `${slate.sport} ${slate.date}`"
      @update:model-value="selectedSlateChanged"
      placeholder="site" /> -->

  </main>
</template>

<style>

</style>