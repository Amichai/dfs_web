<template>
  <div class="dialog" v-if="isOpen">
    <div class="dialog-content">
      <slot></slot>
    </div>
  </div>
</template>

<script>
export default {
  props: ['isOpen'],
  methods: {
    close() {
      this.$emit('close')
    }
  }
}
</script>

<style scoped>
.dialog {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  background: rgba(0, 0, 0, 0.75);
  text-align: center;
  z-index: 9999;
}
</style>
