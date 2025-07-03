<template>
    <div id="app">
        <Navbar @open-login="showLogin = true" />
        <LoginRegisterModal v-if="showLogin" @close="showLogin = false" />
        <router-view />
        <Footer />
    </div>
</template>

<script>
    import Navbar from "@/components/Navbar.vue";
    import Footer from "@/components/Footer.vue";
    import LoginRegisterModal from "@/components/LoginRegisterModal.vue";

    export default {
        components: {
            Navbar,
            LoginRegisterModal,
            Footer,
        },

        data() {
            return {
                showLogin: false,
            };
        },
    };
</script>
