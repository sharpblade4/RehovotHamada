window.addEventListener('load', (event) => {
  document.body.style.display = "block";
});

function onTabSelected(tabIndex, event) {
  const selectedTab = document.getElementById("tab-selected");
  if (window.screen.availWidth > 600) {
    selectedTab.style.right = tabIndex * 140 + "px";
  } else {
    selectedTab.style.right = tabIndex * 33 + "%";
  }
  removeClass(document.getElementsByClassName("tabs")[0].children, "selected");
  event.classList.add("selected");
  removeClass(document.getElementsByClassName("tab-content"), "selected-tab-content");
  document.getElementById("tab" + tabIndex).classList.add("selected-tab-content");
}

function removeClass(elements, className){
  for (var i = 0; i < elements.length; i++) {
    elements[i].classList.remove(className);
  }
}