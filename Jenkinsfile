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
    string(
        name: 'APPLICATION',
        defaultValue: 'ALL',
        description: 'Application(s): OTC_GUI, MC_GUI, or ALL. Multiple allowed: OTC_GUI,MC_GUI'
    )

    string(
        name: 'PACK',
        defaultValue: 'ALL',
        description: 'Pack(s): SMOKE, SECURITY, REGRESSION, or ALL. Multiple allowed: SMOKE,SECURITY'
    )

    string(
        name: 'TEST_ID',
        defaultValue: '',
        description: 'Optional test ID(s), comma-separated, e.g. OTCT-7968_TC_004,OTCT-7968_TC_005'
    )

    booleanParam(
        name: 'STOP_ON_FAIL',
        defaultValue: false,
        description: 'Stop execution after first failed test'
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

        // OTC-GUI credentials
        OTC_USERNAME = 'CBKFRCLR001'
        OTC_PASSWORD = 'CBKFRCLR001'
        OTC_GUI_URL = 'https://10.130.209.10:8443/OTC_GUI/App.html'

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
        STOP_ON_FAIL = "${params.STOP_ON_FAIL}"
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
                    rm -rf runtime/screenshots
                    rm -rf runtime/logs
                    rm -rf runtime/reports
                    rm -rf runtime/email_attachments

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
                    echo "STOP_ON_FAIL=${STOP_ON_FAIL}"
                    echo "HEADLESS=${HEADLESS}"
                    echo "======================================"

                    export APPLICATION="${APPLICATION}"
                    export PACK="${PACK}"
                    export TEST_ID="${TEST_ID}"
                    export STOP_ON_FAIL="${STOP_ON_FAIL}"
                    export HEADLESS="${HEADLESS}"

                    python3 runner.py
                '''
            }
        }
    }

post {
    always {
        echo 'Preparing zipped HTML report artifact...'

        sh '''
            mkdir -p runtime/email_attachments
            rm -f runtime/email_attachments/*

            if [ -f runtime/reports/screenshot_report.html ]; then
                zip -j runtime/email_attachments/screenshot_report.zip runtime/reports/screenshot_report.html
                echo "Created zipped screenshot report artifact"
            else
                echo "runtime/reports/screenshot_report.html not found. No report zip created."
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
            subject: "Playwright | Daily UI Automation Test Execution | ${currentBuild.currentResult}",
            body: """
Daily Playwright UI Automation Test Execution Completed

[ Result ] : ${currentBuild.currentResult}

[ Application(s) ] : ${params.APPLICATION}

[ Pack(s) ] : ${params.PACK}

[ Node ] : ${env.NODE_NAME}

[ Playwright Report ] : ${env.BUILD_URL}artifact/runtime/email_attachments/screenshot_report.zip




[Playwright Automation Runner © 2026]
            """,
            to: 'siddharth.panigrahy@deutsche-boerse.com'
        )
    }

    success {
        echo 'Daily Playwright UI test execution completed successfully. Check console logs and archived reports for details.'
    }

    failure {
        echo 'Daily Playwright UI test execution failed. Check console logs and archived reports.'
    }

    cleanup {
        echo 'Pipeline cleanup completed.'
    }
}
}