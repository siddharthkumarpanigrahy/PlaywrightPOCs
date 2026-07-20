pipeline {

    agent {
        label 'otc-smoke2-primary_otcci'
    }

    stages {

        stage('Install Dependencies') {
            steps {
                sh '''
                pip3 install -r requirements.txt
                playwright install firefox
                '''
            }
        }

        stage('Run Smoke Test') {
            steps {
                sh '''
                    HEADLESS=true python3 test.py
                '''
            }
        }
    }
}