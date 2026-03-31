<template>
  <q-page padding>
    <div class="app-page-inner" style="max-width: 520px">
      <div class="page-title">Perfil</div>
      <q-form @submit="onSave" class="q-gutter-md">
        <div class="row justify-center q-mb-md" v-if="profile?.photo_url">
          <q-avatar size="100px" round class="shadow-1">
            <img style="object-fit: fill" :src="profile.photo_url" alt="Foto">
          </q-avatar>
        </div>
        <q-file v-model="photoFile" label="Alterar foto" outlined dense accept="image/*">
          <template #prepend>
            <q-icon name="attach_file" />
          </template>
        </q-file>
        <q-input v-model="fullName" label="Nome" outlined dense />
        <q-input v-model="birthDate" type="date" label="Data de nascimento" outlined dense stack-label />
        <q-input v-model.number="weightKg" type="number" label="Peso (kg)" outlined dense step="0.1" min="0" />
        <q-input v-model.number="heightCm" type="number" label="Altura (cm)" outlined dense step="0.1" min="0" />
        <div class="row justify-end">
          <q-btn type="submit" unelevated no-caps color="primary" padding="sm md" label="Guardar" :loading="saving" />
        </div>
        <q-separator class="q-my-lg" />
        <q-btn
          flat
          no-caps
          color="negative"
          label="Terminar sessão"
          icon="logout"
          align="left"
          class="full-width"
          @click="onLogout"
        />
      </q-form>
    </div>
  </q-page>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Notify } from 'quasar'
import { useAuthStore } from 'src/stores/auth'
import { api } from 'src/api/client'

const router = useRouter()
const auth = useAuthStore()

const profile = ref(null)
const fullName = ref('')
const birthDate = ref('')
const weightKg = ref(null)
const heightCm = ref(null)
const photoFile = ref(null)
const saving = ref(false)

async function load () {
  const { data } = await api.get('/profiles/me')
  profile.value = data
  fullName.value = data.full_name || ''
  birthDate.value = data.birth_date || ''
  weightKg.value = data.weight_kg
  heightCm.value = data.height_cm
}

async function onSave () {
  saving.value = true
  try {
    const raw = photoFile.value
    const file = Array.isArray(raw) ? raw[0] : raw
    if (file instanceof File) {
      const form = new FormData()
      form.append('file', file)
      await api.post('/profiles/me/photo', form)
      photoFile.value = null
    }
    await api.patch('/profiles/me', {
      full_name: fullName.value || null,
      birth_date: birthDate.value || null,
      weight_kg: weightKg.value,
      height_cm: heightCm.value,
    })
    Notify.create({ type: 'positive', message: 'Perfil atualizado' })
    await load()
  } finally {
    saving.value = false
  }
}

function onLogout () {
  auth.logout()
  router.push({ name: 'login' })
}

onMounted(load)
</script>
