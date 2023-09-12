"""scanlist module.

This module contains a class ScanList which can be used to construct lists of
complete file paths based on several schemas.
"""

from os.path import join


class ScanList:
    """ScanList class.

    This class can be used to generate sequential lists of file paths based on
    several schemas.
    """
    def __init__(self, path, scan_number=1, ext='.dat', prefix='',
                 suffix='', n_scans=1, format_str=''):
        """Minimum requirement for initializing ScanList is the path to the
        directory containting the scan files.

        Args:
            path -- directory containing scan files
            scan_number -- first file number in list of scans (default 1)
            ext -- scan file extension (default .dat)
            prefix -- scan file prefix (default '')
            suffix -- scan file suffix (default '')
            n_scans -- number of scans in sequential list (default 1)
            format_str -- format string for sequential numbering (default '')
        """
        self.path = path
        self.scan_number = scan_number
        self.ext = ext
        self.prefix = prefix
        self.suffix = suffix
        self.n_scans = n_scans
        self.format_str = format_str

    def build_list(self):
        """Returns sequential list of file paths."""
        scans = []

        for i in range(self.n_scans):
            if self.format_str == '':
                scan_number = str(self.scan_number + i)
            else:
                # n_string = '{' + self.format_str + '}'
                # scan_number = n_string.format(self.scan_number + 1)
                scan_number = format(self.scan_number + i, self.format_str)

            scans.append(self.get_full_path(self.path, self.prefix,
                                            scan_number, self.suffix,
                                            self.ext))

        if self.n_scans == 1:
            return scans[0]

        return scans

    def from_array(self, scan_numbers):
        """Returns list of file paths based on supplied list of scan
        numbers.

        Args:
            scan_numbers -- array of integer scan numbers

        Returns:
            Array containing all the generated paths from the input array.
        """
        scan_list = []

        for n in scan_numbers:
            scan_list.append(self.get_full_path(self.path, self.prefix, n,
                                                self.suffix, self.ext))

        return scan_list

    def get_full_path(self, path, prefix, scan_number, suffix, ext):
        return join(path, prefix + str(scan_number) + suffix + ext)
