
# Syllabus Generator

This project provides a tool to generate course syllabi based on input data provided in JSON format. The system allows users to specify various course-related details and outputs a structured syllabus.

## Features

- **Input JSON**: Define course details including subject, grade level, course description, objectives, materials, grading policy, and more.
- **Automated Syllabus Generation**: Creates a detailed syllabus based on the provided data.

## Usage

To generate a syllabus, provide an input JSON file with the necessary course information. The expected JSON structure is as follows:

```json
{
    "user": {
        "id": "string",
        "fullName": "string",
        "email": "string"
    },
    "type": "tool",
    "tool_data": {
        "tool_id": 2,
        "inputs": [
            {
                "name": "subject_topic",
                "value": "Introduction to Algebra"
            },
            {
                "name": "grade_level",
                "value": "High School"
            },
            {
                "name": "subject",
                "value": "Mathematics"
            },
            {
                "name": "course_description",
                "value": "An introductory course on algebra and geometry."
            },
            {
                "name": "course_objectives",
                "value": "To teach students the fundamentals of algebra."
            },
            {
                "name": "required_materials",
                "value": "Textbook, calculator, notebook"
            },
            {
                "name": "grading_policy",
                "value": "50% Exams, 30% Homework, 20% Participation"
            },
            {
                "name": "course_outline",
                "value": "Week 1-2: Algebra basics, Week 3-4: Geometry"
            },
            {
                "name": "class_policies",
                "value": "No late submissions, attendance required"
            },
            {
                "name": "instructor_name",
                "value": "Dr. John Doe"
            },
            {
                "name": "instructor_title",
                "value": "Professor"
            },
            {
                "name": "important_dates",
                "value": "2024-08-01 to 2024-12-15"
            },
            {
                "name": "learning_outcomes",
                "value": "Students will understand basic algebraic principles."
            },
            {
                "name": "class_schedule",
                "value": "Monday and Wednesday, 10:00 AM - 11:30 AM"
            },
            {
                "name": "instructor_contact",
                "value": "johndoe@example.com"
            },
            {
                "name": "additional_customizations",
                "value": "Include extra instructor_contact johndo@example.com in the syllabus."
            }
        ]
    }
}
```

## File Structure

- **core.py**: Contains the core logic for processing the input and generating the syllabus.
- **tools.py**: Contains helper functions and utilities for the project as well as the default input prompt to the LLM which the user can change.
- **metadata.json**: Defines the input structure and metadata for the syllabus generation tool.

## Input Data Description

The JSON input data should contain the following fields:
- `Grade Level`: The educational level for which the syllabus is intended (e.g., "High School").
- `Important Dates`: Start and end dates of the course.
- `Subject`: The subject of the course (e.g., "Mathematics").
- `Course Description`: A brief overview of the course content.
- `Learning Outcomes`: The expected outcomes for students.
- `Course Objectives`: The goals of the course.
- `Class Schedule`: Days and times the class will meet.
- `Required Materials`: Materials needed for the course.
- `Grading Policy`: Breakdown of grading criteria.
- `Course Outline`: A weekly outline of topics to be covered.
- `Class Policies`: Rules and expectations for the class.
- `Instructor Name`: The name of the course instructor.
- `Instructor Title`: The title of the course instructor.
- `Instructor Contact`: Contact information for the instructor.
- `Additional Customizations`: Any additional customization requests for the syllabus.

