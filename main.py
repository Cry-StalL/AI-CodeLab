from fastapi import FastAPI
from utils.models import CodeRequest
from utils import code_executors

app = FastAPI()

@app.post("/run_code/")
async def run_code(request: CodeRequest):
    language = request.language
    code = request.code

    if language == "Python":
        return code_executors.run_python(code)
    elif language == "C++":
        return code_executors.run_cpp(code)
    elif language == "C":
        return code_executors.run_c(code)
    elif language == "Java":
        return code_executors.run_java(code)
    elif language == "Rust":
        return code_executors.run_rust(code)
    elif language == "Go":
        return code_executors.run_go(code)
    else:
        return {"error": f"Unsupported language: {language}"}
