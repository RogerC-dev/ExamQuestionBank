/**
 * @typedef {Object} QuestionOption
 * @property {number} id - Unique identifier for the option
 * @property {string} content - The option text content
 * @property {boolean} isCorrect - Whether this option is the correct answer
 */

/**
 * @typedef {Object} ExamQuestion
 * @property {string} id - Unique identifier for the question
 * @property {number} order - Question order in the exam
 * @property {string} content - The question text content
 * @property {QuestionOption[]} options - Array of answer options
 * @property {string} [subject] - Optional subject classification
 * @property {string} [category] - Optional category classification
 * @property {number} [points] - Optional point value for the question
 */

/**
 * @typedef {Object} ExamSettings
 * @property {boolean} allowReview - Whether students can review answers
 * @property {boolean} showResults - Whether to show results after completion
 * @property {boolean} randomizeQuestions - Whether to randomize question order
 * @property {boolean} randomizeOptions - Whether to randomize option order
 */

/**
 * @typedef {Object} Exam
 * @property {string} id - Unique identifier for the exam
 * @property {string} name - Exam title/name
 * @property {string} [description] - Optional exam description
 * @property {number} [timeLimit] - Optional time limit in minutes
 * @property {ExamQuestion[]} questions - Array of exam questions
 * @property {ExamSettings} settings - Exam configuration settings
 */

/**
 * @typedef {Object} QuestionResult
 * @property {string} questionId - ID of the question
 * @property {string} question - The question text
 * @property {string|null} userAnswer - User's selected answer text
 * @property {string} correctAnswer - The correct answer text
 * @property {boolean} isCorrect - Whether the user answered correctly
 * @property {number} [timeSpent] - Optional time spent on question in seconds
 */

/**
 * @typedef {Object} ExamResults
 * @property {string} examId - ID of the completed exam
 * @property {number} score - Number of correct answers
 * @property {number} correctCount - Number of correct answers (same as score)
 * @property {number} totalCount - Total number of questions
 * @property {number} percentage - Percentage score (0-100)
 * @property {number} duration - Time taken to complete exam in seconds
 * @property {QuestionResult[]} details - Detailed results for each question
 * @property {string[]} wrongQuestionIds - IDs of incorrectly answered questions
 */

/**
 * @typedef {Object} ExamState
 * @property {Exam|null} exam - Current exam data
 * @property {number} currentQuestionIndex - Index of currently displayed question
 * @property {Record<number, number>} userAnswers - Map of question index to selected option ID
 * @property {number} timeLeft - Remaining time in seconds
 * @property {boolean} isActive - Whether exam is currently active
 * @property {boolean} isLoading - Whether exam data is loading
 * @property {string|null} error - Current error message if any
 * @property {ExamResults|null} results - Exam results after completion
 */

/**
 * @typedef {Object} TimerProps
 * @property {number} timeLimit - Time limit in seconds
 * @property {function(): void} onTimeExpired - Callback when timer expires
 */

/**
 * @typedef {Object} NavigatorProps
 * @property {ExamQuestion[]} questions - Array of exam questions
 * @property {number} currentIndex - Currently selected question index
 * @property {Set<number>} answeredQuestions - Set of answered question indices
 */

/**
 * @typedef {Object} ErrorState
 * @property {'network'|'data'|'state'|'user'} type - Type of error
 * @property {string} message - Error message to display
 * @property {boolean} recoverable - Whether error can be recovered from
 * @property {function(): void} [retryAction] - Optional retry function
 */

export {}