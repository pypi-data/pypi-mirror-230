"""Analyses."""
import logging
import os, shutil
import tempfile
import subprocess as sb

import pandas as pd


logger = logging.getLogger('garjus.analyses')


def _download_zip(xnat, uri, zipfile):
    # Build the uri to download
    _uri = uri + '?format=zip&structure=simplified'

    response = xnat.get(_uri, stream=True)
    with open(zipfile, 'wb') as f:
        shutil.copyfileobj(response.raw, f)

    return zipfile


def _download_file_stream(xnat, uri, dst):

    response = xnat.get(uri, stream=True)

    with open(dst, 'wb') as f:
        shutil.copyfileobj(response.raw, f)

    return dst


def update(garjus, projects=None):
    """Update analyses."""
    for p in (projects or garjus.projects()):
        if p in projects:
            logger.debug(f'updating analyses:{p}')
            _update_project(garjus, p)


def _update_project(garjus, project):
    analyses = garjus.analyses([project], download=True)

    if len(analyses) == 0:
        logger.debug(f'no open analyses for project:{project}')
        return

    # Handle each record
    for i, a in analyses.iterrows():
        aname = a['NAME']

        if not a.get('PROCESSOR', False):
            logger.debug(f'no processor:{aname}')
            continue

        if a['COMPLETE'] != '2':
            logger.debug(f'skipping complete not set:{aname}')
            continue

        if a['STATUS'] == 'READY':
            logger.debug(f'skipping done:{aname}')
            continue

        logger.info(f'updating analysis:{aname}')
        _update(garjus, a)


def update_analysis(
    garjus,
    project,
    analysis_id
):
    """Update analysis."""

    # Run it
    _update(garjus, analysis)


def _has_outputs(garjus, analysis):
    project = analysis['PROJECT']
    analysis_id = analysis['ID']
    resource = f'{project}_{analysis_id}'
    res_uri = f'/projects/{project}/resources/{resource}'
    output_zip = f'{project}_{analysis_id}_OUTPUTS.zip'

    res = garjus.xnat().select(res_uri)

    file_list = res.files()
    if output_zip in file_list:
        logger.info(f'found:{output_zip}')
        return True
    else:
        return False


def _has_inputs(garjus, analysis):
    project = analysis['PROJECT']
    analysis_id = analysis['ID']
    resource = f'{project}_{analysis_id}'
    res_uri = f'/projects/{project}/resources/{resource}'
    inputs_zip = f'{project}_{analysis_id}_INPUTS.zip'

    res = garjus.xnat().select(res_uri)

    file_list = res.files()
    if inputs_zip in file_list:
        logger.info(f'found:{inputs_zip}')
        return True
    else:
        logger.info(f'inputs not found:{res_uri}:{inputs_zip}')

        return False


def _update(garjus, analysis):
    with tempfile.TemporaryDirectory() as tempdir:
        inputs_dir = f'{tempdir}/INPUTS'
        outputs_dir = f'{tempdir}/OUTPUTS'

        if _has_outputs(garjus, analysis):
            logger.debug(f'outputs exist')
        elif _has_inputs(garjus, analysis):
            logger.debug(f'inputs exist')
        else:
            _make_dirs(inputs_dir)
            _make_dirs(outputs_dir)

            # Create new inputs
            logger.info(f'downloading analysis inputs to {inputs_dir}')
            _download_inputs(garjus, analysis, inputs_dir)

            logger.info(f'uploading analysis inputs zip')
            try:
                dst = upload_inputs(
                    garjus,
                    analysis['PROJECT'], 
                    analysis['ID'],
                    tempdir)

                logger.debug(f'set analysis inputs')
                garjus.set_analysis_inputs(
                    analysis['PROJECT'],
                    analysis['ID'],
                    dst)
            except Exception as err:
                logger.error(f'upload failed')
                return

            logger.info(f'running analysis')
            _run(garjus, analysis, tempdir)

            # Set STATUS
            logger.info(f'set analysis status')
            garjus.set_analysis_status(
                analysis['PROJECT'],
                analysis['ID'],
                'READY')

    # That is all
    logger.info(f'analysis done!')


