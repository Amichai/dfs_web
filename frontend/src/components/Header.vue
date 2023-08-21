<script setup>
</script>

<template>
  <nav class="nav-bar">
    <a href="/slates" class="nav-item">Slates</a>
    <a href="/players" class="nav-item">Players</a>
    <a href="/optimizer" class="nav-item">Optimizer</a>
    <a href="/backtester" class="nav-item">Backtester</a>
  </nav>
  <hr>
</template>

<style scoped>
.nav-bar {
    background-color: var(--clr-background);
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