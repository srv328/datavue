<script setup>
import { ref, computed } from 'vue';

const props = defineProps({
	stats: {
		type: Object,
		required: true
	},
	features: {
		type: Array,
		required: true
	}
});

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

const getFeatureDescription = (name) => {
	const feature = props.features.find(f => f.name === name);
	return feature ? feature.description : name;
};

const formatNumber = (value) => {
	if (typeof value === 'number') {
		return value.toFixed(4);
	}
	return value;
};

const selectedFeature1 = ref('');
const selectedFeature2 = ref('');
const customCorrelation = ref(null);

const correlations = computed(() => {
	if (!props.stats || !props.stats.corr) return [];

	const result = Object.entries(props.stats.corr)
		.filter(([key]) => key !== 'PRICE')
		.map(([key, value]) => ({
			feature: key,
			description: getFeatureDescription(key),
			correlation: value,
			strength: Math.abs(value)
		}))
		.sort((a, b) => b.strength - a.strength);

	return result;
});

const getCorrelationClass = (value) => {
	const absValue = Math.abs(value);
	if (absValue >= 0.7) return 'very-strong';
	if (absValue >= 0.5) return 'strong';
	if (absValue >= 0.3) return 'moderate';
	if (absValue >= 0.1) return 'weak';
	return 'very-weak';
};

const getCorrelationDescription = (value) => {
	const absValue = Math.abs(value);
	if (absValue >= 0.7) return 'Очень сильная';
	if (absValue >= 0.5) return 'Сильная';
	if (absValue >= 0.3) return 'Умеренная';
	if (absValue >= 0.1) return 'Слабая';
	return 'Очень слабая';
};

const calculateCorrelation = () => {
	if (!selectedFeature1.value || !selectedFeature2.value) {
		customCorrelation.value = null;
		return;
	}

	if (selectedFeature1.value === selectedFeature2.value) {
		customCorrelation.value = 1.0;
		return;
	}

	if (props.stats && props.stats.corr_matrix) {
		const feature1 = selectedFeature1.value;
		const feature2 = selectedFeature2.value;

		if (props.stats.corr_matrix[feature1] && props.stats.corr_matrix[feature1][feature2] !== undefined) {
			customCorrelation.value = props.stats.corr_matrix[feature1][feature2];
			console.log('Found correlation (1->2):', customCorrelation.value);
		} else if (props.stats.corr_matrix[feature2] && props.stats.corr_matrix[feature2][feature1] !== undefined) {
			customCorrelation.value = props.stats.corr_matrix[feature2][feature1];
			console.log('Found correlation (2->1):', customCorrelation.value);
		} else {
			console.log('No correlation found, setting to 0');
			customCorrelation.value = 0;
		}
	} else {
		console.log('No corr_matrix in stats, setting to 0');
		customCorrelation.value = 0;
	}
};
</script>

