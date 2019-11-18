<template>
  <v-container fluid :key="curriculum">
    <v-layout row wrap>
      <v-alert :value="errorMsg.length > 0" dismissible type="error">
        {{ errorMsg }}
      </v-alert>
      <v-flex xs12 sm6 lg4 xl3 class="section" d-flex>
        <Node v-if="node1" :nodeData="node1" />
        <div v-else class="loading">
          <v-progress-circular indeterminate color="primary" />
        </div>
      </v-flex>
      <v-flex xs12 sm6 lg4 xl3 class="section" d-flex>
        <Node v-if="node2" :nodeData="node2" />
        <div v-else class="loading">
          <v-progress-circular indeterminate color="primary" />
        </div>
      </v-flex>
      <v-spacer />
      <v-flex sm12 lg4 xl6 class="section" height="100%" d-flex>
        <v-layout fill-height row wrap>
          <v-flex xs12>
            <h2>Are these two curricular standards relevant to one another?</h2>
            <v-layout row wrap>
              <v-flex>
                <v-btn
                  flat
                  v-if="answer"
                  @click="setAnswer(null)"
                  style="padding: 5px; min-width: 0px; font-weight: bold;"
                  color="primary"
                >
                  Back
                </v-btn>
              </v-flex>
              <v-spacer />
              <v-flex class="progress"> {{ count }} / {{ total }} </v-flex>
              <v-flex xs12 v-for="option in answers" :key="option.id">
                <v-btn
                  block
                  round
                  outline
                  large
                  :color="option.color"
                  class="answer-button"
                  v-if="!answer || answer.id === option.id"
                  @click="setAnswer(option.id)"
                >
                  <v-icon large>{{ option.icon }}</v-icon>
                  &nbsp;&nbsp;
                  {{ option.text }}
                </v-btn>
                <br />
              </v-flex>
              <v-expand-transition>
                <v-flex xs12 v-show="answer">
                  <v-fade-transition>
                    <v-alert
                      ref="error"
                      v-show="showValidationError"
                      :value="true"
                      color="red"
                      icon="error"
                    >
                      Please complete the rubric to continue
                    </v-alert>
                  </v-fade-transition>
                  <Rubric
                    v-if="answer && answer.showRubric"
                    v-model="rubric"
                    ref="rubric"
                    @change="showValidationError = false"
                  />
                  <br />
                  <v-divider />
                  <br />
                  <h3 v-if="answer">{{ answer.textboxLabel }}</h3>
                  <br />
                  <v-textarea auto-grow solo v-model="comment" />
                </v-flex>
              </v-expand-transition>
              <v-layout row style="text-align: center; margin-top: 25px;">
                <v-spacer />
                <v-flex>
                  <v-tooltip top>
                    <template v-slot:activator="{ on }">
                      <v-btn
                        color="primary"
                        outline
                        fab
                        depressed
                        v-on="on"
                        v-clipboard:copy="shareUrl"
                        @click="setCopied"
                      >
                        <v-icon large>share</v-icon>
                      </v-btn>
                    </template>
                    <span>{{ shareText }}</span>
                  </v-tooltip>
                </v-flex>
                <v-spacer />
                <v-flex>
                  <v-tooltip top>
                    <template v-slot:activator="{ on }">
                      <v-btn
                        color="primary"
                        outline
                        fab
                        depressed
                        :disabled="!answer"
                        v-on="on"
                        @click="submitRating"
                      >
                        <v-icon large>arrow_forward</v-icon>
                      </v-btn>
                    </template>
                    <span>Next</span>
                  </v-tooltip>
                </v-flex>
                <v-spacer />
              </v-layout>
            </v-layout>
          </v-flex>
        </v-layout>
      </v-flex>
    </v-layout>
  </v-container>
</template>

