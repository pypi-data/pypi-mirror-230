ACTIVITY_RENAME = {
    'redcap_repeat_instance': 'ID',
    'activity_description': 'DESCRIPTION',
    'activity_datetime': 'DATETIME',
    'activity_event': 'EVENT',
    'activity_field': 'FIELD',
    'activity_result': 'RESULT',
    'activity_scan': 'SCAN',
    'activity_subject': 'SUBJECT',
    'activity_session': 'SESSION',
    'activity_type': 'CATEGORY',
}

ANALYSES_RENAME = {
    'redcap_repeat_instance': 'ID',
    'analysis_name': 'NAME',
    'analysis_include': 'SUBJECTS',
    'analysis_processor': 'PROCESSOR',
    'analysis_input': 'INPUT',
    'analysis_output': 'OUTPUT',
    'analyses_complete': 'COMPLETE',
    'analysis_status': 'STATUS',
    'analysis_covars': 'COVARS',
    'analysis_notes': 'NOTES',
}

ISSUES_RENAME = {
    'redcap_repeat_instance': 'ID',
    'issue_date': 'DATETIME',
    'issue_description': 'DESCRIPTION',
    'issue_event': 'EVENT',
    'issue_field': 'FIELD',
    'issue_scan': 'SCAN',
    'issue_session': 'SESSION',
    'issue_subject': 'SUBJECT',
    'issue_type': 'CATEGORY',
}

PROCESSING_RENAME = {
    'redcap_repeat_instance': 'ID',
    'processor_file': 'FILE',
    'processor_filter': 'FILTER',
    'processor_args': 'ARGS',
}

TASKS_RENAME = {
    'task_assessor': 'ASSESSOR',
    'task_status': 'STATUS',
    'task_inputlist': 'INPUTLIST',
    'task_var2val': 'VAR2VAL',
    'task_memreq': 'MEMREQ',
    'task_walltime': 'WALLTIME',
    'task_procdate': 'PROCDATE',
    'task_timeused': 'TIMEUSED',
    'task_memused': 'MEMUSED',
    'task_yamlfile': 'YAMLFILE',
    'task_userinputs': 'USERINPUTS',
    'task_failcount': 'FAILCOUNT',
    'task_yamlupload': 'YAMLUPLOAD',
}

REPORTS_RENAME = {
    'progress_name': 'NAME',
    'progress_datetime': 'DATE',
    'progress_pdf': 'PDF',
    'progress_zip': 'DATA',
    'double_resultspdf': 'PDF',
    'double_resultsfile': 'DATA',
    'double_name': ' NAME',
    'double_datetime': 'DATE',
}

DISABLE_STATTYPES = [
    'fmri_rest_v2',
    'fmri_roi_v1',
    'struct_preproc_noflair_v1',
    'fmri_nback_v2',
    'Multi_Atlas_v3', 
    'fmri_roi_v2',
]

COLUMNS = {
    'activity': [
        'PROJECT', 'SUBJECT', 'SESSION', 'SCAN', 'ID', 'DESCRIPTION',
        'DATETIME', 'EVENT', 'FIELD', 'CATEGORY', 'RESULT', 'STATUS', 'SOURCE'],
    'assessors': [
        'PROJECT', 'SUBJECT', 'SESSION', 'SESSTYPE', 'NOTE', 'DATE', 'SITE',
        'ASSR', 'PROCSTATUS', 'PROCTYPE', 'JOBDATE', 'QCSTATUS',
        'QCDATE', 'QCBY', 'XSITYPE', 'INPUTS', 'MODALITY', 'full_path'],
    'issues': [
        'ID', 'DATETIME', 'PROJECT', 'CATEGORY',
        'SUBJECT', 'SESSION', 'SCAN ', 'DESCRIPTION',
        'EVENT', 'FIELD', 'STATUS'],
    'scans': [
        'PROJECT', 'SUBJECT', 'SESSION', 'SESSTYPE', 'TRACER', 'NOTE', 'DATE', 'SITE',
        'SCANID', 'SCANTYPE', 'QUALITY', 'RESOURCES', 'MODALITY', 'XSITYPE', 'full_path'],
    'processing': [
        'ID', 'PROJECT', 'TYPE', 'FILTER', 'FILE', 'CUSTOM', 'ARGS', 'YAMLUPLOAD', 'EDIT'],
    'subjects': [
        'PROJECT', 'SUBJECT', 'AGE', 'SEX', 'RACE'],
    'tasks': [
        'ID', 'PROJECT', 'STATUS', 'PROCTYPE', 'MEMREQ', 'WALLTIME',
        'TIMEUSED', 'MEMUSED', 'ASSESSOR', 'PROCDATE', 'INPUTLIST', 'VAR2VAL',
        'IMAGEDIR', 'JOBTEMPLATE', 'YAMLFILE', 'YAMLUPLOAD', 'USERINPUTS', 'FAILCOUNT'],
    'analyses': ['PROJECT', 'ID', 'NAME', 'STATUS', 'COMPLETE', 'EDIT', 'INPUT', 'OUTPUT', 'NOTES', 'SUBJECTS', 'PROCESSOR'],
    'processors': ['ID', 'PROJECT', 'TYPE', 'EDIT', 'FILE', 'FILTER', 'ARGS'],
    'sgp': ['PROJECT', 'SUBJECT', 'ASSR', 'PROCSTATUS', 'PROCTYPE', 'QCSTATUS', 'INPUTS', 'DATE', 'XSITYPE'],
    'reports': ['TYPE', 'PROJECT', 'NAME', 'DATE', 'PDF', 'DATA'],
}


