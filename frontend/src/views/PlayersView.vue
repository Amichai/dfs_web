<script setup>
import { ref, onMounted, computed, nextTick, watch } from 'vue'
  
const props = defineProps({
  msg: {
    type: String,
    required: true
  }
})

const emits = defineEmits([])
</script>

<template>
  <div></div>
</template>

<style>
</style>