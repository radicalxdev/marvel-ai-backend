import pytest

from app.assistants.classroom_support.co_teacher.core import executor
from app.services.assistant_registry import Message, MessagePayload, MessageType, Role, UserInfo

base_attributes = {
    "user_info": UserInfo(
        user_name="Aaron",
        user_age=30,
        user_preference="Senior AI Engineer"
    )
}

def test_executor_translate_valid():
    result = executor(
        **base_attributes,
        messages = [
            Message(
                role=Role.human,
                type=MessageType.text,
                timestamp="string",
                payload=MessagePayload(
                    text="Give me insights for personalized teaching"
                )
            ),
            Message(
                role=Role.ai,
                type=MessageType.text,
                timestamp=None,
                payload=MessagePayload(
                    text=(
                        "Okay, Aaron, as a Senior AI Engineer, you're likely someone who values data-driven strategies and innovative "
                        "solutions. Let's tailor some insights for personalized teaching with that in mind. Here's how you can approach "
                        "this, leveraging your analytical and problem-solving skills:\n\n"
                        "**1. Data-Driven Student Understanding:**\n\n"
                        "*   **Analytics Approach:** Just like in AI projects, you can analyze student performance data to identify patterns "
                        "and tailor your teaching methods. Look at areas where students excel and where they struggle. Use this data to "
                        "understand the varying needs of your students.\n"
                        "*   **Actionable Steps:**\n"
                        "    *   Use formative assessments (quizzes, exit tickets, in-class activities) to collect data.\n"
                        "    *   Create a spreadsheet or use a digital tool to track student performance across different topics or skills.\n"
                        "    *   Identify individual student strengths, areas of improvement, and preferred learning styles.\n\n"
                        "**2. Adaptive Content and Delivery:**\n\n"
                        "*   **Modular Content Creation:** Think of your teaching material like modular code, where you can easily modify "
                        "and adapt it. Develop a core set of learning materials and then adapt to student needs by offering multiple versions "
                        "(different problem sets, examples, or explanations).\n"
                        "*   **Actionable Steps:**\n"
                        "    *   Develop a resource repository of varying complexity levels for each topic.\n"
                        "    *   Experiment with different media formats (videos, interactive simulations, audio explanations) to cater to diverse "
                        "learning preferences.\n"
                        "    *   Offer a range of choices in how students approach their learning - which project they want to work on, which "
                        "practice questions they attempt, etc.\n\n"
                        "**3. Algorithm-Based Feedback:**\n\n"
                        "*   **Timely and Specific Feedback:** Aim to provide feedback that is not only timely but also very specific. Think "
                        "of it as debugging a code – the feedback needs to pinpoint the problem precisely.\n"
                        "*   **Actionable Steps:**\n"
                        "    *   Use rubrics for grading that clearly outline expectations.\n"
                        "    *   Provide feedback that is focused on the concepts, not just the final answer.\n"
                        "    *   Use automated tools, where possible, to offer initial feedback, allowing you to focus on more complex issues.\n\n"
                        "**4. Collaborative Problem-Solving:**\n\n"
                        "*   **Agile Team Teaching:** Approach your classroom as an agile team working on a project. Encourage collaboration "
                        "and peer-to-peer learning.\n"
                        "*   **Actionable Steps:**\n"
                        "    *   Implement group activities with defined roles, as you might in a project team.\n"
                        "    *   Have students teach each other concepts, thereby reinforcing their own understanding.\n"
                        "    *   Use pair programming or group programming tasks to foster learning from each other.\n\n"
                        "**5. Iterative Teaching Process:**\n\n"
                        "*   **Continuous Improvement:** Just like in software development, use a continuous improvement approach to your teaching. "
                        "Regularly evaluate your teaching practices and make adjustments based on results.\n"
                        "*   **Actionable Steps:**\n"
                        "    *   Solicit student feedback on your teaching methods and the content.\n"
                        "    *   Periodically reflect on what works and what doesn't.\n"
                        "    *   Don't be afraid to experiment with new approaches based on feedback and data.\n\n"
                        "Aaron, your experience with AI and data analysis can be a powerful asset in personalizing your teaching approach. By treating "
                        "your classroom as a dynamic system with evolving needs, you can create a learning environment that is truly tailored to each "
                        "of your students. You have an analytical mindset and the tools to make data-driven decisions in the classroom. By embracing "
                        "these strategies, you'll be able to provide a more engaging and effective learning experience for your students! Let me know "
                        "if you want to explore any of these strategies further."
                    )
                )
            ),
            Message(
                role=Role.human,
                type=MessageType.text,
                timestamp="string",
                payload=MessagePayload(
                    text="Please, summarize what you said and translate that to Spanish"
                )
            )
        ]
    )
    assert isinstance(result, str)

