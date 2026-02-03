from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI(title="KitchAI")

@app.get("/", response_class=HTMLResponse)
def kitchai():
    return """
    <html>
        <head>
            <title>KitchAI</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    background: linear-gradient(135deg, #1e1e2f, #2b5876);
                    color: white;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    margin: 0;
                }
                .box {
                    text-align: center;
                    padding: 40px;
                    border-radius: 15px;
                    background: rgba(255, 255, 255, 0.1);
                    box-shadow: 0 0 20px rgba(0,0,0,0.4);
                }
                h1 {
                    font-size: 3em;
                }
                p {
                    font-size: 1.2em;
                }
            </style>
        </head>
        <body>
            <div class="box">
                <h1>KitchAI</h1>
                <p>La forma inteligente de gestionar tu restaurante.</p>
                <p>Powered by FastAPI</p>
            </div>
        </body>
    </html>
    """
