<template>
  <div class="register-form">
    <h2>Créer un compte</h2>

    <form @submit.prevent="register">
      <input v-model="nom_utilisateur" placeholder="Nom d'utilisateur" required />
      <input v-model="email" type="email" placeholder="Email" required />
      <input v-model="mot_de_passe" type="password" placeholder="Mot de passe" required />

      <input
        v-model="confirm"
        type="password"
        placeholder="Confirmer le mot de passe"
        required
        :style="confirm ? (motsDePasseOk ? styleValide : styleInvalide) : ''"
      />

      <button type="button" @click="montrerChampCle = !montrerChampCle">
        {{ montrerChampCle ? 'Annuler Clé Agent' : 'Je suis agent' }}
      </button>

      <input
        v-if="montrerChampCle"
        v-model="access_key"
        placeholder="Clé d’accès agent"
        @input="verifierCle"
        :style="access_key ? (cleValide === true ? styleValide : cleValide === false ? styleInvalide : '') : ''"
      />

      <button type="submit" :disabled="loading || !motsDePasseOk">
        {{ loading ? 'Création...' : 'S’inscrire' }}
      </button>

      <p v-if="error" class="error-message">{{ error }}</p>
      <p v-if="success" class="success">{{ success }}</p>
    </form>
  </div>
</template>

<script>
    import { register } from '../services/api';
    import API from '../services/api';

    export default {
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

                if (this.mot_de_passe !== this.confirm) {
                this.error = 'Les mots de passe ne correspondent pas.';
                return;
                }

                // Bloquer l'inscription agent si la clé est fausse
                if (this.access_key && this.cleValide === false) {
                    this.error = 'Clé d’accès invalide.';
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

                const res = await register(payload);

                this.$emit(
                    'switchToLogin',
                    `Compte créé avec succès. Vous pouvez maintenant vous connecter.`
                );

                // Reset
                this.nom_utilisateur = '';
                this.email = '';
                this.mot_de_passe = '';
                this.confirm = '';
                this.access_key = '';
                this.cleValide = null;
                this.montrerChampCle = false;
                } catch (err) {
                    this.error = err.response?.data?.error || 'Erreur inconnue.';
                } finally {
                    this.loading = false;
                }
            }
        }
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