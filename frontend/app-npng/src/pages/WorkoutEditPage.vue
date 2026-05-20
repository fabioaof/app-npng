<template>
  <q-page padding class="workout-edit-page">
    <template v-if="ready && !loading">
      <div class="app-page-inner workout-edit-inner">
        <div class="workout-edit-top row items-center no-wrap q-mb-sm">
          <q-btn
            round
            flat
            dense
            icon="arrow_back"
            class="workout-edit-back"
            aria-label="Voltar"
            @click="goBack"
          />
          <div class="col min-width-0 q-pl-xs">
            <div class="text-h6 text-weight-bold ellipsis" style="letter-spacing: -0.02em">
              {{ isNew ? 'Novo treino' : (title || 'Treino') }}
            </div>
          </div>
          <q-btn
            v-if="!isNew"
            flat
            dense
            no-caps
            rounded
            color="negative"
            label="Apagar"
            class="workout-edit-top-delete"
            @click="onDelete"
          />
        </div>
        <div v-if="!isNew" class="row q-gutter-sm q-mb-lg">
          <q-chip outline dense class="app-chip-pill text-grey-8">
            <q-icon name="schedule" size="16px" class="q-mr-xs" />
            {{ chipDate }}
          </q-chip>
          <q-chip outline dense class="app-chip-pill text-grey-8">
            <q-icon name="sports_gymnastics" size="16px" class="q-mr-xs" />
            {{ exerciseBlockCount }} exercícios · {{ totalSets }} sets
          </q-chip>
        </div>

        <q-banner
          v-if="auth.isProfessional && !prof.selectedStudentId && isNew"
          class="app-banner q-mb-md"
          dense
          rounded
        >
          {{ t('Seleciona um aluno antes de registar o treino.') }}
        </q-banner>

        <q-form ref="workoutFormRef" class="workout-edit-form" @submit="onSave">
          <div class="workout-edit-card q-mb-md">
            <div class="workout-edit-card__label">Sessão</div>
            <div class="row q-col-gutter-md">
              <div class="col-12 col-sm-6">
                <q-input
                  v-model="performedAtLocal"
                  label="Data e hora"
                  outlined
                  dense
                  rounded
                  bg-color="white"
                  type="datetime-local"
                />
              </div>
              <div class="col-12 col-sm-6">
                <q-input
                  v-model="title"
                  label="Título (opcional)"
                  outlined
                  dense
                  rounded
                  bg-color="white"
                />
              </div>
            </div>
            <q-input
              v-model="notes"
              class="q-mt-md"
              label="Notas"
              type="textarea"
              outlined
              dense
              rounded
              rows="2"
              bg-color="white"
            />
          </div>

          <div
            v-if="!blocks.length"
            class="text-body2 text-grey-7 q-mb-md workout-edit-empty"
          >
            {{ t('Ainda não há exercícios. Clica em «Adicionar exercício».') }}
          </div>

          <div
            v-for="(block, bIdx) in blocks"
            :key="block.id"
            class="workout-block q-mb-lg"
          >
            <div class="workout-block__head row items-center justify-between q-mb-sm">
              <span class="workout-block__label">Exercício {{ bIdx + 1 }}</span>
              <div class="row items-center no-wrap q-gutter-xs">
                <q-btn
                  flat
                  dense
                  no-caps
                  color="grey-7"
                  icon="history"
                  :label="compactBlockToolbar ? undefined : 'Histórico'"
                  rounded
                  class="workout-block__head-history"
                  :aria-label="'Histórico de ' + exerciseName(block.exercise_id)"
                  @click="openExerciseHistory(block)"
                />
                <q-btn
                  flat
                  dense
                  no-caps
                  icon="close"
                  label="Remover"
                  rounded
                  class="workout-block__remove-exercise"
                  @click="removeBlock(bIdx)"
                />
              </div>
            </div>

            <button
              type="button"
              class="workout-exercise-title text-subtitle1 text-weight-bold text-grey-9 q-mb-sm workout-exercise-title--pick"
              :class="{ 'workout-exercise-title--pick-active': block.id === selectedBlockIdForSet }"
              :aria-pressed="block.id === selectedBlockIdForSet"
              :aria-label="'Selecionar ' + exerciseName(block.exercise_id) + ' para adicionar sets'"
              @click="selectBlockForAddSet(block)"
            >
              {{ exerciseName(block.exercise_id) }}
            </button>

            <div class="workout-sets-stack">
              <div
                v-for="(row, idx) in block.sets"
                :key="idx"
                class="workout-set-card"
              >
                <div class="workout-set-card__toolbar row items-center justify-between no-wrap">
                  <span class="workout-set-card__badge">Set {{ idx + 1 }}</span>
                  <q-btn
                    flat
                    dense
                    round
                    icon="delete"
                    color="grey-7"
                    size="sm"
                    :disable="block.sets.length <= 1"
                    aria-label="Remover set"
                    @click="removeSetFromBlock(block, idx)"
                  />
                </div>
                <div class="row q-col-gutter-sm">
                  <div class="col-6">
                    <q-input
                      v-model.number="row.weight_kg"
                      type="number"
                      outlined
                      dense
                      rounded
                      bg-color="white"
                      min="0"
                      step="0.5"
                      label="Peso (kg)"
                      input-class="text-center"
                    />
                  </div>
                  <div class="col-6">
                    <q-input
                      v-model.number="row.reps"
                      type="number"
                      outlined
                      dense
                      rounded
                      bg-color="white"
                      min="0"
                      label="Reps"
                      input-class="text-center"
                    />
                  </div>
                  <div class="col-12">
                    <q-input
                      v-model.number="row.rest_seconds"
                      type="number"
                      outlined
                      dense
                      rounded
                      bg-color="white"
                      min="0"
                      label="Descanso (s)"
                      input-class="text-center"
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </q-form>
      </div>
    </template>

    <template v-else>
      <div class="app-page-inner">
        <div class="page-title">{{ isNew ? 'Novo treino' : 'Treino' }}</div>
      </div>
    </template>
    <q-inner-loading :showing="loading" />

    <q-page-sticky
      v-if="ready && !loading"
      position="bottom"
      expand
      class="workout-edit-sticky-wrap"
    >
      <div class="workout-edit-sticky-actions">
        <div class="app-page-inner workout-edit-sticky-actions__inner">
          <div class="workout-edit-sticky-toolbar row no-wrap items-center">
            <q-btn
              outline
              dense
              no-caps
              color="grey-8"
              rounded
              :icon="compactWorkoutToolbar ? 'fitness_center' : undefined"
              :label="compactWorkoutToolbar ? undefined : 'Adicionar exercício'"
              aria-label="Adicionar exercício"
              class="workout-edit-sticky-toolbar__add"
              padding="xs sm"
              @click="openExerciseDialog"
            />
            <q-btn
              outline
              dense
              no-caps
              color="grey-8"
              rounded
              :icon="compactWorkoutToolbar ? 'exposure_plus_1' : undefined"
              :label="compactWorkoutToolbar ? undefined : 'Adicionar set'"
              aria-label="Adicionar set"
              class="workout-edit-sticky-toolbar__add"
              padding="xs sm"
              @click="addSetToSelectedBlock"
            />
            <q-space />
            <q-btn
              flat
              dense
              no-caps
              rounded
              color="grey-8"
              label="Cancelar"
              padding="xs sm"
              class="workout-edit-sticky-toolbar__text"
              @click="goBack"
            />
            <q-btn
              unelevated
              dense
              no-caps
              color="primary"
              padding="xs sm"
              rounded
              :label="saveWorkoutLabel"
              class="workout-edit-sticky-save"
              :loading="saving"
              @click="submitWorkoutForm"
            />
          </div>
        </div>
      </div>
    </q-page-sticky>

    <q-dialog
      v-model="exerciseDialogOpen"
      position="bottom"
      class="workout-exercise-dialog"
    >
      <q-card class="workout-exercise-dialog__card">
        <q-card-section class="q-pb-sm">
          <div class="text-h6 text-weight-bold" style="letter-spacing: -0.02em">
            Novo exercício
          </div>
          <p class="text-body2 text-grey-7 q-mb-none q-mt-xs">
            Escolhe o exercício a registar neste treino.
          </p>
        </q-card-section>
        <q-card-section class="q-pt-sm">
          <q-select
            v-model="dialogExerciseId"
            :options="exerciseOptions"
            emit-value
            map-options
            label="Exercício"
            outlined
            dense
            rounded
            bg-color="white"
            :disable="!exerciseOptions.length"
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
            label="Adicionar"
            :disable="dialogExerciseId == null"
            @click="confirmAddExerciseFromDialog"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <q-dialog
      v-model="exerciseHistoryDialogOpen"
      position="bottom"
      class="workout-exercise-dialog"
    >
      <q-card class="workout-exercise-dialog__card workout-history-dialog__card">
        <q-card-section class="q-pb-sm">
          <div class="text-h6 text-weight-bold" style="letter-spacing: -0.02em">
            Histórico
          </div>
          <p class="text-body2 text-grey-7 q-mb-none q-mt-xs">
            {{ exerciseHistoryExerciseId != null ? exerciseName(exerciseHistoryExerciseId) : '' }}
          </p>
        </q-card-section>
        <q-card-section class="q-pt-none workout-history-body">
          <q-inner-loading :showing="exerciseHistoryLoading" />
          <template v-if="!exerciseHistoryLoading">
            <div
              v-if="!historySessions.length"
              class="text-body2 text-grey-7 text-center q-py-lg"
            >
              Ainda não há treinos anteriores com este exercício.
            </div>
            <q-timeline
              v-else
              color="primary"
              layout="comfortable"
              class="workout-history-timeline"
            >
              <q-timeline-entry
                v-for="s in historySessions"
                :key="s.id"
                :title="s.title || 'Treino'"
                :subtitle="formatHistorySessionDate(s.performed_at)"
                icon="fitness_center"
              >
                <div class="workout-history-sets text-body2 text-grey-9">
                  <div
                    v-for="(row, i) in historySetsForSession(s)"
                    :key="row.id ?? i"
                    class="workout-history-set-line"
                  >
                    Set {{ i + 1 }}: {{ row.weight_kg }} kg × {{ row.reps }} reps
                    <template v-if="row.rest_seconds != null">
                      · {{ row.rest_seconds }} s descanso
                    </template>
                  </div>
                </div>
              </q-timeline-entry>
            </q-timeline>
          </template>
        </q-card-section>
        <q-card-actions align="right" class="q-px-md q-pb-md">
          <q-btn v-close-popup flat no-caps rounded color="grey-8" label="Fechar" />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Dialog, Notify, useQuasar } from 'quasar'
