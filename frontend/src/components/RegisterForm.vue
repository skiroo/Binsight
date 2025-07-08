
<!-- RegisterForm.vue -->
<template>
  <div class="register-form">
    <h2>{{ t('Créer un compte', 'Create an account') }}</h2>

    <form @submit.prevent="register">
      <input v-model="nom_utilisateur" :placeholder="t(`Nom d'utilisateur`, 'Username')" required />
      <input v-model="email" type="email" :placeholder="t('Email', 'Email')" required />
      <input v-model="mot_de_passe" type="password" :placeholder="t('Mot de passe', 'Password')" required />

      <input
        v-model="confirm"
        type="password"
        :placeholder="t('Confirmer le mot de passe', 'Confirm password')"
        required
        :style="confirm ? (motsDePasseOk ? styleValide : styleInvalide) : ''"
      />

      <button type="button" @click="montrerChampCle = !montrerChampCle">
        {{ montrerChampCle ? t('Annuler Clé Agent', 'Cancel Agent Key') : t('Je suis agent', 'I am an agent') }}
      </button>

      <input
        v-if="montrerChampCle"
        v-model="access_key"
        :placeholder="t(`Clé d’accès agent`, 'Agent access key')"
        @input="verifierCle"
        :style="access_key ? (cleValide === true ? styleValide : cleValide === false ? styleInvalide : '') : ''"
      />

      <button type="submit" :disabled="loading || !motsDePasseOk">
        {{ loading ? t('Création...', 'Creating...') : t("S’inscrire", "Sign up") }}
      </button>

      <p v-if="error" class="error-message">{{ error }}</p>
      <p v-if="success" class="success-message">{{ success }}</p>
    </form>
  </div>
</template>

<script>
import { register } from '../services/api';
import API from '../services/api';

export default {
  props: {
    lang: {
      type: String,
      default: 'fr'
    }
  },
  data() {
    return {
      nom_utilisateur: '',
      email: '',
      mot_de_passe: '',
      confirm: '',
      access_key: '',
      montrerChampCle: false,
      cleValide: null,
      loading: false,
      error: '',
      success: '',
      styleValide: 'border: 2px solid #10b981;',
      styleInvalide: 'border: 2px solid #ff6b6b;'
    };
  },
  computed: {
    motsDePasseOk() {
      return this.mot_de_passe === this.confirm;
    }
  },
  methods: {
    t(fr, en) {
      return this.lang === 'fr' ? fr : en;
    },
    async verifierCle() {
      this.cleValide = null;
      if (!this.access_key) return;
      try {
        const res = await API.get('/verify_key', {
          params: { cle: this.access_key }
        });
        this.cleValide = res.data.valide === true;
      } catch (e) {
        this.cleValide = false;
      }
    },
    async register() {
      this.error = '';
      this.success = '';

      if (!this.motsDePasseOk) {
        this.error = this.t('Les mots de passe ne correspondent pas.', 'Passwords do not match.');
        return;
      }
      if (this.access_key && this.cleValide === false) {
        this.error = this.t("Clé d’accès invalide.", "Invalid access key.");
        return;
      }

      this.loading = true;
      try {
        const roleFinal = this.access_key && this.cleValide === true ? 'agent' : 'citoyen';
        const payload = {
          nom_utilisateur: this.nom_utilisateur,
          email: this.email,
          mot_de_passe: this.mot_de_passe,
          role: roleFinal,
          access_key: this.access_key || ''
        };
        await register(payload);
        this.$emit(
          'switchToLogin',
          this.t('Compte créé avec succès. Vous pouvez maintenant vous connecter.',
                 'Account created successfully. You can now log in.')
        );
        this.nom_utilisateur = '';
        this.email = '';
        this.mot_de_passe = '';
        this.confirm = '';
        this.access_key = '';
        this.cleValide = null;
        this.montrerChampCle = false;
      } catch (err) {
        this.error = err.response?.data?.error || this.t('Erreur inconnue.', 'Unknown error.');
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
  margin-top: 10px;
}
.error-message {
  color: #ff6b6b;
  margin-top: 10px;
  font-size: 0.9rem;
}
</style>
