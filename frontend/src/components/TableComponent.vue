<script setup>
import { ref, onMounted, computed, nextTick, watch } from 'vue'
import Column from 'primevue/column';
import DataTable from 'primevue/datatable';

const props = defineProps({
  content: {
    type: Object,
    required: true
  }
})

const emits = defineEmits([])

const rows = ref([])

watch(() => props.content, (newVal, oldVal) => {
  rows.value = props.content.mappedVals.map((item, index) => {
    const toReturn = Object.values(item).reduce((acc, value, index) => {
      acc[props.content.columns[index]] = value
      return acc
    }, {})

    return toReturn
  })
}, { deep: true })

</script>

<template>
  <DataTable :value="rows" class="p-datatable-sm" tableStyle="min-width: 50rem" showGridlines stripedRows paginator :rows="50"
  removableSort
  paginatorTemplate="RowsPerPageDropdown FirstPageLink PrevPageLink CurrentPageReport NextPageLink LastPageLink"
  >
    <Column v-for="(column, idx) in content.columns" :key="idx" :field="column" :header="column" sortable="">
    </Column>
  </DataTable>
</template>

<style scoped>
tr {
  font-size: 0.8em;
}
</style>