describe('File Upload and Processing', () => {
  beforeEach(() => {
    cy.checkServerStatus()
    
    // Create and login test user
    const testUser = {
      username: `uploadtest_${Date.now()}`,
      password: 'testpass123'
    }
    cy.register(testUser.username, testUser.password)
    cy.login(testUser.username, testUser.password)
    cy.visit('/')
    
    // Mock API responses
    cy.mockApiResponses()
    
    // Create test files
    cy.writeFile('cypress/fixtures/test-photo.jpg', 'fake-photo-data')
    cy.writeFile('cypress/fixtures/test-audio.wav', 'fake-audio-data')
    cy.writeFile('cypress/fixtures/test-text.txt', 'This is test personality text with emotional content.')
  })

  afterEach(() => {
    cy.cleanup()
  })

  describe('Upload Form Display', () => {
    it('should show upload form as first step', () => {
      cy.get('[data-cy="upload-form"]').should('be.visible')
      cy.get('[data-cy="progress-stepper"]').within(() => {
        cy.get('.Mui-active').should('contain', 'Upload Files')
      })
    })

    it('should display all required file inputs', () => {
      cy.get('[data-cy="photo-upload"]').should('exist')
      cy.get('[data-cy="audio-upload"]').should('exist') 
      cy.get('[data-cy="text-upload"]').should('exist')
      
      // Upload button should be disabled initially
      cy.get('[data-cy="upload-submit"]').should('be.disabled')
    })

    it('should show file type requirements and limits', () => {
      cy.get('[data-cy="upload-form"]').within(() => {
        cy.contains('JPG or PNG').should('be.visible')
        cy.contains('WAV or MP3').should('be.visible')
        cy.contains('TXT').should('be.visible')
        cy.contains('5MB').should('be.visible')
        cy.contains('30 seconds').should('be.visible')
      })
    })
  })

  describe('File Selection and Validation', () => {
    it('should enable upload button when all files are selected', () => {
      // Initially disabled
      cy.get('[data-cy="upload-submit"]').should('be.disabled')
      
      // Select photo
      cy.get('[data-cy="photo-upload"]').selectFile('cypress/fixtures/test-photo.jpg', { force: true })
      cy.get('[data-cy="upload-submit"]').should('be.disabled')
      
      // Select audio
      cy.get('[data-cy="audio-upload"]').selectFile('cypress/fixtures/test-audio.wav', { force: true })
      cy.get('[data-cy="upload-submit"]').should('be.disabled')
      
      // Select text - now should be enabled
      cy.get('[data-cy="text-upload"]').selectFile('cypress/fixtures/test-text.txt', { force: true })
      cy.get('[data-cy="upload-submit"]').should('be.enabled')
    })

    it('should show selected file names', () => {
      cy.uploadFiles(
        'cypress/fixtures/test-photo.jpg',
        'cypress/fixtures/test-audio.wav',
        'cypress/fixtures/test-text.txt'
      )
      
      // Should display selected file names
      cy.get('[data-cy="selected-photo"]').should('contain', 'test-photo.jpg')
      cy.get('[data-cy="selected-audio"]').should('contain', 'test-audio.wav')
      cy.get('[data-cy="selected-text"]').should('contain', 'test-text.txt')
    })

    it('should validate file types client-side', () => {
      // Create invalid file types
      cy.writeFile('cypress/fixtures/invalid.gif', 'fake-gif-data')
      cy.writeFile('cypress/fixtures/invalid.mp4', 'fake-video-data')
      cy.writeFile('cypress/fixtures/invalid.pdf', 'fake-pdf-data')
      
      // Try to upload invalid photo type
      cy.get('[data-cy="photo-upload"]').selectFile('cypress/fixtures/invalid.gif', { force: true })
      cy.get('[data-cy="photo-error"]').should('contain', 'Invalid file type')
      
      // Try to upload invalid audio type  
      cy.get('[data-cy="audio-upload"]').selectFile('cypress/fixtures/invalid.mp4', { force: true })
      cy.get('[data-cy="audio-error"]').should('contain', 'Invalid file type')
      
      // Try to upload invalid text type
      cy.get('[data-cy="text-upload"]').selectFile('cypress/fixtures/invalid.pdf', { force: true })
      cy.get('[data-cy="text-error"]').should('contain', 'Invalid file type')
    })
  })

  describe('File Upload Process', () => {
    it('should upload files successfully and show consent dialog', () => {
      cy.uploadFiles(
        'cypress/fixtures/test-photo.jpg',
        'cypress/fixtures/test-audio.wav',
        'cypress/fixtures/test-text.txt'
      )
      
      // Should show loading state
      cy.get('[data-cy="upload-loading"]').should('be.visible')
      
      // Wait for upload completion
      cy.wait('@uploadFiles')
      
      // Should show consent dialog
      cy.get('[data-cy="consent-dialog"]').should('be.visible')
    })

    it('should show upload progress and success message', () => {
      cy.uploadFiles(
        'cypress/fixtures/test-photo.jpg',
        'cypress/fixtures/test-audio.wav',
        'cypress/fixtures/test-text.txt'
      )
      
      // Should show progress
      cy.get('[data-cy="upload-progress"]').should('be.visible')
      
      cy.wait('@uploadFiles')
      
      // Should show success message
      cy.get('[data-cy="success-alert"]').should('contain', 'Files uploaded successfully')
    })

    it('should handle upload failure gracefully', () => {
      // Mock upload failure
      cy.intercept('POST', '**/upload', {
        statusCode: 400,
        body: { detail: 'File validation failed: Invalid file type' }
      }).as('uploadFail')
      
      cy.uploadFiles(
        'cypress/fixtures/test-photo.jpg',
        'cypress/fixtures/test-audio.wav',
        'cypress/fixtures/test-text.txt'
      )
      
      cy.wait('@uploadFail')
      
      // Should show error message
      cy.get('[data-cy="error-alert"]').should('contain', 'File validation failed')
      
      // Should remain on upload step  
      cy.get('[data-cy="upload-form"]').should('be.visible')
    })

    it('should handle server errors during upload', () => {
      cy.intercept('POST', '**/upload', {
        statusCode: 500,
        body: { detail: 'Internal server error' }
      }).as('serverError')
      
      cy.uploadFiles(
        'cypress/fixtures/test-photo.jpg',
        'cypress/fixtures/test-audio.wav', 
        'cypress/fixtures/test-text.txt'
      )
      
      cy.wait('@serverError')
      
      // Should show generic error message
      cy.get('[data-cy="error-alert"]').should('contain', 'Upload failed')
    })
  })

  describe('Processing Status', () => {
    beforeEach(() => {
      // Complete upload and consent
      cy.uploadFiles(
        'cypress/fixtures/test-photo.jpg',
        'cypress/fixtures/test-audio.wav',
        'cypress/fixtures/test-text.txt'
      )
      cy.wait('@uploadFiles')
      cy.submitConsent()
    })

    it('should show processing status after consent', () => {
      cy.get('[data-cy="processing-status"]').should('be.visible')
      cy.get('[data-cy="progress-stepper"]').within(() => {
        cy.get('.Mui-active').should('contain', 'Process Data')
      })
    })

    it('should display all processing steps', () => {
      cy.get('[data-cy="processing-status"]').within(() => {
        cy.get('[data-cy="photo-processing"]').should('be.visible')
        cy.get('[data-cy="voice-cloning"]').should('be.visible')
        cy.get('[data-cy="text-processing"]').should('be.visible')
        cy.get('[data-cy="model-training"]').should('be.visible')
      })
    })

    it('should show processing progress indicators', () => {
      cy.get('[data-cy="processing-status"]').within(() => {
        // Should show progress indicators
        cy.get('.MuiLinearProgress-root').should('exist')
        cy.get('[data-cy="processing-step-1"]').should('contain', 'Processing')
      })
    })

    it('should complete processing and enable interaction', () => {
      // Mock all processing steps completion
      cy.wait('@preprocessPhoto')
      cy.wait('@cloneVoice')
      
      // Should show completed status
      cy.get('[data-cy="processing-complete"]').should('contain', 'Processing complete')
      
      // Should enable interaction step
      cy.get('[data-cy="progress-stepper"]').within(() => {
        cy.contains('Interact').should('not.have.class', 'Mui-disabled')
      })
    })

    it('should handle processing errors', () => {
      // Mock processing failure
      cy.intercept('GET', '**/preprocess_photo/*', {
        statusCode: 500,
        body: { detail: 'Photo processing failed' }
      }).as('processingError')
      
      cy.wait('@processingError')
      
      // Should show error message
      cy.get('[data-cy="error-alert"]').should('contain', 'processing failed')
    })
  })

  describe('Session Management', () => {
    it('should create and track session ID', () => {
      cy.uploadFiles(
        'cypress/fixtures/test-photo.jpg',
        'cypress/fixtures/test-audio.wav',
        'cypress/fixtures/test-text.txt'
      )
      
      cy.wait('@uploadFiles')
      
      // Should show session ID in header
      cy.get('[data-cy="session-chip"]').should('contain', 'Session:')
      
      // Should store session ID in localStorage
      cy.window().then((win) => {
        expect(win.localStorage.getItem('currentSessionId')).to.exist
      })
    })

    it('should maintain session across page refresh', () => {
      cy.uploadFiles(
        'cypress/fixtures/test-photo.jpg',
        'cypress/fixtures/test-audio.wav',
        'cypress/fixtures/test-text.txt'
      )
      
      cy.wait('@uploadFiles')
      
      // Get session ID
      cy.get('[data-cy="session-chip"]').invoke('text').as('originalSession')
      
      // Refresh page
      cy.reload()
      
      // Should maintain same session
      cy.get('@originalSession').then((originalText) => {
        cy.get('[data-cy="session-chip"]').should('contain', originalText)
      })
    })
  })
})