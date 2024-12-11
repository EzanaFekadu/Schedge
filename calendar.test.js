import { render, screen } from '@testing-library/react'; // Assuming you're using React Testing Library
import Calendar from './Calendar'; // Import your Calendar component

test('displays events correctly', () => {
    const events = [
        { id: 1, title: 'Meeting', start: '2024-12-10T10:00:00', end: '2024-12-10T11:00:00' },
    ];

    render(<Calendar events={events} />); // Use JSX syntax here

    // Check if the event title is rendered
    expect(screen.getByText('Meeting')).toBeInTheDocument();
});