def _run(garjus, analysis, tempdir):
    processor = analysis['PROCESSOR']

    # Run commmand and upload output
    command = processor.get('command', None)
    if command is None:
        logger.debug('no command found')
        return

    # Run steps
    logger.info('running analysis steps...')

    # Get the container name or path
    container = processor['command']['container']
    for c in processor['containers']:
        if c['name'] == container:
            container = c['source']

        if 'path' in c:
            print(c['path'], 'not yet')
            continue

    if shutil.which('singularity'):
        command_mode = 'singularity'
    elif shutil.which('docker'):
        command_mode = 'docker'
    else:
        logger.error('command mode not found, cannot run container command')
        return

    logger.debug(f'command mode is {command_mode}')

    if command_mode == 'singularity':
        # Build the command string
        cmd = f'singularity run -c -e -B {tempdir}/INPUTS:/INPUTS -B {tempdir}/OUTPUTS:/OUTPUTS {container}'
    elif command_mode == 'docker':
        if container.startswith('docker://'):
            # Remove docker prefix
            container = container.split('docker://')[1]

        # Build the command string
        cmd = f'docker run -it --rm -v {tempdir}/INPUTS:/INPUTS -v {tempdir}/OUTPUTS:/OUTPUTS {container}'

    # Run it
    logger.info(cmd)
    os.system(cmd)

    # Upload it
    logger.info(f'uploading output')
    dst = upload_outputs(garjus, analysis['PROJECT'], analysis['ID'], tempdir)
    garjus.set_analysis_outputs(analysis['PROJECT'], analysis['ID'], dst)


def run_analysis(garjus, project, analysis_id):
    analysis = garjus.load_analysis(project, analysis_id)

    _run(garjus, analysis)

    # That is all
    logger.info(f'analysis done!')


def upload_outputs(garjus, project, analysis_id, tempdir):
    # Upload output_zip Project Resource on XNAT named with
    # the project and analysis id as PROJECT_ID, e.g. REMBRANDT_1
    resource = f'{project}_{analysis_id}'
    res_uri = f'/projects/{project}/resources/{resource}'
    outputs_zip = f'{tempdir}/{project}_{analysis_id}_OUTPUTS.zip'

    # Zip output
    logger.info(f'zipping output to {outputs_zip}')
    sb.run(['zip', '-r', outputs_zip, 'OUTPUTS'], cwd=tempdir)

    logger.debug(f'connecting to xnat resource:{res_uri}')
    res = garjus.xnat().select(res_uri)

    logger.debug(f'uploading file to xnat resource:{outputs_zip}')
    res.file(os.path.basename(outputs_zip)).put(
        outputs_zip,
        overwrite=True,
        params={"event_reason": "analysis upload"})

    uri = f'{garjus.xnat_host()}/data{res_uri}/files/{os.path.basename(outputs_zip)}'

    return uri


def upload_inputs(garjus, project, analysis_id, tempdir):
    # Upload to Project Resource on XNAT named with
    # the project and analysis id as PROJECT_ID, e.g. REMBRANDT_1
    resource = f'{project}_{analysis_id}'
    res_uri = f'/projects/{project}/resources/{resource}'
    inputs_zip = f'{tempdir}/{project}_{analysis_id}_INPUTS.zip'

    logger.info(f'zipping inputs {tempdir} to {inputs_zip}')
    sb.run(['zip', '-r', inputs_zip, 'INPUTS'], cwd=tempdir)

    assert(os.path.isfile(inputs_zip))

    logger.debug(f'connecting to xnat resource:{res_uri}')
    res = garjus.xnat().select(res_uri)

    logger.debug(f'uploading file to xnat resource:{inputs_zip}')
    res.file(os.path.basename(inputs_zip)).put(
        inputs_zip,
        overwrite=True,
        params={"event_reason": "analysis upload"})

    uri = f'{garjus.xnat_host()}/data{res_uri}/files/{os.path.basename(inputs_zip)}'

    return uri


def _sessions_from_scans(scans):
    return scans[[
        'PROJECT',
        'SUBJECT',
        'SESSION',
        'SESSTYPE',
        'DATE',
        'SITE'
    ]].drop_duplicates()


def _sessions_from_assessors(assessors):
    return assessors[[
        'PROJECT',
        'SUBJECT',
        'SESSION',
        'SESSTYPE',
        'DATE',
        'SITE'
    ]].drop_duplicates()


def _download_file(garjus, proj, subj, sess, assr, res, fmatch, dst):
    # Make the folders for this file path
    _make_dirs(os.path.dirname(dst))

    # Connect to the resource on xnat
    r = garjus.xnat().select_assessor_resource(proj, subj, sess, assr, res)

    # TODO: apply regex or wildcards in fmatch
    # res_obj.files()[0].label()).get(fpath)
    # res.files().label()

    r.file(fmatch).get(dst)

    return dst


