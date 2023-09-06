<script setup>
import { ref, onMounted, computed, nextTick, watch } from 'vue'
import { DKResultsParser } from '../parsers';
import { writeData } from './../apiHelper';

const props = defineProps({})

const emits = defineEmits([])

const reader = new FileReader();
const dkParser = new DKResultsParser()


const contestId = ref('')
const entryFee = ref('')
const score1 = ref('')
const winning1 = ref('')
const score2 = ref('')
const winning2 = ref('')

const uploadSlate = () => {
  if (!slateId.value) {
    alert('no slate id')
    return
  }

  dkParser.upload(slateId.value)
}


const fileUploaded = (evt) => {
  const files = evt.target.files; // FileList object
  const f = files[0];
  const name = f.name;
  if (name.includes('contest-standings-')) {
    ///DK results
  } else {
    alert('file name not recognized')
    return
  }

  if (!name.includes('.csv')) {
    alert('not a csv file')
    return
  }

  reader.onload = (() => {
    return function (e) {
      const content = e.target.result
      dkParser.parse(content)
    };
  })();

  reader.readAsText(f);
}

const clearFile = () => {
  document.getElementById('formFile').value = ''
}

const uploadScores = async () => {
  const result = await writeData('ContestScores', {
    contestId: contestId.value,
    slateId: slateId.value,
    entryFee: entryFee.value,
    score1: score1.value,
    winning1: winning1.value,
    score2: score2.value,
    winning2: winning2.value,
  })

  contestId.value = ''
  entryFee.value = ''
  score1.value = ''
  score2.value = ''
  winning1.value = ''
  winning2.value = ''
}

const slateId = ref('')
</script>

<template>
  <main>
    <h1>Results</h1>
    <div class="input-file-row">
      <input class="form-control" @change="fileUploaded" type="file" id="formFile">
      <button class="btn btn-outline-danger" type="button" @click="clearFile">×</button>
    </div>
    <div class="upload-data-row">
      <input type="text" placeholder="slate id" v-model="slateId">
      <button class="btn upload-data-button" type="button" @click="uploadSlate" :disabled="!slateId">Upload</button>
    </div>
    <br>
    <hr>
    <br>
    <div >

    </div>
    <div class="contest-results">
      <p>Contest id:</p>
      <input type="text" placeholder="contest id" v-model="contestId">
      <p></p>
      <p>Entry fee:</p>
      <input type="text" placeholder="entry fee" v-model="entryFee">
      <p></p>
      <p>1st:</p>
      <input type="text" placeholder="highest score" v-model="score1">
      <input type="text" placeholder="winning" v-model="winning1">
      <p>Money:</p>
      <input type="text" placeholder="money line" v-model="score2">
      <input type="text" placeholder="winning" v-model="winning2">
    </div>
    <br>
    <button class="btn upload-data-button" type="button" @click="uploadScores" :disabled="!slateId || !contestId">Upload</button>
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

.upload-data-button {
  font-size: var(--fs-0);
  padding: 0.6rem;
  color: white;
}

.upload-data-row {
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 1rem;
}

.contest-results {
  display: grid;
  grid-template-columns: 6rem 1fr 1fr;
  gap: 1rem;
}
</style>