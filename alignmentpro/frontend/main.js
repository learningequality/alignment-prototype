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
import App from "./App.vue";
import router from "./router";
import VueClipboard from "vue-clipboard2";
import Vuetify from "vuetify";
import "vuetify/dist/vuetify.min.css";
import VueConfetti from "vue-confetti";

Vue.config.productionTip = false;
Vue.use(VueClipboard);
Vue.use(Vuetify, {
  theme: {
    background: "#F0F6FB",
    primary: "#18BAFF",
    green: "#22D64C",
    red: "#FD867A",
    grey: "#698DA0"
  }
});
Vue.use(VueConfetti);

new Vue({
  router,
  render: h => h(App)
}).$mount("#app");
