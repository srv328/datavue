<script setup>
import { ref, onMounted } from 'vue';
import DataService from './services/DataService.js';
import DataTable from './components/DataTable.vue';
import DataStats from './components/DataStats.vue';
import DataCharts from './components/DataCharts.vue';

const activeTab = ref('table');
const loading = ref(true);
const data = ref([]);
const stats = ref(null);
const features = ref([]);
const menuItems = ref([
	{
		label: 'Таблица данных',
		icon: 'pi pi-table',
		command: () => setActiveTab('table'),
		class: activeTab.value === 'table' ? 'active-tab' : ''
	},
	{
		label: 'Статистика',
		icon: 'pi pi-chart-bar',
		command: () => setActiveTab('stats'),
		class: activeTab.value === 'stats' ? 'active-tab' : ''
	},
	{
		label: 'Графики',
		icon: 'pi pi-chart-line',
		command: () => setActiveTab('charts'),
		class: activeTab.value === 'charts' ? 'active-tab' : ''
	}
]);
const darkMode = ref(false);

onMounted(async () => {
	try {
		data.value = await DataService.getData();

		stats.value = await DataService.getStats();

		features.value = await DataService.getFeatures();

		loading.value = false;
	} catch (error) {
		loading.value = false;
	}
});

const setActiveTab = (tab) => {
	activeTab.value = tab;
	menuItems.value.forEach(item => {
		item.class = item.label.toLowerCase().includes(tab) ? 'active-tab' : '';
	});
};

const toggleDarkMode = () => {
	darkMode.value = !darkMode.value;
	document.documentElement.classList.toggle('dark', darkMode.value);

	if (darkMode.value) {
		setTimeout(() => {
			const tables = document.querySelectorAll('.p-datatable');
			tables.forEach(table => {
				const cells = table.querySelectorAll('td, th');
				cells.forEach(cell => {
					cell.style.color = '#e5e7eb';
				});
			});

			const cards = document.querySelectorAll('.p-card');
			cards.forEach(card => {
				const elements = card.querySelectorAll('*');
				elements.forEach(el => {
					el.style.color = '#e5e7eb';
				});
			});
		}, 100);
	}
};
</script>

<template>
	<div class="min-h-screen flex flex-col bg-gray-50 dark:bg-gray-900" :class="{ 'dark': darkMode }">
		<Toast position="top-right" />

		<nav class="bg-white dark:bg-gray-800 shadow-md">
			<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
				<div class="flex justify-between h-16">
					<div class="flex items-center">
						<div class="flex-shrink-0 flex items-center">
							<i class="pi pi-chart-line text-green-600 dark:text-green-400 text-2xl mr-2"></i>
							<span class="font-bold text-xl text-green-600 dark:text-green-400">DataVue</span>
						</div>
					</div>
					<div class="flex items-center space-x-4">
						<button @click="toggleDarkMode"
							class="p-2 rounded-full text-gray-500 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 focus:outline-none">
							<i :class="darkMode ? 'pi pi-moon' : 'pi pi-sun'" class="text-lg"></i>
						</button>
					</div>
				</div>
			</div>
		</nav>

		<main class="flex-grow">
			<div class="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
				<div class="px-4 py-6 sm:px-0">
					<div class="bg-white dark:bg-gray-800 overflow-hidden shadow-md rounded-lg mb-6">
						<div class="px-4 py-5 sm:p-6">
							<h1 class="text-2xl font-bold text-gray-900 dark:text-white">
								Анализ данных о недвижимости Калифорнии
							</h1>
						</div>
					</div>
					<div class="bg-white dark:bg-gray-800 shadow-md rounded-lg mb-6">
						<div class="border-b border-gray-200 dark:border-gray-700">
							<nav class="flex -mb-px">
								<button @click="setActiveTab('table')" :class="[
									activeTab === 'table'
										? 'border-green-500 text-green-600 dark:text-green-400'
										: 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 hover:border-gray-300',
									'group inline-flex items-center py-4 px-6 border-b-2 font-medium text-sm'
								]">
									<i class="pi pi-table mr-2"></i>
									Таблица данных
								</button>
								<button @click="setActiveTab('stats')" :class="[
									activeTab === 'stats'
										? 'border-green-500 text-green-600 dark:text-green-400'
										: 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 hover:border-gray-300',
									'group inline-flex items-center py-4 px-6 border-b-2 font-medium text-sm'
								]">
									<i class="pi pi-chart-bar mr-2"></i>
									Статистика
								</button>
								<button @click="setActiveTab('charts')" :class="[
									activeTab === 'charts'
										? 'border-green-500 text-green-600 dark:text-green-400'
										: 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 hover:border-gray-300',
									'group inline-flex items-center py-4 px-6 border-b-2 font-medium text-sm'
								]">
									<i class="pi pi-chart-line mr-2"></i>
									Графики
								</button>
							</nav>
						</div>
					</div>
					<div class="bg-white dark:bg-gray-800 overflow-hidden shadow-md rounded-lg">
						<div class="px-4 py-5 sm:p-6">
							<div v-if="loading" class="flex justify-center py-12">
								<div class="animate-spin rounded-full h-8 w-8 border-b-2 border-green-500"></div>
							</div>
							<div v-else>
								<DataTable v-if="activeTab === 'table' && data && data.length > 0" :data="data"
									:features="features" />
								<DataStats v-if="activeTab === 'stats' && stats" :stats="stats" :features="features" />
								<DataCharts v-if="activeTab === 'charts' && data && data.length > 0" :data="data"
									:features="features" />
								<div v-if="!loading && (!data || data.length === 0)"
									class="text-center py-12 text-gray-500">
									<p>Данные не загружены</p>
								</div>
							</div>
						</div>
					</div>
				</div>
			</div>
		</main>
	</div>
