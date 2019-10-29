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
