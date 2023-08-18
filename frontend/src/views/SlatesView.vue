<script setup>
import axios from 'axios';
import { writeData, queryData, searchData } from '../apiHelper';
import { ref, onMounted, computed, nextTick, watch } from 'vue'
import ComboBox from '../components/ComboBox.vue'

const fetchData = async () => {
  searchData('test1', 'test', 'test3').then((res) => {
    console.log(res);
  })

  // searchData('test1', 'time', '2023-08-17T02' ).then((res) => {
  //   console.log(res);
  // })
}

onMounted(async () => {
  await fetchData();
})

/// handle uploads of slate files
/// diff the data and only write new data to the db
/// show today's slate files with date picker, sport picker, site picker, etc

const fileUploaded = (evt) => {
  let files = evt.target.files; // FileList object
  let f = files[0];
  let reader = new FileReader();

  reader.onload = (() => {
    return function (e) {
      const content = e.target.result
      const lines = content.split('\n')
      // console.log(lines[0])

      // const slate = lines.map((line) => {
      //   const [id, position, firstName, nickName, lastName, FPPG, played, salary, game, team, opponent, injuryIndicator, injuryDetails, Tier] = line.split(',')
      //   return {
      //     id, position, firstName, nickName, lastName, FPPG
      //   }
      // })
    };
  })();

  reader.readAsText(f);
}

const date = ref(new Date().toISOString().slice(0, 10))

const selectedChanged = (val) => {
  console.log('test test', val)
}

const clearFile = () => {
  document.getElementById('formFile').value = ''
}
</script>

<template>
  <main>
    <h2>Slates</h2>
    <div class="slate-filter">
      <ComboBox :array="['NBA FD', 'NFL FD', 'MLB FD', 'NBA DK', 'NFL DK', 'MLB DK']" @selected="selectedChanged"
        placeholder="slate" />

      <VueDatePicker class="datepicker" v-model="date" 
      :month-change-on-scroll="false"
      auto-apply
      text-input
      :enable-time-picker="false"
      ></VueDatePicker>
    </div>
    <div class="upload-button">
      <!-- :disabled="!Object.keys(byPlayerId).length" -->
      <input class="form-control" @change="fileUploaded" type="file" id="formFile">
      <button class="btn btn-outline-danger" type="button" @click="clearFile">×</button>
    </div>

    <button class="btn main-button" type="button">Upload</button>
  </main>
</template>

<style scoped>
.upload-button {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
  margin: 1rem;
}

#formFile {
  width: 100%;
}

.slate-filter {
  display: flex;
  flex-direction: row;
  align-items: center;
}

.main-button {
  margin: 1rem;
  font-size: var(--fs-1);
}
</style>