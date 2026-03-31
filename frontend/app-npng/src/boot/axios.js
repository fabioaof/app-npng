import { defineBoot } from '#q-app/wrappers'
import axios from 'axios'
import { api } from 'src/api/client'

export default defineBoot(({ app }) => {
  app.config.globalProperties.$axios = axios
  app.config.globalProperties.$api = api
})

export { api }
