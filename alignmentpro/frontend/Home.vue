<template>
  <v-content class="home">
    <v-container fluid>
      <v-layout justify-center row wrap fill-height>
        <v-flex xs12 style="text-align: center; padding-top: 50px;">
          <h1>Semi-Automated Curriculum Alignment Tools</h1>
          <br /><br />
          <h3>You currently have {{ points }} points</h3>
          <br />
          <div style="width: 600px; max-width: 100%; margin: 0 auto;">
            <p v-if="isAdmin">
              <v-btn
                block
                round
                large
                depressed
                color="blue"
                to="/curriculum_review"
                class="white--text"
              >
                Review scanned curriculum documents
              </v-btn>
            </p>
            <p>
              <v-btn
                block
                round
                large
                depressed
                color="blue"
                to="/judgment"
                class="white--text"
              >
                Add curriculum alignment judgments
              </v-btn>
            </p>
            <p>
              <v-btn
                block
                round
                large
                depressed
                color="blue"
                to="/visualization"
                class="white--text"
              >
                View recommendations
              </v-btn>
            </p>
            <br /><br />
            <v-divider />
            <br />
            <Leaderboard />
          </div>
        </v-flex>
      </v-layout>
    </v-container>
  </v-content>
</template>

<script>
import { userResource } from "./client";
import Leaderboard from "./Leaderboard";

export default {
  name: "Home",
  components: {
    Leaderboard
  },
  created() {
    this.getUserPoints();
  },
  data() {
    return {
      points: 0
    };
  },
  computed: {
    isAdmin() {
      return window.isAdmin;
    }
  },
  methods: {
    getUserPoints() {
      let self = this;
      userResource.getUser().then(userData => {
        self.points = userData.points;
      });
    },
    displayName(root, name) {
      name = name.replace(`${root}-`, "");
      return (
        name.slice(0, 1).toUpperCase() + name.replace("-index", "").slice(1)
      );
    }
  }
};
</script>

<style scoped>
.v-btn {
  text-transform: none;
  font-weight: normal !important;
  font-size: 16pt;
}
</style>
