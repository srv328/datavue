<template>
  <div class="space-y-6">
    <!-- Вкладки администрирования -->
    <div class="border-b border-gray-200 dark:border-gray-700">
      <nav class="-mb-px flex space-x-8">
        <button
          v-for="tab in adminTabs"
          :key="tab.id"
          @click="activeAdminTab = tab.id"
          :class="[
            activeAdminTab === tab.id
              ? 'border-blue-500 text-blue-600 dark:text-blue-400'
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300',
            'whitespace-nowrap py-2 px-1 border-b-2 font-medium text-sm'
          ]"
        >
          {{ tab.name }}
        </button>
      </nav>
    </div>

    <!-- Управление типами данных -->
    <div v-if="activeAdminTab === 'data-types'" class="space-y-6">
      <!-- Создание нового типа данных -->
      <div class="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
        <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-4">
          Создать новый тип данных
        </h3>
        
        <form @submit.prevent="createDataType" class="space-y-4">
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Название типа данных
              </label>
              <input
                v-model="newDataType.name"
                type="text"
                required
                class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
                placeholder="Например: Недвижимость"
              >
            </div>
            
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Описание
              </label>
              <input
                v-model="newDataType.description"
                type="text"
                class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
                placeholder="Описание типа данных"
              >
            </div>
          </div>
          
          <button
            type="submit"
            :disabled="loading"
            class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
          >
            {{ loading ? 'Создание...' : 'Создать тип данных' }}
          </button>
        </form>
      </div>

      <!-- Список типов данных -->
      <div class="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
        <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-4">
          Существующие типы данных
        </h3>
        
        <div v-if="loading" class="text-center py-4">
          <div class="inline-block animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
        </div>
        
        <div v-else-if="dataTypes.length === 0" class="text-center py-8 text-gray-500 dark:text-gray-400">
          Нет созданных типов данных
        </div>
        
        <div v-else class="space-y-4">
          <div
            v-for="dataType in dataTypes"
            :key="dataType.id"
            class="border border-gray-200 dark:border-gray-600 rounded-lg p-4"
          >
            <div class="flex justify-between items-start">
              <div>
                <h4 class="font-medium text-gray-900 dark:text-white">
                  {{ dataType.name }}
                </h4>
                <p class="text-sm text-gray-600 dark:text-gray-400">
                  {{ dataType.description }}
                </p>
                <p class="text-xs text-gray-500 dark:text-gray-500 mt-1">
                  Создано: {{ formatDate(dataType.created_at) }}
                </p>
              </div>
              
              <div class="flex space-x-2">
                <button
                  @click="selectDataTypeForFields(dataType)"
                  class="px-3 py-1 text-sm bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300 rounded hover:bg-blue-200 dark:hover:bg-blue-800"
                >
                  Управление полями
                </button>
                <button
                  @click="confirmDeleteDataType(dataType)"
                  class="px-3 py-1 text-sm bg-red-100 dark:bg-red-900 text-red-700 dark:text-red-300 rounded hover:bg-red-200 dark:hover:bg-red-800"
                >
                  Удалить
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Управление полями выбранного типа данных -->
      <div v-if="selectedDataTypeForFields" class="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
        <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-4">
          Поля для: {{ selectedDataTypeForFields.name }}
        </h3>
        
        <!-- Добавление нового поля -->
        <form @submit.prevent="addField" class="space-y-4 mb-6">
          <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Название поля
              </label>
              <input
                v-model="newField.field_name"
                type="text"
                required
                class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
                placeholder="Например: price"
              >
            </div>
            
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Тип поля
              </label>
              <select
                v-model="newField.field_type"
                @change="onFieldTypeChange"
                required
                class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
              >
                <option value="text">Текст</option>
                <option value="integer">Целое число</option>
                <option value="decimal">Десятичное число</option>
                <option value="date">Дата</option>
                <option value="boolean">Да/Нет</option>
                <option value="enum">Перечислимое значение</option>
                <option value="coordinates">Координаты</option>
              </select>
            </div>
            
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Описание
              </label>
              <input
                v-model="newField.description"
                type="text"
                class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
                placeholder="Описание поля"
              >
            </div>
            
            <div class="flex items-end">
              <label class="flex items-center">
                <input
                  v-model="newField.is_required"
                  type="checkbox"
                  class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                >
                <span class="ml-2 text-sm text-gray-700 dark:text-gray-300">
                  Обязательное
                </span>
              </label>
            </div>
          </div>
          
          <!-- Поле для ввода значений enum -->
          <div v-if="newField.field_type === 'enum'" class="mt-4 p-4 bg-blue-50 dark:bg-blue-900 rounded-lg border border-blue-200 dark:border-blue-700">
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Значения справочника (по одному на строку)
            </label>
            <textarea
              v-model="newField.enum_values_text"
              rows="5"
              placeholder="Например:&#10;Значение 1&#10;Значение 2&#10;Значение 3"
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
            ></textarea>
            <p class="mt-2 text-xs text-gray-600 dark:text-gray-400">
              Введите возможные значения для перечислимого поля, каждое значение на новой строке
            </p>
          </div>
          
          <button
            type="submit"
            :disabled="loading"
            class="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 disabled:opacity-50"
          >
            {{ loading ? 'Добавление...' : 'Добавить поле' }}
          </button>
        </form>
        
        <!-- Список полей -->
        <div v-if="dataFields.length === 0" class="text-center py-8 text-gray-500 dark:text-gray-400">
          Нет добавленных полей
        </div>
        
        <div v-else class="space-y-2">
          <div
            v-for="field in dataFields"
            :key="field.id"
            class="flex justify-between items-center p-3 border border-gray-200 dark:border-gray-600 rounded-lg"
          >
            <div>
              <span class="font-medium text-gray-900 dark:text-white">
                {{ field.field_name }}
              </span>
              <span class="ml-2 text-sm text-gray-500 dark:text-gray-400">
                ({{ getFieldTypeName(field.field_type) }})
              </span>
              <span v-if="field.is_required" class="ml-2 text-xs text-red-600 dark:text-red-400">
                Обязательное
              </span>
              <p v-if="field.description" class="text-sm text-gray-600 dark:text-gray-400">
                {{ field.description }}
              </p>
              <p v-if="field.field_type === 'enum' && field.enum_values && field.enum_values.length > 0" class="text-xs text-gray-500 dark:text-gray-500 mt-1">
                Значения: {{ field.enum_values.join(', ') }}
              </p>
            </div>
            
            <div class="flex space-x-2">
              <button
                @click="deleteField(field.id, field.field_name)"
                class="px-3 py-1 text-sm bg-red-100 dark:bg-red-900 text-red-700 dark:text-red-300 rounded hover:bg-red-200 dark:hover:bg-red-800"
                title="Удалить поле"
              >
                Удалить
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Управление пользователями -->
    <div v-if="activeAdminTab === 'users'" class="space-y-6">
      <!-- Автоматическая генерация пользователей -->
      <div class="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
        <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-4">
          Автоматическая генерация пользователей
        </h3>
        
        <form @submit.prevent="generateUsers" class="space-y-4">
          <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Количество пользователей
              </label>
              <input
                v-model.number="generateForm.count"
                type="number"
                min="1"
                max="100"
                required
                class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
                placeholder="Введите количество"
              >
            </div>
            
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Роль
              </label>
              <select
                v-model="generateForm.role"
                required
                class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
              >
                <option value="user">Пользователь</option>
                <option value="admin">Администратор</option>
              </select>
            </div>
            
            <div class="flex items-end">
              <button
                type="submit"
                :disabled="loading"
                class="w-full px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 disabled:opacity-50"
              >
                {{ loading ? 'Генерация...' : 'Сгенерировать пользователей' }}
              </button>
            </div>
          </div>
        </form>
        
        <!-- Результаты генерации -->
        <div v-if="generatedUsers.length > 0" class="mt-6">
          <h4 class="text-md font-medium text-gray-900 dark:text-white mb-3">
            Созданные пользователи:
          </h4>
          <div class="bg-gray-50 dark:bg-gray-700 rounded-lg p-4 max-h-60 overflow-y-auto">
            <div v-for="user in generatedUsers" :key="user.id" class="mb-2 p-2 bg-white dark:bg-gray-800 rounded border">
              <div class="flex justify-between items-center">
                <div class="flex items-center space-x-2">
                  <span class="font-medium text-gray-900 dark:text-white">{{ user.username }}</span>
                  <span class="text-gray-400">:</span>
                  <span class="font-mono text-sm text-gray-600 dark:text-gray-400">{{ user.password }}</span>
                  <button
                    @click="copyCredentials(user.username, user.password)"
                    class="p-1 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
                    title="Копировать логин:пароль"
                  >
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"></path>
                    </svg>
                  </button>
                  <span class="text-xs text-gray-500 dark:text-gray-400">
                    ({{ user.role === 'admin' ? 'Администратор' : 'Пользователь' }})
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Создание нового пользователя -->
      <div class="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
        <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-4">
          Создать пользователя вручную
        </h3>
        
        <form @submit.prevent="createUser" class="space-y-4">
          <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Имя пользователя
              </label>
              <input
                v-model="newUser.username"
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
                v-model="newUser.password"
                type="password"
                required
                class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
                placeholder="Введите пароль"
              >
            </div>
            
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                ФИО (необязательно)
              </label>
              <input
                v-model="newUser.full_name"
                type="text"
                class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
                placeholder="Введите ФИО"
              >
            </div>
            
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Роль
              </label>
              <select
                v-model="newUser.role"
                required
                class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
              >
                <option value="user">Пользователь</option>
                <option value="admin">Администратор</option>
              </select>
            </div>
          </div>
          
          <button
            type="submit"
            :disabled="loading"
            class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
          >
            {{ loading ? 'Создание...' : 'Создать пользователя' }}
          </button>
        </form>
      </div>

      <!-- Список пользователей -->
      <div class="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
        <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-4">
          Пользователи системы
        </h3>
        
        <div v-if="loading" class="text-center py-4">
          <div class="inline-block animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
        </div>
        
        <div v-else-if="users.length === 0" class="text-center py-8 text-gray-500 dark:text-gray-400">
          Нет пользователей
        </div>
        
        <div v-else class="overflow-x-auto">
          <table class="w-full divide-y divide-gray-200 dark:divide-gray-700">
            <thead class="bg-gray-50 dark:bg-gray-700">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  Имя пользователя
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  ФИО
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  Роль
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  Дата создания
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  Статус
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  Действия
                </th>
              </tr>
            </thead>
            <tbody class="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
              <tr v-for="user in paginatedUsers" :key="user.id">
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                  <div class="flex items-center">
                    <span>{{ user.username }}</span>
                    <button
                      @click="copyToClipboard(user.username)"
                      class="ml-2 p-1 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
                      title="Копировать логин"
                    >
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"></path>
                      </svg>
                    </button>
                  </div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                  <div class="flex items-center">
                    <span v-if="editingUser !== user.id">{{ user.full_name || '-' }}</span>
                    <input
                      v-else
                      v-model="editFullName"
                      @blur="saveFullName(user.id)"
                      @keyup.enter="saveFullName(user.id)"
                      @keyup.escape="cancelEdit"
                      class="w-full px-2 py-1 text-sm border border-gray-300 dark:border-gray-600 rounded dark:bg-gray-700 dark:text-white"
                      placeholder="Введите ФИО"
                      ref="editInput"
                    >
                    <button
                      v-if="editingUser !== user.id"
                      @click="startEditFullName(user)"
                      class="ml-2 p-1 text-gray-400 hover:text-blue-600 dark:hover:text-blue-400"
                      title="Редактировать ФИО"
                    >
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
                      </svg>
                    </button>
                  </div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                  <span class="px-2 py-1 text-xs rounded" :class="user.role === 'admin' ? 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200' : 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200'">
                    {{ user.role === 'admin' ? 'Администратор' : 'Пользователь' }}
                  </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                  {{ formatDate(user.created_at) }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                  <span class="px-2 py-1 text-xs rounded" :class="user.is_active ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' : 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'">
                    {{ user.is_active ? 'Активен' : 'Заблокирован' }}
                  </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                  <div class="flex space-x-2">
                    <button
                      @click="resetPassword(user.id)"
                      class="p-1 text-blue-400 hover:text-blue-600 dark:hover:text-blue-300"
                      title="Сбросить пароль"
                    >
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z"></path>
                      </svg>
                    </button>
                    <button
                      @click="deleteUser(user.id, user.username)"
                      :disabled="user.id === currentUserId"
                      class="p-1 text-red-400 hover:text-red-600 dark:hover:text-red-300 disabled:opacity-50 disabled:cursor-not-allowed"
                      :title="user.id === currentUserId ? 'Нельзя удалить собственный аккаунт' : 'Удалить пользователя'"
                    >
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
                      </svg>
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
          
          <!-- Пагинация для пользователей -->
          <div v-if="users.length > 0" class="px-6 py-3 bg-gray-50 dark:bg-gray-700 border-t border-gray-200 dark:border-gray-600 flex flex-col lg:flex-row justify-between items-start lg:items-center gap-4 text-sm text-gray-600 dark:text-gray-300">
            <!-- Информация о записях -->
            <div class="flex flex-col sm:flex-row gap-2 sm:gap-4">
              <span>Показано {{ (currentUsersPage - 1) * usersPerPage + 1 }}-{{ Math.min(currentUsersPage * usersPerPage, users.length) }} из {{ users.length }} пользователей</span>
            </div>
            
            <!-- Элементы управления пагинацией -->
            <div class="flex flex-col sm:flex-row items-start sm:items-center gap-4 w-full lg:w-auto">
              <!-- Выбор количества пользователей на странице -->
              <div class="flex items-center gap-2">
                <span>Пользователей на странице:</span>
                <select v-model="usersPerPage"
                  class="w-20 p-1 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-200 text-sm">
                  <option value="5">5</option>
                  <option value="10">10</option>
                  <option value="20">20</option>
                  <option value="50">50</option>
                </select>
              </div>
              
              <!-- Навигация по страницам -->
              <div class="flex items-center gap-1">
                <!-- Первая страница -->
                <button @click="goToFirstUsersPage" :disabled="currentUsersPage === 1"
                  class="px-2 py-1 border border-gray-300 dark:border-gray-600 rounded disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-100 dark:hover:bg-gray-600 text-sm"
                  title="Первая страница">
                  ⏮
                </button>
                
                <!-- Предыдущая страница -->
                <button @click="goToPreviousUsersPage" :disabled="currentUsersPage === 1"
                  class="px-2 py-1 border border-gray-300 dark:border-gray-600 rounded disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-100 dark:hover:bg-gray-600 text-sm"
                  title="Предыдущая страница">
                  ←
                </button>
                
                <!-- Номера страниц -->
                <div class="flex gap-1">
                  <button v-for="page in getUsersPageNumbers()" :key="page"
                    @click="page !== '...' && goToUsersPage(page)"
                    :disabled="page === '...'"
                    :class="[
                      'px-3 py-1 text-sm border rounded transition-colors',
                      page === currentUsersPage 
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
                <button @click="goToNextUsersPage" :disabled="currentUsersPage === totalUsersPages"
                  class="px-2 py-1 border border-gray-300 dark:border-gray-600 rounded disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-100 dark:hover:bg-gray-600 text-sm"
                  title="Следующая страница">
                  →
                </button>
                
                <!-- Последняя страница -->
                <button @click="goToLastUsersPage" :disabled="currentUsersPage === totalUsersPages"
                  class="px-2 py-1 border border-gray-300 dark:border-gray-600 rounded disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-100 dark:hover:bg-gray-600 text-sm"
                  title="Последняя страница">
                  ⏭
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Управление правами доступа -->
    <div v-if="activeAdminTab === 'permissions'" class="space-y-6">
      <!-- Выбор пользователя -->
      <div class="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
        <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-4">
          Настройка прав на редактирование
        </h3>
        
        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Выберите пользователя
          </label>
          <select
            v-model="selectedUserForPermissions"
            @change="loadUserPermissions"
            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
          >
            <option value="">Выберите пользователя...</option>
            <option v-for="user in users" :key="user.id" :value="user.id">
              {{ user.username }} ({{ user.full_name || 'Без ФИО' }})
            </option>
          </select>
        </div>
      </div>

      <!-- Права доступа выбранного пользователя -->
      <div v-if="selectedUserForPermissions" class="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
        <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-4">
          Права на редактирование для: {{ getSelectedUserName() }}
        </h3>
        <p class="text-sm text-gray-600 dark:text-gray-400 mb-4">
          Все пользователи могут просматривать данные по умолчанию. Отметьте галочками таблицы, которые пользователь может редактировать.
        </p>
        
        <div v-if="loading" class="text-center py-4">
          <div class="inline-block animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
        </div>
        
        <div v-else-if="dataTypes.length === 0" class="text-center py-8 text-gray-500 dark:text-gray-400">
          Нет типов данных для настройки прав
        </div>
        
        <div v-else class="space-y-4">
          <div
            v-for="dataType in dataTypes"
            :key="dataType.id"
            class="border border-gray-200 dark:border-gray-600 rounded-lg p-4"
          >
            <div class="flex justify-between items-start">
              <div class="flex-1">
                <h4 class="font-medium text-gray-900 dark:text-white">
                  {{ dataType.name }}
                </h4>
                <p class="text-sm text-gray-600 dark:text-gray-400">
                  {{ dataType.description }}
                </p>
              </div>
              
              <div class="ml-4">
                <label class="flex items-center">
                  <input
                    :checked="getUserPermission(dataType.id) === 'write'"
                    @change="updateUserPermission(dataType.id, $event.target.checked)"
                    type="checkbox"
                    class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                  >
                  <span class="ml-2 text-sm text-gray-700 dark:text-gray-300">
                    Может редактировать
                  </span>
                </label>
              </div>
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
  name: 'AdminPanel',
  setup() {
    const activeAdminTab = ref('data-types')
    const dataTypes = ref([])
    const users = ref([])
    const selectedDataTypeForFields = ref(null)
    const dataFields = ref([])
    const loading = ref(false)
    
    // Пагинация для пользователей
    const usersPerPage = ref(10)
    const currentUsersPage = ref(1)
    
    // Пагинация для типов данных
    const dataTypesPerPage = ref(5)
    const currentDataTypesPage = ref(1)
    
    const newDataType = ref({
      name: '',
      description: ''
    })
    
    const newField = ref({
      field_name: '',
      field_type: 'text',
      description: '',
      is_required: false,
      enum_values_text: ''
    })
    
    const newUser = ref({
      username: '',
      password: '',
      full_name: '',
      role: 'user'
    })
    
    const generateForm = ref({
      count: 5,
      role: 'user'
    })
    
    const generatedUsers = ref([])
    
    // Состояние для редактирования ФИО
    const editingUser = ref(null)
    const editFullName = ref('')
    const editInput = ref(null)
    const currentUserId = ref(null)
    
    // Переменные для управления правами доступа
    const selectedUserForPermissions = ref('')
    const userPermissions = ref({})
    
    const adminTabs = [
      { id: 'data-types', name: 'Типы данных' },
      { id: 'users', name: 'Пользователи' },
      { id: 'permissions', name: 'Права доступа' }
    ]
    
    // Computed свойства для пагинации пользователей
    const totalUsersPages = computed(() => {
      return Math.ceil(users.value.length / usersPerPage.value)
    })
    
    const paginatedUsers = computed(() => {
      const start = (currentUsersPage.value - 1) * usersPerPage.value
      const end = start + usersPerPage.value
      return users.value.slice(start, end)
    })
    
    const loadDataTypes = async () => {
      try {
        const response = await fetch('http://localhost:5000/api/data-types', {
          credentials: 'include'
        })
        
        if (response.ok) {
          dataTypes.value = await response.json()
        }
      } catch (err) {
        console.error('Ошибка загрузки типов данных:', err)
      }
    }
    
    const loadUsers = async () => {
      try {
        const response = await fetch('http://localhost:5000/api/users', {
          credentials: 'include'
        })
        
        if (response.ok) {
          users.value = await response.json()
        }
      } catch (err) {
        console.error('Ошибка загрузки пользователей:', err)
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
    
    const createDataType = async () => {
      loading.value = true
      try {
        const response = await fetch('http://localhost:5000/api/data-types', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          credentials: 'include',
          body: JSON.stringify(newDataType.value)
        })
        
        if (response.ok) {
          newDataType.value = { name: '', description: '' }
          await loadDataTypes()
        } else {
          const error = await response.json()
          window.$notify?.error('Ошибка создания типа данных', error.error)
        }
      } catch (err) {
        console.error('Ошибка создания типа данных:', err)
        window.$notify?.error('Ошибка соединения', 'Не удалось подключиться к серверу')
      } finally {
        loading.value = false
      }
    }
    
    const addField = async () => {
      loading.value = true
      try {
        // Подготавливаем данные для отправки
        const fieldData = {
          field_name: newField.value.field_name,
          field_type: newField.value.field_type,
          description: newField.value.description,
          is_required: newField.value.is_required
        }
        
        // Если тип enum, добавляем значения справочника
        if (newField.value.field_type === 'enum') {
          // Разбиваем текст на массив значений, убирая пустые строки
          const enumValues = newField.value.enum_values_text
            .split('\n')
            .map(v => v.trim())
            .filter(v => v.length > 0)
          
          if (enumValues.length === 0) {
            window.$notify?.error('Ошибка', 'Для перечислимого поля необходимо указать хотя бы одно значение')
            loading.value = false
            return
          }
          
          fieldData.enum_values = enumValues
        }
        
        const response = await fetch(`http://localhost:5000/api/data-types/${selectedDataTypeForFields.value.id}/fields`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          credentials: 'include',
          body: JSON.stringify(fieldData)
        })
        
        if (response.ok) {
          newField.value = {
            field_name: '',
            field_type: 'text',
            description: '',
            is_required: false,
            enum_values_text: ''
          }
          await loadDataFields(selectedDataTypeForFields.value.id)
        } else {
          const error = await response.json()
          window.$notify?.error('Ошибка добавления поля', error.error)
        }
      } catch (err) {
        console.error('Ошибка добавления поля:', err)
        window.$notify?.error('Ошибка соединения', 'Не удалось подключиться к серверу')
      } finally {
        loading.value = false
      }
    }
    
    const onFieldTypeChange = () => {
      // Сбрасываем значения enum при смене типа поля
      if (newField.value.field_type !== 'enum') {
        newField.value.enum_values_text = ''
      }
    }
    
    const createUser = async () => {
      loading.value = true
      try {
        const response = await fetch('http://localhost:5000/api/users', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          credentials: 'include',
          body: JSON.stringify(newUser.value)
        })
        
        if (response.ok) {
          newUser.value = { username: '', password: '', full_name: '', role: 'user' }
          await loadUsers()
        } else {
          const error = await response.json()
          window.$notify?.error('Ошибка создания пользователя', error.error)
        }
      } catch (err) {
        console.error('Ошибка создания пользователя:', err)
        window.$notify?.error('Ошибка соединения', 'Не удалось подключиться к серверу')
      } finally {
        loading.value = false
      }
    }
    
    const generateUsers = async () => {
      loading.value = true
      try {
        const response = await fetch('http://localhost:5000/api/users/generate', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          credentials: 'include',
          body: JSON.stringify(generateForm.value)
        })
        
        if (response.ok) {
          const data = await response.json()
          generatedUsers.value = data.users
          await loadUsers()
          window.$notify?.success('Пользователи созданы', `Успешно создано ${data.users.length} пользователей!`)
        } else {
          const error = await response.json()
          window.$notify?.error('Ошибка генерации пользователей', error.error)
        }
      } catch (err) {
        console.error('Ошибка генерации пользователей:', err)
        window.$notify?.error('Ошибка соединения', 'Не удалось подключиться к серверу')
      } finally {
        loading.value = false
      }
    }
    
    const copyToClipboard = async (text) => {
      try {
        await navigator.clipboard.writeText(text)
        window.$notify?.success('Скопировано', 'Текст скопирован в буфер обмена!')
      } catch (err) {
        // Fallback для старых браузеров
        const textArea = document.createElement('textarea')
        textArea.value = text
        document.body.appendChild(textArea)
        textArea.select()
        document.execCommand('copy')
        document.body.removeChild(textArea)
        window.$notify?.success('Скопировано', 'Текст скопирован в буфер обмена!')
      }
    }
    
    // Функции пагинации пользователей
    const goToUsersPage = (page) => {
      if (page >= 1 && page <= totalUsersPages.value) {
        currentUsersPage.value = page
      }
    }
    
    const goToPreviousUsersPage = () => {
      goToUsersPage(Math.max(1, currentUsersPage.value - 1))
    }
    
    const goToNextUsersPage = () => {
      goToUsersPage(Math.min(totalUsersPages.value, currentUsersPage.value + 1))
    }
    
    const goToFirstUsersPage = () => {
      goToUsersPage(1)
    }
    
    const goToLastUsersPage = () => {
      goToUsersPage(totalUsersPages.value)
    }
    
    const getUsersPageNumbers = () => {
      const total = totalUsersPages.value
      const current = currentUsersPage.value
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
    
    const copyCredentials = async (username, password) => {
      const credentials = `${username}:${password}`
      await copyToClipboard(credentials)
    }
    
    const resetPassword = async (userId) => {
      try {
        const response = await fetch(`http://localhost:5000/api/users/${userId}/reset-password`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          credentials: 'include'
        })
        
        if (response.ok) {
          const data = await response.json()
          // Показываем новые учетные данные
          const credentials = `${data.username}:${data.password}`
          await copyToClipboard(credentials)
          window.$notify?.success('Пароль сброшен', `Новые учетные данные скопированы: ${credentials}`)
        } else {
          let errorMessage = 'Не удалось сбросить пароль'
          try {
            const data = await response.json()
            errorMessage = data.error || errorMessage
          } catch (e) {
            // Если не удалось распарсить JSON, используем статус код
            if (response.status === 404) {
              errorMessage = 'Сервер не запущен или API недоступен'
            } else if (response.status === 500) {
              errorMessage = 'Ошибка сервера'
            }
          }
          window.$notify?.error('Ошибка', errorMessage)
        }
      } catch (error) {
        console.error('Ошибка при сбросе пароля:', error)
        window.$notify?.error('Ошибка', 'Не удалось сбросить пароль')
      }
    }
    
    const startEditFullName = (user) => {
      editingUser.value = user.id
      editFullName.value = user.full_name || ''
      // Фокусируемся на поле ввода после следующего рендера
      setTimeout(() => {
        if (editInput.value) {
          editInput.value.focus()
          editInput.value.select()
        }
      }, 0)
    }
    
    const saveFullName = async (userId) => {
      if (editingUser.value !== userId) return
      
      try {
        const response = await fetch(`http://localhost:5000/api/users/${userId}`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
          },
          credentials: 'include',
          body: JSON.stringify({ full_name: editFullName.value })
        })
        
        if (response.ok) {
          await loadUsers()
          editingUser.value = null
          editFullName.value = ''
          window.$notify?.success('ФИО обновлено', 'ФИО пользователя успешно обновлено')
        } else {
          const error = await response.json()
          window.$notify?.error('Ошибка обновления ФИО', error.error)
        }
      } catch (err) {
        console.error('Ошибка обновления ФИО:', err)
        window.$notify?.error('Ошибка соединения', 'Не удалось подключиться к серверу')
      }
    }
    
    const cancelEdit = () => {
      editingUser.value = null
      editFullName.value = ''
    }
    
    const deleteField = async (fieldId, fieldName) => {
      const confirmed = await window.$modal?.confirm({
        title: 'Удаление поля',
        message: `Вы уверены, что хотите удалить поле "${fieldName}"? Это действие нельзя отменить.`,
        type: 'danger',
        confirmText: 'Удалить',
        cancelText: 'Отмена'
      })
      
      if (!confirmed) return
      
      loading.value = true
      try {
        const response = await fetch(`http://localhost:5000/api/data-types/${selectedDataTypeForFields.value.id}/fields/${fieldId}`, {
          method: 'DELETE',
          credentials: 'include'
        })
        
        if (response.ok) {
          await loadDataFields(selectedDataTypeForFields.value.id)
          window.$notify?.success('Поле удалено', `Поле "${fieldName}" успешно удалено`)
        } else {
          const error = await response.json()
          window.$notify?.error('Ошибка удаления поля', error.error)
        }
      } catch (err) {
        console.error('Ошибка удаления поля:', err)
        window.$notify?.error('Ошибка соединения', 'Не удалось подключиться к серверу')
      } finally {
        loading.value = false
      }
    }
    
    const confirmDeleteDataType = async (dataType) => {
      const confirmed = await window.$modal?.confirm({
        title: 'Удаление типа данных',
        message: `Вы уверены, что хотите удалить тип данных "${dataType.name}"? Это действие удалит ВСЕ данные, поля и записи, связанные с этим типом. Действие нельзя отменить.`,
        type: 'danger',
        confirmText: 'Удалить',
        cancelText: 'Отмена'
      })
      
      if (!confirmed) return
      
      loading.value = true
      try {
        const response = await fetch(`http://localhost:5000/api/data-types/${dataType.id}`, {
          method: 'DELETE',
          credentials: 'include'
        })
        
        if (response.ok) {
          await loadDataTypes()
          // Сбрасываем выбранный тип данных, если он был удален
          if (selectedDataTypeForFields.value?.id === dataType.id) {
            selectedDataTypeForFields.value = null
            dataFields.value = []
          }
          window.$notify?.success('Тип данных удален', `Тип данных "${dataType.name}" и все связанные данные успешно удалены`)
        } else {
          const error = await response.json()
          window.$notify?.error('Ошибка удаления типа данных', error.error)
        }
      } catch (err) {
        console.error('Ошибка удаления типа данных:', err)
        window.$notify?.error('Ошибка соединения', 'Не удалось подключиться к серверу')
      } finally {
        loading.value = false
      }
    }
    
    const deleteUser = async (userId, username) => {
      const confirmed = await window.$modal?.confirm({
        title: 'Удаление пользователя',
        message: `Вы уверены, что хотите удалить пользователя "${username}"? Это действие нельзя отменить.`,
        type: 'danger',
        confirmText: 'Удалить',
        cancelText: 'Отмена'
      })
      
      if (!confirmed) return
      
      try {
        const response = await fetch(`http://localhost:5000/api/users/${userId}`, {
          method: 'DELETE',
          credentials: 'include'
        })
        
        if (response.ok) {
          await loadUsers()
          window.$notify?.success('Пользователь удален', `Пользователь "${username}" успешно удален`)
        } else {
          const error = await response.json()
          window.$notify?.error('Ошибка удаления пользователя', error.error)
        }
      } catch (err) {
        console.error('Ошибка удаления пользователя:', err)
        window.$notify?.error('Ошибка соединения', 'Не удалось подключиться к серверу')
      }
    }
    
    const selectDataTypeForFields = async (dataType) => {
      selectedDataTypeForFields.value = dataType
      await loadDataFields(dataType.id)
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
    
    const loadUserPermissions = async () => {
      if (!selectedUserForPermissions.value) {
        userPermissions.value = {}
        return
      }
      
      try {
        const response = await fetch(`http://localhost:5000/api/users/${selectedUserForPermissions.value}/permissions`, {
          credentials: 'include'
        })
        
        if (response.ok) {
          const permissions = await response.json()
          userPermissions.value = {}
          permissions.forEach(permission => {
            userPermissions.value[permission.data_type_id] = permission.permission_type
          })
        }
      } catch (err) {
        console.error('Ошибка загрузки прав пользователя:', err)
      }
    }
    
    const updateUserPermission = async (dataTypeId, canEdit) => {
      try {
        const url = `http://localhost:5000/api/users/${selectedUserForPermissions.value}/permissions/${dataTypeId}`
        
        if (!canEdit) {
          // Удаляем разрешение на редактирование (оставляем только просмотр)
          const response = await fetch(url, {
            method: 'DELETE',
            credentials: 'include'
          })
          
          if (response.ok) {
            delete userPermissions.value[dataTypeId]
            window.$notify?.success('Право на редактирование отозвано', 'Пользователь может только просматривать данные')
          } else {
            const error = await response.json()
            window.$notify?.error('Ошибка отзыва права', error.error)
          }
        } else {
          // Устанавливаем разрешение на редактирование
          const response = await fetch(url, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            credentials: 'include',
            body: JSON.stringify({ permission_type: 'write' })
          })
          
          if (response.ok) {
            userPermissions.value[dataTypeId] = 'write'
            window.$notify?.success('Право на редактирование выдано', 'Пользователь может редактировать данные')
          } else {
            const error = await response.json()
            window.$notify?.error('Ошибка выдачи права', error.error)
          }
        }
      } catch (err) {
        console.error('Ошибка обновления права доступа:', err)
        window.$notify?.error('Ошибка соединения', 'Не удалось подключиться к серверу')
      }
    }
    
    const getUserPermission = (dataTypeId) => {
      return userPermissions.value[dataTypeId] || ''
    }
    
    const getSelectedUserName = () => {
      const user = users.value.find(u => u.id == selectedUserForPermissions.value)
      return user ? `${user.username} (${user.full_name || 'Без ФИО'})` : ''
    }
    
    onMounted(async () => {
      loadDataTypes()
      loadUsers()
      
      // Получаем ID текущего пользователя
      try {
        const response = await fetch('http://localhost:5000/api/auth/me', {
          credentials: 'include'
        })
        if (response.ok) {
          const user = await response.json()
          currentUserId.value = user.id
        }
      } catch (err) {
        console.error('Ошибка получения текущего пользователя:', err)
      }
    })
    
    watch(activeAdminTab, () => {
      if (activeAdminTab.value === 'users') {
        loadUsers()
      }
    })
    
    return {
      activeAdminTab,
      dataTypes,
      users,
      selectedDataTypeForFields,
      dataFields,
      loading,
      newDataType,
      newField,
      newUser,
      generateForm,
      generatedUsers,
      editingUser,
      editFullName,
      editInput,
      currentUserId,
      selectedUserForPermissions,
      userPermissions,
      adminTabs,
      // Пагинация пользователей
      usersPerPage,
      currentUsersPage,
      totalUsersPages,
      paginatedUsers,
      goToUsersPage,
      goToPreviousUsersPage,
      goToNextUsersPage,
      goToFirstUsersPage,
      goToLastUsersPage,
      getUsersPageNumbers,
      createDataType,
      addField,
      deleteField,
      confirmDeleteDataType,
      createUser,
      generateUsers,
      copyToClipboard,
      copyCredentials,
      resetPassword,
      startEditFullName,
      saveFullName,
      cancelEdit,
      deleteUser,
      selectDataTypeForFields,
      loadUserPermissions,
      updateUserPermission,
      getUserPermission,
      getSelectedUserName,
      formatDate,
      getFieldTypeName,
      onFieldTypeChange
    }
  }
}
</script>
