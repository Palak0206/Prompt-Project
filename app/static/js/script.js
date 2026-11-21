
// ==============================
// 1. Get HTML Elements
// ==============================

const studyForm = document.getElementById("study-form");
const studentQuery = document.getElementById("student-query");
const generateBtn = document.getElementById("generate-btn");

const loadingState = document.getElementById("loading-state");
const errorMessage = document.getElementById("error-message");
const clarificationSection = document.getElementById("clarification-section");
const timetableSection = document.getElementById("timetable-section");


// ==============================
// 2. Enable Button Only When Input Exists
// ==============================

function updateButtonState() {
    generateBtn.disabled = studentQuery.value.trim().length === 0;
}

studentQuery.addEventListener("input", updateButtonState);

updateButtonState();


// ==============================
// 3. Example Prompt Selection
// ==============================

const exampleCards = document.querySelectorAll(".example-card");

const exampleQueries = [
    "I have Mathematics on December 5 and DBMS on December 8. I can study 4 hours daily. Mathematics is difficult for me and I have completed 40% of my preparation. DBMS is medium difficulty and I have completed 60%.",

    "I have three exams coming up. I can study only 2 hours per day because of my college classes. Please help me organise my preparation.",

    "I struggle with Mathematics and Operating Systems. My exams are approaching, and I want to spend more time on these subjects while keeping up with my other subjects."
];

exampleCards.forEach((card, index) => {

    card.style.cursor = "pointer";

    card.addEventListener("click", () => {

        studentQuery.value = exampleQueries[index];

        updateButtonState();

        studentQuery.focus();

    });

});


// ==============================
// 4. Form Submission
// ==============================

studyForm.addEventListener("submit", (event) => {

    event.preventDefault();

    const query = studentQuery.value.trim();

    if (!query) {
        return;
    }

    // Hide previous messages and results
    errorMessage.classList.add("hidden");
    timetableSection.classList.add("hidden");
    clarificationSection.classList.add("hidden");

    // Show loading state
    loadingState.classList.remove("hidden");

    generateBtn.disabled = true;
    generateBtn.textContent = "Preparing...";

    // Temporary message until backend integration
    setTimeout(() => {

        loadingState.classList.add("hidden");

        clarificationSection.innerHTML = `
            <div class="example-card">
                <h3>Your request is ready!</h3>
                <p>
                    The frontend is working. In the next step,
                    we'll connect this input to Groq so the AI
                    can extract your study details, ask for
                    missing information, and generate your timetable.
                </p>
            </div>
        `;

        clarificationSection.classList.remove("hidden");

        generateBtn.disabled = false;
        generateBtn.innerHTML = 'Generate my plan <span>→</span>';

    }, 700);

});
