Vue.component("Page", {
  template: `
<div style="margin:20px;">
  <img src="/app/static/images/baseball.png" style="float:left"/>
  <slot/>
</div>`
});
