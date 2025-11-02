<template>
  <div class="fixed top-1 right-1 sm:top-2 sm:right-2 md:top-4 md:right-4 z-50 space-y-1 sm:space-y-2 max-w-xs sm:max-w-sm w-full pointer-events-none sm:pointer-events-auto">
    <TransitionGroup name="notification" tag="div">
      <div
        v-for="notification in notifications"
        :key="notification.id"
        :class="[
          'w-full bg-white dark:bg-gray-800 shadow-lg rounded-lg pointer-events-auto ring-1 ring-black ring-opacity-5 overflow-hidden',
          getNotificationClasses(notification.type)
        ]"
      >
        <div class="p-3 sm:p-4">
          <div class="flex items-start">
            <div class="flex-shrink-0">
              <!-- Иконка успеха -->
              <svg v-if="notification.type === 'success'" class="h-5 w-5 sm:h-6 sm:w-6 text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <!-- Иконка ошибки -->
              <svg v-else-if="notification.type === 'error'" class="h-5 w-5 sm:h-6 sm:w-6 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <!-- Иконка предупреждения -->
              <svg v-else-if="notification.type === 'warning'" class="h-5 w-5 sm:h-6 sm:w-6 text-yellow-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
              </svg>
              <!-- Иконка информации -->
              <svg v-else class="h-5 w-5 sm:h-6 sm:w-6 text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div class="ml-2 sm:ml-3 flex-1 min-w-0">
              <p class="text-xs sm:text-sm font-medium text-gray-900 dark:text-white break-words">
                {{ notification.title }}
              </p>
              <p v-if="notification.message" class="mt-1 text-xs sm:text-sm text-gray-500 dark:text-gray-400 break-words">
                {{ notification.message }}
              </p>
            </div>
            <div class="ml-2 flex-shrink-0 flex">
              <button
                @click="removeNotification(notification.id)"
                class="bg-white dark:bg-gray-800 rounded-md inline-flex text-gray-400 hover:text-gray-500 dark:hover:text-gray-300 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 p-1"
              >
                <span class="sr-only">Закрыть</span>
                <svg class="h-4 w-4 sm:h-5 sm:w-5" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
                </svg>
              </button>
            </div>
          </div>
        </div>
        <!-- Прогресс-бар для автозакрытия -->
        <div v-if="notification.autoClose" class="h-1 bg-gray-200 dark:bg-gray-700">
          <div
            class="h-1 bg-current transition-all duration-1000 ease-linear"
            :class="getProgressBarClass(notification.type)"
            :style="{ width: `${notification.progress}%` }"
          ></div>
        </div>
      </div>
    </TransitionGroup>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted } from 'vue'

export default {
  name: 'NotificationSystem',
  setup() {
    const notifications = ref([])
    const timers = new Map()

    const getNotificationClasses = (type) => {
      const baseClasses = 'border-l-4'
      switch (type) {
        case 'success':
          return `${baseClasses} border-green-400`
        case 'error':
          return `${baseClasses} border-red-400`
        case 'warning':
          return `${baseClasses} border-yellow-400`
        case 'info':
        default:
          return `${baseClasses} border-blue-400`
      }
    }

    const getProgressBarClass = (type) => {
      switch (type) {
        case 'success':
          return 'text-green-400'
        case 'error':
          return 'text-red-400'
        case 'warning':
          return 'text-yellow-400'
        case 'info':
        default:
          return 'text-blue-400'
      }
    }

    const addNotification = (notification) => {
      const id = Date.now() + Math.random()
      const newNotification = {
        id,
        type: notification.type || 'info',
        title: notification.title,
        message: notification.message,
        autoClose: notification.autoClose !== false,
        duration: notification.duration || 5000,
        progress: 100
      }

      if (notifications.value.length >= 3) {
        const oldest = notifications.value.shift()
        if (timers.has(oldest.id)) {
          clearInterval(timers.get(oldest.id))
          timers.delete(oldest.id)
        }
      }

      notifications.value.push(newNotification)

      if (newNotification.autoClose) {
        startAutoClose(newNotification)
      }
    }

    const removeNotification = (id) => {
      const index = notifications.value.findIndex(n => n.id === id)
      if (index > -1) {
        notifications.value.splice(index, 1)
      }
      
      if (timers.has(id)) {
        clearInterval(timers.get(id))
        timers.delete(id)
      }
    }

    const startAutoClose = (notification) => {
      const startTime = Date.now()
      const updateInterval = 50
      
      const timer = setInterval(() => {
        const elapsed = Date.now() - startTime
        const remaining = Math.max(0, notification.duration - elapsed)
        const progress = (remaining / notification.duration) * 100
        
        const notificationIndex = notifications.value.findIndex(n => n.id === notification.id)
        if (notificationIndex > -1) {
          notifications.value[notificationIndex].progress = progress
        }
        
        if (remaining <= 0) {
          removeNotification(notification.id)
        }
      }, updateInterval)
      
      timers.set(notification.id, timer)
    }

    const showSuccess = (title, message = '') => {
      addNotification({ type: 'success', title, message })
    }

    const showError = (title, message = '') => {
      addNotification({ type: 'error', title, message })
    }

    const showWarning = (title, message = '') => {
      addNotification({ type: 'warning', title, message })
    }

    const showInfo = (title, message = '') => {
      addNotification({ type: 'info', title, message })
    }

    onMounted(() => {
      window.$notify = {
        success: showSuccess,
        error: showError,
        warning: showWarning,
        info: showInfo
      }
    })

    onUnmounted(() => {
      timers.forEach(timer => clearInterval(timer))
      timers.clear()
      
      delete window.$notify
    })

    return {
      notifications,
      removeNotification,
      getNotificationClasses,
      getProgressBarClass
    }
  }
}
</script>

<style scoped>
.notification-enter-active,
.notification-leave-active {
  transition: all 0.3s ease;
}

.notification-enter-from {
  opacity: 0;
  transform: translateX(100%);
}

.notification-leave-to {
  opacity: 0;
  transform: translateX(100%);
}

.notification-move {
  transition: transform 0.3s ease;
}

@media (max-width: 320px) {
  .fixed {
    top: 0.25rem !important;
    right: 0.25rem !important;
    left: 0.25rem !important;
    max-width: none !important;
    width: auto !important;
  }
}

@media (max-width: 480px) {
  .fixed {
    max-width: calc(100vw - 1rem) !important;
    right: 0.5rem !important;
    left: 0.5rem !important;
    width: auto !important;
  }
}

@media (max-width: 640px) {
  .fixed {
    max-width: calc(100vw - 2rem) !important;
  }
}
</style>
