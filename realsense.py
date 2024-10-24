import numpy as np
import pyrealsense2 as rs


class RealSense:
    def __init__(self, device_index=0):
        self.pipeline = rs.pipeline()
        self.config = rs.config()
        self.setup()

    def __del__(self):
        self.finalize()


    def finalize(self):
        self.finalize_sensor()


    def setup(self):
        width = 1280
        height = 720
        self.config.enable_stream(rs.stream.color, width, height, rs.format.bgr8, 30)
        #  self.config.enable_stream(rs.stream.depth, width, height, rs.format.z16, 30)
        self.pipeline.start(self.config)

    def finalize_sensor(self):
        # stop realsense
        self.pipeline.stop()

    def update(self):
        self.update_frame()
        self.update_color()
        #  self.update_depth()

    def update_frame(self):
        self.frame = self.pipeline.wait_for_frames()

    def update_color(self):
        color_frame = self.frame.get_color_frame()

        if not color_frame:
            return

        self.color_image = np.asanyarray(color_frame.get_data())


    def update_depth(self):
        self.depth_data = self.frame.get_depthframe()
        self.depth_arr = np.asanyarray(self.depth_data)

if __name__ == '__main__':
    rs = RealSense()

    while True:
        rs.update()
        

        
    
