pipeline {
    agent {
        label 'otc-smoke2-primary_otcci'
    }

    options {
        timestamps()
        ansiColor('xterm')
        buildDiscarder(
            logRotator(
                numToKeepStr: '20',
                artifactNumToKeepStr: '20'
            )
        )
    }

    parameters {
        choice(
            name: 'APPLICATION',
            choices: [
                'OTC_GUI',
                'MC_GUI',
                'ALL'
            ],
            description: 'Select application test suite'
        )

        choice(
            name: 'PACK',
            choices: [
                'SMOKE',
                'SECURITY',
                'ALL'
            ],
            description: 'Select test pack'
        )

        string(
            name: 'TEST_ID',
            defaultValue: '',
            description: 'Optional specific test ID, for example OTCT-7968_TC_004'
        )

        booleanParam(
            name: 'HEADLESS',
            defaultValue: true,
            description: 'Run browser in headless mode if supported by common.browser'
        )
    }

    environment {
        // Common network/proxy bypass
        NO_PROXY = '10.130.209.10'
        no_proxy = '10.130.209.10'

        // MC-GUI credentials
        MC_USERNAME = 'CBKFRCLR001'
        MC_PASSWORD = 'CBKFRCLR001'

        // Optional OTC-GUI / password reset users if needed
        PASSWORD_RESET_USERNAME = 'CBKFRCLR001'
        PASSWORD_RESET_PASSWORD = 'CBKFRCLR001'
        RESET_TARGET_USER = 'DBKFRCLR001'
        RESET_TARGET_USER_DIFFERENT_MEMBER = 'DBKFRCLR001'

        // Optional browser setting if common.browser reads this
        HEADLESS = "${params.HEADLESS}"
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Show Execution Context') {
            steps {
                sh '''
                    echo "======================================"
                    echo "Execution Context"
                    echo "======================================"
                    echo "APPLICATION=${APPLICATION}"
                    echo "PACK=${PACK}"
                    echo "TEST_ID=${TEST_ID}"
                    echo "HEADLESS=${HEADLESS}"
                    echo "WORKSPACE=${WORKSPACE}"
                    echo "Python:"
                    python3 --version
                    echo "======================================"
                '''
            }
        }

        stage('Install Dependencies') {
            steps {
                sh '''
                    set -e

                    python3 -m pip install --upgrade pip
                    pip3 install -r requirements.txt
                    playwright install firefox

                    # Install Chromium browser for Playwright.
                    # If your Jenkins agent already has browser binaries,
                    # this command is still safe.
                '''
            }
        }

        stage('Prepare Runtime Folders') {
            steps {
                sh '''
                    mkdir -p runtime
                    mkdir -p runtime/screenshots
                    mkdir -p runtime/logs
                    mkdir -p runtime/reports
                '''
            }
        }

        stage('Run Tests') {
            steps {
                sh '''
                    set -e

                    echo "======================================"
                    echo "Running Daily Playwright UI Test Runner"
                    echo "APPLICATION=${APPLICATION}"
                    echo "PACK=${PACK}"
                    echo "TEST_ID=${TEST_ID}"
                    echo "======================================"

                    export APPLICATION="${APPLICATION}"
                    export PACK="${PACK}"
                    export TEST_ID="${TEST_ID}"
                    export HEADLESS="${HEADLESS}"

                    python3 runner.py
                '''
            }
        }
    }

    post {
        always {
            echo 'Archiving runtime artifacts...'

            archiveArtifacts(
                artifacts: 'runtime/screenshots/**/*.png',
                allowEmptyArchive: true,
                fingerprint: true
            )

            archiveArtifacts(
                artifacts: 'runtime/logs/**/*.log',
                allowEmptyArchive: true,
                fingerprint: true
            )

            archiveArtifacts(
                artifacts: 'runtime/reports/**/*',
                allowEmptyArchive: true,
                fingerprint: true
            )

            archiveArtifacts(
                artifacts: 'test_data/**/*.csv',
                allowEmptyArchive: true,
                fingerprint: false
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

        success {
            echo 'Daily Playwright UI test execution completed successfully. Check console logs and archived screenshots for details.'
        }

        failure {
            echo 'Daily Playwright UI test execution failed. Check console logs and archived screenshots.'
        }

        cleanup {
            echo 'Pipeline cleanup completed.'
        }
    }
}