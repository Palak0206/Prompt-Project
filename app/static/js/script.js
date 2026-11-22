
// ============================================
// 1. GET HTML ELEMENTS
// ============================================

const studyForm = document.getElementById("study-form");
const studentQuery = document.getElementById("student-query");
const generateBtn = document.getElementById("generate-btn");

const loadingState = document.getElementById("loading-state");
const errorMessage = document.getElementById("error-message");
const clarificationSection = document.getElementById("clarification-section");
const timetableSection = document.getElementById("timetable-section");


// ============================================
// 2. BUTTON STATE
// ============================================

function updateButtonState() {
    generateBtn.disabled = studentQuery.value.trim().length === 0;
}

studentQuery.addEventListener("input", updateButtonState);
updateButtonState();


// ============================================
// 3. EXAMPLE PROMPTS
// ============================================

const exampleCards = document.querySelectorAll(".example-card");

const exampleQueries = [
    "I have Mathematics on December 5 and DBMS on December 8. I can study 4 hours daily. Mathematics is difficult for me and I have completed 40% of my preparation. DBMS is medium difficulty and I have completed 60%.",

    "I have three exams coming up. I can study only 2 hours per day because of my college classes. Please help me organise my preparation.",

    "My DSA exam is on December 5. I struggle with Mathematics and Operating Systems. My exams are approaching, and I want to spend more time on difficult subjects."
];

exampleCards.forEach((card, index) => {
    card.style.cursor = "pointer";

    card.addEventListener("click", () => {
        if (exampleQueries[index]) {
            studentQuery.value = exampleQueries[index];
            updateButtonState();
            studentQuery.focus();
        }
    });
});


// ============================================
// 4. HELPER FUNCTIONS
// ============================================

function showError(message) {
    errorMessage.textContent = message;
    errorMessage.classList.remove("hidden");
}

function hidePreviousResults() {
    errorMessage.classList.add("hidden");
    clarificationSection.classList.add("hidden");
    timetableSection.classList.add("hidden");
}

function escapeHTML(value) {
    return String(value ?? "").replace(/[&<>"']/g, char => ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#039;"
    })[char]);
}


// ============================================
// 5. SAFELY READ API RESPONSES
// ============================================

async function readApiResponse(response, endpointName) {

    const rawResponse = await response.text();

    let result;

    try {
        result = JSON.parse(rawResponse);

    } catch (error) {

        console.error(
            `${endpointName} returned a non-JSON response:`,
            rawResponse
        );

        const preview = rawResponse
            .replace(/<[^>]*>/g, " ")
            .replace(/\s+/g, " ")
            .trim()
            .slice(0, 250);

        throw new Error(
            `${endpointName} failed (HTTP ${response.status}). ` +
            `The server returned HTML instead of JSON. ` +
            `Check the Flask terminal. Response: ${preview || "Empty response"}`
        );
    }

    if (!response.ok) {

        const details = result.details
            ? typeof result.details === "string"
                ? result.details
                : JSON.stringify(result.details, null, 2)
            : "";

        throw new Error(
            `${result.error || `${endpointName} failed.`}` +
            (details ? `\n${details}` : "")
        );
    }

    return result;
}


// ============================================
// 6. SHOW MISSING INFORMATION
// ============================================

function showMissingInformation(missingFields) {

    clarificationSection.innerHTML = `
        <div class="example-card">
            <h3>A few details are missing</h3>

            <p>Please provide the following information:</p>

            <ul>
                ${missingFields.map(field =>
                    `<li>${escapeHTML(field)}</li>`
                ).join("")}
            </ul>

            <p>Update your description and click Generate again.</p>
        </div>
    `;

    clarificationSection.classList.remove("hidden");
}


// ============================================
// 7. EXTRACT STUDENT INFORMATION
// ============================================

async function extractStudentInformation(query) {

    const response = await fetch("/api/extract-student-details", {
        method: "POST",

        headers: {
            "Content-Type": "application/json"
        },

        body: JSON.stringify({
            query: query
        })
    });

    const result = await readApiResponse(
        response,
        "Student information extraction"
    );

    if (!result.extracted_data) {
        throw new Error(
            "The extraction API did not return student details."
        );
    }

    return result.extracted_data;
}


// ============================================
// 8. CHECK REQUIRED INFORMATION
// ============================================

