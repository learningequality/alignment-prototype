<template>
  <v-content class="home">
    <div>
        <h1>Semi-Automated Curriculum Alignment Tools</h1>
        <router-link to="/judgment">Add Curriculum Alignment Judgments</router-link>
        <router-link to="/curriculum_review">Review Scanned Curriculum Documents</router-link>
        <router-link to="/visualization">View Recommendations</router-link>
    </div>
  </v-content>
</template>

<script>

export default {
  name: "Home",
  computed: {
  },
  methods: {
    displayName(root, name) {
      name = name.replace(`${root}-`, "");
      return (
        name.slice(0, 1).toUpperCase() + name.replace("-index", "").slice(1)
      );
    }
  }
};
</script>
