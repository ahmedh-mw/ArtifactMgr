function generate_jenkins_pipeline()
    cp = openProject('scm');

    op = padv.pipeline.GitHubOptions;
    % op.PipelineArchitecture = "IndependentModelParallelJobs"; # SingleJob, SerialJobs, SerialJobsGroupPerTask
    op.PipelineArchitecture = "IndependentModelParallelJobs";
    op.MatlabInstallationLocation = "D:/sb/Bslcicd_1217/matlab/bin";
    op.RunnerLabels = "padv_win_agents";
    op.StopOnStageFailure = true;
    op.RunprocessCommandOptions.GenerateJUnitForProcess = true;
    op.ReportPath = "$PROJECTROOT$/PA_Results/Report/ProcessAdvisorReport";
    padv.pipeline.generatePipeline(op, "CIPipeline");
    % Copy the pipeline and dag files just outside the project folder
    copyfile( fullfile(cp.RootFolder, 'derived', 'pipeline' , '*'), cp.RootFolder);
end