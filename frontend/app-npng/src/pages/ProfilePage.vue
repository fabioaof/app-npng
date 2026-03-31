<template>
  <q-page padding>
    <div class="app-page-inner" style="max-width: 520px">
      <div class="page-title">Perfil</div>
      <q-form @submit="onSave" class="q-gutter-md">
        <div class="row justify-center q-mb-md" v-if="profile !== null">
          <div class="profile-photo-uploader relative-position">
            <q-avatar size="100px" round class="shadow-1">
              <img
                v-if="avatarSrc"
                :src="avatarSrc"
                alt="Foto"
                style="object-fit: cover; width: 100%; height: 100%"
              />
              <q-icon v-else name="person" size="48px" />
            </q-avatar>
            <q-file
              v-model="photoFile"
              accept="image/*"
              borderless
              dense
              hide-bottom-space
              class="profile-photo-qfile absolute-full q-pa-none"
            />
          </div>
        </div>
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
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
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
const photoPreviewUrl = ref(null)
const saving = ref(false)

const avatarSrc = computed(() => photoPreviewUrl.value || profile.value?.photo_url || null)

watch(photoFile, (val) => {
  if (photoPreviewUrl.value) {
    URL.revokeObjectURL(photoPreviewUrl.value)
    photoPreviewUrl.value = null
  }
  const raw = val
  const file = Array.isArray(raw) ? raw[0] : raw
  if (file instanceof File) {
    photoPreviewUrl.value = URL.createObjectURL(file)
  }
})

onUnmounted(() => {
  if (photoPreviewUrl.value) {
    URL.revokeObjectURL(photoPreviewUrl.value)
  }
})

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

<style scoped>
.profile-photo-uploader {
  width: 100px;
  height: 100px;
}

.profile-photo-qfile {
  opacity: 0;
  z-index: 1;
}

.profile-photo-qfile :deep(.q-field__control) {
  min-height: 100px;
  height: 100px;
  padding: 0;
}

.profile-photo-qfile :deep(.q-field__native) {
  min-height: 100px;
}
</style>
