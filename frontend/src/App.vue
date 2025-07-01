<template>
    <div id="app">
        <Navbar @open-login="showLogin = true" />
        <LoginRegisterModal v-if="showLogin" @close="showLogin = false" />
        <router-view />
    </div>
</template>

<script>
    import Navbar from "@/components/Navbar.vue";
    import LoginRegisterModal from "@/components/LoginRegisterModal.vue";

    export default {
        components: {
            Navbar,
            LoginRegisterModal,
        },

        data() {
            return {
                showLogin: false,
            };
        },
    };
</script>
