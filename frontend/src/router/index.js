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
      path: '/slates',
      name: 'Slates',
      component: () => import('../views/SlatesView.vue')
    },
    {
      path: '/scrapers',
      name: 'Scrapers',
      component: () => import('../views/ScrapersView.vue')
    },
    {
      path: '/optimizer',
      name: 'optimizer',
      component: () => import('../views/OptimizerView.vue')
    },
    {
      path: '/optimizerdk',
      name: 'optimizerdk',
      component: () => import('../views/OptimizerDKView.vue')
    },
    {
      path: '/optimizernew',
      name: 'optimizernew',
      component: () => import('../views/OptimizerViewNew.vue')
    },
    {
      path: '/results',
      name: 'results',
      component: () => import('../views/ResultsView.vue')
    },
    {
      path: '/backtester',
      name: 'backtester',
      component: () => import('../views/BacktesterView.vue')
    }
  ]
})

export default router
