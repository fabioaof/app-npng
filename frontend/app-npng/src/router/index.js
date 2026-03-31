import { defineRouter } from '#q-app/wrappers'
import { createRouter, createMemoryHistory, createWebHistory, createWebHashHistory } from 'vue-router'
import routes from './routes'
import { useAuthStore } from 'src/stores/auth'

export default defineRouter(function (/* { store, ssrContext } */) {
  const createHistory = process.env.SERVER
    ? createMemoryHistory
    : (process.env.VUE_ROUTER_MODE === 'history' ? createWebHistory : createWebHashHistory)

  const Router = createRouter({
    scrollBehavior: () => ({ left: 0, top: 0 }),
    routes,
    history: createHistory(process.env.VUE_ROUTER_BASE),
  })

  Router.beforeEach(async (to, from, next) => {
    const auth = useAuthStore()

    if (to.meta.requiresAuth && !auth.token) {
      return next({ name: 'login', query: { redirect: to.fullPath } })
    }
    if (to.meta.guestOnly && auth.token) {
      return next({ name: 'dashboard' })
    }

    if (auth.token && !auth.user) {
      try {
        await auth.fetchMe()
      } catch {
        auth.logout()
        if (to.meta.requiresAuth) {
          return next({ name: 'login', query: { redirect: to.fullPath } })
        }
      }
    }

    if (to.meta.professionalOnly && auth.user && auth.user.role !== 'professional') {
      return next({ name: 'dashboard' })
    }

    next()
  })

  return Router
})
