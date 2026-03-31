<template>
  <q-page class="calendar-page" padding>
    <div class="app-page-inner calendar-page__inner">
      <div class="page-title q-mb-md">Agenda</div>

      <q-banner v-if="auth.isProfessional && !prof.selectedStudentId" class="app-banner q-mb-md" dense rounded>
        Selecione um aluno para ver o calendário desse aluno.
      </q-banner>

      <q-card flat class="calendar-page__shell">
        <q-date
          v-model="proxyDate"
          :events="eventDates"
          event-color="primary"
          mask="YYYY/MM/DD"
          class="calendar-page__date"
          color="primary"
          borderless
          :first-day-of-week="1"
          :locale="calendarLocale"
        />

        <div class="calendar-page__handle" aria-hidden="true" />

        <div class="calendar-page__agenda">
          <div class="calendar-page__agenda-head row no-wrap items-start justify-between">
            <div class="calendar-page__day-block">
              <div class="calendar-page__day-num">{{ dayOfMonth }}</div>
              <div class="calendar-page__day-week">{{ weekdayShort }}</div>
            </div>
            <div class="calendar-page__agenda-meta column items-end text-right">
              <span class="calendar-page__today-label">{{ todayOrDateLabel }}</span>
              <span class="calendar-page__agenda-sub">{{ agendaSummary }}</span>
            </div>
          </div>

          <div v-if="daySessions.length" class="calendar-page__timeline">
            <div
              v-for="(s, idx) in daySessions"
              :key="s.id"
              class="calendar-page__timeline-row row no-wrap"
            >
              <div class="calendar-page__time-col">{{ formatTime(s.performed_at) }}</div>
              <router-link
                class="calendar-page__event col"
                :class="'calendar-page__event--tone-' + (idx % 3)"
                :to="{ name: 'workout-detail', params: { id: s.id } }"
              >
                <div class="calendar-page__event-title">{{ s.title || 'Treino' }}</div>
                <div class="calendar-page__event-caption">{{ formatTimeRange(s) }}</div>
              </router-link>
            </div>
          </div>
          <div v-else class="calendar-page__empty text-body2">
            Sem treinos neste dia.
          </div>
        </div>
      </q-card>

      <!-- <q-page-sticky position="bottom-right" :offset="fabOffset">
        <q-btn
          fab
          icon="add"
          color="primary"
          class="calendar-page__fab"
          :to="{ name: 'workout-new' }"
          aria-label="Novo treino"
        />
      </q-page-sticky> -->
    </div>
  </q-page>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { api } from 'src/api/client'
import { useAuthStore } from 'src/stores/auth'
import { useProfessionalStore } from 'src/stores/professional'

const auth = useAuthStore()
const prof = useProfessionalStore()
const sessions = ref([])
const proxyDate = ref(new Date().toISOString().slice(0, 10).replace(/-/g, '/'))

const calendarLocale = {
  days: 'Domingo_Segunda-feira_Terça-feira_Quarta-feira_Quinta-feira_Sexta-feira_Sábado'.split('_'),
  daysShort: 'Dom_Seg_Ter_Qua_Qui_Sex_Sáb'.split('_'),
  months: 'Janeiro_Fevereiro_Março_Abril_Maio_Junho_Julho_Agosto_Setembro_Outubro_Novembro_Dezembro'.split('_'),
  monthsShort: 'Jan_Fev_Mar_Abr_Mai_Jun_Jul_Ago_Set_Out_Nov_Dez'.split('_'),
}

// const fabOffset = [18, 96]

function scopeParams () {
  if (auth.isProfessional && prof.selectedStudentId) {
    return { user_id: prof.selectedStudentId }
  }
  return {}
}

