<template>
  <div>
    <!-- Модальное окно подтверждения -->
    <ConfirmDialog
      :is-visible="confirmDialog.visible"
      :title="confirmDialog.title"
      :message="confirmDialog.message"
      :type="confirmDialog.type"
      :confirm-text="confirmDialog.confirmText"
      :cancel-text="confirmDialog.cancelText"
      @confirm="handleConfirm"
      @cancel="handleCancel"
    />
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted } from 'vue'
import ConfirmDialog from './ConfirmDialog.vue'

export default {
  name: 'ModalSystem',
  components: {
    ConfirmDialog
  },
  setup() {
    const confirmDialog = ref({
      visible: false,
      title: 'Подтверждение',
      message: 'Вы уверены?',
      type: 'warning',
      confirmText: 'Подтвердить',
      cancelText: 'Отмена',
      resolve: null
    })

    const showConfirm = (options) => {
      return new Promise((resolve) => {
        confirmDialog.value = {
          visible: true,
          title: options.title || 'Подтверждение',
          message: options.message || 'Вы уверены?',
          type: options.type || 'warning',
          confirmText: options.confirmText || 'Подтвердить',
          cancelText: options.cancelText || 'Отмена',
          resolve
        }
      })
    }

    const handleConfirm = () => {
      confirmDialog.value.visible = false
      if (confirmDialog.value.resolve) {
        confirmDialog.value.resolve(true)
      }
    }

    const handleCancel = () => {
      confirmDialog.value.visible = false
      if (confirmDialog.value.resolve) {
        confirmDialog.value.resolve(false)
      }
    }

    onMounted(() => {
      window.$modal = {
        confirm: showConfirm
      }
    })

    onUnmounted(() => {
      delete window.$modal
    })

    return {
      confirmDialog,
      handleConfirm,
      handleCancel
    }
  }
}
</script>

