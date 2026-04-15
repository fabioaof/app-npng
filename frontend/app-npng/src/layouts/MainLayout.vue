<template>
  <q-layout view="lhh Lpr lFf" class="bg-transparent">
    <q-page-container class="bg-transparent">
      <router-view />
    </q-page-container>

    <q-footer bordered class="app-footer-nav bg-white">
      <div v-if="auth.isProfessional && students.length" class="app-student-strip">
        <q-select
          v-model="selectedStudentId"
          class="full-width app-student-strip__select"
          :options="studentOptions"
          dense
          outlined
          emit-value
          map-options
          label="Aluno"
          color="grey-8"
          bg-color="white"
          rounded
        />
      </div>
      <q-tabs
        dense
        indicator-color="transparent"
        active-color="primary"
        class="app-footer-tabs text-grey-7"
        align="justify"
        stretch
        outside-arrows
        mobile-arrows
      >
        <q-route-tab
          v-for="link in navLinksWithoutProfile"
          :key="link.to"
          :to="link.to"
          no-caps
        >
          <div class="column items-center no-wrap">
            <template v-if="link.to === '/dashboard'">
              <img :src="npngIcon" alt="Início" class="app-tab-home__icon">
            </template>
            <template v-else>
              <q-icon :name="link.icon" size="22px" />
              <span class="app-footer-tabs__label">{{ link.shortLabel }}</span>
            </template>
          </div>
        </q-route-tab>
        <q-route-tab :to="{ name: 'profile' }" no-caps class="app-tab-profile">
          <div class="column items-center no-wrap app-tab-profile__inner">
            <q-avatar
              size="28px"
              rounded
              color="grey-4"
              text-color="grey-8"
              class="app-tab-profile__avatar"
            >
              <img v-if="profile?.photo_url" :src="profile.photo_url" alt="">
              <span v-else class="text-weight-bold" style="font-size: 0.65rem">{{ initials }}</span>
            </q-avatar>
            <span class="app-tab-profile__label">Perfil</span>
          </div>
        </q-route-tab>
      </q-tabs>
    </q-footer>
  </q-layout>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { storeToRefs } from 'pinia'
import { useRoute } from 'vue-router'
import { useAuthStore } from 'src/stores/auth'
import { useProfessionalStore } from 'src/stores/professional'
import { api } from 'src/api/client'
import npngIcon from 'src/assets/npng-icon.png'

const route = useRoute()
const auth = useAuthStore()
const prof = useProfessionalStore()
const { selectedStudentId } = storeToRefs(prof)
const students = ref([])
const profile = ref(null)

const navLinks = computed(() => {
  const base = [
    { label: 'Dashboard', shortLabel: 'Início', to: '/dashboard', icon: 'insights' },
    { label: 'Treinos', shortLabel: 'Treinos', to: '/workouts', icon: 'fitness_center' },
    { label: 'Calendário', shortLabel: 'Agenda', to: '/calendar', icon: 'calendar_month' },
    { label: 'Exercícios', shortLabel: 'Exercícios', to: '/exercises', icon: 'sports_gymnastics' },
    { label: 'Perfil', shortLabel: 'Perfil', to: '/profile', icon: 'person' },
  ]
  if (auth.isProfessional) {
    base.splice(1, 0, { label: 'Alunos', shortLabel: 'Alunos', to: '/professional/students', icon: 'groups' })
  }
  return base
})

const navLinksWithoutProfile = computed(() =>
  navLinks.value.filter((l) => l.to !== '/profile'),
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

async function loadProfile () {
  try {
    const { data } = await api.get('/profiles/me')
    profile.value = data
  } catch {
    profile.value = null
  }
}

async function loadStudents () {
  if (!auth.isProfessional) return
  try {
    const { data } = await api.get('/professional/students')
    students.value = data || []
  } catch {
    students.value = []
  } finally {
    ensureStudentSelectedIfRequired()
  }
}

function ensureStudentSelectedIfRequired () {
  if (!auth.isProfessional) return
  const isCalendar = route.name === 'calendar' || String(route.path || '').startsWith('/calendar')
  if (isCalendar) return
  if (selectedStudentId.value != null) return
  if (sortedStudents.value.length) {
    selectedStudentId.value = sortedStudents.value[0].user?.id ?? null
  }
}

watch(
  () => route.name,
  (n, prev) => {
    if (prev === 'profile' && n !== 'profile') loadProfile()
    // Ao sair da Agenda, se ficou sem aluno selecionado, repõe automaticamente
    ensureStudentSelectedIfRequired()
  },
)

onMounted(() => {
  loadProfile()
  loadStudents()
})
watch(() => auth.user?.role, loadStudents)
watch(selectedStudentId, (id) => {
  if (!auth.isProfessional) return
  if (id != null) return
  ensureStudentSelectedIfRequired()
})
</script>

<style scoped>
.app-footer-tabs__label {
  font-size: 0.7rem;
  line-height: 1;
  margin-top: 4px;
}

.app-tab-home__icon {
  width: 50px;
  height: 50px;
  object-fit: contain;
  margin-top: 2px;
}
</style>
