
pipeline {
    agent any

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Install Dependencies') {
            steps {
                bat 'pip install -r requirements.txt'
            }
        }

        stage('Test') {
            steps {
                bat 'pytest'
            }
        }

        stage('Build Docker Image') {
            steps {
                bat 'docker build -t mayurnaik208/expense-flask:latest .'
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
                        echo %DOCKER_PASS% | docker login -u %DOCKER_USER% --password-stdin
                        docker push mayurnaik208/expense-flask:latest
                    '''
                }
            }
        }
    }
}

