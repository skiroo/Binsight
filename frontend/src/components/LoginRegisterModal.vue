<template>
  <div class="modal-overlay">
    <div class="modal-content" :class="isDark ? 'dark' : 'light'">
      <button class="close-button" @click="$emit('close')">✕</button>

      <component :is="currentForm" @switch-mode="toggleMode" />

      <div class="switch-mode">
        <span>
          {{ currentForm === 'LoginForm' ? "Pas encore inscrit ?" : "Déjà un compte ?" }}
        </span>
        <button @click="toggleMode">
          {{ currentForm === 'LoginForm' ? "S’enregistrer" : "Se connecter" }}
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import LoginForm from "./LoginForm.vue";
import RegisterForm from "./RegisterForm.vue";

export default {
  props: {
    isDark: Boolean,
  },
  components: {
    LoginForm,
    RegisterForm,
  },
  data() {
    return {
      currentForm: "LoginForm",
    };
  },
  methods: {
    toggleMode() {
      this.currentForm =
        this.currentForm === "LoginForm" ? "RegisterForm" : "LoginForm";
    },
  },
};
</script>

<style>
/* Overlay */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background-color: rgba(0, 0, 0, 0.6);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

/* Container */
.modal-content {
  padding: 30px;
  border-radius: 20px;
  width: 90%;
  max-width: 500px;
  box-shadow: 0 15px 40px rgba(0, 0, 0, 0.4);
  position: relative;
  text-align: center;
  display: flex;
  flex-direction: column;
  gap: 25px;
  transition: background-color 0.3s ease, color 0.3s ease;
}

/* Light & dark variables */
.modal-content.light {
  background-color: #ffffff;
  color: #1a1a1a;
  --input-bg: #f4f4f4;
  --input-text: #1a1a1a;
}

.modal-content.dark {
  background-color: #1e1e1e;
  color: #f1f1f1;
  --input-bg: #2c2c2c;
  --input-text: #ffffff;
}

/* Close button */
.close-button {
  position: absolute;
  top: 12px;
  right: 16px;
  background: none;
  border: none;
  font-size: 22px;
  color: inherit;
  cursor: pointer;
}

/* Form style inside child components */
form {
  display: flex;
  flex-direction: column;
  gap: 15px;
  width: 100%;
}

form input {
  padding: 12px 16px;
  border-radius: 10px;
  border: 1px solid #ccc;
  background-color: var(--input-bg);
  color: var(--input-text);
  font-size: 1rem;
  box-sizing: border-box;
  width: 100%;
  transition: border-color 0.3s, box-shadow 0.3s;
}

form input::placeholder {
  color: #aaa;
}

form input:focus {
  outline: none;
  border-color: #10b981;
  box-shadow: 0 0 0 2px rgba(129, 199, 132, 0.3);
}


form button {
  padding: 12px;
  background-color: #10b981;
  color: #1e1e1e;
  font-weight: bold;
  border: none;
  border-radius: 10px;
  cursor: pointer;
  font-size: 1rem;
  transition: background-color 0.3s ease;
}

form button:hover {
  background-color: #10b981;
}

/* Switch mode */
.switch-mode {
  font-size: 0.95rem;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 6px;
}

.switch-mode button {
  background: none;
  border: none;
  color: #10b981;
  font-weight: bold;
  font-size: 1rem;
  cursor: pointer;
}
</style>