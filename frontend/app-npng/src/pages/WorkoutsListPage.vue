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
            :to="{ name: 'workout-new' }"
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

      <q-banner v-if="auth.isProfessional && !prof.selectedStudentId" class="app-banner q-mb-md" dense rounded>
        Seleciona um aluno no topo para listar os treinos desse aluno.
      </q-banner>

      <div v-if="filteredSessions.length">
        <div
          v-for="s in filteredSessions"
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
            <div class="app-workout-card__thumb">
              <q-icon name="fitness_center" size="36px" color="grey-7" />
            </div>
          </div>
        </div>
      </div>
      <div v-else-if="!loading" class="text-grey-7 q-mt-md text-center">
        {{ search ? 'Nenhum resultado.' : 'Sem treinos registados.' }}
      </div>
      <q-inner-loading :showing="loading" />
    </div>
  </q-page>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { api } from 'src/api/client'
import { useAuthStore } from 'src/stores/auth'
import { useProfessionalStore } from 'src/stores/professional'

const router = useRouter()
const sessions = ref([])
const loading = ref(false)
const search = ref('')
const auth = useAuthStore()
const prof = useProfessionalStore()

const filteredSessions = computed(() => {
  const q = search.value.trim().toLowerCase()
  if (!q) return sessions.value
  return sessions.value.filter((s) => {
    const title = (s.title || 'Treino').toLowerCase()
    const date = formatDateShort(s.performed_at).toLowerCase()
    return title.includes(q) || date.includes(q)
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
  await api.post(`/workouts/sessions/${session.id}/duplicate`, {
    performed_at: new Date().toISOString(),
  })
  await load()
}

function progressPct (s) {
  const n = s.sets?.length || 0
  return Math.min(100, n * 14 + 18)
}

watch(() => prof.selectedStudentId, load)
onMounted(load)
</script>
