
pipeline {
    agent any

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Test') {
            steps {
                bat '''
                    "C:\\Users\\mayur\\AppData\\Local\\Programs\\Python\\Python312\\python.exe" --version
                    "C:\\Users\\mayur\\AppData\\Local\\Programs\\Python\\Python312\\python.exe" -m pip install -r requirements.txt
                    "C:\\Users\\mayur\\AppData\\Local\\Programs\\Python\\Python312\\python.exe" -m pytest
                '''
            }
        }

        stage('Build Docker Image') {
            steps {
                bat '''
                    docker build -t mayurnaik208/expense-flask:latest .
                '''
            }
        }

        stage('Push to Docker Hub') {
            steps {
                withCredentials([
                    usernamePassword(
                        credentialsId: 'dockerhub-cred',
                        usernameVariable: 'DOCKER_USER',
                        passwordVariable: 'DOCKER_PASS'
                    )
                ]) {
                    bat '''
                        docker login -u %DOCKER_USER% -p %DOCKER_PASS%
                        docker push mayurnaik208/expense-flask:latest
                    '''
                }
            }
        }
    }
}

