from src import create_app

app = create_app()

if __name__ == "__main__":
    # app.run(debug=True) # debug=True é útil para desenvolvimento
    app.run(host="0.0.0.0", port=5000, debug=True) # Executa em 0.0.0.0 para ser acessível

