<script setup>
import { writeSlate } from '../apiHelper';
import { FDParser, DKParser } from '../parsers';
import { ref, onMounted, computed, nextTick, watch } from 'vue'
import TableComponent from '../components/TableComponent.vue'


onMounted(async () => {
})

const inputChanged = () => {
  const lines = slateInput.value.split('\n')
  let gameCount = 0
  let startTime = null

  for(var i = 0; i < lines.length; i += 1) {
    if(lines[i][0] === '@'){
      gameCount += 1
      console.log(lines[i])
      const timeString1 = lines[i + 1]
      const timeString2 = lines[i + 2] ?? ''
      const isString1Time = !isNaN(parseInt(timeString1[0]))
      const isString2Time = !isNaN(parseInt(timeString2[0]))
      if((isString1Time && isString2Time)
        || (!isString1Time && !isString2Time)
      ) {
        alert('failed to parse slate')
      }

      if(!startTime) {
        startTime = (isString1Time ? timeString1 : timeString2).replace(' ET', '')
      }
    }
  }

  if(site.value == 'FD') {
    if (gameCount > 1) {
        slateId.value = `${site.value}_${startTime}_${gameCount}games`
      } else {
        slateId.value = `${site.value}_${startTime}_1game`
      }
    }
}

const slatesToParsers = {
  'FD NBA': new FDParser(),
  'FD NFL': new FDParser(),
  'FD MLB': new FDParser(),
  'DK NFL': new DKParser(),
  'DK FIBA': new DKParser(),
  'DK NBA': new DKParser(),
}

const slateInput = ref('')

const parsedContent = ref({})

let parser = null;
const reader = new FileReader();
const date = ref(new Date().toISOString().slice(0, 10))
const slateId = ref('')
const selectedSlate = ref('DK NBA')
const sport = ref('')

const site = computed(() => selectedSlate.value.split(' ')[0])

const uploadSlate = () => {
  // parser = slatesToParsers[selectedSlate.value]
  // parsedContent.value.mappedVals
  sport.value = 'NBA'

  const currentDate = new Date();
  const dateString = currentDate.toLocaleDateString('en-CA', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
  });
  if(slateId.value.includes(' ')) {
    debugger
  }

  writeSlate(sport.value, slateId.value, site.value.toLowerCase(), dateString,

  parsedContent.value.columns,
  parsedContent.value.mappedVals,
  slateInput.value.replaceAll('\n',','))
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
    date.value = `${year}-${month}-${day}`
    slateId.value = parts[5];
    selectedSlate.value = 'FD ' + sport.value
  } else if(name.includes('DKSalaries') ) {
    // selectedSlate.value = 'DK'
    // date.value = ''
    // slateId.value = ''
    sport.value = selectedSlate.value.split(' ')[1]
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

      if(site.value == 'DK') {
        const seenStartTimes = []
        const seenGames = []

        parsedContent.value.mappedVals.forEach(row => {
          const gameParts = row[4].split(' ')
          const game = gameParts[0]
          const startTime = gameParts[2]

          if(!seenStartTimes.includes(startTime)) {
            seenStartTimes.push(startTime)
          }

          if(!seenGames.includes(game)) {
            seenGames.push(game)
          }
        });

        if (seenGames.length > 1) {
          slateId.value = `${site.value}_${seenStartTimes.sort()[0]}_${seenGames.length}games`
        } else {
          slateId.value = `${site.value}_${seenStartTimes.sort()[0]}_${seenGames[0]}`
        }
      }
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
    <h1>Upload</h1>
    <div class="slate-filter">
      <div>{{ selectedSlate }}</div>

    </div>
    <hr />
    <div class="input-file-row">
      <input class="form-control" @change="fileUploaded" type="file" id="formFile">
      <button class="btn btn-outline-danger" type="button" @click="clearFile">×</button>
    </div>

    <textarea name="slate-input" class="slate-input" rows="3" placeholder="start times" v-model="slateInput" @change="inputChanged"></textarea>
    
    
    <div class="upload-data-row">
      <input type="text" placeholder="slate id" v-model="slateId">
      <button class="btn upload-data-button" type="button" @click="uploadSlate"
      :disabled="!slateId || !date"
      >Upload</button>


    </div>
    <br>
    
    <br>
    <TableComponent 
      :columns="parsedContent?.columns ?? []"
      :mappedVals="parsedContent?.mappedVals ?? []"
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

.slate-input {
  width: 100%;
  resize: vertical;
}
</style>