import { api } from 'src/api/client'
import { useAuthStore } from 'src/stores/auth'
import { useProfessionalStore } from 'src/stores/professional'
import { useI18n } from 'vue-i18n'


const { t } = useI18n()
const $q = useQuasar()
const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const prof = useProfessionalStore()

/** Ecrã estreito: barra numa linha com ícones + «Guardar» curto */
const compactWorkoutToolbar = computed(() => $q.screen.lt.md)

/** Cabeçalho do bloco: só ícone no histórico em ecrãs muito estreitos */
const compactBlockToolbar = computed(() => $q.screen.lt.sm)

const saveWorkoutLabel = computed(() =>
  compactWorkoutToolbar.value ? 'Guardar' : 'Guardar treino',
)

const isNew = computed(() => route.name === 'workout-new')
const sessionId = computed(() => route.params.id)

const cameFromCalendar = computed(() => route.query.from === 'calendar')

const duplicateOfSessionId = computed(() => {
  const v = route.query.duplicate_of
  if (v == null) return null
  const n = Number(v)
  return Number.isFinite(n) && n > 0 ? n : null
})

const fromAppointmentId = computed(() => {
  const v = route.query.from_appointment
  if (v == null) return null
  const n = Number(v)
  return Number.isFinite(n) && n > 0 ? n : null
})

