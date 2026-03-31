<template>
  <q-page padding>
    <div class="app-page-inner">
      <div class="page-title">Alunos</div>
      <q-card flat class="app-card q-pa-md q-mb-md">
        <div class="text-subtitle2 text-weight-medium q-mb-md">Associar aluno (email já registado)</div>
        <div class="row q-col-gutter-sm items-end">
          <div class="col">
            <q-input v-model="email" type="email" label="Email do aluno" outlined dense />
          </div>
          <q-btn unelevated no-caps color="primary" padding="sm md" label="Adicionar" :loading="adding" @click="addStudent" />
        </div>
      </q-card>
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
              <q-btn flat no-caps dense color="primary" label="Usar" @click="selectStudent(s.user.id)" />
              <q-btn flat dense round icon="delete" color="grey-7" @click="removeStudent(s.user.id)" />
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

const students = ref([])
const email = ref('')
const adding = ref(false)
const prof = useProfessionalStore()

async function load () {
  const { data } = await api.get('/professional/students')
  students.value = data
}

function selectStudent (id) {
  prof.setSelectedStudent(id)
  Notify.create({ message: 'Aluno selecionado no topo da página', position: 'top' })
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

function removeStudent (id) {
  Dialog.create({
    title: 'Remover aluno',
    message: 'Remover associação?',
    cancel: true,
  }).onOk(async () => {
    await api.delete(`/professional/students/${id}`)
    if (prof.selectedStudentId === id) prof.setSelectedStudent(null)
    await load()
  })
}

onMounted(load)
</script>