PROCLIB = {
    'AMYVIDQA_v2': {
        'short_descrip': 'Regional Amyloid SUVR using cerebellum as reference.',
        'inputs_descrip': 'T1w MRI processed with FreeSurfer (FS7_v1), Amyloid PET',
        'procurl': 'https://github.com/ccmvumc/AMYVIDQA',
        'stats_subset': ['compositegm_suvr', 'cblmtot_suvr', 'cblmwm_suvr', 'cblmgm_suvr', 'hippocampus_suvr']
    },
    'BFC_v2': {
        'short_descrip': 'Basal Forebrain Volumes.',
        'inputs_descrip': 'T1w MRI',
        'procurl': 'https://github.com/ccmvumc/BFC',
        'stats_subset': ['CH4_L_VOL', 'CH4_R_VOL']
    },
    'BrainAgeGap_v2': {
        'short_descrip': 'Predicted age of brain.',
        'inputs_descrip': 'T1w MRI parcellated with BrainColor atlas',
        'procurl': 'https://pubmed.ncbi.nlm.nih.gov/32948749/',
    },
    'FALLYPRIDEQA_v1':{
        'short_descrip': 'Fallypride QA with Regional SUVR using whole cerebellum as reference.',
        'inputs_descrip': 'T1w MRI processed with FreeSurfer (FS7_v1), Fallypride PET',
        'procurl': 'https://github.com/bud42/FALLYPRIDEQA',
        'stats_subset': ['antcing_suvr', 'compositegm_suvr', 'cblmgm_suvr', 'cblmwm_suvr', 'cblmtot_suvr'],
    },
    'fmri_bct_v1': {
        'short_descrip': 'Brain Connectivity Toolbox measures.',
        'inputs_descrip': 'Resting MRI processed with fmri_roi_v2',
        'procurl': 'https://github.com/REMBRANDT-study/fmri_bct',
        'stats_subset': ['Shen268_thr0p3_degree', 'Schaefer400_thr0p3_degree'],
    },
    'fmri_msit_v2': {
        'short_descrip': 'fMRI MSIT task pre-processing and 1st-Level analysis.',
        'inputs_descrip': 'T1w MRI, MSIT fMRI, E-prime EDAT',
        'procurl': 'https://github.com/REMBRANDT-study/fmri_msit',
        'stats_subset': ['con_amyg_mean', 'inc_amyg_mean', 'med_pct_outliers', 'con_bnst_mean', 'inc_bnst_mean'],
    },
    'fmri_rest_v2': {
        'short_descrip': 'fMRI Resting State pre-processing.',
        'inputs_descrip': 'T1w MRI, Resting State fMRI',
        'procurl': 'https://github.com/REMBRANDT-study/fmri_rest',
    },
    'fmri_roi_v2': {
        'short_descrip': 'Regional measures of functional connectivity',
        'inputs_descrip': 'Resting State fMRI processed with fmri_rest_v2',
        'procurl': 'https://github.com/REMBRANDT-study/fmri_roi',
    },
    'FS7sclimbic_v0': {
        'short_descrip': 'FreeSurfer 7 ScLimbic - volumes of subcortical limbic regions including Basal Forebrain.',
        'inputs_descrip': 'T1w MRI processed with FreeSurfer (FS7_v1)',
        'procurl': 'https://surfer.nmr.mgh.harvard.edu/fswiki/ScLimbic',
        'stats_subset': ['Left-Basal-Forebrain', 'Right-Basal-Forebrain', 'Left-Nucleus-Accumbens', 'Right-Nucleus-Accumbens', 'eTIV'],
    },
    'FEOBVQA_v2': {
        'short_descrip': 'Regional SUVR using Supra-ventricular White Matter as reference.',
        'inputs_descrip': 'T1w MRI processed with FreeSurfer (FS7_v1), FEOBV PET',
        'procurl': 'https://github.com/ccmvumc/FEOBVQA',
        'stats_subset': ['cblmwm_suvr', 'compositegm_suvr', 'cblmgm_suvr'],
    },
    'FS7_v1': {
        'short_descrip': 'FreeSurfer 7 recon-all - whole brain parcellation, surfaces, cortical thickness.',
        'inputs_descrip': 'T1w MRI',
        'procurl': 'https://github.com/bud42/FS7',
    },
    'FS7HPCAMG_v1': {
        'short_descrip': 'FreeSurfer 7 hippocampus & amygdala sub-region volumes.',
        'inputs_descrip': 'T1w processed with FreeSurfer (FS7_v1)',
        'procurl': 'https://github.com/bud42/FS7HPCAMG_v1',
        'stats_subset': ['hpchead_lh', 'hpchead_rh', 'hpcbody_lh', 'hpcbody_rh', 'hpctail_lh', 'hpctail_rh'],
    },
    'LST_v1': {
        'short_descrip': 'Lesion Segmentation Toolbox - white matter lesion volumes.',
        'inputs_descrip': 'T1w MRI, FLAIR MRI',
        'procurl': 'https://github.com/ccmvumc/LST1',
    },
    'SAMSEG_v1': {
        'short_descrip': 'Runs SAMSEG from FreeSurfer 7.2 to get White Matter Lesion Volume.',
        'inputs_descrip': 'T1w MRI processed with FreeSurfer (FS7_v1), FLAIR MRI',
        'procurl': 'https://surfer.nmr.mgh.harvard.edu/fswiki/Samseg',
    },
    'fmriqa_v4': {
        'short_descrip': 'Functional MRI QA',
        'stats_subset': ['dvars_mean', 'fd_mean'],
    },
    'fmri_emostroop_v2': {
        'short_descrip': 'fMRI EmoStroop Pre-processing and 1st-Level',
        'inputs_descrip': 'T1w MRI, fMRI, EDAT',
        'procurl': 'https://github.com/ccmvumc/fmri_emostroop:v2',
        'stats_subset': ['lhSFG2_incgtcon', 'rhSFG2_incgtcon', 'overall_rt_mean'],
    },
}

