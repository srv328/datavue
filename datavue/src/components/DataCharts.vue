<script setup>
import { ref, computed, onMounted } from 'vue';

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

const selectedFeatureX = ref('');
const selectedFeatureY = ref('PRICE');
const chartType = ref('scatter');

const chartTypes = [
	{ name: 'Точечная диаграмма', value: 'scatter' },
	{ name: 'Гистограмма', value: 'histogram' },
	{ name: 'Линейный график', value: 'line' },
	{ name: 'Столбчатая диаграмма', value: 'bar' }
];

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

onMounted(() => {
	if (props.features.length > 0) {
		const nonPriceFeature = props.features.find(f => f.name !== 'PRICE');
		if (nonPriceFeature) {
			selectedFeatureX.value = nonPriceFeature.name;
		}
	}
});

const chartData = computed(() => {
	if (!selectedFeatureX.value || !selectedFeatureY.value || props.data.length === 0) {
		return null;
	}

	switch (chartType.value) {
		case 'scatter':
			return getScatterData();
		case 'histogram':
			return getHistogramData();
		case 'line':
			return getLineData();
		case 'bar':
			return getBarData();
		default:
			return null;
	}
});

const getScatterData = () => {
	const datasets = [{
		label: `${getRussianName(selectedFeatureX.value)} vs ${getRussianName(selectedFeatureY.value)}`,
		data: props.data.map(item => ({
			x: item[selectedFeatureX.value],
			y: item[selectedFeatureY.value]
		})),
		backgroundColor: 'rgba(75, 192, 192, 0.2)',
		borderColor: 'rgba(75, 192, 192, 1)',
		borderWidth: 1,
		pointRadius: 3
	}];

	return {
		datasets
	};
};

const getHistogramData = () => {
	const values = props.data.map(item => item[selectedFeatureX.value]);
	const min = Math.min(...values);
	const max = Math.max(...values);
	const binCount = 20;
	const binSize = (max - min) / binCount;

	const bins = Array(binCount).fill(0);
	values.forEach(value => {
		const binIndex = Math.min(Math.floor((value - min) / binSize), binCount - 1);
		bins[binIndex]++;
	});

	const labels = bins.map((_, i) => {
		const binStart = min + i * binSize;
		return binStart.toFixed(2);
	});

	return {
		labels,
		datasets: [{
			label: `Распределение ${getRussianName(selectedFeatureX.value)}`,
			data: bins,
			backgroundColor: 'rgba(54, 162, 235, 0.5)',
			borderColor: 'rgba(54, 162, 235, 1)',
			borderWidth: 1
		}]
	};
};

const getLineData = () => {
	const sortedData = [...props.data].sort((a, b) =>
		a[selectedFeatureX.value] - b[selectedFeatureX.value]
	);

	const sampledData = [];
	for (let i = 0; i < sortedData.length; i += 10) {
		sampledData.push(sortedData[i]);
	}

	const labels = sampledData.map(item => item[selectedFeatureX.value].toFixed(2));
	const data = sampledData.map(item => item[selectedFeatureY.value]);

	return {
		labels,
		datasets: [{
			label: `${getRussianName(selectedFeatureY.value)} по ${getRussianName(selectedFeatureX.value)}`,
			data,
			fill: false,
			borderColor: 'rgba(75, 192, 192, 1)',
			tension: 0.1
		}]
	};
};

const getBarData = () => {
	const sortedData = [...props.data].sort((a, b) =>
		a[selectedFeatureX.value] - b[selectedFeatureX.value]
	);

	const min = Math.min(...sortedData.map(item => item[selectedFeatureX.value]));
	const max = Math.max(...sortedData.map(item => item[selectedFeatureX.value]));
	const groupCount = 15;
	const groupSize = (max - min) / groupCount;

	const groups = Array(groupCount).fill().map(() => []);

	sortedData.forEach(item => {
		const groupIndex = Math.min(Math.floor((item[selectedFeatureX.value] - min) / groupSize), groupCount - 1);
		groups[groupIndex].push(item);
	});

	const labels = groups.map((_, i) => {
		const groupStart = min + i * groupSize;
		return groupStart.toFixed(2);
	});

	const data = groups.map(group => {
		if (group.length === 0) return 0;
		return group.reduce((sum, item) => sum + item[selectedFeatureY.value], 0) / group.length;
	});

	return {
		labels,
		datasets: [{
			label: `Среднее ${getRussianName(selectedFeatureY.value)} по ${getRussianName(selectedFeatureX.value)}`,
			data,
			backgroundColor: 'rgba(153, 102, 255, 0.5)',
			borderColor: 'rgba(153, 102, 255, 1)',
			borderWidth: 1
		}]
	};
};