def _download_sgp_resource_zip(xnat, project, subject, assessor, resource, outdir):
    reszip = '{}_{}.zip'.format(assessor, resource)
    respath = 'data/projects/{}/subjects/{}/experiments/{}/resources/{}/files'
    respath = respath.format(project, subject, assessor, resource)

    # Download the resource as a zip file
    download_zip(respath, reszip)

    # Unzip the file to output dir
    logger.debug(f'unzip file {rezip} to {outdir}')
    with zipfile.ZipFile(reszip) as z:
        z.extractall(outdir)

    # TODO: check downloaded files, compare/size/md5 to xnat

    # Delete the zip
    os.remove(reszip)


def _download_sgp_file(garjus, proj, subj, assr, res, fmatch, dst):
    # Make the folders for this file path
    _make_dirs(os.path.dirname(dst))

    # Download the file
    uri = f'data/projects/{proj}/subjects/{subj}/experiments/{assr}/resources/{res}/files/{fmatch}'
    _download_file_stream(garjus.xnat(), uri, dst)


def _download_resource(garjus, proj, subj, sess, assr, res, dst):
    # Make the folders for destination path
    _make_dirs(dst)

    # Connect to the resource on xnat
    r = garjus.xnat().select_assessor_resource(proj, subj, sess, assr, res)

    # Download resource and extract
    r.get(dst, extract=True)

    return dst


def _download_sgp_resource(garjus, proj, subj, assr, res, dst):
    # Make the folders for destination path
    _make_dirs(dst)

    # Connect to the resource on xnat
    r = garjus.xnat().select_sgp_assessor(proj, subj, assr).resource(res)

    # Download extracted
    r.get(dst, extract=True)

    return dst


def _make_dirs(dirname):
    try:
        os.makedirs(dirname)
    except FileExistsError:
        pass


def _download_subject_assessors(garjus, subj_dir, sgp_spec, proj, subj, sgp):

    sgp = sgp[sgp.SUBJECT == subj]

    for k, a in sgp.iterrows():

        assr = a.ASSR

        for assr_spec in sgp_spec:
            logger.debug(f'assr_spec={assr_spec}')

            assr_types = assr_spec['types'].split(',')

            logger.debug(f'assr_types={assr_types}')

            if a.PROCTYPE not in assr_types:
                logger.debug(f'skip assr, no match on type={assr}:{a.PROCTYPE}')
                continue

            for res_spec in assr_spec['resources']:

                try:
                    res = res_spec['resource']
                except (KeyError, ValueError) as err:
                    logger.error(f'reading resource:{err}')
                    continue

                if 'fmatch' in res_spec:
                    # Download files
                    for fmatch in res_spec['fmatch'].split(','):
                        # Where shall we save it?
                        dst = f'{subj_dir}/{assr}/{res}/{fmatch}'

                        # Have we already downloaded it?
                        if os.path.exists(dst):
                            logger.debug(f'exists:{dst}')
                            continue

                        # Download it
                        logger.info(f'download file:{proj}:{subj}:{assr}:{res}:{fmatch}')
                        try:
                            _download_sgp_file(
                                garjus,
                                proj,
                                subj,
                                assr,
                                res,
                                fmatch,
                                dst
                            )
                        except Exception as err:
                            logger.error(f'{subj}:{assr}:{res}:{fmatch}:{err}')
                            import traceback
                            traceback.print_exc()
                            raise err
                else:
                    # Download whole resource

                    # Where shall we save it?
                    dst = f'{subj_dir}/{assr}'

                    # Have we already downloaded it?
                    if os.path.exists(os.path.join(dst, res)):
                        logger.debug(f'exists:{dst}')
                        continue

                    # Download it
                    logger.info(f'download resource:{proj}:{subj}:{assr}:{res}')
                    try:
                        _download_sgp_resource(
                            garjus,
                            proj,
                            subj,
                            assr,
                            res,
                            dst
                        )
                    except Exception as err:
                        logger.error(f'{subj}:{assr}:{res}:{err}')
                        raise err


