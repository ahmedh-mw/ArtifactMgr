# Classic pipeline files propagation
Propagate all pipeline artifacts between jobs

## Job names
- Job names must not contain any special characters as they will be used as the pipeline job names and artficatory folder names so it should be acceptable Windows folder's path and Linux folder's path
- It is recommended that Job names be short

## Branching logic
- Branch name is named as the first job on the branch (Start job branch name is always the same as the job name)
- Every job must has a branch name
- Branch has one or more sequential jobs
- Each branch has its own individual artifacts folder
- **Sequential jobs case:** Sequential jobs use the same branch hence the same artifacts folder
- **Parallel jobs splitting case:** When any job splits into multiple parallel jobs, each of these jobs will initiates its own separate branch.
- **Parallel jobs merging case:** If two or more parallel jobs (i.e. parallel branches) merge into a single job, this merged job will initiates a new separate branch
> - ***Job at the middle or the end of the branch:*** The branch name is the same as the predecessor job branch name
>   - When the job has only one predecessor job and the predecessor job has only one successor job
> - ***First Job on the branch***: The branch name is the same as the job name
>   - First job after merging (has more than one predecessor jobs)
>   - Start job (has no predecessor jobs)

## Start activities logic
- **Parallel jobs case:** If 'Start' activity is followed by multiple parallel jobs, 'Start' activity is executed in a seperate job:
    1. ***[Start Activity]*** Download 'End' artifacts (branch name stored in 'downloadBranch' field) from the previous run if incremental option is enabled
    1. ***[Start Activity]*** Open the project and update the artifacts.
    1. ***[Start Activity]*** Upload the artifacts to the 'Start' branch's folder.

- **Sequential jobs case:** If 'Start' activity is followed by single sequential job, 'Start' activity is executed as part of this job: 
    1. ***[Start Activity]*** Download 'End' artifacts (branch name stored in 'downloadBranch' field) from the previous run if incremental option is enabled
    1. ***[Job]*** Open the project and execute tasks.
    1. ***[Job]*** Upload the artifacts to the 'Start' branch's folder.
- 'Start' job always has 'flow_predecessor_jobs' equal null and it is the only job that allowed to have 'flow_predecessor_jobs' equal to null
- All other jobs must have 'flow_predecessor_jobs' not equal null, because this field describe the pipeline flow and all jobs must have at least one predecessor job.

## Download activity logic
There are three sub activities :
#### 1. Download:
> - 'Start' job: 
>    - download only the 'End' job branch folder from the last succssful run
>    - No merging will be required in this case
> - All other jobs:
>    - download all input branches, input branches are the branches of all
>    - predecessor jobs (using 'flow_predecessor_jobs' field)
#### 2. Merge:    
> - Merge downloaded branches into a single current job branch if there are more than one branch downloaded

#### 3. Move to project:
> - Move the single downloaded branch or the merged one to the project folder


## Merging logic (Artifacts and DMRs)
- Merging happens only when multiple branches merges into one single branch
- 

## Uploading activity logic
- If the job is on the same branch as the previous job, it will upload the job output folders only
- If the job is initiating a new branch, it will upload all pipeline output folders. This case includes 'Start' job.
- Upload all artifacts of pipeline out directories
- Move all out folders of the pipeline to the '\_uploads_' folder
- Upload '\_uploads_' folder

## End activities logic
- All pipelines must have one and only one 'End' activities at the last job of the pipeline
- **Parallel jobs ending case:** If 'End' activities are preceded by multiple parallel jobs, 'End' activity is executed in a seperate job:
    1. Download all predecessor jobs' branches and merge them
    1. Generate Final Report if required.
    1. Upload the pipeline artifacts to artifactory if incremental option is enabled.
    1. Upload the pipeline artifacts to CI platform if required.
- **Sequential jobs ending case:** If 'End' activities are preceded by a single sequential job, 'End' activity is executed as part of this job:
    1. [Job] Open the project and execute tasks.
    1. [End Activities] Generate Final Report if required.
    1. [End Activities] Upload the pipeline artifacts to artifactory 'End' branch if incremental option is enabled.
    1. [End Activities] Upload the pipeline artifacts to CI platform if required.
- All non merged/terminated jobs will implicitly flow to the 'End' job
- End job must not have any successor jobs: can not be added to 'flow_predecessor_jobs' field of any other jobs

---
# ***Examples:***
## 1. Single Stage example
- JOB1: All activities
    - Download using 'downloadBranch' field from the previous pipeline run
    - Tasks Execution
    - Generate Final Report if GenerateReport is enabled
    - Upload using 'branchName' field
    - Upload to CI platform if EnableArtifactCollection is enabled

## 2. Serial Stages example
- JOB1: Start Job
    - Download using 'downloadBranch' field from the previous pipeline run
    - Tasks Execution
    - Upload using 'branchName' field
- JOBx: Normal Job
    - Download using job 'branchName' field of the job at flow_predecessor_jobs
    - Tasks Execution
    - Upload using 'branchName' field
- JOBn: End Job
    - Download using job 'branchName' field of the job at flow_predecessor_jobs
    - Tasks Execution
    - Generate Final Report if GenerateReport is enabled
    - Upload using 'branchName' field
    - Upload to CI platform if EnableArtifactCollection is enabled