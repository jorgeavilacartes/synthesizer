# Setup based on Liu et al. (2018)

import time
Simobserve = True
Clean = True
polarization = False

if Simobserve:
    simobserve(
        project = 'synobs_data',
        skymodel = 'radmc3d_I.fits',
        incenter = '44GHz',
        inwidth = '8GHz', 
        setpointings = True,
        integration = '2s',
        totaltime = '46min',
        indirection = 'J2000 16h32m22.62 -24d28m32.5',
        refdate = '2015/01/18', 
        hourangle = 'transit',
        obsmode = 'int',
        antennalist = 'vla.cnb.cfg',
        thermalnoise = 'tsys-atm',
        graphics = 'both',
        overwrite = True,
        verbose = True
    )

if Clean:
    tclean(
        vis = 'synobs_data/synobs_data.vla.cnb.noisy.ms',
        imagename = 'synobs_data/clean_I',
        imsize = 400,
        cell = '0.03arcsec',
        reffreq = '44GHz', 
        specmode = 'mfs',
        gridder = 'standard',
        deconvolver = 'multiscale',
        scales = [1, 8, 20], 
        weighting = 'briggs',
        robust = 0.0,
        uvtaper = '0.1arcsec',
        niter = 10000,
        threshold = '4e-5Jy',
        mask = 'centerbox[[200pix, 200pix], [50pix, 50pix]]', 
        pbcor = True, 
        interactive = True,
        verbose = True
    )

    imregrid(
        'synobs_data/clean_I.image', 
        template='synobs_data/synobs_data.vla.cnb.skymodel.flat', 
        output='synobs_data/clean_I.image_modelsize', 
        overwrite=True
    )
    exportfits(
        'synobs_data/clean_I.image_modelsize', 
        fitsimage='synobs_I.fits', 
        dropstokes=True, 
        dropdeg=True, 
        overwrite=True
    )