def _download_subject(garjus, subj_dir, subj_spec, proj, subj, sessions, assessors, sgp):

    #  subject-level assessors
    sgp_spec = subj_spec.get('assessors', None)
    if sgp_spec:
        logger.debug(f'download_sgp={subj_dir}')
        _download_subject_assessors(garjus, subj_dir, sgp_spec, proj, subj, sgp)

    # Download the subjects sessions
    for sess_spec in subj_spec.get('sessions', []):
        sess_types = sess_spec['types'].split(',')

        for i, s in sessions[sessions.SUBJECT == subj].iterrows():
            sess = s.SESSION

            # Apply session type filter
            if s.SESSTYPE not in sess_types:
                logger.debug(f'skip session, no match on type={sess}:{s.SESSTYPE}')
                continue

            sess_dir = f'{subj_dir}/{sess}'
            logger.debug(f'download_session={sess_dir}')
            _download_session(
                garjus, sess_dir, sess_spec, proj, subj, sess, assessors)


def _download_session(garjus, sess_dir, sess_spec, proj, subj, sess, assessors):
    # get the assessors for this session
    sess_assessors = assessors[assessors.SESSION == sess]

    for k, a in sess_assessors.iterrows():
        assr = a.ASSR

        for assr_spec in sess_spec.get('assessors', []):
            logger.debug(f'assr_spec={assr_spec}')

            assr_types = assr_spec['types'].split(',')

            logger.debug(f'assr_types={assr_types}')

            if a.PROCTYPE not in assr_types:
                logger.debug(f'skip assr, no match on type={assr}:{a.PROCTYPE}')
                continue

            for res_spec in assr_spec['resources']:

                try:
                    res = res_spec['resource']
                except (KeyError, ValueError) as err:
                    logger.error(f'reading resource:{err}')
                    continue

                if 'fmatch' in res_spec:
                    # Download files
                    for fmatch in res_spec['fmatch'].split(','):

                        # Where shall we save it?
                        dst = f'{sess_dir}/{assr}/{res}/{fmatch}'

                        # Have we already downloaded it?
                        if os.path.exists(dst):
                            logger.debug(f'exists:{dst}')
                            continue

                        # Download it
                        logger.info(f'download file:{proj}:{subj}:{sess}:{assr}:{res}:{fmatch}')
                        try:
                            _download_file(
                                garjus,
                                proj,
                                subj,
                                sess,
                                assr,
                                res,
                                fmatch,
                                dst
                            )
                        except Exception as err:
                            logger.error(f'{subj}:{sess}:{assr}:{res}:{fmatch}:{err}')
                            raise err
                else:
                    # Download whole resource

                    # Where shall we save it?
                    dst = f'{sess_dir}/{assr}'

                    # Have we already downloaded it?
                    if os.path.exists(os.path.join(dst, res)):
                        logger.debug(f'exists:{dst}')
                        continue

                    # Download it
                    logger.info(f'download resource:{proj}:{subj}:{sess}:{assr}:{res}')
                    try:
                        _download_resource(
                            garjus,
                            proj,
                            subj,
                            sess,
                            assr,
                            res,
                            dst
                        )
                    except Exception as err:
                        logger.error(f'{subj}:{sess}:{assr}:{res}:{err}')
                        raise err


def download_analysis_inputs(garjus, project, analysis_id, download_dir):

    logger.debug(f'download_analysis_inputs:{project}:{analysis_id}:{download_dir}')

    analysis = garjus.load_analysis(project, analysis_id)

    _download_inputs(garjus, analysis, download_dir)


def _download_inputs(garjus, analysis, download_dir):
    errors = []

    project = analysis['PROJECT']

    logger.info('loading project data')
    assessors = garjus.assessors(projects=[project])
    scans = garjus.scans(projects=[project])
    sgp = garjus.subject_assessors(projects=[project])

    sessions = pd.concat([
        _sessions_from_scans(scans),
        _sessions_from_assessors(assessors)
    ])
    sessions = sessions.drop_duplicates()

    # Which subjects to include?
    subjects = analysis['SUBJECTS'].splitlines()

    logger.debug(f'subjects={subjects}')

    # What to download for each subject?
    subj_spec = analysis['PROCESSOR']['inputs']['xnat']['subjects']

    logger.debug(f'subject spec={subj_spec}')

    for subj in subjects:
        logger.debug(f'subject={subj}')

        # Make the Subject download folder
        subj_dir = f'{download_dir}/{subj}'
        _make_dirs(subj_dir)

        # Download the subject as specified in subj_spec
        try:
            logger.debug(f'_download_subject={subj}')
            _download_subject(
                garjus,
                subj_dir,
                subj_spec,
                project,
                subj,
                sessions,
                assessors,
                sgp)
        except Exception as err:
            logger.debug(err)
            errors.append(subj)
            continue

    # report what's missing
    if errors:
        logger.info(f'errors{errors}')
    else:
        logger.info(f'download complete with no errors!')

    logger.debug('done!')