function prepareStudentData(extractedData) {

    const missingFields = [];

    if (!extractedData.start_date) {
        missingFields.push("Study plan start date");
    }

    if (
        extractedData.max_daily_hours === null ||
        extractedData.max_daily_hours === undefined
    ) {
        missingFields.push("Maximum study hours per day");
    }

    if (
        !extractedData.subjects ||
        extractedData.subjects.length === 0
    ) {
        missingFields.push("At least one subject");
    }

    extractedData.subjects?.forEach((subject, index) => {

        const subjectName = subject.name || `Subject ${index + 1}`;

        if (!subject.exam_date) {
            missingFields.push(`Exam date for ${subjectName}`);
        }

        if (!subject.difficulty) {
            missingFields.push(`Difficulty level for ${subjectName}`);
        }

        if (
            subject.preparation_percentage === null ||
            subject.preparation_percentage === undefined
        ) {
            missingFields.push(
                `Preparation percentage for ${subjectName}`
            );
        }
    });

    if (missingFields.length > 0) {

        return {
            valid: false,
            missingFields: missingFields
        };
    }

    const studentData = {
        start_date: extractedData.start_date,

        max_daily_hours: extractedData.max_daily_hours,

        subjects: extractedData.subjects,

        preferences: {
            max_session_duration_minutes:
                extractedData.max_session_duration_minutes ?? 90
        }
    };

    return {
        valid: true,
        studentData: studentData
    };
}


// ============================================
// 9. GENERATE TIMETABLE
// ============================================

async function requestTimetable(studentData) {

    const response = await fetch("/api/generate-timetable", {
        method: "POST",

        headers: {
            "Content-Type": "application/json"
        },

        body: JSON.stringify(studentData)
    });

    const result = await readApiResponse(
        response,
        "Timetable generation"
    );

    if (!result.timetable) {
        throw new Error(
            "The timetable API did not return a timetable."
        );
    }

    return result.timetable;
}


// ============================================
// 10. DISPLAY TIMETABLE
// ============================================

function displayTimetable(timetable) {

    const days = timetable.days || [];

    if (days.length === 0) {
        throw new Error(
            "The generated timetable contains no days."
        );
    }

    const timetableHTML = days.map(day => {

        const dateObject = new Date(`${day.date}T00:00:00`);

        const formattedDate = dateObject.toLocaleDateString("en-IN", {
            weekday: "long",
            day: "numeric",
            month: "long",
            year: "numeric"
        });

        const items = day.items || [];

        const itemsHTML = items.map(item => {

            if (item.kind === "break") {

                return `
                    <div class="schedule-item break-item">
                        <div>
                            <strong>Break</strong>
                            <p>Take a short rest</p>
                        </div>

                        <span>${item.duration_minutes} min</span>
                    </div>
                `;
            }

            return `
                <div class="schedule-item study-item">

                    <div>
                        <span class="session-type">
                            ${escapeHTML(
                                item.session_type.replace("_", " ")
                            )}
                        </span>

                        <h4>${escapeHTML(item.subject)}</h4>

                        <p>${escapeHTML(item.task)}</p>

                        ${
                            item.topics?.length
                                ? `
                                    <p class="topic-list">
                                        Topics:
                                        ${item.topics.map(escapeHTML).join(", ")}
                                    </p>
                                `
                                : ""
                        }
                    </div>

                    <span class="duration">
                        ${item.duration_minutes} min
                    </span>

                </div>
            `;
        }).join("");

        return `
            <div class="day-card">

                <div class="day-header">
                    <h3>${escapeHTML(formattedDate)}</h3>
                    <span>${items.length} activities</span>
                </div>

                ${
                    items.length
                        ? itemsHTML
                        : `<p class="empty-day">No study sessions scheduled.</p>`
                }

            </div>
        `;

    }).join("");

    timetableSection.innerHTML = `

        <div class="timetable-heading">
            <h2>Your Study Timetable</h2>
            <p>Your AI-generated, validated study plan is ready.</p>
        </div>

        <div class="timetable-days">
            ${timetableHTML}
        </div>

    `;

    timetableSection.classList.remove("hidden");

    timetableSection.scrollIntoView({
        behavior: "smooth",
        block: "start"
    });
}


// ============================================
// 11. COMPLETE GENERATION PIPELINE
// ============================================

studyForm.addEventListener("submit", async (event) => {

    event.preventDefault();

    const query = studentQuery.value.trim();

    if (!query) {
        return;
    }

    hidePreviousResults();

    loadingState.classList.remove("hidden");

    generateBtn.disabled = true;
    generateBtn.textContent = "Extracting details...";

    try {

        // STEP 1: Extract student details using Groq

        const extractedData =
            await extractStudentInformation(query);


        // STEP 2: Check required information

        const prepared = prepareStudentData(extractedData);

        if (!prepared.valid) {

            showMissingInformation(prepared.missingFields);

            return;
        }


        // STEP 3: Send structured data to timetable API

        generateBtn.textContent = "Generating timetable...";

        const timetable =
            await requestTimetable(prepared.studentData);


        // STEP 4: Display generated timetable

        displayTimetable(timetable);

    } catch (error) {

        console.error("Generation error:", error);

        showError(
            error.message || "Something went wrong. Please try again."
        );

    } finally {

        loadingState.classList.add("hidden");

        generateBtn.disabled =
            studentQuery.value.trim().length === 0;

        generateBtn.innerHTML =
            'Generate my plan <span>→</span>';

    }

});
