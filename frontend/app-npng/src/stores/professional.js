import { defineStore } from 'pinia'

export const useProfessionalStore = defineStore('professional', {
  state: () => ({
    selectedStudentId: null,
  }),
  actions: {
    setSelectedStudent (id) {
      this.selectedStudentId = id
    },
  },
})
