function generate_jenkins_pipeline_subfolder()
    % ************** 1
    % cp = openProject('scm');
    % cp = openProject('scm');
    % cp = openProject(pwd);
    cp = openProject(pwd);

    op = padv.pipeline.JenkinsOptions;
    % op.PipelineArchitecture = "IndependentModelParallelJobs"; # SingleJob, SerialJobs, SerialJobsGroupPerTask
    op.PipelineArchitecture = "IndependentModelParallelJobs";

    % ************** 2
    % op.MatlabInstallationLocation = "G:/86/ahmedh.Bslcicd.j2884790.10/matlab/bin";
    % op.MatlabInstallationLocation = "D:/sb/Bslcicd_0209/matlab";
    % op.MatlabInstallationLocation = "D:/sb/Bslcicd_0225/matlab/bin";
    op.MatlabInstallationLocation = "/mathworks/devel/sbs/86/ahmedh.Bslcicd.j2896530";

    % ************** 3
    % op.GeneratedPipelineDirectory = "";
    % op.GeneratedPipelineDirectory = "";
    %op.GeneratedPipelineDirectory = "scm";
    op.GeneratedPipelineDirectory = "scm";
    % op.AgentLabel = "padv_win_agents";
    op.AgentLabel = "padv_linux_agents";
    op.StopOnStageFailure = true;
    op.RunprocessCommandOptions.GenerateJUnitForProcess = true;
    op.ReportPath = "$PROJECTROOT$/PA_Results/Report/ProcessAdvisorReport";
    padv.pipeline.generatePipeline(op, "CIPipeline");
end