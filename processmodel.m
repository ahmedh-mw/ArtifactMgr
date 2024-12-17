function processmodel(pm)
    % Defines the project's processmodel

    arguments
        pm padv.ProcessModel
    end

    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    %% Include/Exclude Tasks in processmodel
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

    includeModelMaintainabilityMetricTask = true;
    includeModelTestingMetricTask = true;
    includeModelStandardsTask = true;
    includeDesignErrorDetectionTask = true;
    includeFindClones = true;
    includeModelComparisonTask = true;
    includeSDDTask = true;
    includeSimulinkWebViewTask = true;
    includeTestsPerTestCaseTask = true;
    includeMergeTestResultsTask = true;
    includeGenerateCodeTask = true;
    includeAnalyzeModelCode = true && ~padv.internal.isMACA64 && exist('polyspaceroot','file');
    includeProveCodeQuality = true && ~padv.internal.isMACA64 && (~isempty(ver('pscodeprover')) || ~isempty(ver('pscodeproverserver')));
    includeCodeInspection = true;

    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    %% Define Shared Path Variables
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

    % Set default root directory for task results
    pm.DefaultOutputDirectory = fullfile('$PROJECTROOT$', '04_Results');
	defaultTestResultPath = fullfile('$DEFAULTOUTPUTDIR$','test_results');

    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    %% Define Shared Queries
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    findModels = padv.builtin.query.FindModels(Name="ModelsQuery");
    findModelsWithTests = padv.builtin.query.FindModelsWithTestCases(Parent=findModels);
    findTestsForModel = padv.builtin.query.FindTestCasesForModel(Parent=findModels);

    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    %% Register Tasks
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

    %% Collect Model Maintainability Metrics
    % Tools required: Simulink Check
    if includeModelMaintainabilityMetricTask
        mmMetricTask = pm.addTask(padv.builtin.task.CollectMetrics());
    end

    %% Check modeling standards
    % Tools required: Model Advisor
    if includeModelStandardsTask
        maTask = pm.addTask(padv.builtin.task.RunModelStandards(IterationQuery=findModels));
        maTask.addInputQueries(padv.builtin.query.FindFileWithAddress( ...
            Type='ma_config_file', Path=fullfile('tools','sampleChecks.json')));
        % Change Report path
        maTask.ReportPath = fullfile(...
            '$DEFAULTOUTPUTDIR$','$ITERATIONARTIFACT$','model_standards_results');
    end

    %% Detect design errors
    % Tools required: Simulink Design Verifier
    if includeDesignErrorDetectionTask
        dedTask = pm.addTask(padv.builtin.task.DetectDesignErrors(IterationQuery=findModels));
    end

    %% Generate clone detection reports
    % Tools required: Clone Detector
    if includeFindClones
        %Across Model Clones Instance
        acrossModelCloneDetectTask = pm.addTask(padv.builtin.task.FindClones(Name = "FindAcrossModelClones", ...
            IterationQuery=findModels,Title=message('padv_spkg:builtin_text:FindClonesAcrossModelTitle').getString()));
        acrossModelCloneDetectTask.ReportPath = fullfile(defaultTestResultPath,'findAcrossModelClones');
        acrossModelCloneDetectTask.AcrossModelReportName = "$ITERATIONARTIFACT$_AcrossModelClonesReport";
        acrossModelCloneDetectTask.DetectLibraryClones = false;
        %Library Clones Instance
        libCloneDetectTask = pm.addTask(padv.builtin.task.FindClones(Name = "FindLibraryClones", ...
            IterationQuery=findModels,Title=message('padv_spkg:builtin_text:FindLibraryClonesTitle').getString()));
        libCloneDetectTask.ReportPath = fullfile(defaultTestResultPath,'findLibraryClones');
        libCloneDetectTask.LibraryReportName = "$ITERATIONARTIFACT$_LibraryClonesReport";
        libCloneDetectTask.DetectClonesAcrossModel = false;
    end

    %% Generate Model Comparison
    if includeModelComparisonTask
        mdlCompTask = pm.addTask(padv.builtin.task.GenerateModelComparison(IterationQuery=findModels));
    end

    %% Generate SDD report (System Design Description)
    %  Tools required: Simulink Report Generator
    if includeSDDTask
        sddTask = pm.addTask(padv.builtin.task.GenerateSDDReport(IterationQuery=findModels));
    end

    %% Generate Simulink web view
    % Tools required: Simulink Report Generator
    if includeSimulinkWebViewTask
        slwebTask = pm.addTask(padv.builtin.task.GenerateSimulinkWebView(IterationQuery=findModels));
    end

    %% Run tests per test case
    % Tools required: Simulink Test
    if includeTestsPerTestCaseTask
        milTask = pm.addTask(padv.builtin.task.RunTestsPerTestCase(IterationQuery=findTestsForModel));
        milTask.OutputDirectory = defaultTestResultPath;
    end

    %% Merge test results
    % Tools required: Simulink Test (and optionally Simulink Coverage)
    if includeTestsPerTestCaseTask && includeMergeTestResultsTask
        mergeTestTask = pm.addTask(padv.builtin.task.MergeTestResults(IterationQuery=findModelsWithTests));
        mergeTestTask.ReportPath = defaultTestResultPath;
    end

    %% Collect Model Testing Metrics
    if includeModelTestingMetricTask
        mtMetricTask = pm.addTask(padv.builtin.task.CollectMetrics(Name="ModelTestingMetrics", IterationQuery=padv.builtin.query.FindUnits));
        mtMetricTask.Title = message('padv_spkg:builtin_text:ModelTestingMetricDemoTaskTitle').getString();
        mtMetricTask.Dashboard = "ModelUnitTesting";
        mtMetricTask.ReportName = "$ITERATIONARTIFACT$_ModelTesting";
    end

    %% Generate Code
    % Tools required: Embedded Coder
    % By default, we generate code for all models in the project;
    if includeGenerateCodeTask
        codegenTask = pm.addTask(padv.builtin.task.GenerateCode(IterationQuery=findModels));
        codegenTask.UpdateThisModelReferenceTarget = 'IfOutOfDate';
    end

    %% Check coding standards 
    % Tools required: Polyspace Bug Finder
    if includeGenerateCodeTask && includeAnalyzeModelCode
        psbfTask = pm.addTask(padv.builtin.task.AnalyzeModelCode(IterationQuery=findModels));
        psbfTask.addInputQueries(padv.builtin.query.FindFileWithAddress( ...
            Type='ps_prj_file',Path=fullfile('tools','CodingRulesOnly_config.psprj')));
        psbfTask.ResultDir = string(fullfile('$DEFAULTOUTPUTDIR$', ...
            '$ITERATIONARTIFACT$','coding_standards'));
        psbfTask.Reports = "CodingStandards";
        psbfTask.ReportPath = string(fullfile('$DEFAULTOUTPUTDIR$', ...
            '$ITERATIONARTIFACT$','coding_standards'));
        psbfTask.ReportNames = "$ITERATIONARTIFACT$_CodingStandards";
        psbfTask.ReportFormat = "PDF";
    end

    %% Prove Code Quality 
    % Tools required: Polyspace Code Prover
    if includeGenerateCodeTask && includeProveCodeQuality
        pscpTask = pm.addTask(padv.builtin.task.AnalyzeModelCode(Name="ProveCodeQuality", IterationQuery=findModels));
        pscpTask.Title = message('padv_spkg:builtin_text:PSCPDemoTaskTitle').getString();
        pscpTask.VerificationMode = "CodeProver";
        pscpTask.ResultDir = string(fullfile('$DEFAULTOUTPUTDIR$', ...
            '$ITERATIONARTIFACT$','code_quality'));
        pscpTask.Reports = ["Developer", "CallHierarchy", "VariableAccess"];
        pscpTask.ReportPath = string(fullfile('$DEFAULTOUTPUTDIR$', ...
            '$ITERATIONARTIFACT$','code_quality'));
        pscpTask.ReportNames = [...
            "$ITERATIONARTIFACT$_Developer", ...
            "$ITERATIONARTIFACT$_CallHierarchy", ...
            "$ITERATIONARTIFACT$_VariableAccess"];
        pscpTask.ReportFormat = "PDF";
    end
    

    %% Inspect Code
    % Tools required: Simulink Code Inspector
    if includeGenerateCodeTask && includeCodeInspection
        slciTask = pm.addTask(padv.builtin.task.RunCodeInspection(IterationQuery=findModels));
    end
    
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    %% Set Task relationships
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

    %% Set Task Dependencies
    if includeGenerateCodeTask && includeCodeInspection
        slciTask.dependsOn(codegenTask);
    end
    if includeGenerateCodeTask && includeAnalyzeModelCode
        psbfTask.dependsOn(codegenTask);
    end
    if includeGenerateCodeTask && includeProveCodeQuality
        pscpTask.dependsOn(codegenTask);
    end
    if includeTestsPerTestCaseTask && includeMergeTestResultsTask
        mergeTestTask.dependsOn(milTask,"WhenStatus",{'Pass','Fail'});
    end

    %% Set Task Run-Order
    if includeMergeTestResultsTask && includeModelTestingMetricTask
        mtMetricTask.runsAfter(mergeTestTask);
    end
    if includeSimulinkWebViewTask && includeModelMaintainabilityMetricTask
        slwebTask.runsAfter(mmMetricTask);
    end
    if includeModelStandardsTask && includeModelMaintainabilityMetricTask
        maTask.runsAfter(mmMetricTask);
    end
    if includeModelStandardsTask && includeSimulinkWebViewTask
        maTask.runsAfter(slwebTask);
    end
    if includeModelStandardsTask && includeFindClones
        acrossModelCloneDetectTask.runsAfter(maTask);
        libCloneDetectTask.runsAfter(maTask);
    end
    if includeDesignErrorDetectionTask && includeModelStandardsTask
        dedTask.runsAfter(maTask);
    end
    if includeModelComparisonTask && includeModelStandardsTask
        mdlCompTask.runsAfter(maTask);
    end
    if includeSDDTask && includeModelStandardsTask
        sddTask.runsAfter(maTask);
    end
    if includeTestsPerTestCaseTask && includeModelStandardsTask
        milTask.runsAfter(maTask);
    end
    if includeGenerateCodeTask && includeAnalyzeModelCode && includeProveCodeQuality
        pscpTask.runsAfter(psbfTask);
    end
    % Set the code generation task to always run after Model Standards,
    % System Design Description, Test tasks, Clone Detection, and Model Testing Metrics
    if includeGenerateCodeTask && includeModelStandardsTask
        codegenTask.runsAfter(maTask);
    end
    if includeGenerateCodeTask && includeFindClones
        codegenTask.runsAfter(acrossModelCloneDetectTask);
        codegenTask.runsAfter(libCloneDetectTask);
    end
    if includeGenerateCodeTask && includeSDDTask
        codegenTask.runsAfter(sddTask);
    end
    if includeGenerateCodeTask && includeMergeTestResultsTask
        codegenTask.runsAfter(mergeTestTask);
    end
    if includeGenerateCodeTask && includeModelTestingMetricTask
        codegenTask.runsAfter(mtMetricTask);
    end
    % Both the Polyspace Bug Finder (PSBF) and the Simulink Code Inspector
    % (SLCI) tasks depend on the code generation tasks. SLCI task is set to
    % run after the PSBF task without establishing an execution dependency
    % by using 'runsAfter'.
    if includeGenerateCodeTask && includeAnalyzeModelCode ...
            && includeCodeInspection
        slciTask.runsAfter(psbfTask);
    end

    % !PROCESSMODEL_EDITOR_MARKER! %
    % Do not remove. Process Advisor uses the comment above to automatically add tasks. %
end
