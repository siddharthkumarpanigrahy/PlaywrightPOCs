
pipeline {
    agent any

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
            choices[
OTC_GUI',
MC_GUI',
ALL'
: 'Select          'SECURITY',
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

        // Optional browser setting if your common.browser reads this
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
                    python3 -m pip install playwright

                    # Install Chromium browser for Playwright.
                    # If your Jenkins agent already has browser binaries,
                    # this command is still safe.
                    python3 -m playwright install chromium
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
                    echo "Running OTCT-7968 Test Runner"
                    echo "APPLICATION=${APPLICATION}"
                    echo "PACK=${PACK}"
                    echo "TEST_ID=${TEST_ID}"
                    echo "======================================"

                    export APPLICATION="${APPLICATION}"
                    export PACK="${PACK}"
                    export TEST_ID="${TEST_ID}"

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
        }

        success {
            echo 'OTCT-7968 Jenkins execution completed successfully.'
        }

        failure {
            echo 'OTCT-7968 Jenkins execution failed. Check console logs and archived screenshots.'
        }

        cleanup {
            echo 'Pipeline cleanup completed.'
        }
    }
}