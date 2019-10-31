<template>
  <v-app id="app">
    <v-toolbar app clipped-left>
      <router-link to="/">Home</router-link>
      <router-link to="/logout">Logout</router-link>
    </v-toolbar>
    <transition name="fade" mode="out-in">
      <router-view />
    </transition>
  </v-app>
</template>

<script>
import routes from "vue-auto-routing";

export default {
  name: "App",
  computed: {
    routes() {
      return routes;
    }
  }
};
</script>

<style lang="scss">
#app {
  font-family: "Avenir", Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
  background-color: #edf4f8;
  #nav {
    text-align: center;
    padding-bottom: 30px;
  }
  a {
    font-weight: bold;
    color: #42b983;
    display: block;
    padding: 5px;
    &.router-link-exact-active {
      color: #2c3e50;
    }
  }

  .fade-enter-active,
  .fade-leave-active {
    transition-duration: 0.2s;
    transition-property: opacity;
    transition-timing-function: ease;
  }

  .fade-enter,
  .fade-leave-active {
    opacity: 0;
  }
}
</style>
