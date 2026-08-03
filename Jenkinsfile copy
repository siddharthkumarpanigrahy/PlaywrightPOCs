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

    post {

    always {

        archiveArtifacts(
            artifacts: '*.txt,*.png',
            fingerprint: true
        )

        emailext(
            subject: "OTC-GUI | Smoke Test | ${currentBuild.currentResult}",
            body: """
            OTC GUI Smoke Test Completed

            Result:
            ${currentBuild.currentResult}

            Build URL:
            ${env.BUILD_URL}
            """,
            attachmentsPattern: '*.txt,*.png',
            to: 'siddharth.panigrahy@deutsche-boerse.com'
        )
    }
}
}