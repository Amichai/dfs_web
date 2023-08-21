import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView
    },
    {
      path: '/upload',
      name: 'Upload',
      component: () => import('../views/UploadView.vue')
    },
    {
      path: '/players',
      name: 'players',
      component: () => import('../views/PlayersView.vue')
    },
    {
      path: '/optimizer',
      name: 'optimizer',
      component: () => import('../views/OptimizerView.vue')
    },
    {
      path: '/backtester',
      name: 'backtester',
      component: () => import('../views/BacktesterView.vue')
    }
  ]
})

export default router