STATLIB = {
    'FALLYPRIDEQA_v1': {
        'accumbens_suvr': 'Accumbens regional mean SUVR normalized by Whole Cerebellum',
        'amygdala_suvr': 'Amygdala regional mean SUVR normalized by Whole Cerebellum',
        'antcing_suvr': 'Anterior Cingulate regional mean SUVR normalized by Whole Cerebellum',
        'antflobe_suvr': 'Anterior Frontal Lobe mean SUVR normalized by Whole Cerebellum',
        'caudate_suvr': 'Caudate regional mean SUVR normalized by Whole Cerebellum',
        'cblmgm_suvr': 'Cerebellum Gray Matter regional mean SUVR normalized by Whole Cerebellum',
        'cblmtot_suvr': 'Cerebellum Total regional mean SUVR normalized by Whole Cerebellum',
        'cblmwm_suvr': 'Cerebellum White Matter regional mean SUVR normalized by Whole Cerebellum',
        'compositegm_suvr': 'Composite Gray Matter regional mean SUVR normalized by Whole Cerebellum',
        'cortwm_suvr': 'Cortical White Matter regional mean SUVR normalized by Whole Cerebellum',
        'hippocampus_suvr': 'Hippocampus regional mean SUVR normalized by Whole Cerebellum',
        'latplobe_suvr': 'Lateral Parietal Lobe regional mean SUVR normalized by Whole Cerebellum',
        'lattlobe_suvr': 'Lateral Temporal Lobe regional mean SUVR normalized by Whole Cerebellum',
        'mofc_suvr': 'Medial Orbito-frontal Cortex regional mean SUVR normalized by Whole Cerebellum',
        'pallidum_suvr': 'Pallidum regional mean SUVR normalized by Whole Cerebellum',
        'postcing_suvr': 'Posterior Cingulate regional mean SUVR normalized by Whole Cerebellum',
        'putamen_suvr': 'Putamen regional mean SUVR normalized by Whole Cerebellum',
        'thalamus_suvr': 'Thalamus regional mean SUVR normalized by Whole Cerebellum',
        'ventraldc_suvr': 'Ventral Diencephalon regional mean SUVR normalized by Whole Cerebellum',
    },
    'FS7_v1': {
        'fs7_etiv': 'Estimated Total Intracranial Volume',
        'fs7_hpc_lh': 'Hippocampus Left Hemisphere Volume',
        'fs7_hpc_rh': 'Hippocampus Right Hemisphere Volume',
        'fs7_latvent_lh': 'Lateral Ventricle Left Hemisphere Volume',
        'fs7_latvent_rh': 'Lateral Ventricle Right Hemisphere Volume',
        'fs7_stnv': 'Supra-tentorial not ventricles Volume',
        'fs7_supflobe_lh': 'Superior Frontal Lobe Left Hemisphere Thickness',
        'fs7_supflobe_rh': 'Superior Frontal Lobe Right Hemisphere Thickness',
    },
    'FEOBVQA_v2': {
        'antcing_suvr': 'Anterior Cingulate SUVR normalized by Supra-ventricular White Matter',
        'antflobe_suvr': 'Anterior Frontal Lobe SUVR normalized by Supra-ventricular White Matter',
        'cblmgm_suvr': 'Cerebellar Gray Matter SUVR normalized by Supra-ventricular White Matter',
        'cblmwm_suvr': 'Cerebellar White Matter SUVR normalized by Supra-ventricular White Matter',
        'compositegm_suvr': 'Composite Gray Matter SUVR normalized by Supra-ventricular White Matter',
        'cblmgm_suvr': 'Cerebellar Gray Matter SUVR normalized by Supra-ventricular White Matter',
        'cortwm_eroded_suvr': 'Eroded Cortical White Matter SUVR normalized by Supra-ventricular White Matter',
        'latplobe_suvr': 'Lateral Parietal Lobe SUVR normalized by Supra-ventricular White Matter',
        'lattlobe_suvr': 'Lateral Temporal Lobe SUVR normalized by Supra-ventricular White Matter',
        'postcing_suvr': 'Posterior Cingulate SUVR normalized by Supra-ventricular White Matter',
    },
    'SAMSEG_v1': {
        'samseg_lesions': 'whole brain White Matter Lesion Volume in cubic millimeters',
        'samseg_sbtiv': 'segmentation-based (estimated) Total Intracranial Volume in cubic millimeters',
    },
    'FS7HPCAMG_v1': {
        'hpcbody_lh': 'Hippocampus Body Left Hemisphere Volume in cubic millimeters',
        'hpcbody_rh': 'Hippocampus Body Right Hemisphere Volume in cubic millimeters',
        'hpchead_lh': 'Hippocampus Head Left Hemisphere Volume in cubic millimeters',
        'hpchead_rh': 'Hippocampus Head Right Hemisphere Volume in cubic millimeters',
        'hpctail_lh': 'Hippocampus Tail Left Hemisphere Volume in cubic millimeters',
        'hpctail_rh': 'Hippocampus Tail Right Hemisphere Volume in cubic millimeters',
    },
    'LST_v1': {
        'wml_volume': 'White Matter Lesion Volume',
    },
    'fmriqa_v4': {
        'dvars_mean': 'DVARS, framewise signal',
        'fd_mean': 'Framewise Displacement',
    },
    'struct_preproc_v1': {
        'Volume1': 'Gray Matter',
        'Volume2': 'White Matter',
        'Volume3': 'CSF',
    },
    'fmri_bct_v1': {
        'Schaefer400_thr0p1_deg': 'Degree'
    }
}
