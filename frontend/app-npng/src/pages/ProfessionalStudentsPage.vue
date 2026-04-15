<template>
  <q-page padding>
    <div class="app-page-inner">
      <div class="page-title">Alunos</div>
      <q-card flat class="app-card q-pa-md q-mb-md">
        <div class="text-subtitle2 text-weight-medium q-mb-md">{{ t('Associar aluno') }}</div>
        <div class="row q-col-gutter-sm">
          <div class="col-12">
            <q-input v-model="email" type="email" :label="t('Email do aluno')" outlined dense />
          </div>
          <div class="col-12">
            <div class="row q-gutter-sm justify-end">
              <q-btn unelevated no-caps color="primary" padding="sm md" :label="t('Adicionar')" :loading="adding" @click="addStudent" />
              <q-btn outline no-caps color="primary" padding="sm md" :label="t('Nova conta')" @click="openCreateDialog" />
            </div>
          </div>
        </div>
      </q-card>

      <q-dialog v-model="createDialogOpen" persistent>
        <q-card style="width: 720px; max-width: 92vw;">
          <q-card-section class="row items-center q-pb-none">
            <div class="text-subtitle1 text-weight-medium">{{ t('Nova conta de aluno') }}</div>
            <q-space />
            <q-btn icon="close" flat round dense :disable="creating" v-close-popup />
          </q-card-section>

          <q-card-section>
            <div class="row q-col-gutter-sm">
              <div class="col-12 col-md-6">
                <q-input v-model="newEmail" type="email" label="Email" outlined dense />
              </div>
              <div class="col-12 col-md-6">
                <q-input v-model="newPassword" :type="showPassword ? 'text' : 'password'" :label="t('Password temporária')" outlined dense>
                  <template #append>
                    <q-btn flat round dense :icon="showPassword ? 'visibility_off' : 'visibility'" @click="showPassword = !showPassword" />
                  </template>
                </q-input>
              </div>
              <div class="col-12">
                <q-input v-model="newFullName" :label="t('Nome (opcional)')" outlined dense />
              </div>
              <div class="col-12 col-md-4">
                <q-input v-model="newBirthDate" type="date" :label="t('Data nascimento (opcional)')" outlined dense />
              </div>
              <div class="col-6 col-md-4">
                <q-input v-model.number="newWeightKg" type="number" :label="t('Peso kg (opcional)')" outlined dense />
              </div>
              <div class="col-6 col-md-4">
                <q-input v-model.number="newHeightCm" type="number" :label="t('Altura cm (opcional)')" outlined dense />
              </div>
            </div>
          </q-card-section>

          <q-card-actions align="right" class="q-pa-md">
            <q-btn flat no-caps color="grey-7" :label="t('Cancelar')" :disable="creating" v-close-popup />
            <q-btn unelevated no-caps color="primary" :label="t('Criar conta e associar')" :loading="creating" @click="createStudentAccount" />
          </q-card-actions>
        </q-card>
      </q-dialog>

      <q-list separator class="app-list">
        <q-item v-for="s in students" :key="s.user.id">
          <q-item-section avatar>
            <q-avatar color="grey-4" text-color="grey-9" icon="person" size="40px" />
          </q-item-section>
          <q-item-section>
            <q-item-label class="text-weight-medium">{{ s.profile?.full_name || s.user.email }}</q-item-label>
            <q-item-label caption>{{ s.user.email }}</q-item-label>
          </q-item-section>
          <q-item-section side class="items-end">
            <div class="row q-gutter-xs no-wrap">
              <q-btn flat no-caps dense color="primary" :label="t('Usar')" @click="selectStudent(s.user.id)" />
              <q-btn flat dense round icon="delete" color="negative" @click="removeStudent(s.user.id)" />
            </div>
          </q-item-section>
        </q-item>
      </q-list>
    </div>
  </q-page>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Dialog, Notify } from 'quasar'
import { api } from 'src/api/client'
import { useProfessionalStore } from 'src/stores/professional'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
const students = ref([])
const email = ref('')
const adding = ref(false)
const newEmail = ref('')
const newPassword = ref('')
const showPassword = ref(false)
const newFullName = ref('')
const newBirthDate = ref('')
const newWeightKg = ref(null)
const newHeightCm = ref(null)
const creating = ref(false)
const createDialogOpen = ref(false)
const prof = useProfessionalStore()

async function load () {
  const { data } = await api.get('/professional/students')
  students.value = data
}

function resetCreateForm () {
  newEmail.value = ''
  newPassword.value = ''
  showPassword.value = false
  newFullName.value = ''
  newBirthDate.value = ''
  newWeightKg.value = null
  newHeightCm.value = null
}

function openCreateDialog () {
  resetCreateForm()
  createDialogOpen.value = true
}

function selectStudent (id) {
  prof.setSelectedStudent(id)
  const student = students.value.find(s => s.user.id === id)
  const name = student?.profile?.full_name || student?.user?.email || `Aluno ${id}`
  Notify.create({ message: `${name} selecionado`, position: 'top', timeout: 500 })
}

async function addStudent () {
  if (!email.value.trim()) return
  adding.value = true
  try {
    await api.post('/professional/students', { student_email: email.value.trim() })
    email.value = ''
    await load()
    Notify.create({ type: 'positive', message: 'Aluno associado' })
  } catch (e) {
    Notify.create({ type: 'negative', message: e.response?.data?.detail || 'Erro' })
  } finally {
    adding.value = false
  }
}

async function createStudentAccount () {
  if (!newEmail.value.trim() || !newPassword.value) return
  creating.value = true
  try {
    await api.post('/professional/students/create-account', {
      email: newEmail.value.trim(),
      password: newPassword.value,
      full_name: newFullName.value?.trim() || null,
      birth_date: newBirthDate.value || null,
      weight_kg: newWeightKg.value ?? null,
      height_cm: newHeightCm.value ?? null,
    })
    createDialogOpen.value = false
    resetCreateForm()
    await load()
    Notify.create({ type: 'positive', message: 'Conta criada e aluno associado' })
  } catch (e) {
    Notify.create({ type: 'negative', message: e.response?.data?.detail || 'Erro' })
  } finally {
    creating.value = false
  }
}

function removeStudent (id) {
  Dialog.create({
    title: 'Remover aluno',
    message: 'Remover associação?',
    cancel: {
      label: t('Cancelar'),
      color: 'negative',
    }
  }).onOk(async () => {
    await api.delete(`/professional/students/${id}`)
    if (prof.selectedStudentId === id) prof.setSelectedStudent(null)
    await load()
  })
}

onMounted(load)
</script>
