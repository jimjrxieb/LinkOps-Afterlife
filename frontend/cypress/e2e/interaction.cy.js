describe('Avatar Interaction', () => {
  beforeEach(() => {
    cy.checkServerStatus()
    
    // Create and login test user
    const testUser = {
      username: `interacttest_${Date.now()}`,
      password: 'testpass123'
    }
    cy.register(testUser.username, testUser.password)
    cy.login(testUser.username, testUser.password)
    cy.visit('/')
    
    // Mock all API responses
    cy.mockApiResponses()
    
    // Complete upload and consent flow to reach interaction
    cy.writeFile('cypress/fixtures/test-photo.jpg', 'fake-photo-data')
    cy.writeFile('cypress/fixtures/test-audio.wav', 'fake-audio-data')
    cy.writeFile('cypress/fixtures/test-text.txt', 'Test personality text')
    
    cy.uploadFiles(
      'cypress/fixtures/test-photo.jpg',
      'cypress/fixtures/test-audio.wav',
      'cypress/fixtures/test-text.txt'
    )
    cy.wait('@uploadFiles')
    cy.submitConsent()
    
    // Wait for processing to complete and navigate to interaction
    cy.waitForProcessing()
    cy.get('[data-cy="interact-tab"]').click()
  })

  afterEach(() => {
    cy.cleanup()
  })

  describe('Interaction Interface', () => {
    it('should display interaction panel correctly', () => {
      cy.get('[data-cy="interaction-panel"]').should('be.visible')
      cy.get('[data-cy="chat-input"]').should('be.visible')
      cy.get('[data-cy="send-message"]').should('be.visible')
      cy.get('[data-cy="video-display"]').should('be.visible')
    })

    it('should show avatar video placeholder initially', () => {
      cy.get('[data-cy="video-display"]').within(() => {
        cy.get('[data-cy="avatar-placeholder"]').should('be.visible')
        cy.contains('Start a conversation').should('be.visible')
      })
    })

    it('should display usage limit information', () => {
      cy.get('[data-cy="usage-info"]').should('be.visible')
      cy.get('[data-cy="remaining-interactions"]').should('contain', 'remaining')
    })

    it('should show conversation history area', () => {
      cy.get('[data-cy="conversation-history"]').should('be.visible')
    })
  })

  describe('Chat Input and Validation', () => {
    it('should enable send button when message is typed', () => {
      // Initially disabled
      cy.get('[data-cy="send-message"]').should('be.disabled')
      
      // Type message
      cy.get('[data-cy="chat-input"]').type('Hello, how are you?')
      
      // Should be enabled
      cy.get('[data-cy="send-message"]').should('be.enabled')
    })

    it('should disable send button for empty messages', () => {
      cy.get('[data-cy="chat-input"]').type('Hello')
      cy.get('[data-cy="send-message"]').should('be.enabled')
      
      // Clear input
      cy.get('[data-cy="chat-input"]').clear()
      cy.get('[data-cy="send-message"]').should('be.disabled')
    })

    it('should limit message length', () => {
      const longMessage = 'a'.repeat(1000)
      cy.get('[data-cy="chat-input"]').type(longMessage)
      
      // Should show character count warning
      cy.get('[data-cy="char-count-warning"]').should('be.visible')
    })

    it('should support multiline messages', () => {
      cy.get('[data-cy="chat-input"]').type('Line 1{shift+enter}Line 2{shift+enter}Line 3')
      
      cy.get('[data-cy="chat-input"]').should('contain.value', 'Line 1\nLine 2\nLine 3')
    })
  })

  describe('Message Sending and Response', () => {
    it('should send message and display response', () => {
      const message = 'Hello, how are you today?'
      
      cy.interactWithAvatar(message)
      
      // Should show loading state
      cy.get('[data-cy="message-loading"]').should('be.visible')
      
      // Wait for response
      cy.wait('@interact')
      
      // Should display user message
      cy.get('[data-cy="user-message"]').should('contain', message)
      
      // Should display avatar response
      cy.get('[data-cy="avatar-response"]').should('be.visible')
      
      // Should show response video
      cy.get('[data-cy="response-video"]').should('be.visible')
    })

    it('should clear input after sending message', () => {
      cy.get('[data-cy="chat-input"]').type('Test message')
      cy.get('[data-cy="send-message"]').click()
      
      // Input should be cleared
      cy.get('[data-cy="chat-input"]').should('have.value', '')
    })

    it('should handle keyboard shortcuts', () => {
      cy.get('[data-cy="chat-input"]').type('Test message{enter}')
      
      // Should send message on Enter
      cy.wait('@interact')
      cy.get('[data-cy="user-message"]').should('contain', 'Test message')
    })

    it('should prevent sending during processing', () => {
      // Send first message
      cy.interactWithAvatar('First message')
      
      // Try to send another while processing
      cy.get('[data-cy="chat-input"]').type('Second message')
      cy.get('[data-cy="send-message"]').should('be.disabled')
      
      // Wait for first response
      cy.wait('@interact')
      
      // Should be able to send again
      cy.get('[data-cy="send-message"]').should('be.enabled')
    })
  })

  describe('Video Response Display', () => {
    beforeEach(() => {
      cy.interactWithAvatar('Hello there!')
      cy.wait('@interact')
    })

    it('should display response video with controls', () => {
      cy.get('[data-cy="response-video"]').should('exist')
      cy.get('[data-cy="video-controls"]').should('be.visible')
      cy.get('[data-cy="play-pause-button"]').should('be.visible')
      cy.get('[data-cy="fullscreen-button"]').should('be.visible')
    })

    it('should support video playback controls', () => {
      // Should be able to play/pause
      cy.get('[data-cy="play-pause-button"]').click()
      cy.get('[data-cy="response-video"]').should('have.prop', 'paused', false)
      
      // Should be able to pause
      cy.get('[data-cy="play-pause-button"]').click()
      cy.get('[data-cy="response-video"]').should('have.prop', 'paused', true)
    })

    it('should support fullscreen mode', () => {
      cy.get('[data-cy="fullscreen-button"]').click()
      
      // Should enter fullscreen (mock check)
      cy.get('[data-cy="video-fullscreen"]').should('have.class', 'fullscreen')
    })

    it('should show video download option', () => {
      cy.get('[data-cy="download-video"]').should('be.visible')
      cy.get('[data-cy="download-video"]').should('have.attr', 'href')
    })

    it('should auto-play response videos', () => {
      // New response should auto-play
      cy.get('[data-cy="response-video"]').should('have.prop', 'paused', false)
    })
  })

  describe('Conversation History', () => {
    beforeEach(() => {
      // Send multiple messages to build history
      const messages = ['Hello!', 'How are you?', 'Tell me about yourself']
      
      messages.forEach((message, index) => {
        cy.interactWithAvatar(message)
        cy.wait('@interact')
        cy.wait(1000) // Small delay between messages
      })
    })

    it('should display conversation history chronologically', () => {
      cy.get('[data-cy="conversation-history"]').within(() => {
        cy.get('[data-cy="message-pair"]').should('have.length', 3)
        
        // Check chronological order
        cy.get('[data-cy="message-pair"]').first().should('contain', 'Hello!')
        cy.get('[data-cy="message-pair"]').last().should('contain', 'Tell me about yourself')
      })
    })

    it('should show timestamps for messages', () => {
      cy.get('[data-cy="message-timestamp"]').should('exist')
      cy.get('[data-cy="message-timestamp"]').should('contain', ':') // Time format
    })

    it('should allow replaying previous responses', () => {
      cy.get('[data-cy="replay-button"]').first().click()
      
      // Should replay the video
      cy.get('[data-cy="response-video"]').should('have.prop', 'paused', false)
    })

    it('should scroll to latest message automatically', () => {
      // Send one more message
      cy.interactWithAvatar('Latest message')
      cy.wait('@interact')
      
      // Should scroll to bottom
      cy.get('[data-cy="conversation-history"]').should('be.scrolledTo', 'bottom')
    })
  })

  describe('Usage Limits and Restrictions', () => {
    it('should show remaining interaction count', () => {
      cy.get('[data-cy="usage-info"]').within(() => {
        cy.get('[data-cy="interactions-remaining"]').should('exist')
        cy.contains(/\d+ remaining/).should('be.visible')
      })
    })

    it('should update usage count after interaction', () => {
      // Get initial count
      cy.get('[data-cy="interactions-remaining"]').invoke('text').as('initialCount')
      
      // Send message
      cy.interactWithAvatar('Test message')
      cy.wait('@interact')
      
      // Count should decrease
      cy.get('@initialCount').then((initial) => {
        cy.get('[data-cy="interactions-remaining"]').should('not.contain', initial)
      })
    })

    it('should warn when approaching usage limit', () => {
      // Mock low usage remaining
      cy.intercept('POST', '**/interact/*', {
        statusCode: 200,
        body: {
          message: 'Interactive response generated successfully',
          usage_info: { remaining_interactions: 2, daily_limit: 10 }
        }
      }).as('lowUsage')
      
      cy.interactWithAvatar('Test message')
      cy.wait('@lowUsage')
      
      // Should show warning
      cy.get('[data-cy="usage-warning"]').should('be.visible')
      cy.get('[data-cy="usage-warning"]').should('contain', 'approaching limit')
    })

    it('should block interaction when limit exceeded', () => {
      // Mock usage limit exceeded
      cy.intercept('POST', '**/interact/*', {
        statusCode: 429,
        body: { detail: 'Daily usage limit exceeded' }
      }).as('limitExceeded')
      
      cy.interactWithAvatar('Test message')
      cy.wait('@limitExceeded')
      
      // Should show error and disable input
      cy.get('[data-cy="error-alert"]').should('contain', 'usage limit exceeded')
      cy.get('[data-cy="chat-input"]').should('be.disabled')
      cy.get('[data-cy="send-message"]').should('be.disabled')
    })
  })

  describe('Error Handling', () => {
    it('should handle interaction failures gracefully', () => {
      cy.intercept('POST', '**/interact/*', {
        statusCode: 500,
        body: { detail: 'Avatar generation failed' }
      }).as('interactionError')
      
      cy.interactWithAvatar('Test message')
      cy.wait('@interactionError')
      
      // Should show error message
      cy.get('[data-cy="error-alert"]').should('contain', 'generation failed')
      
      // Should re-enable input for retry
      cy.get('[data-cy="chat-input"]').should('be.enabled')
      cy.get('[data-cy="send-message"]').should('be.enabled')
    })

    it('should handle network timeouts', () => {
      cy.intercept('POST', '**/interact/*', { forceNetworkError: true }).as('networkError')
      
      cy.interactWithAvatar('Test message')
      cy.wait('@networkError')
      
      // Should show network error
      cy.get('[data-cy="error-alert"]').should('contain', 'network')
    })

    it('should retry failed interactions', () => {
      cy.intercept('POST', '**/interact/*', {
        statusCode: 500,
        body: { detail: 'Temporary error' }
      }).as('tempError')
      
      cy.interactWithAvatar('Test message')
      cy.wait('@tempError')
      
      // Should show retry button
      cy.get('[data-cy="retry-button"]').should('be.visible')
      
      // Mock successful retry
      cy.intercept('POST', '**/interact/*', {
        statusCode: 200,
        body: { message: 'Success', video_path: '/mock/video.mp4' }
      }).as('retrySuccess')
      
      cy.get('[data-cy="retry-button"]').click()
      cy.wait('@retrySuccess')
      
      // Should show successful response
      cy.get('[data-cy="avatar-response"]').should('be.visible')
    })
  })

  describe('Accessibility', () => {
    it('should support keyboard navigation', () => {
      // Should be able to tab to input
      cy.get('body').tab()
      cy.focused().should('have.attr', 'data-cy', 'chat-input')
      
      // Should be able to tab to send button
      cy.focused().tab()
      cy.focused().should('have.attr', 'data-cy', 'send-message')
    })

    it('should have proper ARIA labels', () => {
      cy.get('[data-cy="chat-input"]').should('have.attr', 'aria-label')
      cy.get('[data-cy="send-message"]').should('have.attr', 'aria-label')
      cy.get('[data-cy="response-video"]').should('have.attr', 'aria-label')
    })

    it('should announce messages to screen readers', () => {
      cy.interactWithAvatar('Test message')
      cy.wait('@interact')
      
      // Should have live region for announcements
      cy.get('[aria-live="polite"]').should('exist')
    })
  })
})