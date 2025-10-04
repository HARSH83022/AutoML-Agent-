from fastapi import FastAPI
from .agents import ps_agent, data_finder, synthetic, pipeline_agent

app = FastAPI(title="AutoML Agents")

# Register routers
app.include_router(ps_agent.router)
app.include_router(data_finder.router)
app.include_router(synthetic.router)
app.include_router(pipeline_agent.router) 

@app.get("/")
def root():
    return {"message": "🚀 AutoML Agents running!"}
