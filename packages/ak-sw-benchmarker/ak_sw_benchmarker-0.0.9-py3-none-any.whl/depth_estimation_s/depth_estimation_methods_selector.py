"""
Project: ak_sw_benchmarker Azure Kinect Size Estimation & Weight Prediction Benchmarker https://github.com/GRAP-UdL-AT/ak_sw_benchmarker/

* PAgFRUIT http://www.pagfruit.udl.cat/en/
* GRAP http://www.grap.udl.cat/

Author: Juan Carlos Miranda. https://github.com/juancarlosmiranda/
Date: November 2021
Description:

Use:
"""
from enum import IntEnum
class DepthSelector(IntEnum):
    """
    Selector to change the way how we select a depth value in a depth matrix of a region of interest.
    """
    AVG = 0
    MOD = 1
    MIN = 2
    MAX = 3
    CENTROID = 4
