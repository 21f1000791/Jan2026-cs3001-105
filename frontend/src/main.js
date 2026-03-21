import { createApp } from "vue";
import { createPinia } from "pinia";
import App from "./App.vue";
import router from "./router";
import "./assets/app.css";

window.addEventListener("cop:auth-expired", () => {
	if (router.currentRoute.value.path !== "/login") {
		router.push("/login");
	}
});

const app = createApp(App);
app.use(createPinia());
app.use(router);
app.mount("#app");
