<template>
  <q-page padding class="app-dash-page">
    <div class="app-page-inner">
      <div class="app-dash-greet-card q-mb-md">
        <div class="row items-center no-wrap">
          <q-avatar size="52px" class="app-dash-greet-card__avatar" color="grey-3" text-color="grey-8">
            <img v-if="profile?.photo_url" style="object-fit: cover; width: 100%; height: 100%" :src="profile.photo_url" alt="">
            <span v-else class="text-weight-bold">{{ initials }}</span>
          </q-avatar>
          <div class="col q-ml-md min-width-0">
            <div class="app-dash-greet-card__line1">
              👋 Olá, <span class="text-weight-medium">{{ greetName }}</span>
            </div>
            <div class="app-dash-greet-card__line2">
              Bem-vindo de volta
            </div>
          </div>
        </div>
      </div>

      <div v-if="auth.isProfessional && !prof.selectedStudentId" class="text-body2 text-grey-7 q-mb-md">
        Seleciona um aluno no topo para ver os dados dele, ou vê os teus dados sem seleção.
      </div>

      <!-- Grelha 2×2: anéis + barra + sparkline -->
      <div class="row q-col-gutter-md app-stat-bento">
        <div class="col-6">
          <div class="app-stat-bento-card">
            <div class="app-stat-bento-card__label">Treinos</div>
            <div class="app-stat-bento-card__value">{{ summary?.total_workouts ?? '—' }}</div>
            <div class="app-stat-bento-card__ring">
              <q-circular-progress
                :value="ringTotal"
                size="52px"
                :thickness="0.14"
                color="primary"
                track-color="grey-3"
              />
            </div>
          </div>
        </div>
        <div class="col-6">
          <div class="app-stat-bento-card">
            <div class="app-stat-bento-card__label">Últimos 30 dias</div>
            <div class="app-stat-bento-card__value">{{ summary?.workouts_last_30_days ?? '—' }}</div>
            <div class="app-stat-bento-card__ring">
              <q-circular-progress
                :value="ring30"
                size="52px"
                :thickness="0.14"
                color="accent"
                track-color="grey-3"
              />
            </div>
          </div>
        </div>
        <div class="col-6">
          <div class="app-stat-bento-card">
            <div class="app-stat-bento-card__label">Volume total</div>
            <div class="app-stat-bento-card__value">{{ summary ? compactVol(summary.total_volume_kg) : '—' }}</div>
            <div class="app-stat-bento-bar">
              <div class="app-stat-bento-bar__fill" :style="{ width: volBarPct + '%' }" />
            </div>
            <div class="text-caption text-grey-6 q-mt-xs">kg×reps acumulado</div>
          </div>
        </div>
        <div class="col-6">
          <div class="app-stat-bento-card">
            <div class="app-stat-bento-card__label">Tendência semanal</div>
            <div class="app-stat-bento-card__value text-body1 text-weight-bold text-grey-8">
              <template v-if="weeklySpark.length">Volume</template>
              <template v-else>—</template>
            </div>
            <div class="app-stat-bento-card__spark">
              <canvas ref="sparkChartEl" />
            </div>
          </div>
        </div>
      </div>

      <!-- Lista recente (estilo mock) -->
      <div class="text-subtitle1 text-weight-bold text-grey-9 q-mb-sm">Treinos recentes</div>
      <q-list v-if="recentSessions.length" class="app-recent-list" separator>
        <q-item
          v-for="s in recentSessions"
          :key="s.id"
          clickable
          :to="{ name: 'workout-detail', params: { id: s.id } }"
        >
          <q-item-section avatar>
            <div class="app-recent-list__icon">
              <q-icon name="fitness_center" size="22px" />
            </div>
          </q-item-section>
          <q-item-section>
            <q-item-label class="text-weight-bold text-grey-9">{{ s.title || 'Treino' }}</q-item-label>
            <q-item-label caption>{{ formatSessionDate(s.performed_at) }} · {{ s.sets?.length || 0 }} sets</q-item-label>
          </q-item-section>
          <q-item-section side>
            <q-icon name="chevron_right" color="grey-5" />
          </q-item-section>
        </q-item>
      </q-list>
      <div v-else class="app-recent-list" style="padding: 20px">
        <div class="text-body2 text-grey-8 text-center">Ainda não há treinos registados.</div>
      </div>

      <div class="text-subtitle1 text-weight-bold text-grey-9 q-mb-sm q-mt-lg">Detalhes</div>
      <div class="text-caption text-grey-7 q-mb-md">Volume por semana e evolução por exercício</div>

      <div class="row q-col-gutter-md q-mb-lg">
        <div class="col-12 col-md-6">
          <q-card flat class="app-card q-pa-md app-chart-card">
            <div class="text-subtitle2 text-weight-bold q-mb-sm">Volume por semana</div>
            <p class="text-caption text-grey-7 q-mb-md">Últimas {{ weeklyChartWeeks }} semanas</p>
            <div class="app-chart-donut-wrap">
              <canvas ref="volChartEl" />
            </div>
            <div v-if="weeklyTotalVol != null" class="text-center text-caption text-grey-7 q-mt-sm">
              Total no período: <strong class="text-grey-9">{{ formatVol(weeklyTotalVol) }}</strong> kg×reps
            </div>
          </q-card>
        </div>
        <div class="col-12 col-md-6">
          <q-card flat class="app-card q-pa-md app-chart-card">
            <div class="text-subtitle2 text-weight-bold q-mb-sm">Peso por sessão</div>
            <div class="row q-col-gutter-sm q-mb-md items-end">
              <div class="col-12">
                <q-select
                  v-model="selectedExerciseId"
                  :options="exerciseOptions"
                  emit-value
                  map-options
                  label="Exercício"
                  outlined
                  dense
                  rounded
                />
              </div>
            </div>
            <div v-if="exercisePoints.length >= 3" class="app-chart-radar-wrap">
              <canvas ref="exChartEl" />
            </div>
            <div v-else-if="exercisePoints.length > 0" class="app-chart-donut-wrap app-chart-donut-wrap--sm">
              <canvas ref="exChartEl" />
            </div>
            <div v-else class="text-body2 text-grey-7 text-center q-py-lg">
              Sem dados para este exercício.
            </div>
          </q-card>
        </div>
      </div>
    </div>
  </q-page>
