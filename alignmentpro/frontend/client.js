/* ***********************************************
* MIT License
*
* Copyright (c) 2019 Learning Equality
*
* Permission is hereby granted, free of charge, to any person obtaining a copy
* of this software and associated documentation files (the "Software"), to deal
* in the Software without restriction, including without limitation the rights
* to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
* copies of the Software, and to permit persons to whom the Software is
* furnished to do so, subject to the following conditions:
*
* The above copyright notice and this permission notice shall be included in all
* copies or substantial portions of the Software.
*
* THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
* IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
* FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
* AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
* LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
* OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
* SOFTWARE.
*
* ********************************************* */

import _ from "lodash";
import axios from "axios";
import session from "./session";
import get_cookie from "get-cookie";

export const baseUrl = "";

export function login(username, password) {
  return axios
    .post(
      `${baseUrl}/api-token-auth/`,
      { username, password },
      { headers: { "X-CSRFToken": get_cookie("csrftoken") } }
    )
    .then(response => {
      session.username = username;
      session.token = response.data.token;
    });
}

class Resource {
  constructor(resourceName) {
    this.resourceName = resourceName;
  }

  get baseUrl() {
    return `${baseUrl}/api/${this.resourceName}/`;
  }

  get config() {
    return {
      headers: {
        Authorization: `Token ${session.token}`
      }
    };
  }

  modelUrl(id) {
    return `${this.baseUrl}${id}`;
  }

  getModel(id) {
    return axios.get(this.modelUrl(id), this.config).then(response => {
      return response.data;
    });
  }
}

class DocumentResource extends Resource {
  getDocuments() {
    return axios.get(`${this.baseUrl}`, this.config).then(response => {
      return response.data.results;
    });
  }
}
export const documentResource = new DocumentResource("document");

class LeaderboardResource extends Resource {
  get baseUrl() {
    return `${baseUrl}/api/${this.resourceName}`;
  }

  getLeaderboard() {
    return axios.get(`${this.baseUrl}`, this.config).then(response => {
      return response.data;
    });
  }
}
export const leaderboardResource = new LeaderboardResource("leaderboard");

class NodeResource extends Resource {
  getNodeInCurriculum(curriculum) {
    return axios
      .get(`${this.baseUrl}?document=${curriculum}`, this.config)
      .then(response => {
        let results = response.data.results;
        let depthMax = _.maxBy(response.data.results, "depth").depth;
        results = _.filter(results, { depth: depthMax });
        return results[_.random(0, results.length - 1)];
      });
  }
  getComparisonNodes(curriculum, scheduler = "random") {
    return axios
      .get(`${this.baseUrl}?scheduler=${scheduler}`, this.config)
      .then(response => {
        return response.data.results;
      });
  }
  getNodeToCompareTo(baseNode, scheduler = "random") {
    return axios
      .get(
        `${this.baseUrl}?left_root_id=${baseNode}&scheduler=${scheduler}`,
        this.config
      )
      .then(response => {
        return _.reject(response.data.results, { id: baseNode })[0];
      });
  }
  getDocumentNode(documentID) {
    return axios
      .get(`${this.baseUrl}?document=${documentID}&depth=1`, this.config)
      .then(response => {
        return response.data.results[0];
      });
  }
  getChildren(nodeID) {
    return axios.get(`${this.baseUrl}${nodeID}`, this.config).then(response => {
      return response.data.children;
    });
  }
}

export const nodeResource = new NodeResource("node");

class JudgmentResource extends Resource {
  submitJudgment(node1, node2, rating, confidence, uiName, extraFields) {
    return axios.post(
      this.baseUrl,
      {
        node1,
        node2,
        rating,
        confidence,
        ui_name: uiName,
        ui_version_hash: "2019_11_with_rubric",
        mode: "rapid_feedback",
        extra_fields: {
          ...extraFields,
          is_dev_build: process.env.NODE_ENV !== "production"
        }
      },
      this.config
    );
  }
}

export const judgmentResource = new JudgmentResource("judgment");

class RecommendedNodesResource extends Resource {
  getRecommendedNodes(nodeID, model = "tf_idf_sample_negs_no_training") {
    return axios
      .get(`${this.baseUrl}?target=${nodeID}&model=${model}`, this.config)
      .then(response => {
        return response.data;
      });
  }
}

export const recommendedNodesResource = new RecommendedNodesResource(
  "recommend"
);

class ModelResource extends Resource {
  getModels() {
    return axios.get(`${this.baseUrl}`, this.config).then(response => {
      return response.data;
    });
  }
}
export const modelResource = new ModelResource("model");

class UserResource extends Resource {
  getUser() {
    return axios.get(`${this.baseUrl}`, this.config).then(response => {
      return response.data;
    });
  }
}

export const userResource = new UserResource("user-points");

class CurriculumDocReviewResource extends Resource {
  getRandomDocTopicForReview() {
    return axios.get(`${this.baseUrl}`, this.config).then(response => {
      return response.data;
    });
  }

  submitReview(section_id, section_text, final) {
    let finalize = false;
    // final can be undefined, so make sure we have an explicit true / false in the JSON.
    if (final) {
      finalize = true;
    }
    return axios.post(
      this.baseUrl,
      {
        section_id: section_id,
        section_text: section_text,
        finalize: finalize
      },
      this.config
    );
  }
}

export const curriculumDocReviewResource = new CurriculumDocReviewResource(
  "section-review"
);
