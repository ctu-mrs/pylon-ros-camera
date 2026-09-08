# MRS ROS2-Driver for Basler Cameras

The MRS fork of the official pylon ROS2 driver for [Basler](http://www.baslerweb.com/) GigE Vision, Basler USB3 Vision and Basler blaze 3D cameras (Jazzy Jalisco)

This driver provides many functionalities available through the Basler [pylon Camera Software Suite](https://www.baslerweb.com/en/products/software/basler-pylon-camera-software-suite/) C++ API.

## Installation

### Prerequisites

- [Ubuntu 24.04 Noble Numbat](https://releases.ubuntu.com/noble/) + [ROS2 Jazzy Jalisco](https://docs.ros.org/en/jazzy/Installation/Ubuntu-Install-Debs.html).

Download the Pylon SDK from the Basler website:
- [pylon Camera Software Suite](https://www2.baslerweb.com/en/downloads/software-downloads/) (version 7.5.0 or newer)
- [pylon Supplementary Package for blaze](https://www2.baslerweb.com/en/downloads/software-downloads/) (version 1.6.0 or newer)

Or obtain all dependencies via [private MRS PPA](https://mrs.fel.cvut.cz/gitlab/internal/ppa-private) using `sudo apt install -y pylon*`.

### Install and build the packages

Clone this repository and build it in your ROS 2 workspace.

Start the driver:  
```
ros2 launch pylon_ros2_camera_wrapper pylon_ros2_camera.launch.py
```


## Usage in a nutshell

Starting the *pylon_ros2_camera_node* starts the acquisition from a given Basler camera. The nodes allow as well to access many camera parameters and parameters related to the grabbing process itself.

The *pylon_ros2_camera_node* can be started thanks to a dedicated launch file thanks to the command:  
``ros2 launch pylon_ros2_camera_wrapper pylon_ros2_camera.launch.py``  or  
``ros2 launch pylon_ros2_camera_wrapper my_blaze.launch.py`` for the blaze  
Several parameters can be set through the launch file and the user parameter file loaded through it (the `pylon_ros2_camera_wrapper/config/default.yaml` user parameter file is loaded by default, `pylon_ros2_camera_wrapper/config/my_blaze.yaml` for the blaze).

Acquisition from a specific camera is possible by setting the `device_user_id` parameter. If no specific camera is specified, the first available camera is connected automatically.  

The pylon node defines the different interface names according to the following convention:  
``[Camera name (= my_camera or my_blaze by default)]/[Node name (= pylon_ros2_camera_node)]/[Interface name]``  
The camera and the node names can be set thanks respectively to the `camera_name` and `node_name` parameters.  

Acquisition images are published through the `[Camera name]/[Node name]/[image_raw]` topic, only if a subscriber to this topic has been registered.  
To visualize the images, [rqt](https://docs.ros.org/en/jazzy/Tutorials/Beginner-CLI-Tools/Introducing-Turtlesim/Introducing-Turtlesim.html#install-rqt) can be used. Add an image viewer plugin through thanks to the contextual menu (Plugin -> Visualization -> Image View) and select the `[Camera name]/[Node name]/[image_raw]` topic to display the acquired and published images. Beware that if you are using rviz2 to visualize the acquired images, this tool is not able not vizualize correctly images encoded in Bayer.  
The 3d point clouds acquired by the blaze can be visualized thanks to [rviz2](https://index.ros.org/p/rviz2/).  

For camera models other than the blaze, specific user set can be specified thanks to the `startup_user_set` parameter.  
``ros2 launch pylon_ros2_camera_wrapper pylon_ros2_camera.launch.py startup_user_set:=Default``  or ``ros2 launch pylon_ros2_camera_wrapper pylon_ros2_camera.launch.py startup_user_set:=UserSet1`` or ``ros2 launch pylon_ros2_camera_wrapper pylon_ros2_camera.launch.py startup_user_set:=UserSet2`` or ``ros2 launch pylon_ros2_camera_wrapper pylon_ros2_camera.launch.py startup_user_set:=UserSet3``  

Through the driver, the camera image acquisition is sequentially triggered by software trigger. It is not possible in the current implementation to change this acquisition mode. In other words, it is not possible through the driver to configure for free run and hardware triggered image acquisition.

Beware that some parameters implemented by the driver, like for instance the parameter `startup_user_set`, can be set through 1. the `pylon_ros2_camera_wrapper/config/default.yaml` user parameter file, 2. the `pylon_ros2_camera.launch.py` driver launch file, and 3. the command line arguments of the launch command to start the driver. A parameter value set as an argument of the launch command to start the driver will overwrite the value set in the driver launch file itself, that will overwrite the value set in the user parameter file.    

### Acquisition mode and frame rate

From version 3.1.0, the driver allows free run as well as sequentially triggered acquisition by software trigger.

When starting the driver, the maximum acquisition frame rate that can be reached according to the current camera settings is displayed (for further information, please refer to the [Basler documentation](https://docs.baslerweb.com/resulting-acquisition-frame-rate)). If this frame rate is lower than the one specified in the driver configuration file, the latter is updated accordingly. Except for the blaze, it is not possible to change the acquisition frame rate when the driver is running.

Free run acquisition is set when the driver starts and loads the `Default` user set. Otherwise, if another user set is loaded, including `CurrentSetting`, the driver does not modify any parameter related to the acqusition, keeping the ones defined by the user. Setting a specific user set can be specified in the driver launch file. By default, the driver load the `CurrentSetting` user set.

- Free run is enabled by setting the following parameters:
```
AcquisitionMode = Continuous
TriggerSelector = FrameStart
TriggerMode = Off
```
- Software triggering is enabled by setting the following parameters:
```
TriggerSelector = FrameStart
TriggerSource = Software
TriggerMode = On
```
More information about acquisition modes can be found [here](https://docs.baslerweb.com/acquisition-mode). The driver does not currently give access to the `AcquisitionMode` parameter and if the `TriggerSource` parameter is not modified, switching from free run to software triggering can be done by setting the `TriggerMode` parameter from `Off` to `On`, and vice versa.

Generally speaking, to increase the acquisition frame rate when using the driver, consider when possible and applicable:
- Switch to free run.
- Changing the image encoding to Bayer or Mono ones.
- Setting a region of interest.
- Decreasing the exposure time.
- Decreasing the inter-packet delay and setting it to 0 if possible.
- Setting the ``enable_current_params_publisher`` parameter to false (it is set to false by default).
- Following the additional suggestions specified in the [Basler documentation](https://docs.baslerweb.com/resulting-acquisition-frame-rate).
- Commenting and modifying the different operations executed in ``PylonROS2CameraNode::spin()``. In addition to grabbing, it checks if the camera is disconnected, publishes images and current settings if there are some subscribers, rectifies images if calibration parameters are available, etc. Beware though that the frame rate increase will not be significant and that the standard driver behaviors will not be guaranteed.

The interested readers can refer to the following discussions for more information: [#21](https://github.com/basler/pylon-ros-camera/issues/21), [#28](https://github.com/basler/pylon-ros-camera/issues/28), [#29](https://github.com/basler/pylon-ros-camera/issues/29), [#81](https://github.com/basler/pylon-ros-camera/issues/81), [#116](https://github.com/basler/pylon-ros-camera/issues/116), [#147](https://github.com/basler/pylon-ros-camera/issues/147), [#200](https://github.com/basler/pylon-ros-camera/issues/200).

### Configuring image publication throughput and latency

The image publication controls are optional parameters that can be added under
`ros__parameters` in any existing camera YAML. Their defaults preserve the
driver's earlier synchronous, reliable behavior, so existing configurations do
not change unless they explicitly opt in.

- `enable_async_image_publishing` (default `false`) separates camera retrieval
  from ROS publication. In synchronous mode, serialization, middleware work, or
  subscriber backpressure can delay the next retrieval. Asynchronous mode lets
  retrieval continue while a dedicated thread publishes the previous image.
- `raw_publish_queue_depth` (default `1`, minimum `1`) bounds the hand-off queue
  between retrieval and publication and is used only in asynchronous mode. If
  it fills, the driver discards the oldest pending image. Depth 1 minimizes
  latency and memory and is normally appropriate for live perception. A larger
  value tolerates short publisher stalls, but can deliver older images and uses
  roughly one additional image buffer per queued frame.
- `use_sensor_data_qos` (default `false`) changes the image publisher from its
  legacy reliable QoS to ROS sensor-data QoS (best effort and volatile). Best
  effort prevents acknowledgements and retransmission of stale frames from
  applying transport backpressure to a live stream. A subscriber must request
  compatible QoS.
- `image_qos_depth` (default `5`, minimum `1`) is the ROS middleware history
  depth used when sensor-data QoS is enabled. It is independent of
  `raw_publish_queue_depth`: one controls middleware history, the other controls
  the driver's acquisition-to-publication hand-off.
- `grab_strategy` controls the Pylon SDK retrieval policy. `0` (`OneByOne`)
  preserves every camera buffer in order, while `1` (`LatestImageOnly`) favors
  the newest frame if acquisition falls behind. Select it independently of ROS
  QoS according to whether completeness or bounded live latency matters more.

For example, the following values favor fresh images and prevent a slow
publisher or subscriber from throttling acquisition. Copy only the parameters
needed into the camera's normal configuration file; tune depths for the image
size, available memory, and acceptable latency.

```yaml
/**:
  ros__parameters:
    enable_async_image_publishing: true
    raw_publish_queue_depth: 1
    use_sensor_data_qos: true
    image_qos_depth: 10
    grab_strategy: 1
```

This configuration keeps acquisition cadence and live latency bounded; it
cannot make a consumer process faster than its own capacity. If publication or
the subscriber falls behind, the bounded driver queue, latest-image Pylon
strategy, and best-effort transport deliberately prefer current frames over
delivering every frame. Use the synchronous/reliable defaults and sufficient
buffering instead when every acquired frame must be delivered.

Zenoh session selection is process environment configuration, not a camera
parameter. Set `ZENOH_SESSION_CONFIG_URI` in `.bashrc`, or export it in the
current shell, before starting any ROS 2 nodes. The camera wrapper inherits the
environment and does not interpret or override the session configuration.

```bash
export ZENOH_SESSION_CONFIG_URI=/absolute/path/to/session.json5
ros2 launch pylon_ros2_camera_wrapper pylon_ros2_camera.launch.py \
  config_file:=/absolute/path/to/camera.yaml
```

At multi-megabyte image sizes, the Python `ros2 topic hz image_raw` command can
itself become the receiver bottleneck and report dropped samples even when the
camera and a native subscriber sustain the configured rate. Use a lightweight
topic such as `camera_info` to check acquisition cadence, and validate image
throughput, end-to-end latency, and drops with the real consumer or a native
benchmark subscriber.

### Image pixel encoding (not for the blaze)

The pylon ROS2 driver support currently the following ROS2 image pixel formats :

	* mono8	        (Basler Format : Mono8)
	* mono16	(Basler Format : Mono16, Mono12)        (Notes 1&2)
	* bgr8 		(Basler Format : BGR8)
	* rgb8 		(Basler Format : RGB8)
	* bayer_bggr8 	(Basler Format : BayerBG8)
	* bayer_gbrg8 	(Basler Format : BayerGB8)
	* bayer_rggb8 	(Basler Format : BayerRG8)
	* bayer_grbg8 	(Basler Format : BayerRG8)
	* bayer_rggb16	(Basler Format : BayerRG16, BayerRG12)  (Notes 1&2)
	* bayer_bggr16 	(Basler Format : BayerBG16, BayerBG12)  (Notes 1&2)
	* bayer_gbrg16 	(Basler Format : BayerGB16, BayerGB12)  (Notes 1&2)
	* bayer_grbg16 	(Basler Format : BayerGR16, BayerGR12)  (Notes 1&2)

More information about the image encoding can be found in the [Basler documentation](https://docs.baslerweb.com/pixel-format).

**NOTES:**

1 : 12-bits image will be remapped to 16-bits using bit shifting to make it work with the ROS2 16-bits sensor standard message.

2 : When the user calls the `set_image_encoding` service to use 16-bits encoding, the driver will check first for the availability of the requested 16-bits encoding to set it, when the requested 16-bits image encoding is not available, then the driver will check the availability of the equivalent 12-bits encoding to set it. When both 16-bits and 12-bits image encoding are not available then an error message will be returned.

### Intrinsic calibration and rectified images (not for the blaze)

ROS2 includes a standardised camera intrinsic calibration process through the *camera_calibration* package. This calibration process generates a file, which can be processed by the pylon ROS2 driver by setting the `camera_info_url` parameter in the `pylon_ros2_camera_wrapper/config/default.yaml` file (it is the user parameter file loaded by default through the driver main launch file) to the correct URI (e.g., file:///home/user/data/calibrations/my_calibration.yaml).

If the calibration is valid, the rectified images are published through the `[Camera name]/[Node name]/[image_rect]` topic, only if a subscriber to this topic has been registered.

### Setting device user id

It is easily possible to connect to a specific camera through its user id. This user id can be set through the parameter `device_user_id` listed in the .yaml user parameter file loaded at launch time (by default `pylon_ros2_camera_wrapper/config/default.yaml`). It is up to the user to create specific launch files, loading specific .yaml user parameter files, which would specify the user ids of the cameras that need to be connected. If no specific camera is specified, either because the `device_user_id` parameter is not set or no .yaml user parameter file is loaded, the first available camera is connected automatically.  

In addition to being able to do so through the pylon Viewer provided by Basler, it is possible to set the device user id with the command: `ros2 run pylon_ros2_camera_component set_device_user_id [-sn SERIAL_NB] your_device_user_id`. If no serial number is specified thanks to the option `-sn`, the specified device user id `your_device_user_id` will be assigned to the first available camera.
USB cameras must be disconnected and then reconnected after setting a new device user id. USB cameras keep their old user id otherwise.


## Packages

- **pylon_ros2_camera_component**: the driver itself. The package includes the main *pylon_ros2_camera_node* developed as a component.
- **pylon_ros2_camera_wrapper**: wrapper creating the main component `pylon_ros2_camera::PylonROS2CameraNode` implemented in the *pylon_ros2_camera_component* package. The wrapper starts the driver in a single process.
- **pylon_ros2_camera_interfaces**: package implementing *pylon_ros2_camera_node* interfaces (messages, services and actions).


## Parameters

**Common parameters**

- **camera_frame**  
  The tf2 frame under which the images were published.  
  ROS2 provides a library called [tf2](https://docs.ros.org/en/jazzy/Concepts/Intermediate/About-Tf2.html) (*TransForm* version 2) to manage the coordinate transformations between the different frames (coordinate systems) defined by the user and assigned to the components of a robotics system.

- **device_user_id**  
  The DeviceUserID of the camera. If empty, the first camera found in the device list will be used.

- **camera_info_url (not for the blaze)**  
  The CameraInfo URL (Uniform Resource Locator) where the optional intrinsic camera calibration parameters are stored. This URL string will be parsed from the CameraInfoManager.

- **image_encoding (not for the blaze)**  
  The encoding of the pixels -- channel meaning, ordering, size taken from the list of strings in include file *sensor_msgs/image_encodings.h*. The supported encodings are 'mono8', 'bgr8', 'rgb8', 'bayer_bggr8', 'bayer_gbrg8' and 'bayer_rggb8'. Default values are 'mono8' and 'rgb8'.

- **binning_x & binning_y (not for the blaze)**  
  Binning factor to get downsampled images. It refers here to any camera setting which combines rectangular neighborhoods of pixels into larger "super-pixels." It reduces the resolution of the output image to (width / binning_x) x (height / binning_y). The default values binning_x = binning_y = 0 are considered the same as binning_x = binning_y = 1 (no subsampling).

- **downsampling_factor_exposure_search (not for the blaze)**  
  To speed up the exposure search, the mean brightness is not calculated on the entire image, but on a subset instead. The image is downsampled until a desired window hight is reached. The window hight is calculated out of the image height divided by the downsampling_factor_exposure search.

- **frame_rate**  
  The desired acquisition frame rate corresponding to the driver spinning frame rate. Calling the GrabImages-Action can result in a higher frame rate.

- **shutter_mode (not for the blaze)**  
  Set mode of camera's shutter if the value is not empty. The supported modes are 'rolling', 'global' and 'global_reset'. Default value is '' (empty)

- **white_balance_auto (not for the blaze)**  
  Camera white balance auto.

- **white_balance_ratio_red & white_balance_ratio_green & white_balance_ratio_blue (not for the blaze)**  
  Camera white balance ratio.

- **trigger_timeout (not for the blaze)**  
  Camera trigger timeout in ms.

- **grab_timeout**  
  Camera grab timeout in ms.

- **grab_strategy (not for the blaze)**  
  Camera grab strategy: 0 = GrabStrategy_OneByOne / 1 = GrabStrategy_LatestImageOnly / 2 = GrabStrategy_LatestImages

**Image Intensity Settings**

The following settings do **NOT** have to be set. Each camera has default values which provide an automatic image adjustment resulting in valid images.

- **exposure**  
  The exposure time in microseconds to be set after opening the camera.

- **gain (not for the blaze)**  
  The target gain in percent of the maximal value the camera supports. For USB cameras, the gain is in dB, for GigE cameras it is given in so called 'device specific units'.

- **gamma (not for the blaze)**  
  Gamma correction of pixel intensity. Adjusts the brightness of the pixel values output by the camera's sensor to account for a non-linearity in the human perception of brightness or of the display system (such as CRT).

- **brightness (not for the blaze)**  
  The average intensity value of the images. It depends on the exposure time as well as the gain setting. If '**exposure**' is provided, the interface will try to reach the desired brightness by only varying the gain. (What may often fail, because the range of possible exposure values is many times higher than the gain range). If '**gain**' is provided, the interface will try to reach the desired brightness by only varying the exposure time. If '**gain**' AND '**exposure**' are given, it is not possible to reach the brightness, because both are assumed to be fixed.

- **brightness_continuous (not for the blaze)**  
  Only relevant, if '**brightness**' is set. The brightness_continuous flag controls the auto brightness function. If it is set to false, the brightness will only be reached once. Hence changing light conditions lead to changing brightness values. If it is set to true, the given brightness will be reached continuously, trying to adapt to changing light conditions. This is only possible for values in the possible auto range of the pylon API which is generally [50 - 205].

- **exposure_auto & gain_auto (not for the blaze)**  
  Only relevant, if '**brightness**' is set. If the camera should try to reach and / or keep the brightness, hence adapting to changing light conditions, at least one of the following flags must be set. If both are set, the interface will use the profile that tries to keep the gain at minimum to reduce white noise. The '**exposure_auto**' flag indicates, that the desired brightness will be reached by adapting the exposure time. The '**gain_auto**' flag indicates, that the desired brightness will be reached by adapting the gain.

**Optional and device specific parameter**

- **exposure_search_timeout (not for the blaze)**  
  The timeout while searching the exposure which is connected to the desired brightness. For slow system this has to be increased.

- **auto_exposure_upper_limit (not for the blaze)**  
  The exposure search can be limited with an upper bound. This is to prevent very high exposure times and resulting timeouts. A typical value for this upper bound is ~2000000us. Beware that this upper limit is only set if `startup_user_set` is set to `Default`.  

- **mtu_size (not for the blaze)**  
  The MTU size. Only used for GigE cameras. To prevent lost frames configure the camera has to be configured with the MTU size the network card supports. A value greater 3000 should be good (1500 for single-board computer)

- **inter_pkg_delay (not for the blaze)**  
  The inter-packet delay in ticks to prevent frame loss, support the network bandwith priorisation. Generally needs to modified if more than one cameras is involved or if hardware is not performing well. Raise inter-packet delay (GevSCPD) for solving error: 'the buffer was incompletely grabbed': https://docs.baslerweb.com/knowledge/troubleshooting-error-code-3774873620-0xe1000014-with-gige-cameras. For most of GigE cameras, a value of 1000 is reasonable. For cameras used on a single-board computer this value should be set to 11772. Beware that the inter-packet delay decrease will result in frame rate reduction.

- **frame_transmission_delay (not for the blaze)**  
  In most cases, this parameter should be set to 0. However, if your network hardware can't handle spikes in network traffic (e.g., if you are triggering multiple camera simultaneously), you can use the frame transmission delay parameter to stagger the start of image data transmissions from each camera.

- **auto_flash (not for the blaze)**  
  Flag that indicates if the camera has a flash connected, which should be on exposure. Only supported for GigE cameras. Default: false.

- **auto_flash_line_2 (not for the blaze)**  
  Flag that indicates if the camera has a flash connected on line 2, which should be on exposure. Only supported for GigE cameras. Default: true.

- **auto_flash_line_3 (not for the blaze)**  
  Flag that indicates if the camera has a flash connected on line 3, which should be on exposure. Only supported for GigE cameras. Default: true.

**ROS2 pylon node specific parameter**

- **startup_user_set (not for the blaze)**  
  Flag specifying if a given user set is used when starting the camera. Can be set to `Default`, `UserSet1`, `UserSet2`, `UserSet3`, and `CurrentSetting`.  

- **enable_status_publisher**  
  Flag used to enable/disable the node status publisher.

- **enable_current_params_publisher**  
  Flag used to enable/disable the current camera publisher.


## PTP synchronization (not for the blaze)

The Precision Time Protocol (PTP) camera feature allows you to synchronize multiple GigE cameras in the same network. It enables a camera to use the following features, if available:
- **Scheduled Action Commands** & **Action Commands**
- **Synchronous Free Run** (applies to ace 1 cameras)
- **Periodic Signal** (applies to ace 2 cameras)  

Refer to [the documentation](https://docs.baslerweb.com/precision-time-protocol) for more info about these features, with multiple code samples.  

The pylon driver gives accordingly access through ROS2 services to the following parameters and commands:

### ACE 1

**PTP configuration & activation**
- *GevIEEE1588*                    -> /my_camera/pylon_ros2_camera_node/enable_ptp [std_srvs/srv/SetBool]

**Scheduled Action Commands** & **Action Commands**
- *ActionDeviceKey*                -> /my_camera/pylon_ros2_camera_node/set_action_trigger_configuration [pylon_ros2_camera_interfaces/srv/SetActionTriggerConfiguration]
- *ActionGroupKey*                 -> /my_camera/pylon_ros2_camera_node/set_action_trigger_configuration [pylon_ros2_camera_interfaces/srv/SetActionTriggerConfiguration]
- *ActionGroupMask*                -> /my_camera/pylon_ros2_camera_node/set_action_trigger_configuration [pylon_ros2_camera_interfaces/srv/SetActionTriggerConfiguration]
- *IssueScheduledActionCommand*    -> /my_camera/pylon_ros2_camera_node/issue_scheduled_action_command [pylon_ros2_camera_interfaces/srv/IssueScheduledActionCommand]
- *IssueActionCommand*             -> /my_camera/pylon_ros2_camera_node/issue_action_command [pylon_ros2_camera_interfaces/srv/IssueActionCommand]

**Synchronous Free Run**
- *SyncFreeRunTimerStartTimeLow*   -> /my_camera/pylon_ros2_camera_node/set_sync_free_run_timer_start_time_low [pylon_ros2_camera_interfaces/srv/SetIntegerValue]
- *SyncFreeRunTimerStartTimeHigh*  -> /my_camera/pylon_ros2_camera_node/set_sync_free_run_timer_start_time_high [pylon_ros2_camera_interfaces/srv/SetIntegerValue]
- *SyncFreeRunTimerTriggerRateAbs* -> /my_camera/pylon_ros2_camera_node/set_sync_free_run_timer_trigger_rate_abs [pylon_ros2_camera_interfaces/srv/SetFloatValue]
- *SyncFreeRunTimerUpdate*         -> /my_camera/pylon_ros2_camera_node/update_sync_free_run_timer [std_srvs/srv/Trigger]
- *SyncFreeRunTimerEnable*         -> //my_camera/pylon_ros2_camera_node/enable_sync_free_run_timer [std_srvs/srv/SetBool]

### ACE 2

**PTP configuration & activation**
- *BslPtpPriority1*                -> /my_camera/pylon_ros2_camera_node/set_ptp_priority [pylon_ros2_camera_interfaces/srv/SetIntegerValue]
- *BslPtpProfile*                  -> /my_camera/pylon_ros2_camera_node/set_ptp_profile [pylon_ros2_camera_interfaces/srv/SetIntegerValue]
- *BslPtpNetworkMode*              -> /my_camera/pylon_ros2_camera_node/set_ptp_network_mode [pylon_ros2_camera_interfaces/srv/SetIntegerValue]
- *BslPtpUcPortAddrIndex*          -> /my_camera/pylon_ros2_camera_node/set_ptp_uc_port_address_index [pylon_ros2_camera_interfaces/srv/SetIntegerValue]
- *BslPtpUcPortAddr*               -> /my_camera/pylon_ros2_camera_node/set_ptp_uc_port_address [pylon_ros2_camera_interfaces/srv/SetIntegerValue]
- *BslPtpManagementEnable*         -> /my_camera/pylon_ros2_camera_node/enable_ptp_management_protocol [std_srvs/srv/SetBool]
- *BslTwoStep*                     -> /my_camera/pylon_ros2_camera_node/enable_two_step_operation [std_srvs/srv/SetBool]
- *PtpEnable*                      -> /my_camera/pylon_ros2_camera_node/enable_ptp [std_srvs/srv/SetBool]

**Scheduled Action Commands** & **Action Commands**
- *ActionDeviceKey*                -> /my_camera/pylon_ros2_camera_node/set_action_trigger_configuration [pylon_ros2_camera_interfaces/srv/SetActionTriggerConfiguration]
- *ActionGroupKey*                 -> /my_camera/pylon_ros2_camera_node/set_action_trigger_configuration [pylon_ros2_camera_interfaces/srv/SetActionTriggerConfiguration]
- *ActionGroupMask*                -> /my_camera/pylon_ros2_camera_node/set_action_trigger_configuration [pylon_ros2_camera_interfaces/srv/SetActionTriggerConfiguration]
- *IssueScheduledActionCommand*    -> /my_camera/pylon_ros2_camera_node/issue_scheduled_action_command [pylon_ros2_camera_interfaces/srv/IssueScheduledActionCommand]
- *IssueActionCommand*             -> /my_camera/pylon_ros2_camera_node/issue_action_command [pylon_ros2_camera_interfaces/srv/IssueActionCommand]

**Periodic Signal**
- *BslPeriodicSignalDelay*         -> /my_camera/pylon_ros2_camera_node/set_periodic_signal_delay [pylon_ros2_camera_interfaces/srv/SetFloatValue]
- *BslPeriodicSignalPeriod*        -> /my_camera/pylon_ros2_camera_node/set_periodic_signal_period [pylon_ros2_camera_interfaces/srv/SetFloatValue]


## Publishers

Name          | Notes
------------- | -------------
/my_camera/pylon_ros2_camera_node/camera_info  | sensor_msgs/msg/CameraInfo
/my_camera/pylon_ros2_camera_node/current_params  | current camera parameter
/my_camera/pylon_ros2_camera_node/image_raw  | acquired images
/my_camera/pylon_ros2_camera_node/image_rect  | rectified images if the camera is calibrated
/my_camera/pylon_ros2_camera_node/status  | camera status
/my_camera/pylon_ros2_camera_node/blaze_camera_info  | sensor_msgs/msg/CameraInfo
/my_camera/pylon_ros2_camera_node/blaze_cloud  | 3d point clouds from the blaze
/my_camera/pylon_ros2_camera_node/blaze_confidence  | confidence images from the blaze
/my_camera/pylon_ros2_camera_node/blaze_depth_map  | depth map images from the blaze
/my_camera/pylon_ros2_camera_node/blaze_depth_map_color  | depth map color images from the blaze
/my_camera/pylon_ros2_camera_node/blaze_intensity  | intensity images from the blaze


## Service servers

Name          | Notes
------------- | -------------
/my_camera/pylon_ros2_camera_node/activate_autoflash_output_[index]  | data : false = deactivate, true = activate
/my_camera/pylon_ros2_camera_node/describe_parameters  | -
/my_camera/pylon_ros2_camera_node/enable_acquisition_frame_rate  | data : false = deactivate, true = activate
/my_camera/pylon_ros2_camera_node/enable_ambiguity_filter  | data : false = deactivate, true = activate
/my_camera/pylon_ros2_camera_node/enable_distortion_correction  | data : false = deactivate, true = activate
/my_camera/pylon_ros2_camera_node/enable_fast_mode  | data : false = deactivate, true = activate
/my_camera/pylon_ros2_camera_node/enable_hdr_mode  | data : false = deactivate, true = activate
/my_camera/pylon_ros2_camera_node/enable_outlier_removal  | data : false = deactivate, true = activate
/my_camera/pylon_ros2_camera_node/enable_ptp  | data : false = deactivate, true = activate
/my_camera/pylon_ros2_camera_node/get_ptp_status  | -
/my_camera/pylon_ros2_camera_node/enable_ptp_management_protocol  | data : false = deactivate, true = activate
/my_camera/pylon_ros2_camera_node/enable_spatial_filter  | data : false = deactivate, true = activate
/my_camera/pylon_ros2_camera_node/enable_sync_free_run_timer  | data : false = deactivate, true = activate
/my_camera/pylon_ros2_camera_node/enable_temporal_filter  | data : false = deactivate, true = activate
/my_camera/pylon_ros2_camera_node/enable_thermal_drift_correction  | data : false = deactivate, true = activate
/my_camera/pylon_ros2_camera_node/enable_two_step_operation  | data : false = deactivate, true = activate
/my_camera/pylon_ros2_camera_node/execute_software_trigger  | -
/my_camera/pylon_ros2_camera_node/get_chunk_counter_value  | -
/my_camera/pylon_ros2_camera_node/get_chunk_enable  | -
/my_camera/pylon_ros2_camera_node/get_chunk_exposure_time  | -
/my_camera/pylon_ros2_camera_node/get_chunk_frame_counter  | -
/my_camera/pylon_ros2_camera_node/get_chunk_line_status_all  | -
/my_camera/pylon_ros2_camera_node/get_chunk_mode_active  | -
/my_camera/pylon_ros2_camera_node/get_chunk_selector  | -
/my_camera/pylon_ros2_camera_node/get_chunk_timestamp  | -
/my_camera/pylon_ros2_camera_node/get_max_num_buffer  | -
/my_camera/pylon_ros2_camera_node/get_parameter_types  | -
/my_camera/pylon_ros2_camera_node/get_parameters  | -
/my_camera/pylon_ros2_camera_node/get_statistic_buffer_underrun_count  | -
/my_camera/pylon_ros2_camera_node/get_statistic_failed_buffer_count  | -
/my_camera/pylon_ros2_camera_node/get_statistic_failed_packet_count  | -
/my_camera/pylon_ros2_camera_node/get_statistic_missed_frame_count  | -
/my_camera/pylon_ros2_camera_node/get_statistic_resend_request_count  | -
/my_camera/pylon_ros2_camera_node/get_statistic_resynchronization_count  | -
/my_camera/pylon_ros2_camera_node/get_statistic_total_buffer_count  | -
/my_camera/pylon_ros2_camera_node/issue_action_command  | -
/my_camera/pylon_ros2_camera_node/issue_scheduled_action_command  | -
/my_camera/pylon_ros2_camera_node/list_parameters  | -
/my_camera/pylon_ros2_camera_node/load_user_set  | -
/my_camera/pylon_ros2_camera_node/get_pfs  | -
/my_camera/pylon_ros2_camera_node/save_pfs  | value : '/path/to/your/output.pfs'
/my_camera/pylon_ros2_camera_node/load_pfs  | value : '/path/to/your/input.pfs'
/my_camera/pylon_ros2_camera_node/reset_device  | -
/my_camera/pylon_ros2_camera_node/save_user_set  | -
/my_camera/pylon_ros2_camera_node/set_PGI_mode  | data : false = deactivate, true = activate
/my_camera/pylon_ros2_camera_node/set_acquisition_frame_count  | value = new targeted frame count
/my_camera/pylon_ros2_camera_node/set_acquisition_frame_rate  | value = new targeted frame rate
/my_camera/pylon_ros2_camera_node/set_action_trigger_configuration  | -
/my_camera/pylon_ros2_camera_node/set_ambiguity_filter_threshold  | value = new ambiguity filter threshold
/my_camera/pylon_ros2_camera_node/set_binning  | -
/my_camera/pylon_ros2_camera_node/set_black_level  | value = new targeted black level
/my_camera/pylon_ros2_camera_node/set_brightness  | -
/my_camera/pylon_ros2_camera_node/set_chunk_enable  | data : false = deactivate, true = activate
/my_camera/pylon_ros2_camera_node/set_chunk_exposure_time  | -
/my_camera/pylon_ros2_camera_node/set_chunk_mode_active  | data : false = deactivate, true = activate
/my_camera/pylon_ros2_camera_node/set_chunk_selector  | -
/my_camera/pylon_ros2_camera_node/set_confidence_threshold  | value = new confidence threshold
/my_camera/pylon_ros2_camera_node/set_demosaicing_mode  | value : 0 = Simple, 1 = Basler PGI
/my_camera/pylon_ros2_camera_node/set_depth_max  | value = new max depth threshold
/my_camera/pylon_ros2_camera_node/set_depth_min  | value = new min depth threshold
/my_camera/pylon_ros2_camera_node/set_device_link_throughput_limit  | value = new targeted throughput limit in Bytes/sec.
/my_camera/pylon_ros2_camera_node/set_device_link_throughput_limit_mode  | data : false = deactivate, true = activate
/my_camera/pylon_ros2_camera_node/set_exposure  | -
/my_camera/pylon_ros2_camera_node/set_exposure_time_selector  | value : 1 = Stage1, 2 = Stage2
/my_camera/pylon_ros2_camera_node/set_gain  | -
/my_camera/pylon_ros2_camera_node/set_gamma  | value: 0 = User, 1 = sRGB
/my_camera/pylon_ros2_camera_node/set_gamma_activation  | (For GigE Cameras)
/my_camera/pylon_ros2_camera_node/set_gamma_selector  | value : 0 = User, 1 = sRGB (For GigE Cameras)
/my_camera/pylon_ros2_camera_node/set_grab_timeout  | -
/my_camera/pylon_ros2_camera_node/set_grabbing_strategy  | -
/my_camera/pylon_ros2_camera_node/set_image_encoding  | value = mono8, mono16, bgr8, rgb8, bayer_bggr8, bayer_gbrg8, bayer_rggb8, bayer_grbg8, bayer_rggb16, bayer_bggr16, bayer_gbrg16, bayer_grbg16
/my_camera/pylon_ros2_camera_node/set_intensity_calculation  | value : 1 = Method1, 2 = Method2
/my_camera/pylon_ros2_camera_node/set_light_source_preset  | value : 0 = Off, 1 = Daylight5000K, 2 = Daylight6500K, 3 = Tungsten2800K
/my_camera/pylon_ros2_camera_node/set_line_debouncer_time  | value = delay in micro sec
/my_camera/pylon_ros2_camera_node/set_line_inverter  | data : false = deactivate, true = activate
/my_camera/pylon_ros2_camera_node/set_line_mode  | value : 0 = Input, 1 = Output
/my_camera/pylon_ros2_camera_node/set_line_selector  | value : 1 = Line1, 2 = Line2, 3 = Line3, 4 = Line4
/my_camera/pylon_ros2_camera_node/set_line_source  | value : 0 = Exposure Active, 1 = FrameTriggerWait, 2 = UserOutput1, 3 = UserOutput2, 4 = UserOutput3, 5 = Timer1Active, 6 = FlashWindow
/my_camera/pylon_ros2_camera_node/set_max_num_buffer  | -
/my_camera/pylon_ros2_camera_node/set_max_transfer_size  | maximum USB data transfer size in bytes
/my_camera/pylon_ros2_camera_node/set_multi_camera_channel  | value = new channel
/my_camera/pylon_ros2_camera_node/set_noise_reduction  | value = reduction value
/my_camera/pylon_ros2_camera_node/set_offset_x  | value = targeted offset in x-axis
/my_camera/pylon_ros2_camera_node/set_offset_y  | value = targeted offset in y-axis
/my_camera/pylon_ros2_camera_node/set_operating_mode  | value : 0 = Long range, 1 = Short range
/my_camera/pylon_ros2_camera_node/set_outlier_removal_threshold  | value = new outlier removal threshold
/my_camera/pylon_ros2_camera_node/set_outlier_removal_tolerance  | value = new outlier removal tolerance
/my_camera/pylon_ros2_camera_node/set_output_queue_size  | -
/my_camera/pylon_ros2_camera_node/set_parameters  | -
/my_camera/pylon_ros2_camera_node/set_parameters_atomically  | -
/my_camera/pylon_ros2_camera_node/set_periodic_signal_delay  | value : delay to be applied to the periodic signal in microseconds
/my_camera/pylon_ros2_camera_node/set_periodic_signal_period  | value : length of the periodic signal in microseconds
/my_camera/pylon_ros2_camera_node/set_ptp_network_mode  | value : 1 = Hybrid, 2 = Multicast, 3 = Unicast
/my_camera/pylon_ros2_camera_node/set_ptp_priority  | value = value indicating the priority of the device when determining the master clock
/my_camera/pylon_ros2_camera_node/set_ptp_profile  | value : 1 = Delay Request Response Default Profile, 2 = Peer to Peer Default Profile
/my_camera/pylon_ros2_camera_node/set_ptp_uc_port_address  | value = unicast port address
/my_camera/pylon_ros2_camera_node/set_ptp_uc_port_address_index  | value = unicast port address index
/my_camera/pylon_ros2_camera_node/set_reverse_x  | data : false = deactivate, true = activate
/my_camera/pylon_ros2_camera_node/set_reverse_y  | data : false = deactivate, true = activate
/my_camera/pylon_ros2_camera_node/set_roi  | -
/my_camera/pylon_ros2_camera_node/set_sensor_readout_mode  | value : 0 = Normal, 1 = Fast
/my_camera/pylon_ros2_camera_node/set_sharpness_enhancement  | value = sharpness value
/my_camera/pylon_ros2_camera_node/set_sleeping  | -
/my_camera/pylon_ros2_camera_node/set_sync_free_run_timer_start_time_high  | value = high 32 bits of the synchronous free run trigger start time
/my_camera/pylon_ros2_camera_node/set_sync_free_run_timer_start_time_low  | value = low 32 bits of the synchronous free run trigger start time
/my_camera/pylon_ros2_camera_node/set_sync_free_run_timer_trigger_rate_abs  | value = synchronous free run trigger rate
/my_camera/pylon_ros2_camera_node/set_temporal_filter_strength  | value = new temporal filter strength
/my_camera/pylon_ros2_camera_node/set_timer_duration  | value = duration of the currently selected timer in microseconds
/my_camera/pylon_ros2_camera_node/set_timer_selector  | value : 1 = Timer 1, 2 = Timer 2, 3 = Timer 3, 4 = Timer 4
/my_camera/pylon_ros2_camera_node/set_timer_trigger_source  | value = see valid values of TimerTriggerSourceEnums in documentation
/my_camera/pylon_ros2_camera_node/set_trigger_activation  | value : 0 = RigingEdge, 1 = FallingEdge
/my_camera/pylon_ros2_camera_node/set_trigger_delay  | value = delay in micro sec.
/my_camera/pylon_ros2_camera_node/set_trigger_mode  | data : false = deactivate, true = activate
/my_camera/pylon_ros2_camera_node/set_trigger_selector  | value : 0 = Frame start, 1 = Frame burst start (ace USB cameras) / Acquisition Start (ace GigE cameras)
/my_camera/pylon_ros2_camera_node/set_trigger_source  | value : 0 = Software, 1 = Line 1, 2 = Line 2, 3 = Line 3, 4 = Line 4, 5 = Action 1, 6 = Periodic Signal 1
/my_camera/pylon_ros2_camera_node/set_trigger_timeout  | -
/my_camera/pylon_ros2_camera_node/set_user_output_[index]  | data : false = deactivate, true = activate
/my_camera/pylon_ros2_camera_node/set_user_set_default_selector  | value : 0 = Default, 1 = UserSet1, 2 = UserSet2, 3 = UserSet3, 4 = HighGain, 5 = AutoFunctions, 6 = ColorRaw
/my_camera/pylon_ros2_camera_node/set_user_set_selector  | value : 0 = Default, 1 = UserSet1, 2 = UserSet2, 3 = UserSet3, 4 = HighGain, 5 = AutoFunctions, 6 = ColorRaw
/my_camera/pylon_ros2_camera_node/set_white_balance  | -
/my_camera/pylon_ros2_camera_node/set_white_balance_auto  | value : 0 = Off, 1 = Once, 2 = Continuous
/my_camera/pylon_ros2_camera_node/start_grabbing  | -
/my_camera/pylon_ros2_camera_node/stop_grabbing  | -
/my_camera/pylon_ros2_camera_node/update_sync_free_run_timer  | -
/my_camera/set_camera_info  | -


## Action servers

Name          | Notes
------------- | -------------
/my_camera/pylon_ros2_camera_node/grab_blaze_data | -
/my_camera/pylon_ros2_camera_node/grab_images_raw  | -

Depending on the camera model, it is possible to grab one or several images or 3d data sets (3d point cloud, intensity, confidence, depth map, depth color map) through the dedicated action with user-specified parameters (e.g., exposure time, brightness value, etc.). Refer to the action definitions to get more information.  

For camera models other than the blaze, the camera-characteristic parameter such as height, width, projection matrix (by ROS2 convention, this matrix specifies the intrinsic (camera) matrix of the processed (rectified) image - see the [CameraInfo message definition](https://github.com/ros2/common_interfaces/blob/master/sensor_msgs/msg/CameraInfo.msg) for detailed information) and camera_frame were published over the /camera_info topic. Furthermore, an action-based image grabbing with desired exposure time, gain, gamma and / or brightness is provided. Hence, one can grab a sequence of images with above target settings as well as a single image. Grabbing images through this action can result in a higher frame rate.  


### Tests

The folder `pylon_ros2_camera_wrapper/test` includes different test programs. testing specific functionalities implemented by the driver. These programs are for testing purposes and should be adapted according to one's needs.
- *test_get_chunk_data*: test the access of specific chunk data
- *test_grab_blaze_data_action_client*, *test_grab_image_action_client*, and *test_grab_images_action_client*: trigger the image or the 3d data set grabbing through the actions `/my_camera/pylon_ros2_camera_node/grab_images_raw` or `/my_camera/pylon_ros2_camera_node/grab_blaze_data`, depending on the camera model. Each grabbed image (only the intensity image for the blaze) is displayed in a dedicated popup window.  


## Known issues

### User input in terminal when starting node through launch files
The ros2 launch mechanism doesn't allow to access stdin through a terminal (see [here](https://github.com/ros2/launch_ros/issues/165) and [here](https://answers.ros.org/question/343326/ros2-prefix-in-launch-file/)). This is solved in this implementation by installing and using `xterm` to emulate a terminal with possible user interaction.

### Service shutdown
In the ROS pylon implementation, the `activate_autoflash_output` and `set_user_output` service servers are shutdowned when the connection with a camera is lost. It is not possible for now to do so with ROS2 without shutting down the whole node (see [here](https://discourse.ros.org/t/how-to-shutdown-and-reinitialize-a-publisher-node-in-ros-2/4090)). There is no way to overcome this issue at the moment. 


## Troubleshooting

Some classes includes in their constructor the following command, commented by default:
`rcutils_ret_t __attribute__((unused)) res = rcutils_logging_set_logger_level(LOGGER_BASE.get_name(), RCUTILS_LOG_SEVERITY_DEBUG);`
Uncomment it to display on your terminal more detailed debug information.

With pylon 7.5.0, if the pylon viewer does not start, this is due to a Qt dependency missing. Try installing the xcb-cursor0 library with the following command: `sudo apt install libxcb-cursor0`. If it does not solve your issue, try starting the pylon viewer from the `bin` directory of pylon:
`cd /opt/pylon/bin/ && ./pylonviewer`. Report then the error message to the pylon support team.

To increase performance and to minimize CPU usage when grabbing images, the following settings should be considered:

### Slow frame rate

Please refer to the dedicated chapter ("Acquisition mode and frame rate") in this documentation for more information.

Beware as well that starting rviz2 or rqt before the driver may result in a slower frame rate. Start the driver starts followed by rqt or rviz2.

### No connection with connected camera (GigE devices)

To be sure to be able to connect to a specific camera, its network configuration must be manually set through Basler's pylon IP configurator. To do so, click on the camera in the list of connected devices, select the `Static IP` option, set an `IP Address` within the same range as the one of your computer, and set the same `Subnet Mask` as the one from your computer.

### Problems acquiring frames

#### Maximum UDP Socket Buffer Size (GigE devices)

The system's maximum UDP receive buffer size should be increased to ensure a stable image acquisition. A maximum size of 2 MB is recommended. This can be achieved by issuing the sudo sysctl net.core.rmem_max=2097152 command. To make this setting persistent, you can add the net.core.rmem_max setting to the /etc/sysctl.conf file.

#### Enable Jumbo Frames (GigE devices)

Many GigE network adapters support so-called jumbo frames, i.e., network packets larger than the usual 1500 bytes. To enable jumbo frames, the maximum transfer unit (MTU) size of the PC's network adapter must be set to a high value. We recommend using a value of 8192.

#### Increase the packet size (GigE devices)

If your network adapter supports jumbo frames, you set the adapter's MTU to 8192 as described above. In order to take advantage of the adapter's jumbo frame capability, you must also set the packet size used by the camera to 8192.

If you are working with the pylon Viewer application, you can set the packet size by first selecting a camera from the tree in the "Device" pane. In the "Features" pane, expand the features group that shows the camera's name, expand the "Transport Layer" parameters group, and set the "Packet Size" parameter to 8192. If you write your own application, use the camera API to set the PacketSize parameter to 8192.

It is possible to change the packet size by changing the default value of the `mtu_size` parameter in the pylon ROS2 wrapper launch file. When the camera is grabbing, it is not possible to modify this parameter.

#### Real-time Priority (GigE devices)

The GigE Vision implementation of Basler pylon software uses a thread for receiving image data. Basler pylon tries to set the thread priority for the receive thread to real-time thread priority. This requires certain permissions. The 'Permissions for Real-time Thread Priorities' section of the pylon INSTALL document describes how to grant the required permissions.

#### Increase Packet Size (U3V devices)

For faster USB transfers you should increase the packet size. You can do this by changing the "Stream Parameters" -> "Maximum Transfer Size" value from inside the pylon Viewer or by setting the corresponding value via the API. After increasing the packet size you will likely run out of kernel space and see corresponding error messages on the console. The default value set by the kernel is 16 MB. To set the value (in this example to 1000 MB) you can execute as root:
`echo 1000 > /sys/module/usbcore/parameters/usbfs_memory_mb`
This would assign a maximum of 1000 MB to the USB stack.