</template>

<script setup>
import { ref, watch, onMounted, onBeforeUnmount, computed, nextTick } from 'vue'
import { Chart, registerables } from 'chart.js'
import { api } from 'src/api/client'
import { useAuthStore } from 'src/stores/auth'
import { useProfessionalStore } from 'src/stores/professional'

Chart.register(...registerables)

const NEUTRAL_RING = [
  'rgba(156, 175, 170, 0.9)',
  'rgba(214, 169, 157, 0.85)',
  'rgba(214, 218, 200, 0.82)',
  'rgba(251, 243, 213, 0.78)',
  'rgba(138, 158, 149, 0.75)',
  'rgba(201, 160, 144, 0.72)',
  'rgba(176, 190, 184, 0.68)',
  'rgba(228, 220, 208, 0.65)',
]

const auth = useAuthStore()
const prof = useProfessionalStore()
const summary = ref(null)
const weekly = ref([])
const volChartEl = ref(null)
const exChartEl = ref(null)
const sparkChartEl = ref(null)
const exercises = ref([])
const selectedExerciseId = ref(null)
const profile = ref(null)
const exercisePoints = ref([])
const recentSessions = ref([])
let volChart
let exChart
let sparkChart

const exerciseOptions = computed(() =>
  exercises.value.map((e) => ({ label: e.name, value: e.id })),
)

const weeklyChartWeeks = computed(() => Math.min(weekly.value.length, 8))

const weeklyTotalVol = computed(() => {
  if (!weekly.value.length) return null
  return weekly.value.reduce((s, w) => s + (w.volume_kg || 0), 0)
})

const weeklySpark = computed(() => weekly.value.slice(-7).map((w) => w.volume_kg || 0))

/** Anéis decorativos 0–100 (metas suaves para visual) */
const ringTotal = computed(() => {
  const t = summary.value?.total_workouts ?? 0
  return Math.min(100, t * 8)
})

const ring30 = computed(() => {
  const t = summary.value?.workouts_last_30_days ?? 0
  return Math.min(100, t * 14)
})

const volBarPct = computed(() => {
  const v = summary.value?.total_volume_kg ?? 0
  return Math.min(100, Math.round((v / 80000) * 100))
})

const displayName = computed(() => {
  const n = profile.value?.full_name?.trim()
  if (n) return n.split(' ')[0] || n
  const email = auth.user?.email
  if (email) return email.split('@')[0]
  return '…'
})

const greetName = computed(() => {
  const raw = displayName.value
  if (!raw || raw === '…') return raw
  return raw.charAt(0).toUpperCase() + raw.slice(1)
})

