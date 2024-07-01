document.addEventListener("DOMContentLoaded", function () {
  const timerDisplays = document.querySelectorAll(".timer-display");
  const startButtons = document.querySelectorAll(".start-button");
  const stopButtons = document.querySelectorAll(".stop-button");
  const resetButtons = document.querySelectorAll(".reset-button");
  const audioElements = document.querySelectorAll("audio");

  let timerIntervals = [];
  let currentTab = document.querySelector(".tab-pane.active");

  function updateTimerDisplay(timerDisplayElement, remainingTime) {
    const minutes = Math.floor(remainingTime / 60);
    const seconds = remainingTime % 60;
    timerDisplayElement.textContent = `${minutes
      .toString()
      .padStart(2, "0")}:${seconds.toString().padStart(2, "0")}`;
  }

  function handleTimer(
    timerDisplayElement,
    startButton,
    stopButton,
    resetButton,
    audioElement,
    initialTime
  ) {
    let remainingTime = initialTime;
    let timerInterval = null;

    function resetTimer() {
      clearInterval(timerInterval);
      timerInterval = null;
      remainingTime = initialTime;
      updateTimerDisplay(timerDisplayElement, remainingTime);
      stopButton.disabled = true;
      startButton.disabled = false;
    }

    startButton.addEventListener("click", () => {
      if (timerInterval === null) {
        timerInterval = setInterval(() => {
          remainingTime--;
          updateTimerDisplay(timerDisplayElement, remainingTime);

          if (remainingTime === 0) {
            clearInterval(timerInterval);
            audioElement.play();
            stopButton.disabled = true;
            startButton.disabled = false;

            if (currentTab.id === "pomodoro") {
              const nextTab = currentTab.nextElementSibling;
              if (nextTab) {
                nextTab.querySelector(".start-button").disabled = false;
              }
            }
          }
        }, 1000);
        stopButton.disabled = false;
        startButton.disabled = true;
      }
    });

    stopButton.addEventListener("click", () => {
      if (timerInterval !== null) {
        clearInterval(timerInterval);
        timerInterval = null;
        stopButton.disabled = true;
        startButton.disabled = false;
      }
    });

    resetButton.addEventListener("click", resetTimer);

    resetTimer(); // Initialize the timer display and state
  }

  function initializeTimers() {
    timerDisplays.forEach((timerDisplayElement, index) => {
      const startButton = startButtons[index];
      const stopButton = stopButtons[index];
      const resetButton = resetButtons[index];
      const audioElement = audioElements[index];

      let initialTime;

      switch (timerDisplayElement.closest(".tab-pane").id) {
        case "pomodoro":
          initialTime = 25 * 60;
          break;
        case "short-break":
          initialTime = 5 * 60;
          break;
        case "long-break":
          initialTime = 15 * 60;
          break;
      }

      handleTimer(
        timerDisplayElement,
        startButton,
        stopButton,
        resetButton,
        audioElement,
        initialTime
      );
    });
  }

  function clearAllIntervals() {
    timerIntervals.forEach((interval) => clearInterval(interval));
    timerIntervals = [];
  }

  document.querySelectorAll(".nav-link").forEach((tabLink) => {
    tabLink.addEventListener("click", (event) => {
      clearAllIntervals();
      currentTab = document.querySelector(tabLink.getAttribute("href"));
      initializeTimers();
    });
  });

  initializeTimers();
});
