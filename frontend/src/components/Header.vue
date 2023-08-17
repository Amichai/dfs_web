<script setup>
</script>

<template>
  <nav class="nav-bar">
    <a href="/slates" class="nav-item">Slates</a>
    <a href="/players" class="nav-item">Players</a>
    <a href="/optimizer" class="nav-item">Optimizer</a>
    <a href="/backtester" class="nav-item">Backtester</a>
  </nav>
</template>

<style>
body {
    margin: 0;
    padding: 0;
    font-family: Arial, sans-serif;
}

.nav-bar {
    background-color: #333;
    overflow: hidden;
}

.nav-item {
    float: left;
    display: block;
    color: #f2f2f2;
    text-align: center;
    padding: 14px 16px;
    text-decoration: none;
}

.nav-item:hover {
    background-color: #ddd;
    color: black;
}
</style>