<template>
	<div class="stats-container">
		<div class="stats-section">
			<h2>Основная статистика</h2>
			<div class="stats-cards">
				<Card class="stats-card">
					<template #title>Количество записей</template>
					<template #content>
						<div class="stat-value">{{ stats.count }}</div>
					</template>
				</Card>
			</div>
		</div>

		<div class="stats-section">
			<h2>Описательная статистика</h2>
			<DataTable :value="features" stripedRows>
				<Column field="name" header="Признак">
					<template #body="{ data }">
						<div class="feature-name" :title="data.description">
							{{ getRussianName(data.name) }}
							<i class="pi pi-info-circle info-icon"></i>
						</div>
					</template>
				</Column>
				<Column header="Среднее">
					<template #body="{ data }">
						{{ formatNumber(stats.mean[data.name]) }}
					</template>
				</Column>
				<Column header="Медиана">
					<template #body="{ data }">
						{{ formatNumber(stats.median[data.name]) }}
					</template>
				</Column>
				<Column header="Минимум">
					<template #body="{ data }">
						{{ formatNumber(stats.min[data.name]) }}
					</template>
				</Column>
				<Column header="Максимум">
					<template #body="{ data }">
						{{ formatNumber(stats.max[data.name]) }}
					</template>
				</Column>
			</DataTable>
		</div>

		<div class="stats-section">
			<h2>Корреляция с ценой (PRICE)</h2>
			<DataTable :value="correlations" stripedRows>
				<Column field="feature" header="Признак">
					<template #body="{ data }">
						<div class="feature-name" :title="data.description">
							{{ getRussianName(data.feature) }}
							<i class="pi pi-info-circle info-icon"></i>
						</div>
					</template>
				</Column>
				<Column field="correlation" header="Корреляция" sortable>
					<template #body="{ data }">
						<div class="correlation-value" :class="getCorrelationClass(data.correlation)">
							{{ formatNumber(data.correlation) }}
						</div>
					</template>
				</Column>
				<Column header="Сила связи">
					<template #body="{ data }">
						<div class="correlation-strength" :class="getCorrelationClass(data.correlation)">
							{{ getCorrelationDescription(data.correlation) }}
							<div class="correlation-bar" :style="{ width: Math.abs(data.correlation) * 100 + '%' }">
							</div>
						</div>
					</template>
				</Column>
			</DataTable>
		</div>

		<div class="stats-section">
			<h2>Калькулятор корреляции</h2>
			<div class="correlation-calculator">
				<div class="calculator-controls">
					<div class="control-group">
						<label for="feature1">Первый признак:</label>
						<select id="feature1" v-model="selectedFeature1" @change="calculateCorrelation"
							class="feature-select">
							<option value="">Выберите признак</option>
							<option v-for="feature in features" :key="feature.name" :value="feature.name">
								{{ getRussianName(feature.name) }}
							</option>
						</select>
					</div>

					<div class="control-group">
						<label for="feature2">Второй признак:</label>
						<select id="feature2" v-model="selectedFeature2" @change="calculateCorrelation"
							class="feature-select">
							<option value="">Выберите признак</option>
							<option v-for="feature in features" :key="feature.name" :value="feature.name">
								{{ getRussianName(feature.name) }}
							</option>
						</select>
					</div>
				</div>

				<div v-if="customCorrelation !== null" class="correlation-result">
					<div class="result-card">
						<h3>Результат корреляции</h3>
						<div class="correlation-display">
							<div class="correlation-value-large" :class="getCorrelationClass(customCorrelation)">
								{{ formatNumber(customCorrelation) }}
							</div>
							<div class="correlation-strength-large" :class="getCorrelationClass(customCorrelation)">
								{{ getCorrelationDescription(customCorrelation) }}
							</div>
							<div class="correlation-bar-large"
								:style="{ width: Math.abs(customCorrelation) * 100 + '%' }">
							</div>
						</div>
						<div class="correlation-interpretation">
							<p v-if="Math.abs(customCorrelation) >= 0.7">
								<strong>Очень сильная связь</strong> - признаки тесно связаны между собой
							</p>
							<p v-else-if="Math.abs(customCorrelation) >= 0.5">
								<strong>Сильная связь</strong> - признаки имеют заметную взаимосвязь
							</p>
							<p v-else-if="Math.abs(customCorrelation) >= 0.3">
								<strong>Умеренная связь</strong> - признаки частично связаны
							</p>
							<p v-else-if="Math.abs(customCorrelation) >= 0.1">
								<strong>Слабая связь</strong> - признаки слабо связаны
							</p>
							<p v-else>
								<strong>Очень слабая связь</strong> - признаки практически не связаны
							</p>
						</div>
					</div>
				</div>
			</div>
		</div>
	</div>
</template>

<style scoped>
.stats-container {
	display: flex;
	flex-direction: column;
	gap: 2rem;
}

.stats-section {
	margin-bottom: 1.5rem;
}

h2 {
	margin-bottom: 1rem;
	color: #10b981;
	font-size: 1.5rem;
}

.dark h2 {
	color: #34d399;
}

.stats-cards {
	display: flex;
	flex-wrap: wrap;
	gap: 1rem;
	margin-bottom: 1rem;
}

.stats-card {
	flex: 1;
	min-width: 200px;
	max-width: 300px;
}

.stat-value {
	font-size: 2rem;
	font-weight: bold;
	color: var(--primary-color);
	text-align: center;
}

.feature-name {
	display: flex;
	align-items: center;
	gap: 0.5rem;
	cursor: help;
}

