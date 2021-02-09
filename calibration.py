import numpy as np
import re
import os

def clean_raw_data(sensor_raw, outlier_factor = 2):
    '''
    sensor_raw is an (n, 4) numpy array (Bx, By, Bz, Temp_out) of raw analog input reading
    raw_filt detects outliers and replaces them with their respective mean value
    function returns a (4,) numpy array of recalculated mean values
    '''
    raw_mean = np.mean(sensor_raw, axis=0)
    raw_stdev = np.std(sensor_raw, axis=0, ddof=1)
    raw_filt = (sensor_raw > -outlier_factor*raw_stdev+raw_mean) & (sensor_raw < outlier_factor*raw_stdev+raw_mean)
    raw_cleaned = np.where(raw_filt, sensor_raw, raw_mean)
    return np.mean(raw_cleaned, axis=0)


def get_xyz_calib_values(path: str):
    '''
    Input: folder path to hall sensor calibration coefficients
    Output: returns numpy array of coefficients for x, y, and z
    array shape (3, 3, 7).
    '''
    files = [i for i in os.listdir(path) if '.txt' in i]
    files_dict = {}
    for i in files:
        with open(f'{path}/{i}', 'r') as contents:
            files_dict[i] = contents.read()
    coeffs_re = re.compile(r'\d+\.\d{7}')
    coeffs_dict = {}
    for i, j in files_dict.items():
        coeffs_dict[i] = re.findall(coeffs_re, j)
        coeffs_dict[i] = np.array(coeffs_dict[i]).astype('float').reshape((3,7))
    xyz_coeffs = np.array([i for i in coeffs_dict.values()])
    return xyz_coeffs

def calib_data(calib_coeffs, sensor_data, sensitivity=5):
    '''
    Arguments:
        calib_coeffs is a (3,3,7) numpy array of calibration coefficients
        sensitivity is the volts per tesla of the probe.  Use only either 5 (2 T range) or 100 (100 mT range)
        default range is 2 T
        sensor_data should be a (4,) numpy array (Bx, By, Bz, Temperature(in volts))
        sensor_data can either be cleaned or raw data.  Must have shape (n, 4) for raw data.
    Returns:
        function returns calibrated hall sensor readings (Bx,By,Bz)
    '''
    if sensor_data.shape != (4,):
        sensor_data = clean_raw_data(sensor_data)

    Bxyz = sensor_data[:3]
    temp_v = calib_coeffs[0, 0, 6]*sensor_data[3] + calib_coeffs[0, 0, 5]
    if sensitivity == 5:
        k1 = calib_coeffs[:, 2, 0]
        k2 = calib_coeffs[:, 2, 1]
        k3 = calib_coeffs[:, 2, 2]
        k4 = calib_coeffs[:, 2, 3]
        k5 = calib_coeffs[:, 2, 4]
    elif sensitivity == 100:
        k1 = calib_coeffs[:, 0, 0]
        k2 = calib_coeffs[:, 0, 1]
        k3 = calib_coeffs[:, 0, 2]
        k4 = calib_coeffs[:, 0, 3]
        k5 = calib_coeffs[:, 0, 4]
    else:
        print('Invalid sensitivity value')
    xyz_prime = k1 + Bxyz
    xyz_dbl_prime = k2 * xyz_prime**3 + xyz_prime
    xyz_cal_mT = (2 * (k5 * (xyz_dbl_prime + xyz_dbl_prime * k3 * temp_v + k4 * temp_v)) / sensitivity) * 1000
    return xyz_cal_mT

if __name__ == "__main__":
    path = 'C:/Users/dyeagly/Documents/hall_probe/hall_probe/Hall probe 443-20'
    calib_coeffs = get_xyz_calib_values(path)
    print(calib_coeffs)
    print(calib_coeffs.shape)
    print('x coefficients\n', calib_coeffs[0])
    print('y coefficients\n', calib_coeffs[1])
    print('z coefficients\n', calib_coeffs[2])
    print('k1\n', calib_coeffs[:, 2, 0])
    print('k1\n', calib_coeffs[:, 2, 0].shape)