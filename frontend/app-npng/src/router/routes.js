const routes = [
  {
    path: '/login',
    component: () => import('layouts/AuthLayout.vue'),
    meta: { guestOnly: true },
    children: [
      { path: '', name: 'login', component: () => import('pages/LoginPage.vue') },
    ],
  },
  {
    path: '/register',
    component: () => import('layouts/AuthLayout.vue'),
    meta: { guestOnly: true },
    children: [
      { path: '', name: 'register', component: () => import('pages/RegisterPage.vue') },
    ],
  },
  {
    path: '/',
    component: () => import('layouts/MainLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      { path: '', name: 'home', redirect: { name: 'dashboard' } },
      {
        path: 'dashboard',
        name: 'dashboard',
        component: () => import('pages/DashboardPage.vue'),
      },
      {
        path: 'workouts',
        name: 'workouts',
        component: () => import('pages/WorkoutsListPage.vue'),
      },
      {
        path: 'workouts/new',
        name: 'workout-new',
        component: () => import('pages/WorkoutEditPage.vue'),
      },
      {
        path: 'workouts/:id',
        name: 'workout-detail',
        component: () => import('pages/WorkoutEditPage.vue'),
      },
      {
        path: 'exercises',
        name: 'exercises',
        component: () => import('pages/ExercisesPage.vue'),
      },
      {
        path: 'calendar',
        name: 'calendar',
        component: () => import('pages/CalendarPage.vue'),
      },
      {
        path: 'profile',
        name: 'profile',
        component: () => import('pages/ProfilePage.vue'),
      },
      {
        path: 'professional/students',
        name: 'professional-students',
        meta: { professionalOnly: true },
        component: () => import('pages/ProfessionalStudentsPage.vue'),
      },
    ],
  },
  {
    path: '/:catchAll(.*)*',
    component: () => import('pages/ErrorNotFound.vue'),
  },
]

export default routes
