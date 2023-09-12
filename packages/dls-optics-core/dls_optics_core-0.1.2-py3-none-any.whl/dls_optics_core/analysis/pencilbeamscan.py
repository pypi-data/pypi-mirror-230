from PIL import Image
from optics.io import Nexus
from optics.analysis import image as opim
import numpy as np
import os
import sys
from lmfit.models import GaussianModel


class PencilBeamScan:
    def __init__(self):
        self.mirror_length = 1.4
        self.source_mirror_distance = 12.8
        self.source_slit_distance = 10.48
        self.mirror_screen_distance = 6.979
        self.scale_factor = 40.0*1e3/811.0
        self.start_offset = 0
        self.end_offset = 0
        self.rotate_images = False
        self._use_roi = False
        self.roi_start_x = 0
        self.roi_end_x = 0
        self.roi_start_y = 0
        self.roi_end_y = 0
        self.image_stack = None
        self.reverse_scan_direction = False
        self.slit_start = -3000 # start position of slit centre in um
        self.slit_step = 100 # % slit centre step size in um
        self.slit_gap = 100 # slit gap size in um
        self.screen_after_focus = False
        self.processed = False

        self.peak_x = None
        self.peak_y = None
        self.peak_max = None
        self.pixel_position = None
        self.sigmas = None
        self.median_y = 0

        self.mirror_position = None
        self.screen_position = None
        self.relative_slit_position = None
        self.beam_width = None
        self.focus_distance = 0

    @property
    def use_roi(self):
        return self._use_roi

    @use_roi.setter
    def use_roi(self, val):
        if self._use_roi and not val and self.processed:
            self.processed = False

        self._use_roi = val

    @property
    def total_images(self):
        if self.image_stack is None:
            return 0

        return self.image_stack.shape[2]

    @property
    def slope_error_rms(self):
        if self.slope_error is None:
            return -1

        return np.std(self.slope_error)

    @property
    def height_error_rms(self):
        if self.height_error is None:
            return -1

        return np.std(self.height_error)

    def set_roi(self, startx, endx, starty, endy):
        self.roi_start_x = startx
        self.roi_end_x = endx
        self.roi_start_y = starty
        self.roi_end_y = endy

    def load_from_nexus(self, file_path, entry=None, finished_cb=None):
        self.processed = False

        if entry is None:
            entry = ['/entry/instrument/detector/data']

        nexus = Nexus(groupstoload=entry)
        data = nexus.load_data(file_path)
        width, height, depth, _ = data.shape

        self.image_stack = np.reshape(data, (width, height, depth))
        self.roi_start_x = 0
        self.roi_end_x = width - 1
        self.roi_start_y = 0
        self.roi_end_y = height - 1

        if finished_cb:
            finished_cb()

    def load_from_list(self, file_list, update_cb=None, finished_cb=None):
        self.processed = False

        n_files = len(file_list)

        if update_cb:
            update_cb(100*1/n_files)

        # load first image to check size
        im = Image.open(file_list[0])
        width, height = im.size

        stack = np.reshape(np.transpose(np.array(im)), (width, height, 1))
        im.close()

        for i in range(1, n_files):
            if update_cb:
                update_cb(100*(i + 1)/n_files)

            im = Image.open(file_list[i])
            stack = np.concatenate((stack, np.reshape(np.transpose(np.array(im)), (width, height, 1))), axis=2)
            im.close

        self.image_stack = stack
        self.roi_start_x = 0
        self.roi_end_x = width - 1
        self.roi_start_y = 0
        self.roi_end_y = height - 1

        if finished_cb:
            finished_cb()

    def process_stack(self, rotate_images=False, update_cb=None):
        if self.total_images <= 0:
            return

        n_images = self.total_images

        self.peak_x = np.empty((n_images, 1))
        self.peak_y = np.empty_like(self.peak_x)
        self.peak_max = np.empty_like(self.peak_x)
        self.pixel_position = np.empty_like(self.peak_x)
        self.sigmas = np.empty_like(self.peak_x)

        self.x_vals = []
        self.y_vals = []

        stack = self.image_stack
        fix_y = False

        if self.use_roi:
            if (self.roi_start_y == self.roi_end_y) or (self.roi_end_y == -1):
                fix_y = True
                stack = self.image_stack[self.roi_start_x:self.roi_end_x, self.roi_start_y, :]
            else:
                stack = self.image_stack[self.roi_start_x:self.roi_end_x, self.roi_start_y:self.roi_end_y, :]

        for i in range(n_images):
            if fix_y:
                temp_image = stack[:,i]
            else:
                temp_image = stack[:, :, i]

            if rotate_images:
                temp_image = np.transpose(temp_image)

            if fix_y:
                peak_y = self.roi_start_y
            else:
                peak_y, _, _ = opim.find_peak(temp_image)

            mod = GaussianModel()
            pars = None
            x_dim = temp_image.shape[0]
            start_x = self.roi_start_x if self.use_roi else 0
            end_x = self.roi_end_x if self.use_roi else x_dim - 1
            x_vals = np.zeros(1)
            y_vals = np.zeros(1)

            # temp image indexing is [col,row] i.e. [x,y]
            if not np.isnan(peak_y):
                x_vals = np.linspace(start_x, end_x, x_dim)

                if not fix_y:
                    peak_y_index = int(np.floor(peak_y))
                    y_vals = temp_image[:, peak_y_index]
                else:
                    y_vals = temp_image

                if pars is None:
                    pars = mod.guess(y_vals, x=x_vals)

                out = mod.fit(y_vals, pars, x=x_vals)

                self.pixel_position[i] = out.best_values['center']
                self.sigmas[i] = out.best_values['sigma']

            peak_x = int(np.floor(self.pixel_position[i])) + self.roi_start_x if self.use_roi and not fix_y else int(np.floor(self.pixel_position[i]))
            peak_y = peak_y + self.roi_start_y if self.use_roi and not fix_y else peak_y

            # self.x_vals.append(x_vals)
            # self.y_vals.append(y_vals)

            self.peak_x[i] = peak_x
            self.peak_y[i] = peak_y

            if update_cb:
                update_cb(i, peak_x, peak_y, x_vals.tolist(), y_vals.tolist())

        # self.median_y = np.median(self.peak_y)

        self.processed = True

    def calculate_parameters(self):
        n_points = self.total_images - self.start_offset - self.end_offset
        self.mirror_position = np.empty(n_points)
        corrected_screen_distance = np.empty_like(self.mirror_position)
        self.screen_position = np.empty_like(self.mirror_position)
        slope = np.empty_like(self.mirror_position)
        self.relative_slit_position = np.empty_like(self.mirror_position)
        slit_position = np.empty_like(self.mirror_position)
        self.beam_width = np.empty_like(self.mirror_position)

        reverse = 1

        if self.reverse_scan_direction:
            reverse = -1

        for i in range(n_points):
            self.mirror_position[i] = self.mirror_length*i/n_points
            corrected_screen_distance[i] = self.mirror_screen_distance + reverse*(self.mirror_length/2 - self.mirror_position[i])
            self.screen_position[i] = self.pixel_position[i + self.start_offset]*self.scale_factor
            slope[i] = self.screen_position[i]/corrected_screen_distance[i]/2
            self.relative_slit_position[i] = self.slit_step*i
            slit_position[i] = self.slit_start + self.relative_slit_position[i]
            self.beam_width[i] = self.sigmas[i + self.start_offset]*self.scale_factor

        screen_factor = 1

        if self.screen_after_focus:
            screen_factor = -1

        k, c = np.polyfit(self.relative_slit_position, self.screen_position, 1)
        big_r = self.mirror_screen_distance/(self.source_mirror_distance/(abs(k)*self.source_slit_distance) - screen_factor*1)

        self.screen_fit = np.polyval([k, c], self.relative_slit_position)
        self.focus_distance = self.mirror_screen_distance + screen_factor*big_r

        fitted_slope = np.polyfit(self.mirror_position, slope, 1)

        self.slope_error = slope - fitted_slope[0]*self.mirror_position - fitted_slope[1]
        self.height_error = np.cumsum(self.slope_error)*self.mirror_length/n_points;