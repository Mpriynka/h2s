# core/document_generator.py
from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

# Initialize the LLM
def get_llm():
    """Get LLM instance with Ollama"""
    try:
        from langchain_ollama import OllamaLLM
        return OllamaLLM(model="llama2")
    except ImportError:
        # Fallback for compatibility
        from langchain_community.llms import Ollama
        return Ollama(model="llama2")

def generate_document_content(template, language, formality, details):
    """Generate document content based on template and details"""
    # Initialize LLM
    llm = get_llm()

    # Prepare the prompt template
    prompt_template = PromptTemplate(
        template=template["prompt_template"],
        input_variables=["formality", "language"] + [field["name"] for field in template["required_fields"]]
    )

    # Prepare inputs for the prompt
    prompt_inputs = {
        "formality": formality,
        "language": language,
        **details
    }

    # Create and run the chain
    chain = LLMChain(llm=llm, prompt=prompt_template)

    # Generate content
    result = chain.run(**prompt_inputs)

    return result