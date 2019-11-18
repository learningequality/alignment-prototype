<template>
  <v-container
    fluid
    fill-height
    style="background-color: #1A2039; color: white;"
  >
    <v-layout align-center justify-center fill-height row wrap>
      <div style="text-align: center;">
        <div>
          <img
            style="width: 150px; margin-right: 20px; vertical-align: bottom;"
            src="./robot.png"
          />
          <div
            style="font-size: 20pt; font-family: Courier; display: inline-block; width: 200px; text-align: center;"
          >
            Thanks for teaching me!
          </div>
        </div>
        <br /><br /><br />

        <h1>Way to go!</h1>
        <br />
        <h2>
          You completed <b>{{ count }}</b> more evaluations successfully.
        </h2>
        <br />
        <v-btn
          round
          depressed
          large
          dark
          color="primary"
          @click="$emit('continue')"
          >Keep going</v-btn
        >
        <br /><br /><br /><br /><br /><br />
        <v-divider dark />
        <div v-if="loadingLeaderboard">
          <br />
          <p style="color: white;">Loading leaderboard...</p>
          <v-progress-linear indeterminate />
        </div>
        <v-container fluid v-else-if="!isNaN(currentStanding)">
          <v-layout row>
            <v-flex xs4>
              <h2>
                You are <b>#{{ currentStanding + 1 }}</b> on the leaderboard!
              </h2>
              <p style="color: white;">
                You've made
                {{ currentUser.number_of_judgments }} evaluations so far
              </p>
              <v-btn
                flat
                color="primary"
                href="https://alignmentapp.learningequality.org/api/leaderboard"
                target="_blank"
                >See leaderboard</v-btn
              >
            </v-flex>
            <v-spacer />
            <v-flex class="rank">
              <div class="number you">{{ currentStanding + 1 }}</div>
              <p>
                <b>{{ currentUser.username }}</b>
              </p>
            </v-flex>
            <v-spacer />
            <v-flex
              v-for="(person, i) in nextFive"
              class="rank"
              :key="person.username"
            >
              <v-tooltip top>
                <template v-slot:activator="{ on }">
                  <div dark v-on="on">
                    <div class="number">
                      {{ currentStanding - i }}
                    </div>
                    <p style="color: white;">{{ person.username }}</p>
                  </div>
                </template>
                <span>{{ person.number_of_judgments }} evaluations</span>
              </v-tooltip>
            </v-flex>
          </v-layout>
        </v-container>
      </div>
    </v-layout>
  </v-container>
</template>

<script>
import _ from "lodash";
import { leaderboardResource } from "../../../client";
import sessionData from "../../../session";

export default {
  name: "DoneScreen",
  props: {
    count: {
      type: Number,
      default: 0
    }
  },
  data() {
    return {
      loadingLeaderboard: false,
      leaderboard: []
    };
  },
  computed: {
    currentUser() {
      if (this.leaderboard.length)
        return this.leaderboard[this.currentStanding];
      return { username: "", number_of_judgments: 0 };
    },
    currentStanding() {
      let names = _.map(this.leaderboard, l => l.username);
      let index = _.indexOf(names, sessionData.username);
      return index;
    },
    nextFive() {
      return _.reverse(
        this.leaderboard.slice(
          Math.max(this.currentStanding - 5, 0),
          this.currentStanding
        )
      );
    }
  },
  methods: {
    load() {
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
b {
  color: #18baff;
}

p {
  font-size: 12pt;
}

.rank {
  text-align: center;
  cursor: pointer;
  max-width: 100px;
  word-break: break-word;
}

.number {
  background-color: #3852c0;
  border-radius: 100px;
  width: 50px;
  height: 50px;
  padding: 7px;
  margin: 0 auto;
  color: white;
  font-size: 18pt;
  margin-bottom: 10px;
}

.number.you {
  background-color: #18baff;
}
</style>