const initials = computed(() => {
  const name = profile.value?.full_name
  const email = auth.user?.email
  let initialsToReturn = ''

  if (name && name !== '') {
    initialsToReturn = name.trim().split(/[\s@]+/).map((part) => part[0]).join('')
  } else if (email && email !== '') {
    const parts = email.split(/[@.]+/)
    if (parts.length > 1) {
      initialsToReturn = parts[0][0].toUpperCase() + parts[0][1].toUpperCase()
    }
  } else {
    initialsToReturn = '?'
  }
  return initialsToReturn
})

function compactVol (kg) {
  if (kg == null) return '—'
  const n = Math.round(kg)
  return n >= 1000 ? `${(n / 1000).toFixed(1)}k` : String(n)
}

function formatVol (v) {
  if (v == null) return '—'
  return Math.round(v).toLocaleString('pt-PT')
}

function formatSessionDate (iso) {
  if (!iso) return ''
  return new Date(iso).toLocaleString('pt-PT', {
    day: '2-digit',
    month: 'short',
    hour: '2-digit',
    minute: '2-digit',
  })
}

function scopeParams () {
  if (auth.isProfessional && prof.selectedStudentId) {
    return { user_id: prof.selectedStudentId }
  }
  return {}
}

async function loadProfile () {
  try {
    const { data } = await api.get('/profiles/me')
    profile.value = data
  } catch {
    profile.value = null
  }
}

async function loadSummary () {
  const { data } = await api.get('/dashboard/summary', { params: scopeParams() })
  summary.value = data
}

async function loadWeekly () {
  const { data } = await api.get('/dashboard/volume-weekly', {
    params: { ...scopeParams(), weeks: 12 },
  })
  weekly.value = data
  renderVolChart()
  await nextTick()
  renderSparkChart()
}

async function loadRecentSessions () {
  try {
    const { data } = await api.get('/workouts/sessions', { params: scopeParams() })
    recentSessions.value = (data || []).slice(0, 6)
  } catch {
    recentSessions.value = []
  }
}

async function loadExercises () {
  const { data } = await api.get('/exercises')
  exercises.value = data
  if (!selectedExerciseId.value && data.length) {
    selectedExerciseId.value = data[0].id
  }
}

async function loadExerciseProgress () {
  if (!selectedExerciseId.value) {
    exercisePoints.value = []
    destroyExChart()
    return
  }
  const { data } = await api.get('/dashboard/exercise-progress', {
    params: { ...scopeParams(), exercise_id: selectedExerciseId.value },
  })
  exercisePoints.value = data
  await nextTick()
  renderExChart(data)
}

function destroyExChart () {
  if (exChart) {
    exChart.destroy()
    exChart = null
  }
}

function destroySparkChart () {
  if (sparkChart) {
    sparkChart.destroy()
    sparkChart = null
  }
}

function shortWeekLabel (iso) {
  if (!iso) return ''
  const d = new Date(iso)
  return `${d.getDate()}/${d.getMonth() + 1}`
}

function renderVolChart () {
  if (!volChartEl.value) return
  const slice = weekly.value.slice(-8)
  const labels = slice.map((w) => shortWeekLabel(w.week_start))
  const values = slice.map((w) => w.volume_kg || 0)
  const colors = labels.map((_, i) => NEUTRAL_RING[i % NEUTRAL_RING.length])
  if (volChart) volChart.destroy()
  volChart = new Chart(volChartEl.value, {
    type: 'doughnut',
    data: {
      labels,
      datasets: [{
        data: values,
        backgroundColor: colors,
        borderWidth: 2,
        borderColor: '#ffffff',
        hoverOffset: 6,
      }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: true,
      aspectRatio: 1.05,
      cutout: '68%',
      plugins: {
        legend: {
          position: 'bottom',
          labels: {
            boxWidth: 10,
            padding: 10,
            font: { size: 10, family: "'Plus Jakarta Sans', sans-serif" },
            color: '#5a5348',
          },
        },
        tooltip: {
          callbacks: {
            label: (ctx) => {
              const v = ctx.raw ?? 0
              return ` ${Number(v).toLocaleString('pt-PT')} kg×reps`
            },
          },
        },
      },
    },
  })
}

function renderSparkChart () {
  destroySparkChart()
  if (!sparkChartEl.value) return
  const pts = weekly.value.slice(-7)
  const values = pts.map((w) => w.volume_kg || 0)
  if (!values.length) return
  sparkChart = new Chart(sparkChartEl.value, {
    type: 'line',
    data: {
      labels: values.map((_, i) => i),
      datasets: [{
        data: values,
        borderColor: '#a8b5b0',
        backgroundColor: 'rgba(168, 181, 176, 0.22)',
        borderWidth: 2,
        tension: 0.4,
        fill: true,
        pointRadius: 0,
      }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false }, tooltip: { enabled: true } },
      scales: {
        x: { display: false },
        y: { display: false },
      },
    },
  })
}

