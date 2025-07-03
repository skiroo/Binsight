<template>
  <div class="form-container">
    <form @submit.prevent="handleRegister">
      <input v-model="username" placeholder="Nom d'utilisateur" required />
      <input type="email" v-model="email" placeholder="Email" required />
      <input type="password" v-model="password" placeholder="Mot de passe" required />
      <button type="submit">S'inscrire</button>
    </form>
    <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>
  </div>
</template>

<script>
export default {
  data() {
    return {
      username: "",
      email: "",
      password: "",
      errorMessage: "",
    };
  },
  methods: {
    handleRegister() {
      // logique d'inscription
    },
  },
};
</script>

<style>
/* LoginForm & RegisterForm */
.form-container {
  display: flex;
  justify-content: center;
  align-items: center;
  flex-direction: column;
  height: 100%;
}

form {
  display: flex;
  flex-direction: column;
  gap: 15px;
  width: 100%;
}

form input {
  padding: 10px;
  border: 1px solid #555;
  border-radius: 5px;
  background-color: #1e1e1e;
  color: white;
}

form input:focus {
  outline: none;
  border-color: #10b981;
}

form button {
  padding: 10px;
  background-color: #10b981;
  color: #1e1e1e;
  font-weight: bold;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}

form button:hover {
  background-color: #10b981;
}

.error-message {
  color: #ff6b6b;
  margin-top: 10px;
  font-size: 0.9rem;
}
</style>