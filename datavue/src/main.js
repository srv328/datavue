import { createApp } from "vue";
import App from "./App.vue";
import PrimeVue from "primevue/config";
import "primeicons/primeicons.css";
import DataTable from "primevue/datatable";
import Column from "primevue/column";
import Button from "primevue/button";
import Card from "primevue/card";
import Chart from "primevue/chart";
import InputText from "primevue/inputtext";
import Dropdown from "primevue/dropdown";
import MultiSelect from "primevue/multiselect";
import Menubar from "primevue/menubar";
import TabMenu from "primevue/tabmenu";
import ProgressSpinner from "primevue/progressspinner";
import Toast from "primevue/toast";
import ToastService from "primevue/toastservice";
import Tooltip from "primevue/tooltip";
import Skeleton from "primevue/skeleton";
import Divider from "primevue/divider";

const app = createApp(App);

app.use(PrimeVue, {
  ripple: true,
  inputStyle: "filled",
});
app.use(ToastService);

app.component("DataTable", DataTable);
app.component("Column", Column);
app.component("Button", Button);
app.component("Card", Card);
app.component("Chart", Chart);
app.component("InputText", InputText);
app.component("Dropdown", Dropdown);
app.component("MultiSelect", MultiSelect);
app.component("Menubar", Menubar);
app.component("TabMenu", TabMenu);
app.component("ProgressSpinner", ProgressSpinner);
app.component("Toast", Toast);
app.component("Skeleton", Skeleton);
app.component("Divider", Divider);

app.directive("tooltip", Tooltip);

app.mount("#app");
