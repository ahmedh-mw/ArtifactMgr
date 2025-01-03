def loadEnvVariables(){
    env.IS_UNIX = isUnix();
    env.SCRIPTS_LOCATION = "$SOURCECODE_FOLDER/pipelines/scripts"
    env.WORKSPACE_PATH_KEY = "WORKSPACE"
    if ("$IS_UNIX" == "true") {
        sh "$PYTHON_ALIAS $SCRIPTS_LOCATION/env_prepare.py --platform jenkins"
    } else {
        bat "$PYTHON_ALIAS $SCRIPTS_LOCATION/env_prepare.py --platform jenkins"
    }
    load "vars.groovy"
}

def addStage(jobName) {
    return {
        stage(jobName) {
            if("$RUNNER_TYPE" == "default"){
                node("$RUNNER_LABEL") {
                    skipDefaultCheckout()
                    cleanWs()
                    checkout scm
                    _getStageBody(jobName);
                }
            } else if ("$RUNNER_TYPE" == "container") {
                node("$RUNNER_LABEL") {
                    skipDefaultCheckout()
                    cleanWs()
                    checkout scm
                    docker.image("$IMAGE_TAG").inside ("$IMAGE_ARGS") {
                        _getStageBody(jobName);
                }}
            }
        }
    }
}

def addParallelStages(stageName, jobs) {
    return {
        stage(stageName){
            parallel(
                jobs
            )
        }
    }
}

def _getStageBody(jobName){
    def exception = null
    try {
        if ("$IS_UNIX" == "true") {
            sh "$PYTHON_ALIAS $SCRIPTS_LOCATION/job_prepare.py --jobname \"$jobName\""
            sh "$PYTHON_ALIAS $SCRIPTS_LOCATION/job_download.py --jobname \"$jobName\""
            if("$ENABLE_CI_DRYRUN" == "true"){
                sh "$PYTHON_ALIAS $SCRIPTS_LOCATION/job_dryrun.py --jobname \"$jobName\""
            } else {
                if ("$USE_MATLAB_PLUGIN" == "true" ) {
                    runMATLABCommand "matlab_job_commands"
                } else {
                    sh "./shell_commands.sh"
                }
            }
        } else {            
            bat "$PYTHON_ALIAS $SCRIPTS_LOCATION/job_prepare.py --jobname \"$jobName\""
            bat "$PYTHON_ALIAS $SCRIPTS_LOCATION/job_download.py --jobname \"$jobName\""
            if("$ENABLE_CI_DRYRUN" == "true"){
                bat "$PYTHON_ALIAS $SCRIPTS_LOCATION/job_dryrun.py --jobname \"$jobName\""
            } else {
                if ("$USE_MATLAB_PLUGIN" == "true" ) {
                    runMATLABCommand "addpath(fileparts(pwd));matlab_job_commands"
                } else {
                    bat ".\\shell_commands.bat"
                }
            }
        }
    } catch (InterruptedException e) {
        echo 'Task interrupted due to pipeline cancellation.'
        throw e
    } catch (e) {
        exception = e
    }
    
    errorDetected = exception? true : false
    if ("$IS_UNIX" == "true") {
        sh "$PYTHON_ALIAS $SCRIPTS_LOCATION/job_delta_upload.py --jobname \"$jobName\" --errordetected \"$errorDetected\""
    } else {
        bat "$PYTHON_ALIAS $SCRIPTS_LOCATION/job_delta_upload.py --jobname \"$jobName\" --errordetected \"$errorDetected\""
    }
    if (errorDetected) {
        if("$CONTINUE_ON_ERROR" == "true"){
            currentBuild.result = 'FAILURE'
            unstable('Job failed!')
        }else{
            throw exception
        }
    }
}

// Clear the upload download temp folders
// bat "if exist ${vars.UPLOAD_TEMP_LOCATION} ( rmdir /s /q ${vars.UPLOAD_TEMP_LOCATION} )"
// bat "if exist ${vars.DOWNLOAD_TEMP_LOCATION} ( rmdir /s /q ${vars.DOWNLOAD_TEMP_LOCATION} )"

// // Prepare the upload folder
// bat "mkdir ${vars.UPLOAD_TEMP_LOCATION}"
// bat "cp -r scm/ExampleArtifacts ${vars.UPLOAD_TEMP_LOCATION}"

// // $UPLOAD_TEMP_LOCATION  ============== ($ARTIFACTS_PATH) ================ $JFROG_FULL_PATH
// jf "rt u ${vars.UPLOAD_TEMP_LOCATION}/${vars.ARTIFACTS_PATH}/(*) ${vars.JFROG_FULL_PATH}/${vars.ARTIFACTS_PATH}/{1} --sync-deletes=${vars.JFROG_FULL_PATH}/${vars.ARTIFACTS_PATH}/"

// // $JFROG_FULL_PATH  ============== ($ARTIFACTS_PATH) ================> $DOWNLOAD_TEMP_LOCATION
// jf "rt dl ${vars.JFROG_FULL_PATH}/${vars.ARTIFACTS_PATH}/(*) ${vars.DOWNLOAD_TEMP_LOCATION}/${vars.ARTIFACTS_PATH}/{1} --sync-deletes=${vars.DOWNLOAD_TEMP_LOCATION}/${vars.ARTIFACTS_PATH}/" {% endcomment %}

return this