</template>

<style>
:deep(.p-component) {
	font-family: sans-serif;
}

:deep(.p-datatable) {
	border-radius: 0.5rem;
	overflow: hidden;
}

:deep(.p-datatable .p-datatable-header) {
	background-color: #f9fafb;
	border-bottom: 1px solid #e5e7eb;
	padding: 1rem;
}

:deep(.p-datatable .p-datatable-thead > tr > th) {
	background-color: #f3f4f6;
	color: #374151;
	border-bottom: 1px solid #e5e7eb;
	padding: 0.75rem;
}

:deep(.p-datatable .p-datatable-tbody > tr) {
	border-bottom: 1px solid #e5e7eb;
}

:deep(.p-datatable .p-datatable-tbody > tr > td) {
	padding: 0.75rem;
	color: #4b5563;
}

:deep(.p-datatable .p-datatable-tbody > tr:nth-child(even)) {
	background-color: #f9fafb;
}

:deep(.p-datatable .p-datatable-tbody > tr:hover) {
	background-color: #f3f4f6;
}

:deep(.p-paginator) {
	background-color: white;
	border-top: 1px solid #e5e7eb;
	padding: 0.75rem;
}

:deep(.p-paginator .p-paginator-pages .p-paginator-page.p-highlight) {
	background-color: #10b981;
	color: white;
}

:deep(.p-dropdown-panel) {
	background-color: white;
	box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
	border: 1px solid #e5e7eb;
	border-radius: 0.375rem;
}

:deep(.p-dropdown-panel .p-dropdown-items .p-dropdown-item) {
	color: #374151;
}

:deep(.p-dropdown-panel .p-dropdown-items .p-dropdown-item:hover) {
	background-color: #f3f4f6;
}

:deep(.p-dropdown-panel .p-dropdown-items .p-dropdown-item.p-highlight) {
	background-color: #10b981;
	color: white;
}

:deep(.p-progressspinner) {
	color: #10b981;
}

:deep(.p-toast) {
	opacity: 0.95;
}

:deep(.p-toast .p-toast-message) {
	border-radius: 0.5rem;
	box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
}

:deep(.p-toast .p-toast-message-success) {
	background-color: #ecfdf5;
	border-left: 4px solid #10b981;
}

:deep(.p-toast .p-toast-message-info) {
	background-color: #eff6ff;
	border-left: 4px solid #3b82f6;
}

:deep(.p-toast .p-toast-message-warn) {
	background-color: #fffbeb;
	border-left: 4px solid #f59e0b;
}

:deep(.p-toast .p-toast-message-error) {
	background-color: #fef2f2;
	border-left: 4px solid #ef4444;
}

.dark :deep(.p-component) {
	color: #e5e7eb;
}

.highlight {
	font-weight: bold;
	color: #10b981;
}

.dark-mode-transition {
	transition: color 0.2s, background-color 0.2s;
}

.dark :deep(.p-datatable .p-datatable-header) {
	background-color: #374151;
	border-bottom: 1px solid #4b5563;
}

.dark :deep(.p-datatable .p-datatable-thead > tr > th) {
	background-color: #374151;
	color: #e5e7eb;
	border-bottom: 1px solid #4b5563;
}

.dark :deep(.p-datatable .p-datatable-tbody > tr) {
	border-bottom: 1px solid #4b5563;
}

.dark :deep(.p-datatable .p-datatable-tbody > tr > td) {
	color: #d1d5db;
}

.dark :deep(.p-datatable .p-datatable-tbody > tr:nth-child(even)) {
	background-color: #1f2937;
}

.dark :deep(.p-datatable .p-datatable-tbody > tr:hover) {
	background-color: #374151;
}

.dark :deep(.p-paginator) {
	background-color: #1f2937;
	border-top: 1px solid #4b5563;
}

.dark :deep(.p-dropdown-panel) {
	background-color: #1f2937;
	border: 1px solid #4b5563;
}

.dark :deep(.p-dropdown-panel .p-dropdown-items .p-dropdown-item) {
	color: #d1d5db;
}

.dark :deep(.p-dropdown-panel .p-dropdown-items .p-dropdown-item:hover) {
	background-color: #374151;
}

.dark .highlight {
	color: #34d399;
}

.dark :deep(.p-toast .p-toast-message-success) {
	background-color: #064e3b;
	border-left: 4px solid #10b981;
}

.dark :deep(.p-toast .p-toast-message-info) {
	background-color: #1e3a8a;
	border-left: 4px solid #3b82f6;
}

.dark :deep(.p-toast .p-toast-message-warn) {
	background-color: #78350f;
	border-left: 4px solid #f59e0b;
}

.dark :deep(.p-toast .p-toast-message-error) {
	background-color: #7f1d1d;
	border-left: 4px solid #ef4444;
}

.dark :deep(.p-datatable .p-datatable-tbody tr td) {
	color: #e5e7eb !important;
}

.dark :deep(.p-datatable .p-datatable-thead tr th) {
	color: #e5e7eb !important;
}

.dark :deep(.p-datatable .p-datatable-tbody tr) {
	color: #e5e7eb !important;
}

.dark :deep(.p-datatable .p-datatable-tbody tr *) {
	color: #e5e7eb !important;
}

.dark :deep(.p-datatable .p-datatable-thead tr *) {
	color: #e5e7eb !important;
}

.dark :deep(.p-card *) {
	color: #e5e7eb !important;
}

.dark :deep(.p-card .p-card-title) {
	color: #e5e7eb !important;
}

.dark :deep(.p-card .p-card-content) {
	color: #e5e7eb !important;
}

.dark :deep(.p-card .p-card-content *) {
	color: #e5e7eb !important;
}
</style>
