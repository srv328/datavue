<template>
  <div class="space-y-6">
    <!-- Выбор типа данных для анализа -->
    <div class="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
      <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-4">
        Выберите тип данных для анализа
      </h3>
      
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
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

    <!-- Анализ выбранного типа данных -->
    <div v-if="selectedDataType" class="space-y-6">
      <!-- Информация о полях -->
      <div class="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-lg font-medium text-gray-900 dark:text-white">
            Поля для анализа: {{ selectedDataType.name }}
          </h3>
        <div class="flex space-x-2">
          <button
            @click="showExportModal = true"
            class="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 flex items-center space-x-2"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
            </svg>
            <span>Экспорт CSV</span>
          </button>
          
          <button
            @click="showExcelExportModal = true"
            class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 flex items-center space-x-2"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
            </svg>
            <span>Экспорт Excel</span>
          </button>
        </div>
        </div>
        
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
          </div>
        </div>
      </div>

      <!-- Статистический анализ -->
      <div v-if="statistics && Object.keys(statistics).length > 0" class="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
        <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-4">
          Статистический анализ
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
              <div v-if="stats.mean !== null">Среднее: {{ stats.mean?.toFixed(2) }}</div>
              <div v-if="stats.min !== null">Мин: {{ stats.min }}</div>
              <div v-if="stats.max !== null">Макс: {{ stats.max }}</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Выбор полей для графиков -->
      <div v-if="dataFields.length > 0" class="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
        <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-4">
          Построение графиков и диаграмм
        </h3>
        
        <div class="space-y-4">
          <!-- Выбор полей -->
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Выберите поля для визуализации:
            </label>
            <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-2">
              <label
                v-for="field in dataFields"
                :key="field.id"
                class="flex items-center space-x-2 p-2 border border-gray-200 dark:border-gray-600 rounded cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-700"
                :class="selectedFieldsForCharts.includes(field.field_name) ? 'bg-blue-50 dark:bg-blue-900 border-blue-300 dark:border-blue-700' : ''"
              >
                <input
                  type="checkbox"
                  :value="field.field_name"
                  v-model="selectedFieldsForCharts"
                  class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                >
                <span class="text-sm text-gray-900 dark:text-white">{{ field.field_name }}</span>
              </label>
            </div>
          </div>
          
          <!-- Выбор типа графика -->
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Тип графика:
            </label>
            <select
              v-model="selectedChartType"
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
            >
              <option value="bar">Столбчатая диаграмма</option>
              <option value="pie">Круговая диаграмма</option>
              <option value="line">Линейный график</option>
              <option value="doughnut">Кольцевая диаграмма</option>
            </select>
          </div>
          
          <!-- Кнопка построения графика -->
          <div class="flex space-x-4">
            <button
              @click="buildChart"
              :disabled="selectedFieldsForCharts.length === 0 || loading"
              class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
            >
              {{ loading ? 'Построение...' : 'Построить график' }}
            </button>
            <button
              @click="clearChart"
              class="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-gray-500"
            >
              Очистить
            </button>
          </div>
        </div>
      </div>

      <!-- График -->
      <div v-if="chartTitle" class="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
        <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-4">
          График: {{ chartTitle }}
        </h3>
        <div class="relative">
          <canvas ref="chartCanvas" width="400" height="200"></canvas>
        </div>
      </div>

      <!-- Простой анализ данных -->
      <div v-if="chartData && chartData.length > 0" class="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
        <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-4">
          Простой анализ данных
        </h3>
        
        <div class="space-y-6">
          <!-- График распределения по полям -->
          <div v-for="chart in chartData" :key="chart.field" class="border border-gray-200 dark:border-gray-600 rounded-lg p-4">
            <h4 class="font-medium text-gray-900 dark:text-white mb-3">
              {{ chart.field }} - {{ chart.type }}
            </h4>
            
            <!-- Простая визуализация данных -->
            <div v-if="chart.type === 'text'" class="space-y-2">
              <div
                v-for="item in chart.data.slice(0, 10)"
                :key="item.value"
                class="flex items-center justify-between p-2 bg-gray-50 dark:bg-gray-700 rounded"
              >
                <span class="text-sm text-gray-900 dark:text-white">{{ item.value }}</span>
                <span class="text-sm text-gray-600 dark:text-gray-400">{{ item.count }}</span>
              </div>
              <div v-if="chart.data.length > 10" class="text-sm text-gray-500 dark:text-gray-400 text-center">
                ... и еще {{ chart.data.length - 10 }} записей
              </div>
            </div>
            
            <div v-else-if="chart.type === 'integer' || chart.type === 'decimal'" class="space-y-2">
              <div class="text-sm text-gray-600 dark:text-gray-400 mb-2">
                Статистика:
              </div>
              <div
                v-for="item in chart.data"
                :key="item.label"
                class="flex items-center justify-between p-2 bg-gray-50 dark:bg-gray-700 rounded"
              >
                <span class="text-sm text-gray-900 dark:text-white">{{ item.label }}</span>
                <span class="text-sm text-gray-600 dark:text-gray-400">{{ item.value }}</span>
              </div>
            </div>
            
            <div v-else-if="chart.type === 'boolean'" class="space-y-2">
              <div
                v-for="item in chart.data"
                :key="item.value"
                class="flex items-center justify-between p-2 bg-gray-50 dark:bg-gray-700 rounded"
              >
                <span class="text-sm text-gray-900 dark:text-white">
                  {{ item.value === true ? 'Да' : item.value === false ? 'Нет' : 'Не указано' }}
                </span>
                <span class="text-sm text-gray-600 dark:text-gray-400">{{ item.count }}</span>
              </div>
            </div>
            
            <div v-else-if="chart.type === 'date'" class="space-y-2">
              <div
                v-for="item in chart.data.slice(0, 10)"
                :key="item.value"
                class="flex items-center justify-between p-2 bg-gray-50 dark:bg-gray-700 rounded"
              >
                <span class="text-sm text-gray-900 dark:text-white">{{ item.value }}</span>
                <span class="text-sm text-gray-600 dark:text-gray-400">{{ item.count }}</span>
              </div>
              <div v-if="chart.data.length > 10" class="text-sm text-gray-500 dark:text-gray-400 text-center">
                ... и еще {{ chart.data.length - 10 }} записей
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Общая информация -->
      <div class="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
        <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-4">
          Общая информация
        </h3>
        
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div class="p-4 border border-gray-200 dark:border-gray-600 rounded-lg">
            <h4 class="font-medium text-gray-900 dark:text-white mb-2">Всего записей</h4>
            <div class="text-2xl font-bold text-blue-600 dark:text-blue-400">
              {{ totalRecords }}
            </div>
          </div>
          
          <div class="p-4 border border-gray-200 dark:border-gray-600 rounded-lg">
            <h4 class="font-medium text-gray-900 dark:text-white mb-2">Поля</h4>
            <div class="text-2xl font-bold text-green-600 dark:text-green-400">
              {{ dataFields.length }}
            </div>
          </div>
          
          <div class="p-4 border border-gray-200 dark:border-gray-600 rounded-lg">
            <h4 class="font-medium text-gray-900 dark:text-white mb-2">Числовые поля</h4>
            <div class="text-2xl font-bold text-purple-600 dark:text-purple-400">
              {{ numericFieldsCount }}
            </div>
          </div>
          
          <div class="p-4 border border-gray-200 dark:border-gray-600 rounded-lg">
            <h4 class="font-medium text-gray-900 dark:text-white mb-2">Текстовые поля</h4>
            <div class="text-2xl font-bold text-orange-600 dark:text-orange-400">
              {{ textFieldsCount }}
            </div>
          </div>
        </div>
      </div>

      <!-- Кнопка обновления -->
      <div class="flex justify-center">
        <button
          @click="loadAnalysis"
          :disabled="loading"
          class="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
        >
          {{ loading ? 'Обновление...' : 'Обновить анализ' }}
        </button>
      </div>
    </div>

    <!-- Модальное окно экспорта CSV -->
    <div v-if="showExportModal" class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
      <div class="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white dark:bg-gray-800">
        <div class="mt-3">
          <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-4">
            Экспорт данных в CSV
          </h3>
          
          <form @submit.prevent="exportToCSV" class="space-y-4">
            <!-- Количество записей -->
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Количество записей для экспорта:
              </label>
              <select
                v-model="exportOptions.limit"
                class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
              >
                <option value="10">10 записей</option>
                <option value="50">50 записей</option>
                <option value="100">100 записей</option>
                <option value="500">500 записей</option>
                <option value="0">Все записи</option>
              </select>
            </div>
            
            <!-- Включать заголовки -->
            <div class="flex items-center">
              <input
                v-model="exportOptions.includeHeaders"
                type="checkbox"
                class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              >
              <label class="ml-2 text-sm text-gray-700 dark:text-gray-300">
                Включать названия полей в заголовки
              </label>
            </div>
            
            <!-- Включать описания -->
            <div class="flex items-center">
              <input
                v-model="exportOptions.includeDescriptions"
                type="checkbox"
                class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              >
              <label class="ml-2 text-sm text-gray-700 dark:text-gray-300">
                Включать описания полей в заголовки
              </label>
            </div>
            
            <!-- Кнопки -->
            <div class="flex justify-end space-x-3 pt-4">
              <button
                type="button"
                @click="showExportModal = false"
                class="px-4 py-2 bg-gray-300 text-gray-700 rounded-md hover:bg-gray-400 focus:outline-none focus:ring-2 focus:ring-gray-500"
              >
                Отмена
              </button>
              <button
                type="submit"
                :disabled="exporting"
                class="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 disabled:opacity-50"
              >
                {{ exporting ? 'Экспорт...' : 'Экспортировать' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
    
    <!-- Модальное окно для экспорта Excel -->
    <div v-if="showExcelExportModal" class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
      <div class="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white dark:bg-gray-800">
        <div class="mt-3">
          <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-4">
            Экспорт данных в Excel
          </h3>
          
          <form @submit.prevent="exportToExcel" class="space-y-4">
            <!-- Количество записей -->
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Количество записей для экспорта:
              </label>
              <select
                v-model="excelExportOptions.limit"
                class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
              >
                <option value="10">10 записей</option>
                <option value="50">50 записей</option>
                <option value="100">100 записей</option>
                <option value="500">500 записей</option>
                <option value="0">Все записи</option>
              </select>
            </div>
            
            <!-- Включать заголовки -->
            <div class="flex items-center">
              <input
                v-model="excelExportOptions.includeHeaders"
                type="checkbox"
                class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              >
              <label class="ml-2 text-sm text-gray-700 dark:text-gray-300">
                Включать названия полей в заголовки
              </label>
            </div>
            
            <!-- Включать описания -->
            <div class="flex items-center">
              <input
                v-model="excelExportOptions.includeDescriptions"
                type="checkbox"
                class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              >
              <label class="ml-2 text-sm text-gray-700 dark:text-gray-300">
                Включать описания полей в заголовки
              </label>
            </div>
            
            <!-- Кнопки -->
            <div class="flex justify-end space-x-3 pt-4">
              <button
                type="button"
                @click="showExcelExportModal = false"
                class="px-4 py-2 bg-gray-300 text-gray-700 rounded-md hover:bg-gray-400 focus:outline-none focus:ring-2 focus:ring-gray-500"
              >
                Отмена
              </button>
              <button
                type="submit"
                :disabled="exporting"
                class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
              >
                {{ exporting ? 'Экспорт...' : 'Экспортировать в Excel' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, computed, nextTick } from 'vue'

// Динамический импорт Chart.js
let Chart = null
const loadChartJS = async () => {
  if (!Chart) {
    try {
      const chartModule = await import('chart.js')
      Chart = chartModule.Chart
      Chart.register(...chartModule.registerables)
      console.log('Chart.js загружен успешно')
    } catch (error) {
      console.error('Ошибка загрузки Chart.js:', error)
    }
  }
  return Chart
}

export default {
  name: 'AnalysisPanel',
  setup() {
    const dataTypes = ref([])
    const selectedDataType = ref(null)
    const dataFields = ref([])
    const statistics = ref({})
    const chartData = ref([])
    const totalRecords = ref(0)
    const loading = ref(false)
    const selectedFieldsForCharts = ref([])
    const selectedChartType = ref('bar')
    const chartCanvas = ref(null)
    const chartTitle = ref('')
    const currentChart = ref(null)
    
    // Переменные для экспорта CSV
    const showExportModal = ref(false)
    const showExcelExportModal = ref(false)
    const exporting = ref(false)
    const exportOptions = ref({
      limit: 100,
      includeHeaders: true,
      includeDescriptions: false
    })
    const excelExportOptions = ref({
      limit: 0, // По умолчанию все записи для Excel
      includeHeaders: true,
      includeDescriptions: false
    })
    
    const loadDataTypes = async () => {
      try {
        const response = await fetch('http://localhost:5000/api/data-types', {
          credentials: 'include'
        })
        
        if (response.ok) {
          const allTypes = await response.json()
          // В анализе показываем все типы данных (и для чтения, и для редактирования)
          dataTypes.value = allTypes
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
        }
      } catch (err) {
        console.error('Ошибка загрузки полей:', err)
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
    
    const loadDataRecords = async (dataTypeId) => {
      try {
        const response = await fetch(`http://localhost:5000/api/data/${dataTypeId}`, {
          credentials: 'include'
        })
        
        if (response.ok) {
          const records = await response.json()
          totalRecords.value = records.length
          return records
        }
        return []
      } catch (err) {
        console.error('Ошибка загрузки записей:', err)
        return []
      }
    }
    
    const generateChartData = (records) => {
      const charts = []
      
      dataFields.value.forEach(field => {
        const fieldData = records.map(record => record[field.field_name])
        
        
        if (field.field_type === 'text') {
          // Подсчет уникальных значений
          const counts = {}
          fieldData.forEach(value => {
            if (value !== null && value !== undefined) {
              counts[value] = (counts[value] || 0) + 1
            }
          })
          
          charts.push({
            field: field.field_name,
            type: 'text',
            data: Object.entries(counts)
              .map(([value, count]) => ({ value, count }))
              .sort((a, b) => b.count - a.count)
          })
        } else if (field.field_type === 'integer' || field.field_type === 'decimal') {
          // Статистика для числовых полей
          const numericValues = fieldData.filter(v => v !== null && v !== undefined).map(Number)
          if (numericValues.length > 0) {
            const sum = numericValues.reduce((a, b) => a + b, 0)
            const avg = sum / numericValues.length
            const min = Math.min(...numericValues)
            const max = Math.max(...numericValues)
            const sorted = numericValues.sort((a, b) => a - b)
            const median = sorted[Math.floor(sorted.length / 2)]
            
            charts.push({
              field: field.field_name,
              type: field.field_type,
              data: [
                { label: 'Среднее', value: field.field_type === 'integer' ? Math.round(avg) : parseFloat(avg.toFixed(2)) },
                { label: 'Минимум', value: field.field_type === 'integer' ? Math.round(min) : parseFloat(min.toFixed(2)) },
                { label: 'Максимум', value: field.field_type === 'integer' ? Math.round(max) : parseFloat(max.toFixed(2)) },
                { label: 'Медиана', value: field.field_type === 'integer' ? Math.round(median) : parseFloat(median.toFixed(2)) },
                { label: 'Сумма', value: field.field_type === 'integer' ? Math.round(sum) : parseFloat(sum.toFixed(2)) }
              ]
            })
          }
        } else if (field.field_type === 'boolean') {
          // Подсчет true/false/null
          const counts = { true: 0, false: 0, null: 0 }
          fieldData.forEach(value => {
            if (value === true || value === 'true' || value === 1) {
              counts.true++
            } else if (value === false || value === 'false' || value === 0) {
              counts.false++
            } else {
              counts.null++
            }
          })
          
          charts.push({
            field: field.field_name,
            type: 'boolean',
            data: Object.entries(counts).map(([value, count]) => ({
              value: value === 'null' ? null : value === 'true',
              count
            }))
          })
        } else if (field.field_type === 'date') {
          // Группировка по месяцам
          const counts = {}
          fieldData.forEach(value => {
            if (value) {
              const date = new Date(value)
              const month = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`
              counts[month] = (counts[month] || 0) + 1
            }
          })
          
          charts.push({
            field: field.field_name,
            type: 'date',
            data: Object.entries(counts)
              .map(([value, count]) => ({ value, count }))
              .sort((a, b) => a.value.localeCompare(b.value))
          })
        }
      })
      
      return charts
    }
    
    const selectDataType = async (dataType) => {
      selectedDataType.value = dataType
      loading.value = true
      
      try {
        await loadDataFields(dataType.id)
        await loadStatistics(dataType.id)
        const records = await loadDataRecords(dataType.id)
        chartData.value = generateChartData(records)
      } catch (err) {
        console.error('Ошибка загрузки данных для анализа:', err)
      } finally {
        loading.value = false
      }
    }
    
    const loadAnalysis = async () => {
      if (selectedDataType.value) {
        await selectDataType(selectedDataType.value)
      }
    }
    
    const formatDate = (dateString) => {
      return new Date(dateString).toLocaleString('ru-RU')
    }
    
    const getFieldTypeName = (fieldType) => {
      const types = {
        'text': 'Текст',
        'integer': 'Целое число',
        'decimal': 'Десятичное число',
        'date': 'Дата',
        'boolean': 'Да/Нет'
      }
      return types[fieldType] || fieldType
    }
    
    const numericFieldsCount = computed(() => {
      return dataFields.value.filter(field => field.field_type === 'integer' || field.field_type === 'decimal').length
    })
    
    const textFieldsCount = computed(() => {
      return dataFields.value.filter(field => field.field_type === 'text').length
    })
    
    const buildChart = async () => {
      if (selectedFieldsForCharts.value.length === 0) {
        console.log('Нет выбранных полей для графика')
        return
      }
      
      console.log('Начинаем построение графика...')
      console.log('Выбранные поля:', selectedFieldsForCharts.value)
      console.log('Тип графика:', selectedChartType.value)
      
      loading.value = true
      try {
        // Загружаем Chart.js
        const ChartClass = await loadChartJS()
        if (!ChartClass) {
          throw new Error('Не удалось загрузить Chart.js')
        }
        
        // Уничтожаем предыдущий график
        if (currentChart.value) {
          console.log('Уничтожаем предыдущий график')
          currentChart.value.destroy()
          currentChart.value = null
        }
        
        // Загружаем данные
        console.log('Загружаем данные...')
        const records = await loadDataRecords(selectedDataType.value.id)
        console.log('Загружено записей:', records.length)
        
        // Подготавливаем данные для графика
        console.log('Подготавливаем данные для графика...')
        const chartData = prepareChartData(records, selectedFieldsForCharts.value)
        console.log('Данные для графика:', chartData)
        
        // Устанавливаем заголовок, чтобы показать секцию с графиком
        chartTitle.value = `Анализ полей: ${selectedFieldsForCharts.value.join(', ')}`
        
        // Ждем, пока DOM обновится и canvas появится
        await nextTick()
        // Добавляем небольшую задержку для гарантии
        await new Promise(resolve => setTimeout(resolve, 100))
        console.log('Canvas элемент:', chartCanvas.value)
        
        if (chartCanvas.value) {
          console.log('Создаем новый график...')
          currentChart.value = new ChartClass(chartCanvas.value, {
            type: selectedChartType.value,
            data: chartData,
            options: {
              responsive: true,
              maintainAspectRatio: false,
              plugins: {
                title: {
                  display: true,
                  text: `Анализ полей: ${selectedFieldsForCharts.value.join(', ')}`
                },
                legend: {
                  display: true,
                  position: 'top'
                }
              }
            }
          })
          
          console.log('График создан успешно!')
        } else {
          console.error('Canvas элемент не найден!')
        }
      } catch (err) {
        console.error('Ошибка построения графика:', err)
        console.error('Стек ошибки:', err.stack)
      } finally {
        loading.value = false
      }
    }
    
    const prepareChartData = (records, fields) => {
      const datasets = []
      const labels = []
      
      // Для каждого выбранного поля создаем набор данных
      fields.forEach((fieldName, index) => {
        const field = dataFields.value.find(f => f.field_name === fieldName)
        if (!field) return
        
        const fieldData = records.map(record => record[fieldName])
        const colors = [
          'rgba(54, 162, 235, 0.8)',
          'rgba(255, 99, 132, 0.8)',
          'rgba(255, 205, 86, 0.8)',
          'rgba(75, 192, 192, 0.8)',
          'rgba(153, 102, 255, 0.8)',
          'rgba(255, 159, 64, 0.8)'
        ]
        
        if (field.field_type === 'text') {
          // Для текстовых полей - подсчет уникальных значений
          const counts = {}
          fieldData.forEach(value => {
            if (value !== null && value !== undefined) {
              counts[value] = (counts[value] || 0) + 1
            }
          })
          
          const sortedData = Object.entries(counts)
            .sort((a, b) => b[1] - a[1])
            .slice(0, 10) // Ограничиваем до 10 значений
          
          if (index === 0) {
            labels.push(...sortedData.map(([value]) => value))
          }
          
          datasets.push({
            label: fieldName,
            data: sortedData.map(([, count]) => count),
            backgroundColor: colors[index % colors.length],
            borderColor: colors[index % colors.length].replace('0.8', '1'),
            borderWidth: 1
          })
        } else if (field.field_type === 'integer' || field.field_type === 'decimal') {
          // Для числовых полей - показываем статистику
          const numericValues = fieldData.filter(v => v !== null && v !== undefined).map(Number)
          if (numericValues.length > 0) {
            const stats = {
              'Среднее': numericValues.reduce((a, b) => a + b, 0) / numericValues.length,
              'Минимум': Math.min(...numericValues),
              'Максимум': Math.max(...numericValues),
              'Медиана': numericValues.sort((a, b) => a - b)[Math.floor(numericValues.length / 2)]
            }
            
            if (index === 0) {
              labels.push(...Object.keys(stats))
            }
            
            datasets.push({
              label: fieldName,
              data: Object.values(stats).map(val => 
                field.field_type === 'integer' ? Math.round(val) : parseFloat(val.toFixed(2))
              ),
              backgroundColor: colors[index % colors.length],
              borderColor: colors[index % colors.length].replace('0.8', '1'),
              borderWidth: 1
            })
          }
        } else if (field.field_type === 'boolean') {
          // Для boolean полей
          const counts = { true: 0, false: 0, null: 0 }
          fieldData.forEach(value => {
            if (value === true || value === 'true' || value === 1) {
              counts.true++
            } else if (value === false || value === 'false' || value === 0) {
              counts.false++
            } else {
              counts.null++
            }
          })
          
          if (index === 0) {
            labels.push('Да', 'Нет', 'Не указано')
          }
          
          datasets.push({
            label: fieldName,
            data: [counts.true, counts.false, counts.null],
            backgroundColor: colors[index % colors.length],
            borderColor: colors[index % colors.length].replace('0.8', '1'),
            borderWidth: 1
          })
        }
      })
      
      return {
        labels: labels.length > 0 ? labels : ['Нет данных'],
        datasets: datasets.length > 0 ? datasets : [{
          label: 'Нет данных',
          data: [1],
          backgroundColor: 'rgba(200, 200, 200, 0.8)'
        }]
      }
    }
    
    const clearChart = () => {
      if (currentChart.value) {
        currentChart.value.destroy()
        currentChart.value = null
      }
      chartTitle.value = ''
      selectedFieldsForCharts.value = []
    }
    
    const exportToCSV = async () => {
      if (!selectedDataType.value) return
      
      exporting.value = true
      try {
        const response = await fetch(`http://localhost:5000/api/data-types/${selectedDataType.value.id}/export-csv`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          credentials: 'include',
          body: JSON.stringify({
            limit: parseInt(exportOptions.value.limit) || 0,
            include_headers: exportOptions.value.includeHeaders,
            include_descriptions: exportOptions.value.includeDescriptions
          })
        })
        
        if (response.ok) {
          // Создаем имя файла на основе выбранного типа данных
          const timestamp = new Date().toISOString().slice(0, 19).replace(/[-:]/g, '').replace('T', '_')
          const safeName = selectedDataType.value.name.replace(/[^a-zA-Z0-9а-яА-Я]/g, '_')
          const filename = `${safeName}_${timestamp}.csv`
          
          
          // Скачиваем файл
          const blob = await response.blob()
          const url = window.URL.createObjectURL(blob)
          const a = document.createElement('a')
          a.href = url
          a.download = filename
          document.body.appendChild(a)
          a.click()
          window.URL.revokeObjectURL(url)
          document.body.removeChild(a)
          
          showExportModal.value = false
          window.$notify?.success('Экспорт завершен', `Файл ${filename} успешно скачан`)
        } else {
          const error = await response.json()
          window.$notify?.error('Ошибка экспорта', error.error)
        }
      } catch (err) {
        console.error('Ошибка экспорта:', err)
        window.$notify?.error('Ошибка соединения', 'Не удалось подключиться к серверу')
      } finally {
        exporting.value = false
      }
    }
    
    const exportToExcel = async () => {
      if (!selectedDataType.value) return
      
      exporting.value = true
      try {
        const response = await fetch(`http://localhost:5000/api/data-types/${selectedDataType.value.id}/export-excel`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          credentials: 'include',
          body: JSON.stringify({
            limit: parseInt(excelExportOptions.value.limit) || 0,
            include_headers: excelExportOptions.value.includeHeaders,
            include_descriptions: excelExportOptions.value.includeDescriptions
          })
        })
        
        if (response.ok) {
          // Создаем имя файла на основе выбранного типа данных
          const timestamp = new Date().toISOString().slice(0, 19).replace(/[-:]/g, '').replace('T', '_')
          const safeName = selectedDataType.value.name.replace(/[^a-zA-Z0-9а-яА-Я]/g, '_')
          const filename = `${safeName}_${timestamp}.xlsx`
          
          
          // Скачиваем файл
          const blob = await response.blob()
          const url = window.URL.createObjectURL(blob)
          const a = document.createElement('a')
          a.href = url
          a.download = filename
          document.body.appendChild(a)
          a.click()
          window.URL.revokeObjectURL(url)
          document.body.removeChild(a)
          
          showExcelExportModal.value = false
          window.$notify?.success('Экспорт Excel завершен', `Файл ${filename} успешно скачан`)
        } else {
          const error = await response.json()
          window.$notify?.error('Ошибка экспорта Excel', error.error)
        }
      } catch (err) {
        console.error('Ошибка экспорта Excel:', err)
        window.$notify?.error('Ошибка соединения', 'Не удалось подключиться к серверу')
      } finally {
        exporting.value = false
      }
    }
    
    onMounted(() => {
      loadDataTypes()
    })
    
    return {
      dataTypes,
      selectedDataType,
      dataFields,
      statistics,
      chartData,
      totalRecords,
      loading,
      selectedFieldsForCharts,
      selectedChartType,
      chartCanvas,
      chartTitle,
      selectDataType,
      loadAnalysis,
      buildChart,
      clearChart,
      formatDate,
      getFieldTypeName,
      numericFieldsCount,
      textFieldsCount,
      showExportModal,
      showExcelExportModal,
      exporting,
      exportOptions,
      excelExportOptions,
      exportToCSV,
      exportToExcel
    }
  }
}
</script>
