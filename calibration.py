import numpy as np
import re
import os

def average_sample(sensor_data):
    data = np.mean(sensor_data, axis=0)
    return data

def calib_data(calib_coeffs, sensor_data, sensitivity=5):
    '''
    Arguments:
        calib_coeffs is a (3,3,7) numpy array of calibration coefficients
        sensitivity is the volts per tesla of the probe.  Use only either 5 (2 T range) or 100 (100 mT range)
            default range is 2 T
        sensor_data should be a (n, 4) numpy array (Bx, By, Bz, Temperature(in volts))
    Returns:
        function returns (n, 3) calibrated hall sensor readings (Bx,By,Bz) in mT
    '''
    Bxyz = sensor_data[:, :-1]
    temp_v = calib_coeffs[0, 0, 6] * (sensor_data[:, 3] + calib_coeffs[0, 0, 5])
    temp_v = np.array([temp_v, temp_v, temp_v]).T

    # k values are a (3,) array (x_coeff, y_coeff, z_coeff)
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
    xyz_cal_mT = ((k5 * (xyz_dbl_prime + xyz_dbl_prime * k3 * temp_v + k4 * temp_v)) / sensitivity) * 1000

    return xyz_cal_mT

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
            files_dict[i[:-4]] = contents.read()
    # coeffs_re = re.compile(r'\d+\.\d{7}')
    coeffs_re = re.compile(r'[+-]*\d+\.\d{7}')
    coeffs_dict = {}
    for i, j in files_dict.items():
        coeffs_dict[i] = re.findall(coeffs_re, j)
        coeffs_dict[i] = np.array(coeffs_dict[i]).astype('float').reshape((3,7))
    xyz_coeffs = np.array((coeffs_dict['CalibrationX'],
                           coeffs_dict['CalibrationY'],
                           coeffs_dict['CalibrationZ']))
    return xyz_coeffs

def filter_data(data: np.ndarray, cutoff: int):
    '''
    data: (n,) array of single axis hallsensor data
    cutoff: integer value for level of filter smoothing
    returns (n,) numpy array of filtered sensor data
    '''
    x_delta = 1
    alpha = np.sqrt(np.log(2)/np.pi)
    x_lc = np.arange(-cutoff, cutoff + x_delta, x_delta)
    sx = (1/alpha*cutoff)*np.exp(-np.pi*(x_lc/(alpha*cutoff))**2)
    sx_norm = sx/np.sum(sx)
    filtered = np.convolve(data, sx_norm, mode='same')
    return filtered

def fit_linear(x, y):
    x_m = np.mean(x)
    y_m = np.mean(y)
    x_dev = x - x_m
    y_dev = y - y_m
    xy_dev = x_dev * y_dev
    xsq_dev = x_dev**2
    m = np.sum(xy_dev)/np.sum(xsq_dev)
    b = y_m - m * x_m
    return np.array([m, b])


# def orthogonalize(cube_data: np.ndarray):
#     '''
#     cube_data is a (12, 3) array
#     function returns (3,3) array
#     '''
#     v1 = np.mean(cube_data[:4], axis=0)
#     v2 = np.mean(cube_data[4:8], axis=0)
#     v3 = np.mean(cube_data[8:], axis=0)
#     e_hat1 = v1/np.linalg.norm(v1)
#     e2 = v2 - np.dot(v2, e_hat1)*e_hat1
#     e_hat2 = e2/np.linalg.norm(e2)
#     e3 = v3 - np.dot(v3, e_hat1)*e_hat1 - np.dot(v3, e_hat2)*e_hat2
#     e_hat3 = e3/np.linalg.norm(e3)
#     S = np.array([e_hat1, e_hat2, e_hat3])
#     return S

# def orthogonalize(cube_data: np.ndarray):
#     '''
#     cube_data is a (12, 3) array
#     function returns (3,3) array
#     Rewritten March 7, Erik Wallen
#     '''
#     v1 = np.mean(cube_data[:4], axis=0)
#     v2 = np.mean(cube_data[4:8], axis=0)
#     v3 = np.mean(cube_data[8:], axis=0)
#     e_hat1 = v1/np.linalg.norm(v1)
#     e_hat2 = v2/np.linalg.norm(v2)
#     e_hat3 = v3/np.linalg.norm(v3)
#     S = np.linalg.inv(np.array([e_hat1, e_hat2, e_hat3]))
#     return S

def orthogonalize(cube_data: np.ndarray):
    '''
    cube_data is a (12, 3) array
    function returns (3,3) array
    Rewritten March 8, Erik Wallen
    '''
    v1 = np.mean(cube_data[:4], axis=0)
    v2 = np.mean(cube_data[4:8], axis=0)
    v3 = np.mean(cube_data[8:], axis=0)
    cubefield=np.max(np.abs(cube_data))
    e_hat1 = v1/cubefield
    e_hat2 = v2/cubefield
    e_hat3 = v3/cubefield
    S = np.array([e_hat1, e_hat2, e_hat3])
    return S

def remove_outliers(sensor_data, stdev=2, iterations=1):
    '''
    sensor_data is an (n, m) numpy array of 
        raw or calibrated hall sensor or temperature sensor data
    raw_filt detects outliers and replaces them with their respective mean value
    function returns a (m,) numpy array of recalculated mean values
    '''
    raw_mean = np.mean(sensor_data, axis=0)
    raw_stdev = np.std(sensor_data, axis=0, ddof=1)
    raw_filt = (sensor_data > -stdev*raw_stdev+raw_mean) & (sensor_data < stdev*raw_stdev+raw_mean)
    raw_cleaned = np.where(raw_filt, sensor_data, raw_mean)
    # print('iteration 1')
    if iterations > 1:
        for iteration in range(iterations-1):
            # print(f'iteration {iteration+2}')
            raw_mean = np.mean(raw_cleaned, axis=0)
            raw_stdev = np.std(raw_cleaned, axis=0, ddof=1)
            raw_filt = (raw_cleaned > -stdev*raw_stdev+raw_mean) & (raw_cleaned < stdev*raw_stdev+raw_mean)
            raw_cleaned = np.where(raw_filt, raw_cleaned, raw_mean)
    return raw_cleaned


if __name__ == "__main__":
    path = 'C:/Users/dyeagly/Documents/hall_probe/hall_probe/Hall probe 444-20'
    calib_coeffs = get_xyz_calib_values(path)
    print(calib_coeffs)
    print(calib_coeffs.shape)
    print('x coefficients\n', calib_coeffs[0])
    print('y coefficients\n', calib_coeffs[1])
    print('z coefficients\n', calib_coeffs[2])
    print('k1\n', calib_coeffs[:, 2, 0])
    print('k1\n', calib_coeffs[:, 2, 0].shape)
    scan_data = np.genfromtxt('scan_data.txt', delimiter=' ', skip_header=1)
    print('scan_data shape:', scan_data.shape)
    sensor_data = scan_data[:, 3:]
    print('sensor_data shape:', sensor_data.shape)
    sensor_calib = calib_data(calib_coeffs, sensor_data)
    print('uncalibrated data:\n', sensor_data[:10])
    print('calibrated data:\n', sensor_calib[:10])