<script setup>
import { ref, onMounted, computed, nextTick, watch, onUpdated } from 'vue'
import Column from 'primevue/column';
import DataTable from 'primevue/datatable';

const props = defineProps({
  columns: {
    type: Array,
    required: true
  },
  mappedVals: {
    type: Array,
    required: true
  },
  columnMapper: {
    type: Object,
    default: {}
  }
})

const emits = defineEmits([])

const rows = ref([])

onUpdated(() => {
  const columnCount = props.columns.length;
  const percentage = 100 / columnCount;
  const tableRows = document.querySelectorAll('.table-row');


  tableRows.forEach((tableRow) => {
    tableRow.style.gridTemplateColumns = `repeat(${props.columns.length}, ${percentage}%)`;
  });
  const headers = document.querySelectorAll('.column-headers');
  headers.forEach((tableRow) => {
    tableRow.style.gridTemplateColumns = `repeat(${props.columns.length}, ${percentage}%)`;
  });
})

watch(() => props.mappedVals, (newVal, oldVal) => {
  rows.value = props.mappedVals.map((item, index) => {
    const toReturn = Object.values(item).reduce((acc, value, index) => {
      const column = props.columns[index]
      acc[column] = column in props.columnMapper
                  ? props.columnMapper[column](value)
                  : value

      return acc
    }, {})

    return toReturn
  })
}, { deep: true })


const sortColumn = ref('')
const sortDirection = ref('')

const clickedColumn = (evt) => {
  const columnKey = evt.target.innerText

  sortColumn.value = columnKey
  sortDirection.value = sortDirection.value === 'desc' ? 'asc' : 'desc'

  rows.value = rows.value.sort((a, b) => {
    if(typeof a[columnKey] === 'number') {
      if(sortDirection.value === 'asc')
        return b[columnKey] - a[columnKey]
      else
        return a[columnKey] - b[columnKey]
    } else {
      if(sortDirection.value === 'asc')
        return b[columnKey].localeCompare(a[columnKey])
      else
        return a[columnKey].localeCompare(b[columnKey])
    }
  })

}

</script>

<template>
  <div>
    <div class="column-headers">
      <div v-for="(col, index) in columns" :key="index">
        <div @click="clickedColumn">{{ col }}</div>
      </div>
    </div>
    <div v-for="(row, index) in rows" :key="index" class="table-row">
      <div v-for="(col, index) in columns" :key="index">
        <div>{{ row[col] }}</div>
      </div>
    </div>
  </div>
  <!-- <DataTable :value="rows" class="p-datatable-sm" tableStyle="min-width: 50rem" showGridlines stripedRows paginator :rows="50"
  removableSort
  paginatorTemplate="RowsPerPageDropdown FirstPageLink PrevPageLink CurrentPageReport NextPageLink LastPageLink"
  >
    <Column v-for="(column, idx) in columns" :key="idx" :field="column" :header="column" sortable="">
    </Column>
  </DataTable> -->
</template>

<style scoped>
tr {
  font-size: 0.8em;
}

.column-headers {
  display: grid;
  grid-template-columns: repeat(10, 1fr);
  gap: 0.3rem;

  border-bottom: 1px solid white;
  font-weight: bold;
}

.table-row {
  display: grid;
  grid-template-columns: repeat(10, 1fr);
  gap: 0.3rem;
}

</style>