const chartOptions = computed(() => {
	const baseOptions = {
		responsive: true,
		maintainAspectRatio: false,
		plugins: {
			legend: {
				position: 'top',
			},
			tooltip: {
				callbacks: {
					label: function (context) {
						return `${context.dataset.label}: (${context.parsed.x}, ${context.parsed.y})`;
					}
				}
			}
		}
	};

	switch (chartType.value) {
		case 'scatter':
			return {
				...baseOptions,
				scales: {
					x: {
						title: {
							display: true,
							text: getRussianName(selectedFeatureX.value)
						}
					},
					y: {
						title: {
							display: true,
							text: getRussianName(selectedFeatureY.value)
						}
					}
				}
			};
		case 'histogram':
			return {
				...baseOptions,
				scales: {
					x: {
						title: {
							display: true,
							text: getRussianName(selectedFeatureX.value)
						}
					},
					y: {
						title: {
							display: true,
							text: 'Количество'
						}
					}
				}
			};
		case 'line':
		case 'bar':
			return {
				...baseOptions,
				scales: {
					x: {
						title: {
							display: true,
							text: getRussianName(selectedFeatureX.value)
						}
					},
					y: {
						title: {
							display: true,
							text: getRussianName(selectedFeatureY.value)
						}
					}
				}
			};
		default:
			return baseOptions;
	}
});

const getFeatureDescription = (name) => {
	const feature = props.features.find(f => f.name === name);
	return feature ? feature.description : name;
};
</script>

<template>
	<div class="charts-container">
		<div class="chart-controls">
			<div class="control-group">
				<label>Тип графика:</label>
				<Dropdown v-model="chartType" :options="chartTypes" optionLabel="name" optionValue="value"
					placeholder="Выберите тип графика" class="control-dropdown" />
			</div>

			<div class="control-group">
				<label>Ось X:</label>
				<Dropdown v-model="selectedFeatureX" :options="features"
					:optionLabel="(option) => getRussianName(option.name)" optionValue="name"
					placeholder="Выберите признак для оси X" class="control-dropdown" />
			</div>

			<div class="control-group" v-if="chartType === 'scatter' || chartType === 'line' || chartType === 'bar'">
				<label>Ось Y:</label>
				<Dropdown v-model="selectedFeatureY" :options="features"
					:optionLabel="(option) => getRussianName(option.name)" optionValue="name"
					placeholder="Выберите признак для оси Y" class="control-dropdown" />
			</div>
		</div>

		<div class="chart-container">
			<div v-if="chartData" class="chart">
				<Chart v-if="chartType === 'scatter'" type="scatter" :data="chartData" :options="chartOptions" />
				<Chart v-else-if="chartType === 'histogram' || chartType === 'bar'" type="bar" :data="chartData"
					:options="chartOptions" />
				<Chart v-else-if="chartType === 'line'" type="line" :data="chartData" :options="chartOptions" />
			</div>
			<div v-else class="no-chart">
				<p>Выберите признаки для построения графика</p>
			</div>
		</div>

		<div class="chart-description">
			<Card>
				<template #title>
					Описание признаков
				</template>
				<template #content>
					<div v-if="selectedFeatureX">
						<strong>{{ getRussianName(selectedFeatureX) }}:</strong> {{
							getFeatureDescription(selectedFeatureX) }}
					</div>
					<div
						v-if="selectedFeatureY && (chartType === 'scatter' || chartType === 'line' || chartType === 'bar')">
						<strong>{{ getRussianName(selectedFeatureY) }}:</strong> {{
							getFeatureDescription(selectedFeatureY) }}
					</div>
				</template>
			</Card>
		</div>
	</div>
