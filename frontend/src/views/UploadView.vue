<script setup>
import axios from 'axios';
import { writeData, queryData, searchData } from '../apiHelper';
import { FDParser, DKParser } from '../parsers';
import { ref, onMounted, computed, nextTick, watch } from 'vue'
import ComboBox from '../components/ComboBox.vue'
import Column from 'primevue/column';
import DataTable from 'primevue/datatable';
import TableComponent from '../components/TableComponent.vue'

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

const slatesToParsers = {
  'FD NBA': new FDParser(),
  'FD NFL': new FDParser(),
  'FD MLB': new FDParser(),
  'DK': new DKParser(),
}

const parsedContent = ref({})

let parser = null;
const reader = new FileReader();
const date = ref(new Date().toISOString().slice(0, 10))
const slateId = ref('')
const selectedSlate = ref('')
const sport = ref('')

const uploadSlate = () => {
  parser.upload(slateId.value, date.value, sport.value)
}

const fileUploaded = (evt) => {
  const files = evt.target.files; // FileList object
  const f = files[0];
  const name = f.name;
  if (name.includes('players-list')) {
    /// This is an FD file and we can parse the name
    console.log('players list')
    const parts = name.split('-');
    sport.value = parts[1];
    const year = parts[2].replace(' ET', '');
    const month = parts[3].replace(' ET', '');
    const day = parts[4].replace(' ET', '');
    date.value = `${year}-${month}-${day} EST`
    slateId.value = parts[5];
    selectedSlate.value = 'FD ' + sport.value
  } else if(name.includes('DKSalaries') ) {
    selectedSlate.value = 'DK'
    date.value = ''
    slateId.value = ''
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
      
      parser = slatesToParsers[selectedSlate.value]
      if(!parser) {
        console.log('no slate selected')
        return
      }

      parsedContent.value = parser.parse(content)
    };
  })();

  reader.readAsText(f);
}

const clearFile = () => {
  document.getElementById('formFile').value = ''

  parsedContent.value = {
    columns: [],
    mappedVals: []
  }
}
</script>

<template>
  <main>
    <h2>Upload</h2>
    <div class="slate-filter">
      <ComboBox :array="Object.keys(slatesToParsers)" 
        v-model="selectedSlate"
        placeholder="site" />

      <VueDatePicker class="datepicker" v-model="date" 
      :month-change-on-scroll="false"
      auto-apply
      text-input
      :enable-time-picker="false"
      ></VueDatePicker>
    </div>
    <hr />
    <div class="input-file-row">
      <input class="form-control" @change="fileUploaded" type="file" id="formFile">
      <button class="btn btn-outline-danger" type="button" @click="clearFile">×</button>
    </div>
    
    <div class="upload-data-row">
      <input type="text" placeholder="slate id" v-model="slateId">
      <button class="btn upload-data-button" type="button" @click="uploadSlate"
      :disabled="!slateId || !date"
      >Upload</button>
    </div>
    <br>
    <TableComponent :content="parsedContent" 
      v-show="parsedContent?.mappedVals?.length > 0" 
    />
    <br><br>
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

.slate-filter {
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 1rem;
  margin: 1rem 0;
}

.upload-data-button {
  font-size: var(--fs-0);
  padding: 0.3rem;
  color: white;
}

.upload-data-row {
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 1rem;
}
</style>
