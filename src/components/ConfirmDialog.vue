<template>
  <Transition name="modal">
    <div v-if="isVisible" class="fixed inset-0 z-50 overflow-y-auto">
      <div class="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
        <!-- Overlay -->
        <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" @click="cancel"></div>

        <!-- Центрирование модального окна -->
        <span class="hidden sm:inline-block sm:align-middle sm:h-screen" aria-hidden="true">&#8203;</span>

        <!-- Модальное окно -->
        <div class="inline-block align-bottom bg-white dark:bg-gray-800 rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
          <div class="bg-white dark:bg-gray-800 px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
            <div class="sm:flex sm:items-start">
              <div class="mx-auto flex-shrink-0 flex items-center justify-center h-12 w-12 rounded-full sm:mx-0 sm:h-10 sm:w-10" :class="iconBgClass">
                <!-- Иконка предупреждения -->
                <svg v-if="type === 'warning'" class="h-6 w-6 text-yellow-600 dark:text-yellow-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
                </svg>
                <!-- Иконка опасности -->
                <svg v-else-if="type === 'danger'" class="h-6 w-6 text-red-600 dark:text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <!-- Иконка информации -->
                <svg v-else class="h-6 w-6 text-blue-600 dark:text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div class="mt-3 text-center sm:mt-0 sm:ml-4 sm:text-left w-full">
                <h3 class="text-lg leading-6 font-medium text-gray-900 dark:text-white" id="modal-title">
                  {{ title }}
                </h3>
                <div class="mt-2">
                  <p class="text-sm text-gray-500 dark:text-gray-400">
                    {{ message }}
                  </p>
                </div>
              </div>
            </div>
          </div>
          <div class="bg-gray-50 dark:bg-gray-700 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
            <button
              @click="confirm"
              :class="confirmButtonClass"
              class="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 text-base font-medium text-white focus:outline-none focus:ring-2 focus:ring-offset-2 sm:ml-3 sm:w-auto sm:text-sm"
            >
              {{ confirmText }}
            </button>
            <button
              @click="cancel"
              class="mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 dark:border-gray-600 shadow-sm px-4 py-2 bg-white dark:bg-gray-800 text-base font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 sm:mt-0 sm:ml-3 sm:w-auto sm:text-sm"
            >
              {{ cancelText }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </Transition>
</template>

<script>
import { ref, computed } from 'vue'

export default {
  name: 'ConfirmDialog',
  props: {
    isVisible: {
      type: Boolean,
      default: false
    },
    title: {
      type: String,
      default: 'Подтверждение'
    },
    message: {
      type: String,
      default: 'Вы уверены?'
    },
    type: {
      type: String,
      default: 'warning', // warning, danger, info
      validator: (value) => ['warning', 'danger', 'info'].includes(value)
    },
    confirmText: {
      type: String,
      default: 'Подтвердить'
    },
    cancelText: {
      type: String,
      default: 'Отмена'
    }
  },
  emits: ['confirm', 'cancel'],
  setup(props, { emit }) {
    const confirm = () => {
      emit('confirm')
    }

    const cancel = () => {
      emit('cancel')
    }

    const iconBgClass = computed(() => {
      switch (props.type) {
        case 'warning':
          return 'bg-yellow-100 dark:bg-yellow-900'
        case 'danger':
          return 'bg-red-100 dark:bg-red-900'
        case 'info':
        default:
          return 'bg-blue-100 dark:bg-blue-900'
      }
    })

    const confirmButtonClass = computed(() => {
      switch (props.type) {
        case 'warning':
          return 'bg-yellow-600 hover:bg-yellow-700 focus:ring-yellow-500'
        case 'danger':
          return 'bg-red-600 hover:bg-red-700 focus:ring-red-500'
        case 'info':
        default:
          return 'bg-blue-600 hover:bg-blue-700 focus:ring-blue-500'
      }
    })

    return {
      confirm,
      cancel,
      iconBgClass,
      confirmButtonClass
    }
  }
}
</script>

<style scoped>
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.3s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-active .bg-white,
.modal-leave-active .bg-white,
.modal-enter-active .bg-gray-800,
.modal-leave-active .bg-gray-800 {
  transition: transform 0.3s ease;
}

.modal-enter-from .bg-white,
.modal-leave-to .bg-white,
.modal-enter-from .bg-gray-800,
.modal-leave-to .bg-gray-800 {
  transform: scale(0.95);
}
</style>

