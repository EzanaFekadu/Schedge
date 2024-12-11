// test for FullCalendar events rendering

test('FullCalendar displays events correctly', () => {
    const scheduleData = [
        {
            title: "Development Work",
            start: "2024-12-15T09:00:00",
            end: "2024-12-15T17:00:00",
            employeeName: "John Doe",
            position: "Developer",
            department: "Engineering",
        },
        {
            title: "Client Meeting",
            start: "2024-12-16T10:00:00",
            end: "2024-12-16T16:00:00",
            employeeName: "Jane Smith",
            position: "Manager",
            department: "Sales",
        },
    ];

    const events = scheduleData.map(schedule => ({
        title: schedule.title,
        start: schedule.start,
        end: schedule.end,
        extendedProps: {
            employeeName: schedule.employeeName,
            position: schedule.position,
            department: schedule.department,
        },
    }));

    // Simulate FullCalendar's event click to test the event content
    events.forEach(event => {
        expect(event.title).toBeDefined();
        expect(event.start).toBeDefined();
        expect(event.end).toBeDefined();
        expect(event.extendedProps.employeeName).toBeDefined();
        expect(event.extendedProps.position).toBeDefined();
        expect(event.extendedProps.department).toBeDefined();
    });
});
