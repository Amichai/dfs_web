<script setup>
import { ref, onMounted, computed, nextTick, watch } from 'vue'
import { runOptimizer } from '../apiHelper';
  
const props = defineProps({
  msg: {
    type: String,
    required: false
  }
})

const emits = defineEmits([])

const optimize = async () => {
  await runOptimizer()
}


/// show a table with every player's projcetions (source of the projection, last updated, etc.)
/// Text input for overriding projections
///Settings to modify projection source

/// Optimize button
/// Upload a slate file
// Modeled after existing optimizer site
</script>

<template>
  <main>
    <h1>Optimizer</h1>

    <button class="button" @click="optimize">Optimize</button>
  </main>
</template>

<style scoped>
.button {
  margin: 1rem 0;
  padding: 0.5rem 1rem;
}
</style>