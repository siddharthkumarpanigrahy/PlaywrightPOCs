pipeline {

    agent {
        label 'otc-smoke2-primary_otcci'
    }

    stages {

        stage('Verify Environment') {
            steps {
                sh '''
                hostname
                whoami
                python3 --version
                '''
            }
        }

        stage('Install Dependencies') {
            steps {
                sh '''
                pip3 install -r requirements.txt
                '''
            }
        }

        stage('Run Smoke Test') {
            steps {
                sh '''
                python3 test.py
                '''
            }
        }
    }
}