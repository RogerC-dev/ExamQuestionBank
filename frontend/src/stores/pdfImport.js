import { defineStore } from 'pinia'

export const usePdfImportStore = defineStore('pdfImport', {
  state: () => ({
    payload: null
  }),

  actions: {
    setPayload(payload) {
      this.payload = payload
    },

    consumePayload() {
      const data = this.payload
      this.payload = null
      return data
    },

    clearPayload() {
      this.payload = null
    }
  }
})









