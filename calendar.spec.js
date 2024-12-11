describe('Calendar Events', () => {
    beforeEach(() => {
        // Visit the employee dashboard page
        cy.visit('/employee-dashboard');
    });

    it('should display events on the calendar', () => {
        cy.get('#calendar') // The calendar container
            .should('exist')
            .within(() => {
                // Verify that events like 'Meeting' are shown on the calendar
                cy.contains('Meeting').should('be.visible');
                cy.contains('Team Update').should('be.visible');
            });
    });

    it('should show event details when clicked', () => {
        cy.get('.fc-event') // Class for calendar events
            .first()
            .click(); // Click on the first event
        cy.contains('Event Details').should('be.visible'); // Adjust with your modal or details section
    });

    it('should allow shift swap requests', () => {
        cy.get('#requested_shift_id')
            .select('2024-12-15 (09:00 - 17:00)'); // Select a shift from the dropdown

        cy.get('#target_shift_id')
            .select('2024-12-16 (10:00 - 18:00)'); // Select a target shift

        cy.get('button[type="submit"]').click(); // Submit the swap request

        // Check if the success message appears
        cy.contains('Shift swap request sent').should('be.visible');
    });
});
