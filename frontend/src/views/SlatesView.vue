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

/// handle uploads of slate files
/// diff the data and only write new data to the db
/// show today's slate files with date picker, sport picker, site picker, etc

const slatesToParsers = {
  'FD NBA': new FDParser(),
  'FD NFL': new FDParser(),
  'FD MLB': new FDParser(),
  'DK NBA': new DKParser(),
  'DK NFL': new DKParser(),
  'DK MLB': new DKParser(),
}

const parsedContent = ref([{ name: 'name1', value: 'test1' }])

const fileUploaded = (evt) => {
  const files = evt.target.files; // FileList object
  const f = files[0];
  const name = f.name;
  if (name.includes('players-list')) {
    /// This is an FD file and we can parse the name
    console.log('players list')
    const parts = name.split('-');
    const sport = parts[1];
    const year = parts[2].replace(' ET', '');
    const month = parts[3].replace(' ET', '');
    const day = parts[4].replace(' ET', '');
    date.value = `${year}-${month}-${day} EST`
    slateId.value = parts[5];
    selectedSlate.value = 'FD ' + sport
  } else if(name.includes('DKSalaries') ) {
    /// this is a DK file
  } else {
    alert('file name not recognized')
    return
  }

  if (!name.includes('.csv')) {
    alert('not a csv file')
    return 
  }

  const reader = new FileReader();

  reader.onload = (() => {
    return function (e) {
      const content = e.target.result
      const parser = slatesToParsers[selectedSlate.value]

      if(!parser) {
        console.log('no slate selected')
        return
      }

      parsedContent.value = parser.parse(content)
    };
  })();

  reader.readAsText(f);
}

const date = ref(new Date().toISOString().slice(0, 10))

const selectedSlate = ref('')

const selectedChanged = (val) => {
  selectedSlate.value = val
}

const clearFile = () => {
  document.getElementById('formFile').value = ''

  parsedContent.value = {
    columns: [],
    mappedVals: []
  }
}

const slateId = ref('')

</script>

<template>
  <main>
    <h2>Slates</h2>
    <div class="slate-filter">
      <ComboBox :array="Object.keys(slatesToParsers)" @selected="selectedChanged"
        placeholder="slate" />

      <VueDatePicker class="datepicker" v-model="date" 
      :month-change-on-scroll="false"
      auto-apply
      text-input
      :enable-time-picker="false"
      ></VueDatePicker>
    </div>
    <hr />
    <div class="upload-button">
      <!-- :disabled="!Object.keys(byPlayerId).length" -->
      <input class="form-control" @change="fileUploaded" type="file" id="formFile">
      <button class="btn btn-outline-danger" type="button" @click="clearFile">×</button>
    </div>
    
    <input type="text" placeholder="slate id" :value="slateId">
    <button class="btn main-button" type="button">Upload</button>


    <TableComponent :content="parsedContent" />
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
  color: white;
  font-size: 0.9em;
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
