<template>
  <q-page padding>
    <div class="app-page-inner">
      <div class="page-title">{{ t('Exercícios') }}</div>
      <!-- <q-card flat class="app-card q-pa-md q-mb-md">
        <div class="text-subtitle2 text-weight-medium q-mb-md">Novo grupo muscular</div>
        <div class="row q-col-gutter-sm items-end">
          <div class="col q-mr-sm">
            <q-input v-model="newGroupName" label="Nome" outlined dense />
          </div>
          <q-btn unelevated no-caps color="primary" padding="sm md" label="Adicionar" @click="addGroup" :loading="loadingG" />
        </div>
      </q-card> -->
      <q-card flat class="app-card q-pa-md q-mb-md">
        <div class="text-subtitle2 text-weight-medium q-mb-md">{{ t('Novo exercício') }}</div>
        <div class="row q-col-gutter-md">
          <div class="col-12 col-sm-6">
            <q-input v-model="newExName" label="Nome" outlined dense />
          </div>
          <div class="col-12 col-sm-6">
            <q-select
              v-model="newExGroupId"
              :options="groupOptions"
              emit-value
              map-options
              :label="t('Grupo muscular')"
              outlined
              dense
            />
          </div>
        </div>
        <div class="row justify-end">
          <q-btn class="q-mt-md" unelevated no-caps color="primary" padding="sm md" :label="t('Criar exercício')" @click="addExercise" :loading="loadingE" />
        </div>
      </q-card>
      <q-list separator class="app-list">
        <q-item v-for="ex in exercises" :key="ex.id">
          <q-item-section>
            <q-item-label class="text-weight-medium">{{ ex.name }}</q-item-label>
            <q-item-label caption>{{ ex.muscle_group?.name }}</q-item-label>
          </q-item-section>
          <q-item-section side v-if="ex.owner_user_id">
            <q-btn flat dense round icon="delete" color="grey-7" @click="removeEx(ex)" />
          </q-item-section>
        </q-item>
      </q-list>
    </div>
  </q-page>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { Dialog } from 'quasar'
import { api } from 'src/api/client'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

const groups = ref([])
const exercises = ref([])
// const newGroupName = ref('')
const newExName = ref('')
const newExGroupId = ref(null)
// const loadingG = ref(false)
const loadingE = ref(false)

const groupOptions = computed(() =>
  groups.value.map((g) => ({ label: g.name, value: g.id })),
)

async function load () {
  const [g, e] = await Promise.all([
    api.get('/exercises/muscle-groups'),
    api.get('/exercises'),
  ])
  groups.value = g.data
  exercises.value = e.data
  if (!newExGroupId.value && groups.value.length) {
    newExGroupId.value = groups.value[0].id
  }
}

// async function addGroup () {
//   if (!newGroupName.value.trim()) return
//   loadingG.value = true
//   try {
//     await api.post('/exercises/muscle-groups', { name: newGroupName.value.trim() })
//     newGroupName.value = ''
//     await load()
//   } finally {
//     loadingG.value = false
//   }
// }

async function addExercise () {
  if (!newExName.value.trim() || !newExGroupId.value) return
  loadingE.value = true
  try {
    await api.post('/exercises', {
      name: newExName.value.trim(),
      muscle_group_id: newExGroupId.value,
    })
    newExName.value = ''
    await load()
  } finally {
    loadingE.value = false
  }
}

function removeEx (ex) {
  Dialog.create({
    title: t('Apagar exercício'),
    message: t('Apagar exercício', { name: ex.name }),
    cancel: true,
  }).onOk(async () => {
    await api.delete(`/exercises/${ex.id}`)
    await load()
  })
}

onMounted(load)
</script>
