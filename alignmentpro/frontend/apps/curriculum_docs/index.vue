<template>
  <v-container fluid style="background-color: #edf4f8;">
    <v-content>
      <v-progress-circular v-if="loading" indeterminate color="grey" />
      <v-alert v-else-if="error" :value="true" color="warning" outline>
        {{ error }}
      </v-alert>
      <v-layout row wrap v-else>
        <v-flex xs9>
          <v-breadcrumbs :items="path">
            <template v-slot:divider>
              <v-icon>chevron_right</v-icon>
            </template>
            <template v-slot:item="props">
              <div class="breadcrumb">
                <Flag v-if="props.item.country" :country="props.item.country" />
                &nbsp;
                {{ props.item.text }}
              </div>
            </template>
          </v-breadcrumbs>
        </v-flex>
        <v-flex xs3 style="text-align: right;">
          <v-btn
            color="blue"
            large
            depressed
            round
            outline
            @click="submitDraftReview"
            >Save</v-btn
          >
          <v-btn
            dark
            color="blue"
            large
            depressed
            round
            @click="submitFinalReview"
            >Finalize</v-btn
          >
        </v-flex>
        <v-flex xs12 sm6 md4>
          <img :src="image_url" style="max-width:100%; max-height:100%" />
        </v-flex>
        <v-flex xs12 sm6 md8>
          <v-container fluid>
            <h3>
              Please mark up the following text according to the following
              rules:
            </h3>
            <ul>
              <li>
                Topics
                <v-tooltip top max-width="300px">
                  <template v-slot:activator="{ on }">
                    <v-icon class="help-icon" color="blue" small dark v-on="on"
                      >info_outline</v-icon
                    >
                  </template>
                  <span
                    >Under a given subject area, a topic is a subfield within
                    which a given learning objective falls; what the learning
                    objective is "about" (e.g. algebra)</span
                  >
                </v-tooltip>
                should be <b>bolded</b>
              </li>
              <li>
                Learning objectives
                <v-tooltip top max-width="300px">
                  <template v-slot:activator="{ on }">
                    <v-icon class="help-icon" color="blue" small dark v-on="on"
                      >info_outline</v-icon
                    >
                  </template>
                  <span
                    >This is what the student should know, understand, or be
                    able to do at the end of the activity/class/semester.
                    Learning objectives should always be framed as tasks with
                    verb statements, not noun phrases (e.g. "Seek and give
                    factual information")</span
                  >
                </v-tooltip>
                should be <em>italicized</em>
              </li>
              <li>
                Make sure each topic and learning objective is on its own line
              </li>
              <li>
                Please correct any spelling errors
              </li>
            </ul>
            <v-btn flat color="blue" @click="dialog = true">See Example</v-btn>
            <br />
            <v-divider />
            <br />
            <input type="hidden" name="section_id" :value="section_id" />
            <Editor
              id="texteditor"
              :init="editorInit"
              v-model="section_text"
            ></Editor>
          </v-container>
        </v-flex>
      </v-layout>
    </v-content>
    <v-dialog v-model="dialog" width="500">
      <v-card>
        <v-card-text>
          <p class="example-header">Before</p>
          <div class="example-text">
            <p>
              Algebra: Learner should be able to add numbers together, subtract
              numbers, and multiply numbers
            </p>
          </div>
          <br />
          <p class="example-header">After</p>
          <div class="example-text">
            <p><b>Algebra</b></p>
            <p><i>Add numbers together</i></p>
            <p><i>Subtract numbers</i></p>
            <p><i>Multiply numbers</i></p>
          </div>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn dark depressed color="blue" @click="dialog = false">
            Got it!
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
    <v-dialog v-model="finished" width="500">
      <v-card>
        <v-card-text>

          <div style="text-align: center;">
            <div>
              <img
                style="width: 150px; margin-right: 20px; vertical-align: bottom;"
                src="../judgment/evaluation/robot.png"
              />
              <div
                style="font-size: 20pt; font-family: Courier; display: inline-block; width: 200px; text-align: center;"
              >
                <em>Munch, munch.</em> More data, yum! Thank you!
              </div>
            </div>
            <br /><br /><br />

            <h1>Way to go!</h1>
            <br />
            <h2>
              You got <b>{{ points }} points</b> for your hard work!
            </h2>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn dark depressed color="blue" @click="finished = false">
            Okay!
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script>
import _ from "lodash";
import Editor from "@tinymce/tinymce-vue";

import Flag from "../judgment/evaluation/Flag";
import { curriculumDocReviewResource } from "../../client";

export default {
  name: "CurriculumDocs",
  components: {
    Editor,
    Flag
  },
  created() {
    this.getSectionToReview();
  },
  computed: {
    editorInit() {
      return {
        height: "400px",
        menubar: false,
        plugins: "lists",
        toolbar: "bold italic | undo redo"
      };
    },
    path() {
      let list = _.map(this.ancestors, a => {
        return { text: a, country: null };
      });
      return [
        { country: this.curriculum.country, text: this.curriculum.title }
      ].concat(list);
    }
  },
  data() {
    return {
      error: null,
      image_url: "",
      section_id: null,
      section_text: "",
      curriculum: null,
      ancestors: [],
      loading: false,
      dialog: false,
      points: null,
      finished: false,
    };
  },
  methods: {
    getSectionToReview() {
      this.loading = true;
      curriculumDocReviewResource
        .getRandomDocTopicForReview()
        .then(section_data => {
          this.loading = false;
          if (section_data["error"]) {
            this.error = section_data["error"];
          } else {
            this.image_url = section_data["image_url"];
            this.section_id = section_data["section_id"];
            this.section_text = section_data["section_text"];
            this.curriculum = section_data["document"];
            this.ancestors = section_data["ancestors"];
          }
        });
    },
    submitDraftReview() {
      this.submitReview();
    },
    submitFinalReview() {
      this.submitReview(true);
    },
    submitReview(final) {
      let self = this;
      curriculumDocReviewResource.submitReview(
        this.section_id,
        this.section_text,
        final
      ).then(response => {
        if (response.data.success && response.data.points && response.data.points > 0) {
          self.finished = true;
          self.points = response.data.points;

          this.$confetti.start();
          setTimeout(() => {
            this.$confetti.stop();
          }, 4000);
        }
      });
    }
  }
};
</script>

<style scoped>
.breadcrumb {
  font-size: 14pt;
}

.help-icon {
  cursor: pointer;
}

ul {
  font-size: 12pt;
}

.example-header {
  margin-bottom: 5px;
}

.v-card__text {
  font-size: 12pt;
}

.example-text {
  border: 1px solid #ccc;
  padding: 10px;
}
</style>
