// LoginForm.vue
<template>
  <div class="login-form">
    <h2>{{ t('Connexion', 'Login') }}</h2>

    <form @submit.prevent="handleLogin">
      <input
        v-model="email"
        type="email"
        :placeholder="t('Email', 'Email')"
        required
      />
      <input
        v-model="mot_de_passe"
        type="password"
        :placeholder="t('Mot de passe', 'Password')"
        required
      />

      <button type="submit" :disabled="loading">
        {{ loading ? t('Connexion...', 'Logging in...') : t('Se connecter', 'Login') }}
      </button>

      <p v-if="error" class="error-message">{{ error }}</p>
    </form>
  </div>
</template>

<script>
import { login } from '../services/api';

export default {
  props: {
    lang: {
      type: String,
      default: 'fr'
    },
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
    t(fr, en) {
      return this.lang === 'fr' ? fr : en;
    },
    async handleLogin() {
      this.error = '';
      this.loading = true;

      try {
        const res = await login(this.email, this.mot_de_passe);
        localStorage.setItem('user', JSON.stringify(res.data));
        localStorage.setItem('role', res.data.role);
        this.$emit('login-success', res.data);
      } catch (err) {
        const msg = err.response?.data?.error || this.t('Erreur de connexion.', 'Login error.');
        this.error = msg;
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