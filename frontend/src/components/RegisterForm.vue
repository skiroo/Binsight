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
                const CLE_AGENT = 'AGENT2025'; // Clé définie par l'admin

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
