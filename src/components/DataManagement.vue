<template>
  <div class="space-y-6">
    <!-- Выбор типа данных -->
    <div class="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
      <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-4">
        Выберите тип данных для редактирования
      </h3>
      
      <div v-if="loading" class="text-center py-4">
        <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <p class="mt-2 text-gray-600 dark:text-gray-400">Загрузка...</p>
      </div>
      
      <div v-else-if="dataTypes.length === 0" class="text-center py-8">
        <div class="flex flex-col items-center">
          <svg class="h-12 w-12 text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"></path>
          </svg>
          <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-2">
            Нет доступных типов данных для редактирования
          </h3>
          <p class="text-gray-500 dark:text-gray-400 mb-4">
            У вас нет прав на редактирование ни одного типа данных. Обратитесь к администратору для получения доступа.
          </p>
          <p class="text-sm text-gray-400 dark:text-gray-500">
            Для просмотра и анализа данных используйте вкладку "Анализ"
          </p>
        </div>
      </div>
      
      <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          <div
            v-for="dataType in dataTypes"
            :key="dataType.id"
            @click="selectDataType(dataType)"
          :class="[
            selectedDataType?.id === dataType.id
              ? 'ring-2 ring-blue-500 bg-blue-50 dark:bg-blue-900'
              : 'hover:bg-gray-50 dark:hover:bg-gray-700',
            'p-4 border border-gray-200 dark:border-gray-600 rounded-lg cursor-pointer transition-colors'
          ]"
        >
          <h4 class="font-medium text-gray-900 dark:text-white">
            {{ dataType.name }}
          </h4>
          <p class="text-sm text-gray-600 dark:text-gray-400 mt-1">
            {{ dataType.description }}
          </p>
          <div class="mt-2 text-xs text-gray-500 dark:text-gray-500">
            Создано: {{ formatDate(dataType.created_at) }}
          </div>
        </div>
      </div>
    </div>

    <!-- Работа с выбранным типом данных -->
    <div v-if="selectedDataType" class="space-y-6">
      <!-- Информация о полях -->
      <div class="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
        <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-4">
          Поля данных: {{ selectedDataType.name }}
        </h3>
        
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          <div
            v-for="field in dataFields"
            :key="field.id"
            class="p-3 border border-gray-200 dark:border-gray-600 rounded-lg"
          >
            <div class="flex items-center justify-between">
              <span class="font-medium text-gray-900 dark:text-white">
                {{ field.field_name }}
              </span>
              <span class="text-xs px-2 py-1 bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 rounded">
                {{ getFieldTypeName(field.field_type) }}
              </span>
            </div>
            <p v-if="field.description" class="text-sm text-gray-600 dark:text-gray-400 mt-1">
              {{ field.description }}
            </p>
            <div v-if="field.is_required" class="text-xs text-red-600 dark:text-red-400 mt-1">
              Обязательное поле
            </div>
          </div>
        </div>
      </div>

      <!-- Форма добавления данных -->
      <div class="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
        <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-4">
          Добавить новую запись
        </h3>
        
        <!-- Сообщение о том, что нет полей -->
        <div v-if="!hasFields" class="bg-yellow-50 dark:bg-yellow-900 border border-yellow-200 dark:border-yellow-700 rounded-lg p-4 mb-4">
          <div class="flex">
            <div class="flex-shrink-0">
              <svg class="h-5 w-5 text-yellow-400" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
              </svg>
            </div>
            <div class="ml-3">
              <h3 class="text-sm font-medium text-yellow-800 dark:text-yellow-200">
                Нет полей для заполнения
              </h3>
              <div class="mt-2 text-sm text-yellow-700 dark:text-yellow-300">
                <p>В этом типе данных нет полей. Сначала добавьте поля к типу данных в разделе администрирования, а затем сможете добавлять записи.</p>
              </div>
            </div>
          </div>
        </div>
        
        <form v-else @submit.prevent="addDataRecord" class="space-y-4">
          <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            <div v-for="field in dataFields" :key="field.id">
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                {{ field.field_name }}
                <span v-if="field.is_required" class="text-red-500">*</span>
              </label>
              
              <!-- Текстовое поле -->
              <input
                v-if="field.field_type === 'text'"
                v-model="newRecord[field.field_name]"
                type="text"
                :required="field.is_required"
                class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
                :placeholder="field.description"
              >
              
              <!-- Целое число -->
              <input
                v-else-if="field.field_type === 'integer'"
                v-model.number="newRecord[field.field_name]"
                type="number"
                step="1"
                :required="field.is_required"
                class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
                :placeholder="field.description"
              >
              
              <!-- Десятичное число -->
              <input
                v-else-if="field.field_type === 'decimal'"
                v-model.number="newRecord[field.field_name]"
                type="number"
                step="any"
                :required="field.is_required"
                class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
                :placeholder="field.description"
              >
              
              <!-- Дата -->
              <input
                v-else-if="field.field_type === 'date'"
                v-model="newRecord[field.field_name]"
                type="date"
                :required="field.is_required"
                class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
              >
              
              <!-- Булево поле -->
              <select
                v-else-if="field.field_type === 'boolean'"
                v-model="newRecord[field.field_name]"
                :required="field.is_required"
                class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
              >
                <option value="">Выберите...</option>
                <option value="true">Да</option>
                <option value="false">Нет</option>
              </select>
            </div>
          </div>
          
          <div class="flex justify-end">
            <button
              type="submit"
              :disabled="loading"
              class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
            >
              {{ loading ? 'Добавление...' : 'Добавить запись' }}
            </button>
          </div>
        </form>
      </div>

      <!-- Таблица данных -->
      <div class="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-lg font-medium text-gray-900 dark:text-white">
            Записи данных
          </h3>
          <button
            @click="loadData"
            class="px-3 py-1 text-sm bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded hover:bg-gray-200 dark:hover:bg-gray-600"
          >
            Обновить
          </button>
        </div>
        
        <div v-if="loading" class="text-center py-4">
          <div class="inline-block animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
        </div>
        
        <div v-else-if="dataRecords.length === 0" class="text-center py-8 text-gray-500 dark:text-gray-400">
          Нет данных для отображения
        </div>
        
        <div v-else class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700" style="min-width: 600px;">
            <thead class="bg-gray-50 dark:bg-gray-700">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  №
                </th>
                <th
                  v-for="field in dataFields"
                  :key="field.id"
                  @click="sortBy(field.field_name)"
                  class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider cursor-pointer hover:bg-gray-200 dark:hover:bg-gray-600 select-none"
                  :title="`Сортировать по ${field.field_name}`"
                >
                  <div class="flex items-center justify-between">
                    <span>{{ field.field_name }}</span>
                    <span class="ml-2 text-sm">{{ getSortIcon(field.field_name) }}</span>
                  </div>
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  Дата создания
                </th>
                <th v-if="currentUser?.role === 'admin'" class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  Добавил
                </th>
              </tr>
            </thead>
            <tbody class="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
              <tr v-for="(record, index) in paginatedRecords" :key="record.id">
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                  {{ (currentRecordsPage - 1) * recordsPerPage + index + 1 }}
                </td>
                <td
                  v-for="field in dataFields"
                  :key="field.id"
                  class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white"
                >
                  {{ formatFieldValue(record[field.field_name], field.field_type) }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                  {{ formatDate(record.created_at) }}
                </td>
                <td v-if="currentUser?.role === 'admin'" class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                  <div class="flex flex-col">
                    <span class="font-medium text-gray-900 dark:text-white">
                      {{ record.created_by_username || 'Неизвестно' }}
                    </span>
                    <span v-if="record.created_by_full_name" class="text-xs text-gray-500 dark:text-gray-400">
                      {{ record.created_by_full_name }}
                    </span>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
          
          <!-- Пагинация для записей данных -->
          <div v-if="dataRecords.length > 0" class="px-6 py-3 bg-gray-50 dark:bg-gray-700 border-t border-gray-200 dark:border-gray-600 flex flex-col lg:flex-row justify-between items-start lg:items-center gap-4 text-sm text-gray-600 dark:text-gray-300">
            <!-- Информация о записях -->
            <div class="flex flex-col sm:flex-row gap-2 sm:gap-4">
              <span>Показано {{ (currentRecordsPage - 1) * recordsPerPage + 1 }}-{{ Math.min(currentRecordsPage * recordsPerPage, dataRecords.length) }} из {{ dataRecords.length }} записей</span>
              <span v-if="sortField" class="text-blue-600 dark:text-blue-400">
                Сортировка: {{ sortField }} {{ sortOrder === 1 ? '↑' : '↓' }}
              </span>
            </div>
            
            <!-- Элементы управления пагинацией -->
            <div class="flex flex-col sm:flex-row items-start sm:items-center gap-4 w-full lg:w-auto">
              <!-- Выбор количества записей на странице -->
              <div class="flex items-center gap-2">
                <span>Записей на странице:</span>
                <select v-model="recordsPerPage"
                  class="w-20 p-1 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-200 text-sm">
                  <option value="10">10</option>
                  <option value="20">20</option>
                  <option value="50">50</option>
                  <option value="100">100</option>
                </select>
              </div>
              
              <!-- Навигация по страницам -->
              <div class="flex items-center gap-1">
                <!-- Первая страница -->
                <button @click="goToFirstRecordsPage" :disabled="currentRecordsPage === 1"
                  class="px-2 py-1 border border-gray-300 dark:border-gray-600 rounded disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-100 dark:hover:bg-gray-600 text-sm"
                  title="Первая страница">
                  ⏮
                </button>
                
                <!-- Предыдущая страница -->
                <button @click="goToPreviousRecordsPage" :disabled="currentRecordsPage === 1"
                  class="px-2 py-1 border border-gray-300 dark:border-gray-600 rounded disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-100 dark:hover:bg-gray-600 text-sm"
                  title="Предыдущая страница">
                  ←
                </button>
                
                <!-- Номера страниц -->
                <div class="flex gap-1">
                  <button v-for="page in getRecordsPageNumbers()" :key="page"
                    @click="page !== '...' && goToRecordsPage(page)"
                    :disabled="page === '...'"
                    :class="[
                      'px-3 py-1 text-sm border rounded transition-colors',
                      page === currentRecordsPage 
                        ? 'bg-blue-500 text-white border-blue-500' 
                        : page === '...'
                        ? 'border-transparent cursor-default text-gray-400'
                        : 'border-gray-300 dark:border-gray-600 hover:bg-gray-100 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-200'
                    ]"
                    :title="page === '...' ? '' : `Страница ${page}`">
                    {{ page }}
                  </button>
                </div>
                
                <!-- Следующая страница -->
                <button @click="goToNextRecordsPage" :disabled="currentRecordsPage === totalRecordsPages"
                  class="px-2 py-1 border border-gray-300 dark:border-gray-600 rounded disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-100 dark:hover:bg-gray-600 text-sm"
                  title="Следующая страница">
                  →
                </button>
                
                <!-- Последняя страница -->
                <button @click="goToLastRecordsPage" :disabled="currentRecordsPage === totalRecordsPages"
                  class="px-2 py-1 border border-gray-300 dark:border-gray-600 rounded disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-100 dark:hover:bg-gray-600 text-sm"
                  title="Последняя страница">
                  ⏭
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Статистика -->
      <div v-if="statistics && Object.keys(statistics).length > 0" class="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
        <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-4">
          Статистика
        </h3>
        
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div
            v-for="(stats, fieldName) in statistics"
            :key="fieldName"
            class="p-4 border border-gray-200 dark:border-gray-600 rounded-lg"
          >
            <h4 class="font-medium text-gray-900 dark:text-white mb-2">
              {{ fieldName }}
            </h4>
            <div class="space-y-1 text-sm text-gray-600 dark:text-gray-400">
              <div>Количество: {{ stats.count }}</div>
              <div>Среднее: {{ stats.mean?.toFixed(2) }}</div>
              <div>Мин: {{ stats.min }}</div>
              <div>Макс: {{ stats.max }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue'

export default {
  name: 'DataManagement',
  setup() {
    const dataTypes = ref([])
    const selectedDataType = ref(null)
    const dataFields = ref([])
    const dataRecords = ref([])
    const statistics = ref({})
    const loading = ref(false)
    const newRecord = ref({})
    const hasFields = ref(false)
    const currentUser = ref(null)
    
    // Пагинация и сортировка
    const recordsPerPage = ref(20)
    const currentRecordsPage = ref(1)
    const sortField = ref('')
    const sortOrder = ref(1) // 1 для возрастания, -1 для убывания
    
    // Computed свойства для сортировки и пагинации
    const sortedRecords = computed(() => {
      let result = [...dataRecords.value]
      
      if (sortField.value) {
        result.sort((a, b) => {
          const aVal = a[sortField.value]
          const bVal = b[sortField.value]
          
          // Обработка разных типов данных
          if (typeof aVal === 'number' && typeof bVal === 'number') {
            return sortOrder.value === 1 ? aVal - bVal : bVal - aVal
          }
          
          if (aVal instanceof Date && bVal instanceof Date) {
            return sortOrder.value === 1 ? aVal - bVal : bVal - aVal
          }
          
          // Для строк и других типов
          const aStr = String(aVal || '').toLowerCase()
          const bStr = String(bVal || '').toLowerCase()
          
          if (aStr < bStr) return sortOrder.value === 1 ? -1 : 1
          if (aStr > bStr) return sortOrder.value === 1 ? 1 : -1
          return 0
        })
      }
      
      return result
    })
    
    const totalRecordsPages = computed(() => {
      return Math.ceil(sortedRecords.value.length / recordsPerPage.value)
    })
    
    const paginatedRecords = computed(() => {
      const start = (currentRecordsPage.value - 1) * recordsPerPage.value
      const end = start + recordsPerPage.value
      return sortedRecords.value.slice(start, end)
    })
    
    const loadCurrentUser = async () => {
      try {
        const response = await fetch('http://localhost:5000/api/auth/me', {
          credentials: 'include'
        })
        
        if (response.ok) {
          currentUser.value = await response.json()
        }
      } catch (err) {
        console.error('Ошибка загрузки пользователя:', err)
      }
    }
    
    const loadDataTypes = async () => {
      try {
        const response = await fetch('http://localhost:5000/api/data-types', {
          credentials: 'include'
        })
        
        if (response.ok) {
          const allTypes = await response.json()
          // Показываем только те типы данных, к которым у пользователя есть права на редактирование
          dataTypes.value = allTypes.filter(type => type.can_edit === true)
        }
      } catch (err) {
        console.error('Ошибка загрузки типов данных:', err)
      }
    }
    
    const loadDataFields = async (dataTypeId) => {
      try {
        const response = await fetch(`http://localhost:5000/api/data-types/${dataTypeId}/fields`, {
          credentials: 'include'
        })
        
        if (response.ok) {
          dataFields.value = await response.json()
          hasFields.value = dataFields.value.length > 0
        }
      } catch (err) {
        console.error('Ошибка загрузки полей:', err)
      }
    }
    
    const checkHasFields = async (dataTypeId) => {
      try {
        const response = await fetch(`http://localhost:5000/api/data-types/${dataTypeId}/has-fields`, {
          credentials: 'include'
        })
        
        if (response.ok) {
          const data = await response.json()
          hasFields.value = data.has_fields
        }
      } catch (err) {
        console.error('Ошибка проверки полей:', err)
      }
    }
    
    const loadDataRecords = async (dataTypeId) => {
      loading.value = true
      try {
        const response = await fetch(`http://localhost:5000/api/data/${dataTypeId}`, {
          credentials: 'include'
        })
        
        if (response.ok) {
          dataRecords.value = await response.json()
        }
      } catch (err) {
        console.error('Ошибка загрузки записей:', err)
      } finally {
        loading.value = false
      }
    }
    
    const loadStatistics = async (dataTypeId) => {
      try {
        const response = await fetch(`http://localhost:5000/api/data/${dataTypeId}/statistics`, {
          credentials: 'include'
        })
        
        if (response.ok) {
          statistics.value = await response.json()
        }
      } catch (err) {
        console.error('Ошибка загрузки статистики:', err)
      }
    }
    
    const selectDataType = async (dataType) => {
      selectedDataType.value = dataType
      newRecord.value = {}
      
      await loadDataFields(dataType.id)
      await checkHasFields(dataType.id)
      await loadDataRecords(dataType.id)
      await loadStatistics(dataType.id)
    }
    
    const addDataRecord = async () => {
      loading.value = true
      try {
        // Подготавливаем данные для отправки
        const recordData = { ...newRecord.value }
        
        // Конвертируем строковые значения в нужные типы
        dataFields.value.forEach(field => {
          if (field.field_type === 'integer' && recordData[field.field_name]) {
            recordData[field.field_name] = parseInt(recordData[field.field_name])
          } else if (field.field_type === 'decimal' && recordData[field.field_name]) {
            recordData[field.field_name] = parseFloat(recordData[field.field_name])
          } else if (field.field_type === 'boolean') {
            // Для boolean полей: если не заполнено - null, иначе конвертируем
            if (recordData[field.field_name] === '' || recordData[field.field_name] === undefined) {
              recordData[field.field_name] = null
            } else {
              recordData[field.field_name] = recordData[field.field_name] === 'true'
            }
          }
        })
        
        const response = await fetch(`http://localhost:5000/api/data/${selectedDataType.value.id}`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          credentials: 'include',
          body: JSON.stringify(recordData)
        })
        
        if (response.ok) {
          // Очищаем форму
          newRecord.value = {}
          
          // Перезагружаем данные
          await loadDataRecords(selectedDataType.value.id)
          await loadStatistics(selectedDataType.value.id)
          
          window.$notify?.success('Запись добавлена', 'Новая запись успешно добавлена в базу данных')
        } else {
          const error = await response.json()
          window.$notify?.error('Ошибка добавления записи', error.error)
        }
      } catch (err) {
        console.error('Ошибка добавления записи:', err)
        window.$notify?.error('Ошибка соединения', 'Не удалось подключиться к серверу')
      } finally {
        loading.value = false
      }
    }
    
    const loadData = async () => {
      if (selectedDataType.value) {
        await loadDataRecords(selectedDataType.value.id)
        await loadStatistics(selectedDataType.value.id)
      }
    }
    
    const formatFieldValue = (value, fieldType) => {
      if (value === null || value === undefined) return '-'
      
      if (fieldType === 'boolean') {
        // Для boolean полей null означает "не выбрано"
        if (value === null) return '-'
        return value ? 'Да' : 'Нет'
      } else if (fieldType === 'integer') {
        return typeof value === 'number' ? Math.round(value) : value
      } else if (fieldType === 'decimal') {
        return typeof value === 'number' ? value.toFixed(2) : value
      } else if (fieldType === 'date') {
        return new Date(value).toLocaleDateString('ru-RU')
      }
      
      return value
    }
    
    const formatDate = (dateString) => {
      return new Date(dateString).toLocaleString('ru-RU')
    }
    
    // Функции сортировки
    const sortBy = (field) => {
      if (sortField.value === field) {
        sortOrder.value = sortOrder.value === 1 ? -1 : 1
      } else {
        sortField.value = field
        sortOrder.value = 1
      }
      currentRecordsPage.value = 1 // Сбрасываем на первую страницу при сортировке
    }
    
    const getSortIcon = (field) => {
      if (sortField.value !== field) return '↕'
      return sortOrder.value === 1 ? '↑' : '↓'
    }
    
    // Функции пагинации
    const goToRecordsPage = (page) => {
      if (page >= 1 && page <= totalRecordsPages.value) {
        currentRecordsPage.value = page
      }
    }
    
    const goToPreviousRecordsPage = () => {
      goToRecordsPage(Math.max(1, currentRecordsPage.value - 1))
    }
    
    const goToNextRecordsPage = () => {
      goToRecordsPage(Math.min(totalRecordsPages.value, currentRecordsPage.value + 1))
    }
    
    const goToFirstRecordsPage = () => {
      goToRecordsPage(1)
    }
    
    const goToLastRecordsPage = () => {
      goToRecordsPage(totalRecordsPages.value)
    }
    
    const getRecordsPageNumbers = () => {
      const total = totalRecordsPages.value
      const current = currentRecordsPage.value
      const pages = []
      
      if (total <= 7) {
        for (let i = 1; i <= total; i++) {
          pages.push(i)
        }
      } else {
        if (current <= 4) {
          pages.push(1, 2, 3, 4, 5)
          pages.push('...')
          pages.push(total)
        } else if (current >= total - 3) {
          pages.push(1)
          pages.push('...')
          for (let i = total - 4; i <= total; i++) {
            pages.push(i)
          }
        } else {
          pages.push(1)
          pages.push('...')
          for (let i = current - 1; i <= current + 1; i++) {
            pages.push(i)
          }
          pages.push('...')
          pages.push(total)
        }
      }
      
      return pages
    }
    
    const getFieldTypeName = (fieldType) => {
      const types = {
        'text': 'Текст',
        'number': 'Число',
        'date': 'Дата',
        'boolean': 'Да/Нет'
      }
      return types[fieldType] || fieldType
    }
    
    onMounted(() => {
      loadCurrentUser()
      loadDataTypes()
    })
    
    return {
      dataTypes,
      selectedDataType,
      dataFields,
      dataRecords,
      statistics,
      loading,
      newRecord,
      hasFields,
      currentUser,
      // Пагинация и сортировка
      recordsPerPage,
      currentRecordsPage,
      sortField,
      sortOrder,
      sortedRecords,
      totalRecordsPages,
      paginatedRecords,
      selectDataType,
      addDataRecord,
      loadData,
      formatFieldValue,
      formatDate,
      getFieldTypeName,
      // Функции сортировки и пагинации
      sortBy,
      getSortIcon,
      goToRecordsPage,
      goToPreviousRecordsPage,
      goToNextRecordsPage,
      goToFirstRecordsPage,
      goToLastRecordsPage,
      getRecordsPageNumbers
    }
  }
}
</script>
