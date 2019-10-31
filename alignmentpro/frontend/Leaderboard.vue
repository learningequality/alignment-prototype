<template>
  <v-layout justify-center wrap>
    <h2>Leaderboard</h2>
    <br /><br />
    <v-progress-circular v-if="loading" indeterminate color="grey" />
    <v-card v-else style="width: 700px; max-width: 100%; margin: 0 auto;">
      <v-list two-line>
        <v-list-tile
          v-for="(item, index) in leaderboardCondensed"
          :key="index"
          :class="{ user: index === currentStanding }"
        >
          <v-list-tile-action>
            <div class="rank" :class="{ first: index === 0 }">
              {{ index + 1 }}
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
      loading: false,
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
    currentUser() {
      if (this.leaderboard.length)
        return this.leaderboard[this.currentStanding];
      return { username: "", number_of_judgments: 0 };
    },
    currentStanding() {
      let names = _.map(this.leaderboard, l => l.username);
      return _.indexOf(names, sessionData.username);
    },
    higherRanks() {
      return _.reverse(
        this.leaderboard.slice(
          this.currentStanding - this.leaderboardRange,
          this.currentStanding
        )
      );
    },
    lowerRanks() {
      return _.reverse(
        this.leaderboard.slice(
          this.currentStanding + 1,
          this.currentStanding + this.leaderboardRange
        )
      );
    },
    leaderboardCondensed() {
      return this.higherRanks.concat(this.currentUser).concat(this.lowerRanks);
    }
  },
  methods: {
    getLeaderboard() {
      this.loadingLeaderboard = true;
      leaderboardResource.getLeaderboard().then(results => {
        this.loadingLeaderboard = false;
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
</style>
