<template>
  <q-page class="calendar-page" padding>
    <div class="app-page-inner calendar-page__inner">
      <div class="row items-center justify-between q-mb-md q-col-gutter-sm">
        <div class="col">
          <div class="page-title q-mb-none">Agenda</div>
        </div>
        <div v-if="auth.isProfessional" class="col-auto">
          <q-btn
            no-caps
            rounded
            :unelevated="!isAllAppointments"
            :outline="isAllAppointments"
            :color="isAllAppointments ? 'accent' : 'primary'"
            :icon="isAllAppointments ? 'person' : 'filter_alt_off'"
            :label="isAllAppointments ? 'Voltar ao aluno' : 'Ver todas as marcações'"
            :disable="isAllAppointments && lastFilteredStudentId == null"
            @click="toggleAllAppointments"
          />
        </div>
      </div>

      <!-- <q-banner v-if="auth.isProfessional && !prof.selectedStudentId" class="app-banner q-mb-md" dense rounded>
        {{ t('A ver todas as marcações (sem filtro de aluno). Para ver treinos no calendário, seleciona um aluno.') }}
      </q-banner> -->

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
          @navigation="onNavigation"
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

          <div v-if="dayItems.length" class="calendar-page__timeline">
            <div
              v-for="(it, idx) in dayItems"
              :key="it.key"
              class="calendar-page__timeline-row row no-wrap"
            >
              <div class="calendar-page__time-col">{{ it.timeLabel }}</div>
              <template v-if="it.kind === 'session'">
                <router-link
                  class="calendar-page__event col"
                  :class="'calendar-page__event--tone-' + (idx % 3)"
                  :to="{ name: 'workout-detail', params: { id: it.id } }"
                >
                  <div class="calendar-page__event-title row items-center no-wrap">
                    <span class="ellipsis">{{ it.title || 'Treino' }}</span>
                    <q-space />
                    <q-btn
                      flat
                      dense
                      round
                      icon="content_copy"
                      color="grey-7"
                      aria-label="Duplicar"
                      class="calendar-page__event-action"
                      @click.stop.prevent="duplicateSession(it.id)"
                    />
                    <q-btn
                      flat
                      dense
                      round
                      icon="delete"
                      color="negative"
                      aria-label="Eliminar"
                      class="calendar-page__event-action"
                      @click.stop.prevent="deleteSession(it.id)"
                    />
                  </div>
                  <div class="calendar-page__event-caption">{{ it.caption }}</div>
                </router-link>
              </template>
              <template v-else>
                <button
                  type="button"
                  class="calendar-page__event calendar-page__event--appt col"
                  @click="openAppointmentDetail(it.id)"
                >
                  <div class="calendar-page__event-title row items-center no-wrap">
                    <q-icon name="event" size="18px" class="q-mr-sm" />
                    <span class="ellipsis">{{ it.title || 'Marcação' }}</span>
                  </div>
                  <div class="calendar-page__event-caption">{{ it.caption }}</div>
                </button>
              </template>
            </div>
          </div>
          <div v-else class="calendar-page__empty text-body2">
            Sem treinos neste dia.
          </div>
        </div>
      </q-card>

      <q-page-sticky position="bottom-right" :offset="fabOffset">
        <q-btn
          fab
          icon="add"
          color="primary"
          class="calendar-page__fab"
          @click="onClickFab"
          aria-label="Novo treino"
        />
      </q-page-sticky>

      <q-dialog v-model="workoutStudentDialogOpen" position="bottom">
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
              v-model="workoutDialogStudentId"
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
              :disable="workoutDialogStudentId == null"
              @click="confirmStudentAndGoNewWorkout"
            />
          </q-card-actions>
        </q-card>
      </q-dialog>

      <q-dialog v-model="studentDialogOpen" position="bottom">
        <q-card style="width: 100%; max-width: 100%; border-radius: 20px 20px 0 0">
          <q-card-section class="q-pb-sm">
            <div class="text-h6 text-weight-bold" style="letter-spacing: -0.02em">
              Selecionar aluno
            </div>
            <p class="text-body2 text-grey-7 q-mb-none q-mt-xs">
              Escolhe o aluno para criar a marcação.
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
              @click="confirmStudentAndOpenCreate"
            />
          </q-card-actions>
        </q-card>
      </q-dialog>

      <q-dialog v-model="createDialogOpen" position="bottom">
        <q-card style="width: 100%; max-width: 100%; border-radius: 20px 20px 0 0">
          <q-card-section class="q-pb-sm">
            <div class="text-h6 text-weight-bold" style="letter-spacing: -0.02em">
              Nova marcação
            </div>
            <p class="text-body2 text-grey-7 q-mb-none q-mt-xs">
              Agenda uma sessão para o aluno selecionado.
            </p>
          </q-card-section>

          <q-card-section class="q-pt-sm">
            <q-input
              v-model="createScheduledLocal"
              label="Data e hora"
              outlined
              dense
              rounded
              bg-color="white"
              type="datetime-local"
            />
            <q-input
              v-model="createTitle"
              class="q-mt-sm"
              label="Título (opcional)"
              outlined
              dense
              rounded
              bg-color="white"
            />
            <q-input
              v-model="createNotes"
              class="q-mt-sm"
              label="Notas (opcional)"
              type="textarea"
              outlined
              dense
              rounded
              rows="2"
              bg-color="white"
            />
          </q-card-section>
          <q-card-actions align="right" class="q-px-md q-pb-md">
            <q-btn v-close-popup flat no-caps rounded color="grey-8" label="Cancelar" />
            <q-btn
              unelevated
              no-caps
              rounded
              color="primary"
              label="Criar"
              :loading="savingAppointment"
              :disable="!createScheduledLocal"
              @click="createAppointment"
            />
          </q-card-actions>
        </q-card>
      </q-dialog>

      <q-dialog v-model="detailDialogOpen" position="bottom">
        <q-card style="width: 100%; max-width: 100%; border-radius: 20px 20px 0 0">
          <q-card-section class="q-pb-sm">
            <div class="text-h6 text-weight-bold" style="letter-spacing: -0.02em">
              {{ selectedAppointment?.title || 'Marcação' }}
            </div>
            <p class="text-body2 text-grey-7 q-mb-none q-mt-xs">
              {{ selectedAppointment ? formatDateTime(selectedAppointment.scheduled_for) : '' }}
            </p>
          </q-card-section>
          <q-card-section v-if="selectedAppointment?.notes" class="q-pt-sm">
            <div class="text-body2 text-grey-8" style="white-space: pre-wrap">{{ selectedAppointment.notes }}</div>
          </q-card-section>
          <q-card-actions align="right" class="q-px-md q-pb-md">
            <q-btn
              v-close-popup
              flat
              no-caps
              rounded
              color="grey-8"
              label="Fechar"
            />
            <q-btn
              v-if="auth.isProfessional"
              flat
              no-caps
              rounded
              color="negative"
              label="Cancelar marcação"
              :disable="selectedAppointment?.status !== 'scheduled'"
              :loading="savingAppointment"
              @click="cancelSelectedAppointment"
            />
            <q-btn
              v-if="auth.isProfessional"
              unelevated
              no-caps
              rounded
              color="primary"
              label="Converter em treino"
              :disable="selectedAppointment?.status !== 'scheduled'"
              @click="goConvertSelected"
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