def test_executor_translate_invalid():
    with pytest.raises(TypeError) as exc_info:
        executor(
            messages=[
                {
                    "role":"human",
                    "type":"text",
                    "timestamp":"string",
                    "payload":{
                    "text":"Give me insights for personalized teaching"
                    }
                },
                {
                    "role":"ai",
                    "type":"text",
                    "timestamp":None,
                    "payload":{
                    "text":"Okay, Aaron, as a Senior AI Engineer, you're likely someone who values data-driven strategies and innovative solutions. Let's tailor some insights for personalized teaching with that in mind. Here's how you can approach this, leveraging your analytical and problem-solving skills:\n\n**1. Data-Driven Student Understanding:**\n\n*   **Analytics Approach:** Just like in AI projects, you can analyze student performance data to identify patterns and tailor your teaching methods. Look at areas where students excel and where they struggle. Use this data to understand the varying needs of your students.\n*   **Actionable Steps:**\n    *   Use formative assessments (quizzes, exit tickets, in-class activities) to collect data.\n    *   Create a spreadsheet or use a digital tool to track student performance across different topics or skills.\n    *   Identify individual student strengths, areas of improvement, and preferred learning styles.\n\n**2. Adaptive Content and Delivery:**\n\n*   **Modular Content Creation:** Think of your teaching material like modular code, where you can easily modify and adapt it. Develop a core set of learning materials and then adapt to student needs by offering multiple versions (different problem sets, examples, or explanations).\n*   **Actionable Steps:**\n    *   Develop a resource repository of varying complexity levels for each topic.\n    *   Experiment with different media formats (videos, interactive simulations, audio explanations) to cater to diverse learning preferences.\n    *   Offer a range of choices in how students approach their learning - which project they want to work on, which practice questions they attempt, etc.\n\n**3. Algorithm-Based Feedback:**\n\n*   **Timely and Specific Feedback:** Aim to provide feedback that is not only timely but also very specific. Think of it as debugging a code – the feedback needs to pinpoint the problem precisely.\n*   **Actionable Steps:**\n    *   Use rubrics for grading that clearly outline expectations.\n    *   Provide feedback that is focused on the concepts, not just the final answer.\n    *   Use automated tools, where possible, to offer initial feedback, allowing you to focus on more complex issues.\n\n**4. Collaborative Problem-Solving:**\n\n*   **Agile Team Teaching:** Approach your classroom as an agile team working on a project. Encourage collaboration and peer-to-peer learning.\n*   **Actionable Steps:**\n    *   Implement group activities with defined roles, as you might in a project team.\n    *   Have students teach each other concepts, thereby reinforcing their own understanding.\n    *   Use pair programming or group programming tasks to foster learning from each other.\n\n**5. Iterative Teaching Process:**\n\n*   **Continuous Improvement:** Just like in software development, use a continuous improvement approach to your teaching. Regularly evaluate your teaching practices and make adjustments based on results.\n*   **Actionable Steps:**\n    *   Solicit student feedback on your teaching methods and the content.\n    *   Periodically reflect on what works and what doesn't.\n    *   Don't be afraid to experiment with new approaches based on feedback and data.\n\nAaron, your experience with AI and data analysis can be a powerful asset in personalizing your teaching approach. By treating your classroom as a dynamic system with evolving needs, you can create a learning environment that is truly tailored to each of your students. You have an analytical mindset and the tools to make data driven decisions in the classroom. By embracing these strategies, you'll be able to provide a more engaging and effective learning experience for your students! Let me know if you want to explore any of these strategies further.\n"
                    }
                },
                {
                    "role":"human",
                    "type":"text",
                    "timestamp":"string",
                    "payload":{
                    "text":"Please, summarize what you said and translate that to spanish"
                    }
                }
            ]
        )
    assert isinstance(exc_info.value, TypeError)