<template>
  <v-app id="app">
    <v-toolbar app clipped-left>
      <v-btn flat icon to="/">
        <v-icon>home</v-icon>
      </v-btn>
      <v-spacer />
      <v-toolbar-items v-if="username">
        <div style="padding-top: 20px; font-size: 12pt;">
          Hello, {{ username }}
        </div>

        <v-menu>
          <template v-slot:activator="{ on }">
            <v-toolbar-title v-on="on">
              <v-btn icon large>
                <v-icon>more_vert</v-icon>
              </v-btn>
            </v-toolbar-title>
          </template>

          <v-list>
            <v-list-tile to="/logout">
              <v-list-tile-title>Logout</v-list-tile-title>
            </v-list-tile>
          </v-list>
        </v-menu>
      </v-toolbar-items>
    </v-toolbar>
    <transition name="fade" mode="out-in">
      <router-view />
    </transition>
  </v-app>
</template>

<script>
import routes from "vue-auto-routing";
import sessionData from "./session";

export default {
  name: "App",
  computed: {
    routes() {
      return routes;
    },
    username() {
      return sessionData.username;
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
