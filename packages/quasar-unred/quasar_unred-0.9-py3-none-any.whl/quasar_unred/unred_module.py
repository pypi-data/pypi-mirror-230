import warnings
import matplotlib.pyplot as plt
import numpy as np
import sys, os
from scipy import stats
from scipy.spatial.distance import euclidean

from astropy.modeling.fitting import LevMarLSQFitter
from astropy.stats import sigma_clip
import astropy.units as u

from dust_extinction import shapes



def load_template(file_name = "qso_template.txt"):
    """
    Loads in template that is used for reddening

    Parameters
    ----------
    file_name: path to .txt file
        .txt file containing the data of a quasar template. Should be two columns,
        first of wavelengths and second of flux.
        Default is template from Glikman et al (2006) that is included in repo


    Returns
    -------
    template_wave: np.array
        Numpy array of template wavelengths

    template_flux: np.array
        Numpy array of template flux

    """

    #Load in the data file
    template_data = np.loadtxt(file_name)

    #Access the two columns of data
    template_wavelength = template_data[:,0]
    template_flux = template_data[:,1]

    #dust_extinction code accepts wavelength range of 912->32000 angstrom, remove values outside this range
    for i in range(template_wavelength. size -1,-1,-1):

        if(template_wavelength[i] < 912 or template_wavelength[i] > 32000):
            template_wavelength = np.delete(template_wavelength, i)
            template_flux = np.delete(template_flux, i)

    return template_wavelength, template_flux

def extinguish(wavelengths, flux, redden_bool, Ebv, c1 = -4.9, c2 = 2.3, c3 = 0, c4 = 0.4):
    """
    Either redden or deredden an input data set with custom c-values

    Parameters
    ----------
    wavelengths: np.array
        wavelengths of quasar spectra that is to be reddened/dereddened

    flux: np.array
        flux of quasar spectra that is to be reddened/dereddened

    redden_bool: boolean
        If true, will return reddened data, if false will return dereddened

    Ebv: float
        E(B-V) value

    c1 -> c4: float
        c-values to use, have default values as seen above

    Returns
    -------
    ext_flux: np.array
        the reddened or dereddened flux, still aligned with input wavelengths


    """

    data_set_size = wavelengths.size

    #Apply the astropy units to the array
    wavelengths*=u.angstrom

    optnir_axav_x = 10000.0 / np.array(
            [26500.0, 12200.0, 6000.0, 5470.0, 4670.0, 4110.0]
        )

    Rv = 3.1
    opt_axebv_y = np.array(
    [
                -0.426 + 1.0044 * Rv,
                -0.050 + 1.0016 * Rv,
                0.701 + 1.0016 * Rv,
                1.208 + 1.0032 * Rv - 0.00033 * (Rv ** 2),
            ]
        )
    nir_axebv_y = np.array([0.265, 0.829]) * Rv / 3.1
    optnir_axebv_y = np.concatenate([nir_axebv_y, opt_axebv_y])

    axavs = np.arange(data_set_size, dtype=float)

    axav = shapes._curve_F99_method(wavelengths, Rv, c1, c2, c3, c4 ,4.596, 0.99, optnir_axav_x, optnir_axebv_y / Rv,[0, 1000000], "test")

    #calculate the fractional extinction for each value
    frac_ext = np.arange(data_set_size, dtype=float)
    for i in range(data_set_size):

        Av = Rv * Ebv
        ext = np.power(10.0, -0.4 * axav[i] * Av)
        frac_ext[i] = ext

    #Now either redden or deredden depending on redden_bool
    ext_flux = np.arange(data_set_size, dtype=float)
    if(redden_bool):
        for i in range(data_set_size):
            ext_flux[i] = flux[i]*frac_ext[i]
    else:
        for i in range(data_set_size):
            ext_flux[i] = flux[i]/frac_ext[i]

    return ext_flux

#Takes in the template wavelenghts and the spectrum wavelengths both as numpy arrays
def fit_composite(template_wavelength, template_flux, spectrum_wavelength, spectrum_flux):
    """
    Finds the scaling factor between the template and the input spectrum

    Parameters
    ----------
    template_wavelength: np.array
        wavelength array of quasar template

    template_flux: np.array
        flux array of quasar template

    spectrum_wavelength: np.array
        wavelength array of observed quasar

    spectrum_flux: np.array
        flux array of observed quasar


    Returns
    -------
    ext_flux: float
        scaling factor between template and observed quasar

    """

    #First find min and max of template
    wmin = np.amin(template_wavelength).item()
    wmax = np.amax(template_wavelength).item()

    #Find the indices of the spectrum that are within this range
    w1 = np.where(spectrum_wavelength > wmin)
    w2 = np.where(spectrum_wavelength < wmax)
    ww = np.intersect1d(w1, w2)

    wave0 = spectrum_wavelength[ww]
    spectrum_flux = spectrum_flux[ww]

    # shift the spectrum onto the template array
    refflux = np.interp(wave0, template_wavelength, template_flux)

    rat_array = spectrum_flux / refflux
    rat_array = rat_array[np.where(~np.isnan(rat_array))]

    # divide the flux array in half
    rat = np.array_split(rat_array,3)[2]
    srat = np.median(rat)

    return srat

