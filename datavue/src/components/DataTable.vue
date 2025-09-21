<script setup>
import { ref, computed, onMounted, nextTick, inject } from 'vue';
import { useToast } from 'primevue/usetoast';

const toast = useToast();

const props = defineProps({
	data: {
		type: Array,
		required: true
	},
	features: {
		type: Array,
		required: true
	}
});

const selectedColumns = ref([]);
const loading = ref(false);
const rowsPerPage = ref(10);
const currentPage = ref(1);
const sortField = ref('');
const sortOrder = ref(1);

onMounted(() => {
	if (props.features.length > 0) {
		selectedColumns.value = [...props.features];
	}
});

const filteredData = computed(() => {
	let result = [...props.data];

	if (sortField.value) {
		result.sort((a, b) => {
			const aVal = a[sortField.value];
			const bVal = b[sortField.value];

			if (typeof aVal === 'number' && typeof bVal === 'number') {
				return sortOrder.value === 1 ? aVal - bVal : bVal - aVal;
			}

			const aStr = String(aVal).toLowerCase();
			const bStr = String(bVal).toLowerCase();

			if (aStr < bStr) return sortOrder.value === 1 ? -1 : 1;
			if (aStr > bStr) return sortOrder.value === 1 ? 1 : -1;
			return 0;
		});
	}

	return result;
});

const totalPages = computed(() => {
	return Math.ceil(filteredData.value.length / rowsPerPage.value);
});

const paginatedData = computed(() => {
	const start = (currentPage.value - 1) * rowsPerPage.value;
	const end = start + rowsPerPage.value;
	return filteredData.value.slice(start, end);
});

const getFeatureDescription = (name) => {
	const feature = props.features.find(f => f.name === name);
	return feature ? feature.description : name;
};

const getRussianName = (name) => {
	const russianNames = {
		'MedInc': 'Средний доход (тыс.$/год)',
		'HouseAge': 'Возраст дома (лет)',
		'AveRooms': 'Среднее количество комнат',
		'AveBedrms': 'Среднее количество спален',
		'Population': 'Население (чел.)',
		'AveOccup': 'Средняя заселенность (чел./дом)',
		'Latitude': 'Широта',
		'Longitude': 'Долгота',
		'PRICE': 'Цена дома (тыс.$)'
	};
	return russianNames[name] || name;
};

const formatNumber = (value, fieldName) => {
	if (typeof value === 'number') {

		if (fieldName === 'HouseAge') {
			return Math.round(value);
		}

		return value.toFixed(4);
	}
	return value;
};

const sortBy = (field) => {
	if (sortField.value === field) {
		sortOrder.value = sortOrder.value === 1 ? -1 : 1;
	} else {
		sortField.value = field;
		sortOrder.value = 1;
	}
	currentPage.value = 1;
};

const getSortIcon = (field) => {
	if (sortField.value !== field) {
		return '↕️'; // Нейтральная иконка
	}
	return sortOrder.value === 1 ? '↑' : '↓';
};

const goToPage = (page) => {
	if (page >= 1 && page <= totalPages.value) {
		currentPage.value = page;
		nextTick(() => {
			const tableElement = document.querySelector('.overflow-x-auto');
			if (tableElement) {
				tableElement.scrollIntoView({
					behavior: 'smooth',
					block: 'start'
				});
			}
		});
	}
};

const goToPreviousPage = () => {
	goToPage(Math.max(1, currentPage.value - 1));
};

const goToNextPage = () => {
	goToPage(Math.min(totalPages.value, currentPage.value + 1));
};

</script>

<template>
	<div class="bg-white dark:bg-gray-800 shadow-md rounded-lg overflow-hidden">
		<div class="flex justify-between items-center p-4 border-b border-gray-200 dark:border-gray-700">
			<h2 class="text-xl font-semibold text-gray-800 dark:text-white">Данные о недвижимости</h2>
		</div>
		<div class="p-4 bg-gray-50 dark:bg-gray-700">
			<div class="flex items-center gap-4">
				<label class="text-sm font-medium text-gray-700 dark:text-gray-300">
					Выберите колонки для отображения:
				</label>
				<select v-model="selectedColumns" multiple
					class="flex-1 max-w-md p-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-200">
					<option v-for="feature in features" :key="feature.name" :value="feature">
						{{ getRussianName(feature.name) }}
					</option>
				</select>
			</div>
		</div>

		<div class="overflow-x-auto">
			<table class="w-full">
				<thead class="bg-gray-100 dark:bg-gray-700">
					<tr>
						<th
							class="px-4 py-2 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider w-16">
							№
						</th>
						<th v-for="feature in selectedColumns" :key="feature.name"
							class="px-4 py-2 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider cursor-pointer hover:bg-gray-200 dark:hover:bg-gray-600 select-none"
							@click="sortBy(feature.name)" :title="getFeatureDescription(feature.name)">
							<div class="flex items-center justify-between">
								<span>{{ getRussianName(feature.name) }}</span>
								<span class="ml-2 text-sm">{{ getSortIcon(feature.name) }}</span>
							</div>
						</th>
					</tr>
				</thead>
				<tbody class="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
					<tr v-for="(row, index) in paginatedData" :key="index"
						class="hover:bg-gray-50 dark:hover:bg-gray-700">
						<td class="px-4 py-2 text-sm text-gray-500 dark:text-gray-400 font-mono">
							{{ (currentPage - 1) * rowsPerPage + index + 1 }}
						</td>
						<td v-for="feature in selectedColumns" :key="feature.name"
							class="px-4 py-2 text-sm text-gray-900 dark:text-gray-100"
							:class="{ 'font-bold text-green-600 dark:text-green-400': feature.name === 'PRICE' }">
							{{ formatNumber(row[feature.name], feature.name) }}
						</td>
					</tr>
				</tbody>
			</table>
		</div>

		<div
			class="p-4 bg-gray-50 dark:bg-gray-700 border-t border-gray-200 dark:border-gray-700 flex flex-wrap justify-between items-center text-sm text-gray-600 dark:text-gray-300">
			<div class="flex flex-col sm:flex-row gap-2 sm:gap-4">
				<span>Всего записей: {{ filteredData.length }}</span>
				<span v-if="sortField" class="text-blue-600 dark:text-blue-400">
					Сортировка: {{ getRussianName(sortField) }} {{ sortOrder === 1 ? '↑' : '↓' }}
				</span>
			</div>
			<div class="mt-2 sm:mt-0 flex items-center gap-2">
				<span>Строк на странице:</span>
				<select v-model="rowsPerPage"
					class="w-20 p-1 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-200">
					<option value="5">5</option>
					<option value="10">10</option>
					<option value="20">20</option>
					<option value="50">50</option>
				</select>
				<div class="flex gap-1 items-center">
					<button @click="goToPreviousPage" :disabled="currentPage === 1"
						class="px-2 py-1 border border-gray-300 dark:border-gray-600 rounded disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-100 dark:hover:bg-gray-600"
						title="Предыдущая страница">
						←
					</button>
					<span class="px-2 py-1">{{ currentPage }} из {{ totalPages }}</span>
					<button @click="goToNextPage" :disabled="currentPage === totalPages"
						class="px-2 py-1 border border-gray-300 dark:border-gray-600 rounded disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-100 dark:hover:bg-gray-600"
						title="Следующая страница">
						→
					</button>
				</div>
			</div>
		</div>
	</div>
</template>

<style scoped></style>
