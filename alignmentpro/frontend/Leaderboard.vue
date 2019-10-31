<template>
  <v-layout justify-center wrap>
    <v-flex xs12>
      <h2>Leaderboard</h2>
      <br /><br />
    </v-flex>
    <p v-if="loading">
      <v-progress-circular indeterminate color="grey" />
    </p>
    <v-card v-else style="width: 700px; max-width: 100%; margin: 0 auto;">
      <p v-if="firstPlace" class="first-place">
        🎉&nbsp;&nbsp;{{ firstPlace.username }} is in the lead with
        <b>{{ firstPlace.number_of_judgments | formatNumber }}</b> points!
      </p>

      <v-list two-line>
        <v-list-tile
          v-for="(item, index) in leaderboardCondensed"
          :key="index"
          :class="{ user: item.username === currentUser.username }"
        >
          <v-list-tile-action>
            <div class="rank" :class="{ first: item.index === 0 }">
              {{ item.index + 1 }}
            </div>
          </v-list-tile-action>
          <v-list-tile-content>
            <v-list-tile-title>
              {{ item.username }}
            </v-list-tile-title>
          </v-list-tile-content>
          <v-spacer />
          <v-list-tile-content>
            <v-list-tile-title class="points">{{
              item.number_of_judgments | formatNumber
            }}</v-list-tile-title>
          </v-list-tile-content>
        </v-list-tile>
      </v-list>
    </v-card>
  </v-layout>
</template>

<script>
import _ from "lodash";
import { leaderboardResource } from "./client";
import sessionData from "./session";
import numeral from "numeral";

export default {
  name: "Leaderboard",
  data() {
    return {
      loading: true,
      leaderboard: [],
      leaderboardRange: 2
    };
  },
  mounted() {
    this.getLeaderboard();
  },
  filters: {
    formatNumber(value) {
      return numeral(value).format("0,0");
    }
  },
  computed: {
    firstPlace() {
      return this.leaderboard[0];
    },
    currentUser() {
      return this.leaderboard[this.currentStanding];
    },
    currentStanding() {
      let names = _.map(this.leaderboard, l => l.username);
      return _.indexOf(names, sessionData.username);
    },
    leaderboardCondensed() {
      let start = Math.max(0, this.currentStanding - this.leaderboardRange - 1);
      let end = Math.min(
        this.leaderboard.length,
        this.currentStanding + this.leaderboardRange + 1
      );
      return this.leaderboard.slice(start, end);
    }
  },
  methods: {
    getLeaderboard() {
      this.loading = true;
      leaderboardResource.getLeaderboard().then(results => {
        this.loading = false;
        results.forEach((r, i) => {
          r.index = i;
        });
        this.leaderboard = results;
      });
    }
  }
};
</script>

<style scoped>
div[role="listitem"] {
  font-size: 14pt;
}

div[role="listitem"]:not(:last-child) {
  border-bottom: 1px solid #eee;
}

div[role="listitem"].user {
  background-color: #fff9c4;
}

div[role="listitem"].user .rank {
  background-color: #f9a825;
}

.rank {
  background-color: #90a4ae;
  color: white;
  height: 50px;
  width: 50px;
  text-align: center;
  border-radius: 100px;
  font-weight: bold;
  padding-top: 10px;
  margin-right: 20px;
  font-size: 15pt;
  min-width: fit-content;
}

.rank.first {
  background-color: #4caf50 !important;
}

.points {
  text-align: right;
  color: gray;
  font-weight: bold;
  font-size: 16pt;
}

.first-place {
  font-size: 16pt;
  font-weight: normal;
  margin-top: 10px;
}
</style>
