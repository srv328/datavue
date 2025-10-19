<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900 transition-colors">
    <!-- Навигационная панель -->
    <nav class="bg-white dark:bg-gray-800 shadow-sm border-b border-gray-200 dark:border-gray-700">
			<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
				<div class="flex justify-between h-16">
					<div class="flex items-center">
            <h1 class="text-lg sm:text-xl font-bold text-gray-900 dark:text-white">
              DataVue
            </h1>
          </div>
          
          <div class="flex items-center space-x-2 sm:space-x-4">
            <!-- Переключатель темы -->
            <button
              @click="toggleDarkMode"
              class="p-2 rounded-md text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
            >
              <svg v-if="!darkMode" class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M10 2a1 1 0 011 1v1a1 1 0 11-2 0V3a1 1 0 011-1zm4 8a4 4 0 11-8 0 4 4 0 018 0zm-.464 4.95l.707.707a1 1 0 001.414-1.414l-.707-.707a1 1 0 00-1.414 1.414zm2.12-10.607a1 1 0 010 1.414l-.706.707a1 1 0 11-1.414-1.414l.707-.707a1 1 0 011.414 0zM17 11a1 1 0 100-2h-1a1 1 0 100 2h1zm-7 4a1 1 0 011 1v1a1 1 0 11-2 0v-1a1 1 0 011-1zM5.05 6.464A1 1 0 106.465 5.05l-.708-.707a1 1 0 00-1.414 1.414l.707.707zm1.414 8.486l-.707.707a1 1 0 01-1.414-1.414l.707-.707a1 1 0 011.414 1.414zM4 11a1 1 0 100-2H3a1 1 0 000 2h1z" clip-rule="evenodd"></path>
              </svg>
              <svg v-else class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path d="M17.293 13.293A8 8 0 016.707 2.707a8.001 8.001 0 1010.586 10.586z"></path>
              </svg>
            </button>
            
            <!-- Информация о пользователе -->
            <div v-if="currentUser" class="flex items-center space-x-2 sm:space-x-3">
              <div class="hidden sm:block">
                <span class="text-sm text-gray-700 dark:text-gray-300">
                  {{ currentUser.username }}
                  <span class="ml-1 px-2 py-1 text-xs bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 rounded">
                    {{ currentUser.role === 'admin' ? 'Админ' : 'Пользователь' }}
                  </span>
                </span>
						</div>
              <div class="sm:hidden">
                <span class="text-sm text-gray-700 dark:text-gray-300">
                  {{ currentUser.username }}
                </span>
					</div>
              <button
                @click="logout"
                class="text-sm text-red-600 hover:text-red-800 dark:text-red-400 dark:hover:text-red-200 px-2 py-1 rounded hover:bg-red-50 dark:hover:bg-red-900"
              >
                Выйти
						</button>
            </div>
					</div>
				</div>
			</div>
		</nav>

    <!-- Основной контент -->
    <main class="max-w-7xl mx-auto py-4 px-2 sm:px-4 lg:px-8">
      <!-- Форма настройки администратора -->
      <div v-if="!currentUser && !adminSetup" class="max-w-md mx-auto">
        <div class="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
          <h2 class="text-2xl font-bold text-gray-900 dark:text-white mb-6 text-center">
            Настройка администратора
          </h2>
          <p class="text-sm text-gray-600 dark:text-gray-400 mb-6 text-center">
            Настройте учетные данные администратора для первого входа в систему
          </p>
          
          <form @submit.prevent="setupAdmin" class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Имя пользователя
              </label>
              <input
                v-model="adminForm.username"
                type="text"
                required
                class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
                placeholder="Введите имя пользователя"
              >
            </div>
            
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Пароль
              </label>
              <input
                v-model="adminForm.password"
                type="password"
                required
                class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
                placeholder="Введите пароль"
              >
            </div>
            
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Полное имя (необязательно)
              </label>
              <input
                v-model="adminForm.full_name"
                type="text"
                class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
                placeholder="Введите полное имя"
              >
            </div>
            
            <div v-if="error" class="mt-4 p-3 bg-red-100 dark:bg-red-900 border border-red-400 text-red-700 dark:text-red-200 rounded">
              {{ error }}
            </div>
            
            <button
              type="submit"
              :disabled="loading"
              class="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
            >
              {{ loading ? 'Создание...' : 'Создать администратора' }}
            </button>
          </form>
        </div>
      </div>

      <!-- Форма входа -->
      <div v-if="!currentUser && adminSetup" class="max-w-md mx-auto">
        <div class="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
          <h2 class="text-2xl font-bold text-gray-900 dark:text-white mb-6 text-center">
            Вход в систему
          </h2>
          
          <form @submit.prevent="login" class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Имя пользователя
              </label>
              <input
                v-model="loginForm.username"
                type="text"
                required
                class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
                placeholder="Введите имя пользователя"
              >
            </div>
            
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Пароль
              </label>
              <input
                v-model="loginForm.password"
                type="password"
                required
                class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
                placeholder="Введите пароль"
              >
            </div>
            
            <button
              type="submit"
              :disabled="loading"
              class="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
            >
              {{ loading ? 'Вход...' : 'Войти' }}
            </button>
          </form>
          
          <div v-if="error" class="mt-4 p-3 bg-red-100 dark:bg-red-900 border border-red-400 text-red-700 dark:text-red-200 rounded">
            {{ error }}
          </div>
          
						</div>
					</div>

      <!-- Интерфейс приложения -->
      <div v-else>
        <!-- Вкладки -->
        <div class="border-b border-gray-200 dark:border-gray-700 mb-4 sm:mb-6">
          <nav class="-mb-px flex space-x-4 sm:space-x-8 overflow-x-auto">
            <button
              v-for="tab in availableTabs"
              :key="tab.id"
              @click="activeTab = tab.id"
              :class="[
                activeTab === tab.id
                  ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300',
                'whitespace-nowrap py-2 px-1 border-b-2 font-medium text-sm flex-shrink-0'
              ]"
            >
              {{ tab.name }}
								</button>
							</nav>
						</div>

        <!-- Контент вкладок -->
        <div v-if="activeTab === 'data'" class="space-y-6">
          <DataManagement />
					</div>
        
        <div v-if="activeTab === 'analysis'" class="space-y-6">
          <AnalysisPanel />
					</div>
        
        <div v-if="activeTab === 'admin'" class="space-y-6">
          <AdminPanel v-if="currentUser.role === 'admin'" />
          <div v-else class="text-center py-8 text-gray-500 dark:text-gray-400">
            У вас нет прав доступа к панели администратора
					</div>
				</div>
			</div>
		</main>
    
    <!-- Система уведомлений -->
    <NotificationSystem />
    
    <!-- Система модальных окон -->
    <ModalSystem />
	</div>
