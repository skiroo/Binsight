<template>
    <nav class="navbar">
        <div class="nav-left">
            <img src="@/assets/logo.png" alt="Logo" class="logo" />
            <router-link to="/">Accueil</router-link>
            <router-link to="/upload">Upload</router-link>
            <router-link to="/dashboard">Dashboard</router-link>
            <router-link to="/map">Carte</router-link>
            <router-link to="/about">À propos</router-link>
        </div>

        <div class="nav-right">
            <template v-if="user">
                <span>Bienvenue, {{ user.nom_utilisateur }}</span>
                <button @click="logout">Déconnexion</button>
            </template>
            <template v-else>
                <button @click="$emit('open-login')">Connexion / Inscription</button>
            </template>
        </div>
    </nav>
</template>

<script>
    export default {
        data() {
            return {
                user: null,
            };
        },

        created() {
            const stored = localStorage.getItem("user");
            this.user = stored ? JSON.parse(stored) : null;
        },

        methods: {
            logout() {
                localStorage.removeItem("user");
                this.user = null;
                this.$router.push("/");
                location.reload(); // recharge l'état global
            },
        },
    };
</script>