#Given spectrum data, srat, and redshift returns E(B-V)
def find_ebv(template_wavelength, template_flux, spectrum_wavelength, spectrum_flux,  srat, z):
    """
    Finds the scaling factor between the template and the input spectrum

    Parameters
    ----------

    template_wavelength: np.array
        wavelength array of quasar template

    template_flux: np.array
        flux array of quasar template

    spectrum_wavelength: np.array
        wavelength array of observed quasar

    spectrum_flux: np.array
        flux array of observed quasar

    srat: float
        scaling ration determined in fit composite

    z: float
        redshift of observed quasar


    Returns
    -------

    **See derivation in readme and should be clearer**

    ebv: float
        E(B-V) value that caused the reddening in observed quasar

    xx: array
        ln(funred) = k(lambda)/1.086

    pt: array
        ln(observed flux / template flux)

    yInt: float
        y-intercept of spectrum

    """

    #Remove nan's from the data
    spectrum_flux = spectrum_flux[~np.isnan(spectrum_wavelength)]
    spectrum_wavelength = spectrum_wavelength[~np.isnan(spectrum_wavelength)]
    spectrum_wavelength= spectrum_wavelength[~np.isnan(spectrum_flux)]
    spectrum_flux = spectrum_flux[~np.isnan(spectrum_flux)]



    cMask = sigma_clip(spectrum_flux)

    spectrum_wavelength = spectrum_wavelength[~cMask.mask]
    spectrum_flux = spectrum_flux[~cMask.mask]


    temporary_wave = spectrum_wavelength
    temporary_flux = spectrum_flux

    #cut where lt 1216, this accounts for the lyman alpha forest
    #sometimes cutting at ~2200 is necessary, trying to figure out how to tell automatically.
    for i in range(spectrum_wavelength.size -1,-1,-1):
        if(spectrum_wavelength[i] < 1216):
            spectrum_wavelength = np.delete(spectrum_wavelength,i)
            spectrum_flux = np.delete(spectrum_flux,i)

    #remove around emission lines
    lines = [1216, 1550, 2800, 4861, 5000, 6563]
    for i in range(6):
        curLine = lines[i]
        l1 = curLine*0.96
        l2 = curLine*1.04

        for j in range(len(spectrum_wavelength)):
            if l1 < spectrum_wavelength[j] and l2 > spectrum_wavelength[j]:

                temporary_wave = np.delete(spectrum_wavelength, j)
                temporary_flux = np.delete(spectrum_flux, j)

    spectrum_wavelength = temporary_wave
    spectrum_flux = temporary_flux

    funred = extinguish(spectrum_wavelength, 0 * spectrum_wavelength + 1, True, 1.0)

    ref =  np.interp(spectrum_wavelength, template_wavelength, template_flux) * srat

    pt = np.zeros(len(ref))


    w = np.where(spectrum_flux > 0)
    pt[w] = np.log(spectrum_flux[w] / ref[w])

    #print('positive flux interpolated onto the template',pt[w].size)

    new_mask = sigma_clip(pt,sigma=3)

    pt = pt[~new_mask.mask]
    funred = funred[~new_mask.mask]
    ref = ref[~new_mask.mask]

    xx = np.log(funred)

    coeff = np.polyfit(xx, pt, 1)

    ebv = coeff[0]
    yInt = coeff[1]

    fitted_curve = ref*np.exp(yInt+ebv*xx)
    adjusted_wave = spectrum_wavelength[~new_mask.mask]
    spure = ref*np.exp(coeff[1])
    #print(ebv)
    #plt.plot(spectrum_wavelength[w],spectrum_flux[w],color='gray')
    #plt.plot(spectrum_wavelength[~new_mask.mask],fitted_curve,color='r')
    #plt.plot(spectrum_wavelength[~new_mask.mask],spure,color='b')
    #plt.yscale("log")

    return (ebv, xx, pt, yInt, fitted_curve, adjusted_wave)


# perturb the best-fit model spectrum by the error array
def mc_spec(temp_wave, temp_flux, err, obs_wave, obs_flux, srat, z, ntrials = 100):
    """
    Finds the uncertainty in measured E(B-V) using random sampling from error array

    Parameters
    ----------

    temp_wave: np.array
        wavelength array of quasar template

    temp_flux: np.array
        flux array of

    err: np.array
        error array of quasar template

    obs_wave: np.array
        wavelength array of observed quasar

    obs_flux: np.array
        flux array of observed quasar

    srat: float
        scaling ratio determined in fit composite

    z: float
        redshift of observed quasar

    ntrials: int
        Number of trials for error calculation. Defaults to 100


    Returns
    -------

    sig_ebv: float
        error in E(B-V)

    """


    ebv_array_float = np.arange(ntrials,dtype=float)
    ebv_array_int = np.arange(ntrials,dtype=int)

    for loop in range(ntrials):

        sig_modl = obs_wave.copy()

        for ii in np.arange(obs_wave.size, dtype=int):
            sig_modl[ii] = np.random.normal(obs_wave[ii], err[ii], 1)
        try:
            output = find_ebv(temp_wave, temp_flux, sig_modl, obs_flux, srat, z)
            ebv = output[0]
            yInt = output[3]

        except (RuntimeError, ValueError):
            print('Monte Carlo Failed')

        ebv_array_float[loop] = output[0]

    sig_ebv = np.std(ebv_array_float)

    return(sig_ebv)