const { t } = useI18n()
const auth = useAuthStore()
const prof = useProfessionalStore()
const router = useRouter()
const sessions = ref([])
const appointments = ref([])
const proxyDate = ref(new Date().toISOString().slice(0, 10).replace(/-/g, '/'))
const visibleYearMonth = ref({ year: new Date().getFullYear(), month: new Date().getMonth() + 1 })

const calendarLocale = {
  days: 'Domingo_Segunda-feira_Terça-feira_Quarta-feira_Quinta-feira_Sexta-feira_Sábado'.split('_'),
  daysShort: 'Dom_Seg_Ter_Qua_Qui_Sex_Sáb'.split('_'),
  months: 'Janeiro_Fevereiro_Março_Abril_Maio_Junho_Julho_Agosto_Setembro_Outubro_Novembro_Dezembro'.split('_'),
  monthsShort: 'Jan_Fev_Mar_Abr_Mai_Jun_Jul_Ago_Set_Out_Nov_Dez'.split('_'),
}

// Aproxima o FAB da barra de navegação inferior (MainLayout)
const fabOffset = [18, 18]

const studentsLoading = ref(false)
const students = ref([])
const studentDialogOpen = ref(false)
const dialogStudentId = ref(null)
const lastFilteredStudentId = ref(null)
const workoutStudentDialogOpen = ref(false)
const workoutDialogStudentId = ref(null)

const isAllAppointments = computed(() =>
  auth.isProfessional && prof.selectedStudentId == null,
)

const createDialogOpen = ref(false)
const savingAppointment = ref(false)
const createScheduledLocal = ref('')
const createTitle = ref('')
const createNotes = ref('')

const detailDialogOpen = ref(false)
const selectedAppointmentId = ref(null)
const selectedAppointment = computed(() =>
  appointments.value.find((a) => a.id === selectedAppointmentId.value) || null,
)

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

const studentsById = computed(() => {
  const map = new Map()
  for (const s of students.value) {
    const id = s.user?.id
    if (id != null) {
      map.set(id, s)
    }
  }
  return map
})

