from flaskblog import create_app, generate_json_file, check_json_file

app = create_app()
generate_json_file()
check_json_file()

if __name__ == '__main__':
    app.run(debug=True)

