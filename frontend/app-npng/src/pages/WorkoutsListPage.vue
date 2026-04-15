<template>
  <q-page padding>
    <div class="app-page-inner">
      <div class="row items-start justify-between q-mb-md q-col-gutter-sm">
        <div class="col">
          <div class="page-title q-mb-none">Treinos</div>
        </div>
        <div class="col-auto">
          <q-btn
            unelevated
            no-caps
            color="primary"
            label="Novo"
            padding="sm md"
            rounded
            @click="onClickNew"
          />
        </div>
      </div>

      <q-input
        v-model="search"
        outlined
        dense
        rounded
        clearable
        placeholder="Pesquisar treinos…"
        class="app-search-pill q-mb-lg"
        bg-color="white"
      >
        <template #prepend>
          <q-icon name="search" color="grey-6" />
        </template>
      </q-input>

      <q-banner v-if="auth.isProfessional && !prof.selectedStudentId" class="app-banner--warning q-mb-md" dense rounded>
        {{ t('Seleciona um aluno para listar os treinos desse aluno.') }}
      </q-banner>

      <div v-if="filteredSessions.length" class="workouts-list">
        <div v-for="group in groupedSessions" :key="group.key" class="workouts-list__group">
          <div class="workouts-list__group-head row items-center no-wrap">
            <div class="text-caption text-weight-bold text-grey-8">
              {{ group.label }}
            </div>
            <q-space />
            <div class="text-caption text-grey-7">
              {{ group.items.length }} {{ group.items.length === 1 ? 'treino' : 'treinos' }}
            </div>
          </div>
          <q-separator class="q-mt-sm q-mb-md" />

          <div
            v-for="s in group.items"
            :key="s.id"
            class="app-workout-card row no-wrap items-center q-gutter-md cursor-pointer"
            @click="goDetail(s.id)"
          >
            <div class="col">
              <div class="text-subtitle1 text-weight-bold q-mb-xs" style="letter-spacing: -0.02em">
                {{ s.title || 'Treino' }}
              </div>
              <div class="text-body2 text-grey-7">
                {{ formatDateShort(s.performed_at) }} · {{ s.sets?.length || 0 }} sets
              </div>
              <div class="app-mini-progress">
                <div class="app-mini-progress__fill" :style="{ width: progressPct(s) + '%' }" />
              </div>
            </div>
            <div class="col-auto row items-center no-wrap q-gutter-xs">
              <q-btn
                flat
                dense
                round
                icon="content_copy"
                color="grey-7"
                aria-label="Duplicar"
                @click.stop="duplicate(s)"
              />
              <q-btn
                flat
                dense
                round
                icon="delete"
                color="negative"
                aria-label="Eliminar"
                @click.stop="onDelete(s)"
              />
            </div>
          </div>
        </div>
      </div>
      <div v-else-if="!loading" class="text-grey-7 q-mt-md text-center">
        {{ search ? 'Nenhum resultado.' : 'Sem treinos registados.' }}
      </div>
      <q-inner-loading :showing="loading" />

      <q-dialog v-model="studentDialogOpen" position="bottom">
        <q-card style="width: 100%; max-width: 100%; border-radius: 20px 20px 0 0">
          <q-card-section class="q-pb-sm">
            <div class="text-h6 text-weight-bold" style="letter-spacing: -0.02em">
              Selecionar aluno
            </div>
            <p class="text-body2 text-grey-7 q-mb-none q-mt-xs">
              Escolhe o aluno para iniciar o treino.
            </p>
          </q-card-section>

          <q-card-section class="q-pt-sm">
            <q-select
              v-model="dialogStudentId"
              :options="studentOptions"
              emit-value
              map-options
              label="Aluno"
              outlined
              dense
              rounded
              bg-color="white"
              :loading="studentsLoading"
              :disable="studentsLoading || !studentOptions.length"
              menu-anchor="bottom middle"
              menu-self="top middle"
            />
          </q-card-section>

          <q-card-actions align="right" class="q-px-md q-pb-md">
            <q-btn v-close-popup flat no-caps rounded color="grey-8" label="Cancelar" />
            <q-btn
              unelevated
              no-caps
              rounded
              color="primary"
              label="Continuar"
              :disable="dialogStudentId == null"
              @click="confirmStudentAndGoNew"
            />
          </q-card-actions>
        </q-card>
      </q-dialog>
    </div>
  </q-page>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Dialog, Notify } from 'quasar'
import { api } from 'src/api/client'
import { useAuthStore } from 'src/stores/auth'
import { useProfessionalStore } from 'src/stores/professional'
import { useI18n } from 'vue-i18n'

const router = useRouter()
const { t } = useI18n()
const sessions = ref([])
const loading = ref(false)
const search = ref('')
const auth = useAuthStore()
const prof = useProfessionalStore()

const studentDialogOpen = ref(false)
const studentsLoading = ref(false)
const students = ref([])
const dialogStudentId = ref(null)

function studentSortKey (s) {
  const name = s?.profile?.full_name?.trim()
  const email = s?.user?.email?.trim()
  return (name || email || '').toLowerCase()
}

