import './assets/main.css'
import 'floating-vue/dist/style.css'

import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import FloatingVue from 'floating-vue'

import VueDatePicker from '@vuepic/vue-datepicker';
import '@vuepic/vue-datepicker/dist/main.css'

const app = createApp(App)

app.use(router)
app.use(FloatingVue)
app.component('VueDatePicker', VueDatePicker);

app.mount('#app')