.info-icon {
	font-size: 0.8rem;
	color: var(--secondary-color);
}

.correlation-value {
	font-weight: bold;
}

.correlation-strength {
	position: relative;
}

.correlation-bar {
	height: 8px;
	background-color: var(--primary-color);
	border-radius: 4px;
	margin-top: 4px;
}

.very-strong {
	color: #d32f2f;
}

.strong {
	color: #f57c00;
}

.moderate {
	color: #ffa000;
}

.weak {
	color: #7cb342;
}

.very-weak {
	color: #9e9e9e;
}

.very-strong .correlation-bar {
	background-color: #d32f2f;
}

.strong .correlation-bar {
	background-color: #f57c00;
}

.moderate .correlation-bar {
	background-color: #ffa000;
}

.weak .correlation-bar {
	background-color: #7cb342;
}

.very-weak .correlation-bar {
	background-color: #9e9e9e;
}

.correlation-calculator {
	background: #f8f9fa;
	border-radius: 8px;
	padding: 1.5rem;
	margin-top: 1rem;
}

.dark .correlation-calculator {
	background: #374151;
}

.calculator-controls {
	display: flex;
	gap: 2rem;
	margin-bottom: 1.5rem;
	flex-wrap: wrap;
}

.control-group {
	flex: 1;
	min-width: 200px;
}

.control-group label {
	display: block;
	margin-bottom: 0.5rem;
	font-weight: 500;
	color: #333;
}

.dark .control-group label {
	color: #e5e7eb;
}

.feature-select {
	width: 100%;
	padding: 0.5rem;
	border: 1px solid #ddd;
	border-radius: 4px;
	background: white;
	font-size: 0.9rem;
}

.dark .feature-select {
	background: #4b5563;
	border-color: #6b7280;
	color: #e5e7eb;
}

.correlation-result {
	margin-top: 1rem;
}

.result-card {
	background: white;
	border-radius: 8px;
	padding: 1.5rem;
	box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.result-card h3 {
	margin: 0 0 1rem 0;
	color: #333;
	font-size: 1.2rem;
}

.dark .result-card h3 {
	color: #e5e7eb;
}

.correlation-display {
	text-align: center;
	margin-bottom: 1rem;
}

.correlation-value-large {
	font-size: 2.5rem;
	font-weight: bold;
	margin-bottom: 0.5rem;
}

.correlation-strength-large {
	font-size: 1.1rem;
	margin-bottom: 1rem;
}

.correlation-bar-large {
	height: 12px;
	border-radius: 6px;
	margin: 0 auto;
	max-width: 300px;
}

.correlation-interpretation {
	background: #f8f9fa;
	padding: 1rem;
	border-radius: 4px;
	border-left: 4px solid #10b981;
}

.dark .correlation-interpretation {
	background: #374151;
	border-left-color: #34d399;
}

.correlation-interpretation p {
	margin: 0;
	color: #555;
	line-height: 1.5;
}

.dark .correlation-interpretation p {
	color: #d1d5db;
}

.dark :deep(.p-datatable) {
	background: transparent !important;
}

.dark :deep(.p-datatable .p-datatable-header) {
	background: #374151 !important;
	color: #e5e7eb !important;
	border-color: #6b7280 !important;
}

.dark :deep(.p-datatable .p-datatable-tbody > tr) {
	background: #1f2937 !important;
	color: #e5e7eb !important;
}

.dark :deep(.p-datatable .p-datatable-tbody > tr:nth-child(even)) {
	background: #374151 !important;
}

.dark :deep(.p-datatable .p-datatable-tbody > tr:hover) {
	background: #4b5563 !important;
}

.dark :deep(.p-datatable .p-datatable-thead > tr > th) {
	background: #374151 !important;
	color: #e5e7eb !important;
	border-color: #6b7280 !important;
}

.dark :deep(.p-datatable .p-datatable-tbody > tr > td) {
	border-color: #6b7280 !important;
	color: #e5e7eb !important;
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

.dark :deep(.p-card .p-card-content *) {
	color: #e5e7eb !important;
}

.dark :deep(.p-card *) {
	color: #e5e7eb !important;
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
</style>
