<template>
  <q-card flat class="auth-card q-pa-lg" style="width: 100%; max-width: 400px">
    <q-card-section>
      <div class="auth-title text-center q-mb-lg">Entrar</div>
      <q-form @submit="onSubmit" class="q-gutter-md">
        <q-input
          v-model="email"
          type="email"
          label="Email"
          outlined
          dense
          :rules="[val => !!val || 'Obrigatório']"
        />
        <q-input
          v-model="password"
          type="password"
          label="Password"
          outlined
          dense
          :rules="[val => !!val || 'Obrigatório']"
        />
        <q-banner v-if="error" class="bg-negative text-white q-mb-sm rounded-borders" dense rounded>{{ error }}</q-banner>
        <q-btn
          type="submit"
          unelevated
          no-caps
          color="primary"
          class="full-width"
          padding="sm md"
          label="Entrar"
          :loading="loading"
        />
        <q-btn
          flat
          no-caps
          color="grey-8"
          class="full-width"
          label="Criar conta"
          :to="{ name: 'register' }"
        />
      </q-form>
    </q-card-section>
  </q-card>
</template>

<script setup>
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from 'src/stores/auth'

const email = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')
const auth = useAuthStore()
const router = useRouter()
const route = useRoute()

async function onSubmit () {
  error.value = ''
  loading.value = true
  try {
    await auth.login(email.value, password.value)
    const redirect = route.query.redirect
    router.replace(typeof redirect === 'string' ? redirect : { name: 'dashboard' })
  } catch (e) {
    error.value = e.response?.data?.detail || 'Erro ao iniciar sessão'
  } finally {
    loading.value = false
  }
}
</script>
