<template>
  <div class="login-form">
    <h2>Connexion</h2>

    <form @submit.prevent="handleLogin">
      <input v-model="email" type="email" placeholder="Email" required />
      <input v-model="mot_de_passe" type="password" placeholder="Mot de passe" required />

      <button type="submit" :disabled="loading">
        {{ loading ? 'Connexion...' : 'Se connecter' }}
      </button>

      <p v-if="error" class="error-message">{{ error }}</p>
    </form>
  </div>
</template>

<script>
import { login } from '../services/api';

export default {
  props: {
    message: {
      type: String,
      default: ''
    }
  },
  data() {
    return {
      email: '',
      mot_de_passe: '',
      loading: false,
      error: ''
    };
  },
  methods: {
    async handleLogin() {
      this.error = '';
      this.loading = true;

      try {
        const res = await login(this.email, this.mot_de_passe);

        // Enregistrer l'utilisateur dans localStorage
        localStorage.setItem('user', JSON.stringify(res.data));

        // Émettre l'événement au parent
        this.$emit('login-success', res.data);
      } catch (err) {
        this.error = err.response?.data?.error || 'Erreur de connexion.';
      } finally {
        this.loading = false;
      }
    }
  }
};
</script>

<style scoped>
.success-message {
  color: #10b981;
  font-weight: bold;
  margin-bottom: 10px;
}
.error-message {
  color: #ff6b6b;
  margin-top: 10px;
  font-size: 0.9rem;
}
</style>