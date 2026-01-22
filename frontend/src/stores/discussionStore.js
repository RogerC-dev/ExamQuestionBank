/**
 * Discussion MVP Store - Pinia Store
 * State management for discussion forum
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import discussionService from '@/services/discussionService'

export const useDiscussionStore = defineStore('discussion', () => {
    // State
    const discussions = ref([])
    const currentDiscussion = ref(null)
    const userCredits = ref(null)
    const loading = ref(false)
    const error = ref(null)
    const pagination = ref({
        offset: 0,
        limit: 20,
        hasMore: true
    })

    // Getters
    const creditBalance = computed(() => userCredits.value?.credits || 0)
    const canClaimDaily = computed(() => userCredits.value?.can_claim_daily || false)
    const reputation = computed(() => userCredits.value?.reputation || 0)

    // Actions
    async function fetchDiscussions(reset = false) {
        if (reset) {
            pagination.value.offset = 0
            discussions.value = []
            pagination.value.hasMore = true
        }

        if (!pagination.value.hasMore) return

        loading.value = true
        error.value = null
        try {
            const data = await discussionService.getDiscussions(
                pagination.value.limit,
                pagination.value.offset
            )

            if (data.length < pagination.value.limit) {
                pagination.value.hasMore = false
            }

            if (reset) {
                discussions.value = data
            } else {
                discussions.value.push(...data)
            }

            pagination.value.offset += data.length
        } catch (err) {
            error.value = err.message
        } finally {
            loading.value = false
        }
    }

    async function fetchDiscussion(id) {
        loading.value = true
        error.value = null
        try {
            const data = await discussionService.getDiscussion(id)
            currentDiscussion.value = data
        } catch (err) {
            error.value = err.message
        } finally {
            loading.value = false
        }
    }

    async function createDiscussion(title, body) {
        loading.value = true
        error.value = null
        try {
            const data = await discussionService.createDiscussion(title, body)
            // Add to list at the beginning
            discussions.value.unshift({
                ...data,
                answer_count: 0,
                view_count: 0
            })
            return data
        } catch (err) {
            error.value = err.message
            throw err
        } finally {
            loading.value = false
        }
    }

    async function submitAnswer(discussionId, body) {
        loading.value = true
        error.value = null
        try {
            const data = await discussionService.submitAnswer(discussionId, body)
            // Refresh discussion to show new answer
            await fetchDiscussion(discussionId)
            return data
        } catch (err) {
            error.value = err.message
            throw err
        } finally {
            loading.value = false
        }
    }

    async function unlockAnswer(answerId) {
        loading.value = true
        error.value = null
        try {
            const result = await discussionService.unlockAnswer(answerId)

            // Update answer in current discussion
            if (currentDiscussion.value?.answers) {
                const answer = currentDiscussion.value.answers.find(a => a.id === answerId)
                if (answer) {
                    answer.body = result.answer_body
                    answer.is_locked = false
                }
            }

            // Update credits
            if (result.remaining_credits !== undefined) {
                if (userCredits.value) {
                    userCredits.value.credits = result.remaining_credits
                }
            }

            return result
        } catch (err) {
            error.value = err.message
            throw err
        } finally {
            loading.value = false
        }
    }

    async function castVote(answerId, voteValue) {
        error.value = null
        try {
            const result = await discussionService.castVote(answerId, voteValue)

            // Update answer vote count in current discussion
            if (currentDiscussion.value?.answers) {
                const answer = currentDiscussion.value.answers.find(a => a.id === answerId)
                if (answer) {
                    answer.vote_count = result.new_vote_count
                    answer.user_vote = voteValue
                }
            }

            return result
        } catch (err) {
            error.value = err.message
            throw err
        }
    }

    async function fetchCredits() {
        try {
            const data = await discussionService.getCredits()
            userCredits.value = data
        } catch (err) {
            console.warn('Failed to fetch credits:', err)
        }
    }

    async function claimDailyCredits() {
        loading.value = true
        error.value = null
        try {
            const result = await discussionService.claimDailyCredits()

            // Update credits
            if (userCredits.value) {
                userCredits.value.credits = result.new_balance
                userCredits.value.can_claim_daily = false
            }

            return result
        } catch (err) {
            error.value = err.message
            throw err
        } finally {
            loading.value = false
        }
    }

    function clearError() {
        error.value = null
    }

    function reset() {
        discussions.value = []
        currentDiscussion.value = null
        userCredits.value = null
        loading.value = false
        error.value = null
        pagination.value = {
            offset: 0,
            limit: 20,
            hasMore: true
        }
    }

    return {
        // State
        discussions,
        currentDiscussion,
        userCredits,
        loading,
        error,
        pagination,

        // Getters
        creditBalance,
        canClaimDaily,
        reputation,

        // Actions
        fetchDiscussions,
        fetchDiscussion,
        createDiscussion,
        submitAnswer,
        unlockAnswer,
        castVote,
        fetchCredits,
        claimDailyCredits,
        clearError,
        reset
    }
})
