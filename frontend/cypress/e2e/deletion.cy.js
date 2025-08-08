describe('Session Deletion and Data Management', () => {
  beforeEach(() => {
    cy.checkServerStatus()
    
    // Create and login test user
    const testUser = {
      username: `deletetest_${Date.now()}`,
      password: 'testpass123'
    }
    cy.register(testUser.username, testUser.password)
    cy.login(testUser.username, testUser.password)
    cy.visit('/')
    
    // Mock API responses
    cy.mockApiResponses()
    
    // Create a complete session with uploaded files
    cy.writeFile('cypress/fixtures/test-photo.jpg', 'fake-photo-data')
    cy.writeFile('cypress/fixtures/test-audio.wav', 'fake-audio-data')
    cy.writeFile('cypress/fixtures/test-text.txt', 'Test personality data')
    
    cy.uploadFiles(
      'cypress/fixtures/test-photo.jpg',
      'cypress/fixtures/test-audio.wav',
      'cypress/fixtures/test-text.txt'
    )
    cy.wait('@uploadFiles')
    cy.submitConsent()
  })

  afterEach(() => {
    cy.cleanup()
  })

  describe('Delete Session Option', () => {
    it('should show delete session option in user menu', () => {
      cy.get('[data-cy="user-menu-button"]').click()
      cy.get('[data-cy="user-menu"]').should('be.visible')
      cy.get('[data-cy="delete-session-button"]').should('be.visible')
      cy.get('[data-cy="delete-session-button"]').should('contain', 'Delete Session')
    })

    it('should only show delete option when session exists', () => {
      // Should show delete option with active session
      cy.get('[data-cy="user-menu-button"]').click()
      cy.get('[data-cy="delete-session-button"]').should('be.visible')
      cy.get('[data-cy="user-menu-button"]').click() // Close menu
      
      // Mock no active session
      cy.window().then((win) => {
        win.localStorage.removeItem('currentSessionId')
      })
      cy.reload()
      
      // Should not show delete option
      cy.get('[data-cy="user-menu-button"]').click()
      cy.get('[data-cy="delete-session-button"]').should('not.exist')
    })

    it('should show warning icon for destructive action', () => {
      cy.get('[data-cy="user-menu-button"]').click()
      cy.get('[data-cy="delete-session-button"]').within(() => {
        cy.get('.MuiSvgIcon-root').should('exist') // Delete icon
      })
    })
  })

  describe('Deletion Confirmation Dialog', () => {
    beforeEach(() => {
      cy.get('[data-cy="user-menu-button"]').click()
      cy.get('[data-cy="delete-session-button"]').click()
    })

    it('should show confirmation dialog before deletion', () => {
      cy.get('[data-cy="delete-confirmation-dialog"]').should('be.visible')
      cy.get('[data-cy="delete-dialog-title"]').should('contain', 'Delete Session')
    })

    it('should explain what will be deleted', () => {
      cy.get('[data-cy="delete-confirmation-dialog"]').within(() => {
        cy.contains('permanently delete').should('be.visible')
        cy.contains('uploaded files').should('be.visible')
        cy.contains('avatar videos').should('be.visible')
        cy.contains('conversation history').should('be.visible')
        cy.contains('cannot be undone').should('be.visible')
      })
    })

    it('should show cancel and confirm buttons', () => {
      cy.get('[data-cy="delete-cancel"]').should('be.visible')
      cy.get('[data-cy="delete-confirm"]').should('be.visible')
      
      // Confirm button should be prominently styled (danger)
      cy.get('[data-cy="delete-confirm"]').should('have.class', 'MuiButton-colorError')
    })

    it('should require typing confirmation text', () => {
      // Confirm button should be disabled initially
      cy.get('[data-cy="delete-confirm"]').should('be.disabled')
      
      // Should have confirmation input
      cy.get('[data-cy="delete-confirmation-input"]').should('be.visible')
      cy.get('[data-cy="delete-confirmation-input"]').type('DELETE')
      
      // Should enable confirm button after typing
      cy.get('[data-cy="delete-confirm"]').should('be.enabled')
    })

    it('should cancel deletion and close dialog', () => {
      cy.get('[data-cy="delete-cancel"]').click()
      
      // Dialog should close
      cy.get('[data-cy="delete-confirmation-dialog"]').should('not.exist')
      
      // Session should still exist
      cy.get('[data-cy="session-chip"]').should('be.visible')
    })
  })

  describe('Session Deletion Process', () => {
    beforeEach(() => {
      cy.get('[data-cy="user-menu-button"]').click()
      cy.get('[data-cy="delete-session-button"]').click()
      
      // Type confirmation
      cy.get('[data-cy="delete-confirmation-input"]').type('DELETE')
    })

    it('should delete session successfully', () => {
      // Mock successful deletion
      cy.intercept('DELETE', '**/delete_session/*', {
        statusCode: 200,
        body: { message: 'Session data deleted successfully' }
      }).as('deleteSession')
      
      cy.get('[data-cy="delete-confirm"]').click()
      
      // Should show loading state
      cy.get('[data-cy="delete-loading"]').should('be.visible')
      
      cy.wait('@deleteSession')
      
      // Should show success message
      cy.get('[data-cy="success-alert"]').should('contain', 'Session deleted successfully')
      
      // Should clear session data from UI
      cy.get('[data-cy="session-chip"]').should('not.exist')
      
      // Should return to upload step
      cy.get('[data-cy="upload-form"]').should('be.visible')
    })

    it('should handle deletion errors gracefully', () => {
      // Mock deletion failure
      cy.intercept('DELETE', '**/delete_session/*', {
        statusCode: 500,
        body: { detail: 'Failed to delete session data' }
      }).as('deleteError')
      
      cy.get('[data-cy="delete-confirm"]').click()
      cy.wait('@deleteError')
      
      // Should show error message
      cy.get('[data-cy="error-alert"]').should('contain', 'Failed to delete session')
      
      // Session should still exist
      cy.get('[data-cy="session-chip"]').should('be.visible')
      
      // Dialog should remain open for retry
      cy.get('[data-cy="delete-confirmation-dialog"]').should('be.visible')
    })

    it('should handle unauthorized deletion attempts', () => {
      // Mock unauthorized response
      cy.intercept('DELETE', '**/delete_session/*', {
        statusCode: 403,
        body: { detail: 'Access denied: Session does not belong to current user' }
      }).as('unauthorizedDelete')
      
      cy.get('[data-cy="delete-confirm"]').click()
      cy.wait('@unauthorizedDelete')
      
      // Should show access denied error
      cy.get('[data-cy="error-alert"]').should('contain', 'Access denied')
    })

    it('should handle network errors during deletion', () => {
      cy.intercept('DELETE', '**/delete_session/*', { forceNetworkError: true }).as('networkError')
      
      cy.get('[data-cy="delete-confirm"]').click()
      cy.wait('@networkError')
      
      // Should show network error
      cy.get('[data-cy="error-alert"]').should('contain', 'network')
      
      // Should offer retry option
      cy.get('[data-cy="retry-delete"]').should('be.visible')
    })
  })

  describe('Post-Deletion State', () => {
    beforeEach(() => {
      // Complete deletion process
      cy.get('[data-cy="user-menu-button"]').click()
      cy.get('[data-cy="delete-session-button"]').click()
      cy.get('[data-cy="delete-confirmation-input"]').type('DELETE')
      
      cy.intercept('DELETE', '**/delete_session/*', {
        statusCode: 200,
        body: { message: 'Session data deleted successfully' }
      }).as('deleteSession')
      
      cy.get('[data-cy="delete-confirm"]').click()
      cy.wait('@deleteSession')
    })

    it('should clear all session-related UI elements', () => {
      // Session chip should be gone
      cy.get('[data-cy="session-chip"]').should('not.exist')
      
      // Progress stepper should reset to first step
      cy.get('[data-cy="progress-stepper"]').within(() => {
        cy.get('.Mui-active').should('contain', 'Upload Files')
      })
      
      // Upload form should be visible and reset
      cy.get('[data-cy="upload-form"]').should('be.visible')
      cy.get('[data-cy="upload-submit"]').should('be.disabled')
    })

    it('should clear session data from localStorage', () => {
      cy.window().then((win) => {
        expect(win.localStorage.getItem('currentSessionId')).to.be.null
        expect(win.localStorage.getItem('sessionData')).to.be.null
      })
    })

    it('should not show delete option in user menu', () => {
      cy.get('[data-cy="user-menu-button"]').click()
      cy.get('[data-cy="delete-session-button"]').should('not.exist')
    })

    it('should allow creating new session after deletion', () => {
      // Should be able to upload files again
      cy.uploadFiles(
        'cypress/fixtures/test-photo.jpg',
        'cypress/fixtures/test-audio.wav',
        'cypress/fixtures/test-text.txt'
      )
      
      cy.wait('@uploadFiles')
      
      // Should create new session
      cy.get('[data-cy="session-chip"]').should('be.visible')
      cy.get('[data-cy="consent-dialog"]').should('be.visible')
    })
  })

  describe('Multiple Sessions Management', () => {
    it('should handle deletion of specific session only', () => {
      // Get current session ID
      cy.get('[data-cy="session-chip"]').invoke('text').as('firstSession')
      
      // Delete current session
      cy.get('[data-cy="user-menu-button"]').click()
      cy.get('[data-cy="delete-session-button"]').click()
      cy.get('[data-cy="delete-confirmation-input"]').type('DELETE')
      
      cy.intercept('DELETE', '**/delete_session/*', {
        statusCode: 200,
        body: { message: 'Session data deleted successfully' }
      }).as('deleteSession')
      
      cy.get('[data-cy="delete-confirm"]').click()
      cy.wait('@deleteSession')
      
      // Create new session
      cy.uploadFiles(
        'cypress/fixtures/test-photo.jpg',
        'cypress/fixtures/test-audio.wav',
        'cypress/fixtures/test-text.txt'
      )
      cy.wait('@uploadFiles')
      
      // Should have different session ID
      cy.get('@firstSession').then((firstText) => {
        cy.get('[data-cy="session-chip"]').should('not.contain', firstText)
      })
    })
  })

  describe('Data Privacy Compliance', () => {
    it('should confirm complete data deletion', () => {
      cy.get('[data-cy="user-menu-button"]').click()
      cy.get('[data-cy="delete-session-button"]').click()
      
      // Should explain GDPR compliance
      cy.get('[data-cy="delete-confirmation-dialog"]').within(() => {
        cy.contains('permanently deleted').should('be.visible')
        cy.contains('cannot be recovered').should('be.visible')
        cy.contains('third-party services').should('be.visible')
      })
    })

    it('should provide data export option before deletion', () => {
      cy.get('[data-cy="user-menu-button"]').click()
      cy.get('[data-cy="export-data-button"]').should('be.visible')
      
      // Should allow exporting session data
      cy.get('[data-cy="export-data-button"]').click()
      
      // Should trigger download
      cy.get('[data-cy="export-progress"]').should('be.visible')
    })

    it('should log deletion for audit purposes', () => {
      cy.get('[data-cy="user-menu-button"]').click()
      cy.get('[data-cy="delete-session-button"]').click()
      cy.get('[data-cy="delete-confirmation-input"]').type('DELETE')
      
      // Mock deletion with audit log
      cy.intercept('DELETE', '**/delete_session/*', (req) => {
        expect(req.headers).to.have.property('authorization')
        req.reply({
          statusCode: 200,
          body: { 
            message: 'Session data deleted successfully',
            audit_log: { deleted_at: new Date().toISOString() }
          }
        })
      }).as('auditedDelete')
      
      cy.get('[data-cy="delete-confirm"]').click()
      cy.wait('@auditedDelete')
    })
  })
})