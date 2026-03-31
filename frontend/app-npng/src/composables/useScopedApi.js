import { computed } from 'vue'
import { useAuthStore } from 'src/stores/auth'
import { useProfessionalStore } from 'src/stores/professional'

export function useScopedApi () {
  const auth = useAuthStore()
  const prof = useProfessionalStore()

  const scopedParams = computed(() => {
    if (auth.isProfessional && prof.selectedStudentId) {
      return { user_id: prof.selectedStudentId }
    }
    return {}
  })

  return { scopedParams }
}
