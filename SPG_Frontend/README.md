Task Management Portal (Frontend)

Welcome to the Vue 3 Frontend for the Task Management Portal!

This application provides a dual-interface system: a **Manager Dashboard** for assigning and tracking tasks (with built-in analytics), and a **Staff Dashboard** for employees to view, update, and read translated task descriptions.

Currently, the application is configured to run in **Demo Mode**, meaning it will work perfectly on your local machine without needing an active backend database or API.

1. Prerequisites:

Before you can run this project, you need to have **Node.js** installed on your computer. Node.js comes with `npm` (Node Package Manager), which is required to download the Vue dependencies.

1. Download and install Node.js from [nodejs.org](https://nodejs.org/) (The "LTS" version is recommended).
2. To verify it installed correctly, open your terminal (or command prompt) and type:
`node -v` and `npm -v`. Both should print out version numbers.

2. Setup & Installation

1. **Open your terminal** and navigate to the root folder of this project.
2. **Install the project dependencies** by running the following command:
npm install
3. **Start the development server** by running:
npm run dev
4. **Open the application:** Once the server starts, your terminal will display a local web address (usually `http://localhost:5173/`). Click that link or copy/paste it into your web browser.


3. How to Log In (Demo Mode)

The application currently has simulated authentication so you can test both the Manager and Staff views without a database.

On the login screen, use the following credentials:

**To access the Manager Dashboard:**

* **Email:** `admin@gmail.com`
* **Password:** `password`

**To access the Staff Dashboard:**

* **Email:** *(You can enter any simulated email here, e.g., `staff@gmail.com`)*
* **Password:** `password`

4. Project Structure Guide

If you need to edit the code, here is a quick guide to where the main files are located based on the project structure:

* **`src/router/index.js`**: Controls the page navigation (routing).
* **`src/views/auth/LoginView.vue`**: The initial login screen.
* **`src/views/manager/ManagerDashboard.vue`**: The administrative command center with charts, user management, and task creation.
* **`src/views/staff/StaffTasks.vue`**: The employee view for updating task statuses and viewing multi-language descriptions.
 
5. Connecting the Python Backend Later

Every main `.vue` file (`LoginView.vue`, `ManagerDashboard.vue`, `StaffTasks.vue`) has a toggle at the very top of its `<script setup>` block:
const USE_REAL_BACKEND = false;

When your Flask backend and SQL database are fully built and running on port 5000, simply change this variable to `true` in those files. The Vue frontend will instantly switch from using the local dummy data to making live API calls to your Python server!