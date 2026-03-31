<template>
  <div class="fullscreen flex flex-center q-pa-md app-error">
    <div class="text-center" style="max-width: 360px">
      <div class="text-weight-bold text-grey-9" style="font-size: 4.5rem; letter-spacing: -0.06em; line-height: 1">
        404
      </div>
      <div class="text-h6 text-weight-medium text-grey-8 q-mt-md">
        Página não encontrada
      </div>
      <p class="text-body2 text-grey-7 q-mt-sm q-mb-lg">
        O endereço pode estar incorreto ou a página foi movida.
      </p>
      <q-btn
        unelevated
        no-caps
        color="primary"
        padding="sm md"
        to="/"
        label="Ir para o início"
      />
    </div>
  </div>
</template>

<script setup>
//
</script>

<style scoped>
.app-error {
  background: var(--app-bg, #f9f8f6);
}
</style>