</template>

<script>
import { ref, onMounted, computed } from 'vue'
import DataManagement from './components/DataManagement.vue'
import AdminPanel from './components/AdminPanel.vue'
import AnalysisPanel from './components/AnalysisPanel.vue'
import NotificationSystem from './components/NotificationSystem.vue'
import ModalSystem from './components/ModalSystem.vue'

export default {
  name: 'App',
  components: {
    DataManagement,
    AdminPanel,
    AnalysisPanel,
    NotificationSystem,
    ModalSystem
  },
  setup() {
    const currentUser = ref(null)
    const loading = ref(false)
    const error = ref('')
    const activeTab = ref('analysis')
    const darkMode = ref(false)
    const adminSetup = ref(true) // По умолчанию считаем, что админ настроен
    
    const loginForm = ref({
      username: '',
      password: ''
    })
    
    const adminForm = ref({
      username: '',
      password: '',
      full_name: ''
    })
    
    const availableTabs = computed(() => {
      const tabs = [
        { id: 'analysis', name: 'Анализ' },
        { id: 'data', name: 'Данные' }
      ]
      
      if (currentUser.value?.role === 'admin') {
        tabs.push({ id: 'admin', name: 'Администрирование' })
      }
      
      return tabs
    })
    
    const login = async () => {
      loading.value = true
      error.value = ''
      
      try {
        const response = await fetch('http://localhost:5000/api/auth/login', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          credentials: 'include',
          body: JSON.stringify(loginForm.value)
        })
        
        const data = await response.json()
        
        if (response.ok) {
          currentUser.value = data.user
          activeTab.value = 'data'
        } else {
          error.value = data.error || 'Ошибка входа'
          window.$notify?.error('Ошибка входа', data.error || 'Неверные учетные данные')
        }
      } catch (err) {
        error.value = 'Ошибка соединения с сервером'
        window.$notify?.error('Ошибка соединения', 'Не удалось подключиться к серверу')
      } finally {
        loading.value = false
      }
    }
    
    const setupAdmin = async () => {
      loading.value = true
      error.value = ''
      
      try {
        const response = await fetch('http://localhost:5000/api/admin/setup', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          credentials: 'include',
          body: JSON.stringify(adminForm.value)
        })
        
        const data = await response.json()
        
        if (response.ok) {
          adminSetup.value = true
          // Автоматически входим после создания администратора
          loginForm.value.username = adminForm.value.username
          loginForm.value.password = adminForm.value.password
          await login()
        } else {
          error.value = data.error || 'Ошибка создания администратора'
        }
      } catch (err) {
        console.error('Ошибка создания администратора:', err)
        error.value = 'Ошибка соединения с сервером'
      } finally {
        loading.value = false
      }
    }
    
    const checkAdminSetup = async () => {
      try {
        const response = await fetch('http://localhost:5000/api/admin/check-setup', {
          credentials: 'include'
        })
        
        if (response.ok) {
          const data = await response.json()
          adminSetup.value = data.is_setup
        }
      } catch (err) {
        console.error('Ошибка проверки настройки администратора:', err)
      }
    }
    
    const logout = async () => {
      try {
        await fetch('http://localhost:5000/api/auth/logout', {
          method: 'POST',
          credentials: 'include'
        })
      } catch (err) {
        console.error('Ошибка выхода:', err)
      } finally {
        currentUser.value = null
        activeTab.value = 'data'
      }
    }
    
    const toggleDarkMode = () => {
      darkMode.value = !darkMode.value
      document.documentElement.classList.toggle('dark', darkMode.value)
    }
    
    const checkAuth = async () => {
      try {
        const response = await fetch('http://localhost:5000/api/auth/me', {
          credentials: 'include'
        })
        
        if (response.ok) {
          const data = await response.json()
          currentUser.value = data
        }
      } catch (err) {
        console.error('Ошибка проверки аутентификации:', err)
      }
    }
    
    onMounted(async () => {
      await checkAdminSetup()
      checkAuth()
      
      // Проверяем сохраненную тему
      const savedTheme = localStorage.getItem('darkMode')
      if (savedTheme === 'true') {
        darkMode.value = true
        document.documentElement.classList.add('dark')
      }
    })
    
    return {
      currentUser,
      loading,
      error,
      activeTab,
      darkMode,
      adminSetup,
      loginForm,
      adminForm,
      availableTabs,
      login,
      logout,
      setupAdmin,
      checkAdminSetup,
      toggleDarkMode
    }
  }
}
</script>