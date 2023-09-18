"""
The Prompt class is designed to encapsulate directives, guidelines, and constraints for guiding a large language model's response.

Directives: These are the core instructions that guide the model's response. They can include various subcategories like questions, statements, instructions, creative requests, analytical questions, hypothetical scenarios, debates, dialogues, step-by-step, and more.

Guidelines: These shape the tone, structure, and context of the response. They can include aspects like role, style, format, context, audience awareness, cultural sensitivity, accessibility considerations, multimodal instructions, and more.

Constraints: These set limitations or boundaries for the response, including length constraints, content restrictions, time, ethics, language, accessibility, legal or regulatory, domain-specific, sensitivity, multimodal constraints, and more.

Example:
    guidelines = {
        'Style': 'Formal',
        'Format': 'Essay',
        'Audience Awareness': 'Academic Readers'
    }
    constraints = {
        'Length Constraints': '1000 words',
        'Content Restrictions': 'Exclude slang or colloquial language'
    }

    section_prompt = Prompt({
            'directives': {'Instruction': 'Write an introduction to the topic of artificial intelligence.'},
            'guidelines': guidelines,
            'constraints': constraints
        }
    )

Access prompt engineering help and tips from the class variables:

Prompt.
    directives
    guidelines
    constraints
    roles
    styles
    formats
    contexts
    audience
    structure
    tone_and_voice

Schema: {key:str -> value:str (may be a semicolon separated list)}
"""


