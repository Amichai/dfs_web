<script setup>
  import axios from 'axios';
  import { writeData, queryData, searchData } from '../apiHelper';
  import { ref, onMounted, computed, nextTick, watch } from 'vue'

  const fetchData = async () => {
    searchData('test1', 'test', 'test3' ).then((res) => {
      console.log(res);
    })
    
    // searchData('test1', 'time', '2023-08-17T02' ).then((res) => {
    //   console.log(res);
    // })
  }

  onMounted(async () => {
    await fetchData();
  })
</script>

<template>
  <div>TESTING</div>
</template>

<style>
</style>