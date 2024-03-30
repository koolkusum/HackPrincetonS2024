// Text for typing animation
const textToType = [
  "Innovative engineers who push the boundaries of technology and design.",
  "Groundbreaking scientists whose research drives progress and discovery.",
  "Inspiring leaders who break through barriers and pave the way for future generations.",
  "Creative problem solvers who tackle complex challenges with ingenuity and determination.",
  "Passionate educators who ignite curiosity and foster a love for learning in STEM fields.",
  "Dedicated researchers who explore the unknown and uncover solutions to global problems.",
  "Visionary entrepreneurs who turn ideas into reality and drive economic growth.",
  "Collaborative team players who thrive in interdisciplinary environments and drive innovation forward.",
  "Adaptive thinkers who embrace change and adapt to new technologies and methodologies.",
  "Trailblazing pioneers who shatter stereotypes and redefine what it means to be a woman in STEM.",
  "Empathetic engineers who design solutions with a focus on inclusivity and accessibility.",
  "Fearless explorers who venture into uncharted territories and expand the boundaries of human knowledge.",
];


// Function to simulate typing effect
let index = 0;
function typeText() {
  let currentText = "";
  let letterIndex = 0;

  const typingInterval = setInterval(() => {
    if (letterIndex < textToType[index].length) {
      currentText += textToType[index].charAt(letterIndex);
      // Add blinking cursor
      document.getElementById("typing-text").innerText = currentText + "|";
      letterIndex++;
    } else {
      clearInterval(typingInterval); // Stop the typing
      setTimeout(eraseText, 1500);
    }
  }, 100);

  function eraseText() {
    const eraseInterval = setInterval(() => {
      if (currentText.length > 0) {
        currentText = currentText.slice(0, -1);
        document.getElementById("typing-text").innerText = currentText + "|";
      } else {
        clearInterval(eraseInterval);
        document.getElementById("typing-text").innerText = ""; // Clear the text
        index = (index + 1) % textToType.length; // Move to the next string
        letterIndex = 0; // Reset letterIndex for the next word
        currentText = ""; // Reset currentText for the next word
        setTimeout(typeText, 500);
      }
    }, 50);
  }
}

// Initiate typing animation
window.onload = typeText;