function scopeParams () {
  if (auth.isProfessional && prof.selectedStudentId) {
    return { user_id: prof.selectedStudentId }
  }
  return {}
}

function scopeParamsAppointments () {
  // Profissional sem aluno selecionado: ver marcações de todos os alunos
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
  const n = dayItems.value.length
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
  for (const a of appointments.value) {
    if (a.status !== 'scheduled') continue
    const d = new Date(a.scheduled_for)
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

const dayAppointments = computed(() => {
  const target = selectedDay.value
  return appointments.value.filter((a) => {
    if (a.status !== 'scheduled') return false
    const d = new Date(a.scheduled_for)
    const key = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
    return key === target
  })
})

const dayItems = computed(() => {
  const items = []
  for (const s of daySessions.value) {
    items.push({
      key: `s:${s.id}`,
      kind: 'session',
      id: s.id,
      at: s.performed_at,
      timeLabel: formatTime(s.performed_at),
      title: s.title,
      caption: formatTimeRange(s),
    })
  }
  for (const a of dayAppointments.value) {
    const st = auth.isProfessional ? studentsById.value.get(a.student_id) : null
    const stLabel = st
      ? (st.profile?.full_name || st.user?.email || `Aluno ${a.student_id}`)
      : (auth.isProfessional ? `Aluno ${a.student_id}` : null)
    items.push({
      key: `a:${a.id}`,
      kind: 'appointment',
      id: a.id,
      at: a.scheduled_for,
      timeLabel: formatTime(a.scheduled_for),
      title: a.title,
      caption: stLabel ? `Marcação · ${stLabel}` : 'Marcação',
    })
  }
  return items.sort((x, y) => new Date(x.at).getTime() - new Date(y.at).getTime())
})

function formatTime (iso) {
  return new Date(iso).toLocaleTimeString('pt-PT', { hour: '2-digit', minute: '2-digit' })
}

function formatTimeRange (s) {
  const start = formatTime(s.performed_at)
  return start
}

function formatDateTime (iso) {
  return new Date(iso).toLocaleString('pt-PT', {
    weekday: 'short',
    day: '2-digit',
    month: 'short',
    hour: '2-digit',
    minute: '2-digit',
  })
}

function toIso (localStr) {
  if (!localStr) return new Date().toISOString()
  const d = new Date(localStr)
  return Number.isNaN(d.getTime()) ? new Date().toISOString() : d.toISOString()
}

function monthRangeForApi (year, month) {
  const start = new Date(year, month - 1, 1)
  const end = new Date(year, month, 0, 23, 59, 59, 999)
  return { date_from: start.toISOString(), date_to: end.toISOString() }
}

async function load (year = visibleYearMonth.value.year, month = visibleYearMonth.value.month) {
  const range = monthRangeForApi(year, month)
  if (auth.isProfessional && !prof.selectedStudentId) {
    sessions.value = []
  } else {
    const { data } = await api.get('/workouts/sessions', { params: { ...scopeParams(), ...range } })
    sessions.value = data
  }

  const { data: ap } = await api.get('/appointments', { params: { ...scopeParamsAppointments(), ...range } })
  appointments.value = ap
}

function onNavigation ({ year, month }) {
  // Navegar mês/ano no calendário não muda o proxyDate, então buscamos aqui.
  if (year === visibleYearMonth.value.year && month === visibleYearMonth.value.month) return
  visibleYearMonth.value = { year, month }
  load(year, month)
}

function syncVisibleMonthFromProxyDate () {
  const [y, m] = proxyDate.value.split('/').map(Number)
  if (!y || !m) return
  visibleYearMonth.value = { year: y, month: m }
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

function goNewWorkout () {
  const d = selectedDate.value
  if (Number.isNaN(d.getTime())) {
    Notify.create({ type: 'warning', message: t('Seleciona um dia para inicar um novo treino'), position: 'top' })
    return
  }
  const isoLocal = new Date(
    d.getFullYear(),
    d.getMonth(),
    d.getDate(),
    new Date().getHours(),
    new Date().getMinutes(),
  )
    .toISOString()
    .slice(0, 16)
  router.push({ name: 'workout-new', query: { performed_at: isoLocal, from: 'calendar' } })
}

function duplicateSession (sessionId) {
  // Igual à lista de treinos: duplicar usa data/hora atual
  const isoLocal = new Date().toISOString().slice(0, 16)
  router.push({ name: 'workout-new', query: { duplicate_of: String(sessionId), performed_at: isoLocal, from: 'calendar' } })
}

function deleteSession (sessionId) {
  Dialog.create({
    title: 'Apagar treino',
    message: 'Tem a certeza?',
    cancel: {
      label: 'Cancelar',
      color: 'negative',
    },
  }).onOk(async () => {
    try {
      await api.delete(`/workouts/sessions/${sessionId}`)
      Notify.create({ type: 'positive', message: 'Treino eliminado.', position: 'top' })
      await load()
    } catch {
      Notify.create({ type: 'negative', message: 'Não foi possível eliminar o treino.', position: 'top' })
    }
  })
}

function onClickFab () {
  if (!proxyDate.value) {
    Notify.create({ type: 'warning', message: t('Seleciona um dia para inicar um novo treino'), position: 'top' })
    return
  }
  if (auth.isProfessional && prof.selectedStudentId == null) {
    workoutDialogStudentId.value = sortedStudents.value[0]?.user?.id ?? null
    workoutStudentDialogOpen.value = true
    return
  }
  goNewWorkout()
}

function toggleAllAppointments () {
  // Toggle: 1º clique limpa e guarda; 2º clique repõe o aluno anterior
  if (prof.selectedStudentId != null) {
    lastFilteredStudentId.value = prof.selectedStudentId
    prof.setSelectedStudent(null)
    return
  }
  if (lastFilteredStudentId.value != null) {
    prof.setSelectedStudent(lastFilteredStudentId.value)
  }
}

function openCreateDialog () {
  const d = selectedDate.value
  const iso = new Date(d.getFullYear(), d.getMonth(), d.getDate(), new Date().getHours(), new Date().getMinutes())
    .toISOString()
    .slice(0, 16)
  createScheduledLocal.value = iso
  createTitle.value = ''
  createNotes.value = ''
  createDialogOpen.value = true
}

function confirmStudentAndOpenCreate () {
  if (dialogStudentId.value == null) {
    Notify.create({ type: 'warning', message: 'Escolhe um aluno.', position: 'top' })
    return
  }
  prof.setSelectedStudent(dialogStudentId.value)
  studentDialogOpen.value = false
  openCreateDialog()
}

function confirmStudentAndGoNewWorkout () {
  if (workoutDialogStudentId.value == null) {
    Notify.create({ type: 'warning', message: 'Escolhe um aluno.', position: 'top' })
    return
  }
  prof.setSelectedStudent(workoutDialogStudentId.value)
  workoutStudentDialogOpen.value = false
  goNewWorkout()
}

async function createAppointment () {
  if (!createScheduledLocal.value) return
  if (auth.isProfessional && !prof.selectedStudentId) return
  savingAppointment.value = true
  try {
    await api.post('/appointments', {
      user_id: prof.selectedStudentId,
      scheduled_for: toIso(createScheduledLocal.value),
      title: createTitle.value || null,
      notes: createNotes.value || null,
    })
    createDialogOpen.value = false
    await load()
  } finally {
    savingAppointment.value = false
  }
}

function openAppointmentDetail (id) {
  selectedAppointmentId.value = id
  detailDialogOpen.value = true
}

async function cancelSelectedAppointment () {
  if (!selectedAppointment.value) return
  savingAppointment.value = true
  try {
    await api.patch(`/appointments/${selectedAppointment.value.id}`, { status: 'cancelled' })
    detailDialogOpen.value = false
    await load()
  } finally {
    savingAppointment.value = false
  }
}

function goConvertSelected () {
  if (!selectedAppointment.value) return
  detailDialogOpen.value = false
  router.push({ name: 'workout-new', query: { from_appointment: String(selectedAppointment.value.id) } })
}

watch(() => prof.selectedStudentId, () => load())
watch(studentDialogOpen, (open) => {
  if (!open) return
  if (dialogStudentId.value == null) {
    dialogStudentId.value = sortedStudents.value[0]?.user?.id ?? null
  }
})
watch(workoutStudentDialogOpen, (open) => {
  if (!open) return
  if (workoutDialogStudentId.value == null) {
    workoutDialogStudentId.value = sortedStudents.value[0]?.user?.id ?? null
  }
})
watch(proxyDate, () => {
  const [y, m] = proxyDate.value.split('/').map(Number)
  if (!y || !m) return
  if (y === visibleYearMonth.value.year && m === visibleYearMonth.value.month) return
  visibleYearMonth.value = { year: y, month: m }
  load(y, m)
})
onMounted(() => {
  syncVisibleMonthFromProxyDate()
  load()
})
onMounted(() => {
  if (auth.isProfessional) loadStudents()
})
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

.calendar-page__event--appt {
  width: 100%;
  text-align: left;
  cursor: pointer;
  background: linear-gradient(145deg, rgba(251, 243, 213, 0.7) 0%, rgba(156, 175, 170, 0.12) 100%);
  border: 1px solid rgba(212, 201, 168, 0.65);
  box-shadow: var(--app-shadow-sm);
}

.calendar-page__event--appt:active {
  transform: scale(0.99);
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

.calendar-page__event-action {
  margin-right: -6px;
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
