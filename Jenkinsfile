pipeline {

    agent any

    stages {

        stage('Checkout') {
            steps {
                echo 'Repository checkout completed'
            }
        }

        stage('Verify Environment') {
            steps {
                sh '''
                pwd
                ls -la
                python3 --version
                '''
            }
        }

    }

}