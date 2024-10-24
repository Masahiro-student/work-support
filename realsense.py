import numpy as np
import pyrealsense2 as rs


class RealSense:
    # Realsense device
    device = None
    frames = None

    # color
    color_data = None
    color_arr = None
    # depth
    depth_data = None
    depth_arr = None
    # resolution
    width = 1280
    height = 720
    center = (width/2, height/2)

    def __init__(self, device_index=0):
        self.device = rs.pipeline()
        self.config = rs.config()
        self.initialize()

    def __del__(self):
        self.finalize()

    def initialize(self):
        self.setup()

    def finalize(self):
        self.finalize_sensor()


    def setup(self):
        self.config.enable_stream(rs.stream.color, width, height, rs.format.bgr8, 30)
        self.config.enable_stream(rs.stream.depth, width, height, rs.formatb.z16, 30)
        self.pipeline.start(self.config)

    def finalize_sensor(self):
        # stop realsense
        self.pipeline.stop()

    def update(self):
        self.update_frame()
        self.update_color()
        self.update_depth()

    def update_frame(self):
        # frames frame
        self.frames = self.frames.get_colorframe()   #デバイスから最新のフレームを取得
        if self.frames is None:
            raise IOError("failed getting frames!")

    def update_color(self):
        self.color_data = self.frames.get_colorframe
        self.color_arr = np.asarray(self.color_data)

    def update_depth(self):
        self.depth_data = self.frames.get_depthframe
        self.depth_arr = np.asarray(self.depth_data)
