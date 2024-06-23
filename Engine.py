import json
from openai import OpenAI
from jinja2 import Environment, FileSystemLoader

class Engine:
    def __init__(self):
        self.agent = OpenAI(base_url="http://localhost:11434/v1/", api_key="I heart Ollama")
    
    @staticmethod
    def remove_my_essay_prefix(s):
        prefix = "My essay:"
        if s.startswith(prefix):
            return s[len(prefix):].strip()
        return s
    
    def get_intro(self, keyword): 
        
        sys_prompt = "You are a robot specialized in creating the introduction sections for Wikipedia-style articles on hypothetical terms."
        sys_prompt += "For any given term, write a concise, informative introduction as if it's an Wikipedia entry."
        sys_prompt += "If you don't know the term, describe it as an everyday-thing from an alternate reality."
        sys_prompt += """Organize your response like {"Introduction": ""}, your output will be in JSON format and starts with {"""
        sys_prompt += "Avoid using apostrophe."
        sys_prompt += "Here are some example outputs:"
        
        output = self.agent.chat.completions.create(messages=[
            {
                "role": "system",
                "content": sys_prompt
            },
            {
                "role": "user",
                "content": keyword
            }],
            model="llama3",
            temperature = 0.5,
            max_tokens = 4096
            )
        
        temp = output.choices[0].message.content
        
        if not temp.endswith('}'): 
            temp += '}'

        intro = json.loads(temp)

        return(intro["Introduction"])
    
    def get_TOC(self, keyword, intro): 
        
        sys_prompt = "Your are a robot specialized in creating table of content for wikipedia-style articles."
        sys_prompt += "You will be given a term and an introduction paragraph of it."
        sys_prompt += "Come up with couple interesting aspects of this term based on the given information in addition to your knowledge."
        sys_prompt += """ Organize your response like {1: "", 2: "", 3: "", 4: ""}, and this is all you will respond with """
        sys_prompt += "Here are some example outputs:"
        sys_prompt += """ {1: "History", 2: "Geography", 3: "Economy"}, {1: "History", 2: "Cultural Significance", 3: "Controversy"} """
        
        output = self.agent.chat.completions.create(messages=[
            {
                "role": "system",
                "content": sys_prompt
            },
            {
                "role": "user",
                "content": f"Term: {keyword}, Introduction: {intro}"
            }],
            model="llama3",
            temperature = 0.5,
            max_tokens = 4096
            )
        
        TOC = output.choices[0].message.content
        
        # Step 1: Replace single quotes with double quotes
        json_compatible_string = TOC.replace("'", '"')
        
        # Step 2: Ensure keys are properly formatted as strings
        # Add double quotes around the keys (note: this example assumes keys are single digits)
        json_compatible_string = json_compatible_string.replace('{', '{"').replace(':', '":').replace(', ', ', "')

        dictionary = json.loads(json_compatible_string)
        
        return(dictionary)
    
    def get_content(self, keyword, intro, section): 
        
        sys_prompt = "Your are a robot specialized in creating sections of wikipedia-style articles."
        sys_prompt += "You will be given a term, an introduction paragraph, and the name of the section."
        sys_prompt += "Based on the introduction write the corresponding section of the article in couple paragraphs."
        sys_prompt += "You will make absurd claims, and try to promote the concept like an infomercial."
        sys_prompt += "Keep your sentences short." 
        sys_prompt += "Your output always starts with 'My essay:'" 

        
        output = self.agent.chat.completions.create(messages=[
            {
                "role": "system",
                "content": sys_prompt
            },
            {
                "role": "user",
                "content": f"Term: {keyword}, Introduction: {intro}, section: {section}"
            }],
            model="llama3",
            temperature = 1.5,
            max_tokens = 8000
            )
        
        content = output.choices[0].message.content
        
        return(content)
    
    def create_page(self, keyword):
        
        intro = self.get_intro(keyword)
        ToC = list(self.get_TOC(keyword, intro).values())
        content = []
        for section in ToC:
            section_i = self.get_content(keyword, intro, section)
            content.append(self.remove_my_essay_prefix(section_i).replace('\n', '<br>'))
            
        template_dir = 'templates/'
        env = Environment(loader=FileSystemLoader(template_dir))
        env.globals.update(zip=zip)
        template = env.get_template('template.html')

        rendered_html = template.render(intro = intro, title = keyword, TOC = ToC, sections = content)
        with open('templates/output/output.html', 'w', encoding='utf-8') as f:
            f.write(rendered_html)