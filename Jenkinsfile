pipeline {
    agent any

    triggers {
        githubPush()
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Test') {
            steps {
                bat '''
                    set SECRET_KEY=dev-secret-key-12345
                    set JWT_SECRET_KEY=dev-secret-key-12345

                    "C:\\Users\\mayur\\AppData\\Local\\Programs\\Python\\Python312\\python.exe" --version
                    "C:\\Users\\mayur\\AppData\\Local\\Programs\\Python\\Python312\\python.exe" -m pip install -r requirements.txt
                    "C:\\Users\\mayur\\AppData\\Local\\Programs\\Python\\Python312\\python.exe" -m pytest
                '''
            }
        }

        stage('SonarQube Analysis') {
            steps {
                script {
                    def scannerHome = tool 'sonarscanner'

                    withSonarQubeEnv('SonarQube') {
                        bat "\"${scannerHome}\\bin\\sonar-scanner.bat\""
                    }
                }
            }
        }

        stage('Quality Gate') {
            steps {
                timeout(time: 2, unit: 'MINUTES') {
                    waitForQualityGate abortPipeline: true
                }
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

    post {
        success {
            emailext(
                subject: "SUCCESS ${env.JOB_NAME} #${env.BUILD_NUMBER}",
                body: """
                    <h2>Jenkins build Successful</h2>
                    <p>
                        <b>URL</b>: ${env.BUILD_URL}
                    </p>
                """,
                to: "arulanandha.guru@revature.com"
            )
        }

        failure {
            emailext(
                subject: "FAILED ${env.JOB_NAME} #${env.BUILD_NUMBER}",
                body: """
                    <h2>Jenkins build Failed</h2>
                    <p>
                        <b>URL</b>: ${env.BUILD_URL}
                    </p>
                """,
                to: "mayurnaik208@gmail.com"
            )
        }
    }
}