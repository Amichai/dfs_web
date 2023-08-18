<template>
    <div class="container">
        <input id="combobox" v-model="selectedElement" list="elements" :placeholder="placeholder"
            @change="$emit('selected', selectedElement)"
        />
        <datalist id="elements">
            <option v-for="element in array" :key="element" :value="element" />
        </datalist>
    </div>
</template>
  
<script setup>
import { ref } from 'vue';

defineProps({
    array: {
        type: Array,
        required: true
    },
    placeholder: {
        type: String,
        required: true
    }
})

defineEmits(['selected'])

const selectedElement = ref('');
</script>
  
<style>
.container {
    font-family: Arial, sans-serif;
    margin: 20px;
}

input {
    color: black;
    font-size: var(--fs-0);
}
</style>
  