const sortedStudents = computed(() =>
  [...students.value].sort((a, b) =>
    studentSortKey(a).localeCompare(studentSortKey(b), 'pt-PT', { sensitivity: 'base' }),
  ),
)

const studentOptions = computed(() =>
  sortedStudents.value.map((s) => ({
    label: s.user?.email + (s.profile?.full_name ? ` (${s.profile.full_name})` : ''),
    value: s.user?.id,
  })),
)

const filteredSessions = computed(() => {
  const q = search.value.trim().toLowerCase()
  if (!q) return sessions.value
  return sessions.value.filter((s) => {
    const title = (s.title || 'Treino').toLowerCase()
    const date = formatDateShort(s.performed_at).toLowerCase()
    return title.includes(q) || date.includes(q)
  })
})

function monthKey (iso) {
  if (!iso) return 'unknown'
  const d = new Date(iso)
  if (Number.isNaN(d.getTime())) return 'unknown'
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`
}

function monthLabel (iso) {
  if (!iso) return 'Sem data'
  const d = new Date(iso)
  if (Number.isNaN(d.getTime())) return 'Sem data'
  const month = d.toLocaleString('pt-PT', { month: 'long' })
  const year = d.getFullYear()
  return `${month.charAt(0).toUpperCase()}${month.slice(1)} ${year}`
}

const groupedSessions = computed(() => {
  const list = filteredSessions.value || []
  const map = new Map()
  for (const s of list) {
    const k = monthKey(s.performed_at)
    if (!map.has(k)) {
      map.set(k, { key: k, label: monthLabel(s.performed_at), items: [] })
    }
    map.get(k).items.push(s)
  }

  // Ordenação: mais recente primeiro; "unknown" no fim
  const keys = [...map.keys()].sort((a, b) => {
    if (a === 'unknown') return 1
    if (b === 'unknown') return -1
    return a < b ? 1 : -1
  })

  return keys.map((k) => {
    const g = map.get(k)
    g.items.sort((x, y) => new Date(y.performed_at).getTime() - new Date(x.performed_at).getTime())
    return g
  })
})

function scopeParams () {
  if (auth.isProfessional && prof.selectedStudentId) {
    return { user_id: prof.selectedStudentId }
  }
  return {}
}

function formatDateShort (iso) {
  if (!iso) return ''
  const d = new Date(iso)
  return d.toLocaleString('pt-PT', { day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit' })
}

function goDetail (id) {
  router.push({ name: 'workout-detail', params: { id } })
}

async function loadStudents () {
  if (!auth.isProfessional) return
  studentsLoading.value = true
  try {
    const { data } = await api.get('/professional/students')
    students.value = data || []
  } catch {
    students.value = []
  } finally {
    studentsLoading.value = false
  }
}

async function onClickNew () {
  if (auth.isProfessional && !prof.selectedStudentId) {
    if (!students.value.length) await loadStudents()
    dialogStudentId.value = sortedStudents.value[0]?.user?.id ?? null
    studentDialogOpen.value = true
    return
  }
  router.push({ name: 'workout-new' })
}

function confirmStudentAndGoNew () {
  if (dialogStudentId.value == null) {
    Notify.create({
      type: 'warning',
      message: t('Escolhe um aluno.'),
      position: 'top',
    })
    return
  }
  prof.setSelectedStudent(dialogStudentId.value)
  studentDialogOpen.value = false
  router.push({ name: 'workout-new' })
}

async function load () {
  loading.value = true
  try {
    const { data } = await api.get('/workouts/sessions', { params: scopeParams() })
    sessions.value = data
  } finally {
    loading.value = false
  }
}

async function duplicate (session) {
  const isoLocal = new Date().toISOString().slice(0, 16)
  router.push({ name: 'workout-new', query: { duplicate_of: String(session.id), performed_at: isoLocal } })
}

function onDelete (session) {
  Dialog.create({
    title: 'Apagar treino',
    message: 'Tem a certeza?',
    cancel: {
      label: t('Cancelar'),
      color: 'negative',
    }
  }).onOk(async () => {
    try {
      await api.delete(`/workouts/sessions/${session.id}`)
      sessions.value = sessions.value.filter((s) => s.id !== session.id)
      Notify.create({
        type: 'positive',
        message: t('Treino eliminado.'),
        position: 'top',
      })
    } catch {
      Notify.create({
        type: 'negative',
        message: t('Não foi possível eliminar o treino.'),
        position: 'top',
      })
    }
  })
}

function progressPct (s) {
  const n = s.sets?.length || 0
  return Math.min(100, n * 14 + 18)
}

watch(() => prof.selectedStudentId, load)
onMounted(load)
</script>

<style scoped>
.workouts-list {
  display: flex;
  flex-direction: column;
  /* gap: 22px; */
}

.workouts-list__group-head {
  padding: 0 6px;
}

@media (max-width: 599px) {
  .workouts-list {
    padding-left: 18px;
    padding-right: 12px;
  }
}
</style>
