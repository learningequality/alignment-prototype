<template>
  <v-layout row wrap>
    <v-flex xs12 v-for="item in items" :key="item.key" class="rubric-row">
      <RubricRow
        v-model="rubric[item.key]"
        :header="item.header"
        :description="item.description"
        :textYes="item.textYes"
        :textNo="item.textNo"
        @input="$emit('change')"
      />
    </v-flex>
  </v-layout>
</template>

<script>
import _ from "lodash";
import RubricRow from "./RubricRow";

export default {
  name: "Rubric",
  props: {
    value: {
      type: Object
    }
  },
  components: {
    RubricRow
  },
  computed: {
    rubric: {
      get() {
        return this.value;
      },
      set(value) {
        this.$emit("input", value);
      }
    },
    items() {
      return [
        {
          key: "subject",
          header: "Subject",
          textYes:
            "They relate to the same general subject area or field of study",
          textNo:
            "They're not related to the same general subject area or field of study"
        },
        {
          key: "keywords",
          header: "Keywords",
          textYes: "They pertain to similar keywords or concepts",
          textNo: "The keywords or concepts mentioned are different"
        },
        {
          key: "task",
          header: "Task",
          textYes:
            "They require learners to perform the same type of task or demonstration of competency",
          textNo:
            "They require different types of tasks or demonstrations of competency"
        },
        {
          key: "level",
          header: "Level",
          textYes:
            "They require the same level of learner proficiency to engage",
          textNo: "They are targeted at different levels of learner proficiency"
        },
        {
          key: "specificity",
          header: "Specificity",
          textYes: "They are at the same level of specificity / granularity",
          textNo:
            "One standard is much broader in scope or coverage than the other"
        }
      ];
    },
    valid() {
      return _.every(this.items, i => {
        return this.rubric[i.key] !== undefined;
      });
    }
  }
};
</script>

<style scoped>
.rubric-row {
  margin-top: 10px !important;
}
</style>
