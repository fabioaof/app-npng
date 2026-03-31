<template>
  <q-card flat class="auth-card q-pa-lg" style="width: 100%; max-width: 420px">
    <q-card-section>
      <div class="auth-title text-center q-mb-lg">Criar conta</div>
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
          label="Password (mín. 8 caracteres)"
          outlined
          dense
          :rules="[val => (val && val.length >= 8) || 'Mínimo 8 caracteres']"
        />
        <q-select
          v-model="role"
          :options="roleOptions"
          emit-value
          map-options
          label="Tipo de conta"
          outlined
          dense
        />
        <q-banner v-if="error" class="bg-negative text-white q-mb-sm rounded-borders" dense rounded>{{ error }}</q-banner>
        <q-btn
          type="submit"
          unelevated
          no-caps
          color="primary"
          class="full-width"
          padding="sm md"
          label="Registar"
          :loading="loading"
        />
        <q-btn
          flat
          no-caps
          color="grey-8"
          class="full-width"
          label="Já tenho conta"
          :to="{ name: 'login' }"
        />
      </q-form>
    </q-card-section>
  </q-card>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from 'src/stores/auth'

const email = ref('')
const password = ref('')
const role = ref('user')
const loading = ref(false)
const error = ref('')
const auth = useAuthStore()
const router = useRouter()

const roleOptions = [
  { label: 'Praticante', value: 'user' },
  { label: 'Profissional', value: 'professional' },
]

async function onSubmit () {
  error.value = ''
  loading.value = true
  try {
    await auth.register({
      email: email.value,
      password: password.value,
      role: role.value,
    })
    router.replace({ name: 'dashboard' })
  } catch (e) {
    error.value = e.response?.data?.detail || 'Erro ao registar'
  } finally {
    loading.value = false
  }
}
</script>