const fromPerformedAtLocal = computed(() => {
  const v = route.query.performed_at
  if (typeof v !== 'string') return null
  // Espera-se o formato de input datetime-local: "YYYY-MM-DDTHH:mm"
  return v.length >= 16 ? v.slice(0, 16) : null
})

const linkedAppointmentId = ref(null)

let blockIdSeq = 0
function nextBlockId () {
  blockIdSeq += 1
  return blockIdSeq
}

function createBlock (exerciseId) {
  return {
    id: nextBlockId(),
    exercise_id: exerciseId,
    sets: [defaultSetRow()],
  }
}

const loading = ref(true)
const saving = ref(false)
const ready = ref(false)
/** @type {import('vue').Ref<import('quasar').QForm | null>} */
const workoutFormRef = ref(null)
const performedAtLocal = ref('')
const title = ref('')
const notes = ref('')
/** @type {import('vue').Ref<Array<{ id: number, exercise_id: number, sets: Array<{ weight_kg: number, reps: number, rest_seconds: number | null }> }>>} */
const blocks = ref([])
const exercises = ref([])

const exerciseDialogOpen = ref(false)
const dialogExerciseId = ref(null)

/** Dono da sessão em edição (histórico com o mesmo âmbito do treino) */
const sessionOwnerUserId = ref(null)
/** Treino duplicado: user_id da fonte quando ainda não há aluno selecionado */
const duplicateSourceUserId = ref(null)