</template>

<style scoped>
.charts-container {
	display: flex;
	flex-direction: column;
	gap: 1.5rem;
}

.chart-controls {
	display: flex;
	flex-wrap: wrap;
	gap: 1rem;
	margin-bottom: 2.5rem;
	padding: 1rem;
	background-color: #f8f9fa;
	border-radius: 8px;
	position: relative;
	z-index: 10;
}

.dark .chart-controls {
	background-color: #374151;
}

.control-group {
	display: flex;
	flex-direction: column;
	gap: 0.5rem;
	flex: 1;
	min-width: 200px;
}

.control-group label {
	color: #374151;
	font-weight: 500;
}

.dark .control-group label {
	color: #e5e7eb;
}

.control-dropdown {
	width: 100%;
	z-index: 1000;
}

.chart-container {
	height: 600px;
	background-color: #fff;
	border-radius: 8px;
	padding: 1rem;
	box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
	position: relative;
	z-index: 1;
}

.dark .chart-container {
	background-color: #1f2937;
}

.chart {
	height: 100%;
}

.no-chart {
	display: flex;
	justify-content: center;
	align-items: center;
	height: 100%;
	color: #666;
	font-style: italic;
}

.chart-description {
	margin-top: 1rem;
}

:deep(.p-dropdown-panel) {
	z-index: 9999 !important;
}

:deep(.p-dropdown) {
	z-index: 1000;
}

:deep(.p-dropdown-panel .p-dropdown-items) {
	max-height: 200px;
	overflow-y: auto;
}

.charts-container {
	position: relative;
}

.dark :deep(.p-dropdown) {
	background: #4b5563 !important;
	border-color: #6b7280 !important;
	color: #e5e7eb !important;
}

.dark :deep(.p-dropdown:not(.p-disabled):hover) {
	border-color: #9ca3af !important;
}

.dark :deep(.p-dropdown:not(.p-disabled).p-focus) {
	border-color: #34d399 !important;
	box-shadow: 0 0 0 0.2rem rgba(52, 211, 153, 0.2) !important;
}

.dark :deep(.p-dropdown-panel) {
	background: #374151 !important;
	border-color: #6b7280 !important;
}

.dark :deep(.p-dropdown-panel .p-dropdown-items .p-dropdown-item) {
	color: #e5e7eb !important;
}

.dark :deep(.p-dropdown-panel .p-dropdown-items .p-dropdown-item:hover) {
	background: #4b5563 !important;
	color: #e5e7eb !important;
}

.dark :deep(.p-dropdown-panel .p-dropdown-items .p-dropdown-item.p-highlight) {
	background: #34d399 !important;
	color: #1f2937 !important;
}

.dark :deep(.p-dropdown-panel .p-dropdown-items .p-dropdown-item.p-highlight:hover) {
	background: #10b981 !important;
	color: #1f2937 !important;
}

.dark :deep(.p-dropdown-label) {
	color: #e5e7eb !important;
}

.dark :deep(.p-dropdown-trigger) {
	color: #e5e7eb !important;
}

.dark :deep(.p-card) {
	background: #1f2937 !important;
	color: #e5e7eb !important;
	border-color: #6b7280 !important;
}

.dark :deep(.p-card .p-card-title) {
	color: #e5e7eb !important;
}

.dark :deep(.p-card .p-card-content) {
	color: #e5e7eb !important;
}

.dark :deep(.p-card .p-card-content div) {
	color: #e5e7eb !important;
}

.dark :deep(.p-card .p-card-content strong) {
	color: #e5e7eb !important;
}

@media (max-width: 768px) {
	.chart-container {
		height: 400px;
	}

	.chart-controls {
		flex-direction: column;
	}

	.control-group {
		min-width: 100%;
	}
}
</style>
