<template>
  <v-layout row wrap class="rubric-row">
    <v-flex xs12>
      <v-layout align-center fill-height class="header">
        {{ header }}
      </v-layout>
    </v-flex>
    <v-spacer />
    <v-flex xs12 sm4>
      <v-layout
        align-center
        fill-height
        class="option"
        :class="{ yes: value === 1 }"
        :color="value === 0 ? 'green' : 'transparent'"
        @click="$emit('input', 1)"
      >
        <div class="full-width">{{ textYes }}</div>
      </v-layout>
    </v-flex>
    <v-flex xs12 sm4>
      <v-layout
        align-center
        fill-height
        class="option"
        :class="{ no: value === 0 }"
        :color="value === 0 ? 'red' : 'transparent'"
        @click="$emit('input', 0)"
      >
        <div class="full-width">{{ textNo }}</div>
      </v-layout>
    </v-flex>
    <v-flex xs12 sm4>
      <v-layout
        align-center
        fill-height
        class="option"
        :class="{ unsure: value === null }"
        :color="value === null ? 'gray' : 'transparent'"
        @click="$emit('input', null)"
      >
        <div class="full-width">Not enough information</div>
      </v-layout>
    </v-flex>
  </v-layout>
</template>

<script>
export default {
  name: "Rubric",
  props: {
    header: {
      type: String
    },
    description: {
      type: String
    },
    textYes: {
      type: String
    },
    textNo: {
      type: String
    },
    value: {
      type: Number
    }
  }
};
</script>

<style scoped>
.header {
  font-size: 14pt;
  font-weight: bold;
  padding-right: 15px;
  word-wrap: break-word;
}
.option {
  font-size: 14pt;
  padding: 10px;
  color: #688da1;
  border: 4px solid #688da1;
  border-radius: 10px;
  text-align: center;
  font-weight: bold;
  cursor: pointer;
  word-wrap: break-word;
  transition: background-color 0.3s ease;
}

.yes {
  border-color: #16d739;
  background-color: #16d739;
  color: white;
}

.no {
  border-color: #fe8577;
  background-color: #fe8577;
  color: white;
}

.unsure {
  border-color: #688da1;
  background-color: #688da1;
  color: white;
}

.flex {
  padding: 5px;
}

.full-width {
  width: 100%;
}
</style>
