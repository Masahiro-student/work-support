import numpy as np
import k4a
from config.kinect_config import KinectConfig


class Kinect:
    # kinect device
    device = None
    capture = None

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
        self.device = k4a.Device.open(device_index)
        self.initialize()

    def __del__(self):
        self.finalize()

    def initialize(self):
        self.setup()

    def finalize(self):
        self.finalize_sensor()

    def start_camera(self):
        # start cameras
        device_config = k4a.DeviceConfiguration(
                color_format=k4a.EImageFormat.COLOR_BGRA32,
                color_resolution=k4a.EColorResolution.RES_720P,
                depth_mode=k4a.EDepthMode.NFOV_UNBINNED,
                camera_fps=k4a.EFramesPerSecond.FPS_15,
                synchronized_images_only=True,
                )
        status = self.device.start_cameras(device_config)

        
        if status != k4a.EStatus.SUCCEEDED:
            raise IOError("failed starting cameras!")
        # k4a.DeviceSetColorControl(self.device, k4a.ColorControlCommand.BRIGHTNESS, k4a.ColorControlMode.MANUAL, 50)

    def setup(self):
        self.__config = KinectConfig()
        color_control_mode, color_control_commands = self._get_color_control_config()
        for color_control_command, value in color_control_commands:
            status = self.device.set_color_control(
                color_control_command,
                color_control_mode,
                value
            )
            if status != k4a.EStatus.SUCCEEDED:
                raise Exception("failed to set color control")

        self.start_camera()

        # 露光時間の確認用
        (saved_value, mode) = self.device.get_color_control(
            k4a.EColorControlCommand.EXPOSURE_TIME_ABSOLUTE
        )
        print(f"exposure time: {saved_value}")
        print(f"exposure mode: {mode}")

        calibration = self.get_calibration()
        self.__transform = k4a.Transformation(calibration)

        print("setup successfully finished")

    def _get_device_config(self):
        return self.__config.get_device_config()
    
    def _get_color_control_config(self):
        return self.__config.get_color_control_config()

    def get_calibration(self):
        device_config = self._get_device_config()
        calibration = self.device.get_calibration(
            depth_mode = device_config.depth_mode,
            color_resolution = device_config.color_resolution,
        )
        return calibration

    def finalize_sensor(self):
        # stop cameras
        self.device.stop_cameras()
        self.device.close()

    def update(self):
        self.update_frame()
        self.update_color()
        self.update_depth()

    def update_frame(self):
        # capture frame
        self.frame = self.pipeline.get_capture(-1)   #デバイスから最新のフレームを取得
        if self.capture is None:
            raise IOError("failed getting capture!")

    def update_color(self):
        self.color_data = self.capture.color.data
        self.color_arr = np.asarray(self.color_data)

    def update_depth(self):
        self.depth_data = self.capture.depth.data
        self.depth_arr = np.asarray(self.depth_data)
