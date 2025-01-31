""" 
    This module is meant to create minimal CASA script templates for
    simulating observations.
    For more customized scripts, please consider modifying a template 
    and provide it to synthesizer via command-line as
    $ synthesizer --synobs --script my_casa_script.py
"""

import os
import re
import subprocess
import numpy as np
import astropy.units as u
import astropy.constants as c

from synthesizer import utils

class CasaScript():
    
    def __init__(self, lam, name='casa_script.py'):
        """ Set default values for a template CASA script. """
        self.name = name
        self.lam = lam
        self.freq = c.c.cgs.value / (lam * u.micron.to(u.cm))
        self.simobserve = True
        self.clean = True
        self.exportfits = True
        self.graphics = 'both'
        self.overwrite = True
        self.polarization = True

        # simobserve
        self.project = 'synobs_data'
        self.skymodel = lambda st: f'radmc3d_{st}.fits'
        self.fitsimage = lambda st: f'synobs_{st}.fits'
        self.inbright = ''
        self.incell = ''
        self.mapsize = ''
        self.resolution = None
        self.pix_per_beam = 5
        self.incenter = f'{self.freq}Hz'
        self.inwidth = '2GHz'
        self.setpointings = True
        self.integration = '2s'
        self.totaltime = '1h'
        self.indirection = 'J2000 16h32m22.63 -24d28m31.8'
        self.hourangle = 'transit'
        self.refdate = '2017/05/20', 
        self.obsmode = 'int'
        self.telescope = None
        self.arrayconfig = self._get_antenna_array(cycle=4, arr=7)
        self.thermalnoise = 'tsys-manual'

        # tclean
        self.vis = f'{self.project}/{self.project}.{self.arrayfile}.noisy.ms'
        self.imagename = lambda s: f'{self.project}/clean_{s}'
        self.imsize = 100
        if self.resolution is None:
            self.cell = '0.008arcsec'
        else:
            self.cell = f'{self.resolution / self.pix_per_beam}arcsec'
        self.reffreq = self.incenter
        self.specmode = 'mfs'
        self.gridder = 'standard'
        self.deconvolver = 'multiscale'
        self.scales = [1, 8, 24]
        self.weighting = 'briggs'
        self.robust = 0.5
        self.niter = 1e4
        self.threshold = '5e-5Jy'
        self.pbcor = True
        self.interactive = False
        self.verbose = False

        # exportfits
        self.dropstokes = True
        self.dropdeg = True

    def _find_telescope(self):
        """ Find a proper telescope given the observing wavelength (microns) """
        if self.lam > 400 or self.lam < 4500:
            self.telescope = 'alma'

        elif self.lam >= 4500 and self.lam < 4e6:
            self.telescope = 'vla'

        else:
            utils.not_implemented('Simulations for telescopes operating '+\
                'outside the sub-/milimeter wavelengths are currently not '+\
                'implemented. But they will.')

    def _find_array(self):
        """ Get the best antenna array that matches a desired angular resolution
            To be implemented ...
        """
        utils.not_implemented()
        if self.resolution is not None:
            res = self.resolution
            pass

    def _get_antenna_array(self, cycle, arr):
        """ Set the antennalist string for a given antenna configuration.
            All possible config files are found in CASA_PATH/data/alma/simmos/
        """
        if self.telescope is None:
            self._find_telescope()
        self.cycle = str(cycle).lower()
        self.arr = str(arr).lower()
        self.arrayfile = f'{self.telescope}.cycle{self.cycle}.{self.arr}'
        return self.arrayfile + '.cfg'

    def write(self, name):
        """ Write a CASA script using the CasaScript parameters """
        
        self.name = name

        stokes = ['I', 'Q', 'U'] if self.polarization else ['I']
    
        with open(self.name, 'w+') as f:
            utils.print_(f'Writing template script: {self.name}')
            f.write('# Template CASA script to simulate observations. \n')
            f.write('# Written by the Synthesizer. \n\n')

            for s in stokes:

                # Overwrite string values if they were overriden from self.read()
                if isinstance(self.skymodel, str):
                    self.skymodel = self.skymodel.replace('I', s)
                else:
                    self.skymodel = self.skymodel(s)

                if isinstance(self.imagename, str):
                    self.imagename = self.imagename.replace('I', s)
                else:
                    self.imagename = self.imagename(s)

                if isinstance(self.fitsimage, str):
                    self.fitsimage = self.fitsimage.replace('I', s)
                else:
                    self.fitsimage = self.fitsimage(s)
    
                if self.simobserve:
                    f.write(f'print("\033[1m\\n[syn_obs] ')
                    f.write(f'Observing Stokes {s} ...\033[0m\\n")\n')
                    f.write(f'simobserve( \n')
                    f.write(f'    project = "{self.project}", \n')
                    f.write(f'    skymodel = "{self.skymodel}", \n')
                    f.write(f'    inbright = "{self.inbright}", \n')
                    f.write(f'    incell = "{self.incell}", \n')
                    f.write(f'    incenter = "{self.incenter}", \n')
                    f.write(f'    inwidth = "{self.inwidth}", \n')
                    f.write(f'    mapsize = "{self.mapsize}", \n')
                    f.write(f'    setpointings = {self.setpointings}, \n')
                    f.write(f'    indirection = "{self.indirection}", \n')
                    f.write(f'    integration = "{self.integration}", \n')
                    f.write(f'    totaltime = "{self.totaltime}", \n')
                    f.write(f'    hourangle = "{self.hourangle}", \n')
                    f.write(f'    obsmode = "{self.obsmode}", \n')
                    f.write(f'    refdate = "{self.refdate}", \n')
                    f.write(f'    antennalist = "{self.arrayconfig}", \n')
                    f.write(f'    thermalnoise = "{self.thermalnoise}", \n')
                    f.write(f'    graphics = "{self.graphics}", \n')
                    f.write(f'    overwrite = {self.overwrite}, \n')
                    f.write(f'    verbose = {self.verbose}, \n')
                    f.write(f') \n')
            
                if self.clean:
                    f.write(f'print("\033[1m\\n[syn_obs] ')
                    f.write(f'Cleaning Stokes {s} ...\033[0m\\n")\n')
                    f.write(f' \n')
                    f.write(f'tclean( \n')
                    f.write(f'    vis = "{self.vis}", \n')
                    f.write(f'    imagename = "{self.imagename}", \n')
                    f.write(f'    imsize = {self.imsize}, \n')
                    f.write(f'    cell = "{self.cell}", \n')
                    f.write(f'    reffreq = "{self.reffreq}", \n')
                    f.write(f'    specmode = "{self.specmode}", \n')
                    f.write(f'    gridder = "{self.gridder}", \n')
                    f.write(f'    deconvolver = "{self.deconvolver}", \n')
                    f.write(f'    scales = {self.scales}, \n')
                    f.write(f'    weighting = "{self.weighting}", \n')
                    f.write(f'    robust = {self.robust}, \n')
                    f.write(f'    niter = {int(self.niter)}, \n')
                    f.write(f'    threshold = "{self.threshold}", \n')
                    f.write(f'    pbcor = {self.pbcor}, \n')
                    f.write(f'    interactive = {self.interactive}, \n')
                    f.write(f'    verbose = {self.verbose}, \n')
                    f.write(f') \n')

                    f.write(f'imregrid( \n')
                    f.write(f'    "{self.imagename}.image", \n')
                    f.write(f'    template = "{self.project}/{self.project}.{self.arrayfile}.skymodel", \n')
                    f.write(f'    output = "{self.imagename}.image_modelsize", \n')
                    f.write(f'    overwrite = True, \n')
                    f.write(f') \n\n')

                if self.exportfits:
                    f.write(f'print("\033[1m\\n[syn_obs] ')
                    f.write(f'Exporting Stokes {s} ...\033[0m\\n")\n')
                    f.write(f' \n')
                    f.write(f'exportfits( \n')
                    f.write(f'    imagename = "{self.imagename}.image_modelsize", \n')
                    f.write(f'    fitsimage = "{self.fitsimage}", \n')
                    f.write(f'    dropstokes = {self.dropstokes}, \n')
                    f.write(f'    dropdeg = {self.dropdeg}, \n')
                    f.write(f'    overwrite = True, \n')
                    f.write(f') \n\n')
                

    def read(self, name):
        """ Read variables and parameters from an already existing file """

        # Raise an error if file doesn't exist, including wildcards
        utils.file_exists(name)

        self.name = name

        def strip_line(l):
            l = l.split('=')[1]
            l = l.strip('\n')
            l = l.strip(',')
            l = l.strip()
            l = l.strip(',')
            l = l.strip('"')
            l = l.strip("'")
            if ',' in l and not '[' in l: l = l.split(',')[0]
            return l

        f = open(str(name), 'r')

        for line in f.readlines():
            # Main boolean switches
            if 'Simobserve' in line and '=' in line: self.simobserve = strip_line(line)
            if 'Clean' in line and '=' in line: self.clean = strip_line(line)
            if 'polarization' in line and '=' in line: self.polarization = strip_line(line)
        
            # Simobserve
            if 'project' in line: self.project = strip_line(line)
            if 'skymodel ' in line and '=' in line: self.skymodel = strip_line(line)
            if 'inbright' in line: self.inbright = strip_line(line)
            if 'incell' in line: self.incell = strip_line(line)
            if 'mapsize' in line: self.mapsize = strip_line(line)
            if 'incenter' in line: self.incenter = strip_line(line)
            if 'inwidth' in line: self.inwidth = strip_line(line)
            if 'setpointings' in line: self.setpointings = strip_line(line)
            if 'integration' in line: self.integration = strip_line(line)
            if 'totaltime' in line: self.totaltime = strip_line(line)
            if 'indirection' in line: self.indirection = strip_line(line)
            if 'refdate' in line: self.refdate = strip_line(line)
            if 'hourangle' in line: self.hourangle = strip_line(line)
            if 'obsmode' in line: self.obsmode = strip_line(line)
            if 'antennalist' in line: self.arrayconfig = strip_line(line)
            if 'thermalnoise' in line: self.thermalnoise = strip_line(line)
            if 'graphics' in line: self.graphics = strip_line(line)
            if 'overwrite' in line: self.overwrite = strip_line(line)
            if 'verbose' in line: self.verbose = strip_line(line)
            self.arrayfile = self.arrayconfig.strip('.cfg')
    
            # tclean
            if 'vis' in line: self.vis = strip_line(line)
            if 'imagename' in line: self.imagename = strip_line(line)
            if 'imsize' in line: self.imsize = strip_line(line)
            if 'cell' in line: self.cell = strip_line(line)
            if 'reffreq' in line: self.reffreq = strip_line(line)
            if 'restfrq' in line: self.restfrq = strip_line(line)
            if 'specmode' in line: self.specmode = strip_line(line)
            if 'gridder' in line: self.gridder = strip_line(line)
            if 'deconvolver' in line: self.deconvolver = strip_line(line)
            if 'scales' in line: self.scales = strip_line(line)
            if 'weighting' in line: self.weighting = strip_line(line)
            if 'robust' in line: self.robust = strip_line(line)
            if 'niter' in line: self.niter = strip_line(line)
            if 'threshold' in line: self.threshold = strip_line(line)
            if 'pbcor' in line: self.pbcor = strip_line(line)
            if 'mask' in line: self.mask = strip_line(line)
            if 'interactive' in line: self.interactive = strip_line(line)

            # Exportfits
            if 'fitsimage' in line: self.fitsimage = strip_line(line)
            if 'dropstokes' in line: self.dropstokes = strip_line(line)
            if 'dropdeg' in line: self.dropdeg = strip_line(line)

        f.close()

    def _clean_project(self):
        """ Delete any previous project to avoid the CASA clashing """

        if self.overwrite and os.path.exists('synobs_data'):
            if not self.simobserve or not self.clean or not self.exportfits: 

                utils.print_(
                    f'Deleting previous observing project: {self.project}')
                subprocess.run('rm -r synobs_data', shell=True)

    def run(self):
        """ Run the ALMA/JVLA simulation script """

        self._clean_project()
        subprocess.run(f'casa -c {self.name} --nologger'.split())

    def cleanup(self):
        if utils.file_exists('casa-*.log', raise_=False) or\
                utils.file_exists('*.last', raise_=False):

            utils.print_('Cleaning up ... deleting casa-*.log and *.last files')
            subprocess.run('rm casa-*.log *.last', shell=True)
