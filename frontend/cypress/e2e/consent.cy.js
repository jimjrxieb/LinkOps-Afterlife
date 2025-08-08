describe('Consent Management', () => {
  beforeEach(() => {
    cy.checkServerStatus()
    
    // Create and login test user
    const testUser = {
      username: `consenttest_${Date.now()}`,
      password: 'testpass123'
    }
    cy.register(testUser.username, testUser.password)
    cy.login(testUser.username, testUser.password)
    cy.visit('/')
    
    // Mock successful file upload to trigger consent dialog
    cy.mockApiResponses()
  })

  afterEach(() => {
    cy.cleanup()
  })

  describe('Consent Dialog Display', () => {
    it('should show consent dialog after file upload', () => {
      // Create test files
      cy.writeFile('cypress/fixtures/test-photo.jpg', 'fake-photo-data')
      cy.writeFile('cypress/fixtures/test-audio.wav', 'fake-audio-data') 
      cy.writeFile('cypress/fixtures/test-text.txt', 'This is test personality text')
      
      // Upload files to trigger consent dialog
      cy.uploadFiles(
        'cypress/fixtures/test-photo.jpg',
        'cypress/fixtures/test-audio.wav', 
        'cypress/fixtures/test-text.txt'
      )
      
      // Wait for upload to complete
      cy.wait('@uploadFiles')
      
      // Consent dialog should appear
      cy.get('[data-cy="consent-dialog"]', { timeout: 10000 }).should('be.visible')
      cy.get('[data-cy="consent-title"]').should('contain', 'Consent Agreement Required')
    })

    it('should display all required consent checkboxes', () => {
      // Trigger consent dialog (using fixture data)
      cy.fixture('test-files').then((data) => {
        cy.window().then((win) => {
          // Simulate upload success to show consent
          win.dispatchEvent(new CustomEvent('showConsent', { 
            detail: { sessionId: 'test-session-123' } 
          }))
        })
      })
      
      cy.get('[data-cy="consent-dialog"]').should('be.visible')
      
      // Check all required consents are present
      cy.get('[data-cy="terms-consent"]').should('exist')
      cy.get('[data-cy="data-processing-consent"]').should('exist') 
      cy.get('[data-cy="emotional-impact-consent"]').should('exist')
      
      // Submit button should be disabled initially
      cy.get('[data-cy="consent-submit"]').should('be.disabled')
    })

    it('should show grief counseling resources link', () => {
      cy.get('[data-cy="consent-dialog"]').should('be.visible')
      
      cy.get('a[href*="griefshare.org"]').should('exist')
        .and('have.attr', 'target', '_blank')
    })
  })

  describe('Consent Submission', () => {
    beforeEach(() => {
      // Show consent dialog
      cy.get('[data-cy="consent-dialog"]').should('be.visible')
    })

    it('should enable submit button when all consents are given', () => {
      // Initially disabled
      cy.get('[data-cy="consent-submit"]').should('be.disabled')
      
      // Check first consent
      cy.get('[data-cy="terms-consent"]').check()
      cy.get('[data-cy="consent-submit"]').should('be.disabled')
      
      // Check second consent  
      cy.get('[data-cy="data-processing-consent"]').check()
      cy.get('[data-cy="consent-submit"]').should('be.disabled')
      
      // Check third consent - now should be enabled
      cy.get('[data-cy="emotional-impact-consent"]').check()
      cy.get('[data-cy="consent-submit"]').should('be.enabled')
    })

    it('should submit consent successfully and proceed to processing', () => {
      // Mock consent submission
      cy.intercept('POST', '**/consent/*', {
        statusCode: 200,
        body: { message: 'Consent recorded successfully' }
      }).as('submitConsent')
      
      // Give all consents
      cy.submitConsent()
      
      // Should submit consent
      cy.wait('@submitConsent')
      
      // Dialog should close
      cy.get('[data-cy="consent-dialog"]').should('not.exist')
      
      // Should proceed to processing step
      cy.get('[data-cy="processing-status"]').should('be.visible')
    })

    it('should show error if consent submission fails', () => {
      // Mock consent submission failure
      cy.intercept('POST', '**/consent/*', {
        statusCode: 500,
        body: { detail: 'Failed to store consent' }
      }).as('submitConsentFail')
      
      cy.submitConsent()
      
      cy.wait('@submitConsentFail')
      
      // Should show error message
      cy.get('[data-cy="error-alert"]').should('contain', 'Failed to submit consent')
      
      // Dialog should remain open
      cy.get('[data-cy="consent-dialog"]').should('be.visible')
    })

    it('should allow canceling consent dialog', () => {
      cy.get('[data-cy="consent-cancel"]').click()
      
      // Dialog should close
      cy.get('[data-cy="consent-dialog"]').should('not.exist')
      
      // Should remain on upload step
      cy.get('[data-cy="upload-form"]').should('be.visible')
    })
  })

  describe('Consent Validation', () => {
    it('should require all three consent types', () => {
      // Try with only terms consent
      cy.get('[data-cy="terms-consent"]').check() 
      cy.get('[data-cy="consent-submit"]').should('be.disabled')
      
      // Add data processing consent
      cy.get('[data-cy="data-processing-consent"]').check()
      cy.get('[data-cy="consent-submit"]').should('be.disabled')
      
      // Only enabled when all three are checked
      cy.get('[data-cy="emotional-impact-consent"]').check()
      cy.get('[data-cy="consent-submit"]').should('be.enabled')
    })

    it('should disable submit if any consent is unchecked', () => {
      // Check all consents
      cy.submitConsent()
      cy.get('[data-cy="consent-submit"]').should('be.enabled')
      
      // Uncheck one consent
      cy.get('[data-cy="terms-consent"]').uncheck()
      cy.get('[data-cy="consent-submit"]').should('be.disabled')
    })

    it('should show detailed consent descriptions', () => {
      // Check that consent descriptions are comprehensive
      cy.get('[data-cy="consent-dialog"]').within(() => {
        cy.contains('Terms of Use').should('be.visible')
        cy.contains('AI-generated content').should('be.visible')
        cy.contains('third-party APIs').should('be.visible')
        cy.contains('encrypted').should('be.visible')
        cy.contains('memorial purposes').should('be.visible')
        
        cy.contains('data processing').should('be.visible')
        cy.contains('avatar generation').should('be.visible')
        cy.contains('voice cloning').should('be.visible')
        cy.contains('personality analysis').should('be.visible')
        
        cy.contains('emotional impact').should('be.visible')
        cy.contains('digital simulation').should('be.visible')
        cy.contains('grief counseling').should('be.visible')
        cy.contains('delete all data').should('be.visible')
      })
    })
  })

  describe('Post-Consent Behavior', () => {
    beforeEach(() => {
      // Complete consent process
      cy.submitConsent()
      
      // Mock consent submission success
      cy.intercept('POST', '**/consent/*', {
        statusCode: 200,
        body: { message: 'Consent recorded successfully' }
      }).as('submitConsent')
      
      cy.wait('@submitConsent')
    })

    it('should not show consent dialog again for same session', () => {
      // Refresh page
      cy.reload()
      
      // Should not show consent dialog
      cy.get('[data-cy="consent-dialog"]').should('not.exist')
      
      // Should show processing step
      cy.get('[data-cy="progress-stepper"]').should('be.visible')
    })

    it('should block processing without consent', () => {
      // Mock consent check as false
      cy.intercept('POST', '**/interact/*', {
        statusCode: 403,
        body: { detail: 'Consent required' }
      }).as('interactNoConsent')
      
      // Try to interact without consent
      cy.get('[data-cy="chat-input"]').type('Hello')
      cy.get('[data-cy="send-message"]').click()
      
      cy.wait('@interactNoConsent')
      
      // Should show error
      cy.get('[data-cy="error-alert"]').should('contain', 'Consent required')
    })
  })
})