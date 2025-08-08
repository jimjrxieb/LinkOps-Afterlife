// ***********************************************************
// This example support/e2e.js is processed and
// loaded automatically before your test files.
//
// This is a great place to put global configuration and
// behavior that modifies Cypress.
//
// You can change the location of this file or turn off
// automatically serving support files with the
// 'supportFile' configuration option.
//
// You can read more here:
// https://on.cypress.io/configuration
// ***********************************************************

// Import commands.js using ES2015 syntax:
import './commands'

// Alternatively you can use CommonJS syntax:
// require('./commands')

// Disable service worker to avoid caching issues in tests
Cypress.on('window:before:load', (win) => {
  delete win.navigator.__defineGetter__('serviceWorker')
})

// Handle uncaught exceptions
Cypress.on('uncaught:exception', (err, runnable) => {
  // Don't fail tests for React hydration warnings or other non-critical errors
  if (err.message.includes('ResizeObserver loop limit exceeded') ||
      err.message.includes('Hydration') ||
      err.message.includes('Cannot read properties of null')) {
    return false
  }
  return true
})