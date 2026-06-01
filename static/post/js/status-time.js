(function () {
  function formatTime(date) {
    return `${String(date.getHours()).padStart(2, "0")}:${String(date.getMinutes()).padStart(2, "0")}`;
  }

  function updateStatusTime() {
    const timeText = formatTime(new Date());
    document
      .querySelectorAll(".status-bar > span:first-child, .status-bar > strong:first-child, .onboarding-status > strong:first-child")
      .forEach((element) => {
        element.textContent = timeText;
      });
  }

  updateStatusTime();
  window.setInterval(updateStatusTime, 30000);
})();
