#!/usr/bin/env python3

import os

import yaml

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.actions import OpaqueFunction
from launch.launch_context import LaunchContext
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


UNSET = '__launch_config_unset__'


def _load_config(path: str):
    try:
        with open(path, 'r', encoding='utf-8') as config_file:
            data = yaml.safe_load(config_file) or {}
            return data if isinstance(data, dict) else {}
    except (OSError, yaml.YAMLError):
        return {}


def _extract_ros_parameters(config):
    root = config.get('/**')
    if isinstance(root, dict):
        params = root.get('ros__parameters')
        if isinstance(params, dict):
            return params

    for value in config.values():
        if isinstance(value, dict):
            params = value.get('ros__parameters')
            if isinstance(params, dict):
                return params

    return {}


def _parse_bool(value, default=False):
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in ('true', '1', 'yes', 'on'):
            return True
        if lowered in ('false', '0', 'no', 'off'):
            return False
    return default


def _resolve_launch_value(context: LaunchContext, name: str, yaml_value, default):
    launch_value = LaunchConfiguration(name).perform(context)
    if launch_value != UNSET:
        return launch_value
    if yaml_value is not None:
        return str(yaml_value)
    return default


def _resolve_param_override(context: LaunchContext, arg_name: str, ros_params, default, cast):
    launch_value = LaunchConfiguration(arg_name).perform(context)
    if launch_value != UNSET:
        return cast(launch_value)
    if arg_name in ros_params:
        return None
    return default


def _launch_node(context: LaunchContext):
    """Return the action to launch `pylon_ros2_camera_wrapper`.
    This is required to evaluate `respawn` as boolean.
    """
    
    # adapt if needed
    debug = False

    config_file = LaunchConfiguration('config_file').perform(context)
    config = _load_config(config_file)
    ros_params = _extract_ros_parameters(config)

    node_name = _resolve_launch_value(context, 'node_name', ros_params.get('node_name'), 'pylon_ros2_camera_node')
    camera_id = _resolve_launch_value(context, 'camera_id', ros_params.get('camera_id'), 'my_camera')
    respawn_bool = _parse_bool(
        _resolve_launch_value(context, 'respawn', ros_params.get('respawn'), 'false'),
        default=False,
    )

    parameter_overrides = {}

    mtu_size = _resolve_param_override(context, 'mtu_size', ros_params, 1500, int)
    if mtu_size is not None:
        parameter_overrides['mtu_size'] = mtu_size

    startup_user_set = _resolve_param_override(context, 'startup_user_set', ros_params, 'CurrentSetting', str)
    if startup_user_set is not None:
        parameter_overrides['startup_user_set'] = startup_user_set

    enable_status_publisher = _resolve_param_override(context, 'enable_status_publisher', ros_params, True, _parse_bool)
    if enable_status_publisher is not None:
        parameter_overrides['enable_status_publisher'] = enable_status_publisher

    enable_current_params_publisher = _resolve_param_override(context, 'enable_current_params_publisher', ros_params, True, _parse_bool)
    if enable_current_params_publisher is not None:
        parameter_overrides['enable_current_params_publisher'] = enable_current_params_publisher

    parameters = [config_file]
    if parameter_overrides:
        parameters.append(parameter_overrides)

    # log format
    os.environ['RCUTILS_CONSOLE_OUTPUT_FORMAT'] = '{time} [{name}] [{severity}] {message}'

    # see https://navigation.ros.org/tutorials/docs/get_backtrace.html
    if debug:
        launch_prefix = ['xterm -e gdb -ex run --args']
    else:
        launch_prefix = ''

    return [
            Node(
                package='pylon_ros2_camera_wrapper',
                namespace=camera_id,
                executable='pylon_ros2_camera_wrapper',
                name=node_name,
                output='screen',
                respawn=respawn_bool,
                emulate_tty=True,
                prefix=launch_prefix,
                parameters=parameters
            ),
        ]

def generate_launch_description():

    default_config_file = os.path.join(
        get_package_share_directory('pylon_ros2_camera_wrapper'),
        'config',
        'default.yaml'
    )

    # launch arguments
    declare_node_name_cmd = DeclareLaunchArgument(
        'node_name',
        default_value=UNSET,
        description='Name of the wrapper node.'
    )

    declare_camera_id_cmd = DeclareLaunchArgument(
        'camera_id',
        default_value=UNSET,
        description='Id of the camera. Used as node namespace.'
    )

    declare_config_file_cmd = DeclareLaunchArgument(
        'config_file',
        default_value=default_config_file,
        description='Camera parameters structured in a .yaml file.'
    )

    declare_mtu_size_cmd = DeclareLaunchArgument(
        'mtu_size',
        default_value=UNSET,
        description='Maximum transfer unit size. To enable jumbo frames, set it to a high value (8192 recommended)'
    )

    declare_startup_user_set_cmd = DeclareLaunchArgument(
        'startup_user_set',
        # possible value: Default, UserSet1, UserSet2, UserSet3, CurrentSetting
        default_value=UNSET,
        description='Specific user set defining user parameters to run the camera.'
    )

    declare_enable_status_publisher_cmd = DeclareLaunchArgument(
        'enable_status_publisher',
        default_value=UNSET,
        description='Enable/Disable the status publishing.'
    )

    declare_enable_current_params_publisher_cmd = DeclareLaunchArgument(
        'enable_current_params_publisher',
        default_value=UNSET,
        description='Enable/Disable the current parameter publishing.'
    )

    declare_respawn_cmd = DeclareLaunchArgument(
        'respawn',
        default_value=UNSET,
        description='If true, the node will be respawned if it exits.'
    )

    # Define LaunchDescription variable and return it
    ld = LaunchDescription()

    ld.add_action(declare_node_name_cmd)
    ld.add_action(declare_camera_id_cmd)

    ld.add_action(declare_config_file_cmd)
    ld.add_action(declare_mtu_size_cmd)
    ld.add_action(declare_startup_user_set_cmd)
    ld.add_action(declare_enable_status_publisher_cmd)
    ld.add_action(declare_enable_current_params_publisher_cmd)

    ld.add_action(declare_respawn_cmd)

    ld.add_action(OpaqueFunction(function=_launch_node))

    return ld
