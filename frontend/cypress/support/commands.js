// ***********************************************
// This example commands.js shows you how to
// create various custom commands and overwrite
// existing commands.
//
// For more comprehensive examples of custom
// commands please read more here:
// https://on.cypress.io/custom-commands
// ***********************************************

// Custom command to register a user
Cypress.Commands.add('register', (username, password, email = '') => {
  cy.request({
    method: 'POST',
    url: `${Cypress.env('apiUrl')}/register`,
    body: {
      username,
      password,
      email
    },
    failOnStatusCode: false
  })
})

// Custom command to login and get token
Cypress.Commands.add('login', (username, password) => {
  cy.request({
    method: 'POST',
    url: `${Cypress.env('apiUrl')}/login`,
    body: {
      username,
      password
    }
  }).then((response) => {
    expect(response.status).to.eq(200)
    const token = response.body.access_token
    
    // Store token in localStorage
    window.localStorage.setItem('token', token)
    
    // Set authorization header for future requests
    Cypress.env('authToken', token)
    
    return cy.wrap(token)
  })
})

// Custom command to login via UI
Cypress.Commands.add('loginUI', (username, password) => {
  cy.get('[data-cy=username-input]').type(username)
  cy.get('[data-cy=password-input]').type(password)
  cy.get('[data-cy=login-button]').click()
})

// Custom command to submit consent form
Cypress.Commands.add('submitConsent', () => {
  cy.get('[data-cy=terms-consent]').check()
  cy.get('[data-cy=data-processing-consent]').check()
  cy.get('[data-cy=emotional-impact-consent]').check()
  cy.get('[data-cy=consent-submit]').click()
})

// Custom command to upload files
Cypress.Commands.add('uploadFiles', (photoFile, audioFile, textFile) => {
  // Upload photo
  cy.get('[data-cy=photo-upload]').selectFile(photoFile, { force: true })
  
  // Upload audio
  cy.get('[data-cy=audio-upload]').selectFile(audioFile, { force: true })
  
  // Upload text
  cy.get('[data-cy=text-upload]').selectFile(textFile, { force: true })
  
  // Submit upload
  cy.get('[data-cy=upload-submit]').click()
})

// Custom command to wait for processing to complete
Cypress.Commands.add('waitForProcessing', () => {
  cy.get('[data-cy=processing-status]', { timeout: 30000 })
    .should('contain', 'completed')
})

// Custom command to interact with avatar
Cypress.Commands.add('interactWithAvatar', (message) => {
  cy.get('[data-cy=chat-input]').type(message)
  cy.get('[data-cy=send-message]').click()
})

// Custom command to check server status
Cypress.Commands.add('checkServerStatus', () => {
  cy.request({
    method: 'GET',
    url: `${Cypress.env('apiUrl')}/ping`,
    timeout: 5000,
    failOnStatusCode: false
  }).then((response) => {
    if (response.status !== 200) {
      throw new Error('Backend server is not running. Please start the backend server before running tests.')
    }
  })
})

// Custom command to clean up test data
Cypress.Commands.add('cleanup', () => {
  const token = Cypress.env('authToken')
  if (token) {
    // Get user sessions and delete them
    cy.window().then((win) => {
      const sessionId = win.localStorage.getItem('currentSessionId')
      if (sessionId) {
        cy.request({
          method: 'DELETE',
          url: `${Cypress.env('apiUrl')}/delete_session/${sessionId}`,
          headers: {
            'Authorization': `Bearer ${token}`
          },
          failOnStatusCode: false
        })
      }
    })
  }
  
  // Clear localStorage
  cy.clearLocalStorage()
})

// Custom command to mock API responses
Cypress.Commands.add('mockApiResponses', () => {
  // Mock successful upload response
  cy.intercept('POST', '**/upload', {
    statusCode: 200,
    body: {
      message: 'Files uploaded and secured successfully',
      session_id: 'test-session-123',
      security: { files_encrypted: true }
    }
  }).as('uploadFiles')
  
  // Mock processing endpoints
  cy.intercept('GET', '**/preprocess_photo/*', {
    statusCode: 200,
    body: { message: 'Photo preprocessed successfully' }
  }).as('preprocessPhoto')
  
  cy.intercept('POST', '**/clone_voice/*', {
    statusCode: 200,
    body: { message: 'Voice cloned successfully' }
  }).as('cloneVoice')
  
  // Mock interaction response
  cy.intercept('POST', '**/interact/*', {
    statusCode: 200,
    body: {
      message: 'Interactive response generated successfully',
      video_path: '/mock/video.mp4',
      user_input: 'Hello'
    }
  }).as('interact')
})