#!/bin/bash

# Base URL
BASE_URL="http://localhost:5000/api/employees"

# Create Employee
echo "Creating employee..."
CREATE_RESPONSE=$(curl -s -X POST $BASE_URL \
    -H "Content-Type: application/json" \
    -d '{"name": "John Doe", "position": "Developer", "department": "IT"}')
EMPLOYEE_ID=$(echo $CREATE_RESPONSE | jq -r '.id')
echo "Employee created with ID: $EMPLOYEE_ID"

# Read Employees
echo "Fetching employees..."
curl -s -X GET $BASE_URL

# Update Employee
echo "Updating employee..."
curl -s -X PUT $BASE_URL/$EMPLOYEE_ID \
    -H "Content-Type: application/json" \
    -d '{"name": "Jane Doe", "position": "Senior Developer", "department": "IT"}'

# Delete Employee
echo "Deleting employee..."
curl -s -X DELETE $BASE_URL/$EMPLOYEE_ID
