<script setup>
import { ref, onMounted, computed, nextTick, watch } from 'vue'
import ComboBox from '../components/ComboBox.vue'
  
const props = defineProps({
})

const emits = defineEmits([])

const selectedSite = ref('')
const date = ref(new Date().toISOString().slice(0, 10))

const lockTimes = ref('')
const slateId = ref('')
const contestId = ref('')

// Pick a day and a site and a sport

// show the different lock times throughout that day
// show contest data we have for that day

// pick a projections algorithm
// pick times to optimize and reoptimize until the end of the slate
// compare scores with the field
</script>

<template>
  <main>
    <h1>Backtester</h1>

    <!-- <div class="slate-filter">
      <ComboBox :array="['FD NBA', 'DK NBA']" 
        v-model="selectedSite"
        placeholder="site" />

      <VueDatePicker class="datepicker" v-model="date" 
      :month-change-on-scroll="false"
      auto-apply
      text-input
      :enable-time-picker="false"
      ></VueDatePicker>
    </div> -->
    <div class="input-grid">
      <p>Slate Id:</p>
      <input type="text" placeholder="slateId" v-model="slateId">
      <p>Contest Id:</p>
      <input type="text" placeholder="contestId" v-model="contestId">
      <p>Lock times:</p>
      <input type="text" placeholder="lock times" v-model="lockTimes">

    </div>
  </main>
</template>

<style scoped>

.input-grid {
  display: grid;
  grid-template-columns: 10rem 20rem;
}

.slate-filter {
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 1rem;
  margin: 1rem 0;
}
</style>