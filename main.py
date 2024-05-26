"""
main.py
"""
import os
import json
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langchain.chains.question_answering import load_qa_chain
from preprocess import *

app = FastAPI()

load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")

def get_info(raw_html):
    texts = split_documents(str(raw_html))
    embeddings = initialize_embeddings()
    docsearch = create_vectorstore(texts, embeddings)
    chain = load_qa_chain(initialize_chat_model(api_key=groq_api_key), chain_type="stuff")
    query = """I have an HTML code snippet of a product page from an e-commerce website. 
    The snippet contains various attributes related to the product.
    Extract the meaningful attributes relevant to e-commerce contexts such as product names, prices, descriptions, and images. 
    Identify the CSS selectors or XPaths for each extracted attribute to pinpoint their location within the HTML structure.
    Return the output in JSON Format without giving any explanation.
    Do not say "Here is the extracted data in JSON format:"
    Extract the class and give the sutiable key names based on the class name. For the value of values, extract the value and create the suitable JSON format.
    For the css_selector, write the value as class name in the format ".class-name".
    For the xpath, write the value as class name in the format "//div[@class='product-name']".
    Generate the key-value pairs as much as the class. Do not creat own class name.
    
    Follow the examples given in the below.

### Example ###

Input HTML:
            <div class="product-name">Sample Product</div>
            <span class="product-price">$19.99</span>
            <div class="product-description">This is a sample product description.</div>
            <img class="product-image" src="sample-product.jpg" />


Output JSON:
{
    "product_name": {
        "value": "Sample Product",
        "css_selector": ".product-name",
        "xpath": "//div[@class='product-name']"
    },
    "price": {
        "value": "$19.99",
        "css_selector": ".product-price",
        "xpath": "//span[@class='product-price']"
    },
    "description": {
        "value": "This is a sample product description.",
        "css_selector": ".product-description",
        "xpath": "//div[@class='product-description']"
    },
    "image_url": {
        "value": "sample-product.jpg",
        "css_selector": ".product-image",
        "xpath": "//img[@class='product-image']/@src"
    }
}

HTML: {raw_html}

JSON:
"""
    docs = docsearch.similarity_search(query)
    answer = chain.run(input_documents=docs, question=query)
    try:
        answer_json = json.loads(answer)
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to decode JSON: {e}")
    
    return answer_json
    
@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/extract_info/")
def extract_info(request):
    try:
        extracted_info = get_info(request)
        return extracted_info
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
   get_info(
    """
     <div class="product-name">Addidas shoes</div>
            <span class="product-price">$100.99</span>
            <div class="product-description">This is a Addidas shoes.</div>
            <img class="product-image" src="sample-product.jpg" />

    """
    )
    