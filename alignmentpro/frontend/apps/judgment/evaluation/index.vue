<template>
  <v-content>
    <v-container v-if="oneComparison">
      <EvaluationWindow @submitted="handleSubmit" :total="1" />
      <v-dialog v-model="dialog" width="500">
        <v-card>
          <v-card-title class="headline" primary-title color="#edf4f8">
            Thank you for your feedback!
          </v-card-title>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn color="primary" depressed @click="reload">
              OK
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>
    </v-container>

    <v-window v-model="step" v-else>
      <v-window-item :value="0">
        <v-layout align-center justify-center fill-height row wrap>
          <div style="text-align: center;">
            <h1>Source standard to compare items to</h1>
            <br />
            <br />
            <CurriculumFilter
              v-model="curriculum"
              hint="Leave blank to compare a random curriculum"
              persistent-hint
            />
            <br />
            <v-btn round depressed large dark color="primary" @click="step++">
              Start
            </v-btn>
          </div>
        </v-layout>
      </v-window-item>
      <v-window-item :value="1">
        <EvaluationWindow
          @submitted="handleSubmit"
          :total="Number(count)"
          :curriculum="curriculum && curriculum.id"
          ref="eval"
        />
      </v-window-item>
      <v-window-item :value="2">
        <DoneScreen @continue="backToStart" :count="count" ref="donescreen" />
      </v-window-item>
    </v-window>
  </v-content>
</template>

<script>
import EvaluationWindow from "./EvaluationWindow";
import CurriculumFilter from "./CurriculumFilter";
import DoneScreen from "./DoneScreen";

export default {
  name: "Judgment",
  components: {
    EvaluationWindow,
    CurriculumFilter,
    DoneScreen
  },
  data() {
    return {
      count: 5,
      step: 0,
      curriculum: null,
      oneComparison: false,
      dialog: false
    };
  },
  mounted() {
    this.oneComparison = !!this.$route.query.node2;
  },
  methods: {
    reload() {
      window.location = "/#/judgment/evaluation";
      window.location.reload();
    },
    backToStart() {
      this.step = 1;
      this.$refs.eval.reset();
      this.$confetti.stop();
    },
    handleSubmit() {
      if (this.oneComparison) {
        this.dialog = true;
      } else {
        this.step++;
        this.$confetti.start();
        this.$refs.donescreen.load();
        setTimeout(() => {
          this.$confetti.stop();
        }, 2000);
      }
    }
  }
};
</script>

<style scoped>
.v-window {
  height: 100%;
}

/deep/ .v-window__container,
.v-window-item {
  height: 100%;
}
</style>
