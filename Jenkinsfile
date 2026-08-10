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
                    # Install Firefox browser for Playwright.
                    # If your Jenkins agent already has browser binaries,
                    # this command is still safe.
                    playwright install firefox

                    
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
        echo 'Preparing single HTML screenshot report attachment...'

        sh '''
            mkdir -p runtime/email_attachments
            rm -f runtime/email_attachments/*

            if [ -f runtime/reports/screenshot_report.html ]; then
                cp runtime/reports/screenshot_report.html runtime/email_attachments/
                echo "Attached screenshot HTML report"
            else
                echo "screenshot_report.html not found. Selecting latest artifact instead."

                LATEST_FILE=$(find runtime/screenshots runtime/logs runtime/reports -type f \
                    \\( -name "*.png" -o -name "*.log" -o -name "*.txt" -o -name "*.json" -o -name "*.html" \\) \
                    -printf "%T@ %p\\n" 2>/dev/null \
                    | sort -nr \
                    | head -1 \
                    | cut -d " " -f2-)

                if [ -n "$LATEST_FILE" ]; then
                    echo "Latest attachment selected: $LATEST_FILE"
                    cp "$LATEST_FILE" runtime/email_attachments/
                else
                    echo "No artifact found for email attachment"
                fi
            fi

            ls -l runtime/email_attachments || true
        '''

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
            artifacts: 'runtime/email_attachments/*',
            allowEmptyArchive: true,
            fingerprint: true
        )

        emailext(
            subject: "Playwright | Daily UI Test Execution | ${currentBuild.currentResult}",
            body: """
Daily Playwright UI Test Execution Completed

Result:
${currentBuild.currentResult}

Application:
${params.APPLICATION}

Pack:
${params.PACK}

Test ID:
${params.TEST_ID}

Node:
${env.NODE_NAME}

Build URL:
${env.BUILD_URL}
            """,
            attachmentsPattern: 'runtime/email_attachments/*',
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