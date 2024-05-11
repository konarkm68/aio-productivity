const timerDisplays = document.querySelectorAll('.timer-display');
const startButtons = document.querySelectorAll('.start-button');
const stopButtons = document.querySelectorAll('.pause-button');
const audioElements = document.querySelectorAll('audio');

let timerIntervals = [];
let currentTab = document.querySelector('.tab-pane.active'); // Get the active tab initially

// Function to update timer display (reusable for all timers)
function updateTimerDisplay(timerDisplayElement, remainingTime) {
  const minutes = Math.floor(remainingTime / 60);
  const seconds = remainingTime % 60;
  timerDisplayElement.textContent = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
}

// Function to handle timer logic (reusable for all timers)
function handleTimer(timerDisplayElement, startButton, pauseButton, audioElement, initialTime) {
  let remainingTime = initialTime; // Set initial remaining time
  let timerInterval = null;

  startButton.addEventListener('click', () => {
    if (timerInterval === null) {
      timerInterval = setInterval(() => {
        remainingTime--;
        updateTimerDisplay(timerDisplayElement, remainingTime);

        if (remainingTime === 0) {
          clearInterval(timerInterval);
          audioElement.play(); // Play the bell sound
          pauseButton.disabled = true;
          startButton.disabled = false;

          // Handle switching to next break after Pomodoro cycle (optional)
          if (currentTab.id === 'pomodoro') {
            const nextTab = currentTab.nextElementSibling;
            if (nextTab) {
              nextTab.querySelector('.start-button').disabled = false; // Enable start button for next break
            }
          }
        }
      }, 1000); // Update timer every second
      pauseButton.disabled = false;
      startButton.disabled = true;
    }
  });

  pauseButton.addEventListener('click', () => {
    if (timerInterval !== null) {
      clearInterval(timerInterval);
      timerInterval = null;
      pauseButton.disabled = true;
      startButton.disabled = false;
    }
  });
}

// Loop through each timer container (tab pane) and set up individual timers
timerDisplays.forEach((timerDisplayElement, index) => {
  const startButton = startButtons[index];
  const stopButton = stopButtons[index];
  const audioElement = audioElements[index];

  let initialTime; // Set initial time based on tab pane (use switch or if/else)

  switch (currentTab.id) {
    case 'pomodoro':
      initialTime = 25 * 60; // Pomodoro (25 minutes)
      break;
    case 'short-break':
      initialTime = 5 * 60; // Short Break (5 minutes)
      break;
    case 'long-break':
      initialTime = 15 * 60; // Long Break (15 minutes)
      startButton.disabled = true; // Initially disable long break start button
      break;
  }

  handleTimer(timerDisplayElement, startButton, stopButton, audioElement, initialTime);
  timerIntervals.push(timerInterval); // Keep track of each timer interval
});
