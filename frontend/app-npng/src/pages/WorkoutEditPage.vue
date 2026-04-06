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
            @click="router.push({ name: 'workouts' })"
          />
          <div class="col min-width-0 q-pl-xs">
            <div class="text-h6 text-weight-bold ellipsis" style="letter-spacing: -0.02em">
              {{ isNew ? 'Novo treino' : (title || 'Treino') }}
            </div>
          </div>
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
          Seleciona um aluno no topo antes de registar o treino.
        </q-banner>

        <q-form @submit="onSave" class="workout-edit-form">
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

          <div class="text-subtitle2 text-weight-bold text-grey-9 q-mb-sm">Exercícios</div>

          <div
            v-if="!blocks.length"
            class="text-body2 text-grey-7 q-mb-md workout-edit-empty"
          >
            Ainda não há exercícios. Clica em «Adicionar exercício».
          </div>

          <div
            v-for="(block, bIdx) in blocks"
            :key="block.id"
            class="workout-block q-mb-lg"
          >
            <div class="workout-block__head row items-center justify-between q-mb-sm">
              <span class="workout-block__label">Exercício {{ bIdx + 1 }}</span>
              <q-btn
                flat
                dense
                no-caps
                color="grey-7"
                icon="close"
                label="Remover"
                rounded
                @click="removeBlock(bIdx)"
              />
            </div>

            <div class="workout-exercise-title text-subtitle1 text-weight-bold text-grey-9 q-mb-sm">
              {{ exerciseName(block.exercise_id) }}
            </div>

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

          <div class="row q-col-gutter-xs q-mt-md q-mb-lg">
            <div v-if="blocks.length" class="col-6">
              <q-btn
                outline
                no-caps
                color="grey-8"
                label="Adicionar set"
                rounded
                class="workout-add-btn"
                @click="addSetToLastBlock"
              />
            </div>
            <div :class="blocks.length ? 'col-6' : 'col-12'">
              <q-btn
                outline
                no-caps
                color="grey-8"
                label="Adicionar exercício"
                rounded
                class="workout-add-btn"
                @click="openExerciseDialog"
              />
            </div>
          </div>

          <div class="row q-gutter-sm q-mt-md items-center justify-end">
            <q-btn flat no-caps rounded color="grey-8" label="Cancelar" :to="{ name: 'workouts' }" />
            <q-btn v-if="!isNew" flat no-caps rounded label="Apagar" color="negative" @click="onDelete" />
            <q-btn
              type="submit"
              unelevated
              no-caps
              color="primary"
              padding="sm md"
              rounded
              label="Guardar treino"
              :loading="saving"
            />
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
  </q-page>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Dialog, Notify } from 'quasar'
import { api } from 'src/api/client'
import { useAuthStore } from 'src/stores/auth'
import { useProfessionalStore } from 'src/stores/professional'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const prof = useProfessionalStore()

const isNew = computed(() => route.name === 'workout-new')
const sessionId = computed(() => route.params.id)

const fromAppointmentId = computed(() => {
  const v = route.query.from_appointment
  if (v == null) return null
  const n = Number(v)
  return Number.isFinite(n) && n > 0 ? n : null
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
const performedAtLocal = ref('')
const title = ref('')
const notes = ref('')
/** @type {import('vue').Ref<Array<{ id: number, exercise_id: number, sets: Array<{ weight_kg: number, reps: number, rest_seconds: number | null }> }>>} */
const blocks = ref([])
const exercises = ref([])

const exerciseDialogOpen = ref(false)
const dialogExerciseId = ref(null)

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

function defaultSetRow () {
  return {
    weight_kg: 0,
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
  blocks.value.push(createBlock(dialogExerciseId.value))
  exerciseDialogOpen.value = false
  dialogExerciseId.value = null
}

function addSetToBlock (block) {
  block.sets.push(defaultSetRow())
}

function addSetToLastBlock () {
  if (!blocks.value.length) {
    Notify.create({
      type: 'info',
      message: 'Adiciona primeiro um exercício.',
      position: 'top',
    })
    return
  }
  addSetToBlock(blocks.value[blocks.value.length - 1])
}

function removeSetFromBlock (block, idx) {
  if (block.sets.length <= 1) return
  block.sets.splice(idx, 1)
}

function removeBlock (idx) {
  blocks.value.splice(idx, 1)
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
    }
    ready.value = true
    return
  }
  const { data } = await api.get(`/workouts/sessions/${sessionId.value}`)
  performedAtLocal.value = data.performed_at.slice(0, 16)
  title.value = data.title || ''
  notes.value = data.notes || ''
  blockIdSeq = 0
  blocks.value = sessionSetsToBlocks(data.sets || [])
  ready.value = true
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
    cancel: true,
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
</script>

<style scoped>
.workout-edit-inner {
  padding-bottom: env(safe-area-inset-bottom, 12px);
}

.workout-edit-top {
  margin-top: env(safe-area-inset-top, 0px);
}

.min-width-0 {
  min-width: 0;
}

.workout-add-btn {
  width: 100%;
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
