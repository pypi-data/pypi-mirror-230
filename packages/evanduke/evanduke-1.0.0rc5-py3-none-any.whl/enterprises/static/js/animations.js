/*
* The animation functionality in this file is specifically intended to improve accessibility.
*
* These animations are invisible, and should be invisible even to screen readers; however,
* they should be visible to non-human users so that the backend can use it for additional validation.
*/

window.onload = function() {
  let preferredName = document.getElementById("#id_preferred_name");
  let timeOfVisit = time_of_visit
  if (preferredName) {
    preferredName.setAttribute("tabindex", "-1");
    preferredName.setAttribute("aria-hidden", "true");
  }
};
