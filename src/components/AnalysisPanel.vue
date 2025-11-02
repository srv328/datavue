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
              <option value="line">Линейный график</option>
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
        
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          <!-- График распределения по полям -->
          <div v-for="chart in chartData" :key="chart.field" class="border border-gray-200 dark:border-gray-600 rounded-lg p-4 bg-gray-50 dark:bg-gray-700/50">
            <h4 class="font-medium text-gray-900 dark:text-white mb-3 text-sm">
              {{ chart.field }}
              <span class="text-xs text-gray-500 dark:text-gray-400 ml-1">({{ getFieldTypeName(chart.type) }})</span>
            </h4>
            
            <!-- Простая визуализация данных -->
            <div v-if="chart.type === 'text'" class="space-y-1.5 max-h-64 overflow-y-auto">
              <div
                v-for="item in chart.data.slice(0, 8)"
                :key="item.value"
                class="flex items-center justify-between p-1.5 bg-white dark:bg-gray-800 rounded text-xs"
              >
                <span class="text-gray-900 dark:text-white truncate flex-1 mr-2" :title="item.value">{{ item.value }}</span>
                <span class="text-gray-600 dark:text-gray-400 font-semibold flex-shrink-0">{{ item.count }}</span>
              </div>
              <div v-if="chart.data.length > 8" class="text-xs text-gray-500 dark:text-gray-400 text-center pt-1">
                ... и еще {{ chart.data.length - 8 }} записей
              </div>
            </div>
            
            <div v-else-if="chart.type === 'integer' || chart.type === 'decimal'" class="space-y-1.5">
              <div
                v-for="item in chart.data"
                :key="item.label"
                class="flex items-center justify-between p-1.5 bg-white dark:bg-gray-800 rounded text-xs"
              >
                <span class="text-gray-700 dark:text-gray-300">{{ item.label }}</span>
                <span class="text-gray-900 dark:text-white font-semibold">{{ item.value }}</span>
              </div>
            </div>
            
            <div v-else-if="chart.type === 'boolean'" class="space-y-1.5">
              <div
                v-for="item in chart.data"
                :key="item.value"
                class="flex items-center justify-between p-1.5 bg-white dark:bg-gray-800 rounded text-xs"
              >
                <span class="text-gray-700 dark:text-gray-300">
                  {{ item.value === true ? 'Да' : item.value === false ? 'Нет' : 'Не указано' }}
                </span>
                <span class="text-gray-900 dark:text-white font-semibold">{{ item.count }}</span>
              </div>
            </div>
            
            <div v-else-if="chart.type === 'date'" class="space-y-1.5 max-h-64 overflow-y-auto">
              <div
                v-for="item in chart.data.slice(0, 8)"
                :key="item.value"
                class="flex items-center justify-between p-1.5 bg-white dark:bg-gray-800 rounded text-xs"
              >
                <span class="text-gray-900 dark:text-white">{{ item.value }}</span>
                <span class="text-gray-600 dark:text-gray-400 font-semibold">{{ item.count }}</span>
              </div>
              <div v-if="chart.data.length > 8" class="text-xs text-gray-500 dark:text-gray-400 text-center pt-1">
                ... и еще {{ chart.data.length - 8 }} записей
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Таблица данных с поиском и выбором столбцов -->
      <div v-if="selectedDataType && dataFields.length > 0" class="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
        <div class="flex justify-between items-center mb-4 flex-wrap gap-4">
          <h3 class="text-lg font-medium text-gray-900 dark:text-white">
            Таблица данных
          </h3>
          <div class="flex items-center gap-4 flex-wrap">
            <!-- Поиск -->
            <div class="relative">
              <input
                v-model="searchQuery"
                type="text"
                placeholder="Поиск по записям..."
                class="pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white text-sm"
              >
              <svg class="w-5 h-5 absolute left-2 top-2.5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
              </svg>
              <button
                v-if="searchQuery"
                @click="searchQuery = ''"
                class="absolute right-2 top-2.5 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
                title="Очистить поиск"
              >
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                </svg>
              </button>
            </div>
            
            <!-- Кнопка выбора столбцов -->
            <button
              @click="showColumnSelector = !showColumnSelector"
              class="px-4 py-2 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-md hover:bg-gray-200 dark:hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-gray-500 text-sm flex items-center gap-2"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4"></path>
              </svg>
              Столбцы
            </button>
            
            <!-- Кнопка обновления -->
            <button
              @click="loadDataRecords(selectedDataType.id)"
              class="px-3 py-2 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-md hover:bg-gray-200 dark:hover:bg-gray-600 text-sm"
            >
              Обновить
            </button>
          </div>
        </div>
        
        <!-- Селектор столбцов -->
        <div v-if="showColumnSelector" class="mb-4 p-4 bg-gray-50 dark:bg-gray-700 rounded-lg border border-gray-200 dark:border-gray-600">
          <div class="flex justify-between items-center mb-2">
            <h4 class="text-sm font-medium text-gray-900 dark:text-white">Выберите столбцы для отображения:</h4>
            <div class="flex gap-2">
              <button
                @click="selectAllColumns"
                class="px-2 py-1 text-xs bg-blue-500 text-white rounded hover:bg-blue-600"
              >
                Все
              </button>
              <button
                @click="deselectAllColumns"
                class="px-2 py-1 text-xs bg-gray-500 text-white rounded hover:bg-gray-600"
              >
                Ничего
              </button>
            </div>
          </div>
          <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-2">
            <label
              v-for="field in dataFields"
              :key="field.id"
              class="flex items-center space-x-2 p-2 border border-gray-200 dark:border-gray-600 rounded cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-600"
              :class="visibleColumns.includes(field.field_name) ? 'bg-blue-50 dark:bg-blue-900 border-blue-300 dark:border-blue-700' : ''"
            >
              <input
                type="checkbox"
                :value="field.field_name"
                v-model="visibleColumns"
                class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              >
              <span class="text-sm text-gray-900 dark:text-white">{{ field.field_name }}</span>
            </label>
            <!-- Добавляем системные столбцы -->
            <label
              class="flex items-center space-x-2 p-2 border border-gray-200 dark:border-gray-600 rounded cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-600"
              :class="visibleColumns.includes('created_at') ? 'bg-blue-50 dark:bg-blue-900 border-blue-300 dark:border-blue-700' : ''"
            >
              <input
                type="checkbox"
                value="created_at"
                v-model="visibleColumns"
                class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              >
              <span class="text-sm text-gray-900 dark:text-white">Дата создания</span>
            </label>
          </div>
        </div>
        
        <!-- Информация о результатах -->
        <div v-if="dataRecords.length > 0 && filteredRecords.length !== dataRecords.length" class="mb-2 text-sm text-gray-600 dark:text-gray-400">
          Найдено записей: {{ filteredRecords.length }} из {{ dataRecords.length }}
        </div>
        
        <!-- Таблица -->
        <div v-if="loading" class="text-center py-4">
          <div class="inline-block animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
        </div>
        
        <div v-else-if="dataRecords.length === 0" class="text-center py-8 text-gray-500 dark:text-gray-400">
          Нет записей данных для отображения
        </div>
        
        <div v-else-if="filteredRecords.length === 0" class="text-center py-8 text-gray-500 dark:text-gray-400">
          Не найдено записей по вашему запросу
        </div>
        
        <div v-else class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700" style="min-width: 600px;">
            <thead class="bg-gray-50 dark:bg-gray-700">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  №
                </th>
                <th
                  v-for="field in visibleFields"
                  :key="field.field_name"
                  @click="sortBy(field.field_name)"
                  class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider cursor-pointer hover:bg-gray-200 dark:hover:bg-gray-600 select-none"
                  :title="`Сортировать по ${field.field_name}`"
                >
                  <div class="flex items-center justify-between">
                    <span>{{ field.field_name === 'created_at' ? 'Дата создания' : field.field_name }}</span>
                    <span class="ml-2 text-sm">{{ getSortIcon(field.field_name) }}</span>
                  </div>
                </th>
              </tr>
            </thead>
            <tbody class="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
              <tr v-for="(record, index) in paginatedRecords" :key="record.id" class="hover:bg-gray-50 dark:hover:bg-gray-700">
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                  {{ (currentPage - 1) * rowsPerPage + index + 1 }}
                </td>
                <td
                  v-for="field in visibleFields"
                  :key="field.field_name"
                  class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white"
                >
                  <span v-if="field.field_name === 'created_at'">
                    {{ formatDate(record[field.field_name]) }}
                  </span>
                  <span v-else>
                    {{ formatFieldValue(record[field.field_name], field.field_type) }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
          
          <!-- Пагинация -->
          <div v-if="filteredRecords.length > 0" class="px-6 py-3 bg-gray-50 dark:bg-gray-700 border-t border-gray-200 dark:border-gray-600 flex flex-col lg:flex-row justify-between items-start lg:items-center gap-4 text-sm text-gray-600 dark:text-gray-300">
            <div class="flex flex-col sm:flex-row gap-2 sm:gap-4">
              <span>
                Показано {{ (currentPage - 1) * rowsPerPage + 1 }}-{{ Math.min(currentPage * rowsPerPage, filteredRecords.length) }} из {{ filteredRecords.length }} записей
              </span>
              <span v-if="sortField" class="text-blue-600 dark:text-blue-400">
                Сортировка: {{ sortField }} {{ sortOrder === 1 ? '↑' : '↓' }}
              </span>
            </div>
            
            <div class="flex flex-col sm:flex-row items-start sm:items-center gap-4 w-full lg:w-auto">
              <div class="flex items-center gap-2">
                <span>Записей на странице:</span>
                <select v-model="rowsPerPage" class="w-20 p-1 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-200 text-sm">
                  <option :value="10">10</option>
                  <option :value="20">20</option>
                  <option :value="50">50</option>
                  <option :value="100">100</option>
                </select>
              </div>
              
              <div class="flex items-center gap-1">
                <button @click="goToFirstPage" :disabled="currentPage === 1"
                  class="px-2 py-1 border border-gray-300 dark:border-gray-600 rounded disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-100 dark:hover:bg-gray-600 text-sm"
                  title="Первая страница">
                  ⏮
                </button>
                <button @click="goToPreviousPage" :disabled="currentPage === 1"
                  class="px-2 py-1 border border-gray-300 dark:border-gray-600 rounded disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-100 dark:hover:bg-gray-600 text-sm"
                  title="Предыдущая страница">
                  ←
                </button>
                <div class="flex gap-1">
                  <button v-for="page in getPageNumbers()" :key="page"
                    @click="page !== '...' && goToPage(page)"
                    :disabled="page === '...'"
                    :class="[
                      'px-3 py-1 text-sm border rounded transition-colors',
                      page === currentPage 
                        ? 'bg-blue-500 text-white border-blue-500' 
                        : page === '...'
                        ? 'border-transparent cursor-default text-gray-400'
                        : 'border-gray-300 dark:border-gray-600 hover:bg-gray-100 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-200'
                    ]">
                    {{ page }}
                  </button>
                </div>
                <button @click="goToNextPage" :disabled="currentPage === totalPages"
                  class="px-2 py-1 border border-gray-300 dark:border-gray-600 rounded disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-100 dark:hover:bg-gray-600 text-sm"
                  title="Следующая страница">
                  →
                </button>
                <button @click="goToLastPage" :disabled="currentPage === totalPages"
                  class="px-2 py-1 border border-gray-300 dark:border-gray-600 rounded disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-100 dark:hover:bg-gray-600 text-sm"
                  title="Последняя страница">
                  ⏭
                </button>
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
      <div class="relative top-10 mx-auto p-5 border w-full max-w-2xl shadow-lg rounded-md bg-white dark:bg-gray-800 max-h-[90vh] overflow-y-auto">
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
            
            <!-- Выбор полей для экспорта -->
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Выберите поля для экспорта:
              </label>
              <div class="border border-gray-300 dark:border-gray-600 rounded-md p-3 max-h-64 overflow-y-auto bg-gray-50 dark:bg-gray-700">
                <div class="flex justify-between items-center mb-2">
                  <span class="text-xs text-gray-600 dark:text-gray-400">
                    Выбрано: {{ exportOptions.selectedFields.length }} из {{ dataFields.length }}
                  </span>
                  <div class="flex gap-2">
                    <button
                      type="button"
                      @click="selectAllFieldsForExport"
                      class="px-2 py-1 text-xs bg-blue-500 text-white rounded hover:bg-blue-600"
                    >
                      Все
                    </button>
                    <button
                      type="button"
                      @click="deselectAllFieldsForExport"
                      class="px-2 py-1 text-xs bg-gray-500 text-white rounded hover:bg-gray-600"
                    >
                      Ничего
                    </button>
                  </div>
                </div>
                <div class="grid grid-cols-2 gap-2">
                  <label
                    v-for="field in dataFields"
                    :key="field.id"
                    class="flex items-center space-x-2 p-2 border border-gray-200 dark:border-gray-600 rounded cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-600"
                    :class="exportOptions.selectedFields.includes(field.field_name) ? 'bg-blue-50 dark:bg-blue-900 border-blue-300 dark:border-blue-700' : ''"
                  >
                    <input
                      type="checkbox"
                      :value="field.field_name"
                      v-model="exportOptions.selectedFields"
                      class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                    >
                    <span class="text-sm text-gray-900 dark:text-white">{{ field.field_name }}</span>
                  </label>
                </div>
              </div>
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
      <div class="relative top-10 mx-auto p-5 border w-full max-w-2xl shadow-lg rounded-md bg-white dark:bg-gray-800 max-h-[90vh] overflow-y-auto">
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
            
            <!-- Выбор полей для экспорта -->
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Выберите поля для экспорта:
              </label>
              <div class="border border-gray-300 dark:border-gray-600 rounded-md p-3 max-h-64 overflow-y-auto bg-gray-50 dark:bg-gray-700">
                <div class="flex justify-between items-center mb-2">
                  <span class="text-xs text-gray-600 dark:text-gray-400">
                    Выбрано: {{ excelExportOptions.selectedFields.length }} из {{ dataFields.length }}
                  </span>
                  <div class="flex gap-2">
                    <button
                      type="button"
                      @click="selectAllFieldsForExcelExport"
                      class="px-2 py-1 text-xs bg-blue-500 text-white rounded hover:bg-blue-600"
                    >
                      Все
                    </button>
                    <button
                      type="button"
                      @click="deselectAllFieldsForExcelExport"
                      class="px-2 py-1 text-xs bg-gray-500 text-white rounded hover:bg-gray-600"
                    >
                      Ничего
                    </button>
                  </div>
                </div>
                <div class="grid grid-cols-2 gap-2">
                  <label
                    v-for="field in dataFields"
                    :key="field.id"
                    class="flex items-center space-x-2 p-2 border border-gray-200 dark:border-gray-600 rounded cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-600"
                    :class="excelExportOptions.selectedFields.includes(field.field_name) ? 'bg-blue-50 dark:bg-blue-900 border-blue-300 dark:border-blue-700' : ''"
                  >
                    <input
                      type="checkbox"
                      :value="field.field_name"
                      v-model="excelExportOptions.selectedFields"
                      class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                    >
                    <span class="text-sm text-gray-900 dark:text-white">{{ field.field_name }}</span>
                  </label>
                </div>
              </div>
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
import { ref, onMounted, computed, nextTick, watch } from 'vue'

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
    
    // Данные для таблицы
    const dataRecords = ref([])
    const searchQuery = ref('')
    const visibleColumns = ref([])
    const showColumnSelector = ref(false)
    
    // Пагинация и сортировка для таблицы
    const rowsPerPage = ref(20)
    const currentPage = ref(1)
    const sortField = ref('')
    const sortOrder = ref(1) // 1 для возрастания, -1 для убывания
    
    // Переменные для экспорта CSV
    const showExportModal = ref(false)
    const showExcelExportModal = ref(false)
    const exporting = ref(false)
    const exportOptions = ref({
      limit: 100,
      includeHeaders: true,
      includeDescriptions: false,
      selectedFields: [] // Выбранные поля для экспорта
    })
    const excelExportOptions = ref({
      limit: 0, // По умолчанию все записи для Excel
      includeHeaders: true,
      includeDescriptions: false,
      selectedFields: [] // Выбранные поля для экспорта
    })
    
    // Функции для выбора полей при экспорте
    const selectAllFieldsForExport = () => {
      exportOptions.value.selectedFields = dataFields.value.map(f => f.field_name)
    }
    
    const deselectAllFieldsForExport = () => {
      exportOptions.value.selectedFields = []
    }
    
    const selectAllFieldsForExcelExport = () => {
      excelExportOptions.value.selectedFields = dataFields.value.map(f => f.field_name)
    }
    
    const deselectAllFieldsForExcelExport = () => {
      excelExportOptions.value.selectedFields = []
    }
    
    // Инициализация выбранных полей при открытии модального окна
    watch(showExportModal, (isOpen) => {
      if (isOpen && exportOptions.value.selectedFields.length === 0) {
        exportOptions.value.selectedFields = dataFields.value.map(f => f.field_name)
      }
    })
    
    watch(showExcelExportModal, (isOpen) => {
      if (isOpen && excelExportOptions.value.selectedFields.length === 0) {
        excelExportOptions.value.selectedFields = dataFields.value.map(f => f.field_name)
      }
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
          dataRecords.value = records
          
          // Инициализируем видимые столбцы, если еще не инициализированы
          if (visibleColumns.value.length === 0 && dataFields.value.length > 0) {
            visibleColumns.value = [
              ...dataFields.value.map(f => f.field_name),
              'created_at'
            ]
          }
          
          return records
        }
        // Если записей нет, все равно инициализируем видимые столбцы
        dataRecords.value = []
        if (visibleColumns.value.length === 0 && dataFields.value.length > 0) {
          visibleColumns.value = [
            ...dataFields.value.map(f => f.field_name),
            'created_at'
          ]
        }
        return []
      } catch (err) {
        console.error('Ошибка загрузки записей:', err)
        dataRecords.value = []
        // Если записей нет, все равно инициализируем видимые столбцы
        if (visibleColumns.value.length === 0 && dataFields.value.length > 0) {
          visibleColumns.value = [
            ...dataFields.value.map(f => f.field_name),
            'created_at'
          ]
        }
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
            const sorted = [...numericValues].sort((a, b) => a - b)
            const median = sorted.length % 2 === 0
              ? (sorted[sorted.length / 2 - 1] + sorted[sorted.length / 2]) / 2
              : sorted[Math.floor(sorted.length / 2)]
            
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
      
      // Сбрасываем поиск и пагинацию при смене типа данных
      searchQuery.value = ''
      currentPage.value = 1
      sortField.value = ''
      sortOrder.value = 1
      visibleColumns.value = []
      
      try {
        await loadDataFields(dataType.id)
        // Инициализируем видимые столбцы после загрузки полей
        if (dataFields.value.length > 0 && visibleColumns.value.length === 0) {
          visibleColumns.value = [
            ...dataFields.value.map(f => f.field_name),
            'created_at'
          ]
        }
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
        'boolean': 'Да/Нет',
        'enum': 'Перечислимое значение',
        'coordinates': 'Координаты'
      }
      return types[fieldType] || fieldType
    }
    
    const numericFieldsCount = computed(() => {
      return dataFields.value.filter(field => field.field_type === 'integer' || field.field_type === 'decimal').length
    })
    
    const textFieldsCount = computed(() => {
      return dataFields.value.filter(field => field.field_type === 'text').length
    })
    
    // Функции для работы с таблицей
    const visibleFields = computed(() => {
      if (visibleColumns.value.length === 0) return []
      return dataFields.value
        .filter(f => visibleColumns.value.includes(f.field_name))
        .concat(visibleColumns.value.includes('created_at') ? [{ field_name: 'created_at', field_type: 'date' }] : [])
    })
    
    // Поиск по записям
    const filteredRecords = computed(() => {
      if (!searchQuery.value.trim()) {
        return dataRecords.value
      }
      
      const query = searchQuery.value.toLowerCase()
      return dataRecords.value.filter(record => {
        // Ищем по всем видимым полям
        return visibleFields.value.some(field => {
          const value = record[field.field_name]
          if (value === null || value === undefined) return false
          
          // Для координат проверяем как объект
          if (field.field_type === 'coordinates' && typeof value === 'object') {
            const coordsStr = `(${value.latitude || ''}, ${value.longitude || ''})`
            return coordsStr.toLowerCase().includes(query)
          }
          
          // Для остальных типов - строковое сравнение
          return String(value).toLowerCase().includes(query)
        }) || String(record.id).includes(query)
      })
    })
    
    // Сортировка
    const sortedRecords = computed(() => {
      let result = [...filteredRecords.value]
      
      if (sortField.value) {
        result.sort((a, b) => {
          const aVal = a[sortField.value]
          const bVal = b[sortField.value]
          
          if (typeof aVal === 'number' && typeof bVal === 'number') {
            return sortOrder.value === 1 ? aVal - bVal : bVal - aVal
          }
          
          if (aVal instanceof Date && bVal instanceof Date) {
            return sortOrder.value === 1 ? aVal - bVal : bVal - aVal
          }
          
          const aStr = String(aVal || '').toLowerCase()
          const bStr = String(bVal || '').toLowerCase()
          
          if (aStr < bStr) return sortOrder.value === 1 ? -1 : 1
          if (aStr > bStr) return sortOrder.value === 1 ? 1 : -1
          return 0
        })
      }
      
      return result
    })
    
    const totalPages = computed(() => {
      return Math.ceil(sortedRecords.value.length / rowsPerPage.value)
    })
    
    const paginatedRecords = computed(() => {
      const start = (currentPage.value - 1) * rowsPerPage.value
      const end = start + rowsPerPage.value
      return sortedRecords.value.slice(start, end)
    })
    
    const sortBy = (fieldName) => {
      if (sortField.value === fieldName) {
        sortOrder.value *= -1
      } else {
        sortField.value = fieldName
        sortOrder.value = 1
      }
      currentPage.value = 1 // Сбрасываем на первую страницу при сортировке
    }
    
    const getSortIcon = (fieldName) => {
      if (sortField.value !== fieldName) return '⇅'
      return sortOrder.value === 1 ? '↑' : '↓'
    }
    
    const formatFieldValue = (value, fieldType) => {
      if (value === null || value === undefined) return '—'
      
      if (fieldType === 'boolean') {
        return value === true || value === 'true' || value === 1 ? 'Да' : 'Нет'
      }
      
      if (fieldType === 'date') {
        return formatDate(value)
      }
      
      if (fieldType === 'coordinates' && typeof value === 'object') {
        const lat = value.latitude !== null && value.latitude !== undefined ? value.latitude : '—'
        const lng = value.longitude !== null && value.longitude !== undefined ? value.longitude : '—'
        return `(${lat}, ${lng})`
      }
      
      return String(value)
    }
    
    // Функции выбора столбцов
    const selectAllColumns = () => {
      visibleColumns.value = [
        ...dataFields.value.map(f => f.field_name),
        'created_at'
      ]
    }
    
    const deselectAllColumns = () => {
      visibleColumns.value = []
    }
    
    // Функции пагинации
    const goToFirstPage = () => {
      currentPage.value = 1
    }
    
    const goToLastPage = () => {
      currentPage.value = totalPages.value
    }
    
    const goToPreviousPage = () => {
      if (currentPage.value > 1) {
        currentPage.value--
      }
    }
    
    const goToNextPage = () => {
      if (currentPage.value < totalPages.value) {
        currentPage.value++
      }
    }
    
    const goToPage = (page) => {
      if (typeof page === 'number' && page >= 1 && page <= totalPages.value) {
        currentPage.value = page
      }
    }
    
    const getPageNumbers = () => {
      const pages = []
      const total = totalPages.value
      const current = currentPage.value
      
      if (total <= 7) {
        for (let i = 1; i <= total; i++) {
          pages.push(i)
        }
      } else {
        pages.push(1)
        
        if (current > 3) {
          pages.push('...')
        }
        
        const start = Math.max(2, current - 1)
        const end = Math.min(total - 1, current + 1)
        
        for (let i = start; i <= end; i++) {
          pages.push(i)
        }
        
        if (current < total - 2) {
          pages.push('...')
        }
        
        pages.push(total)
      }
      
      return pages
    }
    
    // Следим за изменением запроса поиска и сбрасываем страницу
    watch(searchQuery, () => {
      currentPage.value = 1
    })
    
    // Следим за изменением количества записей на странице
    watch(rowsPerPage, () => {
      currentPage.value = 1
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
          // Для числовых полей - показываем распределение значений
          const numericValues = fieldData.filter(v => v !== null && v !== undefined).map(Number)
          if (numericValues.length > 0) {
            // Если уникальных значений немного (до 20), показываем все значения
            const uniqueValues = [...new Set(numericValues)]
            
            if (uniqueValues.length <= 20) {
              // Показываем количество каждого значения
              const counts = {}
              numericValues.forEach(value => {
                counts[value] = (counts[value] || 0) + 1
              })
              
              const sortedData = Object.entries(counts)
                .sort((a, b) => Number(a[0]) - Number(b[0]))
                .slice(0, 30)
              
              if (index === 0) {
                labels.push(...sortedData.map(([value]) => {
                  return field.field_type === 'integer' 
                    ? Math.round(Number(value)).toString()
                    : parseFloat(value).toFixed(2)
                }))
              }
              
              datasets.push({
                label: fieldName,
                data: sortedData.map(([, count]) => count),
                backgroundColor: colors[index % colors.length],
                borderColor: colors[index % colors.length].replace('0.8', '1'),
                borderWidth: 1
              })
            } else {
              // Если много уникальных значений - создаем гистограмму (группировка по интервалам)
              const min = Math.min(...numericValues)
              const max = Math.max(...numericValues)
              const range = max - min
              const bins = 15 // Количество интервалов
              const binSize = range / bins
              
              const histogram = Array(bins).fill(0)
              const binLabels = []
              
              // Создаем метки для интервалов
              for (let i = 0; i < bins; i++) {
                const binStart = min + i * binSize
                const binEnd = min + (i + 1) * binSize
                binLabels.push(
                  `${field.field_type === 'integer' ? Math.round(binStart) : binStart.toFixed(2)} - ${field.field_type === 'integer' ? Math.round(binEnd) : binEnd.toFixed(2)}`
                )
              }
              
              // Распределяем значения по интервалам
              numericValues.forEach(value => {
                let binIndex = Math.floor((value - min) / binSize)
                if (binIndex === bins) binIndex = bins - 1 // Последнее значение попадает в последний интервал
                histogram[binIndex]++
              })
              
              if (index === 0) {
                labels.push(...binLabels)
              }
              
              datasets.push({
                label: fieldName,
                data: histogram,
                backgroundColor: colors[index % colors.length],
                borderColor: colors[index % colors.length].replace('0.8', '1'),
                borderWidth: 1
              })
            }
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
      
      // Проверяем, что выбрано хотя бы одно поле
      if (exportOptions.value.selectedFields.length === 0) {
        window.$notify?.warning('Выберите поля', 'Выберите хотя бы одно поле для экспорта')
        return
      }
      
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
            include_descriptions: exportOptions.value.includeDescriptions,
            selected_fields: exportOptions.value.selectedFields.length > 0 
              ? exportOptions.value.selectedFields 
              : null // Если ничего не выбрано, экспортируем все поля
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
      
      // Проверяем, что выбрано хотя бы одно поле
      if (excelExportOptions.value.selectedFields.length === 0) {
        window.$notify?.warning('Выберите поля', 'Выберите хотя бы одно поле для экспорта')
        return
      }
      
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
            include_descriptions: excelExportOptions.value.includeDescriptions,
            selected_fields: excelExportOptions.value.selectedFields.length > 0 
              ? excelExportOptions.value.selectedFields 
              : null // Если ничего не выбрано, экспортируем все поля
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
      exportToExcel,
      selectAllFieldsForExport,
      deselectAllFieldsForExport,
      selectAllFieldsForExcelExport,
      deselectAllFieldsForExcelExport,
      // Данные для таблицы
      dataRecords,
      searchQuery,
      visibleColumns,
      showColumnSelector,
      visibleFields,
      filteredRecords,
      paginatedRecords,
      rowsPerPage,
      currentPage,
      totalPages,
      sortField,
      sortOrder,
      sortBy,
      getSortIcon,
      formatFieldValue,
      selectAllColumns,
      deselectAllColumns,
      goToFirstPage,
      goToLastPage,
      goToPreviousPage,
      goToNextPage,
      goToPage,
      getPageNumbers,
      loadDataRecords
    }
  }
}
</script>
