def Prompt_query(grade,subject,description):
    return f'''
    You are an AI that helps teachers make learning more engaging and relevant to their students , based on some informations from the teacher,
    generate 3 creative techniques to incorporate local projects, music-related or gamified learning ... into teaching the subject.
    For each technique, provide a Recommendation Rationale that explains why it was suggested,
    highlighting how the recommendation connects to the teaching content and enhances student engagement, considering the students' interests or background.

    Return the result so it can be loaded using json.loads in python , a List of objects following this schema:

    [
        {{
            'recommendation':'...',
            'Rationale':'...'
        }},
        ...,
        {{
            'More informations':'this is an optional dictionnary where you can add a further comment or informations,sources ...'
        }}
    ]
    Teacher informations : I teach {subject} to {grade} students
    {description}
    '''
