<template>
    <v-container>
        <v-content>
            <div v-if="error">
                <p>{{ error }}</p>
            </div>
            <div v-else>
                <input type="hidden" name="section_id" :value="section_id"/>
                <div style="height: 30px; width: 100vw; align: right">
                    <v-btn color="primary" @click="submitReview">Save</v-btn>
                </div>
                <div style="overflow: scroll">
                    <div style="width: 48%; float: left">
                        <img :src="image_url" style="max-width:100%; max-height:100%"/>
                    </div>
                    <div style="width: 48%; height:95vh; float: right">
                        <Editor id="texteditor" :init="editorInit" v-model="section_text"></Editor>
                    </div>
                </div>
            </div>
        </v-content>
    </v-container>
</template>

<script>
import Editor from '@tinymce/tinymce-vue';
import tinymce from 'tinymce/tinymce';

import { curriculumDocReviewResource } from "../../client";
export default {
  name: "CurriculumDocs",
  components: {
    'Editor': Editor
  },
  created() {
    this.getSectionToReview();
  },
  computed: {
    editorInit() {
      return {
        height: "100%",
        menubar: false,
        plugins: "lists",
        toolbar: "bold italic | bullist | undo redo"
      }
    }
  },
  data() {
    return {
      error: null,
      image_url: '',
      section_id: null,
      section_text: ''
    };
  },
  methods: {
    getSectionToReview() {
      curriculumDocReviewResource.getRandomDocTopicForReview().then(section_data => {
        if (section_data["error"]) {
          this.error = section_data["error"];
        } else {
          this.image_url = section_data["image_url"];
          this.section_id = section_data["section_id"];
          this.section_text = section_data["section_text"];
          console.log("section_text = " + this.section_text);
        }
      });
    },
    submitReview() {
      curriculumDocReviewResource.submitReview(this.section_id, this.section_text);
    }
  }
};
</script>
