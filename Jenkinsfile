pipeline {

    agent {
        label 'otc-smoke2-primary_otcci'
    }

    stages {

        stage('Checkout') {
            steps {
                echo 'Repository checkout completed'
            }
        }

        stage('Verify Environment') {
            steps {
                sh '''
                hostname
                pwd
                ls -la
                python3 --version
                '''
            }
        }
    }
}