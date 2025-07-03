<template>
    <form @submit.prevent="handleLogin">
        <input v-model="email" placeholder="Email" type="email" required />
        <input v-model="password" placeholder="Mot de passe" type="password" required />
        <button type="submit">Se connecter</button>
        <p v-if="error" class="error">{{ error }}</p>
    </form>
</template>

<script>
    import { login } from '../services/api';

    export default {
        data() {
            return {
                email: '',
                password: '',
                error: ''
            };
        },

        methods: {
            async handleLogin() {
                try {
                    const res = await login(this.email, this.password);
                    const user = res.data;
                    localStorage.setItem('user', JSON.stringify(user));
                    this.$emit('success');
                    this.$router.push('/dashboard');
                } catch (err) {
                    this.error = "Email ou mot de passe incorrect";
                }
            }
        }
    };
</script>
