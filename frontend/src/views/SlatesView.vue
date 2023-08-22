<script setup>
import { ref, onMounted, computed, nextTick, watch } from 'vue'
import ComboBox from '../components/ComboBox.vue'
import { writeData, queryData, searchData } from '../apiHelper';


const date = ref(new Date().toISOString().slice(0, 10) + ' EST')

console.log(date.value + ' ET')

const slateInput = ref('')
const selectedSport = ref('')

const selectedSportChanged = () => {
  query();
}

const dateString = computed(() => {
  return new Date(date.value).toISOString().slice(0, 10)
})

const query = async () => {
  await queryData('slates', 'date', dateString.value).then((res) => {
    const filteredOnSport = res.filter((item) => {
      return !selectedSport.value || item.sport === selectedSport.value
    })
    if(filteredOnSport.length > 0) {
      const lastElement = filteredOnSport.pop()
      slateInput.value = lastElement.slate
      selectedSport.value = lastElement.sport
    } else {
      slateInput.value = ''
    }
  })
}

onMounted(async () => {
  await query();
})

const dateChanged = async () => {
  await query();
}

const submitSlate = () => {
  console.log(slateInput.value)
  if(!selectedSport.value) {
    alert('select a sport')
    return
  }

  writeData('slates', {
    date: dateString.value,
    slate: slateInput.value,
    sport: selectedSport.value
  })
}

const inputChanged = () => {
  const lines = slateInput.value.split('\n')

  for(var i = 0; i < lines.length; i += 1) {
    if(lines[i][0] === '@'){
      console.log(lines[i])
      const timeString1 = lines[i + 1]
      const timeString2 = lines[i + 2]
      const isString1Time = !isNaN(parseInt(timeString1[0]))
      const isString2Time = !isNaN(parseInt(timeString2[0]))
      if((isString1Time && isString2Time)
        || (!isString1Time && !isString2Time)
      ) {
        alert('failed to parse slate')
      }    
    }
  }

  console.log(lines)
}

</script>

<template>
  <main>
    <h1>Slates</h1>
    <div class="day-sport-selector">
      <VueDatePicker class="datepicker" v-model="date" 
        :month-change-on-scroll="false"
        auto-apply
        text-input
        :enable-time-picker="false"
        @update:modelValue="dateChanged"
      ></VueDatePicker>

      <ComboBox :array="['NBA', 'NFL', 'MLB']" 
        v-model="selectedSport"
        @update:model-value="selectedSportChanged"
        placeholder="site" />
    </div>
    <br>

      <textarea name="slate-input" class="slate-input" rows="10" v-model="slateInput" @change="inputChanged"></textarea>

      <br>
      <br>

      <button class="btn btn-primary upload-data-button" @click="submitSlate">Upload</button>
    </main>
</template>

<style scoped>
.slate-input {
  width: 100%;
}

.upload-data-button {
  font-size: var(--fs-0);
  padding: 0.3rem 1.1rem;
  color: white;
}

.day-sport-selector {
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 1rem;
  margin: 1rem 0;
}
</style>