const exerciseHistoryDialogOpen = ref(false)
const exerciseHistoryLoading = ref(false)
const exerciseHistoryExerciseId = ref(null)
const historySessions = ref([])

/** Bloco onde «Adicionar set» aplica; escolhido ao clicar no nome do exercício */
const selectedBlockIdForSet = ref(null)

const exerciseOptions = computed(() =>
  exercises.value.map((e) => ({ label: e.name, value: e.id })),
)

const totalSets = computed(() =>
  blocks.value.reduce((acc, b) => acc + b.sets.length, 0),
)

const exerciseBlockCount = computed(() => blocks.value.length)

const chipDate = computed(() => {
  if (!performedAtLocal.value) return '—'
  const d = new Date(performedAtLocal.value)
  if (Number.isNaN(d.getTime())) return '—'
  return d.toLocaleString('pt-PT', {
    weekday: 'short',
    day: 'numeric',
    month: 'short',
    hour: '2-digit',
    minute: '2-digit',
  })
})

function exerciseName (exerciseId) {
  const ex = exercises.value.find((e) => e.id === exerciseId)
  return ex?.name ?? ''
}

function defaultSetRow (previousSet = null) {
  return {
    weight_kg: previousSet?.weight_kg ?? 0,
    reps: 10,
    rest_seconds: 90,
  }
}

function openExerciseDialog () {
  dialogExerciseId.value = exercises.value[0]?.id ?? null
  exerciseDialogOpen.value = true
}

function confirmAddExerciseFromDialog () {
  if (dialogExerciseId.value == null) {
    Notify.create({
      type: 'warning',
      message: 'Escolhe um exercício.',
      position: 'top',
    })
    return
  }
  const block = createBlock(dialogExerciseId.value)
  blocks.value.push(block)
  selectedBlockIdForSet.value = block.id
  exerciseDialogOpen.value = false
  dialogExerciseId.value = null
}

function syncSelectedBlockIdForSet () {
  if (!blocks.value.length) {
    selectedBlockIdForSet.value = null
    return
  }
  const ids = new Set(blocks.value.map((b) => b.id))
  if (selectedBlockIdForSet.value == null || !ids.has(selectedBlockIdForSet.value)) {
    selectedBlockIdForSet.value = blocks.value[blocks.value.length - 1].id
  }
}

function selectBlockForAddSet (block) {
  selectedBlockIdForSet.value = block.id
}

function addSetToBlock (block) {
  const previousSet = block.sets.length > 0 ? block.sets[block.sets.length - 1] : null
  block.sets.push(defaultSetRow(previousSet))
}

function addSetToSelectedBlock () {
  if (!blocks.value.length) {
    Notify.create({
      type: 'info',
      message: 'Adiciona primeiro um exercício.',
      position: 'top',
    })
    return
  }
  syncSelectedBlockIdForSet()
  const block = blocks.value.find((b) => b.id === selectedBlockIdForSet.value)
  if (!block) {
    Notify.create({
      type: 'warning',
      message: 'Clica no nome do exercício onde queres o novo set.',
      position: 'top',
    })
    return
  }
  addSetToBlock(block)
}

