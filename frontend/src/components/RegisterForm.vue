<template>
    <form @submit.prevent="handleRegister">
        <input v-model="nom_utilisateur" placeholder="Nom d'utilisateur" required />
        <input v-model="email" placeholder="Email" type="email" required />
        <input v-model="mot_de_passe" placeholder="Mot de passe" type="password" required />

        <input v-model="accessKey" placeholder="Clé d'accès (optionnel)" />
        
        <button type="submit">Créer un compte</button>
        <p v-if="error" class="error">{{ error }}</p>
    </form>
</template>

<script>
    import { register } from '../services/api';

    export default {
        data() {
            return {
                nom_utilisateur: '',
                email: '',
                mot_de_passe: '',
                accessKey: '',
                error: ''
            };
        },

        methods: {
            async handleRegister() {
                let role = 'citoyen';
                const CLE_AGENT = 'AGENT2025'; // Clé définie par l'admin côté client

                if (this.accessKey === CLE_AGENT) {
                    role = 'agent';
                }

                try {
                    const res = await register({
                        nom_utilisateur: this.nom_utilisateur,
                        email: this.email,
                        mot_de_passe: this.mot_de_passe,
                        role
                    });
                    localStorage.setItem('user', JSON.stringify(res.data));
                    this.$emit('success');
                    this.$router.push('/dashboard');
                } catch (err) {
                    this.error = "Inscription échouée. Vérifie les champs.";
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