<script>
import _ from "lodash";
import Node from "./Node";
import Rubric from "./Rubric";
import { nodeResource, judgmentResource } from "../../../client";
export default {
  name: "EvaluationWindow",
  components: {
    Node,
    Rubric
  },
  data() {
    return {
      node1: null,
      node2: null,
      rating: null,
      confidence: null,
      comment: "",
      selectedCurriculum: null,
      answer: null,
      showValidationError: false,
      rubric: {},
      count: 1,
      errorMsg: "",
      copied: false
    };
  },
  props: {
    total: {
      type: Number,
      default: 5
    },
    curriculum: {
      type: Number,
      required: false
    }
  },
  created() {
    this.setNodes();
  },
  computed: {
    shareUrl() {
      if (this.node1 && this.node2) {
        let query = { node1: this.node1.id, node2: this.node2.id };
        const route = { name: "judgment-evaluation-index", query };
        return window.location.origin + "/" + this.$router.resolve(route).href;
      }
      return "";
    },
    shareText() {
      return this.copied ? "Copied!" : "Share";
    },
    answers() {
      return [
        {
          id: "yes",
          color: "green",
          icon: "check",
          text: "Yes",
          rating: 1,
          showRubric: true,
          textboxLabel: "What factors made these standards relevant?"
        },
        {
          id: "no",
          color: "red",
          icon: "clear",
          text: "No",
          rating: 0,
          showRubric: true,
          textboxLabel:
            "What were the main indicators that these standards were not relevant?"
        },
        {
          id: "unsure",
          color: "grey",
          icon: "remove",
          text: "Not enough information",
          rating: null,
          showRubric: false,
          textboxLabel:
            "What information was missing that prevented you from deciding?"
        }
      ];
    },
    valid() {
      return this.$refs.rubric.valid;
    }
  },
  watch: {
    curriculum(newVal) {
      if (newVal || newVal === 0) {
        this.node2 = null;
        nodeResource.getNodeInCurriculum(newVal).then(node => {
          this.setNodes(node.id);
        });
      }
    }
  },
  methods: {
    setNodes(nodeID) {
      this.node2 = null;
      this.rating = null;
      this.answer = null;
      this.confidence = null;
      this.startTimer();

      if (!this.maybeSetNodesFromQueryParams(nodeID)) {
        // Randomly get two nodes to compare if the user hasn't specified them.
        nodeResource.getComparisonNodes().then(nodes => {
          this.node1 = this.node1 || nodes[0];
          this.node2 = nodes[1];
        });
      }
    },
    reset() {
      this.node1 = null;
      this.node2 = null;
      this.rating = null;
      this.confidence = null;
      this.comment = "";
      this.valid = true;
      this.selectedCurriculum = null;
      this.answer = null;
      this.rubric = {};
      this.showValidationError = false;
      this.count = 1;
      this.errorMsg = "";
      this.copied = false;
      this.node2 = null;
      if (this.curriculum) {
        nodeResource.getNodeInCurriculum(this.curriculum).then(node => {
          this.setNodes(node.id);
        });
      } else {
        this.setNodes();
      }
    },
    setCopied() {
      this.copied = true;
      setTimeout(() => {
        this.copied = false;
      }, 1500);
    },
    maybeSetNodesFromQueryParams(nodeParam1) {
      nodeParam1 = nodeParam1 || this.$route.query.node1;
      // node1 must be set and a valid number to proceed.
      if (nodeParam1 == null) {
        return false;
      }
      let nodeId1 = parseInt(nodeParam1);
      if (isNaN(nodeId1)) {
        this.errorMsg = "The node1 and node2 parameters must be valid numbers.";
        return false;
      }
      nodeResource.getModel(nodeId1).then(node => {
        this.node1 = node;
      });

      let nodeParam2 = this.$route.query.node2;
      let nodeId2 = parseInt(nodeParam2);
      if (!isNaN(nodeId2)) {
        nodeResource.getModel(nodeId2).then(node => {
          this.node2 = node;
        });
      } else if (nodeParam2 != null) {
        // node2 is specified but not a valid number.
        this.errorMsg = "The node1 and node2 parameters must be valid numbers.";
        nodeResource.getNodeToCompareTo(nodeId1).then(node => {
          this.node2 = node;
        });
      } else {
        nodeResource.getNodeToCompareTo(nodeId1).then(node => {
          this.node2 = node;
        });
      }

      return true;
    },
    submitRating() {
      if (this.valid) {
        const name = this.$route.name.replace("judgment-", "");
        const uiName =
          name.slice(0, 1).toUpperCase() + name.replace("-index", "").slice(1);
        this.stopTimer();
        return judgmentResource
          .submitJudgment(
            this.node1.id,
            this.node2.id,
            this.answer.rating,
            this.confidence,
            uiName,
            {
              comment: this.comment,
              time_for_judgment: this.elapsedTime,
              rubric: this.rubric
            }
          )
          .then(() => {
            if (this.count >= this.total) {
              this.$emit("submitted");
            } else {
              this.count++;
            }
            return this.setNodes();
          });
      } else {
        this.showValidationError = true;

        window.scrollTo({
          top: this.$refs.error.$el.scrollHeight,
          behavior: "smooth"
        });
      }
    },
    skip() {
      return this.setNodes();
    },
    startTimer() {
      this.elapsedTime = null;
      this.resumeTimer();
      window.addEventListener("blur", this.stopTimer.bind(this));
      window.addEventListener("focus", this.resumeTimer.bind(this));
    },
    stopTimer() {
      if (this.timerRunning) {
        this.timerRunning = false;
        this.elapsedTime += Date.now() - this.startTime;
      }
    },
    resumeTimer() {
      if (!this.timerRunning) {
        this.timerRunning = true;
        this.startTime = Date.now();
      }
    },
    setAnswer(answer) {
      this.answer = _.find(this.answers, { id: answer });
      this.rubric = {};
      this.comment = "";
      this.showValidationError = false;
    }
  }
};
</script>

<style scoped>
.section {
  padding: 20px;
}
.loading {
  text-align: center;
  padding-top: 10%;
}

.v-btn {
  border-width: 5px !important;
  height: unset;
  padding: 10px;
  font-weight: bold;
  text-transform: none;
  font-size: 16pt;
}

.v-btn .v-icon {
  font-size: 14pt;
}

/deep/ .v-input--selection-controls {
  padding: 10px 20px;
  border: 2px solid #bbb;
  height: 50px;
  border-radius: 30px;
  width: 100%;
  margin-bottom: 15px;
}
/deep/ .v-input--selection-controls label {
  width: 100%;
}

/deep/ .v-textarea {
  font-size: 16pt;
}

.progress {
  text-align: right;
  font-size: 13pt;
  font-weight: bold;
  margin-bottom: 10px;
  padding: 10px;
}

.v-alert {
  font-size: 14pt;
}
</style>
