describe('Authentication Flow', () => {
  beforeEach(() => {
    // Check if backend is running
    cy.checkServerStatus()
    
    // Visit the app
    cy.visit('/')
    
    // Wait for app to load
    cy.get('[data-testid="app-title"]', { timeout: 10000 }).should('be.visible')
  })

  afterEach(() => {
    // Cleanup after each test
    cy.cleanup()
  })

  describe('User Registration', () => {
    it('should register a new user successfully', () => {
      const testUser = {
        username: `testuser_${Date.now()}`,
        password: 'testpass123',
        email: 'test@example.com'
      }

      // Should show login form initially
      cy.get('[data-cy="login-form"]').should('be.visible')
      
      // Switch to register tab
      cy.get('[data-cy="register-tab"]').click()
      
      // Fill registration form
      cy.get('[data-cy="username-input"]').type(testUser.username)
      cy.get('[data-cy="password-input"]').type(testUser.password)
      cy.get('[data-cy="email-input"]').type(testUser.email)
      
      // Submit registration
      cy.get('[data-cy="register-button"]').click()
      
      // Should show success message
      cy.get('[data-cy="success-alert"]').should('contain', 'Registration successful')
      
      // Should switch back to login tab
      cy.get('[data-cy="login-tab"]').should('have.class', 'Mui-selected')
    })

    it('should show error for duplicate username', () => {
      const testUser = {
        username: 'duplicateuser',
        password: 'testpass123',
        email: 'test1@example.com'
      }

      // Register user first time
      cy.register(testUser.username, testUser.password, testUser.email)
      
      // Try to register same username again via UI
      cy.get('[data-cy="register-tab"]').click()
      cy.get('[data-cy="username-input"]').type(testUser.username)
      cy.get('[data-cy="password-input"]').type(testUser.password)
      cy.get('[data-cy="email-input"]').type('different@example.com')
      cy.get('[data-cy="register-button"]').click()
      
      // Should show error
      cy.get('[data-cy="error-alert"]').should('contain', 'Username already exists')
    })

    it('should show error for weak password', () => {
      cy.get('[data-cy="register-tab"]').click()
      cy.get('[data-cy="username-input"]').type('testuser')
      cy.get('[data-cy="password-input"]').type('weak')  // Too short
      cy.get('[data-cy="register-button"]').click()
      
      cy.get('[data-cy="error-alert"]').should('contain', '8 characters')
    })
  })

  describe('User Login', () => {
    beforeEach(() => {
      // Create test user
      const testUser = {
        username: `logintest_${Date.now()}`,
        password: 'testpass123',
        email: 'login@test.com'
      }
      cy.register(testUser.username, testUser.password, testUser.email)
      cy.wrap(testUser).as('testUser')
    })

    it('should login successfully with valid credentials', function() {
      // Fill login form
      cy.get('[data-cy="username-input"]').type(this.testUser.username)
      cy.get('[data-cy="password-input"]').type(this.testUser.password)
      cy.get('[data-cy="login-button"]').click()
      
      // Should show success and redirect to main app
      cy.get('[data-cy="success-alert"]').should('contain', 'Login successful')
      
      // Should show stepper (main app UI)
      cy.get('[data-cy="progress-stepper"]', { timeout: 5000 }).should('be.visible')
      
      // Should show user menu
      cy.get('[data-cy="user-menu-button"]').should('be.visible')
    })

    it('should show error for invalid credentials', function() {
      cy.get('[data-cy="username-input"]').type(this.testUser.username)
      cy.get('[data-cy="password-input"]').type('wrongpassword')
      cy.get('[data-cy="login-button"]').click()
      
      cy.get('[data-cy="error-alert"]').should('contain', 'Invalid username or password')
    })

    it('should show error for empty fields', () => {
      cy.get('[data-cy="login-button"]').click()
      
      cy.get('[data-cy="error-alert"]').should('contain', 'required')
    })
  })

  describe('User Menu and Logout', () => {
    beforeEach(() => {
      // Create and login test user
      const testUser = {
        username: `menutest_${Date.now()}`,
        password: 'testpass123',
        email: 'menu@test.com'
      }
      cy.register(testUser.username, testUser.password, testUser.email)
      cy.login(testUser.username, testUser.password)
      cy.visit('/')
      cy.wrap(testUser).as('testUser')
    })

    it('should show user menu with correct username', function() {
      cy.get('[data-cy="user-menu-button"]').click()
      cy.get('[data-cy="user-menu"]').should('be.visible')
      cy.get('[data-cy="username-display"]').should('contain', this.testUser.username)
    })

    it('should logout successfully', () => {
      cy.get('[data-cy="user-menu-button"]').click()
      cy.get('[data-cy="logout-button"]').click()
      
      // Should return to login form
      cy.get('[data-cy="login-form"]').should('be.visible')
      
      // User menu should not be visible
      cy.get('[data-cy="user-menu-button"]').should('not.exist')
    })
  })

  describe('Session Management', () => {
    beforeEach(() => {
      // Create and login test user
      const testUser = {
        username: `sessiontest_${Date.now()}`,
        password: 'testpass123'
      }
      cy.register(testUser.username, testUser.password)
      cy.login(testUser.username, testUser.password)
      cy.visit('/')
    })

    it('should persist login across page refresh', () => {
      // Verify logged in
      cy.get('[data-cy="progress-stepper"]').should('be.visible')
      
      // Refresh page
      cy.reload()
      
      // Should still be logged in
      cy.get('[data-cy="progress-stepper"]').should('be.visible')
      cy.get('[data-cy="user-menu-button"]').should('be.visible')
    })

    it('should handle expired tokens gracefully', () => {
      // Mock expired token
      cy.window().then((win) => {
        win.localStorage.setItem('token', 'expired.token.here')
      })
      
      cy.reload()
      
      // Should redirect to login
      cy.get('[data-cy="login-form"]').should('be.visible')
    })
  })
})