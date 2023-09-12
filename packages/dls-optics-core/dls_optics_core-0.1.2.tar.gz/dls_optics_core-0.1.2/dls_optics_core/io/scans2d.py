'''Module for loading 2D data sets where each point is a complete scan'''

import numpy as np


class Scan2DLoader:
    '''2D scan loader.

    Load a set of 2D data where each data points is itself a scan.
    '''
    def __init__(self, x_points, y_points, start_scans, scan_list_builder):
        self.x_points = x_points
        self.y_points = y_points
        self.start_scans = start_scans
        self.scan_list_builder = scan_list_builder
        self.data = []
        self.scan_files = []


    def load_scans(self, skiprows=0):
        '''Load the data from the files defined in the scan list builder
        and return a 2D list of the data.
        '''
        self.data = []
        self.scan_files = []

        for i in range(len(self.x_points)):
            self.scan_list_builder.scan_number = self.start_scans[i]
            scan_list = self.scan_list_builder.build_list()
            self.scan_files.append(scan_list)

            tmp_data = []

            for path in scan_list:
                print('Loading ' + path + '...')
                tmp_data.append(np.asarray(np.loadtxt(path, skiprows=skiprows)))

            self.data.append(tmp_data)

        return self.data, self.scan_files
