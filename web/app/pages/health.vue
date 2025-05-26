<template>
  <div>
    <h1>Health Check</h1>
    <p>Status: OK</p>
    <p>Timestamp: {{ new Date().toISOString() }}</p>
  </div>
</template>

<script setup>
// 简单的健康检查页面
definePageMeta({
  layout: false
})
</script>
