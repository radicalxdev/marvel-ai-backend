import re
from app.features.syllabus_generator import credentials
from app.features.syllabus_generator.tools import Search_engine, Syllabus_generator

data = {
    "course_description": "This university-level economics course prepares students for success in standardized exams by providing a comprehensive overview of microeconomic and macroeconomic principles. Through lectures, discussions, and practice problems, students will gain a deep understanding of supply and demand, market structures, economic growth, monetary and fiscal policy, and international trade. The course emphasizes critical thinking, problem-solving, and analytical skills, equipping students to apply economic concepts to real-world scenarios. By mastering the material covered in this course, students will be well-prepared to excel in their exams and gain a strong foundation for further study or careers in economics. \n",
    "course_objectives": [
      "1) Demonstrate a comprehensive understanding of fundamental microeconomic and macroeconomic principles.",
      "2) Analyze and interpret economic data and models to draw informed conclusions.",
      "3) Apply economic concepts to real-world scenarios and policy issues.",
      "4) Develop critical thinking and problem-solving skills in the context of economic analysis.",
      "5) Effectively communicate economic ideas and arguments in written and oral formats.",
      "6) Prepare for success in standardized economics exams by mastering key concepts and exam-taking strategies.",
      "7) Gain a solid foundation for further study or careers in economics."
    ],
    "study_materials": [
      {
        "material": "**Textbooks:**\n* Mankiw, N. Gregory. Principles of Economics. 9th ed., Cengage Learning, 2020.\n* Samuelson, Paul A., and William D. Nordhaus. Economics. 20th ed., McGraw-Hill Education, 2020.",
        "purpose": "Provide a comprehensive foundation in economic principles and theories."
      },
      {
        "material": "**Lecture Notes and Slides:**\n* Downloadable lecture notes and slides from the course website, covering each week's topics in detail.",
        "purpose": "Supplement textbook learning with additional explanations, examples, and visuals."
      },
      {
        "material": "**Online Resources:**\n* The Economist: https://www.economist.com/\n* Project Syndicate: https://www.project-syndicate.org/\n* International Monetary Fund (IMF): https://www.imf.org/\n* World Bank: https://www.worldbank.org/",
        "purpose": "Stay informed about current economic events, analyses, and policy discussions."
      },
      {
        "material": "**Past Exams and Solutions:**\n* Access to previous years' exam papers and solutions, available on the course website.",
        "purpose": "Familiarize yourself with the exam format, question types, and expected answer structure."
      },
      {
        "material": "**Practice Problems and Exercises:**\n* Textbook end-of-chapter problems and additional practice exercises provided by the instructor.",
        "purpose": "Test your understanding of key concepts and apply economic theories to real-world scenarios."
      },
      {
        "material": "**Study Groups and Collaboration:**\n* Form study groups with classmates to discuss course material, clarify doubts, and work on problems together.",
        "purpose": "Enhance learning through peer interaction, collaborative problem-solving, and diverse perspectives."
      },
      {
        "material": "**Office Hours and Instructor Support:**\n* Utilize office hours to ask questions, seek clarification, and receive personalized guidance from the instructor.",
        "purpose": "Address specific learning challenges, gain deeper insights, and ensure a strong grasp of the material."
      },
      {
        "material": "**Academic Integrity:**\n* Adhere to the university's policies on academic integrity, avoiding plagiarism and upholding ethical standards in all academic work.",
        "purpose": "Foster a culture of honesty, fairness, and respect for intellectual property."
      }
    ],
    "course_outline": [
      {
        "duration": "4 weeks",
        "topic": "Introduction to Economics",
        "subtopics": [
          "What is economics?",
          "Scarcity and choice",
          "The economic way of thinking",
          "Economic models",
          "Economic systems",
          "Economic measurement",
          "The history of economic thought"
        ]
      },
      {
        "duration": "6 weeks",
        "topic": "Microeconomics",
        "subtopics": [
          "Demand and supply",
          "Consumer theory",
          "Production and cost theory",
          "Market structures",
          "Perfect competition",
          "Monopoly",
          "Oligopoly",
          "Monopolistic competition",
          "Game theory",
          "Externalities",
          "Public goods",
          "Income distribution"
        ]
      },
      {
        "duration": "6 weeks",
        "topic": "Macroeconomics",
        "subtopics": [
          "National income accounting",
          "Economic growth",
          "Inflation and unemployment",
          "Monetary policy",
          "Fiscal policy",
          "International economics",
          "Comparative advantage and trade",
          "Balance of payments",
          "Exchange rates",
          "Economic development",
          "Development strategies",
          "Poverty and inequality",
          "Environmental economics",
          "Sustainability",
          "Climate change"
        ]
      },
      {
        "duration": "2 weeks",
        "topic": "Behavioral Economics",
        "subtopics": [
          "Decision-making",
          "Prospect theory",
          "Heuristics and biases",
          "Nudge theory"
        ]
      },
      {
        "duration": "2 weeks",
        "topic": "Public Economics",
        "subtopics": [
          "Taxation",
          "Public goods",
          "Health economics",
          "Education economics",
          "Labor economics",
          "Wage determination",
          "Unemployment"
        ]
      },
      {
        "duration": "2 weeks",
        "topic": "Econometrics",
        "subtopics": [
          "Statistical methods",
          "Regression analysis",
          "Time series analysis"
        ]
      }
    ],
    "grading_policy": [
      {
        "Component": "Midterm Exam",
        "Coefficient": 0.3,
        "Note": "Covers all topics up to the midterm break."
      },
      {
        "Component": "Final Exam",
        "Coefficient": 0.4,
        "Note": "Comprehensive exam covering all topics in the course."
      },
      {
        "Component": "Assignments",
        "Coefficient": 0.3,
        "Note": "Includes problem sets, quizzes, and other assessments throughout the semester."
      }
    ],
    "rules_policies": {
      "Attendance": [
        "Attendance is mandatory for all lectures and tutorials.",
        "Students are expected to be on time and prepared for each class.",
        "Excessive absences may result in a penalty to the final grade.",
        "Students who miss a class due to illness or other unavoidable circumstances must provide a valid excuse to the instructor."
      ],
      "Assignments": [
        "All assignments must be submitted on time and in the specified format.",
        "Late submissions will be penalized according to the course policy.",
        "Plagiarism will not be tolerated and will result in disciplinary action.",
        "Students are encouraged to collaborate on assignments, but all work must be original and properly cited."
      ],
      "Exams": [
        "There will be two midterm exams and one final exam.",
        "The exams will cover all material covered in lectures, tutorials, and assigned readings.",
        "Students are responsible for knowing the exam schedule and location.",
        "No cheating or unauthorized materials will be allowed during exams."
      ],
      "Grading": [
        "The final grade will be based on the following weights:",
        "Midterm exams (20% each)",
        "Final exam (40%)",
        "Assignments (20%)",
        "The grading scale is as follows:",
        "90-100% = A",
        "80-89% = B",
        "70-79% = C",
        "60-69% = D",
        "Below 60% = F"
      ],
      "Academic Integrity": [
        "All students are expected to uphold the highest standards of academic integrity.",
        "Plagiarism, cheating, and other forms of academic dishonesty will not be tolerated.",
        "Students who violate the academic integrity policy will be subject to disciplinary action, which may include failing the course or being expelled from the university."
      ],
      "Disability Services": [
        "Students with disabilities who require accommodations should contact the Disability Services office at the beginning of the semester.",
        "The Disability Services office will work with students to develop an accommodation plan that meets their individual needs."
      ],
      "Communication": [
        "Students are encouraged to communicate with the instructor and teaching assistants if they have any questions or concerns.",
        "The instructor and teaching assistants will hold regular office hours.",
        "Students can also contact the instructor and teaching assistants by email."
      ]
    },
    "memes": [
      "https://i.redd.it/jajhk68osghd1.jpeg",
      "https://i.redd.it/uj9ew9358xgd1.jpeg",
      "https://i.redd.it/dp4m2l8neggd1.jpeg",
      "https://i.redd.it/yk9m1j3b0ggd1.jpeg",
      "https://i.redd.it/522ei5fb3cgd1.jpeg",
      "https://i.redd.it/fy03xtsih3gd1.jpeg",
      "https://i.redd.it/x30mlkqjdxfd1.jpeg",
      "https://i.redd.it/oyml6qag0ifd1.jpeg",
      "https://i.redd.it/cbhcff0avhfd1.png",
      "https://i.redd.it/0w97pf6rrefd1.jpeg",
      "https://i.redd.it/820jeutjnthd1.jpeg",
      "https://i.redd.it/ys40mz1wqphd1.png",
      "https://i.redd.it/7hpc9fotpohd1.jpeg",
      "https://i.redd.it/tvmw22313vhd1.png",
      "https://i.redd.it/il0wcc32nmhd1.jpeg"
    ]
  }

def is_valid_url(url):
    pattern = re.compile(r'^https?://(www\.)?([\w\.-]+)(/[\w\-/]*)?$')
    return bool(pattern.match(url))

grade = 'university'
subject = 'Mathematics'
Syllabus_type = 'Exam-based'
instructions = 'None'

Test_Engine = Search_engine(grade,subject)
Test_Generator = Syllabus_generator(grade,subject,Syllabus_type,instructions)