class Prompt(dict):
    """
    The Prompt class is designed to encapsulate directives, guidelines, and constraints for guiding a large language model's response.

    Example:
        guidelines = {
            'Style': 'Formal',
            'Format': 'Essay',
            'Audience Awareness': 'Academic Readers'
        }
        constraints = {
            'Length Constraints': '1000 words',
            'Content Restrictions': 'Exclude slang or colloquial language'
        }

        section_prompt = Prompt({
                'directives': {'Instruction': 'Write an introduction to the topic of artificial intelligence.'},
                'guidelines': guidelines,
                'constraints': constraints
            }
        )

    Access prompt engineering help and tips from the class variables:

    Prompt.
        directives
        guidelines
        constraints
        roles
        styles
        formats
        contexts
        audience
        structure
        tone_and_voice

    Schema: {key:str -> value:str (may be a semicolon separated list)}
    """

    directives = """
## Example Directives (Keys and contents may vary)

#### Clarity and Explicitness
- **Be More Explicit**: "Explicitly state your assumptions."
- **Specify the Format**: "Present the answer as a bullet-point list."
- **Prioritize Important Information**: "Place the most important points first."
- **Limit the Response Length**: "Keep the response under 200 words."
- **Adjust the Level of Detail**: "Give a high-level overview."
- **Set a Time Constraint**: "Complete within 2 minutes."

#### Experimentation and Iteration
- **Experiment with Phrasing**: "Try two different ways of presenting the same point."
- **Iterate and Refine**: "Revise for clarity and conciseness."
- **Iterate on User Inputs**: "Incorporate user feedback."
- **Enhance the Prompt**: "Add clarifying details to the original question."

#### Step-by-Step and Sequential
- **Think Step-by-Step**: "Outline your thought process."
- **Use a Step-by-Step Approach**: "Explain each step in solving the equation."
- **Break Down Complex Questions**: "Address each part of the question separately."
- **Prompt Hierarchy**: "Start with a main question, followed by sub-questions."

#### System Awareness and Self-Evaluation
- **Critical Reflection**: "Point out the limitations of your response."
- **Encourage Self-Evaluation**: "Rate the quality of your response."
- **Feedback Solicitation**: "Ask for user feedback."
- **Self-Assessment**: "Indicate confidence level in your answer."
- **Self-Questioning**: "Pose questions to check your own assumptions."

#### Sources, Citations, Fact-Checking
- **Request Sources or Citations**: "Cite supporting data."
- **Fact-Checking**: "Verify the dates mentioned."
- **Cross-Referencing**: "Cross-check facts with multiple sources."
- **Employ Socratic Questioning**: "Question the underlying assumptions."

#### Analysis, Evaluation, Alternative Perspectives
- **Request Pros and Cons**: "List pros and cons."
- **Encourage Evaluation and Analysis**: "Compare two options critically."
- **Request Alternative Perspectives**: "Include minority viewpoints."
- **Elicit Opinions or Interpretations**: "Give your own interpretation of the data."

#### Examples, Templates, Analogies
- **Incorporate Positive or Negative Examples**: "Use case studies as examples."
- **Utilize Templates and Placeholders**: "Follow the essay template provided."
- **Use Fill-in-the-Blank Prompts**: "Complete the sentence: 'The main point is...'"
- **Leverage Analogies or Comparisons**: "Explain the concept using an analogy."

#### Guided Dialogue, Conditional Branching, Creativity
- **Create a Guided Dialogue**: "Structure as a Q&A session."
- **Employ Conditional Branching**: "If X, then discuss Y; otherwise, discuss Z."
- **Combine Multiple Strategies**: "Use analogies and examples."
- **Encourage Creativity and Storytelling**: "Use a narrative structure."

#### Context, Background Information, Role-Playing
- **Provide Context**: "Set the historical or social context."
- **Supply Background Information**: "Explain key terms."
- **Role-Play**: "Write as if you are a historical figure."
- **Adopt Different Perspectives**: "Switch between multiple viewpoints."

#### Advanced Strategies
- **Emotional and Empathetic Responses**: "Acknowledge the user's feelings."
- **Counterfactual and Speculative Thinking**: "Discuss what could have happened."
- **Framing and Reframing**: "Present the issue from another angle."
- **Multiple Intelligences and Learning Styles**: "Include both textual and visual explanations."

#### Metacognition, Visualization, Rhetorical Techniques
- **Metacognition and Self-Reflection**: "Reflect on your thought process."
- **Visualization and Imagery**: "Describe in vivid detail."
- **Paraphrasing and Summarizing**: "Rephrase key points."
- **Probing Assumptions and Challenging Bias**: "Question your own biases."

#### Historical Context, Cross-Disciplinary Perspectives, Contingency Plans
- **Historical Context and Connections**: "Relate to past events."
- **Analogies and Transfer of Learning**: "Draw parallels to different fields."
- **Cross-Disciplinary Perspectives**: "Include insights from sociology in a tech discussion."
- **Contingency Plans and Risk Assessment**: "Outline potential risks and mitigation strategies."

#### Synthesis, Integration, Iterative Templates
- **Synthesis and Integration**: "Combine insights from multiple sources."
- **Rhetorical Techniques and Persuasive Arguments**: "Use ethos, logos, and pathos."
- **Use Iterative Templates**: "Reuse successful structures."
- **Combine Templates with List-Based Prompts**: "Mix and match multiple formats."
"""

    guidelines = """
## Example Guidelines (Keys and contents may vary)

### Role
- **Persona**:
  - "Journalist"
  - "High School Teacher"
  - "Customer Service Agent"
  - "Financial Advisor"
- **Scenario**:
  - "Job Interview"
  - "Product Review"
  - "Historical Reenactment"
  - "Provide Historical Context"

### Style
- **Language or Tone**:
  - "Formal"
  - "Sarcastic"
  - "Inspirational"
  - "Be More Explicit"
- **Vocabulary**:
  - "Technical"
  - "Simple"
  - "Slang"
  - "Limit Response Length"
  - "Adjust the Level of Detail"

### Format
- **Structure or Layout**:
  - "Listicle"
  - "Q&A"
  - "Dialogue"
  - "Specify the Format"
  - "Create a Guided Dialogue"
- **Paragraph Length**:
  - "Short Paragraphs"
  - "One-Sentence Paragraphs"
  - "Long, Detailed Paragraphs"
  - "Break Down Complex Questions"
  - "Prioritize Important Information"

### Context
- **Background Information**:
  - "Include Historical Context"
  - "State the Problem First"
  - "Supply Background Information"
  - "Set a Time Constraint"
- **Setting**:
  - "Office Environment"
  - "Outdoor Adventure"
  - "Virtual Space"
  - "Role-Play"
  - "Adopt Different Perspectives"

### N-Shot Learning
- **Examples**:
  - "Similar to Hemingway's Style"
  - "As in Scientific Journals"
  - "Like a TED Talk"
  - "Incorporate Positive or Negative Examples"
  - "Leverage Analogies or Comparisons"

### Audience Awareness
- **Demographic**:
  - "Teenagers"
  - "Professionals"
  - "Global Audience"
  - "Emotional and Empathetic Responses"
  - "Multiple Intelligences and Learning Styles"
- **Knowledge Level**:
  - "Beginner"
  - "Intermediate"
  - "Expert"
  - "Use Iterative Templates"
  - "Combine Templates with List-Based Prompts"
"""

    constraints = """
## Example Constraints (Keys and contents may vary)

### Length Constraints
- **Word Limit**:
  - "At least 150"
  - "2000-2500"
  - "Maximum 1000 words"
- **Character Limit**:
  - "300 at minimum"
  - "1000-1250"
  - "Not exceeding 4000 characters"

### Content Restrictions
- **Disallowed Phrases**:
  - "Limited Time Offer;Buy Now"
  - "As Everyone Knows"
  - "In Conclusion"
- **Taboo Elements**:
  - "Hate Speech;Discrimination"
  - "Explicit Material"
  - "Financial Advice"

### Ethical Constraints
- **Privacy**:
  - "No Personal Anecdotes"
  - "No Contact Information"
- **Bias**:
  - "Non-Partisan"
  - "No Endorsements"
  - "Equitable Representation"

### Legal or Regulatory Constraints
- **Citations**:
  - "MLA Style"
  - "Government Publications Only"
  - "No User-Generated Content"
- **Compliance**:
  - "ADA Compliant"
  - "Fair Use Guidelines"
  - "GDPR Compliant"

### Domain-Specific Constraints
- **Technical Accuracy**:
  - "Validated Models Only"
  - "Latest Research"
  - "Statistical Significance"
- **Jargon**:
  - "Plain Language"
  - "No Business Buzzwords"
  - "No Medical Abbreviations"
- **Restrited Sources**:
  - "Wikipedia"
  - "Blog posts"

### Language Constraints
- **Language/Dialect**:
  - "Australian English"
  - "European Portuguese"
  - "Mandarin Chinese"

### Sensitivity Constraints
- **Offensive Content**:
  - "No Religious Symbols"
  - "No Cultural Stereotypes"
  - "Avoid Sensitive Topics"
"""

    roles = """
## Example Roles

- **Narrator**:
  - Provides a balanced and comprehensive look at the topic from a third-person perspective.

- **Expert**:
  - Delves into technical details and offers expert opinions, writing from a position of authority.

- **Educator**:
  - Explains complex concepts in an easy-to-understand manner, targeting readers new to the subject.

- **Historian**:
  - Focuses on the historical context and evolution of the topic, detailing key milestones and figures.

- **Journalist**:
  - Adopts a news-style format, potentially incorporating interviews, quotes, and multiple viewpoints.

- **Advocate**:
  - Writes from a committed standpoint, advocating for specific theories, applications, or ethical considerations.

- **Storyteller**:
  - Weaves the information into a narrative, possibly using anecdotes or hypothetical scenarios to illustrate points.

- **Reviewer**:
  - Critically assesses various theories, experiments, or applications, providing pros and cons.

- **Guide**:
  - Takes the reader on a journey through the topic, asking questions and exploring answers along the way.
"""

    styles = """
### Example Styles

- **Academic**:
  - Utilizes scholarly language and citations, aiming for high rigor and detail. Suitable for academic journals.

- **Informative**:
  - Provides straightforward and factual information, aiming to educate without embellishments.

- **Engaging**:
  - Merges factual content with compelling narrative or storytelling elements to maintain reader interest.

- **Conversational**:
  - Adopts a friendly and approachable tone, as if speaking directly to the reader.

- **Formal**:
  - Adheres to strict grammatical rules and avoids colloquialisms, aiming for a professional and authoritative tone.

- **Analytical**:
  - Breaks down complex topics into understandable parts, often leveraging data and logical reasoning.

- **Persuasive**:
  - Aims to convince the reader of a particular viewpoint, using rhetorical devices like ethos, pathos, and logos.

- **Expository**:
  - Explains the topic in a straightforward manner, often using examples or definitions for clarification.

- **Descriptive**:
  - Utilizes vivid language and details to evoke emotions or deepen understanding, painting a picture of the topic.

- **Journalistic**:
  - Employs the "inverted pyramid" structure, presenting crucial information first before delving into details.

- **Creative Non-Fiction**:
  - Combines factual information with creative writing techniques, such as metaphor, simile, and personification, to enhance engagement.
"""

    formats = """
### Example Formats

- **Essay**:
  - A traditional academic format with an introduction, body, and conclusion. Suitable for in-depth exploration.

- **Article**:
  - Similar to an essay but more focused and often shorter. Common in magazines, journals, or online platforms.

- **Report**:
  - Structured document presenting information in organized sections, such as abstract, methodology, findings, and conclusion.

- **Review**:
  - Offers a critical assessment of theories, experiments, or applications, often including summary, evaluation, and recommendation.

- **Tutorial**:
  - Step-by-step guide aimed at breaking down complex concepts or procedures in an easy-to-follow manner.

- **Q&A**:
  - Presents content in a question-and-answer format, making complex topics more accessible.

- **Case Study**:
  - Focuses on a specific event, experiment, or application to provide in-depth insights.

- **Listicle**:
  - Organizes information in a list format, often for lighter content or to present multiple viewpoints or tips.

- **Op-Ed**:
  - Opinion piece that presents a strong viewpoint, backed by facts and arguments.

- **Interview**:
  - A transcript or summary of an interview with an expert or key figure in the field.

- **Narrative**:
  - Tells a story or describes a journey through the topic, often using anecdotes or hypothetical scenarios.

- **Explainer**:
  - Clarifies complex topics or concepts, often using visuals, examples, or analogies.

- **Infographic**:
  - Presents information visually, often with accompanying text to explain key concepts or data.

- **Multimedia**:
  - Incorporates multiple forms of media, such as text, images, and videos, to offer a comprehensive view of the topic.
"""

    contexts = """
### Example Contexts

- **Academic Research**:
  - Focuses on scholarly rigor, including citations, references, and a literature review.

- **Educational**:
  - Tailored for learning environments like classrooms, breaking down complex topics into digestible pieces.

- **Popular Science**:
  - Simplifies scientific topics for a general audience, highlighting relevance to everyday life.

- **Historical**:
  - Offers a historical perspective, detailing key milestones, figures, and breakthroughs in the field.

- **Technical**:
  - Targets professionals, focusing on technical aspects, equations, and methodologies.

- **Policy and Ethics**:
  - Discusses implications on public policy, ethical considerations, and societal impact.

- **Industry Application**:
  - Focuses on field applications in industries like energy, medicine, or technology.

- **Public Awareness**:
  - Aims to educate the public on importance, risks, and benefits, often with a call to action.

- **Global Perspective**:
  - Addresses the topic in the context of global issues like international collaborations and climate change.

- **Cultural**:
  - Explores the influence on culture, art, or philosophy, offering a humanistic perspective.

- **Futuristic**:
  - Looks at future applications and implications, including upcoming research and potential breakthroughs.

- **Interdisciplinary**:
  - Merges insights from other fields like biology or social sciences for a more holistic view.
"""

    audience = """
### Example Audiences

- **General Public**:
  - Content is accessible, avoids jargon, and focuses on broad concepts appealing to the average reader.

- **Students**:
  - Aimed at educational settings, focusing on foundational concepts and learning objectives.

- **Academics and Researchers**:
  - Targets a scholarly audience, including technical details, citations, and advanced theories.

- **Industry Professionals**:
  - Geared towards professionals in applicable fields, focusing on practical applications and challenges.

- **Policy Makers**:
  - Centers on implications for public policy, including ethical considerations and societal impact.

- **Enthusiasts**:
  - For readers with a strong but non-professional interest, balancing depth with accessibility.

- **Interdisciplinary Audience**:
  - Appeals to professionals and enthusiasts from various fields, highlighting broader implications.

- **Global Audience**:
  - Addresses issues with international relevance, suitable for a geographically diverse readership.

- **Children and Young Adults**:
  - Simplifies content and may include engaging elements like stories or illustrations.

- **Specialized Groups**:
  - Tailored for specific communities, focusing on aspects most relevant to them, such as environmentalism or ethics.
"""

    structure = """
### Example Structures

- **Chronological**:
  - Organizes content based on the timeline of developments, from early theories to modern applications.

- **Thematic**:
  - Divides content into themes or categories, such as key theories, notable scientists, and practical applications.

- **Problem-Solution**:
  - Presents a problem or challenge and then discusses solutions or advancements.

- **Cause and Effect**:
  - Explores causes behind key discoveries or theories and their subsequent effects on science and society.

- **Comparative**:
  - Compares and contrasts different theories, methodologies, or applications.

- **Hierarchical**:
  - Starts with broad concepts and narrows down to specifics, or vice versa.

- **Sequential**:
  - Follows a step-by-step approach, useful for tutorials or guides.

- **Spatial**:
  - Organizes content based on spatial relationships, such as atomic structure or facility layout.

- **Pros and Cons**:
  - Discusses advantages and disadvantages of theories, applications, or ethical considerations.

- **FAQ Format**:
  - Organizes as a series of questions and answers for easy information retrieval.

- **Case Study Approach**:
  - Focuses on specific examples or case studies to illustrate broader concepts.

- **Narrative Structure**:
  - Weaves information into a story or journey for more engaging reader experience.

- **Modular**:
  - Breaks content into standalone modules that contribute to an overall understanding.

- **Interactive**:
  - Incorporates elements like quizzes or interactive diagrams to actively engage the reader.
"""

    tone_and_voice = """
### Example Tones and Voices

- **Authoritative**:
  - Conveys expertise and credibility, often using technical language and citing reputable sources.

- **Conversational**:
  - Engages the reader as if in a dialogue, using a friendly and approachable tone.

- **Formal**:
  - Adheres to strict grammatical rules, avoiding colloquialisms for a professional tone.

- **Informal**:
  - Uses a relaxed style, possibly including humor or colloquial language.

- **Inspirational**:
  - Aims to motivate or inspire, often using uplifting language and focusing on positive aspects.

- **Objective**:
  - Maintains a neutral tone, presenting facts and arguments without showing bias.

- **Persuasive**:
  - Aims to convince the reader using rhetorical devices and strong arguments.

- **Reflective**:
  - Encourages deep thinking about the topic, often posing questions or scenarios.

- **Skeptical**:
  - Questions established theories, encouraging critical thinking and debate.

- **Whimsical**:
  - Uses playful or imaginative language, often suitable for a younger audience or creative pieces.

- **Didactic**:
  - Educational, aiming to instruct the reader, often used in tutorials or guides.

- **Empathetic**:
  - Shows understanding for the reader's feelings, aiming to connect emotionally.

- **Analytical**:
  - Breaks down complex topics into understandable parts, using data and logical reasoning.

- **Storytelling**:
  - Uses narrative elements to weave information into a compelling story.
"""

    def __init__(self, data={}):
        """
        Initializes the Prompt class with directives, guidelines, and constraints in data dictionary.

        Parameters:
            data (dict): The core instruction that guides the language model's response.
                directives (dict): See more Prompt.directives
                guidelines (dict):  See more Prompt.guidelines
                constraints (dict): See more Prompt.constraints

        Example:
            guidelines = {
                'Style': 'Formal',
                'Format': 'Essay',
                'Audience Awareness': 'Academic Readers'
            }
            constraints = {
                'Length Constraints': '1000 words',
                'Content Restrictions': 'Exclude slang or colloquial language'
            }

            section_prompt = Prompt({
                    'directives': {'Instruction': 'Write an introduction to the topic of artificial intelligence.'},
                    'guidelines': guidelines,
                    'constraints': constraints
                }
            )

        Access prompt engineering help and tips from the class variables:

        Prompt.
            directives
            guidelines
            constraints
            roles
            styles
            formats
            contexts
            audience
            structure
            tone_and_voice

        Prompt.variable schema: {key:str -> value:str (may be a semicolon separated list)}
        """
        attributes_to_update = ['directives', 'guidelines', 'constraints']
        for attr in attributes_to_update:
            self.update({attr: data.get(attr, {})})
        # Other keys are left out

    def __repr__(self):
        return f"Prompt(directives={self.get('directives', {})}, guidelines={self.get('guidelines', {})}, constraints={self.get('constraints', {})})"

    def __str__(self):
        return f"Prompt(directives: {self.get('directives', {})}, guidelines: {self.get('guidelines', {})}, constraints: {self.get('constraints', {})})"
