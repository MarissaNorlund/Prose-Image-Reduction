from prose.reports.core import copy_figures
import os, requests
from pathlib import Path

class UploadToExofop:
    """
    Adapted from Karen Collins' code for LCO observations:
    Created on Sun Oct 13 23:46:04 2019
    @author: Karen
    version = '3.01'
    versiondate = '2020.01.24'

    """
    def __init__(self,obs,report_destination,transcov='',skip_summary_upload=0,skip_file_upload=0,username=None,password=None
                 ,notes='',tag_number=1,delta_mag=0):
        """

        Parameters
        ----------
        obs : Observation object
        report_destination : path or str
        delta_mag : float
            delta magnitude of faintest neighbor cleared, or delta magnitude of NEB, set to 0 to leave blank
        transcov : str
            Full, Ingress, Egress or Out of Transit (CASE SENSITIVE!!!)
        notes : str
            public note such as "deep" etc. - do not put proprietary results here
        skip_summary_upload : float
            set to 1 to skip uploading observation summary, set to 0 to upload observation summary
        skip_file_upload : float
            set to 1 to skip file uploads, set to 0 to upload matching files
        tag_number: str
        """
        self.obs = obs
        self.report_destination = report_destination
        self.delta_mag = delta_mag
        self.transcov = transcov
        self.notes = notes
        self.skip_summary_upload = skip_summary_upload
        self.skip_file_upload = skip_file_upload
        self.username = username
        self.password = password
        self.tag_number = tag_number
        self.email_title = None
        self.figures_path = None
        self.tag = None
        self.fileList = self.check_files()


    def check_files(self):
        if isinstance(self.report_destination,str):
            path = Path(self.report_destination)
        else:
            path = self.report_destination
        self.figures_path = path / 'figures'
        if self.figures_path.is_dir():
            return os.listdir(self.figures_path)
        else :
            copy_figures(path,self.obs.tfop_prefix,self.figures_path)
            return os.listdir(self.figures_path)

    def upload(self):
        toi = "TOI" + self.obs.toi
        observatory = self.obs.telescope.name
        telsize = str(self.obs.telescope.diameter / 100)
        camera = self.obs.telescope.camera_name
        filterband = self.obs.filter
        pixscale = str(self.obs.telescope.pixel_scale.value)
        psf = str(round(self.obs.mean_target_psf * self.obs.telescope.pixel_scale.value, 2)) #mean psf in arcsec
        photaprad = str(round(self.obs.optimal_aperture, 1))  # mean aperture radius in pixels
        obsstart = self.obs.time[0]
        obsend = self.obs.time[-1]
        obsdur = str(round(abs((obsend - obsstart) * 24 * 60)))
        obsnum = str(self.obs.time.size)  # number of exposures
        if self.transcov.lower() == 'full':
            transcov = 'Full'
        elif self.transcov.lower() == 'ingress':
            transcov = 'Ingress'
        elif self.transcov.lower() == 'egress':
            transcov = 'Egress'
        else:
            transcov = 'Out of Transit'
        if self.delta_mag == 0:
            deltamag = ''
        else:
            deltamag = str(self.delta_mag)
        self.tag = self.obs.night_date.strftime("%Y%m%d") + '_' + self.username + '_' + observatory + '_' + str(self.tag_number)  # short_date+'_'+username+'_TIC'+tic+'_'+planet
        tic = self.obs.tic_id

        entries = {
            'planet': toi,
            'tel': observatory,
            'telsize': telsize,
            'camera': camera,
            'filter': filterband,
            'pixscale': pixscale,
            'psf': psf,
            'photaprad': photaprad,
            'obsdate': self.obs.night_date.strftime("%Y-%m-%d"),
            'obsdur': obsdur,
            'obsnum': obsnum,
            'obstype': 'Continuous',
            'transcov': transcov,
            'deltamag': deltamag,
            'tag': self.tag,
            'groupname': 'tfopwg',
            'notes': self.notes,
            'id': tic
        }
        self.email_title = 'TIC ' + tic + '.' + self.obs.planet + ' ('f"{self.obs.name}"') on UT' + self.obs.night_date.strftime("%Y.%m.%d") + ' from ' + observatory + ' in ' + filterband

        if self.figures_path.is_dir():
            credentials = {
                'username': self.username,
                'password': self.password,
                'ref': 'login_user',
                'ref_page': '/tess/'
            }
            with requests.Session() as session:
                response1 = session.post('https://exofop.ipac.caltech.edu/tess/password_check.php', data=credentials)
                if response1:
                    print('Login OK.')
                else:
                    print('ERROR:  Login did not work.')

                if not self.skip_summary_upload:
                    response2 = session.post('https://exofop.ipac.caltech.edu/tess/insert_tseries.php', data=entries)
                    if response2:
                        print('Added new Time Series...')
                        #print(response2.text)
                    else:
                        print('ERROR: Time Series Add failed.')
                else:
                    print('Skipped observation summary upload per user request.')

                if not self.skip_file_upload:
                    for fileName in self.fileList:
                        if (self.figures_path / fileName).is_file() and fileName.startswith('TIC') and not fileName.startswith('TIC '):
                            description = ''
                            if fileName.endswith('stars.png'):
                                print('stars')
                                description = 'Field Image with Apertures'
                                print(description)

                            elif fileName.endswith('model.png'):
                                description = 'Light curve plot target star with model'

                            elif fileName.endswith('psf.png'):
                                description = 'Seeing profile'

                            elif fileName.endswith('comparison.png'):
                                description = 'Light curve plot comparison stars'

                            elif fileName.endswith('systematics.png'):
                                description = 'AstroImageJ Photometry Aperture File'

                            elif fileName.endswith('Light curve plot target target star with systematics'):
                                description = 'AstroImageJ Plot Configuration File'

                            elif fileName.endswith('measurements.txt'):
                                description = ' Measurements Table'

                            elif fileName.endswith('lightcurve.png'):
                                description = 'Light curve plot target star'

                            #else:
                            #    description=''
                            #    print('******NOT UPLOADED: ' + fileName)

                            if description == '':
                                print('******NOT UPLOADED: ' + fileName)
                            else:
                                print(fileName,type(fileName))
                                files = {'file_name': (open(str(self.figures_path) + '/' + fileName), 'rb')}
                                payload = {
                                    'file_type': 'Light_Curve',
                                    'planet': toi,
                                    'file_desc': description,
                                    'file_tag': self.tag,
                                    'groupname': 'tfopwg',
                                    'propflag': 'on',
                                    'id': tic
                                }
                                print(toi)
                                print(tic)
                                print(description)
                                print(files)
                                response3 = session.post('https://exofop.ipac.caltech.edu/tess/insert_file.php', files=files, data=payload)
                                print(response3.text)

                                if response3:
                                    print('Uploading file: {}'.format(fileName))
                                else:
                                    print('ERROR: File upload failed: {}'.format(fileName))
                                print('UPLOADED:' + fileName)
                        else:
                            print('******NOT UPLOADED: ' + fileName)
                else:
                    print("Skipped file uploads per user request.")


