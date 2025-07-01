<template>
    <div class="modal">
        <button @click="mode = 'login'">Connexion</button>
        <button @click="mode = 'register'">Inscription</button>
        <component :is="currentComponent" @success="$emit('close')" />
    </div>
</template>

<script>
    import LoginForm from './LoginForm.vue';
    import RegisterForm from './RegisterForm.vue';

    export default {
        data() {
            return { mode: 'login' };
        },

        computed: {
            currentComponent() {
                return this.mode === 'login' ? LoginForm : RegisterForm;
            }
        },

        components: {
            LoginForm,
            RegisterForm
        }
    };
</script>