const selectedDay = computed(() => proxyDate.value.replace(/\//g, '-'))

const selectedDate = computed(() => {
  const [y, m, d] = proxyDate.value.split('/').map(Number)
  return new Date(y, m - 1, d)
})

const dayOfMonth = computed(() => selectedDate.value.getDate())

const weekdayShort = computed(() =>
  selectedDate.value.toLocaleDateString('pt-PT', { weekday: 'short' }).replace('.', '').toUpperCase(),
)

const isSelectedToday = computed(() => {
  const t = new Date()
  const [y, m, d] = proxyDate.value.split('/').map(Number)
  return t.getFullYear() === y && t.getMonth() + 1 === m && t.getDate() === d
})

const todayOrDateLabel = computed(() => {
  if (isSelectedToday.value) return 'Hoje'
  return selectedDate.value.toLocaleDateString('pt-PT', {
    day: 'numeric',
    month: 'long',
  })
})

const agendaSummary = computed(() => {
  const n = daySessions.value.length
  if (n === 0) return 'Nenhum treino agendado'
  if (n === 1) return '1 treino'
  return `${n} treinos`
})

const eventDates = computed(() => {
  const set = new Set()
  for (const s of sessions.value) {
    const d = new Date(s.performed_at)
    const key = `${d.getFullYear()}/${String(d.getMonth() + 1).padStart(2, '0')}/${String(d.getDate()).padStart(2, '0')}`
    set.add(key)
  }
  return [...set]
})

const daySessions = computed(() => {
  const target = selectedDay.value
  return sessions.value.filter((s) => {
    const d = new Date(s.performed_at)
    const key = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
    return key === target
  })
})

function formatTime (iso) {
  return new Date(iso).toLocaleTimeString('pt-PT', { hour: '2-digit', minute: '2-digit' })
}

function formatTimeRange (s) {
  const start = formatTime(s.performed_at)
  return start
}

async function load () {
  const { data } = await api.get('/workouts/sessions', { params: scopeParams() })
  sessions.value = data
}

watch(() => prof.selectedStudentId, load)
onMounted(load)
</script>

<style lang="scss" scoped>
.calendar-page {
  padding-bottom: calc(100px + env(safe-area-inset-bottom, 0px));
}

.calendar-page__inner {
  max-width: 520px;
}

.calendar-page__shell {
  background: var(--app-surface-elevated);
  border: 1px solid var(--app-border);
  border-radius: var(--app-radius-xl);
  box-shadow: var(--app-shadow-md);
  overflow: hidden;
}

.calendar-page__date {
  width: 100%;
  min-width: 0;

  :deep(.q-date__header) {
    border: none;
    padding: 14px 16px 8px;
  }

  :deep(.q-date__header-subtitle) {
    font-size: 0.8rem;
    font-weight: 600;
    letter-spacing: 0.04em;
    color: var(--app-text-muted);
  }

  :deep(.q-date__header-title-label) {
    font-size: 1.2rem;
    font-weight: 800;
    letter-spacing: -0.03em;
    color: var(--app-text);
  }

  :deep(.q-date__navigation) {
    padding: 0 8px 10px;
  }

  :deep(.q-date__calendar-item) {
    border-radius: 999px;
  }

  :deep(.q-date__calendar-weekdays) {
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 0.06em;
    color: var(--app-text-muted);
    text-transform: uppercase;
  }

  :deep(.q-date__calendar-days-container) {
    padding: 4px 10px 16px;
  }

  :deep(.q-date__event) {
    box-shadow: 0 0 0 1px rgba(156, 175, 170, 0.45);
  }
}

.calendar-page__handle {
  width: 36px;
  height: 4px;
  border-radius: 999px;
  background: rgba(61, 56, 48, 0.12);
  margin: 0 auto 8px;
}

.calendar-page__agenda {
  padding: 8px 18px 24px;
}

.calendar-page__agenda-head {
  margin-bottom: 20px;
}

.calendar-page__day-num {
  font-size: 2.35rem;
  font-weight: 800;
  letter-spacing: -0.05em;
  line-height: 1;
  color: var(--app-text);
}

.calendar-page__day-week {
  font-size: 0.7rem;
  font-weight: 600;
  letter-spacing: 0.12em;
  color: var(--app-text-muted);
  margin-top: 4px;
}

.calendar-page__today-label {
  font-size: 1rem;
  font-weight: 700;
  letter-spacing: -0.02em;
  color: var(--app-text);
}

.calendar-page__agenda-sub {
  font-size: 0.8rem;
  color: var(--app-text-muted);
  margin-top: 2px;
}

.calendar-page__timeline {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.calendar-page__timeline-row {
  align-items: stretch;
  gap: 12px;
}

.calendar-page__time-col {
  flex: 0 0 44px;
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--app-text-muted);
  padding-top: 12px;
}

.calendar-page__event {
  display: block;
  text-decoration: none;
  color: inherit;
  border-radius: var(--app-radius-lg);
  padding: 14px 16px;
  transition: transform 0.15s ease, box-shadow 0.2s ease;
}

.calendar-page__event:active {
  transform: scale(0.99);
}

.calendar-page__event-title {
  font-size: 0.95rem;
  font-weight: 700;
  letter-spacing: -0.02em;
  color: var(--app-text);
}

.calendar-page__event-caption {
  font-size: 0.78rem;
  color: var(--app-text-muted);
  margin-top: 4px;
}

/* Tons da paleta da app: primary (sage), creme, accent (terracota) */
.calendar-page__event--tone-0 {
  background: linear-gradient(145deg, rgba(156, 175, 170, 0.32) 0%, rgba(156, 175, 170, 0.14) 100%);
  border: 1px solid rgba(156, 175, 170, 0.45);
  box-shadow: var(--app-shadow-sm);
}

.calendar-page__event--tone-1 {
  background: linear-gradient(145deg, #fbf3d5 0%, #f0e8dc 100%);
  border: 1px solid rgba(212, 201, 168, 0.65);
  box-shadow: var(--app-shadow-sm);
}

.calendar-page__event--tone-2 {
  background: linear-gradient(145deg, rgba(214, 169, 157, 0.35) 0%, rgba(214, 169, 157, 0.18) 100%);
  border: 1px solid rgba(214, 169, 157, 0.5);
  box-shadow: var(--app-shadow-sm);
}

.calendar-page__empty {
  color: var(--app-text-muted);
  padding: 12px 0 8px;
  text-align: center;
}

.calendar-page__fab {
  box-shadow: 0 8px 28px rgba(125, 148, 137, 0.38);
}
</style>
