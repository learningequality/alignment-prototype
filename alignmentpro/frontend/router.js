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

import Vue from "vue";
import Router from "vue-router";
// Import generated routes
import routes from "vue-auto-routing";
import Home from "./Home.vue";
import CurriculumDocs from './apps/curriculum_docs/index.vue';
import Judgment from "./apps/judgment/evaluation/index.vue";
import Visualization from "./apps/visualization/example/index.vue";
import Login from "./Login.vue";
import Logout from "./Logout.vue";
import session from "./session";


Vue.use(Router);

const homeRoute = {
  path: "/",
  name: "home",
  component: Home
};

const loginRoute = {
  path: "/login",
  name: "login",
  component: Login
};

const logoutRoute = {
  path: "/logout",
  name: "logout",
  component: Logout
};

const judgmentRoute = {
  path: "/judgment",
  name: "judgment",
  component: Judgment
}

const visualizationRoute = {
  path: "/visualization",
  name: "visualization",
  component: Visualization
}

const curriculumDocsRoute = {
  path: "/curriculum_review",
  name: "curriculum_review",
  component: CurriculumDocs
}

const router = new Router({
  routes: [homeRoute, loginRoute, logoutRoute, judgmentRoute, visualizationRoute, curriculumDocsRoute]
});

router.beforeEach((to, from, next) => {
  if (to.name != loginRoute.name) {
    // this route requires auth, check if logged in
    // if not, redirect to login page.
    if (!session.loggedIn) {
      next({
        name: loginRoute.name
      });
    } else {
      next();
    }
  } else {
    next();
  }
});

export default router;
