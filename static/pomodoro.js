document.addEventListener("DOMContentLoaded", function () {
  var timerDisplays = document.querySelectorAll(".timer-display");
  var startButtons = document.querySelectorAll(".start-button");
  var stopButtons = document.querySelectorAll(".stop-button");
  var resetButtons = document.querySelectorAll(".reset-button");

  let currentTab = document.querySelector(".tab-pane.active");

  const POMODORO_TIME = 25 * 60;
  const SHORT_BREAK = 5 * 60;
  const LONG_BREAK = 15 * 60;

  // Arrays of messages for Pomodoro and break endings
  const pomodoroEndMessages = [
    "Time's up! Take a well-deserved break.",
    "Great work! Time to recharge.",
    "Pomodoro complete! Stretch those muscles.",
    "Nice focus session! How about a breather?",
    "You've earned a pause. What's next on your break agenda?"
  ];

  const breakEndMessages = [
    "Break's over! Ready to dive back in?",
    "Refreshed and recharged? Let's get back to it!",
    "Hope you enjoyed your break. Time to refocus!",
    "Break time's up! What's your next big task?",
    "Alright, let's kick off another productive session!"
  ];

  // Get Users permission on notifications
  if (Notification.permission !== "granted") {
    Notification.requestPermission();
  }

  function updateTimerDisplay(timerDisplayElement, remainingTime) {
    var minutes = Math.floor(remainingTime / 60);
    var seconds = remainingTime % 60;
    timerDisplayElement.textContent = pad(minutes) + ':' + pad(seconds);
  }

  function pad(num) {
    return ("0"+num).slice(-2);
  }

  function sendNotification(title, options) {
    if (Notification.permission === "granted") {
      new Notification(title, options);
    }
  }

  function getRandomMessage(messageArray) {
    return messageArray[Math.floor(Math.random() * messageArray.length)];
  }

  function TimerSetup(timerDisplayElement, startButton, stopButton, resetButton, initialTime) {
    var remainingTime = initialTime;
    var timerInterval = null;

    function resetTimer() {
      clearInterval(timerInterval);
      timerInterval = null;
      remainingTime = initialTime;
      updateTimerDisplay(timerDisplayElement, remainingTime);
      stopButton.disabled = true;
      startButton.disabled = false;
    }

    startButton.onclick = function() {
      if (!timerInterval) {
        timerInterval = setInterval(function() {
          remainingTime--;
          updateTimerDisplay(timerDisplayElement, remainingTime);

          if (remainingTime <= 0) {
            clearInterval(timerInterval);
            stopButton.disabled = true;
            startButton.disabled = false;

            var notificationTitle = "All-in-1 Productivity";
            var notificationBody = currentTab.id === "pomodoro" ?
              getRandomMessage(pomodoroEndMessages) : getRandomMessage(breakEndMessages);
            sendNotification(notificationTitle, {body: notificationBody, icon: "/static/ico.png"});

            // Enable next timer
            var tabs = Array.from(document.querySelectorAll('.tab-pane'));
            var currentTabIndex = tabs.indexOf(currentTab);
            var nextTab = tabs[(currentTabIndex + 1) % tabs.length];
            if (nextTab) {
              nextTab.querySelector(".start-button").disabled = false;
            }
          }
        }, 1000);
        stopButton.disabled = false;
        startButton.disabled = true;
      }
    };

    stopButton.addEventListener("click", function() {
      if (timerInterval) {
        clearInterval(timerInterval);
        timerInterval = null;
        stopButton.disabled = true;
        startButton.disabled = false;
      }
    });

    resetButton.addEventListener("click", resetTimer);

    resetTimer();
  }

  function initializeTimers() {
    for (let i = 0; i < timerDisplays.length; i++) {
      var timerDisplayElement = timerDisplays[i];
      var startButton = startButtons[i];
      var stopButton = stopButtons[i];
      var resetButton = resetButtons[i];

      var initialTime;
      switch (timerDisplayElement.closest(".tab-pane").id) {
        case "pomodoro":
          initialTime = POMODORO_TIME;
          break;
        case "short-break":
          initialTime = SHORT_BREAK;
          break;
        case "long-break":
          initialTime = LONG_BREAK;
          break;
        default:
          console.error("Unknown timer type");
      }

      //initialTime = 2; // FIXME: For testing purposes, once satisfied, remove this line

      TimerSetup(timerDisplayElement, startButton, stopButton, resetButton, initialTime);
    }
  }

  // Switch tabs without breaking everything
  document.querySelectorAll(".nav-link").forEach(function(tabLink) {
    tabLink.addEventListener("click", function(event) {
      currentTab = document.querySelector(tabLink.getAttribute("href"));
    });
  });

  // Initialize timers
  initializeTimers();
});