function renderExChart (points) {
  if (!exChartEl.value) return
  destroyExChart()
  const vals = points.map((p) => p.max_weight_kg).filter((v) => v != null)
  if (!vals.length) return

  if (vals.length >= 3) {
    const labels = points.map((_, i) => `S${i + 1}`)
    exChart = new Chart(exChartEl.value, {
      type: 'radar',
      data: {
        labels,
        datasets: [{
          label: 'Peso máx. (kg)',
          data: vals,
          borderColor: '#9cafaa',
          backgroundColor: 'rgba(156, 175, 170, 0.22)',
          borderWidth: 2,
          pointBackgroundColor: '#9cafaa',
          pointBorderColor: '#ffffff',
          pointHoverBackgroundColor: '#7d9489',
        }],
      },
      options: {
        responsive: true,
        maintainAspectRatio: true,
        aspectRatio: 1.1,
        scales: {
          r: {
            beginAtZero: true,
            angleLines: { color: 'rgba(156, 175, 170, 0.22)' },
            grid: { color: 'rgba(156, 175, 170, 0.28)' },
            pointLabels: {
              font: { size: 10, family: "'Plus Jakarta Sans', sans-serif" },
              color: '#7d7568',
            },
            ticks: {
              backdropColor: 'transparent',
              color: '#7d7568',
            },
          },
        },
        plugins: {
          legend: { display: false },
        },
      },
    })
    return
  }

  const colors = vals.map((_, i) => NEUTRAL_RING[i % NEUTRAL_RING.length])
  exChart = new Chart(exChartEl.value, {
    type: 'doughnut',
    data: {
      labels: points.map((_, i) => `Sessão ${i + 1}`),
      datasets: [{
        data: vals,
        backgroundColor: colors,
        borderWidth: 2,
        borderColor: '#ffffff',
      }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: true,
      aspectRatio: 1.1,
      cutout: '62%',
      plugins: {
        legend: {
          position: 'bottom',
          labels: {
            boxWidth: 8,
            font: { size: 10 },
            color: '#5a5348',
          },
        },
        tooltip: {
          callbacks: {
            label: (ctx) => ` ${ctx.raw} kg`,
          },
        },
      },
    },
  })
}

async function refresh () {
  await loadSummary()
  await loadWeekly()
  await loadRecentSessions()
  await loadExercises()
  await loadExerciseProgress()
}

watch(() => prof.selectedStudentId, refresh)
watch(selectedExerciseId, loadExerciseProgress)

onMounted(async () => {
  await loadProfile()
  await refresh()
})
onBeforeUnmount(() => {
  if (volChart) volChart.destroy()
  destroyExChart()
  destroySparkChart()
})
</script>

<style scoped>
.app-dash-greet-card {
  background: #ffffff;
  border-radius: 22px;
  padding: 18px 16px;
  box-shadow: 0 2px 14px rgba(61, 56, 48, 0.06);
  border: 1px solid rgba(214, 218, 200, 0.65);
}

.app-dash-greet-card__avatar {
  flex-shrink: 0;
  border: 2px solid #e8e4d8;
}

.app-dash-greet-card__line1 {
  font-size: 0.8125rem;
  line-height: 1.35;
  color: #7d7568;
}

.app-dash-greet-card__line2 {
  font-size: 1.25rem;
  font-weight: 800;
  letter-spacing: -0.04em;
  color: #3d3a36;
  line-height: 1.2;
  margin-top: 4px;
}

.app-dash-greet-card__bell {
  flex-shrink: 0;
}

.min-width-0 {
  min-width: 0;
}

.app-chart-donut-wrap {
  position: relative;
  max-width: 300px;
  margin: 0 auto;
}

.app-chart-donut-wrap--sm {
  max-width: 260px;
}

.app-chart-radar-wrap {
  max-width: 320px;
  margin: 0 auto;
}

.app-chart-card {
  min-height: 100%;
}
</style>
