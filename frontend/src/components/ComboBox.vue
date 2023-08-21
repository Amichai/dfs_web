<template>
  <div class="container">
    <input id="combobox" v-model="selectedElement" list="elements" :placeholder="placeholder"
      @change="$emit('update:modelValue', selectedElement)" 
      
      />
    <datalist id="elements">
      <option v-for="element in array" :key="element" :value="element" />
    </datalist>
  </div>
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
  }
})

defineEmits(['update:modelValue'])

const selectedElement = ref(props.modelValue);

watch(() => props.modelValue, (val) => {
  selectedElement.value = val;
})
</script>
  
<style scoped>
.container {
  font-family: Arial, sans-serif;
}

input {
  color: black;
  font-size: var(--fs-0);
}
</style>
  