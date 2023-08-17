<script setup>
import axios from 'axios';
import { writeData, queryData, searchData } from '../apiHelper';
import { ref, onMounted, computed, nextTick, watch } from 'vue'

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

const clearFile = () => {
  document.getElementById('formFile').value = ''
}
</script>

<template>
  <main>
    <h2>Slates</h2>
    <!-- date picker -->
    <div class="upload-button">
      <!-- :disabled="!Object.keys(byPlayerId).length" -->
      <input class="form-control" @change="fileUploaded" type="file" id="formFile">
      <button class="btn btn-outline-danger" type="button" @click="clearFile">clear</button>
    </div>
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
</style>