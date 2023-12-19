<template>
  <select v-model="selectedElement" class="container">
    <option v-for="element in array" :key="element" :value="element">
      {{ element }}
    </option>
  </select>
</template>
  
<script setup>
import { ref, watch } from 'vue';

const props = defineProps({
  array: {
    type: Array,
    required: true
  },
  placeholder: {
    type: String,
    required: true
  },
  modelValue: {
    type: String,
    default: ''
  },
})

const emits = defineEmits(['update:modelValue'])

const selectedElement = ref(props.modelValue);

watch(() => props.modelValue, (val) => {
  selectedElement.value = val;
})

watch(() => selectedElement.value, (val) => {
  emits('update:modelValue', val)
})
</script>
  
<style scoped>
.container {
  font-family: Arial, sans-serif;
  padding: 0.5rem 1rem;
}

input {
  color: black;
  font-size: var(--fs-0);
}
</style>
  