function removeSetFromBlock (block, idx) {
  if (block.sets.length <= 1) return
  block.sets.splice(idx, 1)
}

function removeBlock (idx) {
  blocks.value.splice(idx, 1)
  syncSelectedBlockIdForSet()
}

function historyScopeParams () {
  if (!isNew.value) {
    if (auth.isProfessional && sessionOwnerUserId.value != null) {
      return { user_id: sessionOwnerUserId.value }
    }
    return {}
  }
  if (auth.isProfessional) {
    const uid = prof.selectedStudentId ?? duplicateSourceUserId.value
    if (uid == null) return null
    return { user_id: uid }
  }
  return {}
}

function formatHistorySessionDate (iso) {
  if (!iso) return '—'
  const d = new Date(iso)
  if (Number.isNaN(d.getTime())) return '—'
  return d.toLocaleString('pt-PT', {
    weekday: 'short',
    day: 'numeric',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

function historySetsForSession (session) {
  const eid = exerciseHistoryExerciseId.value
  if (eid == null || !session.sets?.length) return []
  return [...session.sets]
    .filter((x) => x.exercise_id === eid)
    .sort((a, b) => a.set_index - b.set_index)
}

async function openExerciseHistory (block) {
  const scope = historyScopeParams()
  if (scope === null) {
    Notify.create({
      type: 'warning',
      message: 'Para ver o histórico, seleciona um aluno (ou duplica um treino existente).',
      position: 'top',
    })
    return
  }
  exerciseHistoryExerciseId.value = block.exercise_id
  exerciseHistoryDialogOpen.value = true
  exerciseHistoryLoading.value = true
  historySessions.value = []
  try {
    const { data } = await api.get('/workouts/sessions', {
      params: {
        ...scope,
        exercise_id: block.exercise_id,
        limit: 50,
      },
    })
    const curId = !isNew.value && sessionId.value ? Number(sessionId.value) : null
    historySessions.value = (data || []).filter((s) => s.id !== curId)
  } catch {
    Notify.create({
      type: 'negative',
      message: 'Não foi possível carregar o histórico.',
      position: 'top',
    })
  } finally {
    exerciseHistoryLoading.value = false
  }
}

/**
 * Ordem da sessão = ordem dos blocos; set_index na API é global na sessão.
 */
function flattenBlocksToPayload () {
  const rows = []
  let globalIdx = 0
  for (const block of blocks.value) {
    for (const s of block.sets) {
      rows.push({
        exercise_id: block.exercise_id,
        set_index: globalIdx++,
        weight_kg: s.weight_kg,
        reps: s.reps,
        rest_seconds: s.rest_seconds,
      })
    }
  }
  return rows
}

/** API → blocos: ordenar por set_index global, agrupar exercícios consecutivos */
function sessionSetsToBlocks (flatSets) {
  if (!flatSets?.length) {
    return []
  }
  const sorted = [...flatSets].sort((a, b) => a.set_index - b.set_index)
  const out = []
  for (const s of sorted) {
    const last = out[out.length - 1]
    const row = {
      weight_kg: s.weight_kg,
      reps: s.reps,
      rest_seconds: s.rest_seconds ?? null,
    }
    if (last && last.exercise_id === s.exercise_id) {
      last.sets.push(row)
    } else {
      out.push({
        id: nextBlockId(),
        exercise_id: s.exercise_id,
        sets: [row],
      })
    }
  }
  return out
}

function toIso (localStr) {
  if (!localStr) return new Date().toISOString()
  const d = new Date(localStr)
  return Number.isNaN(d.getTime()) ? new Date().toISOString() : d.toISOString()
}

async function loadExercises () {
  const { data } = await api.get('/exercises')
  exercises.value = data
}

async function loadSession () {
  if (isNew.value) {
    sessionOwnerUserId.value = null
    duplicateSourceUserId.value = null
    performedAtLocal.value = new Date().toISOString().slice(0, 16)
    blockIdSeq = 0
    blocks.value = []
    linkedAppointmentId.value = null
    if (fromAppointmentId.value) {
      try {
        const { data } = await api.get(`/appointments/${fromAppointmentId.value}`)
        performedAtLocal.value = data.scheduled_for?.slice(0, 16) || performedAtLocal.value
        title.value = data.title || ''
        notes.value = data.notes || ''
        linkedAppointmentId.value = data.id
      } catch {
        // Se a marcação não existir/permissões, ignora e cria treino normal.
        linkedAppointmentId.value = null
      }
    } else if (fromPerformedAtLocal.value) {
      performedAtLocal.value = fromPerformedAtLocal.value
    }

    if (duplicateOfSessionId.value) {
      try {
        const { data } = await api.get(`/workouts/sessions/${duplicateOfSessionId.value}`)
        // Duplicar conteúdo (título/notas/sets) mas manter "data atual"
        title.value = data.title || ''
        notes.value = data.notes || ''
        blockIdSeq = 0
        blocks.value = sessionSetsToBlocks(data.sets || [])
        duplicateSourceUserId.value = data.user_id ?? null
      } catch {
        // Se não existir/permissões, mantém treino vazio.
      }
    }
    syncSelectedBlockIdForSet()
    ready.value = true
    return
  }
  const { data } = await api.get(`/workouts/sessions/${sessionId.value}`)
  sessionOwnerUserId.value = data.user_id ?? null
  performedAtLocal.value = data.performed_at.slice(0, 16)
  title.value = data.title || ''
  notes.value = data.notes || ''
  blockIdSeq = 0
  blocks.value = sessionSetsToBlocks(data.sets || [])
  syncSelectedBlockIdForSet()
  ready.value = true
}

function submitWorkoutForm () {
  workoutFormRef.value?.submit()
}

async function onSave () {
  if (auth.isProfessional && !prof.selectedStudentId && isNew.value) {
    return
  }
  const payloadSets = flattenBlocksToPayload()
  if (!payloadSets.length && !auth.isProfessional) {
    Notify.create({
      type: 'warning',
      message: 'Adiciona pelo menos um exercício e um set antes de guardar.',
      position: 'top',
    })
    return
  }
  saving.value = true
  try {
    const payload = {
      performed_at: toIso(performedAtLocal.value),
      title: title.value || null,
      notes: notes.value || null,
      sets: payloadSets,
    }
    if (auth.isProfessional && prof.selectedStudentId) {
      payload.user_id = prof.selectedStudentId
    }
    if (isNew.value) {
      const { data: created } = await api.post('/workouts/sessions', payload)
      if (linkedAppointmentId.value) {
        await api.post(`/appointments/${linkedAppointmentId.value}/convert`, { session_id: created.id })
      }
    } else {
      await api.patch(`/workouts/sessions/${sessionId.value}`, payload)
    }
    router.push({ name: 'workouts' })
  } finally {
    saving.value = false
  }
}

function onDelete () {
  Dialog.create({
    title: 'Apagar treino',
    message: 'Tem a certeza?',
    cancel: {
      label: t('Cancelar'),
      color: 'negative',
    }
  }).onOk(async () => {
    await api.delete(`/workouts/sessions/${sessionId.value}`)
    router.push({ name: 'workouts' })
  })
}

onMounted(async () => {
  loading.value = true
  try {
    await loadExercises()
    await loadSession()
  } finally {
    loading.value = false
  }
})

watch(() => route.params.id, async () => {
  loading.value = true
  ready.value = false
  try {
    await loadSession()
  } finally {
    loading.value = false
  }
})

function goBack () {
  if (cameFromCalendar.value) {
    router.push({ name: 'calendar' })
    return
  }
  router.push({ name: 'workouts' })
}
</script>

<style scoped>
.workout-edit-inner {
  padding-bottom: calc(72px + env(safe-area-inset-bottom, 12px));
}

.workout-edit-sticky-wrap {
  z-index: 2000;
}

.workout-edit-sticky-actions {
  width: 100%;
  padding: 0;
  background: rgba(250, 249, 247, 0.97);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border-top: 1px solid var(--app-border);
  box-shadow: 0 -6px 24px rgba(15, 23, 42, 0.08);
}

.workout-edit-sticky-actions__inner {
  max-width: 720px;
  margin-left: auto;
  margin-right: auto;
  padding: 10px 0 calc(10px + env(safe-area-inset-bottom, 0px));
}

.workout-edit-sticky-toolbar {
  width: 100%;
  min-height: 44px;
  column-gap: 6px;
  padding: 0 16px;
}

.workout-edit-sticky-toolbar__add {
  flex: 1 1 0;
  min-width: 0;
}

.workout-edit-sticky-toolbar__text {
  flex-shrink: 0;
}

.workout-edit-sticky-save {
  flex-shrink: 0;
}

@media (min-width: 1024px) {
  .workout-edit-sticky-toolbar {
    column-gap: 10px;
  }
}

.workout-edit-top-delete {
  flex-shrink: 0;
  font-size: 0.8rem;
}

.workout-edit-top {
  margin-top: env(safe-area-inset-top, 0px);
}

.min-width-0 {
  min-width: 0;
}

.workout-edit-empty {
  padding: 14px 16px;
  border-radius: 18px;
  background: rgba(109, 99, 89, 0.06);
  border: 1px dashed var(--app-border);
}

.workout-exercise-dialog__card {
  width: 100%;
  max-width: 100%;
  border-radius: 20px 20px 0 0;
}

.workout-history-dialog__card {
  max-height: min(78vh, 640px);
  display: flex;
  flex-direction: column;
}

.workout-history-body {
  position: relative;
  min-height: 100px;
  overflow: auto;
  flex: 1 1 auto;
}

.workout-history-timeline {
  padding-top: 4px;
}

.workout-history-set-line + .workout-history-set-line {
  margin-top: 4px;
}

.workout-block__head-history {
  flex-shrink: 0;
}

.workout-block__remove-exercise {
  color: #b8877a;
}

.workout-edit-form {
  max-width: 720px;
}

.workout-edit-card {
  background: #ffffff;
  border-radius: 22px;
  padding: 18px 16px;
  box-shadow: 0 2px 14px rgba(15, 23, 42, 0.06);
  border: 1px solid rgba(0, 0, 0, 0.04);
}

.workout-edit-card__label {
  font-size: 0.65rem;
  font-weight: 600;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--app-text-muted);
  margin-bottom: 14px;
}

.workout-block__label {
  font-size: 0.65rem;
  font-weight: 600;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--app-text-muted);
}

.workout-exercise-title--pick {
  display: block;
  width: 100%;
  text-align: left;
  font: inherit;
  font-family: inherit;
  border: none;
  background: transparent;
  cursor: pointer;
  border-radius: 12px;
  padding: 6px 8px;
  margin-left: -8px;
  margin-right: -8px;
  box-sizing: border-box;
  transition: background 0.15s ease, box-shadow 0.15s ease;
}

.workout-exercise-title--pick:focus-visible {
  outline: 2px solid var(--app-accent-mid);
  outline-offset: 1px;
}

.workout-exercise-title--pick-active {
  background: var(--app-accent-soft);
  box-shadow: inset 0 0 0 1px var(--app-border);
}

.workout-sets-stack {
  display: flex;
  flex-direction: column;
  gap: 12px;
  width: 100%;
  max-width: 100%;
}

.workout-set-card {
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
  padding: 14px 14px 16px;
  border-radius: 18px;
  background: #ffffff;
  border: 1px solid var(--app-border);
  box-shadow: var(--app-shadow-sm);
}

.workout-set-card__toolbar {
  margin-bottom: 10px;
  min-height: 36px;
}

.workout-set-card__badge {
  font-size: 0.7rem;
  font-weight: 700;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--app-text-muted);
}

.workout-set-card .row {
  min-width: 0;
}

.workout-set-card .col-6,
.workout-set-card .col-12 {
  min-width: 0;
}

.workout-set-card :deep(.q-field__native) {
  font-size: 16px;
}
</style>
