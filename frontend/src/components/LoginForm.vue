<template>
  <form @submit.prevent="handleLogin">
    <input
      v-model="email"
      placeholder="Email"
      type="email"
      required
      :style="{ backgroundColor: 'var(--input-bg)', color: 'var(--input-text)' }"
    />
    <input
      v-model="password"
      placeholder="Mot de passe"
      type="password"
      required
      :style="{ backgroundColor: 'var(--input-bg)', color: 'var(--input-text)' }"
    />
    <button type="submit">Se connecter</button>
    <p v-if="error" class="error">{{ error }}</p>
  </form>
</template>